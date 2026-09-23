#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tipografia uniforme en todas las plantillas (instructor, 23/09/2026).

Mandato: todo el texto que no esta en nota al pie, Arial Narrow y un solo tamaño,
salvo las iniciales de redaccion («LSQ/DCQ»), en 8 pt; todo el texto de las notas
al pie, Arial Narrow y un solo tamaño; y el mismo espacio entre notas.

Medido antes (574 plantillas): el cuerpo mezclaba 11 pt (tamaño por defecto en
573), 10 pt (540 000 caracteres forzados), 10,5 y 9 pt; las notas, 8 pt
(mayoria), 7 y 7,5 pt; 6 260 notas terminaban con una linea en blanco y 2 212 no.
Norma: cuerpo 11 pt, iniciales 8 pt, notas 8 pt, cada nota seguida de UNA linea
en blanco. El membrete (encabezado y pie de pagina) no se toca.

Uso:
    python scripts/migraciones/uniformar_tipografia.py [--aplicar] [archivos.docx ...]
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
FUENTE = "Arial Narrow"
SZ_CUERPO, SZ_INICIALES, SZ_NOTAS = 22, 16, 16
RE_P = re.compile(r"<w:p\b[^>]*>.*?</w:p>", re.S)
RE_R = re.compile(r"<w:r\b[^>]*>.*?</w:r>", re.S)
RE_T = re.compile(r"<w:t(?:\s[^>/]*)?>([^<]*)</w:t>")
RE_INICIALES = re.compile(r"[A-ZÑ]{2,5}(?:/[A-ZÑ]{2,5})+")
# Orden del esquema de w:rPr: rFonts va tras rStyle; sz y szCs antes de estos.
DESPUES_DE_SZ = (
    "highlight",
    "u",
    "effect",
    "bdr",
    "shd",
    "fitText",
    "vertAlign",
    "rtl",
    "cs",
    "em",
    "lang",
    "eastAsianLayout",
    "specVanish",
    "oMath",
    "rPrChange",
)


def fijar_rpr(rpr: str, sz: int) -> str:
    """Devuelve el `w:rPr` con la fuente y el tamaño de la norma, en el orden del esquema."""
    cuerpo = rpr[len("<w:rPr>") : -len("</w:rPr>")]
    cuerpo = re.sub(r"<w:rFonts\b[^>]*/>", "", cuerpo)
    cuerpo = re.sub(r"<w:(?:sz|szCs)\b[^>]*/>", "", cuerpo)
    fuentes = '<w:rFonts w:ascii="%s" w:eastAsia="%s" w:hAnsi="%s" w:cs="%s"/>' % (
        (FUENTE,) * 4
    )
    m = re.match(r"\s*<w:rStyle\b[^>]*/>", cuerpo)
    corte = m.end() if m else 0
    cuerpo = cuerpo[:corte] + fuentes + cuerpo[corte:]
    tam = '<w:sz w:val="%d"/><w:szCs w:val="%d"/>' % (sz, sz)
    m = re.search(r"<w:(?:%s)\b" % "|".join(DESPUES_DE_SZ), cuerpo)
    k = m.start() if m else len(cuerpo)
    return "<w:rPr>" + cuerpo[:k] + tam + cuerpo[k:] + "</w:rPr>"


def fijar_run(r: str, sz: int) -> str:
    m = re.search(r"<w:rPr>.*?</w:rPr>", r, re.S)
    if m:
        return r[: m.start()] + fijar_rpr(m.group(0), sz) + r[m.end() :]
    abre = re.match(r"<w:r\b[^>]*>", r).group(0)
    return abre + fijar_rpr("<w:rPr></w:rPr>", sz) + r[len(abre) :]


def fijar_parrafo(p: str, sz: int) -> str:
    p = RE_R.sub(lambda m: fijar_run(m.group(0), sz), p)
    # Marca de parrafo: el alto de una linea vacia depende de ella.
    ppr = re.search(r"<w:pPr>.*?</w:pPr>", p, re.S)
    if ppr:
        nuevo = re.sub(
            r"<w:rPr>.*?</w:rPr>",
            lambda m: fijar_rpr(m.group(0), sz),
            ppr.group(0),
            flags=re.S,
        )
        if "<w:rPr>" not in nuevo:
            nuevo = nuevo.replace(
                "</w:pPr>", fijar_rpr("<w:rPr></w:rPr>", sz) + "</w:pPr>"
            )
        p = p[: ppr.start()] + nuevo + p[ppr.end() :]
    return p


def texto(p: str) -> str:
    return "".join(RE_T.findall(p))


def cuerpo_documento(x: str) -> str:
    def _p(m):
        p = m.group(0)
        sz = SZ_INICIALES if RE_INICIALES.fullmatch(texto(p).strip()) else SZ_CUERPO
        return fijar_parrafo(p, sz)

    return RE_P.sub(_p, x)


def notas(fx: str) -> str:
    def _nota(m):
        abre, contenido, cierra = m.group(1), m.group(3), m.group(4)
        if int(m.group(2)) <= 0 or "<w:footnoteRef" not in contenido:
            return m.group(0)  # separadores y notas vacias sin llamada
        ps = RE_P.findall(contenido)
        if not ps:
            return m.group(0)
        while (
            len(ps) > 1 and not texto(ps[-1]).strip() and "<w:footnoteRef" not in ps[-1]
        ):
            ps.pop()
        ppr = re.search(r"<w:pPr>.*?</w:pPr>", ps[0], re.S)
        vacio = "<w:p>%s</w:p>" % (ppr.group(0) if ppr else "")
        ps = [fijar_parrafo(p, SZ_NOTAS) for p in ps + [vacio]]
        return abre + "".join(ps) + cierra

    return re.sub(
        r'(<w:footnote\b[^>]*w:id="(-?\d+)"[^>]*>)(.*?)(</w:footnote>)',
        _nota,
        fx,
        flags=re.S,
    )


def falsar(x: str, fx: str) -> list[str]:
    """R-174: fuente y tamaño unicos en cuerpo y notas; una linea en blanco tras cada nota."""
    fallos = []
    for p in RE_P.findall(x):
        t = texto(p).strip()
        if not t:
            continue
        sz = SZ_INICIALES if RE_INICIALES.fullmatch(t) else SZ_CUERPO
        for r in RE_R.findall(p):
            if not texto(r).strip():
                continue
            s = re.search(r'<w:sz w:val="(\d+)"', r)
            f = re.search(r'<w:rFonts\b[^>]*w:ascii="([^"]+)"', r)
            if (
                not s
                or int(s.group(1)) != sz
                or not f
                or f.group(1) != FUENTE
                or re.search(r"w:asciiTheme=", r)
            ):
                fallos.append(
                    "R-174: cuerpo fuera de norma (%s pt, %s): '%s'"
                    % (
                        int(s.group(1)) / 2 if s else "?",
                        f.group(1) if f else "?",
                        t[:60],
                    )
                )
                break
        if len(fallos) >= 3:
            return fallos
    for i, n in re.findall(
        r'<w:footnote\b[^>]*w:id="(\d+)"[^>]*>(.*?)</w:footnote>', fx, re.S
    ):
        if int(i) <= 0 or "<w:footnoteRef" not in n:
            continue
        ps = RE_P.findall(n)
        if len(ps) < 2 or texto(ps[-1]).strip() or not texto(ps[-2]).strip():
            fallos.append(
                "R-174: la nota %s no va seguida de exactamente una linea en blanco" % i
            )
            break
        for r in RE_R.findall(n):
            if not texto(r).strip():
                continue
            s = re.search(r'<w:sz w:val="(\d+)"', r)
            f = re.search(r'<w:rFonts\b[^>]*w:ascii="([^"]+)"', r)
            if not s or int(s.group(1)) != SZ_NOTAS or not f or f.group(1) != FUENTE:
                fallos.append(
                    "R-174: nota %s fuera de norma (%s pt)"
                    % (i, int(s.group(1)) / 2 if s else "?")
                )
                break
    return fallos[:4]


def main(argv: list[str]) -> int:
    aplicar = "--aplicar" in argv
    rutas = [Path(a) for a in argv if not a.startswith("--")] or (
        sorted((RAIZ / "plantillas_maestras").rglob("*.docx"))
        + sorted((RAIZ / "automatizacion_antigravity/modelos").glob("*.docx"))
    )
    tocados = errores = 0
    for ruta in rutas:
        with zipfile.ZipFile(ruta) as z:
            infos = z.infolist()
            datos = {i.filename: z.read(i.filename) for i in infos}
        x = datos["word/document.xml"].decode("utf-8")
        fx = datos["word/footnotes.xml"].decode("utf-8")
        x2, fx2 = cuerpo_documento(x), notas(fx)
        f = falsar(x2, fx2)
        if f:
            errores += 1
            print("  ERROR %s: %s" % (ruta.name, f))
            continue
        if (x2, fx2) == (x, fx):
            continue
        tocados += 1
        if aplicar:
            datos["word/document.xml"] = x2.encode("utf-8")
            datos["word/footnotes.xml"] = fx2.encode("utf-8")
            tmp = ruta.with_suffix(".tmp")
            with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
                for i in infos:
                    zout.writestr(i, datos[i.filename])
            tmp.replace(ruta)
    print(
        "%s: %d de %d documentos; %d errores"
        % ("APLICADO" if aplicar else "SIMULACION", tocados, len(rutas), errores)
    )
    return 1 if errores else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
