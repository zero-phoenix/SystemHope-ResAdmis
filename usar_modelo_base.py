#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para usar el modelo base y adaptarlo al expediente 0955-2026 R1.
ESTRATEGIA: Copiar modelo, mantener formato visual (imágenes, colores),
reemplazar solo el contenido de texto específico.
"""

from docx import Document
from docx.shared import Pt, RGBColor
from pathlib import Path
import re


def limpiar_doc_y_adaptarlo():
    """
    1. Abre modelo base
    2. Mantiene: Estructura, estilos, imágenes, colores
    3. Reemplaza: Contenido específico del expediente
    """

    # Rutas
    modelo_path = r'D:\BETTER CALL DAVID\ResAdmi\Modelos al 30-06-26\MODELO xxxx exp. ADM ver. David 1 DDO,  VARIAS IMPUTACIONES.docx'
    output_path = r'D:\BETTER CALL DAVID\ResAdmi\productos (resoluciones) elaborada por claude\ADM_0955-2026_R1.docx'

    # Abrir modelo
    print(f"[1] Abriendo modelo base...")
    doc = Document(modelo_path)

    print(f"    - Párrafos: {len(doc.paragraphs)}")
    print(f"    - Tablas: {len(doc.tables)}")
    print(f"    - Secciones: {len(doc.sections)}")

    # ESTRATEGIA: Análisis de qué reemplazar
    print(f"\n[2] Analizando contenido para reemplazar...")

    contenido_expediente_955 = {
        'expediente': '0955-2026/CC1',
        'denunciante': 'Eufemia Estefa Martínez Moreno de Romero (Señora Martínez)',
        'denunciado': 'Interseguro Compañía de Seguros S.A. (Interseguro)',
        'póliza': 'N°1760006823',
        'asegurado': 'Leonardo Romero Martínez (L.M.R.)',
        'fecha': 'Lima, 20 de abril de 2026',
        'resolucion': '1',
        'materias': 'ADMISIÓN A TRÁMITE / REQUERIMIENTO DE INFORMACIÓN',
    }

    # Buscar y mostrar estructura actual
    print(f"\n[3] Buscando patrones en documento actual...")
    patrones_encontrados = 0
    for i, p in enumerate(doc.paragraphs[:30]):
        text = p.text.strip()
        if text:
            # Buscar patrones de expediente, denunciante, etc.
            if 'expediente' in text.lower() or 'denuncia' in text.lower():
                print(f"    [{i}] {text[:70]}")
                patrones_encontrados += 1

    if patrones_encontrados == 0:
        print(f"    [⚠] No se encontraron patrones obvios")
        print(f"    [ℹ] Mostrando primeras líneas del documento:")
        for i, p in enumerate(doc.paragraphs[:10]):
            if p.text.strip():
                print(f"        [{i}] {p.text[:70]}")

    # Buscar en tablas
    print(f"\n[4] Buscando tablas con datos...")
    for t_idx, table in enumerate(doc.tables):
        print(f"    Tabla {t_idx}: {len(table.rows)} filas x {len(table.columns)} cols")
        # Mostrar primeras celdas
        for r_idx, row in enumerate(table.rows[:3]):
            for c_idx, cell in enumerate(row.cells[:2]):
                text = cell.text.strip()[:50]
                if text:
                    print(f"      [{r_idx},{c_idx}] {text}")

    # Guardar documento (análisis sin cambios aún)
    print(f"\n[5] Guardando copia base...")
    doc.save(output_path)

    print(f"\n✓ Documento guardado: {Path(output_path).name}")
    print(f"  Tamaño: {Path(output_path).stat().st_size} bytes")
    print(f"  IMPORTANTE: Este es el modelo base sin cambios")
    print(f"  Próximo paso: Reemplazar contenido manteniendo formato")

    return doc, output_path


if __name__ == '__main__':
    limpiar_doc_y_adaptarlo()
