#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrae del corpus el catalogo de imputaciones admitidas, y nada mas.

Mandato del instructor (15/09/2026): **solo se puede imputar como imputan los
modelos**. Ni mezclas de imputaciones distintas, ni combinaciones de articulos que
no figuren en ninguna resolucion del corpus.

No es una preferencia de estilo. Una imputacion es la pieza que fija el objeto del
procedimiento: de ella dependen los descargos, la carga de la prueba y el marco
sancionador. Una combinacion de articulos inventada --aunque cada articulo por
separado sea correcto-- crea un cargo que la Comision nunca ha formulado, y el
administrado tiene que defenderse de algo que no existe en la practica.

Que hace: recorre las plantillas, extrae cada enunciado
`Presunta infraccion <al deber X>, tipificado en <normas> del Codigo` y agrupa por
la **combinacion exacta de normas**, guardando su frecuencia, su redaccion canonica
y las plantillas donde aparece.

Que NO hace: decidir cual corresponde a un caso. Eso es juicio del redactor. El
catalogo solo dice que combinaciones existen en el corpus y cuales no.

Uso:
    python scripts/catalogar_imputaciones.py              # informe
    python scripts/catalogar_imputaciones.py --guardar    # escribe el catalogo
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import zipfile
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PLANTILLAS = RAIZ / "plantillas_maestras"
CATALOGO = RAIZ / "docs" / "catalogo_imputaciones.json"

# La imputacion se enuncia de dos maneras y hay que cazar las dos: en la
# considerativa, «Presunta infraccion al deber X, tipificado en los articulos...»;
# en la resolutiva, «Presunta infraccion a los articulos 18 y 19 de la Ley 29571,
# en tanto...», sin «tipificado». Un patron que solo cubriera la primera dejaria
# sin vigilar justo donde el cargo se formula.
RE_IMPUTACION = re.compile(
    r"Presunta infracci[oó]n\s+(.{8,260}?)"
    r"(?:,?\s+en tanto|\.\s|;|$)",
    re.I,
)
RE_ARTICULO = re.compile(r"art[ií]culos?\s*([\d°º.,\s y]+)", re.I)
RE_NUMERAL = re.compile(r"numeral(?:es)?\s*([\d.]+)", re.I)
RE_LITERAL = re.compile(r"literal(?:es)?\s+([a-z])\)", re.I)


def sin_tildes(t: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn"
    )


def texto_docx(ruta: Path) -> str:
    with zipfile.ZipFile(ruta) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", xml))


def normas_de(texto: str) -> tuple[str, ...]:
    """La combinacion de normas, normalizada para poder compararla.

    «los articulos 18 y 19», «los articulos 18° y 19°» y «el articulo 18 y el
    articulo 19» son la misma imputacion escrita de tres maneras.
    """
    piezas: set[str] = set()
    for m in RE_ARTICULO.finditer(texto):
        for n in re.findall(r"\d+(?:\.\d+)?", m.group(1)):
            piezas.add("art.%s" % n)
    for m in RE_NUMERAL.finditer(texto):
        piezas.add("num.%s" % m.group(1))
    for m in RE_LITERAL.finditer(texto):
        piezas.add("lit.%s" % m.group(1).lower())
    return tuple(sorted(piezas))


def deber_de(texto: str) -> str:
    t = sin_tildes(texto.strip()).lower()
    t = re.sub(r"^a\s+l[oa]s?\s+|^al\s+|^a\s+", "", t)
    return re.sub(r"\s+", " ", t)[:120]


def catalogar(rutas: list[Path]) -> dict:
    grupos: dict[tuple, dict] = {}
    por_deber: dict[str, set] = defaultdict(set)
    sin_normas = 0

    for ruta in rutas:
        try:
            texto = texto_docx(ruta)
        except Exception:
            continue
        for m in RE_IMPUTACION.finditer(texto):
            enunciado = m.group(1)
            deber = deber_de(re.split(r"tipificad[oa]\s+en", enunciado, 1)[0])
            normas = normas_de(enunciado)
            if not normas:
                sin_normas += 1
                continue
            clave = (deber, normas)
            ficha = grupos.setdefault(
                clave,
                {
                    "deber": deber,
                    "normas": list(normas),
                    "frecuencia": 0,
                    "literal": re.sub(r"\s+", " ", m.group(0))[:240],
                    "plantillas": [],
                },
            )
            ficha["frecuencia"] += 1
            if ruta.name not in ficha["plantillas"] and len(ficha["plantillas"]) < 5:
                ficha["plantillas"].append(ruta.name)
            por_deber[deber].add(normas)

    return {
        "combinaciones": sorted(grupos.values(), key=lambda f: -f["frecuencia"]),
        "normas_admitidas": sorted({"|".join(n) for (_d, n) in grupos}),
        "sin_normas_reconocibles": sin_normas,
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--guardar", action="store_true")
    ap.add_argument(
        "--minimo",
        type=int,
        default=1,
        help="Frecuencia minima para entrar al catalogo",
    )
    args = ap.parse_args(argv[1:])

    rutas = sorted(PLANTILLAS.rglob("*.docx"))
    catalogo = catalogar(rutas)
    combinaciones = [
        c for c in catalogo["combinaciones"] if c["frecuencia"] >= args.minimo
    ]

    print("=" * 78)
    print("CATALOGO DE IMPUTACIONES  (%d plantillas)" % len(rutas))
    print("=" * 78)
    print(
        "  Combinaciones distintas de normas ...: %d"
        % len(catalogo["normas_admitidas"])
    )
    print("  Enunciados distintos (deber+normas) .: %d" % len(combinaciones))
    print(
        "  Sin normas reconocibles .............: %d"
        % catalogo["sin_normas_reconocibles"]
    )
    print()
    print("  Las quince mas frecuentes:")
    print("  %-7s %-26s %s" % ("veces", "normas", "deber"))
    for c in combinaciones[:15]:
        print(
            "  %-7d %-26s %s"
            % (c["frecuencia"], "|".join(c["normas"])[:26], c["deber"][:44])
        )

    if args.guardar:
        CATALOGO.parent.mkdir(exist_ok=True)
        CATALOGO.write_text(
            json.dumps(
                {
                    "combinaciones": combinaciones,
                    "normas_admitidas": catalogo["normas_admitidas"],
                },
                ensure_ascii=False,
                indent=1,
            ),
            encoding="utf-8",
        )
        print()
        print("  Guardado en %s" % CATALOGO)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
