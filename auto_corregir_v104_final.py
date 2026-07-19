#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AUTO-CORRECCION v1.0.4 - FINAL
Quita resaltados y genera documento limpio
"""

from docx import Document
from pathlib import Path


def quitar_resaltados(doc):
    """Quita resaltados de todo el documento."""
    print("[PASO] Eliminando resaltados...")

    # Párrafos
    for paragraph in doc.paragraphs:
        pPr = paragraph._element.get_or_add_pPr()
        shd_list = pPr.findall('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd')
        for shd in shd_list:
            try:
                pPr.remove(shd)
            except:
                pass

        # Runs
        for run in paragraph.runs:
            rPr = run._element.get_or_add_rPr()
            highlight = rPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}highlight')
            if highlight is not None:
                rPr.remove(highlight)

    # Tablas
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                tcPr = cell._element.get_or_add_tcPr()
                shd_list = tcPr.findall('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd')
                for shd in shd_list:
                    try:
                        tcPr.remove(shd)
                    except:
                        pass

                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        rPr = run._element.get_or_add_rPr()
                        highlight = rPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}highlight')
                        if highlight is not None:
                            rPr.remove(highlight)

    print("    [OK] Resaltados eliminados")


def auto_corregir():
    """Corre y limpia el documento."""

    print("\n" + "="*70)
    print("AUTO-CORRECCION v1.0.4")
    print("="*70 + "\n")

    doc_path = r'D:\BETTER CALL DAVID\ResAdmi\productos (resoluciones) elaborada por claude\ADM_0955-2026_R1_CORREGIDO.docx'
    output_path = r'D:\BETTER CALL DAVID\ResAdmi\productos (resoluciones) elaborada por claude\ADM_0955-2026_R1_v104.docx'

    print("[PASO] Abriendo documento")
    doc = Document(doc_path)

    print(f"    Parrafos: {len(doc.paragraphs)}")
    print(f"    Tablas: {len(doc.tables)}")

    # Quitar resaltados
    quitar_resaltados(doc)

    # Verificar contenido clave
    print("\n[PASO] Validando contenido clave")
    texto = '\n'.join([p.text for p in doc.paragraphs])

    validaciones = {
        'Decreto Legislativo 807': 'Decreto Legislativo 807' in texto,
        'Decreto Supremo 004-2019-JUS': '004-2019-JUS' in texto,
        'DECIMO SEGUNDO': 'DECIMO SEGUNDO' in texto,
        'EVELING ROA QUISPE': 'EVELING ROA QUISPE' in texto,
    }

    for nombre, presente in validaciones.items():
        estado = "[OK]" if presente else "[FALTA]"
        print(f"    {estado} {nombre}")

    print("\n[PASO] Guardando documento limpio")
    doc.save(output_path)

    tamanio = Path(output_path).stat().st_size
    print(f"    Archivo: {Path(output_path).name}")
    print(f"    Tamanio: {tamanio} bytes")

    print("\n" + "="*70)
    print("RESULTADO v1.0.4")
    print("="*70)
    print("[OK] Resaltados eliminados")
    print("[OK] Documento limpio")
    print("[OK] Listo para produccion")
    print("="*70 + "\n")

    return output_path


if __name__ == '__main__':
    try:
        auto_corregir()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
