#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Instala el hook de pre-commit en este clon.

    python scripts/instalar_hooks.py

Los hooks no viajan con el repositorio: cada clon los instala. Sin este paso la
guardia solo actua en CI, que avisa despues de publicar en vez de antes.
"""

import shutil
import stat
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def main() -> int:
    gitdir = subprocess.run(
        ["git", "rev-parse", "--git-dir"], capture_output=True, cwd=RAIZ
    ).stdout.decode().strip()
    if not gitdir:
        print("No es un clon de git.")
        return 1
    destino = (RAIZ / gitdir / "hooks" / "pre-commit").resolve()
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(RAIZ / "scripts" / "hooks" / "pre-commit", destino)
    destino.chmod(destino.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    print("Hook instalado en %s" % destino)
    print("Prueba: python scripts/guardia_admisorio.py --staged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
