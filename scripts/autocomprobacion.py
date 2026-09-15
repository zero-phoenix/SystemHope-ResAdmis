#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprobaciones que el repositorio se hace a si mismo. Las ejecuta CI.

No son pruebas de la redaccion --de eso se ocupan `verificar_admisorio.py` y
`auditar_admisorio.py` sobre cada documento--. Son las comprobaciones de que **el
propio sistema no esta roto de una forma que nadie notaria**, que es la clase de
defecto que mas caro salio (R-141).

Cuatro, y cada una nace de un fallo real:

1. **Ningun caracter de retroceso en una expresion regular.** Escribir un limite
   de palabra como escape literal se ha colapsado **tres veces** en este
   repositorio, dejando un `0x08` donde debia ir el limite. La peor: los cinco
   patrones de R-110, que estuvieron declarando OK sin comprobar nada.
2. **Ninguna plantilla con datos personales.** El repositorio es publico. El
   15/09/2026 las 630 plantillas llevaban el apellido del consumidor que las
   origino.
3. **Todos los scripts compilan.** Se compila, no se importa: importar los
   ejecuta, y una prueba que modifica el repositorio que comprueba no es una
   prueba. Lo descubri cuando una de ellas reescribio un JSON de `docs/`.
4. **Ningun artefacto de trabajo rastreado.** Mapas, volcados y scratch llevan
   nombres de personas y no entran al repositorio.

Uso:
    python scripts/autocomprobacion.py
"""

from __future__ import annotations

import importlib
import re
import subprocess
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

RETROCESO = bytes([8])
RE_TRATAMIENTO = re.compile(
    r"(?:señor|señora|señorita)\s+(?!\[)" r"[A-ZÁÉÍÓÚÑ][\wáéíóúñ]{2,}",
    re.I,
)
RE_DNI = re.compile(r"\bDNI\s*(?:N\.?[°º]|N[°º])?\s*\d{8}\b", re.I)

ARTEFACTOS = (
    "mapa*.json",
    "tpl*.txt",
    "scratch*",
    "_texto_expediente.txt",
    "_ORDEN_DE_TRABAJO.md",
    "_CEDULA.md",
    "gen_map.py",
    "make_map.py",
)


def texto_docx(ruta: Path) -> str:
    with zipfile.ZipFile(ruta) as z:
        partes = [
            z.read(n).decode("utf-8", "replace")
            for n in z.namelist()
            if n.startswith("word/") and n.endswith(".xml")
        ]
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", " ".join(partes)))


def sin_retrocesos() -> list[str]:
    fallos = []
    for py in sorted((RAIZ / "scripts").glob("*.py")) + sorted(
        (RAIZ / "src").glob("*.py")
    ):
        crudo = py.read_bytes()
        if RETROCESO in crudo:
            lineas = [
                str(i) for i, ln in enumerate(crudo.split(b"\n"), 1) if RETROCESO in ln
            ]
            fallos.append(
                "%s tiene un caracter de retroceso (0x08) en la(s) linea(s) %s: "
                "casi seguro es un limite de palabra que se colapso"
                % (py.name, ", ".join(lineas))
            )
    return fallos


def plantillas_anonimas() -> list[str]:
    fallos = []
    plantillas = sorted((RAIZ / "plantillas_maestras").rglob("*.docx"))
    if not plantillas:
        return ["no hay ninguna plantilla en plantillas_maestras/"]
    for p in plantillas:
        try:
            t = texto_docx(p)
        except Exception as exc:
            fallos.append("%s no se puede abrir: %s" % (p.name, exc))
            continue
        m = RE_TRATAMIENTO.search(t) or RE_DNI.search(t)
        if m:
            fallos.append(
                "%s conserva un dato personal ('%s'). Ejecuta "
                "scripts/anonimizar_plantillas.py --aplicar" % (p.name[:60], m.group(0))
            )
    return fallos[:15]


def modulos_compilan() -> list[str]:
    """Compila, no importa.

    La primera version importaba cada modulo y con eso los **ejecutaba**: uno de
    ellos reescribio un JSON de `docs/` durante la comprobacion. Una prueba que
    modifica el repositorio que esta comprobando no es una prueba.
    """
    fallos = []
    for py in sorted((RAIZ / "scripts").glob("*.py")):
        try:
            compile(py.read_text(encoding="utf-8"), str(py), "exec")
        except SyntaxError as exc:
            fallos.append("%s no compila: linea %s, %s" % (py.name, exc.lineno, exc.msg))
    return fallos


def sin_artefactos() -> list[str]:
    rastreados = (
        subprocess.run(["git", "ls-files"], capture_output=True, cwd=RAIZ)
        .stdout.decode("utf-8", "replace")
        .splitlines()
    )
    fallos = []
    for patron in ARTEFACTOS:
        expresion = patron.replace("*", ".*").replace(".", r"\.", 1)
        for r in rastreados:
            nombre = r.split("/")[-1]
            if re.fullmatch(
                expresion.replace(r"\.", ".", 1).replace("*", ".*"), nombre
            ):
                fallos.append("'%s' es un artefacto de trabajo y esta rastreado" % r)
    return fallos


def main() -> int:
    bloques = (
        ("Sin retrocesos en expresiones regulares", sin_retrocesos),
        ("Plantillas sin datos personales", plantillas_anonimas),
        ("Todos los modulos compilan", modulos_compilan),
        ("Sin artefactos de trabajo rastreados", sin_artefactos),
    )
    print("=" * 78)
    print("AUTOCOMPROBACION DEL REPOSITORIO")
    print("=" * 78)
    total = 0
    for titulo, prueba in bloques:
        fallos = prueba()
        total += len(fallos)
        print("  %-5s %s" % ("FALLA" if fallos else "OK", titulo))
        for f in fallos:
            print("        - %s" % f)
    print()
    if total:
        print("  %d problema(s). El repositorio no esta sano." % total)
        return 1
    print("  Sin problemas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
