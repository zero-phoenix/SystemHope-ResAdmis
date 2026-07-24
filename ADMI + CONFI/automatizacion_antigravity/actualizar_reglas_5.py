import os
from pathlib import Path

reglas_path = Path("automatizacion_antigravity/REGLAS_DE_APRENDIZAJE.md")

nuevas_reglas_5 = """
64. MODIFICACIÓN A LA REGLA 62: NO USAR SALTOS SUAVES EN TEXTO JUSTIFICADO
Contexto
Se había intentado usar `\\x0b` (soft line break) en las notas al pie para mantener el estilo original. Sin embargo, dado que los pies de página están JUSTIFICADOS, un salto de línea suave provoca que Word estire las palabras de forma grotesca para abarcar todo el ancho del párrafo (espacios gigantes entre palabras).
La Regla Definitiva
En el JSON, las notas al pie de múltiples párrafos DEBEN utilizar saltos de párrafo reales (`\\n`). Para evitar la pérdida del formato, la aplicación obligatoria de la Regla 63 (bucle COM forzando `Arial Narrow 8` a todo `document.Footnotes`) es suficiente para mantener el formato en todos los sub-párrafos sin causar estiramientos indeseados.

65. RESPETAR LOS PÁRRAFOS Y NOTAS RESIDENTES DE LA PLANTILLA
Contexto
Se inyectó el párrafo "En tanto la denuncia reúne..." y su correspondiente nota al pie en el JSON, ignorando que la plantilla ya traía ese párrafo de base. Esto causó duplicidad del párrafo y de la nota (Nota 5 inyectada vs Nota 6 residente).
La Regla Definitiva
Antes de rellenar `imputaciones_analisis`, se debe constatar qué párrafos de conclusión ("En tanto la denuncia...") ya habitan la plantilla. La automatización NO DEBE inyectar párrafos redundantes que ya existan en la estructura base del Word.
"""

if reglas_path.exists():
    with open(reglas_path, "a", encoding="utf-8") as f:
        f.write(nuevas_reglas_5)
    print("Reglas 64 y 65 añadidas a REGLAS_DE_APRENDIZAJE.md")
else:
    print("Archivo REGLAS_DE_APRENDIZAJE.md no encontrado.")
