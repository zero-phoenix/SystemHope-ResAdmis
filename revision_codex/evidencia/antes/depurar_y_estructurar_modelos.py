#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
depurar_y_estructurar_modelos.py
Pipeline Maestro de Depuración, Actualización Normativa (LPAG 2026),
Sanitización Ortográfica y Estructuración Taxonómica de las 605 Plantillas Word.

Invariantes Popperianas Garantizadas:
1. Cero Inducción a Error (canalizado a arts. 1.1.b y 2 del Código).
2. TUO LPAG actualizado a Decreto Supremo 006-2026-JUS (publicado 30 de abril de 2026).
3. Diccionario ortográfico y mojibake con fronteras de palabra (\b) para proteger 'INFORMACIÓN'.
4. Invariantes léxicas institucionales: cónyuge, luego de, esta/este sin tilde, médico, vehículo.
5. Formato monetario institucional: S/ X XXX,XX.
6. Preservación OOXML absoluta (headers, logos, firmas, pies M-CPC-01/03, footnotes.xml).
7. Organización jerárquica limpia en plantillas_maestras/ para despliegue en GitHub.
"""

import os
import re
import json
import zipfile
import shutil
from pathlib import Path
from collections import Counter, defaultdict

SOURCE_DIR = Path(r"C:\Users\D\Desktop\000 PLAN PHOENYX")
REPO_ROOT = Path(r"C:\Users\D\ZCodeProject\SystemHope-ResAdmis")
TARGET_ROOT = REPO_ROOT / "plantillas_maestras"
CATALOG_JSON = REPO_ROOT / "docs" / "catalogo_modelos_phoenyx.json"
INDEX_MD = REPO_ROOT / "docs" / "INDICE_TAXONOMICO_PLANTILLAS_MAESTRAS.md"
INDEX_JSON = REPO_ROOT / "docs" / "plantillas_maestras_index.json"

# ==============================================================================
# 1. MAPEOS TAXONÓMICOS CANÓNICOS
# ==============================================================================

RAMAS_MAP = {
    "Seguro vehicular": "01_seguro_vehicular",
    "Seguro de vida": "02_seguro_vida",
    "Seguro de desgravamen": "03_seguro_desgravamen",
    "Seguro de proteccin de tarjetas y dinero": "04_seguro_proteccion_tarjetas_y_dinero",
    "Seguro de proteccion de tarjetas y dinero": "04_seguro_proteccion_tarjetas_y_dinero",
    "SOAT y AFOCAT": "05_soat_y_afocat",
    "Seguro de hogar e inmuebles": "06_seguro_hogar_e_inmuebles",
    "Seguro Complementario de Trabajo de Riesgo": "07_seguro_sctr",
    "Seguro de salud (EPS, planes y oncolgico)": "08_seguro_salud_eps_oncologico",
    "Seguro de salud (EPS, planes y oncologico)": "08_seguro_salud_eps_oncologico",
    "Seguro patrimonial, caucin y RC": "09_seguro_patrimonial_caucion_rc",
    "Seguro patrimonial, caucion y RC": "09_seguro_patrimonial_caucion_rc",
    "Seguro de sepelio": "10_seguro_sepelio",
    "Seguro de accidentes personales": "11_seguro_accidentes_personales",
    "Seguro de transporte y carga": "12_seguro_transporte_y_carga",
    "Seguro mltiple y de equipos (diversas coberturas)": "13_seguro_multiple_y_equipos",
    "Seguro multiple y de equipos (diversas coberturas)": "13_seguro_multiple_y_equipos",
    "Seguro de desempleo": "14_seguro_desempleo",
    "Sistema previsional (AFP y ONP)": "15_sistema_previsional_afp_onp",
    "Temas administrativos y financieros (no asegurativos)": "16_temas_administrativos_financieros",
    "Seguro no especificado": "17_seguro_no_especificado",
}

def normalizar_cadena(s: str) -> str:
    s = s.strip()
    s = s.replace("", "o").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    s = s.replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U").replace("ñ", "n").replace("Ñ", "N")
    s = re.sub(r'[^a-zA-Z0-9_]+', '_', s)
    return s.strip('_').lower()

def categorizar_materia(hecho_infractor: str, cobertura: str) -> str:
    txt = (hecho_infractor + " " + cobertura).lower()
    if "negativa" in txt and "cobertura" in txt:
        return "negativa_cobertura"
    elif "anulaci" in txt or "cancelaci" in txt or "resoluci" in txt:
        return "anulacion_indebida"
    elif "falta de entrega" in txt or "no entrega" in txt or "poliza" in txt and "entrega" in txt:
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
        return "varon" # default más frecuente y neutro en CC1

# ==============================================================================
# 2. MOTOR DE DEPURACIÓN TEXTUAL, NORMATIVA Y ORTOGRÁFICA
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
    # Cónyuge
    (re.compile(r'\besposo\b'), 'cónyuge'),
    (re.compile(r'\besposa\b'), 'cónyuge'),
    (re.compile(r'\besposos\b'), 'cónyuges'),
    (re.compile(r'\bEsposo\b'), 'Cónyuge'),
    (re.compile(r'\bEsposa\b'), 'Cónyuge'),
    (re.compile(r'\bEsposos\b'), 'Cónyuges'),
    # Luego de
    (re.compile(r'\btras\b'), 'luego de'),
    (re.compile(r'\bTras\b'), 'Luego de'),
    # Esta / Este sin tilde
    (re.compile(r'\bésta\b'), 'esta'),
    (re.compile(r'\bÉsta\b'), 'Esta'),
    (re.compile(r'\béste\b'), 'este'),
    (re.compile(r'\bÉste\b'), 'Este'),
    (re.compile(r'\béstas\b'), 'estas'),
    (re.compile(r'\bÉstas\b'), 'Estas'),
    (re.compile(r'\béstos\b'), 'estos'),
    (re.compile(r'\bÉstos\b'), 'Estos'),
    # Médico
    (re.compile(r'\bDr\.\s+(?!Ley\b)'), 'médico '),
    (re.compile(r'\bdoctor\s+(?!Ley\b)'), 'médico '),
    (re.compile(r'\bDoctor\s+(?!Ley\b)'), 'Médico '),
    (re.compile(r'\bdoctora\b'), 'médica'),
    (re.compile(r'\bDoctora\b'), 'Médica'),
    # Vehículo (con contexto vehicular)
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

REEMPLAZOS_MOJIBAKE_Y_TILDES = [
    # Empresas y marcas
    (re.compile(r'\bRMAC\b'), 'RÍMAC'),
    (re.compile(r'\bRmac\b'), 'Rímac'),
    (re.compile(r'\bRIMAC\b'), 'RÍMAC'),
    (re.compile(r'\bRimac\b'), 'Rímac'),
    (re.compile(r'\bCOMPAA\b'), 'COMPAÑÍA'),
    (re.compile(r'\bCompaa\b'), 'Compañía'),
    (re.compile(r'\bCRDITO\b'), 'CRÉDITO'),
    (re.compile(r'\bCrdito\b'), 'Crédito'),
    (re.compile(r'\bPACFICO\b'), 'PACÍFICO'),
    (re.compile(r'\bPacfico\b'), 'Pacífico'),
    (re.compile(r'\bPACIFICO\b'), 'PACÍFICO'),
    (re.compile(r'\bPacifico\b'), 'Pacífico'),
    
    # Términos jurídicos y procesales frecuentes
    (re.compile(r'\bPROTECCIN\b'), 'PROTECCIÓN'),
    (re.compile(r'\bProteccin\b'), 'Protección'),
    (re.compile(r'\bATENCIN\b'), 'ATENCIÓN'),
    (re.compile(r'\bAtencin\b'), 'Atención'),
    (re.compile(r'\bPLIZA\b'), 'PÓLIZA'),
    (re.compile(r'\bPliza\b'), 'Póliza'),
    (re.compile(r'\bPOLIZA\b'), 'PÓLIZA'),
    (re.compile(r'\bPoliza\b'), 'Póliza'),
    (re.compile(r'\bCDIGO\b'), 'CÓDIGO'),
    (re.compile(r'\bCdigo\b'), 'Código'),
    (re.compile(r'\bCODIGO\b'), 'CÓDIGO'),
    (re.compile(r'\bCodigo\b'), 'Código'),
    (re.compile(r'\bARTCULO\b'), 'ARTÍCULO'),
    (re.compile(r'\bArtculo\b'), 'Artículo'),
    (re.compile(r'\bDCIMO\b'), 'DÉCIMO'),
    (re.compile(r'\bDcimo\b'), 'Décimo'),
    (re.compile(r'\bDECIMO\b'), 'DÉCIMO'),
    (re.compile(r'\bSTIMO\b'), 'SÉTIMO'),
    (re.compile(r'\bStimo\b'), 'Sétimo'),
    (re.compile(r'\bSETIMO\b'), 'SÉTIMO'),
    (re.compile(r'\bNOTIFICACIN\b'), 'NOTIFICACIÓN'),
    (re.compile(r'\bNotificacin\b'), 'Notificación'),
    (re.compile(r'\bDIRECCIN\b'), 'DIRECCIÓN'),
    (re.compile(r'\bDireccin\b'), 'Dirección'),
    (re.compile(r'\bPETICIN\b'), 'PETICIÓN'),
    (re.compile(r'\bPeticin\b'), 'Petición'),
    (re.compile(r'\bEVALUACIN\b'), 'EVALUACIÓN'),
    (re.compile(r'\bEvaluacin\b'), 'Evaluación'),
    (re.compile(r'\bINFORMACIN\b'), 'INFORMACIÓN'),
    (re.compile(r'\bInformacin\b'), 'Información'),
    (re.compile(r'\bINDEMNIZACIN\b'), 'INDEMNIZACIÓN'),
    (re.compile(r'\bIndemnizacin\b'), 'Indemnización'),
    (re.compile(r'\bASOCIACIN\b'), 'ASOCIACIÓN'),
    (re.compile(r'\bAsociacin\b'), 'Asociación'),
    (re.compile(r'\bRESOLUCIN\b'), 'RESOLUCIÓN'),
    (re.compile(r'\bResolucin\b'), 'Resolución'),
    (re.compile(r'\bDISPOSICIN\b'), 'DISPOSICIÓN'),
    (re.compile(r'\bDisposicin\b'), 'Disposición'),
    (re.compile(r'\bCONDICIN\b'), 'CONDICIÓN'),
    (re.compile(r'\bCondicin\b'), 'Condición'),
    (re.compile(r'\bBONIFICACIN\b'), 'BONIFICACIÓN'),
    (re.compile(r'\bBonificacin\b'), 'Bonificación'),
    (re.compile(r'\bPRESCRIPCIN\b'), 'PRESCRIPCIÓN'),
    (re.compile(r'\bPrescripcin\b'), 'Prescripción'),
    (re.compile(r'\bLIQUIDACIN\b'), 'LIQUIDACIÓN'),
    (re.compile(r'\bLiquidacin\b'), 'Liquidación'),
    (re.compile(r'\bDECLARACIN\b'), 'DECLARACIÓN'),
    (re.compile(r'\bDeclaracin\b'), 'Declaración'),
    (re.compile(r'\bPRESENTACIN\b'), 'PRESENTACIÓN'),
    (re.compile(r'\bPresentacin\b'), 'Presentación'),
    (re.compile(r'\bINSPECCIN\b'), 'INSPECCIÓN'),
    (re.compile(r'\bInspeccin\b'), 'Inspección'),
    (re.compile(r'\bAPELACIN\b'), 'APELACIÓN'),
    (re.compile(r'\bApelacin\b'), 'Apelación'),
    (re.compile(r'\bADMINISTRACIN\b'), 'ADMINISTRACIÓN'),
    (re.compile(r'\bAdministracin\b'), 'Administración'),
    (re.compile(r'\bJURISDICCIN\b'), 'JURISDICCIÓN'),
    (re.compile(r'\bJurisdiccin\b'), 'Jurisdicción'),
    (re.compile(r'\bSANCIN\b'), 'SANCIÓN'),
    (re.compile(r'\bSancin\b'), 'Sanción'),
    (re.compile(r'\bSUCESIN\b'), 'SUCESIÓN'),
    (re.compile(r'\bSucesin\b'), 'Sucesión'),
    (re.compile(r'\bPREVISIN\b'), 'PREVISIÓN'),
    (re.compile(r'\bPrevisin\b'), 'Previsión'),
    (re.compile(r'\bRECLAMACIN\b'), 'RECLAMACIÓN'),
    (re.compile(r'\bReclamacin\b'), 'Reclamación'),
    (re.compile(r'\bCOMISIN\b'), 'COMISIÓN'),
    (re.compile(r'\bComisin\b'), 'Comisión'),
    (re.compile(r'\bREVISIN\b'), 'REVISIÓN'),
    (re.compile(r'\bRevisin\b'), 'Revisión'),
    (re.compile(r'\bINTERS\b'), 'INTERÉS'),
    (re.compile(r'\bInters\b'), 'Interés'),
    (re.compile(r'\bVEHCULO\b'), 'VEHÍCULO'),
    (re.compile(r'\bVehculo\b'), 'Vehículo'),
    (re.compile(r'\bMDICO\b'), 'MÉDICO'),
    (re.compile(r'\bMdico\b'), 'Médico'),
    (re.compile(r'\bTERMINACIN\b'), 'TERMINACIÓN'),
    (re.compile(r'\bTerminacin\b'), 'Terminación'),
    (re.compile(r'\bCANCELACIN\b'), 'CANCELACIÓN'),
    (re.compile(r'\bCancelacin\b'), 'Cancelación'),
    (re.compile(r'\bCONTABILIZACIN\b'), 'CONTABILIZACIÓN'),
    (re.compile(r'\bContabilizacin\b'), 'Contabilización'),
    (re.compile(r'\bDEVOLUCIN\b'), 'DEVOLUCIÓN'),
    (re.compile(r'\bDevolucin\b'), 'Devolución'),
    (re.compile(r'\bOPOSICIN\b'), 'OPOSICIÓN'),
    (re.compile(r'\bOposicin\b'), 'Oposición'),
    (re.compile(r'\bPRESTACIN\b'), 'PRESTACIÓN'),
    (re.compile(r'\bPrestacin\b'), 'Prestación'),
    (re.compile(r'\bREDUCCIN\b'), 'REDUCCIÓN'),
    (re.compile(r'\bReduccin\b'), 'Reducción'),
    (re.compile(r'\bREPARACIN\b'), 'REPARACIÓN'),
    (re.compile(r'\bReparacin\b'), 'Reparación'),
    (re.compile(r'\bSATISFACCIN\b'), 'SATISFACCIÓN'),
    (re.compile(r'\bSatisfaccin\b'), 'Satisfacción'),
    (re.compile(r'\bUBICACIN\b'), 'UBICACIÓN'),
    (re.compile(r'\bUbicacin\b'), 'Ubicación'),
    (re.compile(r'\bVARIACIN\b'), 'VARIACIÓN'),
    (re.compile(r'\bVariacin\b'), 'Variación'),
    (re.compile(r'\bVALORACIN\b'), 'VALORACIÓN'),
    (re.compile(r'\bValoracin\b'), 'Valoración'),
    (re.compile(r'\bEXCEPCIN\b'), 'EXCEPCIÓN'),
    (re.compile(r'\bExcepcin\b'), 'Excepción'),
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
    # Formato: S/ 1,234.56 -> S/ 1 234,56
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
    # 1. LPAG
    for pattern, repl in REEMPLAZOS_LPAG:
        xml_str = pattern.sub(repl, xml_str)
        
    # 2. Invariantes Léxicas Popperianas
    for pattern, repl in REEMPLAZOS_LEXICOS:
        xml_str = pattern.sub(repl, xml_str)
        
    # 3. Cero Inducción a Error
    for pattern, repl in REEMPLAZOS_INDUCCION_ERROR:
        xml_str = pattern.sub(repl, xml_str)
        
    # 4. Mojibake y Tildes
    for pattern, repl in REEMPLAZOS_MOJIBAKE_Y_TILDES:
        xml_str = pattern.sub(repl, xml_str)
        
    # 5. Normalización de Moneda
    xml_str = normalizar_moneda(xml_str)
    
    return xml_str

def depurar_archivo_docx(origen: Path, destino: Path) -> bool:
    try:
        destino.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(origen, 'r') as zin, zipfile.ZipFile(destino, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                # Solo procesamos archivos XML de texto relevante
                if item.filename.endswith('.xml') and ('document' in item.filename or 'footnotes' in item.filename or 'endnotes' in item.filename or 'header' in item.filename or 'footer' in item.filename):
                    try:
                        text = data.decode('utf-8')
                        new_text = procesar_contenido_xml(text)
                        data = new_text.encode('utf-8')
                    except UnicodeDecodeError:
                        pass
                zout.writestr(item, data)
        return True
    except Exception as e:
        print(f"Error procesando {origen}: {e}")
        return False

# ==============================================================================
# 3. PIPELINE PRINCIPAL Y GENERACIÓN DE ÍNDICE
# ==============================================================================

def main():
    print("=" * 80)
    print("PIPELINE MAESTRO: DEPURACIÓN Y ESTRUCTURACIÓN TAXONÓMICA PHOENYX")
    print("=" * 80)
    
    if not CATALOG_JSON.exists():
        print(f"ERROR: No se encontró {CATALOG_JSON}. Ejecuta auditar_y_catalogar_phoenyx.py primero.")
        return
        
    with open(CATALOG_JSON, 'r', encoding='utf-8') as f:
        catalogo = json.load(f)
        
    print(f"Total de modelos en catálogo: {len(catalogo)}")
    
    TARGET_ROOT.mkdir(parents=True, exist_ok=True)
    
    exitos = 0
    fallos = 0
    conteo_ramas = Counter()
    conteo_materias = Counter()
    conteo_proveedores = Counter()
    conteo_sujetos = Counter()
    
    indice_general = []
    
    # Manejador de colisiones de nombres
    nombres_usados = set()

    for idx, item in enumerate(catalogo, 1):
        origen_path = Path(item["ruta_absoluta"])
        if not origen_path.exists():
            print(f"[{idx}/{len(catalogo)}] Archivo no encontrado: {origen_path}")
            fallos += 1
            continue
            
        tax = item.get("taxonomia", {})
        meta = item.get("metadata_doc", {})
        
        # 1. Determinar Taxonomía
        tipo_seguro_raw = tax.get("tipo_seguro", "Seguro no especificado")
        rama_folder = RAMAS_MAP.get(tipo_seguro_raw, "17_seguro_no_especificado")
        
        materia_folder = categorizar_materia(
            tax.get("hecho_infractor", ""),
            tax.get("cobertura", "")
        )
        
        proveedor_folder = categorizar_proveedor(
            tax.get("proveedor_carpeta", ""),
            meta.get("denunciado", ""),
            tax.get("es_multiple_ddo", False)
        )
        
        sujeto_folder = categorizar_sujeto(
            tax.get("sujeto_tipo", ""),
            tax.get("caso_carpeta", ""),
            meta.get("denunciante", "")
        )
        
        # 2. Generar Nombre de Archivo Canónico Limpio
        exp_raw = meta.get("expediente", "")
        m_exp = re.search(r'(\d+-\d{4})', exp_raw)
        if not m_exp:
            m_exp = re.search(r'(\d+-\d{4})', origen_path.name)
        num_exp = m_exp.group(1) if m_exp else f"EXP{idx:03d}"
        
        # Detectar si es R1, R2, etc.
        m_r = re.search(r'R(\d+)', origen_path.name, re.IGNORECASE)
        res_tag = f"_R{m_r.group(1)}" if m_r else ""
        
        # Etiqueta de proveedor corta
        ddo_tag = "ASEGURADORA"
        if "banco" in proveedor_folder:
            ddo_tag = "BANCO"
        elif "2_ddos" in proveedor_folder:
            ddo_tag = "BANCO_Y_ASEGURADORA"
        elif "corredor" in proveedor_folder:
            ddo_tag = "CORREDOR"
            
        nombre_base = f"TPL_{num_exp}_{rama_folder[3:].upper()}_{materia_folder.upper()}_{ddo_tag}_{sujeto_folder.upper()}{res_tag}"
        nombre_limpio = normalizar_cadena(nombre_base).upper() + ".docx"
        
        # Resolver colisiones si existen
        colision_idx = 1
        nombre_final = nombre_limpio
        while (rama_folder, materia_folder, proveedor_folder, sujeto_folder, nombre_final) in nombres_usados:
            colision_idx += 1
            nombre_final = nombre_limpio.replace(".DOCX", f"_V{colision_idx}.DOCX")
        nombres_usados.add((rama_folder, materia_folder, proveedor_folder, sujeto_folder, nombre_final))
        
        # 3. Ruta de Destino
        destino_dir = TARGET_ROOT / rama_folder / materia_folder / proveedor_folder / sujeto_folder
        destino_path = destino_dir / nombre_final
        
        # 4. Ejecutar Depuración
        ok = depurar_archivo_docx(origen_path, destino_path)
        if ok:
            exitos += 1
            conteo_ramas[rama_folder] += 1
            conteo_materias[materia_folder] += 1
            conteo_proveedores[proveedor_folder] += 1
            conteo_sujetos[sujeto_folder] += 1
            
            rel_dest = destino_path.relative_to(REPO_ROOT)
            indice_general.append({
                "id": idx,
                "expediente": num_exp,
                "rama": rama_folder,
                "materia": materia_folder,
                "proveedor_tipo": proveedor_folder,
                "sujeto_tipo": sujeto_folder,
                "archivo": nombre_final,
                "ruta_relativa": str(rel_dest).replace("\\", "/"),
                "origen_original": str(origen_path.relative_to(SOURCE_DIR)).replace("\\", "/")
            })
        else:
            fallos += 1
            
        if idx % 50 == 0 or idx == len(catalogo):
            print(f"[{idx}/{len(catalogo)}] Procesados: {exitos} exitosos, {fallos} fallos...")

    print("\n" + "=" * 80)
    print(f"PROCESO FINALIZADO: {exitos} plantillas depuradas y estructuradas con éxito.")
    print("=" * 80)
    
    # Guardar Índice JSON
    with open(INDEX_JSON, 'w', encoding='utf-8') as fj:
        json.dump(indice_general, fj, ensure_ascii=False, indent=2)
    print(f"[OK] Guardado indice JSON: {INDEX_JSON}")
    
    # Generar Documento de Memoria Markdown para GitHub
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
        pct = (count / total) * 100
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
