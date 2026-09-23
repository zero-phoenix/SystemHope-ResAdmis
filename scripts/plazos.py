#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Plazo de 20 dias habiles para emitir la imputacion de cargos (D3, 23/09/2026).

Directiva Unica: la Comision emite la resolucion dentro de veinte (20) dias
habiles contados a partir del dia siguiente de la presentacion de la denuncia o
del ingreso de la denuncia a la Comision cuando la remite otro organo (fecha de
RECEPCION en CC1 del memorandum o documento de traslado).

El plazo se CALCULA y se informa; NO se menciona en la resolucion. Lo que si va
en la resolucion es la nota al pie 1 (R-159) con el documento, su fecha de
emision y la fecha de recepcion en CC1.

Dias habiles: lunes a viernes, excepto los feriados nacionales del Peru (se
calculan para cualquier ano, incluida la Semana Santa) y los dias no laborables
que se anadan en config/feriados_peru.json.

Uso:
    python scripts/plazos.py --desde 15/09/2026                 # vencimiento
    python scripts/plazos.py --desde 15/09/2026 --al 23/09/2026 # dias consumidos y restantes
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EXTRA = RAIZ / "config" / "feriados_peru.json"
PLAZO = 20

# Feriados nacionales de fecha fija (Decreto Legislativo 713 y leyes posteriores).
FIJOS = [
    (1, 1, "Año Nuevo"),
    (5, 1, "Día del Trabajo"),
    (6, 7, "Batalla de Arica y Día de la Bandera"),
    (6, 29, "San Pedro y San Pablo"),
    (7, 23, "Día de la Fuerza Aérea del Perú"),
    (7, 28, "Fiestas Patrias"),
    (7, 29, "Fiestas Patrias"),
    (8, 6, "Batalla de Junín"),
    (8, 30, "Santa Rosa de Lima"),
    (10, 8, "Combate de Angamos"),
    (11, 1, "Día de Todos los Santos"),
    (12, 8, "Inmaculada Concepción"),
    (12, 9, "Batalla de Ayacucho"),
    (12, 25, "Navidad"),
]


def pascua(anio: int) -> date:
    """Domingo de Resurreccion (algoritmo de Meeus/Butcher)."""
    a, b, c = anio % 19, anio // 100, anio % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return date(anio, mes, dia)


def feriados(anio: int) -> dict[date, str]:
    salida = {date(anio, m, d): n for m, d, n in FIJOS}
    p = pascua(anio)
    salida[p - timedelta(days=3)] = "Jueves Santo"
    salida[p - timedelta(days=2)] = "Viernes Santo"
    try:
        extra = json.loads(EXTRA.read_text(encoding="utf-8"))
    except FileNotFoundError:
        extra = {}
    for item in extra.get("no_laborables", []):
        f = datetime.strptime(item["fecha"], "%Y-%m-%d").date()
        if f.year == anio:
            salida[f] = item.get("motivo", "no laborable")
    for item in extra.get("habiles_forzados", []):
        f = datetime.strptime(item["fecha"], "%Y-%m-%d").date()
        salida.pop(f, None)
    return salida


def es_habil(d: date) -> bool:
    return d.weekday() < 5 and d not in feriados(d.year)


def vencimiento(inicio: date, dias: int = PLAZO) -> date:
    """Dia habil numero `dias` contado desde el dia siguiente a `inicio`."""
    d, n = inicio, 0
    while n < dias:
        d += timedelta(days=1)
        if es_habil(d):
            n += 1
    return d


def habiles_entre(inicio: date, fin: date) -> int:
    """Dias habiles transcurridos desde el dia siguiente a `inicio` hasta `fin` inclusive."""
    d, n = inicio, 0
    while d < fin:
        d += timedelta(days=1)
        if es_habil(d):
            n += 1
    return n


def leer_fecha(texto: str) -> date:
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(texto.strip(), fmt).date()
        except ValueError:
            pass
    raise SystemExit("Fecha no reconocida: %r (use DD/MM/AAAA)" % texto)


def informe(inicio: date, al: date | None = None) -> str:
    v = vencimiento(inicio)
    lineas = [
        "Recepcion en CC1 / presentacion : %s" % inicio.strftime("%d/%m/%Y"),
        "Vence (20 dias habiles)          : %s" % v.strftime("%d/%m/%Y"),
    ]
    if al:
        usados = habiles_entre(inicio, al)
        lineas.append(
            "Dias habiles al %s          : %d consumidos, %d restantes%s"
            % (
                al.strftime("%d/%m/%Y"),
                usados,
                max(PLAZO - usados, 0),
                "  ** VENCIDO **" if usados > PLAZO else "",
            )
        )
    return "\n".join(lineas)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--desde",
        required=True,
        help="Fecha de recepcion en CC1 (o de presentacion si fue directa)",
    )
    ap.add_argument("--al", help="Fecha de corte (por defecto, hoy)")
    a = ap.parse_args(argv)
    print(informe(leer_fecha(a.desde), leer_fecha(a.al) if a.al else date.today()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
