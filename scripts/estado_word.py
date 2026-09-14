#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagnostico de instancias de Word huerfanas y bloqueos de documento.

Uso:
    python scripts/estado_word.py [carpeta_o_docx ...]

Por que existe: `footnote_injector` abre Word por COM. Si el proceso que lo
lanzo muere entre `Documents.Open` y `word.Quit()`, queda un WINWORD.EXE
invisible con el documento abierto. El siguiente intento se encuentra el .docx
bloqueado y se queda esperando, que es como una generacion de minutos se
convierte en una espera indefinida.

**Este script no mata nada.** Informa. Cerrar un Word que podria tener trabajo
sin guardar es decision de la persona, no del agente.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def instancias_word() -> list[dict]:
    """Lista los WINWORD.EXE con su ventana principal y su CPU acumulada."""
    ps = (
        "Get-Process -Name WINWORD -ErrorAction SilentlyContinue | "
        "ForEach-Object { '{0}|{1}|{2}|{3}' -f $_.Id, [math]::Round($_.CPU,1), "
        "$_.MainWindowTitle, $_.StartTime }"
    )
    try:
        salida = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
            capture_output=True,
            timeout=30,
        ).stdout.decode("utf-8", "replace")
    except Exception:
        return []
    filas = []
    for linea in salida.splitlines():
        partes = linea.strip().split("|")
        if len(partes) >= 4 and partes[0].isdigit():
            filas.append(
                {
                    "pid": int(partes[0]),
                    "cpu": partes[1],
                    "ventana": partes[2].strip(),
                    "inicio": partes[3].strip(),
                }
            )
    return filas


def bloqueos(rutas: list[str]) -> list[Path]:
    """Archivos de bloqueo `~$nombre.docx` que Word deja mientras tiene abierto
    un documento. Si sobreviven al cierre, son basura que confunde al siguiente
    intento de apertura."""
    encontrados = []
    for r in rutas:
        p = Path(r)
        carpeta = p if p.is_dir() else p.parent
        if not carpeta.exists():
            continue
        encontrados.extend(sorted(carpeta.glob("~$*.doc*")))
    return encontrados


def main(argv: list[str]) -> int:
    if os.name != "nt":
        print("Solo aplica en Windows.")
        return 0

    print("=" * 78)
    print("ESTADO DE WORD")
    print("=" * 78)

    procesos = instancias_word()
    if not procesos:
        print("  No hay WINWORD.EXE en ejecucion.")
    for p in procesos:
        huerfano = not p["ventana"]
        etiqueta = (
            "HUERFANO (sin ventana: instancia de automatizacion)"
            if huerfano
            else "en uso"
        )
        print(
            "  PID %-6d CPU %-7ss  %-52s %s"
            % (p["pid"], p["cpu"], etiqueta, p["inicio"])
        )
        if huerfano:
            print(
                "         Probablemente quedo de un DispatchEx sin Quit. Mantiene el .docx"
            )
            print("         abierto y hace esperar al siguiente intento.")
            print(
                "         Para cerrarlo, con conocimiento de causa: Stop-Process -Id %d"
                % p["pid"]
            )

    rutas = argv[1:] or [os.getcwd()]
    locks = bloqueos(rutas)
    print()
    if locks:
        print("  ARCHIVOS DE BLOQUEO encontrados:")
        for l in locks:
            print("     %s" % l)
        print(
            "  Si ningun Word tiene ese documento abierto, son residuo y se pueden borrar."
        )
    else:
        print("  Sin archivos de bloqueo ~$ en las rutas revisadas.")
    print()
    print("  Este script no cierra procesos ni borra archivos: solo informa.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
