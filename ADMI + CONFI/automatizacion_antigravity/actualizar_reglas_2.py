import os
from pathlib import Path

reglas_path = Path("automatizacion_antigravity/REGLAS_DE_APRENDIZAJE.md")

nuevas_reglas_2 = """
60. CONTROL DE FORMATO NATIVO (ELIMINACIÓN DE RESALTADOS)
Contexto
En las plantillas Word maestras a veces existen textos o viñetas resaltados en verde (como marcadores de posición) que ensucian el documento final.
La Regla Definitiva
El script `insert_footnotes.py` o el procesador final DEBE aplicar `document.Content.HighlightColorIndex = 0` a todo el documento para erradicar cualquier resaltado residual simulando un "Ctrl+E" -> "Sin Color".

61. INSERCIÓN CORRECTA DE NOTAS AL PIE VÍA WIN32COM
Contexto
Las notas al pie aparecían vacías (sin texto) porque se pasaba un argumento nombrado (`Text=...`) que el puente COM ignora o malinterpreta.
La Regla Definitiva
Para agregar notas al pie por COM se deben pasar los argumentos de forma posicional estricta. Ejemplo correcto: `document.Footnotes.Add(rng, "", str(note))` en lugar de usar `Text=...`.
"""

if reglas_path.exists():
    with open(reglas_path, "a", encoding="utf-8") as f:
        f.write(nuevas_reglas_2)
    print("Nuevas reglas (60, 61) añadidas a REGLAS_DE_APRENDIZAJE.md")
else:
    print("Archivo REGLAS_DE_APRENDIZAJE.md no encontrado.")
