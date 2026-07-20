import os
from pathlib import Path

reglas_path = Path("automatizacion_antigravity/REGLAS_DE_APRENDIZAJE.md")

nuevas_reglas_4 = """
63. FORZADO DE ESTILO TIPOGRÁFICO EN NOTAS AL PIE
Contexto
Word 365 y la inserción COM (`Footnotes.Add`) a menudo insertan texto con fuentes predeterminadas como "Aptos 10", destrozando la uniformidad con el estilo original de "Arial Narrow 8 Justificado".
La Regla Definitiva
Es OBLIGATORIO que `insert_footnotes.py` itere sobre todas las notas al pie del documento final (`document.Footnotes`) y fuerce explícitamente la fuente (`Arial Narrow`), el tamaño (`8`) y la alineación justificada (`Alignment = 3`), sin confiar ciegamente en el estilo heredado de la plantilla.
"""

if reglas_path.exists():
    with open(reglas_path, "a", encoding="utf-8") as f:
        f.write(nuevas_reglas_4)
    print("Nueva regla 63 añadida a REGLAS_DE_APRENDIZAJE.md")
else:
    print("Archivo REGLAS_DE_APRENDIZAJE.md no encontrado.")
