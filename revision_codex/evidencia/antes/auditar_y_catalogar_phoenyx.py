#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
auditar_y_catalogar_phoenyx.py
Recorre los 605 modelos de C:\\Users\\D\\Desktop\\000 PLAN PHOENYX,
extrae su taxonomía, metadatos, problemas ortográficos/mojibake y versión LPAG.
Genera un catálogo unificado en docs/catalogo_modelos_phoenyx.json.
"""

import os
import re
import json
from pathlib import Path
import docx

SOURCE_DIR = Path(r"C:\Users\D\Desktop\000 PLAN PHOENYX")
REPO_ROOT = Path(r"C:\Users\D\ZCodeProject\SystemHope-ResAdmis")
OUTPUT_JSON = REPO_ROOT / "docs" / "catalogo_modelos_phoenyx.json"
OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)

def sanitizar_texto(texto):
    if not texto:
        return ""
    return re.sub(r'\s+', ' ', texto).strip()

def analizar_archivo(ruta_docx: Path):
    rel_path = ruta_docx.relative_to(SOURCE_DIR)
    parts = list(rel_path.parts)
    
    # 1. Taxonomía de carpetas
    tipo_seguro = parts[0] if len(parts) > 1 else "No especificado"
    cobertura = parts[1] if len(parts) > 2 else "General"
    hecho_infractor = parts[2] if len(parts) > 3 else "No especificado"
    proveedor_carpeta = parts[3] if len(parts) > 4 else "Varios"
    caso_carpeta = parts[4] if len(parts) > 5 else parts[-2]
    
    # Detección de género / sujeto en la carpeta
    sujeto_tipo = "NO_ESPECIFICADO"
    if "MUJER" in caso_carpeta.upper():
        sujeto_tipo = "MUJER"
    elif "VAR" in caso_carpeta.upper(): # VARÓN o VARON
        sujeto_tipo = "VARON"
    elif "SUCESI" in caso_carpeta.upper():
        sujeto_tipo = "SUCESION_INTESTADA"
    elif "VARIOS" in caso_carpeta.upper():
        sujeto_tipo = "VARIOS"

    # 2. Análisis del documento Word
    metadata = {
        "expediente": "",
        "denunciante": "",
        "denunciado": "",
        "resolucion": "1",
        "fecha": "",
    }
    
    notificaciones = []
    menciones_lpag = []
    tiene_mojibake = False
    articulos_resolutivos = []
    num_parrafos = 0
    
    try:
        doc = docx.Document(str(ruta_docx))
        num_parrafos = len(doc.paragraphs)
        
        for p in doc.paragraphs:
            txt = p.text
            if not txt:
                continue
            
            if '\ufffd' in txt or '' in txt:
                tiene_mojibake = True
                
            clean = sanitizar_texto(txt)
            
            # Extraer metadata inicial
            if clean.startswith("EXPEDIENTE"):
                metadata["expediente"] = clean.split(":")[-1].strip()
            elif clean.startswith("DENUNCIANTE"):
                metadata["denunciante"] = clean.split(":")[-1].strip()
            elif clean.startswith("DENUNCIADO"):
                metadata["denunciado"] = clean.split(":")[-1].strip()
            elif clean.startswith("RESOLUCI"):
                metadata["resolucion"] = clean.split(":")[-1].strip()
            elif clean.startswith("Lima,"):
                metadata["fecha"] = clean
                
            # LPAG
            m_lpag = re.findall(r'Decreto\s+Supremo\s+N?[°º]?\s*(\d{3,4}-\d{4}-JUS)', clean, re.IGNORECASE)
            for lpag in m_lpag:
                menciones_lpag.append(lpag.upper())
                
            # Notificaciones
            if any(k in clean.lower() for k in ['casilla electr', 'correo electr', 'domicilio procesal', 'domicilio real']):
                if any(clean.upper().startswith(x) for x in ['DÉCIMO', 'DECIMO', 'UNDÉCIMO', 'DUODÉCIMO']):
                    notificaciones.append(clean)
                    
            # Artículos resolutivos
            m_art = re.match(r'^(PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|S[EÉ]TIMO|OCTAVO|NOVENO|D[EÉ]CIMO(?:\s+\w+)?):', clean, re.IGNORECASE)
            if m_art:
                articulos_resolutivos.append(m_art.group(1).upper())
                
    except Exception as e:
        return {
            "error": str(e),
            "ruta_relativa": str(rel_path),
            "ruta_absoluta": str(ruta_docx)
        }

    # Determinar si hay múltiples denunciados
    es_multiple_ddo = False
    ddo_txt = metadata.get("denunciado", "")
    if ";" in ddo_txt or " Y " in ddo_txt.upper() or "BANCO" in ddo_txt.upper() and "SEGUROS" in ddo_txt.upper():
        es_multiple_ddo = True

    return {
        "ruta_relativa": str(rel_path),
        "ruta_absoluta": str(ruta_docx),
        "archivo": ruta_docx.name,
        "taxonomia": {
            "tipo_seguro": tipo_seguro,
            "cobertura": cobertura,
            "hecho_infractor": hecho_infractor,
            "proveedor_carpeta": proveedor_carpeta,
            "caso_carpeta": caso_carpeta,
            "sujeto_tipo": sujeto_tipo,
            "es_multiple_ddo": es_multiple_ddo,
        },
        "metadata_doc": metadata,
        "lpag": list(set(menciones_lpag)),
        "tiene_mojibake": tiene_mojibake,
        "num_notificaciones": len(notificaciones),
        "articulos_resolutivos": articulos_resolutivos,
        "num_parrafos": num_parrafos,
    }

def main():
    print(f"Buscando archivos .docx en {SOURCE_DIR}...")
    archivos = sorted(SOURCE_DIR.glob("**/*.docx"))
    print(f"Total encontrados: {len(archivos)}")
    
    catalogo = []
    con_lpag_viejo = 0
    con_mojibake = 0
    
    for idx, f in enumerate(archivos, 1):
        if idx % 50 == 0 or idx == len(archivos):
            print(f"Procesando {idx}/{len(archivos)}...")
        res = analizar_archivo(f)
        catalogo.append(res)
        
        if "004-2019-JUS" in res.get("lpag", []):
            con_lpag_viejo += 1
        if res.get("tiene_mojibake", False):
            con_mojibake += 1

    print("\n--- RESUMEN DE AUDITORÍA ---")
    print(f"Modelos procesados: {len(catalogo)}")
    print(f"Modelos con LPAG desactualizado (004-2019-JUS): {con_lpag_viejo}")
    print(f"Modelos con mojibake detectado: {con_mojibake}")
    
    with open(OUTPUT_JSON, "w", encoding="utf-8") as out:
        json.dump(catalogo, out, ensure_ascii=False, indent=2)
        
    print(f"Catálogo guardado exitosamente en: {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
