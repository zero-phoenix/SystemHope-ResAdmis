#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Migración v3.3 (R-207, instructor 24/09/2026): la considerativa de toda
imputación por el deber de información cierra con la fórmula

    «[hecho]; involucraría una presunta afectación al derecho de información
    de los consumidores. Por consiguiente, corresponde calificar el hecho
    materia de denuncia como una presunta infracción al deber de información,
    tipificado en el artículo 1, numeral 1, literal b) y al artículo 2 del
    Código.»

Solo toca párrafos de la considerativa («considera que el hecho…»)
cuya calificación es el deber de información (o «los derechos de los
consumidores» con el literal b) del artículo 1). No toca el resolutivo ni las
imputaciones de idoneidad. Edita `word/document.xml` en crudo (solo los
`<w:t>` del párrafo): formato, notas y demás partes quedan intactos.

Uso:
    python scripts/migraciones/afectacion_derecho_informacion.py            # simula
    python scripts/migraciones/afectacion_derecho_informacion.py --aplicar
"""
from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "scripts"))

import notas_pie as N  # noqa: E402

FRASE = "involucraría una presunta afectación al derecho de información de los consumidores"
CALIFICACION = (
    "Por consiguiente, corresponde calificar el hecho materia de denuncia como una presunta "
    "infracción al deber de información, tipificado en el artículo 1, numeral 1, literal b) "
    "y al artículo 2 del Código"
)
CIERRE = "; " + FRASE + ". " + CALIFICACION

# Desde el fin del hecho hasta el fin de la calificación (sin el punto final,
# para no tocar la llamada de nota que pueda seguir).
RE_COLA = re.compile(
    r"(?:\s*;\s*involucrar[ií]a\s+(?:una\s+)?(?:presunta\s+)?afectaci[oó]n\s+al\s+derecho\s+de\s+informaci[oó]n[^.]*)?"
    r"\s*\.\s*Por consiguiente,\s*corresponde calificar el hecho materia de denuncia como una presunta "
    r"infracci[oó]n (?:al deber de informaci[oó]n|a los derechos de los consumidores),\s*tipificado en "
    r"(?:el |al )?(?:art[ií]culo 1|literal b\)|numeral 1\.1)[^;]{0,90}?art[ií]culo 2\s+del C[oó]digo"
)
RE_COLA_SIN_TIPO = re.compile(
    r"\s*\.\s*Por consiguiente,\s*corresponde calificar el hecho materia de denuncia como una presunta "
    r"infracci[oó]n al literal b\) del art[ií]culo 1 y art[ií]culo 2 del C[oó]digo"
)


def escapar(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def es_considerativa_informacion(t: str) -> bool:
    return "considera que el hecho" in t and "idoneidad" not in t and (
        "deber de información" in t or ("literal b)" in t and "artículo 2" in t)
    )


def migrar_parrafo(p: str) -> tuple[str, bool]:
    ts = list(N.RE_T.finditer(p))
    if not ts:
        return p, False
    textos = [N.desescapar(m.group(2)) for m in ts]
    t = "".join(textos)
    if not es_considerativa_informacion(t):
        return p, False
    m = RE_COLA.search(t) or RE_COLA_SIN_TIPO.search(t)
    if not m:
        return p, False
    nuevo = t[: m.start()].rstrip() + CIERRE + t[m.end():]
    if nuevo == t:
        return p, False
    # Reparte: el prefijo común se queda en sus <w:t>; el resto del texto nuevo
    # va al <w:t> donde empieza el cambio y se vacían los siguientes hasta el
    # fin del cambio. Lo posterior (punto final, espacios) queda donde estaba.
    ini = len(t[: m.start()].rstrip())
    fin = m.end()
    reemplazo = CIERRE
    salida, pos, puesto = [], 0, False
    for s in textos:
        a, b = pos, pos + len(s)
        pos = b
        if b <= ini or a >= fin:
            if a >= fin and not puesto:  # cambio en el borde exacto
                s = reemplazo + s
                puesto = True
            salida.append(s)
            continue
        izq = s[: max(0, ini - a)] if a < ini else ""
        der = s[fin - a:] if b > fin else ""
        if not puesto:
            salida.append(izq + reemplazo + der)
            puesto = True
        else:
            salida.append(izq + der)
    if not puesto:
        salida[-1] += reemplazo
    assert "".join(salida) == nuevo, "reparto inconsistente"
    out, ult = [], 0
    for m_t, s in zip(ts, salida):
        abre = m_t.group(1)
        if "xml:space" not in abre:
            abre = abre[:-1] + ' xml:space="preserve">'
        out.append(p[ult:m_t.start()] + abre + escapar(s) + m_t.group(3))
        ult = m_t.end()
    out.append(p[ult:])
    return "".join(out), True


def migrar_docx(ruta: Path, aplicar: bool) -> int:
    with zipfile.ZipFile(ruta) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    n = 0

    def _p(m):
        nonlocal n
        nuevo, cambio = migrar_parrafo(m.group(0))
        n += cambio
        return nuevo

    x2 = N.RE_P.sub(_p, xml)
    if n and aplicar:
        tmp = ruta.with_suffix(".tmp")
        with zipfile.ZipFile(ruta) as zi, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
            for it in zi.infolist():
                datos = x2.encode("utf-8") if it.filename == "word/document.xml" else zi.read(it.filename)
                zo.writestr(it, datos)
        tmp.replace(ruta)
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("rutas", nargs="*")
    a = ap.parse_args()
    rutas = [Path(r) for r in a.rutas] or sorted((RAIZ / "plantillas_maestras").rglob("*.docx"))
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
