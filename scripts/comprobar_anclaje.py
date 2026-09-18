#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprueba que el agente está anclado a ESTE repositorio antes de trabajar.

Por qué existe, con la medida delante (R-142, `docs/PLAN_WORKSPACE_ANTIGRAVITY.md`):

    workspaceFolderAbsoluteUri: file:///c:/Users/D/_ConfigIA/.resadmi

Antigravity arrancaba en una carpeta con una sola subcarpeta. Desde ahí no
existen `AGENTS.md`, ni `scripts/`, ni `plantillas_maestras/`. Casi todos los
fallos medidos del agente —no leer las reglas, buscar scripts con `-Recurse` por
todo `C:\\Users`, irse a proyectos ajenos, gastar 67 llamadas sin producir el
triaje— eran consecuencias de esa raíz equivocada, no fallos independientes.

Un archivo que diga «el trabajo está en otro sitio» es una instrucción, y este
sistema tiene medido lo que valen las instrucciones que dependen de que el
agente se acuerde: se le ordenó leer con Lens y la tanda siguiente entregó con
cero toques a imagen. Por eso esto **no es un aviso: es una puerta**. El paso 1
del flujo (`admisorio.py preparar`) la llama y se detiene si no pasa.

Falsador de esta comprobación: un flujo que produzca un admisorio habiendo
arrancado fuera del repositorio, sin que esta puerta lo haya parado.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# Lo que tiene que existir para que la raíz sea esta y no otra.
SEÑAS = [
    "AGENTS.md",
    "scripts/verificar_admisorio.py",
    "scripts/construir_admisorio.py",
    "plantillas_maestras",
    "docs/catalogo_imputaciones.json",
    "docs/casillas_habilitadas.json",
    "automatizacion_antigravity/REGLAS_DE_APRENDIZAJE.md",
]

REMEDIO = """
  ┌──────────────────────────────────────────────────────────────────────────┐
  │  EL AGENTE NO ESTA ANCLADO AL REPOSITORIO                                │
  ├──────────────────────────────────────────────────────────────────────────┤
  │  Arreglo, una sola vez y a mano:                                         │
  │                                                                          │
  │      Antigravity  ->  Add Workspace  ->  la raiz de este repositorio     │
  │      {raiz}
  │                                                                          │
  │  Sin eso, el agente carga otro AGENTS.md (o ninguno), no encuentra los   │
  │  scripts y termina buscando con -Recurse por todo el disco. No es una    │
  │  molestia: es la causa raiz medida de casi todos sus fallos.             │
  │                                                                          │
  │  Diagnostico ampliado:  python scripts/orquestar.py sanear               │
  └──────────────────────────────────────────────────────────────────────────┘
"""


def comprobar(estricto: bool = True) -> list[str]:
    """Devuelve la lista de problemas. Vacía = anclado."""
    problemas = []

    faltan = [s for s in SEÑAS if not (RAIZ / s).exists()]
    if faltan:
        problemas.append("faltan piezas del repositorio: " + ", ".join(faltan))

    if not estricto:
        return problemas

    # El cwd debe caer dentro del repositorio. Si no, las rutas relativas del
    # agente apuntan a otro sitio aunque los scripts sepan encontrarse solos.
    try:
        cwd = Path(os.getcwd()).resolve()
        cwd.relative_to(RAIZ)
    except (ValueError, OSError):
        problemas.append(
            f"el directorio de trabajo es {os.getcwd()!r}, fuera del repositorio "
            f"({RAIZ}). Ejecuta desde la raiz.")

    return problemas


def main(argv: list[str]) -> int:
    estricto = "--laxo" not in argv
    problemas = comprobar(estricto)
    if not problemas:
        print(f"anclaje: OK — raiz {RAIZ}")
        return 0
    print(REMEDIO.replace("{raiz}", f"{str(RAIZ):<70}"))
    for p in problemas:
        print(f"  - {p}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
