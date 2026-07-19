#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Genera resolución ADM 0955-2026 R1 usando modelo base como plantilla.
Mantiene: Imágenes, colores, formato visual
Reemplaza: Datos específicos del expediente
"""

from docx import Document
from pathlib import Path


def reemplazar_en_texto(texto_original, expediente_origen, expediente_destino):
    """Reemplaza datos de un expediente por otro."""
    resultado = texto_original

    # Mapeos de reemplazo
    mapeos = {
        # Expediente
        expediente_origen['expediente']: expediente_destino['expediente'],

        # Denunciante (cuidado con variaciones)
        expediente_origen['denunciante']: expediente_destino['denunciante'],
        expediente_origen['denunciante'].upper(): expediente_destino['denunciante'].upper(),
        expediente_origen['denunciante'].split('(')[0].strip(): expediente_destino['denunciante'].split('(')[0].strip(),

        # Denunciado
        expediente_origen['denunciado']: expediente_destino['denunciado'],
        expediente_origen['denunciado'].upper(): expediente_destino['denunciado'].upper(),

        # Asegurado (si aplica)
        expediente_origen.get('asegurado', ''): expediente_destino.get('asegurado', ''),
    }

    for old, new in mapeos.items():
        if old and new:
            # Case sensitive
            resultado = resultado.replace(old, new)
            # Uppercase
            if old.isupper():
                resultado = resultado.replace(old.upper(), new.upper())

    return resultado


def generar_resolucion_955():
    """Genera resolución 0955-2026 desde modelo base."""

    print("[1] Abriendo modelo base (expediente 0672-2026)...")
    modelo_path = r'D:\BETTER CALL DAVID\ResAdmi\Modelos al 30-06-26\MODELO xxxx exp. ADM ver. David 1 DDO,  VARIAS IMPUTACIONES.docx'
    doc = Document(modelo_path)

    # Datos origen (del modelo)
    exp_origen = {
        'expediente': '0672-2026/CC1',
        'denunciante': 'MEDALITH MEDINA GUTIERREZ (SEÑORA MEDINA)',
        'denunciado': 'RÓMAC SEGUROS Y REASEGUROS S.A. (RÓMAC)',
        'asegurado': 'NOMBRE_ASEGURADO',  # Variar si existe
    }

    # Datos destino (expediente 0955-2026)
    exp_destino = {
        'expediente': '0955-2026/CC1',
        'denunciante': 'EUFEMIA ESTEFA MARTÍNEZ MORENO DE ROMERO (SEÑORA MARTÍNEZ)',
        'denunciado': 'INTERSEGURO COMPAÑÍA DE SEGUROS S.A. (INTERSEGURO)',
        'asegurado': 'LEONARDO ROMERO MARTÍNEZ (L.M.R.)',
    }

    print("[2] Reemplazando datos...")
    print(f"    Expediente: {exp_origen['expediente']} >> {exp_destino['expediente']}")
    print(f"    Denunciante: {exp_origen['denunciante'][:30]}... >> {exp_destino['denunciante'][:30]}...")
    print(f"    Denunciado: {exp_origen['denunciado'][:30]}... >> {exp_destino['denunciado'][:30]}...")

    # Reemplazar en todos los párrafos
    reemplazos_realizados = 0
    for i, paragraph in enumerate(doc.paragraphs):
        texto_original = paragraph.text
        if any(val in texto_original for val in exp_origen.values() if val):
            # Reemplazar en runs (preserva formato de runs)
            for run in paragraph.runs:
                if run.text:
                    run.text = reemplazar_en_texto(run.text, exp_origen, exp_destino)
                    if run.text != texto_original:
                        reemplazos_realizados += 1

    print(f"    Reemplazos realizados: {reemplazos_realizados}")

    # Guardar
    output_path = r'D:\BETTER CALL DAVID\ResAdmi\productos (resoluciones) elaborada por claude\ADM_0955-2026_R1.docx'
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    print(f"\n[3] Guardando documento...")
    doc.save(output_path)

    tamanio = Path(output_path).stat().st_size
    print(f"\n[OK] Documento generado:")
    print(f"    Archivo: {Path(output_path).name}")
    print(f"    Tamanio: {tamanio} bytes")
    print(f"    Expediente: {exp_destino['expediente']}")
    print(f"    Formato visual: Preservado del modelo")
    print(f"    Imagenes y colores: Mantenidos")

    return output_path


if __name__ == '__main__':
    try:
        generar_resolucion_955()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
