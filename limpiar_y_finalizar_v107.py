#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LIMPIEZA FINAL v1.0.7
Toma el documento v106 y elimina TODOS los resaltados
"""

from docx import Document
from pathlib import Path

def limpiar_resaltados_completo(doc):
    """Limpieza EXHAUSTIVA de todo tipo de resaltados."""
    contador = 0

    # Párrafos
    for paragraph in doc.paragraphs:
        pPr = paragraph._element.get_or_add_pPr()
        for elem in list(pPr):
            tag_str = str(elem.tag).lower()
            if 'shd' in tag_str or 'color' in tag_str:
                try:
                    pPr.remove(elem)
                    contador += 1
                except:
                    pass

        # Runs
        for run in paragraph.runs:
            rPr = run._element.get_or_add_rPr()
            for elem in list(rPr):
                tag_str = str(elem.tag).lower()
                if any(x in tag_str for x in ['highlight', 'color', 'shd']):
                    try:
                        rPr.remove(elem)
                        contador += 1
                    except:
                        pass

    # Tablas
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                # Cell properties
                tcPr = cell._element.get_or_add_tcPr()
                for elem in list(tcPr):
                    tag_str = str(elem.tag).lower()
                    if 'shd' in tag_str:
                        try:
                            tcPr.remove(elem)
                            contador += 1
                        except:
                            pass

                # Cell paragraphs
                for paragraph in cell.paragraphs:
                    pPr = paragraph._element.get_or_add_pPr()
                    for elem in list(pPr):
                        if 'shd' in str(elem.tag).lower():
                            try:
                                pPr.remove(elem)
                                contador += 1
                            except:
                                pass

                    for run in paragraph.runs:
                        rPr = run._element.get_or_add_rPr()
                        for elem in list(rPr):
                            tag_str = str(elem.tag).lower()
                            if any(x in tag_str for x in ['highlight', 'color', 'shd']):
                                try:
                                    rPr.remove(elem)
                                    contador += 1
                                except:
                                    pass

    return contador

print("\n" + "="*70)
print("LIMPIEZA FINAL v1.0.7")
print("="*70 + "\n")

doc_path = r'D:\BETTER CALL DAVID\ResAdmi\productos (resoluciones) elaborada por claude\ADM_0955-2026_R1_v106_FINAL.docx'

print("[1] Abriendo documento v106...")
doc = Document(doc_path)
print(f"    Párrafos: {len(doc.paragraphs)}")
print(f"    Tablas: {len(doc.tables)}")

print("\n[2] Eliminando TODOS los resaltados...")
contador = limpiar_resaltados_completo(doc)
print(f"    [OK] {contador} elementos removidos")

print("\n[3] Guardando documento final v107...")
output_path = r'D:\BETTER CALL DAVID\ResAdmi\productos (resoluciones) elaborada por claude\ADM_0955-2026_R1_v107_FINAL.docx'
doc.save(output_path)

tamanio = Path(output_path).stat().st_size
print(f"    Archivo: ADM_0955-2026_R1_v107_FINAL.docx")
print(f"    Tamaño: {tamanio} bytes")

print("\n" + "="*70)
print("✅ DOCUMENTO v1.0.7 - LISTO PARA GITHUB")
print("="*70 + "\n")
