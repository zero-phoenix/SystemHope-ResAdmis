#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utilidades comunes de las migraciones v3.4: reemplazar un tramo del texto
de un párrafo tocando solo sus `<w:t>` (formato, notas y demás runs intactos)
y reescribir `word/document.xml` dentro del .docx sin tocar las otras partes.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "scripts"))

import notas_pie as N  # noqa: E402


def escapar(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def textos(p: str) -> tuple[list, list[str]]:
    ts = list(N.RE_T.finditer(p))
    return ts, [N.desescapar(m.group(2)) for m in ts]


def texto(p: str) -> str:
    return "".join(textos(p)[1])


def reemplazar(p: str, ini: int, fin: int, reemplazo: str) -> str:
    """Sustituye t[ini:fin] por `reemplazo` en el párrafo `p`.

    El prefijo común se queda en sus `<w:t>`; el reemplazo va al `<w:t>` donde
    empieza el tramo y se vacían los siguientes hasta su fin. Lo posterior
    (punto final, llamada de nota, espacios) queda donde estaba.
    """
    ts, partes = textos(p)
    t = "".join(partes)
    nuevo = t[:ini] + reemplazo + t[fin:]
    salida, pos, puesto = [], 0, False
    for s in partes:
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
    return "".join(out)


def leer(ruta: Path) -> str:
    with zipfile.ZipFile(ruta) as z:
        return z.read("word/document.xml").decode("utf-8")


def escribir(ruta: Path, xml: str) -> None:
    tmp = ruta.with_suffix(".tmp")
    with zipfile.ZipFile(ruta) as zi, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
        for it in zi.infolist():
            datos = xml.encode("utf-8") if it.filename == "word/document.xml" else zi.read(it.filename)
            zo.writestr(it, datos)
    tmp.replace(ruta)
