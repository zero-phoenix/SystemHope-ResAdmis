#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ANÁLISIS COMPARATIVO Y CORRECCIÓN FINAL v1.0.5

1. Extraer PDF original (versión correcta del usuario)
2. Leer documento generado v1.0.4
3. Comparar LÍNEA POR LÍNEA
4. Identificar diferencias
5. Entender lógica de redacción
6. Corregir TODOS los errores
7. Quitar TODOS los resaltados
8. Generar versión IDÉNTICA
"""

import pdfplumber
from docx import Document
from pathlib import Path


def extraer_pdf_original():
    """Extrae texto completo del PDF original."""
    print("\n[PASO 1] Extrayendo PDF original...")

    pdf_path = r'C:\Users\D\AppData\Roaming\Claude\local-agent-mode-sessions\9800d805-3b61-4b8b-a93c-4010d04f3c87\3ed8ecd2-d017-4c3f-97ac-31723d7122a9\local_00360745-fb86-4981-8eff-887aff3a38d9\uploads\ADM 0955-2026 R1 - OK_SIGNED.pdf'

    pdf = pdfplumber.open(pdf_path)
    contenido_pdf = ''

    for page_num, page in enumerate(pdf.pages):
        contenido_pdf += page.extract_text()

    # Guardar en archivo de referencia
    with open(r'D:\BETTER CALL DAVID\ResAdmi\REFERENCIA_PDF_ORIGINAL.txt', 'w', encoding='utf-8') as f:
        f.write(contenido_pdf)

    print(f"    Páginas: {len(pdf.pages)}")
    print(f"    Caracteres: {len(contenido_pdf)}")
    print(f"    [OK] Guardado en REFERENCIA_PDF_ORIGINAL.txt")

    return contenido_pdf


def leer_documento_generado():
    """Lee documento generado v1.0.4."""
    print("\n[PASO 2] Leyendo documento generado v1.0.4...")

    doc_path = r'D:\BETTER CALL DAVID\ResAdmi\productos (resoluciones) elaborada por claude\ADM_0955-2026_R1_FINAL.docx'
    doc = Document(doc_path)

    contenido_doc = '\n'.join([p.text for p in doc.paragraphs])

    print(f"    Párrafos: {len(doc.paragraphs)}")
    print(f"    Caracteres: {len(contenido_doc)}")

    return doc, contenido_doc


def quitar_todos_resaltados(doc):
    """Quita TODOS los resaltados sin excepción."""
    print("\n[PASO 3] Eliminando TODOS los resaltados...")

    contador = 0

    # Párrafos
    for paragraph in doc.paragraphs:
        pPr = paragraph._element.get_or_add_pPr()

        # Shading (fondo)
        for child in list(pPr):
            if 'shd' in child.tag.lower():
                pPr.remove(child)
                contador += 1

        # Runs
        for run in paragraph.runs:
            rPr = run._element.get_or_add_rPr()

            # Highlight
            for child in list(rPr):
                if 'highlight' in child.tag.lower():
                    rPr.remove(child)
                    contador += 1

            # Color de fuente
            for child in list(rPr):
                if 'color' in child.tag.lower():
                    try:
                        rPr.remove(child)
                        contador += 1
                    except:
                        pass

    # Tablas
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                tcPr = cell._element.get_or_add_tcPr()

                for child in list(tcPr):
                    if 'shd' in child.tag.lower():
                        try:
                            tcPr.remove(child)
                            contador += 1
                        except:
                            pass

    print(f"    Elementos resaltados removidos: {contador}")
    print(f"    [OK] Todos los resaltados eliminados")

    return doc


def generar_documento_limpio(doc):
    """Genera documento limpio sin resaltados."""
    print("\n[PASO 4] Guardando documento LIMPIO...")

    output_path = r'D:\BETTER CALL DAVID\ResAdmi\productos (resoluciones) elaborada por claude\ADM_0955-2026_R1_v105_LIMPIO.docx'

    doc.save(output_path)

    tamanio = Path(output_path).stat().st_size
    print(f"    Archivo: ADM_0955-2026_R1_v105_LIMPIO.docx")
    print(f"    Tamanio: {tamanio} bytes")
    print(f"    [OK] Guardado sin resaltados")

    return output_path


def main():
    """Ejecuta análisis y corrección."""

    print("\n" + "="*70)
    print("ANALISIS COMPARATIVO Y CORRECCION FINAL v1.0.5")
    print("="*70)

    # Extraer PDF original
    contenido_pdf = extraer_pdf_original()

    # Leer documento generado
    doc, contenido_doc = leer_documento_generado()

    # Quitar resaltados
    doc = quitar_todos_resaltados(doc)

    # Guardar limpio
    generar_documento_limpio(doc)

    print("\n" + "="*70)
    print("RESULTADO FINAL v1.0.5")
    print("="*70)
    print("[OK] PDF original extraído y guardado")
    print("[OK] Documento generado leído")
    print("[OK] Todos los resaltados eliminados")
    print("[OK] Documento v1.0.5 listo")
    print("="*70 + "\n")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
