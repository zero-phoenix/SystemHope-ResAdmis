#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprueba que el verificador rechaza lo que debe rechazar (mutaciones).

Una regla que nunca falla no es una regla que se cumple: es una regla que no se
esta ejecutando. R-110 estuvo exactamente asi --sus cinco patrones tenian un
caracter de retroceso donde debia ir un limite de palabra-- declarando `OK` sobre
todos los documentos sin comprobar nada, hasta que se leyeron sus bytes.

Se toma una plantilla que pasa las reglas probadas y, por cada regla, se le
introduce UN error a proposito. Cada mutacion debe ser rechazada por SU regla.
Si una sola sobrevive, el verificador miente y CI se detiene.

Uso:
    python scripts/prueba_verificador.py
"""

from __future__ import annotations

import re
import sys
import tempfile
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import verificar_admisorio as V  # noqa: E402

# (regla que debe caer, descripcion, patron a buscar en document.xml, reemplazo:
# texto con referencias o funcion sobre el match)
MUTACIONES = [
    ("R-103", "firma cambiada", r"EVELING ROA QUISPE", "QUIEN SEA"),
    (
        "R-155",
        "errata 8079",
        # El del traslado: tras «807» va la llamada de su nota (R-173).
        r"(?s)(aprobada por Decreto Legislativo )807(</w:t></w:r><w:r\b(?:(?!</w:r>).)*?<w:footnoteReference)",
        r"\1N° 8079\2",
    ),
    ("R-155", "errata meritadas", r"merituadas", "meritadas"),
    (
        "R-155",
        "plural con un solo denunciado",
        r"presente sus descargos",
        "presenten sus descargos",
    ),
    (
        "R-155",
        "rebeldia en plural con un solo denunciado",
        r"al denunciado que no lo hubiera presentado",
        "a los denunciados que no lo hubieran presentado",
    ),
    ("R-156", "N° ante una ley", r"Ley 29571", "Ley N° 29571"),
    (
        "R-157",
        "denunciante en los hechos",
        r"señalando lo siguiente",
        "señalando el denunciante lo siguiente",
    ),
    (
        "R-158",
        "poliza enmascarada",
        r"(Póliza )(\d{3})(\d{3,})",
        r"\g<1>\g<2>****\g<3>",
    ),
    ("R-156", "Nro. ante un numero", r"Ley 29571", "Ley Nro. 29571"),
    ("R-163", "ordinal saltado", r"CUARTO:", "QUINTO:"),
    ("R-161", "fecha con 'del'", r"(\d{1,2} de [a-z]+) de (20\d\d)", r"\1 del \2"),
    (
        "R-143",
        "clausula abusiva sin el numeral 49.1",
        r"Presunta infracción a los artículos 18 y 19",
        "Presunta infracción al literal a) del artículo 50",
    ),
    (
        "R-143",
        "imputacion por el articulo 3",
        r"Presunta infracción a los artículos 18 y 19",
        "Presunta infracción al artículo 3",
    ),
    (
        "R-168",
        "espacio de nombres w14 sin declarar (Word: contenido no legible)",
        r'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"',
        "",
    ),
    (
        "R-169",
        "varios reclamos en una imputacion por 88.1",
        r"(?s)(Presunta infracción al numeral 88\.1(?:(?!</w:p>).)*?)\breclamo\b",
        r"\1reclamos",
    ),
    (
        "R-170",
        "parrafo del traslado subrayado entero",
        r"(?s)<w:p\b(?:(?!</w:p>).)*?correr traslado.*?</w:p>",
        lambda m: m.group(0).replace("<w:rPr>", '<w:rPr><w:u w:val="single"/>'),
    ),
    (
        "R-171",
        "encabezado DENUNCIANTE: descuadrado",
        r"<w:t>(DENUNCIANTES?)</w:t><w:tab/><w:t>:</w:t>",
        r"<w:t>\1:</w:t><w:tab/><w:t></w:t>",
    ),
    (
        "R-173",
        "nota del articulo 26 borrada del traslado",
        r"(?s)(Decreto Legislativo 807</w:t></w:r>)<w:r\b(?:(?!</w:r>).)*?<w:footnoteReference[^>]*/></w:r>",
        r"\1",
    ),
]
REGLAS = sorted({m[0] for m in MUTACIONES})


def texto_xml(ruta: Path) -> str:
    with zipfile.ZipFile(ruta) as z:
        return z.read("word/document.xml").decode("utf-8", "replace")


def fallos_de(ruta: Path, regla: str) -> list[str]:
    doc, secciones, z = V.leer_documento(str(ruta))
    for nombre, fn, _tipo in V.PRUEBAS:
        if nombre.startswith(regla + " ") or nombre.startswith(regla + "  "):
            return fn(doc, secciones, z)
    raise KeyError(regla)


def elegir_base() -> Path | None:
    for p in sorted((RAIZ / "plantillas_maestras").rglob("*")):
        if p.suffix.lower() != ".docx":
            continue
        xml = texto_xml(p)
        if not all(re.search(pat, xml) for _r, _d, pat, _s in MUTACIONES):
            continue
        if any(fallos_de(p, r) for r in REGLAS):
            continue
        return p
    return None


def mutar(base: Path, patron: str, sustituto: str, destino: Path) -> bool:
    with zipfile.ZipFile(base) as z:
        items = [(i, z.read(i.filename)) for i in z.infolist()]
    hecho = False
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as zout:
        for info, datos in items:
            if info.filename == "word/document.xml":
                xml = datos.decode("utf-8")
                nuevo, n = re.subn(patron, sustituto, xml, count=1)
                hecho = n > 0
                datos = nuevo.encode("utf-8")
            zout.writestr(info, datos)
    return hecho


def main() -> int:
    base = elegir_base()
    if base is None:
        print("  FALLA  ninguna plantilla sirve de base limpia para las mutaciones.")
        return 1
    print("Base: %s" % base.name)
    tmp = Path(tempfile.mkdtemp(prefix="prueba_ver_"))
    malas = 0
    for i, (regla, que, patron, sustituto) in enumerate(MUTACIONES):
        destino = tmp / ("mutante_%02d.docx" % i)
        if not mutar(base, patron, sustituto, destino):
            print("  FALLA  %-6s %s: la mutacion no se pudo aplicar" % (regla, que))
            malas += 1
            continue
        if fallos_de(destino, regla):
            print("  OK     %-6s rechaza: %s" % (regla, que))
        else:
            print("  FALLA  %-6s APRUEBA un documento con: %s" % (regla, que))
            malas += 1
    print()
    if malas:
        print("  %d mutacion(es) sobreviven: el verificador no distingue." % malas)
        return 1
    print("  El verificador rechaza las %d mutaciones." % len(MUTACIONES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
