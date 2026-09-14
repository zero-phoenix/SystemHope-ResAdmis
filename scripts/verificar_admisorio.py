#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Falsador automatico de admisorios CC1.

Uso:
    python scripts/verificar_admisorio.py <archivo.docx> [...]

Cada prueba corresponde a una regla de `automatizacion_antigravity/REGLAS_DE_APRENDIZAJE.md`
y esta escrita para FALLAR, no para confirmar. Un admisorio se entrega solo con
salida `APTO`. La salida es determinista y apta para CI.

Codigo de salida: 0 si todos los documentos son APTOS, 1 si alguno falla.
"""

from __future__ import annotations

import re
import sys
import zipfile
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

ORDINALES = [
    "PRIMERO",
    "SEGUNDO",
    "TERCERO",
    "CUARTO",
    "QUINTO",
    "SEXTO",
    "SETIMO",
    "OCTAVO",
    "NOVENO",
    "DECIMO",
    "UNDECIMO",
    "DUODECIMO",
]

# R-103 (mandato del instructor, 14/09/2026): TODOS los admisorios firman
# LUISA ANALI SILVA MALPARTIDA como Secretaria Tecnica (e). Nunca Evelyn y
# nunca designacion Ad Hoc. La firma dejo de depender del proveedor.
FIRMA_MANDATO = "LUISA ANALI SILVA MALPARTIDA"
FIRMA_PROHIBIDA = "EVELING ROA QUISPE"
CARGO_MANDATO = "SECRETARIA TECNICA (E)"


def sin_tildes(texto: str) -> str:
    tabla = str.maketrans("áéíóúÁÉÍÓÚñÑüÜ", "aeiouAEIOUnNuU")
    return texto.translate(tabla)


class Parrafo:
    __slots__ = ("texto", "runs_bold", "numerado", "notas", "estilo", "ilvl")

    def __init__(self, texto, runs_bold, numerado, notas, estilo, ilvl):
        self.texto = texto
        self.runs_bold = runs_bold
        self.numerado = numerado
        self.notas = notas
        self.estilo = estilo
        self.ilvl = ilvl

    @property
    def vacio(self) -> bool:
        return not self.texto.strip()


def leer_parrafos(xml: bytes) -> list[Parrafo]:
    root = ET.fromstring(xml)
    salida = []
    for p in root.iter(W + "p"):
        pr = p.find(W + "pPr")
        estilo = ""
        numerado = False
        ilvl = -1
        if pr is not None:
            s = pr.find(W + "pStyle")
            estilo = s.get(W + "val") if s is not None else ""
            num = pr.find(W + "numPr")
            numerado = num is not None
            if num is not None:
                nivel = num.find(W + "ilvl")
                ilvl = int(nivel.get(W + "val")) if nivel is not None else 0
        partes, bolds, notas = [], [], []
        for r in p.iter(W + "r"):
            rpr = r.find(W + "rPr")
            b = rpr.find(W + "b") if rpr is not None else None
            es_bold = b is not None and b.get(W + "val") not in ("0", "false")
            texto = "".join(t.text or "" for t in r.iter(W + "t"))
            for fr in r.iter(W + "footnoteReference"):
                notas.append(fr.get(W + "id"))
            if texto:
                partes.append(texto)
                bolds.append((texto, es_bold))
        salida.append(Parrafo("".join(partes), bolds, numerado, notas, estilo, ilvl))
    return salida


def leer_documento(ruta: str):
    z = zipfile.ZipFile(ruta)
    doc = leer_parrafos(z.read("word/document.xml"))
    crudo = z.read("word/document.xml").decode("utf-8", "replace")
    secciones = re.findall(r"<w:(?:header|footer)Reference[^>]*>", crudo)
    return doc, secciones, z


# --------------------------------------------------------------------------- #
# Pruebas. Cada una devuelve una lista de fallos (vacia = corroborada).
# --------------------------------------------------------------------------- #


def prueba_r97_isomorfismo(doc) -> list[str]:
    """El nucleo factico de la considerativa debe repetirse palabra por palabra
    en el articulo de imputacion correspondiente."""
    nucleos_cons = []
    for p in doc:
        m = re.search(
            r"consistente en que (.+?)(?:;\s*involucrar|\.\s*Por consiguiente)", p.texto, re.S
        )
        if m:
            nucleos_cons.append(re.sub(r"\s+", " ", m.group(1)).strip())
    nucleos_res = []
    for p in doc:
        m = re.search(
            r"Presunta infracci[oó]n .*?, en tanto (.+?)\s*\.\s*$", p.texto, re.S
        )
        if m:
            nucleos_res.append(re.sub(r"\s+", " ", m.group(1)).strip())
    fallos = []
    if not nucleos_cons:
        return ["R-97: no se hallo ningun nucleo factico en la considerativa"]
    if len(nucleos_cons) != len(nucleos_res):
        fallos.append(
            "R-97: %d nucleos en considerativa vs %d imputaciones en resolutiva"
            % (len(nucleos_cons), len(nucleos_res))
        )
    for i, nucleo in enumerate(nucleos_cons):
        if nucleo not in nucleos_res:
            fallos.append(
                "R-97: el nucleo %d no aparece verbatim en la resolutiva: %.90s..."
                % (i + 1, nucleo)
            )
    return fallos


def prueba_r108_requerimiento(doc) -> list[str]:
    """La lista de incisos del REQUERIMIENTO DE INFORMACION (considerativa) debe
    repetirse verbatim en el articulo resolutivo que la ordena."""

    def incisos(texto):
        return [
            re.sub(r"\s+", " ", x).strip()
            for x in re.findall(r"\((?:i|ii|iii|iv)\)\s*([^;]+)", texto)
        ]

    cons = []
    res = []
    for p in doc:
        t = sin_tildes(p.texto)
        if "conviene requerir" in t and "cumpla con" in t:
            cons = incisos(p.texto)
            if not cons:
                return [
                    "R-108: el REQUERIMIENTO DE INFORMACION anuncia 'cumpla con lo siguiente:' y no formula ningun inciso"
                ]
        if (
            re.match(r"\s*(QUINTO|CUARTO|SEXTO)\s*:", sin_tildes(p.texto))
            and "cumpla con" in t
        ):
            res = incisos(p.texto)
    if not cons:
        return [
            "R-108: no existe el parrafo de REQUERIMIENTO DE INFORMACION en la considerativa"
        ]
    if not res:
        return [
            "R-108: no existe el articulo resolutivo espejo del requerimiento probatorio"
        ]
    faltan = [c for c in cons if c not in res]
    return [
        "R-108: inciso de la considerativa ausente en la resolutiva: %.70s..." % c
        for c in faltan
    ]


def prueba_r103_firma(doc) -> list[str]:
    """Mandato del instructor (14/09/2026): firma unica.

    Todos los admisorios firman LUISA ANALI SILVA MALPARTIDA con el cargo
    'Secretaria Tecnica (e)'. Ninguno firma EVELING ROA QUISPE y ninguno usa
    la designacion 'Ad Hoc'.
    """
    texto_doc = sin_tildes(" ".join(p.texto for p in doc)).upper()
    denunciado = ""
    for p in doc:
        t = sin_tildes(p.texto).upper()
        if t.startswith("DENUNCIADO"):
            denunciado = t
            break
    if not denunciado:
        return ["R-103: no se hallo la linea DENUNCIADO en el encabezado"]
    fallos = []
    if FIRMA_MANDATO not in texto_doc:
        fallos.append(
            "R-103: no firma %s (mandato del instructor del 14/09/2026)" % FIRMA_MANDATO
        )
    if CARGO_MANDATO not in texto_doc:
        fallos.append("R-103: falta el cargo 'Secretaria Tecnica (e)' bajo el nombre")
    if FIRMA_PROHIBIDA in texto_doc:
        fallos.append(
            "R-103: firma %s, prohibida por mandato del instructor" % FIRMA_PROHIBIDA
        )
    if "AD HOC" in texto_doc:
        fallos.append("R-103: aparece una designacion 'Ad Hoc', prohibida por mandato")
    return fallos


def prueba_r104_negritas(doc) -> list[str]:
    """El rotulo ordinal de todo articulo resolutivo va en negrita, sin excepcion."""
    fallos = []
    for p in doc:
        t = sin_tildes(p.texto).lstrip()
        for ordinal in ORDINALES:
            if t.startswith(ordinal + ":"):
                bold_rotulo = any(
                    b
                    for texto, b in p.runs_bold
                    if sin_tildes(texto).lstrip().startswith(ordinal)
                )
                if not bold_rotulo:
                    fallos.append("R-104: el rotulo %s: no esta en negrita" % ordinal)
                break
    encabezado = [
        p
        for p in doc[:8]
        if sin_tildes(p.texto)
        .upper()
        .startswith(("EXPEDIENTE", "DENUNCIANTE", "DENUNCIADO", "RESOLUCION"))
    ]
    for p in encabezado:
        if not any(b for _, b in p.runs_bold):
            fallos.append(
                "R-104: la linea de encabezado '%.28s' no esta en negrita"
                % p.texto.strip()
            )
    return fallos


def prueba_r105_vacios(doc) -> list[str]:
    huerfanos = sum(1 for p in doc if p.numerado and p.vacio)
    if huerfanos:
        return [
            "R-105: %d parrafo(s) con numeracion activa y sin texto (viñeta huerfana en Word)"
            % huerfanos
        ]
    return []


def prueba_r106_notas(doc, z) -> list[str]:
    usadas = {n for p in doc for n in p.notas}
    definidas = set()
    if "word/footnotes.xml" in z.namelist():
        root = ET.fromstring(z.read("word/footnotes.xml"))
        for fn in root.iter(W + "footnote"):
            fid = fn.get(W + "id")
            tipo = fn.get(W + "type")
            if tipo in ("separator", "continuationSeparator", "continuationNotice"):
                continue
            if "".join(t.text or "" for t in fn.iter(W + "t")).strip():
                definidas.add(fid)
    huerfanas = sorted(definidas - usadas, key=lambda v: int(v))
    if huerfanas:
        return [
            "R-106: nota(s) al pie definidas sin ancla en el cuerpo: %s"
            % ", ".join(huerfanas)
        ]
    return []


def prueba_r107_membrete(z) -> list[str]:
    """Lo invariante del modelo institucional es el CONTENIDO del encabezado y del
    pie, no el numero de referencias de seccion: el corpus de control incluye
    documentos con seis referencias y documentos con dos."""

    def compacta(texto):
        return re.sub(r"[^A-Z0-9/]", "", sin_tildes(texto).upper())

    cab_xml = pie_xml = ""
    for n in z.namelist():
        if re.match(r"word/header\d+\.xml", n):
            cab_xml += z.read(n).decode("utf-8", "replace")
        if re.match(r"word/footer\d+\.xml", n):
            pie_xml += z.read(n).decode("utf-8", "replace")
    cab = compacta(re.sub(r"<[^>]+>", " ", cab_xml))
    pie = compacta(re.sub(r"<[^>]+>", " ", pie_xml))
    fallos = []
    for etiqueta, esperado in (
        ("membrete linea 1", "SECRETARIATECNICADELA"),
        ("membrete linea 2", "COMISIONDEPROTECCIONALCONSUMIDOR1"),
        ("membrete linea 3", "SEDECENTRAL"),
    ):
        if esperado not in cab:
            fallos.append("R-107: falta el %s en el encabezado" % etiqueta)
    if "MCPC01/03" not in pie:
        fallos.append("R-107: falta el codigo de calidad M-CPC-01/03 en el pie de pagina")
    # El campo dinamico de numero de pagina NO se exige: el control ADM 2723-2026 R2
    # carece de el y es un documento valido. Presente en 2 de 3 controles.
    return fallos


def prueba_r110_modo_verbal(doc) -> list[str]:
    """En los incisos de hechos, toda conducta del proveedor se enuncia bajo
    atribucion al denunciante (estilo indirecto) o en modo potencial. Afirmarla
    en indicativo asertivo prejuzga el fondo antes de los descargos."""
    atribucion = re.compile(
        r"\b(senal[oó]|indic[oó]|precis[oó]|manifest[oó]|refiri[oó]|sostuvo|agreg[oó]"
        r"|aleg[oó]|cuestion[oó]|denunci[oó]|afirm[oó]|declar[oó])\b", re.I)
    potencial = re.compile(r"\bhabr[ií]a\b", re.I)
    proveedor_activo = re.compile(
        r"\b(R[ií]mac|Pac[ií]fico|el Banco|la compa[nñ][ií]a aseguradora|la aseguradora|el proveedor)\b"
        r"\s+(?:no\s+)?(?:se\s+)?(?:le\s+)?[a-záéíóú]+"
        r"(?:[oó]|aron|ieron|uvo|izo|ab[ií]a)\b")
    fallos = []
    dentro = False
    for p in doc:
        t = p.texto.strip()
        if sin_tildes(t).upper().startswith("HECHOS"):
            dentro = True
            continue
        if sin_tildes(t).upper().startswith("DE LA ADMISION A TRAMITE"):
            break
        if not dentro or p.ilvl != 2 or p.vacio:
            continue
        if atribucion.search(t) or potencial.search(t):
            continue
        m = proveedor_activo.search(t)
        if m:
            fallos.append(
                "R-110: inciso de hechos afirma en indicativo la conducta del proveedor "
                "('%s') sin atribucion ni modo potencial: %.60s..." % (m.group(0), t))
    return fallos


PRUEBAS = [
    ("R-97  isomorfismo considerativa/resolutiva", lambda d, s, z: prueba_r97_isomorfismo(d), "falsador"),
    ("R-103 firma segun proveedor denunciado", lambda d, s, z: prueba_r103_firma(d), "falsador"),
    ("R-104 negritas de ordinales y encabezado", lambda d, s, z: prueba_r104_negritas(d), "falsador"),
    ("R-105 parrafos numerados vacios", lambda d, s, z: prueba_r105_vacios(d), "falsador"),
    ("R-106 anclas de nota al pie", lambda d, s, z: prueba_r106_notas(d, z), "falsador"),
    ("R-107 membrete y pie institucional", lambda d, s, z: prueba_r107_membrete(z), "falsador"),
    # R-108 es observacion, no falsador: el control ADM 2723-2026 R2 diverge en una
    # clausula entre considerativa y resolutiva y sigue siendo un documento valido.
    ("R-108 espejo del requerimiento de informacion", lambda d, s, z: prueba_r108_requerimiento(d), "observacion"),
    ("R-110 modo verbal en hechos", lambda d, s, z: prueba_r110_modo_verbal(d), "falsador"),
]


def verificar(ruta: str) -> bool:
    doc, secciones, z = leer_documento(ruta)
    print("=" * 78)
    print(ruta)
    print("=" * 78)
    falsadores, observaciones = [], []
    for etiqueta, prueba, severidad in PRUEBAS:
        fallos = prueba(doc, secciones, z)
        if not fallos:
            estado = "OK   "
        else:
            estado = "FALLA" if severidad == "falsador" else "AVISO"
        print("  [%s] %s" % (estado, etiqueta))
        for f in fallos:
            print("         - %s" % f)
        (falsadores if severidad == "falsador" else observaciones).extend(fallos)
    print(
        "  --> %s (%d falsadores, %d observaciones)"
        % ("APTO" if not falsadores else "NO APTO", len(falsadores), len(observaciones))
    )
    if observaciones:
        print("      Las observaciones no bloquean la entrega: se elevan al instructor.")
    print()
    return not falsadores


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    return 0 if all([verificar(a) for a in argv[1:]]) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
