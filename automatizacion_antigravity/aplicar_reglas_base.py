#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
aplicar_reglas_base.py - Regla Suprema 55 (Arquitectura de Código)
===============================================================
Fuerza el formato estricto CC1 sobre cualquier documento DOCX generado.
TODO script generador DEBE llamar a esta función antes de guardar.

USO:
    from aplicar_reglas_base import aplicar_reglas_base, aplicar_reglas_base_win32com
    
    # Para python-docx:
    aplicar_reglas_base(doc, tipo="CC1")
    doc.save("salida.docx")
    
    # Para win32com (Word COM API):
    aplicar_reglas_base_win32com(doc_com)
    doc_com.SaveAs("salida.docx")
"""

import re
from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn


# ============================================================
# REGLAS DE FORMATO (constantes)
# ============================================================
FUENTE_CUERPO = "Arial Narrow"
TAMANO_CUERPO = Pt(11)
FUENTE_NOTAS = "Arial Narrow"
TAMANO_NOTAS = Pt(8)
FUENTE_INICIALES = "Arial Narrow"
TAMANO_INICIALES = Pt(8)
ALINEACION = WD_ALIGN_PARAGRAPH.JUSTIFY
SPACE_BEFORE = Pt(0)
SPACE_AFTER = Pt(0)
LINE_SPACING = 1.0

# Sangrías CC1
INDENT_METADATA = Inches(1.48)
HANGING_METADATA = Inches(-1.48)
INDENT_ROMANO = Inches(0.39)
HANGING_ROMANO = Inches(-0.39)
INDENT_NUMERAL = Inches(0.39)
HANGING_NUMERAL = Inches(-0.39)
INDENT_VINETA_HECHOS = Inches(0.79)
HANGING_VINETA = Inches(-0.39)
INDENT_VINETA_RESOL = Inches(0.39)

# Boilerplate CC1 - secciones obligatorias
BOLERPLATE_CC1 = [
    "III. REQUERIMIENTO DE INFORMACI\u00d3N",
    "IV. RESOLUCI\u00d3N DE LA SECRETAR\u00cdA T\u00c9CNICA",
]

ARTICULOS_RESOLUTIVOS_CC1 = [
    "PRIMERO", "SEGUNDO", "TERCERO", "CUARTO",
    "QUINTO", "SEXTO", "S\u00c9TIMO", "OCTAVO",
    "NOVENO", "D\u00c9CIMO", "D\u00c9CIMO PRIMERO",
]

FOOTER_TEXT = "M-CPC-01/03"


def aplicar_reglas_base(doc, tipo="CC1"):
    """
    Funci\u00f3n principal para python-docx.
    Aplica TODAS las reglas de formato CC1 sobre el documento.
    
    Args:
        doc: Document (python-docx)
        tipo: "CC1" o "PS1"
    """
    _forzar_fuente_y_espaciado(doc)
    _forzar_estilo_normal(doc)
    _forzar_sangrias_metadata(doc)
    _limpiar_resaltados(doc)
    _forzar_pie_pagina(doc)
    return doc


def _forzar_fuente_y_espaciado(doc):
    """Fuerza Arial Narrow 11, spacing 0, line spacing 1.0 en TODOS los párrafos."""
    for p in doc.paragraphs:
        pf = p.paragraph_format
        pf.space_before = SPACE_BEFORE
        pf.space_after = SPACE_AFTER
        pf.line_spacing = LINE_SPACING
        if p.alignment is None:
            p.alignment = ALINEACION
        
        for run in p.runs:
            run.font.name = FUENTE_CUERPO
            run.font.size = TAMANO_CUERPO
    
    # Tablas
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    pf = p.paragraph_format
                    pf.space_before = SPACE_BEFORE
                    pf.space_after = SPACE_AFTER
                    pf.line_spacing = LINE_SPACING
                    for run in p.runs:
                        run.font.name = FUENTE_CUERPO
                        run.font.size = TAMANO_CUERPO


def _forzar_estilo_normal(doc):
    """Fuerza el estilo Normal del documento."""
    style = doc.styles['Normal']
    style.font.name = FUENTE_CUERPO
    style.font.size = TAMANO_CUERPO
    pf = style.paragraph_format
    pf.space_before = SPACE_BEFORE
    pf.space_after = SPACE_AFTER
    pf.line_spacing = LINE_SPACING


def _forzar_sangrias_metadata(doc):
    """
    Busca líneas de metadata (EXPEDIENTE, DENUNCIANTE, etc.)
    y les aplica la sangría colgante correcta.
    """
    campos_metadata = ["EXPEDIENTE", "DENUNCIANTE", "DENUNCIADO", "MATERIAS", "RESOLUCI\u00d3N"]
    for p in doc.paragraphs:
        text = p.text.strip()
        for campo in campos_metadata:
            if text.startswith(campo):
                pf = p.paragraph_format
                pf.left_indent = INDENT_METADATA
                pf.first_line_indent = HANGING_METADATA
                break


def _limpiar_resaltados(doc):
    """Elimina resaltados/backgrounds residuales."""
    for paragraph in doc.paragraphs:
        pPr = paragraph._element.get_or_add_pPr()
        for elem in list(pPr):
            if 'shd' in str(elem.tag).lower():
                try:
                    pPr.remove(elem)
                except:
                    pass
        for run in paragraph.runs:
            rPr = run._element.get_or_add_rPr()
            for elem in list(rPr):
                tag = str(elem.tag).lower()
                if any(x in tag for x in ['highlight', 'shd']):
                    try:
                        rPr.remove(elem)
                    except:
                        pass
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                tcPr = cell._element.get_or_add_tcPr()
                for elem in list(tcPr):
                    if 'shd' in str(elem.tag).lower():
                        try:
                            tcPr.remove(elem)
                        except:
                            pass


def _forzar_pie_pagina(doc):
    """
    Intenta establecer el pie de p\u00e1gina M-CPC-01/03.
    NOTA: python-docx tiene soporte limitado para headers/footers.
    Para control completo, usar la versi\u00f3n win32com.
    """
    try:
        section = doc.sections[0]
        footer = section.footer
        if footer.paragraphs:
            for p in footer.paragraphs:
                if not p.text.strip():
                    run = p.add_run(FOOTER_TEXT)
                    run.font.name = FUENTE_CUERPO
                    run.font.size = TAMANO_NOTAS
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    except:
        pass  # Fallback silencioso


# ============================================================
# VERSIÓN WIN32COM (Word COM API)
# ============================================================

def aplicar_reglas_base_win32com(doc_com, tipo="CC1"):
    """
    Versi\u00f3n para win32com (Word COM API).
    Aplica formato directamente a trav\u00e9s de la API de Word.
    
    Args:
        doc_com: Word.Document (COM object)
        tipo: "CC1" o "PS1"
    """
    _forzar_fuente_win32com(doc_com)
    _forzar_espaciado_win32com(doc_com)
    _forzar_notas_pie_win32com(doc_com)
    _forzar_footer_win32com(doc_com)
    _forzar_iniciales_win32com(doc_com)


def _forzar_fuente_win32com(doc_com):
    """Fuerza Arial Narrow 11 en todo el cuerpo."""
    for paragraph in doc_com.Paragraphs:
        try:
            rng = paragraph.Range
            rng.Font.Name = FUENTE_CUERPO
            rng.Font.Size = 11
        except:
            pass


def _forzar_espaciado_win32com(doc_com):
    """Fuerza spacing 0 y line spacing 1.0."""
    for paragraph in doc_com.Paragraphs:
        try:
            pf = paragraph.Format
            pf.SpaceBefore = 0
            pf.SpaceAfter = 0
            pf.LineSpacingRule = 0  # wdLineSpaceSingle
        except:
            pass


def _forzar_notas_pie_win32com(doc_com):
    """Fuerza Arial Narrow 8 en notas al pie."""
    try:
        for fn in doc_com.Footnotes:
            fn.Range.Font.Name = FUENTE_NOTAS
            fn.Range.Font.Size = 8
            fn.Range.ParagraphFormat.Alignment = 3  # justify
    except:
        pass


def _forzar_footer_win32com(doc_com):
    """Establece el footer M-CPC-01/03."""
    try:
        for section in doc_com.Sections:
            footer = section.Footers(1)  # wdHeaderFooterPrimary
            footer.Range.Text = ""
            footer.Range.Text = FOOTER_TEXT
            footer.Range.Font.Name = FUENTE_CUERPO
            footer.Range.Font.Size = 9
            footer.Range.ParagraphFormat.Alignment = 1  # center
    except:
        pass


def _forzar_iniciales_win32com(doc_com):
    """Fuerza tama\u00f1o 8 en iniciales al final del documento."""
    patron_iniciales = re.compile(r'^[A-Z]{2,4}/[A-Z]{2,4}$')
    try:
        for paragraph in doc_com.Paragraphs:
            text = paragraph.Range.Text.strip()
            if patron_iniciales.match(text):
                paragraph.Range.Font.Size = 8
    except:
        pass


# ============================================================
# MAIN: Demo / Test
# ============================================================

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
        print(f"Aplicando reglas base a: {path}")
        doc = Document(path)
        aplicar_reglas_base(doc)
        out = path.replace(".docx", "_REGULADO.docx")
        doc.save(out)
        print(f"Guardado como: {out}")
    else:
        print("Uso: python aplicar_reglas_base.py <ruta_docx>")
        print("Ejemplo: python aplicar_reglas_base.py temp_v7.docx")
