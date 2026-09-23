#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rotulos, titulos y encabezado segun la mayoria medida (supervision 2898-2026).

1. DECIMO en adelante: solo el rotulo en negrita (303 frente a 111 en las
   notificaciones de DECIMO PRIMERO), como SEGUNDO a NOVENO. El instructor
   objeto la negrita de parrafo entero.
2. «REQUERIMIENTO DE INFORMACION» -> «INFORMACIÓN» (1 015 frente a 127).
3. (Revertido) El encabezado sigue justificado como en el corpus (R-144).

Uso:
    python scripts/migraciones/normalizar_rotulos.py [--aplicar] [archivos.docx ...]
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
RE_P = re.compile(r"<w:p\b[^>]*>.*?</w:p>", re.S)
RE_R = re.compile(r"<w:r\b[^>]*>.*?</w:r>", re.S)
RE_T = re.compile(r"(<w:t(?:\s[^>/]*)?>)([^<]*)(</w:t>)")
RE_ROTULO = re.compile(
    r"^\s*(D[ÉE]CIMO(?: [A-ZÉÍÓÚ]+)?|UND[ÉE]CIMO|DUOD[ÉE]CIMO|VIG[ÉE]SIMO(?: [A-ZÉÍÓÚ]+)?):\s*"
)
RE_ENCABEZADO = re.compile(
    r"^(DENUNCIANTES?|DENUNCIAD[OA]S?|EXPEDIENTE|MATERIAS?|RESOLUCI[ÓO]N)"
)
RE_NEGRITA = re.compile(r"<w:b(?:Cs)?(?: w:val=\"(?:1|true|on)\")? ?/>")


def texto(x: str) -> str:
    return "".join(m.group(2) for m in RE_T.finditer(x))


def partir_run(r: str, k: int) -> tuple[str, str]:
    """Parte un run con un solo <w:t> en el caracter k."""
    t = RE_T.search(r)
    cabeza = re.match(r"<w:r\b[^>]*>(?:\s*<w:rPr>.*?</w:rPr>)?", r, re.S).group(0)
    a = r[: t.start()] + '<w:t xml:space="preserve">%s</w:t></w:r>' % t.group(2)[:k]
    b = cabeza + '<w:t xml:space="preserve">%s</w:t>' % t.group(2)[k:] + r[t.end() :]
    return a, b


def sin_negrita_tras_rotulo(p: str) -> str:
    m = RE_ROTULO.match(texto(p))
    if not m:
        return p
    limite = m.end()
    salida, pos, acum = [], 0, 0
    for mr in RE_R.finditer(p):
        r = mr.group(0)
        t = texto(r)
        salida.append(p[pos : mr.start()])
        pos = mr.end()
        if acum >= limite:
            r = RE_NEGRITA.sub("", r)
        elif acum + len(t) > limite and len(RE_T.findall(r)) == 1:
            a, b = partir_run(r, limite - acum)
            r = a + RE_NEGRITA.sub("", b)
        acum += len(t)
        salida.append(r)
    salida.append(p[pos:])
    return "".join(salida)


def procesar(x: str) -> str:
    ps = list(RE_P.finditer(x))
    piezas, pos = [], 0
    for k, m in enumerate(ps):
        p = m.group(0)
        n = sin_negrita_tras_rotulo(p)
        if k < 16 and RE_ENCABEZADO.match(texto(n).strip()):
            n = n.replace('<w:jc w:val="left"/>', '<w:jc w:val="both"/>')  # revertido: R-144, el corpus justifica
        piezas.append(x[pos : m.start()] + n)
        pos = m.end()
    piezas.append(x[pos:])
    x = "".join(piezas)
    return x.replace("REQUERIMIENTO DE INFORMACION<", "REQUERIMIENTO DE INFORMACIÓN<")


def main(argv: list[str]) -> int:
    aplicar = "--aplicar" in argv
    rutas = [Path(a) for a in argv if not a.startswith("--")] or (
        sorted((RAIZ / "plantillas_maestras").rglob("*.docx"))
        + sorted((RAIZ / "automatizacion_antigravity/modelos").glob("*.docx"))
    )
    tocados = 0
    for ruta in rutas:
        with zipfile.ZipFile(ruta) as z:
            infos = z.infolist()
            datos = {i.filename: z.read(i.filename) for i in infos}
        x = datos["word/document.xml"].decode("utf-8")
        x2 = procesar(x)
        if x2 == x:
            continue
        tocados += 1
        if aplicar:
            datos["word/document.xml"] = x2.encode("utf-8")
            tmp = ruta.with_suffix(".tmp")
            with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
                for i in infos:
                    zout.writestr(i, datos[i.filename])
            tmp.replace(ruta)
    print(
        "%s: %d de %d documentos"
        % ("APLICADO" if aplicar else "SIMULACION", tocados, len(rutas))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
