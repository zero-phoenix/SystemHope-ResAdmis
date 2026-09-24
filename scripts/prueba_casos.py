#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regresion de extremo a extremo: construir y verificar casos de prueba (v3.1).

Las mutaciones (`prueba_verificador.py`) prueban que el verificador RECHAZA lo
que debe. Esta prueba es la otra mitad: que el CONSTRUCTOR, sobre plantillas
reales del corpus, produce documentos que el verificador declara APTO. Cada
caso de `pruebas/ficticios/*.json` es un mapa de construccion de un expediente
FICTICIO (sin datos reales) que el instructor reviso pagina por pagina el
24/09/2026: si un cambio del sistema reintroduce un defecto que el reviso,
este script lo detiene en CI.

Uso:
    python scripts/prueba_casos.py
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import construir_admisorio  # noqa: E402
import verificar_admisorio  # noqa: E402


def main() -> int:
    casos = sorted((RAIZ / "pruebas" / "ficticios").glob("*.json"))
    if not casos:
        print("  FALLA  no hay casos en pruebas/ficticios/")
        return 1
    malos = 0
    with tempfile.TemporaryDirectory(prefix="casos_") as t:
        for ruta in casos:
            mapa = json.loads(ruta.read_text(encoding="utf-8"))
            meta = mapa.pop("_prueba", {})
            salida = Path(t) / ("ADM %s %s.docx" % (meta.get("expediente", ruta.stem), meta.get("resolucion", "R1")))
            mapa["salida"] = str(salida)
            traza = io.StringIO()
            with contextlib.redirect_stdout(traza):
                codigo = construir_admisorio.construir(mapa)
                apto = salida.exists() and verificar_admisorio.verificar(str(salida))
            if codigo == 0 and apto:
                print("  OK     %s: construido sin residuo y APTO" % ruta.stem)
                continue
            malos += 1
            print("  FALLA  %s: %s" % (ruta.stem, "residuo en la construccion" if codigo else "NO APTO"))
            for linea in traza.getvalue().splitlines():
                if "FALLA" in linea or linea.strip().startswith("- "):
                    print("         " + linea.strip())
    print()
    if malos:
        print("  %d caso(s) de prueba fallan." % malos)
        return 1
    print("  Los %d casos de prueba se construyen y salen APTO." % len(casos))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
