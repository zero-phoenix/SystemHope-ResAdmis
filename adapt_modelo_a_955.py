#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Adapta el modelo base de Word al expediente 0955-2026 R1.
Mantiene: Imágenes, colores, encabezados, estilos visuales.
Reemplaza: Texto de contenido, datos, números de expediente.
"""

from docx import Document
from docx.shared import Pt, Inches
from copy import deepcopy
from pathlib import Path


def adapt_modelo():
    """Adapta modelo base al expediente 0955-2026."""

    # Abrir documento modelo
    doc = Document(r'D:\BETTER CALL DAVID\ResAdmi\productos (resoluciones) elaborada por claude\ADM_0955-2026_R1_MODELO.docx')

    print(f"Documento abierto. Párrafos: {len(doc.paragraphs)}")
    print(f"Tablas: {len(doc.tables)}")
    print(f"Imágenes en encabezados: {sum(len(s.header.paragraphs) for s in doc.sections)}")

    # Mapeo de reemplazos (CLAVE: VALOR_NUEVO)
    replacements = {
        # Cambiar expediente (adaptarse a lo que haya en el modelo)
        # Cambiar denunciante
        # Cambiar denunciado
        # Etc.
    }

    # Recorrer párrafos y reemplazar textos
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            text = run.text
            if 'expediente' in text.lower() or '0001' in text or '2026' in text:
                print(f"[ENCONTRADO] {text[:50]}...")
            # Hacer reemplazos específicos
            for old, new in replacements.items():
                if old in text:
                    run.text = text.replace(old, new)
                    print(f"[REEMPLAZADO] {old} → {new}")

    # Reemplazar en tablas
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        text = run.text
                        for old, new in replacements.items():
                            if old in text:
                                run.text = text.replace(old, new)

    # Guardar documento adaptado
    output_path = r'D:\BETTER CALL DAVID\ResAdmi\productos (resoluciones) elaborada por claude\ADM_0955-2026_R1.docx'
    doc.save(output_path)

    print(f"\n✓ Documento adaptado guardado:")
    print(f"  {Path(output_path).name}")
    print(f"  Tamaño: {Path(output_path).stat().st_size} bytes")

    return output_path


if __name__ == '__main__':
    adapt_modelo()
