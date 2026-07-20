import os
from pathlib import Path

reglas_path = Path("automatizacion_antigravity/REGLAS_DE_APRENDIZAJE.md")

nuevas_reglas = """
57. REGLA SUPREMA DE NOMENCLATURA SOAT Y OTORGAMIENTO
Contexto
El usuario exige estricta precisión técnica para casos de SOAT.
La Regla Definitiva
Cuando se trate de SOAT, usar "(en adelante, SOAT)" de inmediato en los Hechos. Además, nunca usar la frase "pagar la cobertura" aislada, sino "otorgar la cobertura de fallecimiento y gastos de sepelio del SOAT".

58. REQUERIMIENTOS IN-LINE PARA UN SOLO PROVEEDOR (SECCIÓN III Y RESOLUTIVO QUINTO)
Contexto
Para ahorrar espacio y mantener la estructura limpia, cuando solo se requiere información a un denunciado.
La Regla Definitiva
NO usar listas verticales numeradas con (i), (ii), (iii) que generen nuevos párrafos. Se deben agrupar todos los requerimientos en un solo párrafo continuo de manera 'in-line', separados por punto y coma. Ejemplo: "...cumpla con lo siguiente: (i) presentar una copia...; (ii) presentar los medios...; y, (iii) presentar todas las comunicaciones...".

59. RESOLUTIVO "PRIMERO" EN PÁRRAFO ÚNICO (CERO VIÑETAS)
Contexto
Cuando solo se está imputando una presunta infracción a un proveedor.
La Regla Definitiva
El punto PRIMERO NUNCA debe contener un bloque introductorio seguido de viñetas. Debe redactarse fluidamente de corrido. Ejemplo: "PRIMERO: admitir a trámite la denuncia del [fecha] interpuesta por [Denunciante] contra [Denunciado], por presunta infracción a los artículos [x], en tanto la compañía aseguradora se habría negado a otorgar..."
"""

if reglas_path.exists():
    content = reglas_path.read_text(encoding="utf-8")
    if "57. REGLA SUPREMA" not in content:
        with open(reglas_path, "a", encoding="utf-8") as f:
            f.write(nuevas_reglas)
        print("Reglas actualizadas.")
    else:
        print("Las reglas ya estaban actualizadas.")
else:
    print("Archivo REGLAS_DE_APRENDIZAJE.md no encontrado.")
