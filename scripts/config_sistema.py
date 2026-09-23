#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fuente unica de configuracion: fecha de la remesa, firmas y modelo.

Antes la fecha de emision estaba escrita a mano en cuatro scripts y la firma en
tres, con valores que se contradecian ("Silva Malpartida (e)" en la orden de
trabajo, "Eveling Roa" en el verificador). Ahora todo se lee de `config/`.

Uso:
    python scripts/config_sistema.py                      # muestra la configuracion
    python scripts/config_sistema.py --fecha "25 de setiembre de 2026"
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CONFIG = RAIZ / "config"
MESES = (
    "enero febrero marzo abril mayo junio julio agosto setiembre octubre noviembre diciembre"
).split()


def _leer(nombre: str) -> dict:
    ruta = CONFIG / nombre
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}


def fecha_emision() -> str:
    """'25 de setiembre de 2026', o '' si la remesa no la fijo (hay que preguntarla)."""
    return str(_leer("remesa.json").get("fecha_emision", "")).strip()


def firma_para(denunciados: str) -> tuple[str, str]:
    """(nombre, cargo) segun el bloque de denunciados del encabezado (R-103)."""
    cfg = _leer("firmas.json")
    plano = denunciados.upper().replace("Í", "I")
    for regla in cfg.get("excepciones", []):
        if any(clave in plano for clave in regla["si_denunciado_contiene"]):
            return regla["nombre"], regla["cargo"]
    titular = cfg.get(
        "titular", {"nombre": "EVELING ROA QUISPE", "cargo": "Secretaria Técnica"}
    )
    return titular["nombre"], titular["cargo"]


def modelo() -> dict:
    return _leer("modelo.json")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--fecha", help="Fija la fecha de emision de la remesa: 'D de mes de AAAA'"
    )
    a = ap.parse_args(argv)
    if a.fecha:
        f = a.fecha.strip()
        if not re.fullmatch(r"\d{1,2} de (%s) de \d{4}" % "|".join(MESES), f):
            print(
                "Formato: '25 de setiembre de 2026' (mes en minusculas, 'setiembre')."
            )
            return 2
        datos = _leer("remesa.json")
        datos["fecha_emision"] = f
        (CONFIG / "remesa.json").write_text(
            json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(
        "Fecha de emision : %s"
        % (
            fecha_emision()
            or "(sin fijar: Antigravity debe preguntarla antes de redactar)"
        )
    )
    print("Firma titular    : %s / %s" % firma_para(""))
    print("Firma Rimac      : %s / %s" % firma_para("RIMAC SEGUROS"))
    m = modelo()
    print(
        "Modelo redactor  : %s (o superior: %s)"
        % (m.get("minimo", "?"), ", ".join(m.get("aceptables", [])))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
