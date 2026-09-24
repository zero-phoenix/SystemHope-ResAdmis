#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Triaje de expediente: inventario de paginas y dossier anclado para contrastar.

Uso:
    python scripts/extraer_expediente.py <carpeta_del_expediente> [--volcar]

**Mandato del instructor (14/09/2026), R-137: cero OCR, Google Lens siempre.**
Todas las paginas del expediente se leen con la vision Google Lens de Antigravity,
tengan o no capa de texto. Este script **no sustituye** esa lectura: la prepara.

Que aporta, entonces:
  - el **numero real de paginas** de cada PDF (estructura, no texto): sin el, un
    documento escaneado se daba por vacio (R-136);
  - que paginas tienen capa de texto y cuales no, como dato de contexto;
  - el **texto embebido**, que sirve de **contraste** contra lo que lea Lens, no de
    reemplazo: esta medido que el volcado pierde tildes y corrompe caracteres
    («1274 de agosto» por «17 de agosto», «MART?N» por «MARTIN») (R-126);
  - un dossier de fechas, cartas notariales, montos, placas, correos y
    resoluciones previas, cada dato anclado a la pagina de la que salio.

Ante discrepancia entre el volcado y lo que ve Lens, **manda Lens**.

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


def paginas_reales(ruta: Path) -> int | None:
    """Numero de paginas segun la estructura del PDF, no segun su texto.

    Es el ancla del triaje: un PDF integramente escaneado no produce texto, y sin
    este conteo el triaje lo daba por vacio (R-136).
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return None
    try:
        with fitz.open(str(ruta)) as doc:
            return doc.page_count
    except Exception:
        return None


def paginas_de_pdf(ruta: Path) -> list[str]:
    """Texto por pagina, con tantas entradas como paginas tenga el PDF.

    Usa pdftotext si esta disponible (≈11x mas rapido que las librerias puras de
    Python) y cuadra el resultado contra el numero real de paginas: las que no
    dieron texto quedan como cadena vacia para que el triaje las mande a vision.
    """
    paginas: list[str] | None = None
    if shutil.which("pdftotext"):
        salida = subprocess.run(
            # -enc UTF-8: sin el, pdftotext escribe en la codificacion del sistema
            # (cp1252 en Windows) y la lectura en UTF-8 dejaba «falleci�» (v3.2).
            ["pdftotext", "-enc", "UTF-8", "-layout", str(ruta), "-"], capture_output=True
        ).stdout.decode("utf-8", "replace")
        paginas = salida.split("\f")
        # pdftotext cierra la salida con un form-feed: el ultimo trozo es vacio y
        # no es una pagina. Se descarta **uno solo**: descartarlos todos borraba
        # el expediente entero cuando ninguna pagina tenia capa de texto.
        if paginas and not paginas[-1].strip():
            paginas.pop()
    if paginas is None:
        try:
            from pypdf import PdfReader  # type: ignore
        except ImportError:
            from PyPDF2 import PdfReader  # type: ignore
        paginas = [(p.extract_text() or "") for p in PdfReader(str(ruta)).pages]

    total = paginas_reales(ruta)
    if total is not None and len(paginas) != total:
        # El conteo estructural manda. Si pdftotext devolvio de menos (PDF
        # escaneado) se rellena; si devolvio de mas, se recorta.
        paginas = (paginas + [""] * total)[:total]
    return paginas


def renderizar_paginas(carpeta: Path, dpi: int = 170) -> list[tuple[str, int, Path]]:
    """Deja cada pagina del expediente como PNG en `_paginas/`, lista para mirar.

    R-137 obliga a leer **todas** las paginas con Google Lens. Si el agente tiene
    que inventarse el mecanismo, gasta llamadas en descubrirlo y a veces no lo
    hace: medido en el Expediente 3122-2026, 17 llamadas y 6 minutos sin una sola
    pasada de vision. La lectura obligatoria se sirve preparada.

    Devuelve [(archivo_pdf, numero_de_pagina, ruta_png)] y no rehace lo ya hecho.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return []

    destino = carpeta / "_paginas"
    destino.mkdir(exist_ok=True)
    salida: list[tuple[str, int, Path]] = []
    for pdf in sorted(carpeta.glob("*.pdf")):
        try:
            doc = fitz.open(str(pdf))
        except Exception:
            continue
        with doc:
            for pagina in doc:
                n = pagina.number + 1
                png = destino / ("%s_p%02d.png" % (pdf.stem[:40].replace(" ", "_"), n))
                if not png.exists():
                    pagina.get_pixmap(dpi=dpi).save(str(png))
                salida.append((pdf.name, n, png))
    return salida


MESES_ES = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
    "agosto", "setiembre", "octubre", "noviembre", "diciembre",
)


def firmas_digitales(ruta: Path) -> list[tuple[str, str]]:
    """Fecha de cada firma digital del PDF, como «12 de agosto de 2026», con su motivo.

    La fecha de un escrito de parte es la de su firma digital (mesa de partes
    virtual o presencial: «Fedatario - Copia fiel del original»). Sin esto, el
    agente improvisaba `python -c` para leerla (Exp. 2898-2026, 23/09/2026).
    """
    try:
        from pypdf import PdfReader

        campos = PdfReader(str(ruta)).get_fields() or {}
    except Exception:
        return []
    salida = []
    for campo in campos.values():
        if campo.get("/FT") != "/Sig" or not campo.get("/V"):
            continue
        v = campo["/V"].get_object()
        m = re.match(r"D:(\d{4})(\d{2})(\d{2})", str(v.get("/M") or ""))
        if not m:
            continue
        fecha = "%d de %s de %s" % (int(m.group(3)), MESES_ES[int(m.group(2)) - 1], m.group(1))
        salida.append((fecha, re.sub(r"\s+", " ", str(v.get("/Reason") or ""))[:70]))
    return salida


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
    sin_capa = sum(len(i["sin_texto"]) for i in inventario)
    print("=" * 78)
    print("TRIAJE DE EXPEDIENTE  %s" % carpeta)
    print("=" * 78)
    for i in inventario:
        estado = (
            "con capa de texto (sirve de contraste)"
            if not i["sin_texto"]
            else "poco o ningun texto embebido (<%d car.) en p. %s" % (UMBRAL_TEXTO, i["sin_texto"])
        )
        print(
            "  %-46s %2d pag  %6d car  %s"
            % (i["archivo"][:46], i["paginas"], i["caracteres"], estado)
        )
    print()
    print("  Paginas totales ................ %d" % total)
    print("  Con capa de texto (contraste) .. %d" % (total - sin_capa))
    print("  Sin capa de texto .............. %d" % sin_capa)
    print("  PAGINAS A LEER CON GOOGLE LENS . %d  (todas, R-137)" % total)
    print("  --> Cero OCR. Todas las paginas se leen con Google Lens, tengan o no")
    print("      capa de texto. El volcado de texto es CONTRASTE, no reemplazo:")
    print("      esta medido que pierde tildes y corrompe caracteres (R-126).")
    print("      Ante discrepancia entre el volcado y lo que ve Lens, manda Lens.")
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
