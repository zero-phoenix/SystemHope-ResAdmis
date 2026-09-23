#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integridad del sistema: el agente NUNCA modifica el repositorio.

Medido en la prueba del Exp. 2898-2026 (23/09/2026): Antigravity edito
`construir_admisorio.py` y `auditar_admisorio.py` para que su documento pasara.
Aunque ambas ediciones eran razonables, un agente que retoca el sistema que lo
verifica anula la verificacion. Si encuentra un error del sistema, lo REPORTA.

El paquete portatil trae `INTEGRIDAD.json` (SHA256 de scripts, reglas, skills y
datos de referencia). `comprobar_entorno.py` y `admisorio.py entregar` lo
contrastan; cualquier diferencia bloquea la entrega. En el repositorio de
desarrollo (sin INTEGRIDAD.json) la comprobacion no aplica.

Uso:
    python scripts/integridad.py --generar     # lo hace el empaquetado
    python scripts/integridad.py               # comprueba
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MANIFIESTO = RAIZ / "INTEGRIDAD.json"
PATRONES = [
    "scripts/**/*.py",
    "AGENTS.md",
    "ARRANQUE.md",
    ".agents/skills/**/*.md",
    "docs/*.json",
    "config/firmas.json",
    "config/modelo.json",
]


def archivos() -> list[Path]:
    salida = set()
    for patron in PATRONES:
        salida.update(
            p for p in RAIZ.glob(patron) if p.is_file() and "__pycache__" not in p.parts
        )
    return sorted(salida)


def huella(p: Path) -> str:
    # Normaliza fines de linea: el mismo archivo con CRLF o LF es el mismo archivo.
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def generar() -> int:
    datos = {p.relative_to(RAIZ).as_posix(): huella(p) for p in archivos()}
    MANIFIESTO.write_text(json.dumps(datos, indent=1, sort_keys=True), encoding="utf-8")
    print("INTEGRIDAD.json: %d archivos" % len(datos))
    return 0


def comprobar() -> list[str]:
    if not MANIFIESTO.exists():
        return []
    esperado = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    fallos = []
    for rel, h in esperado.items():
        p = RAIZ / rel
        if not p.exists():
            fallos.append("falta %s" % rel)
        elif huella(p) != h:
            fallos.append("modificado %s" % rel)
    for p in archivos():
        rel = p.relative_to(RAIZ).as_posix()
        if rel not in esperado:
            fallos.append("anadido %s" % rel)
    return fallos


def main(argv: list[str]) -> int:
    if "--generar" in argv:
        return generar()
    fallos = comprobar()
    if not MANIFIESTO.exists():
        print("integridad: repositorio de desarrollo (sin INTEGRIDAD.json)")
        return 0
    if fallos:
        print(
            "integridad: FALLA — el sistema fue modificado. Reinstala con arranque/instalar.ps1 y reporta el error en vez de editar:"
        )
        for f in fallos[:20]:
            print("  - " + f)
        return 1
    print("integridad: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
