#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Migración v3.5 (R-211, instructor 24/09/2026): la considerativa de toda
imputación por reclamos (numeral 88.1 del artículo 88, o artículo 24) cierra
el hecho con

    «[hecho]; involucraría una presunta afectación a su derecho de recibir
    respuestas adecuadas a los reclamos formulados. Por consiguiente,
    corresponde calificar el hecho materia de denuncia como …»

Solo toca párrafos de la considerativa («considera que el hecho…») cuya
calificación cita el artículo 88 o el artículo 24 del Código y no la
idoneidad. Si el hecho cerraba con la frase de «expectativas» (propia de
idoneidad), se sustituye. La calificación no se toca, ni el resolutivo.

Uso:
    python scripts/migraciones/afectacion_derecho_reclamos.py            # simula
    python scripts/migraciones/afectacion_derecho_reclamos.py --aplicar
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _tramos as T  # noqa: E402

FRASE = "involucraría una presunta afectación a su derecho de recibir respuestas adecuadas a los reclamos formulados"

RE_CALIFICA = re.compile(r"\s*\.\s*Por consiguiente,\s*corresponde calificar el hecho materia de denuncia")
RE_NORMA_RECLAMO = re.compile(r"art[ií]culo 88\b|art[ií]culo 24 del C[oó]digo")
# Cierre previo del hecho que se sustituye: «; involucraría … expectativas …»
RE_AFECTACION_PREVIA = re.compile(r"\s*;\s*involucrar[ií]a\s+una\s+presunta\s+afectaci[oó]n[^;]*$")


def es_considerativa_reclamo(t: str) -> bool:
    if "considera que el hecho" not in t:
        return False
    m = None
    for m in RE_CALIFICA.finditer(t):
        pass
    if m is None:
        return False
    cola = t[m.end():]
    return bool(RE_NORMA_RECLAMO.search(cola)) and "idoneidad" not in cola


def migrar_parrafo(p: str) -> tuple[str, bool]:
    t = T.texto(p)
    if not es_considerativa_reclamo(t):
        return p, False
    m = None
    for m in RE_CALIFICA.finditer(t):
        pass
    hecho = t[: m.start()]
    if hecho.rstrip().endswith(FRASE):
        return p, False
    previa = RE_AFECTACION_PREVIA.search(hecho)
    ini = previa.start() if previa else len(hecho.rstrip())
    return T.reemplazar(p, ini, m.start(), "; " + FRASE), True


def migrar_xml(xml: str) -> tuple[str, int]:
    n = 0

    def _p(m):
        nonlocal n
        nuevo, cambio = migrar_parrafo(m.group(0))
        n += cambio
        return nuevo

    return T.N.RE_P.sub(_p, xml), n


def migrar_docx(ruta: Path, aplicar: bool) -> int:
    x2, n = migrar_xml(T.leer(ruta))
    if n and aplicar:
        T.escribir(ruta, x2)
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("rutas", nargs="*")
    a = ap.parse_args()
    rutas = [Path(r) for r in a.rutas] or sorted((T.RAIZ / "plantillas_maestras").rglob("*.docx"))
    total = archivos = 0
    for r in rutas:
        n = migrar_docx(r, a.aplicar)
        if n:
            archivos += 1
            total += n
    print("%s: %d párrafos en %d plantillas" % ("APLICADO" if a.aplicar else "SIMULADO", total, archivos))
    return 0


if __name__ == "__main__":
    sys.exit(main())
