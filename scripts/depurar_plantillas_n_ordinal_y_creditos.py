# -*- coding: utf-8 -*-
"""
Depuración Masiva de Plantillas Word (.docx) para INDECOPI CC1:
1. Erradicación estricta y total de "Nº", "N°", "n°", "nº", y de los símbolos ordinales "º" y "°".
   - Normas: "Ley 29571", "Decreto Supremo 006-2026-JUS", "Decreto Legislativo 807".
   - Artículos: "artículo 81 de la Ley...", "artículo 19", "artículo 1", "artículo 108".
   - Pólizas: "Póliza 4053053", "Póliza 1760006823".
   - Resoluciones: "Resolución 1", "Expediente 1451-2026".
2. Censura confidencial de números de tarjetas de crédito y números de créditos bancarios:
   - Ejemplo: "el credito hipotecario 123xxxxxx879".
   - NUNCA se censuran pólizas ni certificados de seguro (mantienen su número íntegro).
"""

import glob
import os
import re
import sys
import time
import zipfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

def mask_number(num_str):
    """Preserva los primeros 3 y últimos 3 dígitos, reemplazando el centro por xxxxxx."""
    clean = re.sub(r'[\s\-\*]', '', num_str)
    if len(clean) <= 6:
        return num_str
    return f"{clean[:3]}xxxxxx{clean[-3:]}"

def depurar_texto(text):
    """Aplica la doble transformación sobre una cadena de texto."""
    if not text:
        return text

    # --- FASE 1: Censura de tarjetas y créditos (NUNCA pólizas ni certificados) ---
    pattern_credit = re.compile(
        r'(\b(?:crédito|credito|préstamo|prestamo|financiamiento|tarjeta|VTAR|cuenta)\b(?:\s+(?:de\s+)?(?:hipotecario|vehicular|personal|mype|por\s+convenio|renovación\s+café|consumo|bancario|revolving|efectivo|ahorros|corriente|crédito|credito|[a-zA-ZáéíóúÁÉÍÓÚñÑ]+)){0,3}\s+(?:N[°º\.]+\s*)?)([0-9\-\*]{7,25})',
        re.IGNORECASE
    )
    def repl_credit(m):
        full_prefix = m.group(1)
        num = m.group(2)
        low_pre = full_prefix.lower()
        if any(w in low_pre for w in ['póliza', 'poliza', 'certificado', 'siniestro', 'reclamo', 'expediente', 'ley', 'decreto', 'resolución', 'resolucion', 'ruc', 'dni', 'placa']):
            return m.group(0)
        return f"{full_prefix}{mask_number(num)}"

    text = pattern_credit.sub(repl_credit, text)

    # --- FASE 2: Erradicación estricta de N°, Nº, n°, nº y ordinales °, º ---
    # Frases compuestas con N°
    text = re.sub(r'\bcon\s+N[°º\.]+\s+de\b', 'con número de', text, flags=re.IGNORECASE)
    text = re.sub(r'\bsin\s+N[°º\.]+', 'sin número', text, flags=re.IGNORECASE)
    text = re.sub(r'\bComisión de Protección al Consumidor\s+N[°º\.]+\s*1\b', 'Comisión de Protección al Consumidor 1', text, flags=re.IGNORECASE)
    text = re.sub(r'\bPlaca\s+(?:de\s+Rodaje\s+)?N[°º\.]+\s*', 'Placa de Rodaje ', text, flags=re.IGNORECASE)

    # N° / Nº / n° / nº antes de cualquier código, número o palabra
    text = re.sub(r'\bN[°º\.]+\s*', '', text)
    text = re.sub(r'\bn[°º\.]+\s*', '', text)

    # Ordinales pegados a dígitos (ej. 19° -> 19, 81° -> 81, 108º -> 108, 1° -> 1)
    text = re.sub(r'(\d+)[°º]', r'\1', text)

    # Cualquier símbolo ° o º remanente
    text = text.replace('°', '').replace('º', '')

    # Normalización de espacios múltiples
    text = re.sub(r' {2,}', ' ', text)

    return text


def procesar_archivo_docx(docx_path):
    """Procesa un archivo .docx in-place reescribiendo sus XML internos."""
    ruta = Path(docx_path)
    tmp_path = ruta.with_suffix('.tmp_docx')
    modificado = False
    
    try:
        with zipfile.ZipFile(ruta, 'r') as zin, zipfile.ZipFile(tmp_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                # Solo procesamos archivos XML de texto
                if item.filename.startswith('word/') and item.filename.endswith('.xml'):
                    xml_str = data.decode('utf-8', errors='ignore')
                    
                    # Procesar cada tag <w:t>...</w:t>
                    def repl_wt(match):
                        attrs = match.group(1)
                        content = match.group(2)
                        depurado = depurar_texto(content)
                        return f"<w:t{attrs}>{depurado}</w:t>"

                    nuevo_xml = re.sub(r'<w:t([^>]*)>(.*?)</w:t>', repl_wt, xml_str, flags=re.DOTALL)
                    if nuevo_xml != xml_str:
                        modificado = True
                        data = nuevo_xml.encode('utf-8')
                
                zout.writestr(item, data)

        if modificado:
            tmp_path.replace(ruta)
            return (ruta.name, True, "Modificado con éxito")
        else:
            tmp_path.unlink(missing_ok=True)
            return (ruta.name, False, "Sin cambios requeridos")

    except Exception as e:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        return (ruta.name, False, f"ERROR: {e}")


def main():
    directorio_base = Path("plantillas_maestras")
    archivos = list(directorio_base.glob("**/*.docx"))
    total = len(archivos)
    print(f"Iniciando depuración masiva de {total} plantillas Word (.docx)...")
    t0 = time.time()

    modificados = 0
    errores = 0

    # Procesar con pool de procesos
    workers = min(os.cpu_count() or 4, 8)
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(procesar_archivo_docx, str(p)): p for p in archivos}
        completados = 0
        for fut in as_completed(futures):
            completados += 1
            nombre, cambio, msg = fut.result()
            if cambio:
                modificados += 1
            if "ERROR" in msg:
                errores += 1
                print(f"[{completados}/{total}] ❌ {nombre}: {msg}")
            elif completados % 100 == 0 or completados == total:
                print(f"[{completados}/{total}] Progreso: {modificados} modificados, {errores} errores...")

    t1 = time.time()
    print("=" * 75)
    print(f"DEPURACIÓN COMPLETADA EN {t1 - t0:.2f} segundos.")
    print(f"Total plantillas inspeccionadas: {total}")
    print(f"Plantillas modificadas y saneadas: {modificados}")
    print(f"Errores encontrados: {errores}")
    print("=" * 75)


if __name__ == "__main__":
    main()
