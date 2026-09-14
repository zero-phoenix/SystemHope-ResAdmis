import os
import re
import json
import zipfile
import shutil
import unicodedata
import time
from pathlib import Path
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

SOURCE_DIR = Path(r"C:\Users\D\Desktop\000 PLAN PHOENYX")
REPO_ROOT = Path(r"C:\Users\D\ZCodeProject\SystemHope-ResAdmis")
TARGET_ROOT = REPO_ROOT / "plantillas_maestras"
CATALOG_JSON = REPO_ROOT / "docs" / "catalogo_modelos_phoenyx.json"
INDEX_MD = REPO_ROOT / "docs" / "INDICE_TAXONOMICO_PLANTILLAS_MAESTRAS.md"
INDEX_JSON = REPO_ROOT / "docs" / "plantillas_maestras_index.json"

# ==============================================================================
# 1. MAPEOS TAXONÓMICOS CANÓNICOS
# ==============================================================================

def normalizar_cadena(s: str) -> str:
    if not s:
        return ""
    s = s.strip()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r'[^a-zA-Z0-9_]+', '_', s)
    return s.strip('_').lower()

def resolver_rama(tipo_seguro_raw: str) -> str:
    norm = normalizar_cadena(tipo_seguro_raw)
    if "vehicular" in norm:
        return "01_seguro_vehicular"
    elif "vida" in norm:
        return "02_seguro_vida"
    elif "desgravamen" in norm:
        return "03_seguro_desgravamen"
    elif "tarjeta" in norm:
        return "04_seguro_proteccion_tarjetas_y_dinero"
    elif "soat" in norm or "afocat" in norm:
        return "05_soat_y_afocat"
    elif "hogar" in norm or "inmueble" in norm or "sismo" in norm:
        return "06_seguro_hogar_e_inmuebles"
    elif "sctr" in norm or "riesgo" in norm:
        return "07_seguro_sctr"
    elif "salud" in norm or "eps" in norm or "oncol" in norm:
        return "08_seguro_salud_eps_oncologico"
    elif "patrimonial" in norm or "caucion" in norm or "rc" in norm:
        return "09_seguro_patrimonial_caucion_rc"
    elif "sepelio" in norm:
        return "10_seguro_sepelio"
    elif "accidente" in norm:
        return "11_seguro_accidentes_personales"
    elif "transporte" in norm or "carga" in norm:
        return "12_seguro_transporte_y_carga"
    elif "multiple" in norm or "equipo" in norm:
        return "13_seguro_multiple_y_equipos"
    elif "desempleo" in norm:
        return "14_seguro_desempleo"
    elif "previsional" in norm or "afp" in norm or "onp" in norm:
        return "15_sistema_previsional_afp_onp"
    elif "administrativ" in norm or "financier" in norm:
        return "16_temas_administrativos_financieros"
    elif "medica" in norm:
        return "18_servicios_salud_atencion_medica"
    else:
        return "17_seguro_no_especificado"

def categorizar_materia(hecho_infractor: str, cobertura: str) -> str:
    txt = (hecho_infractor + " " + cobertura).lower()
    if "negativa" in txt and "cobertura" in txt:
        return "negativa_cobertura"
    elif "anulaci" in txt or "cancelaci" in txt or "resoluci" in txt:
        return "anulacion_indebida"
    elif "falta de entrega" in txt or "no entrega" in txt or ("poliza" in txt and "entrega" in txt):
        return "falta_entrega_poliza"
    elif "cobro" in txt or "debito" in txt or "cuota" in txt:
        return "cobro_indebido_primas"
    elif "atenci" in txt or "demora" in txt or "reclamo" in txt or "respuesta" in txt:
        return "falta_atencion_o_demora_reclamo"
    elif "evaluaci" in txt or "invalidez" in txt or "sctr" in txt or "inr" in txt:
        return "falta_evaluacion_invalidez"
    elif "liquidaci" in txt or "pago" in txt or "devoluci" in txt or "menor" in txt:
        return "liquidacion_o_pago_menor"
    elif "no consentida" in txt or "atribuci" in txt:
        return "contratacion_no_consentida"
    elif "discriminaci" in txt:
        return "discriminacion"
    elif "siniestro" in txt or "reparaci" in txt:
        return "deficiente_gestion_siniestro"
    elif "clausula" in txt or "abusiv" in txt:
        return "clausula_abusiva"
    elif "modificaci" in txt:
        return "modificacion_unilateral"
    elif "renovaci" in txt:
        return "falta_renovacion_poliza"
    else:
        return "materia_general_asegurativa"

def categorizar_proveedor(proveedor_carpeta: str, ddo_text: str, es_multiple: bool) -> str:
    full = (proveedor_carpeta + " " + ddo_text).upper()
    tiene_banco = any(b in full for b in ["BANCO", "BBVA", "BCP", "INTERBANK", "SCOTIABANK", "FALABELLA", "RIPLEY", "PICHINCHA", "MIBANCO", "CREDITO DEL PERU"])
    tiene_seguro = any(s in full for s in ["SEGURO", "RIMAC", "RÍMAC", "PACIFICO", "PACÍFICO", "MAPFRE", "POSITIVA", "INTERSEGURO", "CARDIF", "CHUBB", "PROTECTA", "OHIO", "CRECER", "VIDA"])
    tiene_corredor = any(c in full for c in ["CORREDOR", "CORREDORES", "BROKER", "MARSH", "AON"])
    
    if (tiene_banco and tiene_seguro) or es_multiple:
        if tiene_banco and tiene_seguro:
            return "2_ddos_banco_y_aseguradora"
        else:
            return "2_o_mas_ddos_varios"
    elif tiene_corredor:
        return "1_ddo_corredor"
    elif tiene_banco and not tiene_seguro:
        return "1_ddo_banco_o_financiera"
    else:
        return "1_ddo_aseguradora"

def categorizar_sujeto(sujeto_tipo: str, caso_carpeta: str, dte_text: str) -> str:
    combined = (sujeto_tipo + " " + caso_carpeta + " " + dte_text).upper()
    if "SUCESI" in combined or "HEREDER" in combined or "CAUSANTE" in combined:
        return "sucesion_intestada"
    elif "VARIOS" in combined or " Y " in dte_text.upper() or ";" in dte_text:
        return "varios"
    elif "MUJER" in combined:
        return "mujer"
    elif "VAR" in combined:
        return "varon"
    else:
        return "varon"

# ==============================================================================
# 2. MOTOR OPTIMIZADO DE DEPURACIÓN TEXTUAL, NORMATIVA Y ORTOGRÁFICA
# ==============================================================================

REEMPLAZOS_LPAG = [
    (re.compile(r'Decreto\s+Supremo\s+N?[°º]?\s*004-2019-JUS', re.IGNORECASE), 'Decreto Supremo 006-2026-JUS'),
    (re.compile(r'DECRETO\s+SUPREMO\s+N?[°º]?\s*004-2019-JUS'), 'DECRETO SUPREMO 006-2026-JUS'),
    (re.compile(r'D\.S\.\s*N?[°º]?\s*004-2019-JUS', re.IGNORECASE), 'Decreto Supremo 006-2026-JUS'),
    (re.compile(r'N[°º]\s*004-2019-JUS'), 'N° 006-2026-JUS'),
    (re.compile(r'\b004-2019-JUS\b'), '006-2026-JUS'),
    (re.compile(r'25\s+de\s+enero\s+de\s+2019', re.IGNORECASE), '30 de abril de 2026'),
]

REEMPLAZOS_LEXICOS = [
    (re.compile(r'\besposo\b'), 'cónyuge'),
    (re.compile(r'\besposa\b'), 'cónyuge'),
    (re.compile(r'\besposos\b'), 'cónyuges'),
    (re.compile(r'\bEsposo\b'), 'Cónyuge'),
    (re.compile(r'\bEsposa\b'), 'Cónyuge'),
    (re.compile(r'\bEsposos\b'), 'Cónyuges'),
    (re.compile(r'\btras\b'), 'luego de'),
    (re.compile(r'\bTras\b'), 'Luego de'),
    (re.compile(r'\bésta\b'), 'esta'),
    (re.compile(r'\bÉsta\b'), 'Esta'),
    (re.compile(r'\béste\b'), 'este'),
    (re.compile(r'\bÉste\b'), 'Este'),
    (re.compile(r'\béstas\b'), 'estas'),
    (re.compile(r'\bÉstas\b'), 'Estas'),
    (re.compile(r'\béstos\b'), 'estos'),
    (re.compile(r'\bÉstos\b'), 'Estos'),
    (re.compile(r'\bDr\.\s+(?!Ley\b)'), 'médico '),
    (re.compile(r'\bdoctor\s+(?!Ley\b)'), 'médico '),
    (re.compile(r'\bDoctor\s+(?!Ley\b)'), 'Médico '),
    (re.compile(r'\bdoctora\b'), 'médica'),
    (re.compile(r'\bDoctora\b'), 'Médica'),
    (re.compile(r'\b(el|su|un|dicho|este|del|al)\s+auto\b', re.IGNORECASE), r'\1 vehículo'),
    (re.compile(r'\b(los|sus|unos|dichos|estos)\s+autos\b', re.IGNORECASE), r'\1 vehículos'),
    (re.compile(r'\b(el|su|un|dicho|este|del|al)\s+carro\b', re.IGNORECASE), r'\1 vehículo'),
    (re.compile(r'\b(los|sus|unos|dichos|estos)\s+carros\b', re.IGNORECASE), r'\1 vehículos'),
]

REEMPLAZOS_INDUCCION_ERROR = [
    (re.compile(r'induci[oó]\s+a\s+error', re.IGNORECASE), 'infringió el deber de información'),
    (re.compile(r'inducir\s+a\s+error', re.IGNORECASE), 'infringir el deber de información'),
    (re.compile(r'inducci[oó]n\s+a\s+error', re.IGNORECASE), 'falta al deber de información'),
]

REEMPLAZOS_MOJIBAKE = [
    (re.compile(r'\bRMAC\b'), 'RÍMAC'),
    (re.compile(r'\bRmac\b'), 'Rímac'),
    (re.compile(r'\bCOMPAA\b'), 'COMPAÑÍA'),
    (re.compile(r'\bCompaa\b'), 'Compañía'),
    (re.compile(r'\bCRDITO\b'), 'CRÉDITO'),
    (re.compile(r'\bCrdito\b'), 'Crédito'),
    (re.compile(r'\bPACFICO\b'), 'PACÍFICO'),
    (re.compile(r'\bPacfico\b'), 'Pacífico'),
    (re.compile(r'\bPROTECCIN\b'), 'PROTECCIÓN'),
    (re.compile(r'\bProteccin\b'), 'Protección'),
    (re.compile(r'\bATENCIN\b'), 'ATENCIÓN'),
    (re.compile(r'\bAtencin\b'), 'Atención'),
    (re.compile(r'\bPLIZA\b'), 'PÓLIZA'),
    (re.compile(r'\bPliza\b'), 'Póliza'),
    (re.compile(r'\bCDIGO\b'), 'CÓDIGO'),
    (re.compile(r'\bCdigo\b'), 'Código'),
    (re.compile(r'\bTRANSACCIN\b'), 'TRANSACCIÓN'),
    (re.compile(r'\bTransaccin\b'), 'Transacción'),
    (re.compile(r'\bOBLIGACIN\b'), 'OBLIGACIÓN'),
    (re.compile(r'\bObligacin\b'), 'Obligación'),
    (re.compile(r'\bEXPEDICIN\b'), 'EXPEDICIÓN'),
    (re.compile(r'\bExpedicin\b'), 'Expedición'),
    (re.compile(r'\bEJECUCIN\b'), 'EJECUCIÓN'),
    (re.compile(r'\bEjecucin\b'), 'Ejecución'),
    (re.compile(r'\bCOMUNICACIN\b'), 'COMUNICACIÓN'),
    (re.compile(r'\bComunicacin\b'), 'Comunicación'),
    (re.compile(r'\bPER\b(?=\s+(?:SAC|SA|S\.A\.|S\.A\.C\.|VIDA|SEGUROS|BANCO))'), 'PERÚ'),
    (re.compile(r'\bPer\b(?=\s+(?:SAC|SA|S\.A\.|S\.A\.C\.|VIDA|SEGUROS|BANCO))'), 'Perú'),
]

def normalizar_moneda(texto: str) -> str:
    def _repl_soles(m):
        miles = m.group(1).replace(',', ' ')
        dec = m.group(2)
        return f"S/ {miles},{dec}"
    
    def _repl_dolares(m):
        miles = m.group(1).replace(',', ' ')
        dec = m.group(2)
        return f"US$ {miles},{dec}"
    
    texto = re.sub(r'S/\s*([0-9]{1,3}(?:,[0-9]{3})+)\.([0-9]{2})\b', _repl_soles, texto)
    texto = re.sub(r'US\$\s*([0-9]{1,3}(?:,[0-9]{3})+)\.([0-9]{2})\b', _repl_dolares, texto)
    return texto

def procesar_contenido_xml(xml_str: str) -> str:
    # 1. LPAG con pre-check
    if '004-2019' in xml_str or '2019-JUS' in xml_str or '25 de enero de 2019' in xml_str:
        for pattern, repl in REEMPLAZOS_LPAG:
            xml_str = pattern.sub(repl, xml_str)
        
    # 2. Invariantes Léxicas con pre-check
    if any(k in xml_str for k in ['esposo', 'esposa', 'tras', 'Tras', 'ésta', 'éste', 'éstas', 'éstos', 'Dr.', 'doctor', 'auto', 'carro']):
        for pattern, repl in REEMPLAZOS_LEXICOS:
            xml_str = pattern.sub(repl, xml_str)
        
    # 3. Cero Inducción a Error con pre-check
    if 'induc' in xml_str or 'Induc' in xml_str:
        for pattern, repl in REEMPLAZOS_INDUCCION_ERROR:
            xml_str = pattern.sub(repl, xml_str)
        
    # 4. Mojibake con pre-check
    if any(k in xml_str for k in ['RMAC', 'COMPAA', 'CRDITO', 'PACFICO', 'PROTECCIN', 'ATENCIN', 'PLIZA', 'CDIGO', 'TRANSACCIN', 'OBLIGACIN', 'EXPEDICIN', 'EJECUCIN', 'COMUNICACIN', 'PER ']):
        for pattern, repl in REEMPLAZOS_MOJIBAKE:
            xml_str = pattern.sub(repl, xml_str)
        
    # 5. Moneda con pre-check
    if 'S/' in xml_str or 'US$' in xml_str:
        xml_str = normalizar_moneda(xml_str)
    
    return xml_str

def depurar_archivo_docx(origen: Path, destino: Path) -> bool:
    try:
        destino.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(origen, 'r') as zin, zipfile.ZipFile(destino, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename.endswith('.xml') and any(k in item.filename for k in ['document', 'footnotes', 'endnotes', 'header', 'footer']):
                    try:
                        text = data.decode('utf-8')
                        new_text = procesar_contenido_xml(text)
                        if new_text != text:
                            data = new_text.encode('utf-8')
                    except UnicodeDecodeError:
                        pass
                zout.writestr(item, data)
        return True
    except Exception as e:
        print(f"Error procesando {origen}: {e}")
        return False

# ==============================================================================
# 3. PIPELINE PRINCIPAL MULTIHILO
# ==============================================================================

def main():
    print("=" * 80)
    print("PIPELINE MAESTRO OPTIMIZADO: DEPURACIÓN Y ESTRUCTURACIÓN TAXONÓMICA")
    print("=" * 80)
    
    if not CATALOG_JSON.exists():
        print(f"ERROR: No se encontró {CATALOG_JSON}")
        return
        
    with open(CATALOG_JSON, 'r', encoding='utf-8') as f:
        catalogo = json.load(f)
        
    print(f"Total de modelos en catálogo: {len(catalogo)}")
    TARGET_ROOT.mkdir(parents=True, exist_ok=True)
    
    # Precomputar rutas y nombres de destino para evitar colisiones
    tareas = []
    nombres_usados = set()
    
    for idx, item in enumerate(catalogo, 1):
        origen_path = Path(item["ruta_absoluta"])
        tax = item.get("taxonomia", {})
        meta = item.get("metadata_doc", {})
        
        rama_folder = resolver_rama(tax.get("tipo_seguro", ""))
        materia_folder = categorizar_materia(tax.get("hecho_infractor", ""), tax.get("cobertura", ""))
        proveedor_folder = categorizar_proveedor(tax.get("proveedor_carpeta", ""), meta.get("denunciado", ""), tax.get("es_multiple_ddo", False))
        sujeto_folder = categorizar_sujeto(tax.get("sujeto_tipo", ""), tax.get("caso_carpeta", ""), meta.get("denunciante", ""))
        
        exp_raw = meta.get("expediente", "")
        m_exp = re.search(r'(\d+-\d{4})', exp_raw)
        if not m_exp:
            m_exp = re.search(r'(\d+-\d{4})', origen_path.name)
        num_exp = m_exp.group(1) if m_exp else f"EXP{idx:03d}"
        
        m_r = re.search(r'R(\d+)', origen_path.name, re.IGNORECASE)
        res_tag = f"_R{m_r.group(1)}" if m_r else ""
        
        ddo_tag = "ASEGURADORA"
        if "banco" in proveedor_folder:
            ddo_tag = "BANCO"
        elif "2_ddos" in proveedor_folder:
            ddo_tag = "BANCO_Y_ASEGURADORA"
        elif "corredor" in proveedor_folder:
            ddo_tag = "CORREDOR"
            
        nombre_base = f"TPL_{num_exp}_{rama_folder[3:].upper()}_{materia_folder.upper()}_{ddo_tag}_{sujeto_folder.upper()}{res_tag}"
        base_sin_ext = normalizar_cadena(nombre_base).upper()
        
        colision_idx = 1
        nombre_final = f"{base_sin_ext}.docx"
        while (rama_folder, materia_folder, proveedor_folder, sujeto_folder, nombre_final) in nombres_usados:
            colision_idx += 1
            nombre_final = f"{base_sin_ext}_V{colision_idx}.docx"
        nombres_usados.add((rama_folder, materia_folder, proveedor_folder, sujeto_folder, nombre_final))
        
        destino_dir = TARGET_ROOT / rama_folder / materia_folder / proveedor_folder / sujeto_folder
        destino_path = destino_dir / nombre_final
        
        tareas.append({
            "idx": idx,
            "origen": origen_path,
            "destino": destino_path,
            "num_exp": num_exp,
            "rama": rama_folder,
            "materia": materia_folder,
            "proveedor": proveedor_folder,
            "sujeto": sujeto_folder,
            "archivo": nombre_final,
            "rel_origen": str(origen_path.relative_to(SOURCE_DIR)).replace("\\", "/") if SOURCE_DIR in origen_path.parents else origen_path.name
        })

    print(f"Preparadas {len(tareas)} asignaciones taxonómicas. Iniciando procesamiento multihilo...")
    t0 = time.time()
    
    conteo_ramas = Counter()
    conteo_materias = Counter()
    conteo_proveedores = Counter()
    conteo_sujetos = Counter()
    indice_general = []
    exitos = 0
    fallos = 0

    def procesar_tarea(t):
        ok = depurar_archivo_docx(t["origen"], t["destino"])
        return t, ok

    with ThreadPoolExecutor(max_workers=8) as executor:
        for t, ok in executor.map(procesar_tarea, tareas):
            if ok:
                exitos += 1
                conteo_ramas[t["rama"]] += 1
                conteo_materias[t["materia"]] += 1
                conteo_proveedores[t["proveedor"]] += 1
                conteo_sujetos[t["sujeto"]] += 1
                rel_dest = t["destino"].relative_to(REPO_ROOT)
                indice_general.append({
                    "id": t["idx"],
                    "expediente": t["num_exp"],
                    "rama": t["rama"],
                    "materia": t["materia"],
                    "proveedor_tipo": t["proveedor"],
                    "sujeto_tipo": t["sujeto"],
                    "archivo": t["archivo"],
                    "ruta_relativa": str(rel_dest).replace("\\", "/"),
                    "origen_original": t["rel_origen"]
                })
            else:
                fallos += 1
            if (exitos + fallos) % 50 == 0 or (exitos + fallos) == len(tareas):
                print(f"[{exitos + fallos}/{len(tareas)}] Progreso: {exitos} exitosos, {fallos} fallos...")

    dt = time.time() - t0
    print("\n" + "=" * 80)
    print(f"PROCESAMIENTO FINALIZADO: {exitos} plantillas depuradas en {dt:.2f}s ({dt/max(1, exitos):.3f}s/plantilla).")
    print("=" * 80)
    
    with open(INDEX_JSON, 'w', encoding='utf-8') as fj:
        json.dump(indice_general, fj, ensure_ascii=False, indent=2)
    print(f"[OK] Guardado indice JSON: {INDEX_JSON}")
    
    generar_reporte_taxonomico(indice_general, conteo_ramas, conteo_materias, conteo_proveedores, conteo_sujetos)

def generar_reporte_taxonomico(indice, conteo_ramas, conteo_materias, conteo_proveedores, conteo_sujetos):
    total = len(indice)
    md = []
    md.append("# ÍNDICE TAXONÓMICO MAESTRO DE PLANTILLAS WORD (INDECOPI CC1)\n")
    md.append("> **ESTADO:** CATÁLOGO DE PRODUCCIÓN PARA GENERACIÓN AUTOMÁTICA  ")
    md.append(f"> **TOTAL DE PLANTILLAS DEPURADAS:** {total} archivos `.docx`  ")
    md.append("> **NORMATIVA LPAG APLICADA:** Decreto Supremo 006-2026-JUS (Vigente al 13 de setiembre de 2026)  ")
    md.append("> **DEPURACIÓN ORTOGRÁFICA:** Sanitización completa de mojibake y reglas léxicas popperianas aplicadas.\n")
    md.append("---\n")
    
    md.append("## 1. Distribución por Ramas de Seguro\n")
    md.append("| Código y Rama | Cantidad | % Total |")
    md.append("| :--- | :--- | :--- |")
    for rama, count in sorted(conteo_ramas.items()):
        pct = (count / total) * 100 if total > 0 else 0
        md.append(f"| `{rama}` | **{count}** | {pct:.1f}% |")
    md.append("\n---\n")
    
    md.append("## 2. Distribución por Materia / Servicio Denunciado\n")
    md.append("| Materia Denunciada | Cantidad |")
    md.append("| :--- | :--- |")
    for mat, count in conteo_materias.most_common():
        md.append(f"| `{mat}` | **{count}** |")
    md.append("\n---\n")

    md.append("## 3. Distribución por Configuración de Proveedores\n")
    md.append("| Tipo de Proveedor | Cantidad |")
    md.append("| :--- | :--- |")
    for prov, count in conteo_proveedores.most_common():
        md.append(f"| `{prov}` | **{count}** |")
    md.append("\n---\n")

    md.append("## 4. Distribución por Sujeto Denunciante\n")
    md.append("| Sujeto Denunciante | Cantidad |")
    md.append("| :--- | :--- |")
    for suj, count in conteo_sujetos.most_common():
        md.append(f"| `{suj}` | **{count}** |")
    md.append("\n---\n")

    md.append("## 5. Guía de Selección Rápida de Plantillas para Admisorios\n")
    md.append("Para generar una nueva resolución admisoria a partir de una denuncia escaneada con Visión Multimodal:\n")
    md.append("1. **Identificar la rama de seguro:** Desgravamen (`03`), Tarjetas (`04`), Vehicular (`01`), Vida (`02`), etc.")
    md.append("2. **Identificar la materia principal:** Negativa de cobertura (`negativa_cobertura`), anulación indebida (`anulacion_indebida`), falta de póliza (`falta_entrega_poliza`), etc.")
    md.append("3. **Identificar proveedores denunciados:** Si solo denuncia a la aseguradora (`1_ddo_aseguradora`), o banco y aseguradora (`2_ddos_banco_y_aseguradora`).")
    md.append("4. **Identificar sujeto:** Varón (`varon`), mujer (`mujer`), o sucesión intestada (`sucesion_intestada`).")
    md.append("5. **Cargar la plantilla `.docx` correspondiente de `plantillas_maestras/`**, la cual ya cuenta con:\n")
    md.append("   - Citas al **Decreto Supremo 006-2026-JUS**.")
    md.append("   - Cero imputaciones a inducción a error.")
    md.append("   - Formato institucional de página, fuentes Arial Narrow, sangrías escalonadas y notas al pie con One Dot Leader.\n")

    with open(INDEX_MD, 'w', encoding='utf-8') as fmd:
        fmd.write("\n".join(md))
        
    print(f"[OK] Reporte Markdown generado en: {INDEX_MD}")

if __name__ == "__main__":
    main()
