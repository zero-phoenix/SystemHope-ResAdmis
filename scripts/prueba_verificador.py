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
        "R-177",
        "rotulo con guiones de markdown",
        r"CUARTO:",
        "__CUARTO__:",
    ),
    (
        "R-176",
        "credito sin enmascarar",
        r"presentar una copia",
        "presentar una copia del Crédito vehicular 53685 y",
    ),
    (
        "R-179",
        "numeral escrito pegado al texto («9.La Secretaria…»)",
        r"(?s)(<w:numPr>(?:(?!</w:p>).)*?<w:t(?:\s[^>]*)?>)",
        r"\g<1>9.",
    ),
    (
        "R-180",
        "numeral escrito sobre la numeracion automatica («1. 1. …»)",
        r"(?s)(<w:numPr>(?:(?!</w:p>).)*?<w:t(?:\s[^>]*)?>)",
        r"\g<1>1. ",
    ),
    (
        "R-181",
        "imputacion del resolutivo entera en negrita",
        r"(?s)<w:p[ >](?:(?!</w:p>).)*?<w:t[^>]*>Presunta infracci(?:(?!</w:p>).)*</w:p>",
        lambda m: m.group(0).replace("<w:rPr>", "<w:rPr><w:b/>"),
    ),
    (
        "R-164",
        "DECIMO con el parrafo entero en negrita",
        r"(?s)<w:p[ >](?:(?!</w:p>).)*?<w:t[^>]*>D\u00c9CIMO(?:(?!</w:p>).)*</w:p>",
        lambda m: m.group(0).replace("<w:rPr>", "<w:rPr><w:b/>"),
    ),
    (
        "R-174",
        "un tramo del cuerpo a 10 pt",
        r'(?s)<w:sz w:val="22"/><w:szCs w:val="22"/>((?:(?!</w:r>|<w:rPr>).)*?</w:rPr><w:t[^>]*>[^<\s])',
        r'<w:sz w:val="20"/><w:szCs w:val="20"/>\1',
    ),
    # ---- v3.1 (revision del instructor del 24/09/2026, admisorio 9999-2026) ----
    (
        "R-164",
        "PRIMERO con el parrafo entero en negrita",
        r"(?s)<w:p[ >](?:(?!</w:p>).)*?<w:t[^>]*>PRIMERO(?:(?!</w:p>).)*</w:p>",
        lambda m: m.group(0).replace("<w:rPr>", "<w:rPr><w:b/>"),
    ),
    (
        "R-183",
        "llamada borrada: su nota queda huerfana",
        r'(?s)<w:r\b(?:(?!</w:r>).)*?<w:footnoteReference[^>]*w:id="3"[^>]*/></w:r>',
        "",
    ),
    (
        "R-184",
        "nota del Codigo fuera de su ancla",
        r"(?s)Defensa del Consumidor(</w:t></w:r><w:r\b(?:(?!</w:r>).)*?<w:footnoteReference)",
        r"Defensa del Consumidor peruano\1",
    ),
    (
        "R-185",
        "dos llamadas de nota pegadas",
        r"(?s)(<w:r\b(?:(?!</w:r>).)*?<w:footnoteReference[^>]*/></w:r>)",
        r"\1\1",
    ),
    (
        "R-186",
        "la calificacion cita una norma y su nota transcribe otra",
        r"tipificado en los artículos 18 y 19 del Código",
        "tipificado en el artículo 38 del Código",
    ),
    (
        "R-187",
        "nota sin tabulacion tras la llamada",
        r"(?s)(<w:footnoteRef/>(?:(?!<w:tab/>|</w:p>).)*?)<w:tab/>",
        r"\1",
        "word/footnotes.xml",
    ),
    (
        "R-187",
        "literal h. del 115.1 sin su letra",
        r"(?s)<w:numPr>(?:(?!</w:numPr>).)*</w:numPr>((?:(?!<w:p[ >]).)*?Pagar los gastos)",
        r"\1",
        "word/footnotes.xml",
    ),
    (
        "R-187",
        "doble espacio dentro de una nota",
        r"(?s)(<w:footnoteRef/>(?:(?!</w:p>).)*?<w:t[^>]*>[^<\s]+) ",
        r"\1  x ",
        "word/footnotes.xml",
    ),
    (
        "R-188",
        "«los proveedores denunciados» y «el proveedor denunciado» a la vez",
        r"consistente en que ",
        "consistente en que el proveedor denunciado y los proveedores denunciados y ",
    ),
    (
        "R-189",
        "rotulo del requerimiento con la razon social en vez del alias",
        None,
        lambda x: re.sub(
            r"(?s)<w:p[ >](?:(?!</w:p>).)*?</w:p>",
            lambda m: re.sub(r"(<w:t[^>]*>)(Al? )", r"\1\2Empresa Ajena Inventada ", m.group(0), count=1)
            if re.match(r"\s*Al?\s+[^:]{2,60}:\s*\(i\)", re.sub(r"<[^>]+>", "", m.group(0)))
            else m.group(0),
            x,
        ),
    ),
    (
        "R-190",
        "razon social ajena al caso en el traslado",
        r"correr traslado de la presente resolución a",
        "correr traslado de la presente resolución a Empresa Ajena Inventada S.A. y a",
    ),
    (
        "R-191",
        "un parrafo de la considerativa con otra numeracion",
        None,
        lambda x: re.sub(
            r"(?s)<w:p[ >](?:(?!</w:p>).)*?</w:p>",
            lambda m: re.sub(r'(<w:numId w:val=")\d+(")', r"\g<1>97\2", m.group(0), count=1)
            if "En tanto la denuncia" in re.sub(r"<[^>]+>", "", m.group(0))
            else m.group(0),
            x,
        ),
    ),
    (
        "R-192",
        "NOVENO con una frase subrayada",
        r"(?s)<w:p[ >](?:(?!</w:p>).)*?<w:t[^>]*>NOVENO(?:(?!</w:p>).)*</w:p>",
        lambda m: m.group(0).replace("<w:rPr>", '<w:rPr><w:u w:val="single"/>', 2),
    ),
    (
        "R-193",
        "firma sin «Firmado digitalmente por»",
        r"Firmado digitalmente por",
        "",
    ),
    (
        "R-194",
        "dos lineas en blanco seguidas en el cuerpo",
        r'(?s)(<w:p\b[^>]*><w:pPr>(?:<w:pStyle\b[^>]*/>)?<w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>(?:(?!</w:p>|<w:t[ >]).)*?</w:p>)',
        r"\1\1",
    ),
    (
        "R-194b",
        "linea en blanco con el espaciado heredado (mide casi dos lineas)",
        r'<w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>',
        "",
    ),
    (
        "R-173",
        "nota del articulo 26 borrada del traslado",
        r"(?s)(Decreto Legislativo 807</w:t></w:r>)<w:r\b(?:(?!</w:r>).)*?<w:footnoteReference[^>]*/></w:r>",
        r"\1",
    ),
    (
        "R-201",
        "«aseguradora» a secas",
        r"señalando lo siguiente",
        "señalando la aseguradora lo siguiente",
    ),
    (
        "R-202",
        "la primera calificacion repetida con su nota de la norma imputada",
        None,
        lambda x: re.sub(
            r"(?s)<w:p[ >](?:(?!</w:p>).)*?considera que el hecho denunciado(?:(?!</w:p>).)*?</w:p>",
            lambda m: m.group(0) + m.group(0),
            x,
            count=1,
        ),
    ),
    ("R-203", "palabra valorativa en los hechos", r"señalando lo siguiente", "señalando únicamente lo siguiente"),
    ("R-204", "«contaba con» el seguro", r"señalando lo siguiente", "señalando que contaba con el Seguro lo siguiente"),
    (
        "R-205",
        "«la parte denunciante» en la imputacion",
        r"consistente en que ",
        "consistente en que respecto de la parte denunciante ",
    ),
    (
        "R-206",
        "dos solicitudes en una imputacion",
        r"consistente en que ",
        "consistente en que pese a sus solicitudes del 1 y el 23 de marzo de 2026 ",
    ),
    (
        "R-207",
        "informacion sin «afectación al derecho de información»",
        r"; involucraría una presunta afectación al derecho de información de los consumidores",
        "",
    ),
]
REGLAS = sorted({m[0] for m in MUTACIONES})
PARTE = "word/document.xml"


def _parte(m) -> str:
    return m[4] if len(m) > 4 else PARTE


def texto_xml(ruta: Path, parte: str = PARTE) -> str:
    with zipfile.ZipFile(ruta) as z:
        return z.read(parte).decode("utf-8", "replace")


def normalizada(p: Path, destino: Path) -> Path:
    """La plantilla tal como la entregaria el constructor: con las reglas
    generales v3.1 aplicadas (las mismas que la migracion del corpus). Asi la
    prueba no depende de que el corpus este migrado."""
    sys.path.insert(0, str(RAIZ / "scripts" / "migraciones"))
    import migrar_v3_1

    with zipfile.ZipFile(p) as z:
        items = [(i, z.read(i.filename)) for i in z.infolist()]
    datos = {i.filename: d for i, d in items}
    x = datos["word/document.xml"].decode("utf-8")
    fx = datos.get("word/footnotes.xml", b"").decode("utf-8")
    x, fx, _c = migrar_v3_1.migrar(x, fx)
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as zout:
        for info, d in items:
            if info.filename == "word/document.xml":
                d = x.encode("utf-8")
            elif info.filename == "word/footnotes.xml" and fx:
                d = fx.encode("utf-8")
            zout.writestr(info, d)
    return destino


def fallos_de(ruta: Path, regla: str) -> list[str]:
    doc, secciones, z = V.leer_documento(str(ruta))
    for nombre, fn, _tipo in V.PRUEBAS:
        if nombre.startswith(regla + " ") or nombre.startswith(regla + "  "):
            return fn(doc, secciones, z)
    raise KeyError(regla)


def _aplica(m, ruta: Path, cache: dict) -> bool:
    clave = (ruta, _parte(m))
    if clave not in cache:
        cache[clave] = texto_xml(ruta, _parte(m))
    t = cache[clave]
    return (m[3](t) != t) if m[2] is None else bool(re.search(m[2], t))


def bases(tmp: Path):
    """Plantillas normalizadas v3.1, en orden estable y bajo demanda."""
    for k, p in enumerate(sorted((RAIZ / "plantillas_maestras").rglob("*.docx"))):
        yield p, normalizada(p, tmp / ("base_%03d.docx" % k))


def elegir_base(m, tmp: Path, hechas: list, cache: dict):
    """Primera plantilla donde la mutacion se puede introducir y cuya regla
    PASA antes de mutar: si no pasara, rechazar el mutante no probaria nada."""
    for p, n in hechas:
        if _aplica(m, n, cache) and not fallos_de(n, m[0]):
            return p, n
    for p, n in BASES:
        hechas.append((p, n))
        if _aplica(m, n, cache) and not fallos_de(n, m[0]):
            return p, n
    return None, None


def mutar(base: Path, patron: str, sustituto, destino: Path, parte: str = PARTE) -> bool:
    with zipfile.ZipFile(base) as z:
        items = [(i, z.read(i.filename)) for i in z.infolist()]
    hecho = False
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as zout:
        for info, datos in items:
            if info.filename == parte:
                xml = datos.decode("utf-8")
                if patron is None:
                    nuevo = sustituto(xml)
                    hecho = nuevo != xml
                else:
                    nuevo, n = re.subn(patron, sustituto, xml, count=1)
                    hecho = n > 0
                datos = nuevo.encode("utf-8")
            zout.writestr(info, datos)
    return hecho


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="prueba_ver_"))
    global BASES
    BASES = bases(tmp)
    hechas: list = []
    cache: dict = {}
    malas = 0
    for i, m in enumerate(MUTACIONES):
        regla, que, patron, sustituto = m[:4]
        origen, base = elegir_base(m, tmp, hechas, cache)
        if base is None:
            print("  FALLA  %-6s %s: ninguna plantilla sirve de base (la regla falla en todas o el error no se puede introducir)" % (regla, que))
            malas += 1
            continue
        destino = tmp / ("mutante_%02d.docx" % i)
        if not mutar(base, patron, sustituto, destino, _parte(m)):
            print("  FALLA  %-6s %s: la mutacion no se pudo aplicar" % (regla, que))
            malas += 1
            continue
        if fallos_de(destino, regla):
            print("  OK     %-6s rechaza: %s  [%s]" % (regla, que, origen.name[:22]))
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
