"""Genera PLANTILLA_MAESTRA_CC1.docx — plantilla base SIN datos reales.

Esta plantilla se crea una sola vez y luego el builder la clona en cada
generación. NO contiene nombres, expedientes ni firmas reales: sólo
placeholders + encabezado institucional + footer M-CPC-01/03.

La generamos con python-docx porque NO necesitamos imágenes del escudo (la
imagen institucional la añadirá el usuario final pegándola en el header, o
usando su propio MODELO base). Lo importante es tener una plantilla mínima
validable para que el repo sea funcional out-of-the-box.

Si el usuario tiene una plantilla institucional real con escudo, debe
reemplazar este archivo por aquella (R-56).
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt


FUENTE = "Arial Narrow"


def _set_font(run, name=FUENTE, size=11, bold=False):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:ascii"), name)
    rFonts.set(qn("w:hAnsi"), name)
    rFonts.set(qn("w:cs"), name)


def _set_format(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=0, line=1.0):
    p.alignment = align
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing = line


def crear_plantilla(salida: str | Path) -> Path:
    salida = Path(salida)
    salida.parent.mkdir(parents=True, exist_ok=True)

    doc = Document()

    # Márgenes razonables A4
    for section in doc.sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)

    # Encabezado (Header) — Regla R-16, R-22
    header = doc.sections[0].header
    # Limpiar y agregar bloque institucional alineado a la derecha
    hp = header.paragraphs[0]
    hp.text = ""
    _set_format(hp, align=WD_ALIGN_PARAGRAPH.RIGHT)
    run = hp.add_run(
        "SECRETARÍA TÉCNICA DE LA\n"
        "COMISIÓN DE PROTECCIÓN AL CONSUMIDOR 1\n"
        "SEDE CENTRAL"
    )
    _set_font(run, size=11, bold=True)

    # Pie de página (Footer) — Regla R-23
    footer = doc.sections[0].footer
    fp = footer.paragraphs[0]
    fp.text = ""
    _set_format(fp, align=WD_ALIGN_PARAGRAPH.CENTER)
    run_f = fp.add_run("M-CPC-01/03")
    _set_font(run_f, size=9)

    # Cuerpo: placeholder mínimo que el builder reemplazará
    # El builder vacía el cuerpo, así que sólo dejamos un marcador informativo
    p = doc.add_paragraph()
    _set_format(p, align=WD_ALIGN_PARAGRAPH.LEFT)
    run = p.add_run("[CUERPO DEL ADMISORIO — El builder inyecta aquí el contenido generado.]")
    _set_font(run, size=11)

    # Propiedades del documento
    doc.core_properties.author = "ResAdmi"
    doc.core_properties.title = "Plantilla Maestra CC1"
    doc.core_properties.subject = "Admisorio INDECOPI CC1"

    doc.save(str(salida))
    return salida


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "templates" / "PLANTILLA_MAESTRA_CC1.docx"
    crear_plantilla(out)
    print(f"Plantilla creada: {out}")
