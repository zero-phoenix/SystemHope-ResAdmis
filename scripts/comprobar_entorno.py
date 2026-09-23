#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprueba que el entorno puede producir un admisorio (cualquier PC).

Mide, no supone: version de Python y del paquete, dependencias importables,
Git disponible, cero OCR, anclaje del repositorio, fecha de la remesa y modelo
exigido. Sale con 1 si falta algo imprescindible.

Uso:
    python scripts/comprobar_entorno.py
"""

from __future__ import annotations

import importlib
import os
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

DEPENDENCIAS = [
    ("fitz", "PyMuPDF"),
    ("pypdf", "pypdf"),
    ("docx", "python-docx"),
    ("lxml", "lxml"),
    ("PIL", "Pillow"),
    ("openpyxl", "openpyxl"),
]


def main() -> int:
    fallos = []
    print("SystemHope ResAdmis — comprobacion del entorno")
    print("  Python   : %s (%s)" % (sys.version.split()[0], sys.executable))
    version = RAIZ.parent / "VERSION.txt"
    print(
        "  Paquete  : %s"
        % (
            version.read_text(encoding="utf-8").strip()
            if version.exists()
            else "repositorio de desarrollo"
        )
    )
    for modulo, nombre in DEPENDENCIAS:
        try:
            importlib.import_module(modulo)
            print("  OK   %s" % nombre)
        except Exception as exc:
            fallos.append("falta %s (%s)" % (nombre, exc))
            print("  FALLA %s" % nombre)
    git = RAIZ.parent / "git" / "cmd" / "git.exe"
    print(
        "  Git      : %s"
        % (
            git
            if git.exists()
            else shutil.which("git") or "no disponible (no imprescindible)"
        )
    )
    import autocomprobacion

    ocr = autocomprobacion.cero_ocr()
    print("  Cero OCR : %s" % ("OK" if not ocr else "FALLA: " + "; ".join(ocr)))
    fallos += ocr
    import comprobar_anclaje

    anclaje = comprobar_anclaje.comprobar(estricto=False)
    print("  Anclaje  : %s" % ("OK" if not anclaje else "; ".join(anclaje)))
    fallos += anclaje
    if Path(os.getcwd()).resolve() != RAIZ:
        print("  AVISO    : ejecuta los comandos desde %s (Set-Location)" % RAIZ)
    import config_sistema

    fecha = config_sistema.fecha_emision()
    print(
        "  Remesa   : %s"
        % (fecha or "SIN FECHA -> pregunta la fecha de emision al instructor")
    )
    m = config_sistema.modelo()
    print(
        "  Modelo   : la conversacion debe usar %s o superior"
        % m.get("minimo", "Gemini 3.8 Flash High")
    )
    print("  %s" % ("LISTO" if not fallos else "NO LISTO: " + "; ".join(fallos)))
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
