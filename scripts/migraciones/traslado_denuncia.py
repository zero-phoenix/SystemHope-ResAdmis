#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Migración v3.5 (R-212, instructor 24/09/2026): el artículo resolutivo del
traslado corre traslado de la **denuncia**, citada con sus escritos y fechas
tal como la cita el artículo que la admite a trámite (y se mantiene
sincronizada con él: el constructor hereda la cita de la plantilla):

    «correr traslado de la denuncia del 30 de abril de 2026, subsanada
    mediante escrito del 7 de setiembre de 2026 a Protecta S.A. … para que, …»

en lugar de «correr traslado de la presente resolución a …». La cita se copia
del párrafo «admitir a trámite la denuncia del …» del mismo documento: nunca se
inventa una fecha. Si el documento no trae esa cita, no se toca y se informa.
Las dos notas del traslado (artículo 26 y artículo 223) quedan intactas (R-173).

Uso:
    python scripts/migraciones/traslado_denuncia.py            # simula
    python scripts/migraciones/traslado_denuncia.py --aplicar
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _tramos as T  # noqa: E402

# La cita se copia literal del artículo que admite: desde «denuncia del» hasta
# donde empieza quién la interpuso («, interpuesta por …», «contra …»).
RE_ADMITE = re.compile(r"admitir a trámite (?:la )?(?=denuncia del )")
RE_FIN_CITA = re.compile(r",?\s+(?:interpuest[ao]s?|presentad[ao]s?|formulad[ao]s?|en contra|contra)\b")
# Lo que va entre «correr traslado de la» y el destinatario: la fórmula
# anterior («presente resolución») o una cita ya puesta, que se sincroniza con
# la del artículo que admite (el constructor hereda la de la plantilla).
TRAMO = re.compile(
    r"correr traslado de la (?:presente resoluci[oó]n|denuncia del .+?)(?=,?\s+al?\s+[A-ZÁÉÍÓÚÑ\[])"
)


def normalizar_cita(cita: str) -> str:
    """Ignora solo espacios de maquetacion y la coma separadora final."""
    return re.sub(r"\s+", " ", cita).strip().rstrip(", ")


def cita_admision(texto: str) -> str | None:
    """Cita completa del ordinal de admision, sea PRIMERO, SEGUNDO u otro."""
    a = RE_ADMITE.search(texto)
    if a:
        f = RE_FIN_CITA.search(texto, a.end())
        if f:
            return texto[a.end():f.start()].rstrip(", ")
    return None


def cita_traslado(texto: str) -> str | None:
    m = TRAMO.search(texto)
    if m:
        cita = m.group(0).removeprefix("correr traslado de la ")
        if cita.startswith("denuncia del "):
            return cita.rstrip(", ")
    return None


def cita_denuncia(xml: str) -> str | None:
    return next(
        (c for m in T.N.RE_P.finditer(xml) if (c := cita_admision(T.texto(m.group(0))))),
        None,
    )


def migrar_xml(xml: str) -> tuple[str, int, bool]:
    """Devuelve (xml, párrafos cambiados, faltó la cita)."""
    cita = cita_denuncia(xml)
    n = 0
    falta = False

    def _p(m):
        nonlocal n, falta
        p = m.group(0)
        t = T.texto(p)
        v = TRAMO.search(t)
        if not v:
            return p
        if cita is None:
            falta = "presente resoluci" in v.group(0)
            return p
        nuevo = "correr traslado de la " + cita
        if v.group(0) == nuevo:
            return p
        n += 1
        return T.reemplazar(p, v.start(), v.end(), nuevo)

    return T.N.RE_P.sub(_p, xml), n, falta


def migrar_docx(ruta: Path, aplicar: bool) -> tuple[int, bool]:
    x2, n, falta = migrar_xml(T.leer(ruta))
    if n and aplicar:
        T.escribir(ruta, x2)
    return n, falta


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("rutas", nargs="*")
    a = ap.parse_args()
    rutas = [Path(r) for r in a.rutas] or sorted((T.RAIZ / "plantillas_maestras").rglob("*.docx"))
    total = 0
    sin_cita = []
    for r in rutas:
        n, falta = migrar_docx(r, a.aplicar)
        total += n
        if falta:
            sin_cita.append(r)
    print("%s: %d traslados" % ("APLICADO" if a.aplicar else "SIMULADO", total))
    for r in sin_cita:
        print("  SIN CITA (no se toca):", r.relative_to(T.RAIZ) if r.is_relative_to(T.RAIZ) else r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
