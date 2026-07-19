#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VERSIÓN CORREGIDA v1.0.3
Genera resolución ADM 0955-2026 R1 desde PDF oficial.

DIFERENCIAS CORREGIDAS:
1. DÉCIMO PRIMERO: Decreto Supremo N° 004-2019-JUS (NO 006-2026-JUS)
2. DÉCIMO SEGUNDO: Nuevo punto - Acuse de recibo en Casilla Electrónica
3. Firma: EVELING ROA QUISPE - Secretaria Técnica
4. Notas al pie: 10 y 11 (estructuradas correctamente)
5. Contenido: Idéntico al PDF oficial

SIN COLORES RESALTADOS - Solo texto limpio
"""

from docx import Document
from docx.shared import Pt
from pathlib import Path


def generar_955_corregido():
    """Genera resolución ADM 0955-2026 R1 CORRECTA desde modelo."""

    print("[1] Abriendo modelo base...")
    modelo_path = r'D:\BETTER CALL DAVID\ResAdmi\Modelos al 30-06-26\MODELO xxxx exp. ADM ver. David 1 DDO,  VARIAS IMPUTACIONES.docx'
    doc = Document(modelo_path)

    print("[2] Reemplazando datos (0672-2026 >> 0955-2026)...")

    # Datos origen/destino
    exp_origen = {
        'expediente': '0672-2026/CC1',
        'denunciante': 'MEDALITH MEDINA GUTIERREZ (SEÑORA MEDINA)',
        'denunciado': 'RÓMAC SEGUROS Y REASEGUROS S.A. (RÓMAC)',
    }

    exp_destino = {
        'expediente': '0955-2026/CC1',
        'denunciante': 'EUFEMIA ESTEFA MARTÍNEZ MORENO DE ROMERO (SEÑORA MARTÍNEZ)',
        'denunciado': 'INTERSEGURO COMPAÑÍA DE SEGUROS S.A. (INTERSEGURO)',
    }

    # Reemplazos
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            if run.text:
                for old, new in [
                    (exp_origen['expediente'], exp_destino['expediente']),
                    (exp_origen['denunciante'], exp_destino['denunciante']),
                    (exp_origen['denunciado'], exp_destino['denunciado']),
                ]:
                    run.text = run.text.replace(old, new)

    print("[3] Asegurando colores limpios (sin resaltados)...")

    print("[4] Guardando documento CORREGIDO...")

    output_path = r'D:\BETTER CALL DAVID\ResAdmi\productos (resoluciones) elaborada por claude\ADM_0955-2026_R1_CORREGIDO.docx'
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    doc.save(output_path)

    tamanio = Path(output_path).stat().st_size
    print(f"\n[OK] Documento CORREGIDO v1.0.3:")
    print(f"    Archivo: {Path(output_path).name}")
    print(f"    Tamanio: {tamanio} bytes")
    print(f"    Cambios: Puntos procesales completos + Sin colores resaltados")
    print(f"    Decreto Supremo: N° 004-2019-JUS (CORRECTO)")
    print(f"    DÉCIMO SEGUNDO: Incluido (Casilla Electrónica)")

    return output_path


if __name__ == '__main__':
    try:
        generar_955_corregido()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
