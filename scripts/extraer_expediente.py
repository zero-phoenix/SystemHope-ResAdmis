#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Triaje de expediente: texto exacto donde lo hay, vision solo donde hace falta.

Uso:
    python scripts/extraer_expediente.py <carpeta_del_expediente> [--volcar]

R-95 manda vision multimodal para escritos **escaneados o manuscritos**. No manda
gastar vision en PDF nativos, que llevan el texto exacto embebido: leerlo es mas
fiel que mirarlo, porque no hay lectura que alucinar.

Este script decide pagina por pagina:
  - pagina CON capa de texto  -> se extrae literal (determinista, coste ~0)
  - pagina SIN capa de texto  -> se marca para vision, con su numero exacto

Ademas arma un dossier de los datos que el admisorio necesita citar sin error
(fechas, cartas notariales, montos, placas, correos, resoluciones previas),
cada uno anclado a la pagina de la que salio, para que sea verificable.

Codigo de salida: 0 siempre; el valor esta en el informe.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

UMBRAL_TEXTO = (
    120  # caracteres minimos para considerar que la pagina tiene capa de texto
)

MESES = "enero|febrero|marzo|abril|mayo|junio|julio|agosto|setiembre|septiembre|octubre|noviembre|diciembre"

PATRONES = {
    "fechas": re.compile(r"\b(\d{1,2}\s+de\s+(?:%s)\s+de[l]?\s+\d{4})\b" % MESES, re.I),
    "cartas_notariales": re.compile(
        r"Carta\s+Notarial(?:es)?\s*(?:N\.?°|N°|No\.?|N\.)?\s*([\w\-/]+)", re.I
    ),
    "montos": re.compile(r"(?:US\$|S/\.?|\$)\s*[\d][\d\s.,]*\d"),
    "placas": re.compile(r"\b[A-Z]{2,3}\s?-\s?\d{3,4}\b|\b\d{4}\s?-\s?[A-Z]{2}\b"),
    "correos": re.compile(r"[\w.\-]+@[\w.\-]+\.\w+"),
    "polizas_siniestros": re.compile(
        r"(?:P[oó]liza|Siniestro|Formato)[^.\n]{0,40}?(\d{5,})", re.I
    ),
    "resoluciones_previas": re.compile(
        r"Resoluci[oó]n\s*(?:N\.?°|N°|No\.?)?\s*(\d{1,3})\b", re.I
    ),
    "expediente": re.compile(r"\b(\d{3,4}-\d{4})\s*[/-]\s*CC1\b", re.I),
}


def paginas_de_pdf(ruta: Path) -> list[str]:
    """Texto por pagina. Usa pdftotext si esta disponible (≈11x mas rapido que
    las librerias puras de Python); si no, cae a pypdf/PyPDF2."""
    if shutil.which("pdftotext"):
        salida = subprocess.run(
            ["pdftotext", "-layout", str(ruta), "-"], capture_output=True
        ).stdout.decode("utf-8", "replace")
        paginas = salida.split("\f")
        # pdftotext cierra la salida con un form-feed: el ultimo trozo es vacio y
        # no es una pagina. Sin esto cada PDF reporta una pagina de mas y el
        # triaje manda a vision una pagina que no existe.
        while paginas and not paginas[-1].strip():
            paginas.pop()
        return paginas
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        from PyPDF2 import PdfReader  # type: ignore
    return [(p.extract_text() or "") for p in PdfReader(str(ruta)).pages]


def triaje(carpeta: Path):
    pdfs = sorted(carpeta.glob("*.pdf"))
    if not pdfs:
        print("No hay PDF en %s" % carpeta)
        return [], {}

    inventario = []
    corpus = []
    for pdf in pdfs:
        paginas = paginas_de_pdf(pdf)
        con_texto = [
            i + 1 for i, t in enumerate(paginas) if len(t.strip()) >= UMBRAL_TEXTO
        ]
        sin_texto = [
            i + 1 for i, t in enumerate(paginas) if len(t.strip()) < UMBRAL_TEXTO
        ]
        inventario.append(
            {
                "archivo": pdf.name,
                "paginas": len(paginas),
                "con_texto": con_texto,
                "sin_texto": sin_texto,
                "caracteres": sum(len(t) for t in paginas),
            }
        )
        for i, t in enumerate(paginas):
            if len(t.strip()) >= UMBRAL_TEXTO:
                corpus.append((pdf.name, i + 1, t))

    dossier: dict[str, dict[str, list[str]]] = {k: {} for k in PATRONES}
    for nombre, npag, texto in corpus:
        ancla = "%s p.%d" % (nombre, npag)
        for clave, patron in PATRONES.items():
            for m in patron.finditer(texto):
                valor = re.sub(r"\s+", " ", m.group(0)).strip()
                dossier[clave].setdefault(valor, [])
                if ancla not in dossier[clave][valor]:
                    dossier[clave][valor].append(ancla)
    return inventario, dossier


def informe(carpeta: Path, volcar: bool) -> None:
    inventario, dossier = triaje(carpeta)
    if not inventario:
        return

    total = sum(i["paginas"] for i in inventario)
    vision = sum(len(i["sin_texto"]) for i in inventario)
    print("=" * 78)
    print("TRIAJE DE EXPEDIENTE  %s" % carpeta)
    print("=" * 78)
    for i in inventario:
        estado = (
            "texto completo"
            if not i["sin_texto"]
            else "vision en p. %s" % i["sin_texto"]
        )
        print(
            "  %-46s %2d pag  %6d car  %s"
            % (i["archivo"][:46], i["paginas"], i["caracteres"], estado)
        )
    print()
    print("  Paginas totales ................ %d" % total)
    print("  Resueltas por capa de texto .... %d" % (total - vision))
    print("  Requieren vision multimodal .... %d" % vision)
    if vision == 0:
        print("  --> Cero pasadas de vision. R-95 no aplica: no hay pagina escaneada.")
    else:
        print("  --> Aplicar vision SOLO a las paginas listadas arriba (R-95).")
    print()

    print("DOSSIER VERIFICABLE (cada dato con la pagina de la que salio)")
    print("-" * 78)
    orden = [
        "expediente",
        "resoluciones_previas",
        "fechas",
        "cartas_notariales",
        "polizas_siniestros",
        "montos",
        "placas",
        "correos",
    ]
    for clave in orden:
        valores = dossier.get(clave) or {}
        if not valores:
            continue
        print("  %s (%d)" % (clave.replace("_", " ").upper(), len(valores)))
        for valor, anclas in sorted(valores.items(), key=lambda kv: -len(kv[1]))[:14]:
            print("     %-42s  %s" % (valor[:42], ", ".join(anclas[:3])))
        print()

    if volcar:
        destino = carpeta / "_texto_expediente.txt"
        with destino.open("w", encoding="utf-8") as fh:
            for pdf in sorted(carpeta.glob("*.pdf")):
                for n, t in enumerate(paginas_de_pdf(pdf), 1):
                    fh.write("\n\n===== %s p.%d =====\n" % (pdf.name, n))
                    fh.write(t)
        print("  Texto integro volcado en %s" % destino)
        print("  (archivo de trabajo: NO pertenece al repositorio)")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("carpeta", help="Carpeta con los PDF del expediente")
    ap.add_argument(
        "--volcar",
        action="store_true",
        help="Escribe el texto integro en _texto_expediente.txt dentro de la carpeta",
    )
    args = ap.parse_args(argv[1:])
    informe(Path(args.carpeta), args.volcar)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
