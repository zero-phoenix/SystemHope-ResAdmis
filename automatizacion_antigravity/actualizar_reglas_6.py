import os
from pathlib import Path

reglas_path = Path("automatizacion_antigravity/REGLAS_DE_APRENDIZAJE.md")

nuevas_reglas_6 = """
66. USO OBLIGATORIO DE `\\r` PARA SALTOS DE PÁRRAFO DUROS EN WIN32COM
Contexto
En MS Word (vía `win32com`), inyectar un string con `\\n` en un objeto Text lo interpreta internamente como un salto de línea suave (Soft Line Break / `Shift+Enter`). En párrafos justificados, esto estira grotescamente la línea final de cada falso párrafo.
La Regla Definitiva
Antes de inyectar textos multilínea vía COM (especialmente en `insert_footnotes.py`), se DEBE reemplazar todo `\\n` por `\\r` (`str(note).replace("\\n", "\\r")`). En MS Word, `\\r` es el verdadero y único salto de párrafo duro, garantizando que el texto justificado no se estire.

67. MANEJO DE LISTAS COMPUESTAS EN RESOLUTIVOS (CLONACIÓN Y PURGA)
Contexto
El resolutivo `TERCERO` de la plantilla contenía una lista dummy `(i) presentar documentos...`. Inyectar todos los requerimientos como un bloque de texto gigante dentro del párrafo principal `TERCERO:` destruía la indentación nativa y generaba estiramientos, además de dejar viva la basura (el ítem `(i)` original) en el documento final.
La Regla Definitiva
Cuando un resolutivo (ej. `TERCERO`) contenga listas separadas por `\\n`:
1. El motor debe inyectar únicamente la línea base ("TERCERO: requerir...") en el párrafo ancla.
2. Debe guardar el resto de ítems en memoria.
3. Debe esperar a toparse con el primer ítem dummy de la plantilla (ej. el párrafo que empieza por `(i)`).
4. Usará ese primer ítem dummy para clonar su estilo perfecto por cada ítem en memoria, inyectándolos uno por uno.
5. Finalmente, el motor debe **eliminar/purgar** todos los ítems residuales de la plantilla que empiecen por un enumerador romano para no dejar duplicados sucios al final de la resolución.
"""

if reglas_path.exists():
    with open(reglas_path, "a", encoding="utf-8") as f:
        f.write(nuevas_reglas_6)
    print("Reglas 66 y 67 añadidas a REGLAS_DE_APRENDIZAJE.md")
else:
    print("Archivo REGLAS_DE_APRENDIZAJE.md no encontrado.")
