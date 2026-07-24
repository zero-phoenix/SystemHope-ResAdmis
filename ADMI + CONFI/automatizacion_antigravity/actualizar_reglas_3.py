import os
from pathlib import Path

reglas_path = Path("automatizacion_antigravity/REGLAS_DE_APRENDIZAJE.md")

nuevas_reglas_3 = """
62. PROHIBICIÓN ABSOLUTA DE MARKDOWN Y SALTOS DE PÁRRAFO DUROS EN NOTAS AL PIE
Contexto
En las notas al pie, usar asteriscos (`**`) para negritas resultaba en la impresión literal de los asteriscos, arruinando la objetividad del documento. Asimismo, los saltos de línea con `\\n` rompían el estilo "Footnote Text" nativo de Word en las líneas subsecuentes (volviéndose letra grande o desfasada).
La Regla Definitiva
JAMÁS usar asteriscos u otro markdown en las cadenas de texto del JSON destinadas a MS Word. Adicionalmente, si una nota al pie requiere varias líneas, se debe utilizar EXCLUSIVAMENTE el salto de línea suave (`\\u000b` o `\\x0b`) en vez de `\\n` para evitar que Word cree nuevos párrafos y destruya la tipografía Arial Narrow tamaño 8.
"""

if reglas_path.exists():
    with open(reglas_path, "a", encoding="utf-8") as f:
        f.write(nuevas_reglas_3)
    print("Nueva regla 62 añadida a REGLAS_DE_APRENDIZAJE.md")
else:
    print("Archivo REGLAS_DE_APRENDIZAJE.md no encontrado.")
