#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repara los .docx que Word declara «contenido no legible» (supervision 2898-2026).

Causa medida: el normalizador R-155 de la v2.3.0 (21/09/2026) reescribio
`word/document.xml` con xml.etree.ElementTree, que renombra los prefijos de
espacio de nombres (`w14` -> `ns2`, `mc` -> `ns0`, `r` -> `ns1`) y descarta las
declaraciones que no ve usadas. `mc:Ignorable` sigue citando `w14 w15 ...` y
Word no puede resolverlos: todas las plantillas (y todo admisorio construido
sobre ellas) abrian con el aviso de contenido no legible.

Este script devuelve los prefijos canonicos y declara en la raiz todos los
espacios de nombres que `mc:Ignorable` cita. NUNCA se reescribe un .docx con
ElementTree: `scripts/autocomprobacion.py` lo prohibe desde ahora.

Uso:
    python scripts/reparar_espacios_nombres.py [--aplicar] [archivos.docx ...]
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

CANONICOS = {
    "http://schemas.openxmlformats.org/markup-compatibility/2006": "mc",
    "http://schemas.microsoft.com/office/word/2010/wordml": "w14",
    "http://schemas.microsoft.com/office/word/2012/wordml": "w15",
    "http://schemas.microsoft.com/office/word/2015/wordml/symex": "w16se",
    "http://schemas.microsoft.com/office/word/2016/wordml/cid": "w16cid",
    "http://schemas.microsoft.com/office/word/2018/wordml": "w16",
    "http://schemas.microsoft.com/office/word/2018/wordml/cex": "w16cex",
    "http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash": "w16sdtdh",
    "http://schemas.microsoft.com/office/word/2023/wordml/word16du": "w16du",
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships": "r",
    "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing": "wp",
    "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing": "wp14",
    "http://schemas.openxmlformats.org/drawingml/2006/main": "a",
    "http://schemas.openxmlformats.org/drawingml/2006/picture": "pic",
    "http://schemas.microsoft.com/office/drawing/2010/main": "a14",
    "http://schemas.openxmlformats.org/officeDocument/2006/math": "m",
    "urn:schemas-microsoft-com:vml": "v",
    "urn:schemas-microsoft-com:office:office": "o",
    "urn:schemas-microsoft-com:office:word": "w10",
    "http://schemas.microsoft.com/office/word/2006/wordml": "wne",
    "http://schemas.microsoft.com/office/word/2010/wordprocessingShape": "wps",
    "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup": "wpg",
    "http://schemas.microsoft.com/office/word/2010/wordprocessingInk": "wpi",
    "http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas": "wpc",
}
URI_DE = {p: u for u, p in CANONICOS.items()}
URI_DE["w"] = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
IGNORABLES = "w14 w15 w16se w16cid w16 w16cex w16sdtdh w16du wp14"


def reparar_xml(x: str) -> tuple[str, int]:
    decl = dict(re.findall(r'xmlns:(ns\d+)="([^"]+)"', x))
    cambios = 0
    for pref, uri in decl.items():
        canon = CANONICOS.get(uri)
        if not canon:
            continue
        x, n = re.subn(r"(?<=[<\s/])%s:" % pref, canon + ":", x)
        x = x.replace('xmlns:%s="%s"' % (pref, uri), "")
        cambios += n
    m = re.search(r"<w:(document|footnotes|endnotes|hdr|ftr)\b[^>]*>", x)
    if not m:
        return x, cambios
    raiz = m.group(0)
    atributos = re.sub(r'\s(xmlns(:\w+)?|mc:Ignorable)="[^"]*"', "", raiz[:-1])
    usados = set(re.findall(r"<(\w+):", x)) | set(re.findall(r"\s(\w+):\w+=", x))
    decls = " ".join(
        'xmlns:%s="%s"' % (p, URI_DE[p])
        for p in sorted(set(URI_DE) & (usados | set(IGNORABLES.split()) | {"mc", "r"}))
    )
    nueva = '%s %s mc:Ignorable="%s">' % (atributos, decls, IGNORABLES)
    if nueva != raiz:
        x = x.replace(raiz, nueva, 1)
        cambios += 1
    return x, cambios


def necesita(z: zipfile.ZipFile) -> bool:
    for n in ("word/document.xml", "word/footnotes.xml", "word/endnotes.xml"):
        if n in z.namelist():
            x = z.read(n).decode("utf-8", "replace")
            if re.search(r"<ns\d+:|\sns\d+:\w+=", x):
                return True
            ign = re.search(r'mc:Ignorable="([^"]+)"', x)
            dec = set(re.findall(r"xmlns:(\w+)=", x))
            if ign and any(p not in dec for p in ign.group(1).split()):
                return True
    return False


def reparar(ruta: Path, aplicar: bool) -> int:
    with zipfile.ZipFile(ruta) as z:
        if not necesita(z):
            return 0
        infos = z.infolist()
        datos = {i.filename: z.read(i.filename) for i in infos}
    total = 0
    for n in (
        "word/document.xml",
        "word/footnotes.xml",
        "word/endnotes.xml",
        "word/header1.xml",
        "word/footer1.xml",
    ):
        if n in datos:
            nuevo, c = reparar_xml(datos[n].decode("utf-8"))
            if c:
                datos[n] = nuevo.encode("utf-8")
                total += c
    if aplicar and total:
        tmp = ruta.with_suffix(".tmp")
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for i in infos:
                zout.writestr(i, datos[i.filename])
        tmp.replace(ruta)
    return total


def main(argv: list[str]) -> int:
    aplicar = "--aplicar" in argv
    rutas = [Path(a) for a in argv if not a.startswith("--")]
    if not rutas:
        rutas = sorted((RAIZ / "plantillas_maestras").rglob("*.docx")) + sorted(
            (RAIZ / "automatizacion_antigravity/modelos").glob("*.docx")
        )
    n = sum(1 for r in rutas if reparar(r, aplicar))
    print(
        "%s: %d de %d documentos %s"
        % (
            "APLICADO" if aplicar else "SIMULACION",
            n,
            len(rutas),
            "reparados" if aplicar else "a reparar",
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
