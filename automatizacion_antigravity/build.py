from pathlib import Path
from typing import Dict

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

from config import TEMPLATE_PATH

ANCHORS = {
    "expediente": "0672-2026/CC1",
    "denunciante": "MEDALITH",
    "denunciado": "RÍMAC",
    "fecha": "Lima, 24 de junio de 2026",
    "hechos": "HECHOS",
    "hechos_dummy": "El xx de abril",
    "medida_dummy": "La señora Medina",
    "analisis": "DE LA ADMISIÓN A TRÁMITE DE LA DENUNCIA",
    "resuelve": "RESOLUCIÓN DE LA SECRETARÍA TÉCNICA",
}


def clean_run(run):
    run.font.name = "Arial Narrow"
    run.font.size = Pt(11)
    run.font.highlight_color = None
    run.font.color.rgb = RGBColor(0, 0, 0)
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), "Arial Narrow")
    rpr = run._element.get_or_add_rPr()
    for tag in ("w:shd", "w:highlight"):
        element = rpr.find(qn(tag))
        if element is not None:
            rpr.remove(element)


def clean_paragraph_shading(paragraph):
    ppr = paragraph._element.get_or_add_pPr()
    for tag in ("w:shd", "w:highlight"):
        element = ppr.find(qn(tag))
        if element is not None:
            ppr.remove(element)


def remove_numbering(paragraph):
    numpr = paragraph._element.get_or_add_pPr().find(qn("w:numPr"))
    if numpr is not None:
        paragraph._element.pPr.remove(numpr)


def add_run(paragraph, text, bold=False):
    run = paragraph.add_run(text)
    run.bold = bold
    clean_run(run)
    return run


def _replace(paragraph, text, bold=False):
    paragraph.text = ""
    add_run(paragraph, text, bold)


def _remove(paragraph):
    parent = paragraph._element.getparent()
    if parent is not None:
        parent.remove(paragraph._element)


def _set_list_paragraph(paragraph, text):
    paragraph.text = ""
    remove_numbering(paragraph)
    paragraph.paragraph_format.left_indent = Inches(0.5)
    paragraph.paragraph_format.first_line_indent = Inches(-0.5)
    paragraph.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    add_run(paragraph, text)


def _default_resolutivos(caso):
    denunciado = caso["denunciado"]
    fecha = caso["fecha_denuncia"]
    return {
        "PRIMERO": f"admitir a trámite la denuncia del {fecha} interpuesta por {caso['denunciante']} contra {denunciado}, por lo siguiente:",
        "SEGUNDO": f"tener por ofrecidos los medios probatorios presentados en el escrito de denuncia del {fecha}.",
        "TERCERO": f"requerir a {denunciado} que cumpla con lo siguiente:",
        "CUARTO": f"correr traslado de la denuncia interpuesta el {fecha} a {denunciado}, para que, de conformidad con lo dispuesto por el artículo 26 de la Ley sobre Facultades, Normas y Organización del Indecopi, aprobada por Decreto Legislativo 807, presente sus descargos en un plazo no mayor de cinco (5) días hábiles contados desde la notificación.",
        "QUINTO": f"requerir que, en un plazo no mayor de cinco (5) días hábiles contado a partir del día siguiente de la notificación de la presente resolución, el proveedor denunciado cumpla con lo siguiente: {caso['req_info']}",
    }


def build(caso: Dict, template_path: Path = TEMPLATE_PATH, output_path: Path = None) -> Path:
    template_path = Path(template_path)
    if not template_path.exists():
        raise FileNotFoundError(f"No existe la plantilla: {template_path}")
    doc = Document(template_path)
    for paragraph in doc.paragraphs:
        clean_paragraph_shading(paragraph)
        for run in paragraph.runs:
            clean_run(run)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    clean_paragraph_shading(paragraph)
                    for run in paragraph.runs:
                        clean_run(run)

    found = set()
    analysis_index = resolution_index = notif_index = 0
    mode = "header"
    resolution_text = _default_resolutivos(caso)
    resolution_text.update(caso.get("resolutivos", {}))
    for paragraph in list(doc.paragraphs):
        text = paragraph.text.strip()
        if "EXPEDIENTE" in text and ANCHORS["expediente"] in text:
            _replace(paragraph, f"EXPEDIENTE\t:\t{caso['expediente']}", True)
            found.add("EXPEDIENTE")
        elif "DENUNCIANTE" in text and ANCHORS["denunciante"] in text:
            _replace(paragraph, f"DENUNCIANTE\t:\t{caso['denunciante']}", True)
            found.add("DENUNCIANTE")
        elif "DENUNCIADO" in text and ANCHORS["denunciado"] in text:
            _replace(paragraph, f"DENUNCIADO\t:\t{caso['denunciado']}", True)
            found.add("DENUNCIADO")
        elif text.startswith("Lima,") and ANCHORS["fecha"] in text:
            _replace(paragraph, caso["fecha_res"])
            paragraph.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            found.add("FECHA")
        elif text == ANCHORS["hechos"]:
            mode = "hechos"
            found.add("HECHOS")
        elif mode == "hechos" and text.startswith("Mediante el escrito"):
            _replace(paragraph, f"Mediante el escrito de denuncia del {caso['fecha_denuncia']}, {caso['intro_denuncia']} señalando lo siguiente:")
            mode = "hechos_list"
            found.add("INTRO_HECHOS")
        elif mode == "hechos_list" and text.startswith(ANCHORS["hechos_dummy"]):
            for hecho in caso["hechos"]:
                new_paragraph = paragraph.insert_paragraph_before()
                _set_list_paragraph(new_paragraph, hecho)
            _remove(paragraph)
            found.add("BLOQUE_HECHOS")
        elif mode == "hechos_list" and text.startswith("El 5 de abril"):
            _remove(paragraph)
        elif mode == "hechos_list" and text.startswith(ANCHORS["medida_dummy"]):
            _set_list_paragraph(paragraph, caso["medida_correctiva"])
            paragraph.paragraph_format.left_indent = Inches(0)
            paragraph.paragraph_format.first_line_indent = Inches(0)
            found.add("MEDIDA_CORRECTIVA")
        elif text == ANCHORS["analisis"]:
            mode = "analisis"
            found.add("ANALISIS")
        elif mode == "analisis" and (text.startswith("La Secretaría Técnica") or text.startswith("Así también") or text.startswith("Asimismo") or text.startswith("Además")):
            if analysis_index < len(caso["imputaciones_analisis"]):
                _replace(paragraph, caso["imputaciones_analisis"][analysis_index])
                analysis_index += 1
                found.add("BLOQUE_ANALISIS")
            else:
                _remove(paragraph)
        elif mode == "analisis" and text.startswith("En tanto la denuncia"):
            mode = "req"
        elif mode == "req" and text.startswith("A efectos de tener mayores elementos"):
            _replace(paragraph, caso["req_info"])
            found.add("REQ_INFO")
        elif text == ANCHORS["resuelve"]:
            mode = "resuelve"
            found.add("RESUELVE")
        elif mode == "resuelve" and text.startswith("PRIMERO"):
            _replace(paragraph, "PRIMERO: ", True)
            add_run(paragraph, resolution_text["PRIMERO"])
            found.add("PRIMERO")
        elif mode == "resuelve" and text.startswith("DÉCIMO"):
            label = text.split(":", 1)[0]
            notificaciones = caso.get("notificaciones")
            if notificaciones is not None and notif_index < len(notificaciones):
                _replace(paragraph, f"{label}: ", True)
                add_run(paragraph, notificaciones[notif_index])
                notif_index += 1
            elif notificaciones is not None:
                _remove(paragraph)
        elif mode == "resuelve" and text.startswith("Presunta infracción"):
            if resolution_index < len(caso["imputaciones_res"]):
                _set_list_paragraph(paragraph, caso["imputaciones_res"][resolution_index])
                resolution_index += 1
                found.add("BLOQUE_RES")
            else:
                _remove(paragraph)
        elif mode == "resuelve" and text.startswith(("SEGUNDO:", "TERCERO:", "CUARTO:", "QUINTO:")):
            roman = text.split(":", 1)[0]
            _replace(paragraph, f"{roman}: ", True)
            add_run(paragraph, resolution_text[roman])
            found.add(roman)

    missing = {"EXPEDIENTE", "DENUNCIANTE", "DENUNCIADO", "FECHA", "HECHOS", "BLOQUE_HECHOS",
               "ANALISIS", "BLOQUE_ANALISIS", "RESUELVE", "PRIMERO", "SEGUNDO", "TERCERO",
               "CUARTO", "QUINTO"} - found
    if analysis_index != len(caso["imputaciones_analisis"]):
        missing.add(f"ANALISIS ({analysis_index}/{len(caso['imputaciones_analisis'])})")
    if resolution_index != len(caso["imputaciones_res"]):
        missing.add(f"IMPUTACIONES_RES ({resolution_index}/{len(caso['imputaciones_res'])})")
    if "notificaciones" in caso and notif_index != len(caso["notificaciones"]):
        missing.add(f"NOTIFICACIONES ({notif_index}/{len(caso['notificaciones'])})")
    if missing:
        raise RuntimeError("No se pudieron reemplazar las secciones obligatorias: " + ", ".join(sorted(missing)))
    if output_path is None:
        raise ValueError("output_path es obligatorio")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)
    return output_path
