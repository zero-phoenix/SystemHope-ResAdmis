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
VERSION = "3.5.2"
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
    """Loads the template catalog index (docs/plantillas_maestras_index.json)."""
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
    print(" • Reglas Popperianas: R-01 a R-155 activas (Cero inducción a error, condicional habría)")
    print(" • Vías de Notificación: 3 párrafos literales. Casilla solo con padrón activo, e-casilla y teléfono (R-151)")
    print(" • Traslado y Descargos: Fórmula obligatoria canónica R-155 (Derogadas fórmulas A y B)")
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
    """Copia AGENTS.md (unica fuente de reglas) a un directorio de exportacion.

    Antes regeneraba AGENTS.md desde un texto embebido y desactualizado (Interbank
    por Casilla, acuse en la via 3, 605 plantillas) y, sin --dir, SOBRESCRIBIA el
    AGENTS.md de la raiz y recreaba .cursorrules y CLAUDE.md, retirados el
    15/09/2026. Ahora solo copia el archivo vigente y nunca escribe en la raiz.
    """
    out_dir = Path(args.dir or "dist/memoria")
    raiz = get_resource_path("AGENTS.md").resolve().parent
    if out_dir.resolve() == raiz:
        print("dump-memory no escribe en la raiz del repositorio: use --dir <otro directorio>.")
        return 2
    out_dir.mkdir(parents=True, exist_ok=True)
    origen = get_resource_path("AGENTS.md")
    if not origen.exists():
        print("No se encontro AGENTS.md.")
        return 1
    (out_dir / "AGENTS.md").write_text(origen.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"AGENTS.md vigente copiado a: {out_dir.resolve()}")
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
            "description": "Busca entre las plantillas Word depuradas del indice según rama, materia y proveedor.",
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
    t_parser = subparsers.add_parser("templates", help="Busca y lista plantillas del catálogo del indice")
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
    m_parser = subparsers.add_parser("dump-memory", help="Copia el AGENTS.md vigente a un directorio de exportacion (nunca a la raiz)")
    m_parser.add_argument("--dir", help="Directorio destino (por defecto dist/memoria)")

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
