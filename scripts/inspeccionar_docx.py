#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Radiografia completa de un .docx en una sola llamada.

Uso:
    python scripts/inspeccionar_docx.py <archivo.docx>                # volcado integro
    python scripts/inspeccionar_docx.py <archivo.docx> --resumen      # esqueleto
    python scripts/inspeccionar_docx.py <candidato.docx> --diff <control.docx>

Por que existe: inspeccionar un documento parrafo por parrafo y run por run con
llamadas sucesivas ("lee el parrafo 75", "ahora sus runs", "ahora sus notas")
cuesta decenas de idas y vueltas por documento y es donde se va el tiempo. Todo
lo que esas llamadas averiguan por separado esta aqui en una sola salida:
texto, negritas, subrayados, estilo, numeracion, anclas de nota al pie, notas,
encabezados, pies y propiedades de seccion.

El modo --diff compara contra un documento de control y **solo imprime lo que
difiere**, que es lo unico que hay que corregir.
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

ORDINALES = (
    "PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|S[EÉ]TIMO|OCTAVO|NOVENO|D[EÉ]CIMO"
    "|UND[EÉ]CIMO|DUOD[EÉ]CIMO"
)


def marca(texto: str, bold: bool, subrayado: bool) -> str:
    if bold:
        texto = "**%s**" % texto
    if subrayado:
        texto = "__%s__" % texto
    return texto


def leer_parrafos(xml: bytes):
    root = ET.fromstring(xml)
    salida = []
    for p in root.iter(W + "p"):
        pr = p.find(W + "pPr")
        estilo = numid = ilvl = jc = ""
        if pr is not None:
            s = pr.find(W + "pStyle")
            estilo = s.get(W + "val") if s is not None else ""
            num = pr.find(W + "numPr")
            if num is not None:
                a = num.find(W + "numId")
                b = num.find(W + "ilvl")
                numid = a.get(W + "val") if a is not None else ""
                ilvl = b.get(W + "val") if b is not None else ""
            j = pr.find(W + "jc")
            jc = j.get(W + "val") if j is not None else ""
        piezas, plano, notas = [], [], []
        for r in p.iter(W + "r"):
            rpr = r.find(W + "rPr")
            b = rpr.find(W + "b") if rpr is not None else None
            u = rpr.find(W + "u") if rpr is not None else None
            bold = b is not None and b.get(W + "val") not in ("0", "false")
            sub = u is not None and u.get(W + "val") not in ("none",)
            texto = "".join(t.text or "" for t in r.iter(W + "t"))
            for fr in r.iter(W + "footnoteReference"):
                notas.append(fr.get(W + "id"))
                texto += "[^%s]" % fr.get(W + "id")
            if texto:
                piezas.append(marca(texto, bold, sub))
                plano.append(texto)
        salida.append(
            {
                "estilo": estilo,
                "numid": numid,
                "ilvl": ilvl,
                "jc": jc,
                "marcado": re.sub(r"\*\*\*\*|____", "", "".join(piezas)),
                "texto": "".join(plano),
                "notas": notas,
            }
        )
    return salida


def abrir(ruta: str):
    z = zipfile.ZipFile(ruta)
    doc = leer_parrafos(z.read("word/document.xml"))
    crudo = z.read("word/document.xml").decode("utf-8", "replace")
    return z, doc, crudo


def volcar(ruta: str, resumen: bool) -> None:
    z, doc, crudo = abrir(ruta)
    print("=" * 78)
    print(ruta)
    print("=" * 78)

    if resumen:
        print("ESQUELETO")
        for i, p in enumerate(doc):
            t = p["texto"].strip()
            if not t:
                continue
            if (
                re.match(r"\s*(%s)\s*:" % ORDINALES, t, re.I)
                or t.isupper()
                or p["estilo"].startswith("Ttulo")
            ):
                print("  %03d  %.100s" % (i, re.sub(r"\s+", " ", p["marcado"])))
        print()
    else:
        print("CUERPO  (%d parrafos)" % len(doc))
        for i, p in enumerate(doc):
            if not p["texto"].strip() and not p["numid"]:
                continue
            meta = "".join(
                filter(
                    None,
                    [
                        "{%s}" % p["estilo"] if p["estilo"] else "",
                        "<num %s/%s>" % (p["numid"], p["ilvl"]) if p["numid"] else "",
                        "<%s>" % p["jc"] if p["jc"] else "",
                        "<VACIO>" if not p["texto"].strip() else "",
                    ],
                )
            )
            print("  %03d %s %s" % (i, meta, re.sub(r"\s+", " ", p["marcado"])))
        print()

        if "word/footnotes.xml" in z.namelist():
            print("NOTAS AL PIE")
            root = ET.fromstring(z.read("word/footnotes.xml"))
            usadas = {n for p in doc for n in p["notas"]}
            for fn in root.iter(W + "footnote"):
                fid = fn.get(W + "id")
                if fn.get(W + "type") in (
                    "separator",
                    "continuationSeparator",
                    "continuationNotice",
                ):
                    continue
                texto = re.sub(
                    r"\s+", " ", "".join(t.text or "" for t in fn.iter(W + "t"))
                ).strip()
                if not texto:
                    continue
                estado = "anclada" if fid in usadas else "SIN ANCLA"
                print("  [%s] %-9s %.110s" % (fid, estado, texto))
            print()

    print("ENCABEZADOS Y PIES")
    for n in sorted(
        x for x in z.namelist() if re.match(r"word/(head|foot)er\d+\.xml", x)
    ):
        t = re.sub(
            r"\s+", " ", re.sub(r"<[^>]+>", " ", z.read(n).decode("utf-8", "replace"))
        ).strip()
        print("  %-14s %s" % (n.replace("word/", ""), t[:100] if t else "(vacio)"))
    refs = re.findall(r'<w:(?:header|footer)Reference w:type="(\w+)"', crudo)
    print("  referencias de seccion: %d  %s" % (len(refs), refs))
    print("  titlePg: %s" % ("si" if "<w:titlePg" in crudo else "no"))
    print()


def diferencias(candidato: str, control: str) -> None:
    _, doc_c, _ = abrir(candidato)
    _, doc_k, _ = abrir(control)

    def normaliza(ps):
        return [
            re.sub(r"\s+", " ", p["marcado"]).strip() for p in ps if p["texto"].strip()
        ]

    a, b = normaliza(doc_c), normaliza(doc_k)
    print("=" * 78)
    print("DIFERENCIAS   candidato: %s" % candidato)
    print("              control  : %s" % control)
    print("=" * 78)
    hubo = False
    for linea in difflib.unified_diff(b, a, "control", "candidato", lineterm="", n=0):
        if linea.startswith(("---", "+++", "@@")):
            continue
        hubo = True
        signo = "FALTA " if linea.startswith("-") else "SOBRA "
        print("  %s %.150s" % (signo, linea[1:]))
    if not hubo:
        print("  Sin diferencias de texto ni de negritas.")
    print()
    print("  NOTA: 'FALTA' = esta en el control y no en el candidato.")
    print("        'SOBRA' = esta en el candidato y no en el control.")
    print("        Los pares FALTA/SOBRA casi identicos son una sola frase reescrita.")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("archivo")
    ap.add_argument(
        "--resumen", action="store_true", help="Solo el esqueleto de la resolucion"
    )
    ap.add_argument(
        "--diff", metavar="CONTROL", help="Compara contra un documento de control"
    )
    args = ap.parse_args(argv[1:])
    if args.diff:
        diferencias(args.archivo, args.diff)
    else:
        volcar(args.archivo, args.resumen)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
