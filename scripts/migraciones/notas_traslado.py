#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pone las dos notas al pie del parrafo del traslado (instructor, 23/09/2026).

El parrafo resolutivo «correr traslado ... artículo 26 de la Ley sobre Facultades,
Normas y Organización del Indecopi, aprobada por Decreto Legislativo 807 ...
artículo 223 del Texto Único Ordenado de la Ley 27444, Ley del Procedimiento
Administrativo General ...» lleva SIEMPRE dos notas, cada una detras de la norma
que anota: la del articulo 26 del D. Leg. 807 y la del articulo 223 del TUO
(D.S. 006-2026-JUS). Medido antes: 15 de 577 plantillas anotaban ese parrafo y
ninguna con las dos.

Texto de las notas: `docs/notas_traslado.json`. El formato (sangria, tamaño,
llamada, tabulacion) se clona de las notas que el propio documento ya tiene,
para que las nuevas no se distingan visualmente. Idempotente.

Uso:
    python scripts/migraciones/notas_traslado.py [--aplicar] [archivos.docx ...]
"""

from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
NOTAS = json.loads((RAIZ / "docs/notas_traslado.json").read_text(encoding="utf-8"))[
    "notas"
]
RE_P = re.compile(r"<w:p\b[^>]*>.*?</w:p>", re.S)
RE_R = re.compile(r"<w:r\b[^>]*>.*?</w:r>", re.S)
RE_T = re.compile(r"(<w:t(?:\s[^>/]*)?>)([^<]*)(</w:t>)")
RE_FN = re.compile(r'<w:footnote\b[^>]*w:id="(-?\d+)"[^>]*>.*?</w:footnote>', re.S)
RE_REF_ID = re.compile(r'(<w:footnoteReference\b[^>]*w:id=")(\d+)(")')
REF_POR_DEFECTO = (
    '<w:r><w:rPr><w:rStyle w:val="Refdenotaalpie"/>'
    '<w:rFonts w:ascii="Arial Narrow" w:hAnsi="Arial Narrow"/>'
    '<w:vertAlign w:val="superscript"/></w:rPr>'
    '<w:footnoteReference w:id="0"/></w:r>'
)


def texto(xml: str) -> str:
    return "".join(m.group(2) for m in RE_T.finditer(xml))


def parrafo_traslado(x: str) -> re.Match | None:
    cand = [
        m
        for m in RE_P.finditer(x)
        if "artículo 223" in texto(m.group(0))
        and all(n["ancla"] in texto(m.group(0)) for n in NOTAS)
    ]
    return cand[0] if len(cand) == 1 else None


def anclar(p: str, ancla: str, run_ref: str) -> tuple[str, str | None]:
    """Parte el run que contiene `ancla` y mete `run_ref` justo detras.

    Si ya hay una llamada inmediatamente detras, devuelve su id y no toca nada.
    """
    for m in RE_R.finditer(p):
        r = m.group(0)
        for t in RE_T.finditer(r):
            k = t.group(2).find(ancla)
            if k < 0:
                continue
            corte = k + len(ancla)
            antes, despues = t.group(2)[:corte], t.group(2)[corte:]
            if not despues and not RE_T.search(r[t.end() :]):
                sig = re.match(
                    r"(?:\s|<w:proofErr[^>]*/>|<w:bookmark(?:Start|End)[^>]*/>)*"
                    r"<w:r\b[^>]*>(?:(?!</w:r>).)*?<w:footnoteReference\b[^>]*w:id=\"(\d+)\"",
                    p[m.end() :],
                    re.S,
                )
                if sig:
                    return p, sig.group(1)
            cabeza = re.match(r"<w:r\b[^>]*>(?:\s*<w:rPr>.*?</w:rPr>)?", r, re.S).group(
                0
            )
            a = r[: t.start()] + '<w:t xml:space="preserve">%s</w:t></w:r>' % antes
            cola = r[t.end() :]
            b = ""
            if despues or cola != "</w:r>":
                b = cabeza + '<w:t xml:space="preserve">%s</w:t>' % despues + cola
            return p[: m.start()] + a + run_ref + b + p[m.end() :], None
    raise ValueError("ancla no encontrada: %s" % ancla)


def _limpiar_rpr(rpr: str) -> str:
    rpr = re.sub(r"<w:(?:b|bCs|i|iCs|u|vertAlign|rStyle|highlight)\b[^>]*/>", "", rpr)
    return rpr


def _con_negrita(rpr: str) -> str:
    m = re.search(r"<w:rFonts\b[^>]*/>", rpr)
    ins = "<w:b/><w:bCs/>"
    if m:
        return rpr[: m.end()] + ins + rpr[m.end() :]
    return rpr.replace("<w:rPr>", "<w:rPr>" + ins, 1)


def molde(fx: str, x: str) -> dict:
    """Formato de la primera nota LLAMADA en el documento que no sea del traslado.

    Se elige por orden de llamada y no por orden en footnotes.xml: ese orden lo
    cambia `ordenar_notas`, y el molde tiene que ser el mismo en cada pasada.
    """
    canon = {texto_canonico(n) for n in NOTAS}
    cuerpos = {m.group(1): m.group(0) for m in RE_FN.finditer(fx)}
    base = None
    for i in re.findall(r'<w:footnoteReference\b[^>]*w:id="(\d+)"', x):
        c = cuerpos.get(i, "")
        plano = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", c)).strip()
        if "<w:footnoteRef" in c and plano not in canon:
            base = c
            break
    if base is None:
        ppr = (
            '<w:pPr><w:pStyle w:val="Textonotapie"/><w:ind w:left="567" w:hanging="567"/>'
            '<w:jc w:val="both"/></w:pPr>'
        )
        rpr = (
            '<w:rPr><w:rFonts w:ascii="Arial Narrow" w:hAnsi="Arial Narrow" w:cs="Arial"/>'
            '<w:sz w:val="16"/><w:szCs w:val="16"/></w:rPr>'
        )
        ref = (
            '<w:r><w:rPr><w:rStyle w:val="Refdenotaalpie"/><w:rFonts w:ascii="Arial Narrow" '
            'w:hAnsi="Arial Narrow"/><w:vertAlign w:val="superscript"/></w:rPr><w:footnoteRef/></w:r>'
        )
        return {"ppr": ppr, "rpr": rpr, "ref": ref, "tab": True}
    p1 = RE_P.search(base).group(0)
    ppr_m = re.search(r"<w:pPr>.*?</w:pPr>", p1, re.S)
    ppr = ppr_m.group(0) if ppr_m else ""
    ppr = re.sub(r"<w:rPr>.*?</w:rPr>", "", ppr, flags=re.S)
    ref = next(r.group(0) for r in RE_R.finditer(p1) if "<w:footnoteRef" in r.group(0))
    rpr = None
    for r in RE_R.finditer(base):
        if "<w:footnoteRef" in r.group(0):
            continue
        if re.search(r"<w:t(?:\s[^>/]*)?>[^<\s]", r.group(0)):
            m = re.search(r"<w:rPr>.*?</w:rPr>", r.group(0), re.S)
            rpr = m.group(0) if m else "<w:rPr></w:rPr>"
            break
    rpr = _limpiar_rpr(rpr or "<w:rPr></w:rPr>")
    tras_ref = p1[p1.index(ref) + len(ref) :]
    tab = "<w:tab/>" in tras_ref[:600]
    return {"ppr": ppr, "rpr": rpr, "ref": ref, "tab": tab}


def _run(rpr: str, contenido: str) -> str:
    return "<w:r>%s%s</w:r>" % (rpr, contenido)


def _esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def cuerpo_nota(nota: dict, f: dict) -> str:
    sangria_francesa = "w:hanging" in f["ppr"]
    ps = []
    for k, segs in enumerate(nota["parrafos"]):
        runs = []
        if k == 0:
            runs.append(f["ref"])
            runs.append(
                _run(
                    f["rpr"],
                    "<w:tab/>" if f["tab"] else '<w:t xml:space="preserve"> </w:t>',
                )
            )
        elif sangria_francesa and f["tab"]:
            runs.append(_run(f["rpr"], "<w:tab/>"))
        for estilo, t in segs:
            rpr = _con_negrita(f["rpr"]) if estilo == "b" else f["rpr"]
            runs.append(_run(rpr, '<w:t xml:space="preserve">%s</w:t>' % _esc(t)))
        ps.append("<w:p>%s%s</w:p>" % (f["ppr"], "".join(runs)))
    return "".join(ps)


def texto_canonico(nota: dict) -> str:
    return re.sub(
        r"\s+", " ", "".join(t for segs in nota["parrafos"] for _e, t in segs)
    ).strip()


def ordenar_notas(fx: str, x: str) -> str:
    """Deja footnotes.xml en el orden en que las notas se llaman en el documento."""
    orden = []
    for i in re.findall(r'<w:footnoteReference\b[^>]*w:id="(\d+)"', x):
        if i not in orden:
            orden.append(i)
    elems = list(RE_FN.finditer(fx))
    if not elems:
        return fx
    sep = [m.group(0) for m in elems if int(m.group(1)) <= 0]
    reales = [m for m in elems if int(m.group(1)) > 0]
    pos = {i: k for k, i in enumerate(orden)}
    reales.sort(key=lambda m: pos.get(m.group(1), len(orden)))
    return (
        fx[: elems[0].start()]
        + "".join(sep)
        + "".join(m.group(0) for m in reales)
        + fx[elems[-1].end() :]
    )


def procesar(x: str, fx: str) -> tuple[str, str]:
    m = parrafo_traslado(x)
    if not m:
        raise ValueError("sin parrafo de traslado unico")
    ids = [int(i) for i in re.findall(r'<w:footnote\b[^>]*w:id="(-?\d+)"', fx)]
    siguiente = max([0] + ids) + 1
    plantilla_ref = next(
        (r.group(0) for r in RE_R.finditer(x) if "<w:footnoteReference" in r.group(0)),
        REF_POR_DEFECTO,
    )
    f = molde(fx, x)
    p = m.group(0)
    for nota in NOTAS:
        run_ref = RE_REF_ID.sub(
            lambda r: r.group(1) + str(siguiente) + r.group(3), plantilla_ref, 1
        )
        p, existente = anclar(p, nota["ancla"], run_ref)
        cuerpo = cuerpo_nota(nota, f)
        if existente:
            fx = re.sub(
                r'(<w:footnote\b[^>]*w:id="%s"[^>]*>).*?(</w:footnote>)' % existente,
                lambda g: g.group(1) + cuerpo + g.group(2),
                fx,
                count=1,
                flags=re.S,
            )
        else:
            fx = fx.replace(
                "</w:footnotes>",
                '<w:footnote w:id="%d">%s</w:footnote></w:footnotes>'
                % (siguiente, cuerpo),
                1,
            )
            siguiente += 1
    x = x[: m.start()] + p + x[m.end() :]
    return x, ordenar_notas(fx, x)


def notas_ancladas(x: str, fx: str) -> list[str]:
    """Fallos si el parrafo del traslado no tiene sus dos notas canonicas (R-173)."""
    m = parrafo_traslado(x)
    if not m:
        return [
            "R-173: no se encuentra un unico parrafo de traslado con sus dos normas"
        ]
    marcado = re.sub(
        r'<w:footnoteReference\b[^>]*w:id="(\d+)"[^>]*/>',
        lambda g: "[[N%s]]" % g.group(1),
        m.group(0),
    )
    plano = re.sub(r"<[^>]+>", "", re.sub(r"(<w:t(?:\s[^>/]*)?>)", "", marcado))
    textos = {
        i: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", c)).strip()
        for i, c in re.findall(
            r'<w:footnote\b[^>]*w:id="(\d+)"[^>]*>(.*?)</w:footnote>', fx, re.S
        )
    }
    fallos = []
    for nota in NOTAS:
        g = re.search(re.escape(nota["ancla"]) + r"\[\[N(\d+)\]\]", plano)
        if not g:
            fallos.append(
                "R-173: falta la nota al pie detras de «%s» en el traslado"
                % nota["ancla"]
            )
        elif textos.get(g.group(1), "") != texto_canonico(nota):
            fallos.append(
                "R-173: la nota de «%s» no es la canonica (docs/notas_traslado.json)"
                % nota["ancla"]
            )
    return fallos


def main(argv: list[str]) -> int:
    aplicar = "--aplicar" in argv
    rutas = [Path(a) for a in argv if not a.startswith("--")]
    if not rutas:
        rutas = sorted((RAIZ / "plantillas_maestras").rglob("*.docx")) + sorted(
            (RAIZ / "automatizacion_antigravity/modelos").glob("*.docx")
        )
    tocados = errores = 0
    for ruta in rutas:
        with zipfile.ZipFile(ruta) as z:
            infos = z.infolist()
            datos = {i.filename: z.read(i.filename) for i in infos}
        x = datos["word/document.xml"].decode("utf-8")
        fx = datos["word/footnotes.xml"].decode("utf-8")
        try:
            x2, fx2 = procesar(x, fx)
        except ValueError as exc:
            errores += 1
            print("  ERROR %s: %s" % (ruta.name, exc))
            continue
        if notas_ancladas(x2, fx2):
            errores += 1
            print("  ERROR %s: %s" % (ruta.name, notas_ancladas(x2, fx2)))
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
        "%s: %d de %d documentos con las notas del traslado; %d errores"
        % ("APLICADO" if aplicar else "SIMULACION", tocados, len(rutas), errores)
    )
    return 1 if errores else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
