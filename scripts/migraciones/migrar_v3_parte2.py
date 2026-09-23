#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Migracion v3, parte 2: mandatos del instructor del 23/09/2026 (segunda tanda).

Sobre el cuerpo (document.xml) y las notas al pie (footnotes.xml):
  1. Nunca "N°", "Nº", "N.º", "Nro.", "N." ni "N" ante un numero, en NINGUN
     contexto (normas, articulos, expediente, poliza, documento de traslado,
     memorandum, resolucion...): se escribe el numero directo.
  2. Fechas: "de 2025", nunca "del 2025"; mes en minuscula; "13 de noviembre
     2025" -> "13 de noviembre de 2025".
  3. Nota al pie del traslado: "recibida", nunca "recepcionada"; "de fecha de
     fecha" -> "de fecha".
  4. "LUISA ANALI" -> "LUISA ANALÍ" (con tilde, siempre).

Uso:
    python scripts/migraciones/migrar_v3_parte2.py [--aplicar]
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import re  # noqa: E402

from migrar_v3_parte1 import RAIZ, RE_P, reemplazar_en_parrafo  # noqa: E402

MESES = "enero|febrero|marzo|abril|mayo|junio|julio|agosto|setiembre|septiembre|octubre|noviembre|diciembre"

REGLAS = [
    ("numero_sin_N", re.compile(r"\b(?:N[°º]|Nº|N\.\s?º|Nro\.?|nro\.?)\s*(?=\d)"), ""),
    ("numero_sin_N", re.compile(r"(?<=[A-Za-zÁÉÍÓÚáéíóú\)] )N\.?\s+(?=\d)"), ""),
    (
        "fecha_del_anio",
        re.compile(r"\b(\d{1,2}) de (%s) del (\d{4})\b" % MESES, re.I),
        None,
    ),
    (
        "fecha_sin_de",
        re.compile(r"\b(\d{1,2}) de (%s),? (\d{4})\b" % MESES, re.I),
        None,
    ),
    (
        "fecha_mes_mayuscula",
        re.compile(r"\b(\d{1,2}) de (%s) de (\d{4})\b" % MESES, re.I),
        None,
    ),
    (
        "mes_del_anio",
        re.compile(r"\b(%s) del ((?:19|20)\d\d)\b" % MESES, re.I),
        r"\1 de \2",
    ),
    ("recibida", re.compile(r"\brecepcionad([ao]s?)\b"), r"recibid\1"),
    ("de_fecha_duplicado", re.compile(r"\bde fecha de fecha\b"), "de fecha"),
    ("anali_con_tilde", re.compile(r"\bANALI\b"), "ANALÍ"),
    ("anali_con_tilde", re.compile(r"\bAnali\b"), "Analí"),
]


def fecha(m: re.Match) -> str:
    mes = m.group(2).lower().replace("septiembre", "setiembre")
    return "%s de %s de %s" % (m.group(1), mes, m.group(3))


def migrar_xml(xml: str, informe: Counter) -> str:
    cambios = {}
    for p in RE_P.findall(xml):
        nuevo = p
        for nombre, patron, sustituto in REGLAS:
            antes = nuevo
            nuevo, n = reemplazar_en_parrafo(
                nuevo, patron, sustituto if sustituto is not None else fecha
            )
            if nombre == "fecha_mes_mayuscula":
                n = 0 if nuevo == antes else n  # solo cuenta si cambio algo
            informe[nombre] += n
        if nuevo != p:
            cambios[p] = nuevo
    for viejo, nuevo in cambios.items():
        xml = xml.replace(viejo, nuevo, 1)
    return xml


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true")
    a = ap.parse_args()
    archivos = sorted(
        p
        for p in (RAIZ / "plantillas_maestras").rglob("*")
        if p.suffix.lower() == ".docx"
    )
    archivos += sorted((RAIZ / "automatizacion_antigravity/modelos").glob("*.docx"))
    informe, tocados = Counter(), 0
    for ruta in archivos:
        with zipfile.ZipFile(ruta) as z:
            partes = {n: z.read(n) for n in z.namelist()}
            infos = z.infolist()
        cambiado = False
        for parte in ("word/document.xml", "word/footnotes.xml"):
            if parte not in partes:
                continue
            xml = partes[parte].decode("utf-8")
            nuevo = migrar_xml(xml, informe)
            if nuevo != xml:
                partes[parte] = nuevo.encode("utf-8")
                cambiado = True
        if cambiado:
            tocados += 1
            if a.aplicar:
                tmp = ruta.with_suffix(".tmp")
                with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
                    for info in infos:
                        zout.writestr(info, partes[info.filename])
                tmp.replace(ruta)
    print(
        "%s: %d documentos, %d modificados"
        % ("APLICADO" if a.aplicar else "SIMULACION", len(archivos), tocados)
    )
    for k, v in sorted(informe.items()):
        print("  %-22s %d" % (k, v))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
