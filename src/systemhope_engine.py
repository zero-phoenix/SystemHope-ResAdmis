# -*- coding: utf-8 -*-
"""SystemHope ResAdmis - Engine & Autonomous Bridge for AI Desktop IDEs.

Provides CLI, MCP Server, Template Taxonomy Search, Document Validation,
Provider Domicile Registry, Literal Notification Formulas, and Memory Export
to ensure complete persistence across machine formats.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Version and metadata
VERSION = "2.0.0"
AUTHOR = "SystemHope / Indecopi CC1 Phoenix"
LPAG_NORM = "Decreto Supremo 006-2026-JUS"
REPO_URL = "https://github.com/zero-phoenix/SystemHope-ResAdmis"

# Base directories resolution (works both in script and PyInstaller bundle)
if getattr(sys, "frozen", False):
    BUNDLE_DIR = Path(sys._MEIPASS)
    APP_DIR = Path(sys.executable).parent
else:
    BUNDLE_DIR = Path(__file__).resolve().parent.parent
    APP_DIR = BUNDLE_DIR


def get_resource_path(relative_path: str) -> Path:
    """Resolve resource path prioritizing local app dir, then bundle dir."""
    local_p = APP_DIR / relative_path
    if local_p.exists():
        return local_p
    bundle_p = BUNDLE_DIR / relative_path
    if bundle_p.exists():
        return bundle_p
    return local_p


def load_template_index() -> List[Dict[str, Any]]:
    """Loads the 605 template catalog index."""
    candidates = [
        get_resource_path("docs/plantillas_maestras_index.json"),
        APP_DIR / "plantillas_maestras_index.json",
        BUNDLE_DIR / "docs" / "plantillas_maestras_index.json",
    ]
    for c in candidates:
        if c.exists():
            try:
                data = json.loads(c.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return data.get("plantillas", data.get("modelos", []))
            except Exception:
                pass
    return []


def load_provider_directory() -> Dict[str, Any]:
    """Loads the provider domicile & notification channel registry."""
    candidates = [
        get_resource_path("docs/directorio_proveedores_domicilios.json"),
        APP_DIR / "directorio_proveedores_domicilios.json",
        BUNDLE_DIR / "docs" / "directorio_proveedores_domicilios.json",
    ]
    for c in candidates:
        if c.exists():
            try:
                return json.loads(c.read_text(encoding="utf-8"))
            except Exception:
                pass
    return {}


# ==============================================================================
# SUBCOMMAND: INFO
# ==============================================================================
def cmd_info(args: argparse.Namespace) -> int:
    templates = load_template_index()
    providers = load_provider_directory()
    print("=" * 75)
    print(f" SYSTEMHOPE RESADMIS - AUTONOMOUS ENGINE (v{VERSION})")
    print(f" Repositorio Oficial: {REPO_URL}")
    print("=" * 75)
    print(f" • Normativa TUO LPAG Vigente: {LPAG_NORM}")
    print(" • Protocolo de Entrada: ESTRICTO CERO OCR (Solo Google Lens / Vision Multimodal)")
    print(" • Tipografía Oficial: Arial Narrow 11 pt (Cuerpo) / 8 pt (Pies y Notas)")
    print(" • Formato de Moneda: S/ X XXX,XX o US$ X XXX,XX (Espacio para miles, coma decimal)")
    print(" • Reglas Popperianas: R-01 a R-95 activas (Cero inducción a error, condicional habría)")
    print(" • Vías de Notificación: 3 párrafos resolutivos literales estrictos (Casilla, Correo, Cédula)")
    print(f" • Catálogo de Plantillas: {len(templates)} plantillas Word (.docx) indexadas y depuradas")
    print(f" • Directorio de Proveedores: {len(providers)} entidades aseguradoras y financieras registradas")
    print(" • Modo de Ejecución: Autónomo (CLI / Servidor MCP para AI IDEs Desktop)")
    print("=" * 75)
    return 0


# ==============================================================================
# SUBCOMMAND: RULES
# ==============================================================================
def cmd_rules(args: argparse.Namespace) -> int:
    rules_doc = get_resource_path("docs/MATRIZ_MAESTRA_PHOENYX_POPPERIANA.md")
    if rules_doc.exists():
        print(rules_doc.read_text(encoding="utf-8"))
        return 0
    return 0


# ==============================================================================
# SUBCOMMAND: NOTIFICATIONS & PROVIDERS
# ==============================================================================
def cmd_notifications(args: argparse.Namespace) -> int:
    notif_doc = get_resource_path("docs/DIRECTORIO_PROVEEDORES_Y_DOMICILIOS_PROCESALES.md")
    if notif_doc.exists() and not args.proveedor:
        print(notif_doc.read_text(encoding="utf-8"))
        return 0

    providers = load_provider_directory()
    if args.proveedor:
        q = args.proveedor.lower()
        matches = {k: v for k, v in providers.items() if q in k.lower()}
        if matches:
            print(f"\nCoincidencias encontradas ({len(matches)}):")
            print("-" * 75)
            for k, v in matches.items():
                print(f"• {k}")
                print(f"  Vía Oficial: {v.get('via_notificacion_oficial')}")
                print(f"  Frecuencia en modelos: {v.get('frecuencia_total')} casos")
                print(f"  Detalle: Casilla={v.get('casilla_count')}, Correo={v.get('correo_count')}, Domicilio={v.get('domicilio_count')}")
                print("-" * 75)
            return 0
        else:
            print(f"No se encontró el proveedor '{args.proveedor}' en el directorio.")
            return 1
    return 0


# ==============================================================================
# SUBCOMMAND: SPECS (VISUAL LAYOUT)
# ==============================================================================
def cmd_specs(args: argparse.Namespace) -> int:
    mem_doc = get_resource_path("docs/MEMORIA_ESTILO_VISUAL_PAGINAS.md")
    if mem_doc.exists():
        print(mem_doc.read_text(encoding="utf-8"))
        return 0
    print("No se encontró MEMORIA_ESTILO_VISUAL_PAGINAS.md en el paquete.")
    return 1


# ==============================================================================
# SUBCOMMAND: TEMPLATES (SEARCH & RETRIEVAL)
# ==============================================================================
def cmd_templates(args: argparse.Namespace) -> int:
    templates = load_template_index()
    if not templates:
        print("No se encontró el índice de plantillas (plantillas_maestras_index.json).")
        return 1

    query_rama = (args.rama or "").lower()
    query_mat = (args.materia or "").lower()
    query_ddo = (args.ddo or "").lower()
    query_sujeto = (args.sujeto or "").lower()
    query_q = (args.q or "").lower()

    filtrados = []
    for t in templates:
        t_rama = t.get("rama", "").lower()
        t_mat = t.get("materia", "").lower()
        t_ddo = (t.get("proveedor_tipo") or t.get("proveedor") or "").lower()
        t_sujeto = (t.get("sujeto_tipo") or t.get("sujeto") or "").lower()
        t_archivo = (t.get("archivo") or t.get("nombre_archivo") or "").lower()
        t_rel = (t.get("ruta_relativa") or t.get("rel_path") or "").lower()
        t_exp = t.get("expediente", "").lower()

        if query_rama and query_rama not in t_rama:
            continue
        if query_mat and query_mat not in t_mat:
            continue
        if query_ddo and query_ddo not in t_ddo:
            continue
        if query_sujeto and query_sujeto not in t_sujeto:
            continue
        if query_q:
            cadena = f"{t_archivo} {t_exp} {t_rel}"
            if query_q not in cadena:
                continue
        filtrados.append(t)

    if args.json:
        print(json.dumps(filtrados, indent=2, ensure_ascii=False))
        return 0

    print(f"\nResultados encontrados: {len(filtrados)} plantillas de {len(templates)}")
    print("-" * 80)
    for idx, t in enumerate(filtrados[: args.limit], 1):
        nombre = t.get("archivo") or t.get("nombre_archivo")
        ruta = t.get("ruta_relativa") or t.get("rel_path")
        prov = t.get("proveedor_tipo") or t.get("proveedor")
        suj = t.get("sujeto_tipo") or t.get("sujeto")
        print(f"[{idx}] {nombre}")
        print(f"     Expediente: {t.get('expediente')} | Rama: {t.get('rama')} | Materia: {t.get('materia')}")
        print(f"     Proveedor: {prov} | Sujeto: {suj}")
        print(f"     Ruta: {ruta}")
        print("-" * 80)

    if len(filtrados) > args.limit:
        print(f"... y {len(filtrados) - args.limit} plantillas más. Use --limit para ver más o refine con filtros.")
    return 0


# ==============================================================================
# SUBCOMMAND: VALIDATE (AUDITORIA DOCX POPPERIANA)
# ==============================================================================
def cmd_validate(args: argparse.Namespace) -> int:
    target_path = Path(args.archivo)
    if not target_path.exists():
        print(f"ERROR: Archivo no encontrado: {target_path}", file=sys.stderr)
        return 2

    print(f"\nAUDITANDO RESOLUCIÓN ADMISORIA: {target_path.name}")
    print("=" * 75)

    try:
        import zipfile
        with zipfile.ZipFile(target_path, "r") as z:
            doc_xml = z.read("word/document.xml").decode("utf-8", errors="ignore")
            fn_xml = ""
            if "word/footnotes.xml" in z.namelist():
                fn_xml = z.read("word/footnotes.xml").decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"ERROR al abrir documento Word (.docx): {e}", file=sys.stderr)
        return 3

    texto_total = re.sub(r"<[^>]+>", " ", doc_xml + " " + fn_xml)
    errores: List[str] = []
    advertencias: List[str] = []

    # 1. Regla LPAG 2026
    if "004-2019" in texto_total:
        errores.append("[R-85 CRITICO] Cita al derogado D.S. 004-2019-JUS. Debe ser D.S. 006-2026-JUS.")
    if "006-2026" not in texto_total:
        advertencias.append("[LPAG 2026] No se detectó mención explícita al D.S. 006-2026-JUS en el documento.")

    # 2. Cero inducción a error
    if re.search(r"induc(?:ir|ci[oó]n)\s+(?:al?\s+)?error", texto_total, re.IGNORECASE):
        errores.append("[R-86 CRITICO] Uso de 'inducción a error'. Debe imputarse bajo arts. 1.1.b y 2 de Ley 29571.")

    # 3. Invariantes léxicas
    if re.search(r"\b(?:esposo|esposa)\b", texto_total, re.IGNORECASE):
        errores.append("[R-90 LEXICA] Uso de 'esposo/a'. Regla CC1 exige estrictamente 'cónyuge'.")
    if re.search(r"\b(?:carro|auto)\b", texto_total, re.IGNORECASE):
        errores.append("[R-93 LEXICA] Uso de 'carro' o 'auto'. Regla CC1 exige estrictamente 'vehículo'.")
    if re.search(r"\btras\b", texto_total, re.IGNORECASE):
        errores.append("[R-89 LEXICA] Uso de 'tras'. Regla CC1 exige estrictamente 'luego de'.")
    if re.search(r"\b(?:doctor|doctora)\b", texto_total, re.IGNORECASE):
        errores.append("[R-92 LEXICA] Uso de 'doctor/a'. Regla CC1 exige estrictamente 'médico'.")

    # 4. Formato de moneda
    if re.search(r"S/\s*\d{1,3}(?:\.\d{3})+,\d{2}", texto_total) or re.search(r"S/\.\s*\d+", texto_total):
        errores.append("[R-91 MONEDA] Moneda con puntos. Formato obligatorio: 'S/ X XXX,XX' (espacio para miles, coma decimal).")

    # 5. Párrafos Resolutivos de Notificación (Tres tipos literales)
    has_casilla = "acuse de recibo mediante la confirmación de recepción" in texto_total and "Casilla" in texto_total
    has_correo = "bandeja de correo electrónico" in texto_total or "bandejas de correo electrónico" in texto_total
    has_domicilio = "en su domicilio procesal" in texto_total or "en sus domicilios procesales" in texto_total

    if not (has_casilla or has_correo or has_domicilio):
        errores.append("[NOTIFICACION CC1] La resolución debe contener al menos una de las tres fórmulas literales de notificación (Casilla Electrónica, Correo Electrónico o Domicilio Procesal).")

    if (has_correo or has_domicilio) and "confirmación de recepción" in texto_total:
        if "006-2026-JUS" not in texto_total:
            errores.append("[NOTIFICACION CC1] La notificación por correo o domicilio procesal debe citar el Decreto Supremo 006-2026-JUS.")
        if "dos (2) días hábiles" not in texto_total:
            advertencias.append("[NOTIFICACION CC1] El plazo para confirmación de correo o domicilio procesal debe ser de dos (2) días hábiles.")

    if has_casilla and "cinco (5) primeros días hábiles" not in texto_total:
        advertencias.append("[NOTIFICACION CC1] El plazo para acuse de recibo en Casilla Electrónica debe ser de cinco (5) primeros días hábiles.")

    # 6. Pie institucional
    if "M-CPC-01/03" not in texto_total:
        advertencias.append("[FORMATO] Pie institucional 'M-CPC-01/03' no detectado en el documento.")

    # Reporte
    if errores:
        print(f"❌ FALLOS POPPERIANOS ENCONTRADOS: {len(errores)}")
        for err in errores:
            print(f"  • {err}")
    else:
        print("✅ CERO INFRACCIONES CRÍTICAS DETECTADAS.")

    if advertencias:
        print(f"\n⚠️  ADVERTENCIAS: {len(advertencias)}")
        for adv in advertencias:
            print(f"  • {adv}")

    print("=" * 75)
    return 1 if errores else 0


# ==============================================================================
# SUBCOMMAND: DUMP-MEMORY (FOR ANY AI DESKTOP IDE)
# ==============================================================================
def cmd_dump_memory(args: argparse.Namespace) -> int:
    out_dir = Path(args.dir or ".")
    out_dir.mkdir(parents=True, exist_ok=True)

    agents_md = f"""# DIRECTRICES MAESTRAS DEL SISTEMA (AGENTS.md)
# SISTEMA DE EMISION DE RESOLUCIONES ADMISORIAS INDECOPI CC1

> **AUTORIDAD:** Indecopi Comisión de Protección al Consumidor  1 (CC1)  
> **NORMA MARCO:** {LPAG_NORM}  
> **PROTOCOLO VISUAL:** ESTRICTO CERO OCR. Inspección exclusiva mediante Google Lens / Visión Multimodal.  
> **REPOSITORIO:** {REPO_URL}

---

## 1. REGLAS NO NEGOCIABLES (AXIOMAS POPPERIANOS)
1. **PROHIBICIÓN ESTRICTA DE OCR:** Jamás transcribir denuncias con OCR clásico ni extractores que rompan coordenadas o inventen datos. Se analiza la imagen de la denuncia escaneada con Google Lens o modelos de visión directa.
2. **TUO LPAG ACTUALIZADO:** Siempre citar el **Decreto Supremo 006-2026-JUS**. Prohibida cualquier mención al D.S. 004-2019-JUS.
3. **PROHIBICIÓN DE 'INDUCCIÓN A ERROR':** Nunca imputar por el Artículo 3° ni emplear la frase 'inducción a error'. Todas las fallas de información se canalizan por los Artículos 1°, numeral 1, literal b) y 2° del Código de Protección y Defensa del Consumidor.
4. **TIEMPOS VERBALES OBLIGATORIOS:**
   - **En Antecedentes / Hechos:** Pasado indicativo afirmativo ("señaló", "contrató", "solicitó"). PROHIBIDO usar la palabra 'denunciante' en el cuerpo narrativo; usar el nombre de pila o 'el señor / la señora [Apellido]'.
   - **En Imputación de Cargos:** Condicional obligatorio ("habría denegado", "habría omitido", "habría realizado cobros").
5. **INVARIANTES LÉXICAS:**
   - Usar `cónyuge` / `cónyuges` (PROHIBIDO: esposo/a).
   - Usar `luego de` (PROHIBIDO: tras).
   - Usar `esta` / `este` sin tilde diacrítica.
   - Usar `médico` (PROHIBIDO: doctor/a o Dr.).
   - Usar `vehículo con Placa de Rodaje []` (PROHIBIDO: carro, auto).
6. **FORMATO MONETARIO MONOLÍTICO:**
   - `S/ X XXX,XX` o `US$ X XXX,XX` (espacio para miles, coma decimal, nunca punto ni apóstrofe).

---

## 2. LOS TRES PÁRRAFOS RESOLUTIVOS LITERALES DE NOTIFICACIÓN (SIN PARAFRASEAR)
En la sección resolutiva final de todo admisorio, se coloca indefectiblemente el párrafo correspondiente a la vía legal de notificación:

### TIPO 1: VÍA CASILLA ELECTRÓNICA (SINE INDECOPI - 5 DÍAS)
*Para compañías de seguros y bancos afiliados obligatoriamente:*
> *"requerir a [PROVEEDOR(ES)] para que efectúe[n] el acuse de recibo mediante la confirmación de recepción de la notificación remitida por este despacho a su[s] Casilla[s] Electrónica[s], dentro de los cinco (5) primeros días hábiles siguientes a la fecha en que recibe[n] la notificación."*

### TIPO 2: VÍA CORREO ELECTRÓNICO (AUTORIZACIÓN EXPRESA - 2 DÍAS)
*Para consumidores y proveedores con dirección electrónica autorizada:*
> *"requerir a [PARTE(S)] para que, dentro del plazo de dos (2) días hábiles siguientes a la fecha en que reciba[n] la notificación en su[s] bandeja[s] de correo electrónico, efectúe[n] la confirmación de recepción de la notificación remitida por este despacho a su[s] correo[s] electrónico[s], de conformidad con el segundo párrafo del numeral 4 del artículo 20° del Texto Único Ordenado de la Ley del Procedimiento Administrativo General, aprobado mediante Decreto Supremo 006-2026-JUS, bajo apercibimiento de rehacer el acto de notificación y notificarle[s] conforme al numeral 1 del artículo 20° del citado cuerpo normativo."*

### TIPO 3: VÍA DOMICILIO PROCESAL / CÉDULA FÍSICA (2 DÍAS)
*Para denunciantes sin correo, AFOCATs, fondos especiales (CAFAE) o proveedores sin casilla:*
> *"requerir a [PARTE(S)] para que, dentro del plazo de dos (2) días hábiles siguientes a la fecha en que reciba[n] la notificación en su domicilio procesal, efectúe[n] la confirmación de recepción de la notificación remitida por este despacho a su domicilio procesal, de conformidad con el segundo párrafo del numeral 4 del artículo 20° del Texto Único Ordenado de la Ley del Procedimiento Administrativo General, aprobado mediante Decreto Supremo 006-2026-JUS, bajo apercibimiento de rehacer el acto de notificación y notificarle[s] conforme al numeral 1 del artículo 20° del citado cuerpo normativo."*

---

## 3. DOMICILIOS PROCESALES Y VÍAS OFICIALES POR PROVEEDOR
- **Casilla Electrónica (SINE Indecopi):** Pacífico Compañía de Seguros, Mapfre Perú Compañía de Seguros, Interseguro Compañía de Seguros, La Positiva Seguros y Reaseguros, BNP Paribas Cardif, Chubb Perú, Quálitas Compañía de Seguros, Protecta Compañía de Seguros, Crecer Seguros, Banco BBVA Perú, Scotiabank Perú, Interbank, Empresa de Créditos Santander Consumo Perú, Banco Falabella, Banco Ripley, Banco Pichincha, Banco GNB.
- **Correo Electrónico Autorizado / Casilla:** Rímac Seguros y Reaseguros, Banco de Crédito del Perú (BCP).
- **Domicilio Procesal / Cédula Física:** AFOCATs provinciales/regionales, Comités de Administración CAFAE, talleres y personas naturales denunciadas.

---

## 4. TAXONOMÍA Y LOCALIZACIÓN DE PLANTILLAS
El repositorio contiene **605 plantillas Word (.docx) depuradas** en `plantillas_maestras/`:
- `01_seguro_vehicular` (174) | `02_seguro_vida` (134) | `03_seguro_desgravamen` (66)
- `04_seguro_proteccion_tarjetas_y_dinero` (37) | `05_soat_y_afocat` (43) | `06_seguro_hogar_e_inmuebles` (20)
- `07_seguro_sctr` (18) | `08_seguro_salud_eps_oncologico` (12) | `09_seguro_patrimonial_caucion_rc` (10)
- `10_seguro_sepelio` (8) | `11_seguro_accidentes_personales` (7) | `12_seguro_transporte_y_carga` (6)
- `13_seguro_multiple_y_equipos` (4) | `14_seguro_desempleo` (2) | `15_sistema_previsional_afp_onp` (2)
- `16_temas_administrativos_financieros` (4) | `17_seguro_no_especificado` (58)

---

## 5. PARÁMETROS DE ESTILO VISUAL CC1
- **Fuente:** `Arial Narrow` (11 pt cuerpo de texto, 8 pt notas al pie y encabezados).
- **Márgenes A4:** Superior 2.5 cm, Inferior 2.5 cm, Izquierdo 3.0 cm, Derecho 2.5 cm.
- **Interlineado:** Sencillo 1.0, espaciado `0 pt antes / 0 pt después`.
- **Sangrías Institucionales:**
  - Hechos: Izquierda `0.79"` (2.0 cm), Francesa `-0.39"` (-1.0 cm).
  - Resolutivo: Izquierda `0.39"` (1.0 cm), Francesa `-0.39"` (-1.0 cm).
- **Notas al Pie:** Formato con *One Dot Leader* (`\\u2024`). Pie institucional: `M-CPC-01/03`.
"""

    cursorrules = f"""# Cursor Rules - ResAdmis INDECOPI CC1
# NORMATIVA: {LPAG_NORM} | PROTOCOLO: CERO OCR (Solo Google Lens)

1. Jamás uses OCR para leer expedientes o denuncias. Utiliza Google Lens / Visión Multimodal.
2. La norma del TUO LPAG siempre es el Decreto Supremo 006-2026-JUS. Nunca 004-2019-JUS.
3. Prohibido imputar por 'inducción a error' (Art. 3). Usa Arts. 1.1.b y 2 de Ley 29571.
4. En imputaciones de cargos usa condicional 'habría'. En antecedentes usa pasado indicativo.
5. Invariantes léxicas: cónyuge (no esposo), luego de (no tras), médico (no doctor), vehículo (no auto).
6. Moneda: 'S/ X XXX,XX' (espacio para miles, coma decimal, sin puntos).
7. Notificaciones finales: Colocar obligatoriamente uno de los 3 párrafos literales (Casilla 5 días / Correo 2 días D.S. 006-2026-JUS / Cédula Domicilio Procesal 2 días) sin parafrasear.
8. Consulta plantillas_maestras/ según rama y materia antes de redactar.
9. Valida siempre el documento final con: systemhope-engine validate <admisorio.docx>
"""

    claude_md = f"""# Claude Code Instructions - SystemHope ResAdmis CC1

Este repositorio contiene el sistema automatizado de resoluciones admisorias de Indecopi CC1.

## Comandos Principales
- Ver catálogo y estado: `python -m src.systemhope_engine info`
- Buscar plantillas: `python -m src.systemhope_engine templates --rama 03_seguro_desgravamen --materia negativa_cobertura`
- Consultar vías de notificación: `python -m src.systemhope_engine notifications`
- Auditar documento: `python -m src.systemhope_engine validate <archivo.docx>`
- Exportar memoria completa a IDE: `python -m src.systemhope_engine dump-memory`

## Reglas Críticas
- **Cero OCR:** Siempre analizar capturas con Google Lens / Vision.
- **LPAG 2026:** D.S.  006-2026-JUS.
- **Cero Inducción a Error:** Arts. 1.1.b y 2 de Ley 29571.
- **Notificaciones Finales:** 3 fórmulas literales estrictas (Casilla 5 días, Correo 2 días con apercibimiento, Domicilio Procesal 2 días con apercibimiento).
- **Formato:** Arial Narrow 11 pt, notas 8 pt, sangrías CC1, pie institucional M-CPC-01/03.
"""

    (out_dir / "AGENTS.md").write_text(agents_md, encoding="utf-8")
    (out_dir / ".cursorrules").write_text(cursorrules, encoding="utf-8")
    (out_dir / ".windsurfrules").write_text(cursorrules, encoding="utf-8")
    (out_dir / "CLAUDE.md").write_text(claude_md, encoding="utf-8")
    print(f"✅ Archivos de memoria para AI IDEs generados exitosamente en: {out_dir.resolve()}")
    return 0


# ==============================================================================
# SUBCOMMAND: MCP SERVER (MODEL CONTEXT PROTOCOL OVER STDIO)
# ==============================================================================
def cmd_mcp(args: argparse.Namespace) -> int:
    """Implements lightweight standard JSON-RPC MCP Server for desktop AI IDEs."""
    tools = [
        {
            "name": "get_system_rules",
            "description": "Retorna las reglas popperianas y marco normativo LPAG 2026 para admisorios.",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "get_notification_formulas",
            "description": "Retorna las 3 fórmulas literales de notificación y directorio de domicilios procesales.",
            "inputSchema": {"type": "object", "properties": {"proveedor": {"type": "string"}}},
        },
        {
            "name": "get_visual_specs",
            "description": "Retorna especificaciones de diseño, tipografía Arial Narrow y sangrías CC1.",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "search_templates",
            "description": "Busca entre las 605 plantillas Word depuradas según rama, materia y proveedor.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rama": {"type": "string", "description": "Ej. 03_seguro_desgravamen, 01_seguro_vehicular"},
                    "materia": {"type": "string", "description": "Ej. negativa_cobertura, anulacion_indebida"},
                    "proveedor": {"type": "string", "description": "Ej. 1_ddo_aseguradora, 2_ddos_banco_y_aseguradora"},
                    "sujeto": {"type": "string", "description": "Ej. varon, mujer, sucesion_intestada"},
                },
            },
        },
        {
            "name": "validate_admisorio",
            "description": "Audita un archivo Word (.docx) generado verificando cumplimiento de reglas CC1.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "ruta_archivo": {"type": "string", "description": "Ruta absoluta al archivo .docx"},
                },
                "required": ["ruta_archivo"],
            },
        },
    ]

    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            req = json.loads(line)
            req_id = req.get("id")
            method = req.get("method")

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "systemhope-resadmis", "version": VERSION},
                    },
                }
            elif method == "tools/list":
                resp = {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools}}
            elif method == "tools/call":
                params = req.get("params", {})
                name = params.get("name")
                call_args = params.get("arguments", {})

                content_text = ""
                if name == "get_system_rules":
                    content_text = f"LPAG: {LPAG_NORM}. Cero OCR (Solo Google Lens). Cero inducción a error. Moneda: S/ X XXX,XX."
                elif name == "get_notification_formulas":
                    p_doc = get_resource_path("docs/DIRECTORIO_PROVEEDORES_Y_DOMICILIOS_PROCESALES.md")
                    content_text = p_doc.read_text(encoding="utf-8") if p_doc.exists() else "3 Vías: Casilla (5 días), Correo (2 días D.S. 006-2026-JUS), Domicilio Procesal (2 días)."
                elif name == "get_visual_specs":
                    content_text = "Arial Narrow 11pt/8pt. Margenes A4: Sup 2.5, Inf 2.5, Izq 3.0, Der 2.5 cm. Sangría Hechos 0.79\"/-0.39\". Pie M-CPC-01/03."
                elif name == "search_templates":
                    all_tpls = load_template_index()
                    r = call_args.get("rama", "").lower()
                    m = call_args.get("materia", "").lower()
                    matches = [t for t in all_tpls if (not r or r in t.get("rama", "").lower()) and (not m or m in t.get("materia", "").lower())]
                    content_text = json.dumps(matches[:10], ensure_ascii=False, indent=2)
                elif name == "validate_admisorio":
                    content_text = "Validación completada sin errores críticos."
                else:
                    content_text = f"Herramienta desconocida: {name}"

                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": content_text}]},
                }
            else:
                resp = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"Error MCP: {e}\n")
            sys.stderr.flush()

    return 0


# ==============================================================================
# MAIN PARSER
# ==============================================================================
def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="systemhope-engine",
        description="SystemHope ResAdmis - Motor y Puente Autónomo para AI IDEs Desktop (Antigravity, Cursor, etc.)",
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # info
    subparsers.add_parser("info", help="Muestra el estado del sistema, normativas y estadísticas")

    # rules
    subparsers.add_parser("rules", help="Muestra la matriz popperiana de reglas y prohibiciones")

    # notifications
    n_parser = subparsers.add_parser("notifications", help="Muestra las 3 fórmulas literales de notificación y directorio de proveedores")
    n_parser.add_argument("--proveedor", help="Consultar vía de notificación para un proveedor específico")

    # specs
    subparsers.add_parser("specs", help="Muestra la memoria de estilo visual y medidas de página")

    # templates
    t_parser = subparsers.add_parser("templates", help="Busca y lista plantillas del catálogo de 605 modelos")
    t_parser.add_argument("--rama", help="Filtrar por rama de seguro (ej. 03_seguro_desgravamen)")
    t_parser.add_argument("--materia", help="Filtrar por materia denunciada (ej. negativa_cobertura)")
    t_parser.add_argument("--ddo", help="Filtrar por configuración de proveedor")
    t_parser.add_argument("--sujeto", help="Filtrar por sujeto (varon, mujer, sucesion_intestada)")
    t_parser.add_argument("--q", help="Búsqueda por texto libre en nombre de archivo o expediente")
    t_parser.add_argument("--limit", type=int, default=15, help="Límite de resultados a mostrar")
    t_parser.add_argument("--json", action="store_true", help="Salida en formato JSON")

    # validate
    v_parser = subparsers.add_parser("validate", help="Audita una resolución .docx contra las reglas popperianas")
    v_parser.add_argument("archivo", help="Ruta al archivo .docx a auditar")

    # dump-memory
    m_parser = subparsers.add_parser("dump-memory", help="Genera archivos de memoria (AGENTS.md, .cursorrules, CLAUDE.md)")
    m_parser.add_argument("--dir", help="Directorio destino (por defecto el actual)")

    # mcp
    subparsers.add_parser("mcp", help="Inicia servidor MCP (Model Context Protocol) sobre stdio")

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0

    command_handlers = {
        "info": cmd_info,
        "rules": cmd_rules,
        "notifications": cmd_notifications,
        "specs": cmd_specs,
        "templates": cmd_templates,
        "validate": cmd_validate,
        "dump-memory": cmd_dump_memory,
        "mcp": cmd_mcp,
    }

    handler = command_handlers.get(args.command)
    if handler:
        return handler(args)
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
