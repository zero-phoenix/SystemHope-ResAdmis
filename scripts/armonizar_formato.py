#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Armoniza el formato visual de los .docx de una carpeta al estilo CC1.

Solo toca atributos de formato: fuente, cuerpo, interlineado, espaciado,
alineacion y margenes. El texto (<w:t>) no se altera; se verifica por
comparacion antes/despues de cada parte del paquete.

Estilo aplicado (modelos plantillas_maestras + AGENTS.md parrafo 5):
  - Fuente unica: Arial Narrow en cada run explicito (ascii/hAnsi/cs).
  - Cuerpo: 11 pt (sz 22) en document.xml; notas y encabezados/pies: 8 pt (16).
  - Parrafo: interlineado sencillo (240 auto), espaciado 0 pt antes/despues.
  - Alineacion: justificado (both), salvo parrafos centrados (se conservan).
  - Pagina: A4 (11906x16838), margenes top 1417, bottom 1417, left 1701,
    right 1701, header 708, footer 708 (los del modelo TPL_266_2026).

Uso:
    python scripts/armonizar_formato.py <carpeta> [--respaldo NOMBRE]

Escribe los armonizados con el mismo nombre y guarda los originales en
<carpeta>/<respaldo> (por defecto _originales_sin_armonizar).
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import zipfile
from pathlib import Path

FUENTE = "Arial Narrow"
SZ_CUERPO = "22"   # 11 pt
SZ_NOTA = "16"     # 8 pt
SPACING = '<w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>'
RFONTS = '<w:rFonts w:ascii="%s" w:hAnsi="%s" w:cs="Arial Narrow"/>' % (FUENTE, FUENTE)
RFONTS_RE = re.compile(r"<w:rFonts[^/]*/>")
RPR_ABRE = re.compile(r"(<w:rPr(?:\s[^>]*)?>)")
PGMAR = ('<w:pgMar w:top="1417" w:right="1701" w:bottom="1417" w:left="1701" '
         'w:header="708" w:footer="708" w:gutter="0"/>')
PGSZ = '<w:pgSz w:w="11906" w:h="16838"/>'


def textos_de(xml: str) -> list[str]:
    return re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml)


def fijar_fuente_y_tamano(xml: str, sz: str) -> str:
    """Quita rFonts heredados, fija Arial Narrow en cada rPr y unifica el cuerpo."""
    xml = RFONTS_RE.sub("", xml)
    rpr_sizes = re.compile(r'(<w:rPr(?:\s[^>]*)?>)(<w:rStyle[^/]*/>)?')

    def _rpr(m: re.Match) -> str:
        bloque = m.group(0)
        if "<w:rFonts" in bloque and "<w:sz " in bloque:
            return bloque
        extras = RFONTS + ('<w:sz w:val="%s"/><w:szCs w:val="%s"/>' % (sz, sz))
        rstyle = re.search(r"<w:rStyle[^/]*/>", bloque)
        if rstyle:
            fin = rstyle.end()
            return bloque[:fin] + extras + bloque[fin:]
        return bloque + extras

    xml = rpr_sizes.sub(_rpr, xml)
    xml = re.sub(r'<w:sz w:val="\d+"/>', '<w:sz w:val="%s"/>' % sz, xml)
    xml = re.sub(r'<w:szCs w:val="\d+"/>', '<w:szCs w:val="%s"/>' % sz, xml)
    return xml


def armonizar_parrafos(xml: str) -> str:
    """Interlineado 0/0/240 y alineacion both (conserva center) por parrafo."""
    salida = []
    fin = 0
    for m in re.finditer(r"<w:p[ >].*?</w:p>", xml, re.S):
        p = m.group(0)
        Centro = '<w:jc w:val="center"/>' in p
        nuevo = re.sub(r"<w:spacing[^/]*/>", "", p, count=0)
        nuevo = re.sub(r"<w:jc[^/]*/>", "", nuevo)
        if "<w:pPr" in nuevo:
            pm = re.search(r"<w:pPr(?:[^>]*)>", nuevo)
            inner_inicio = pm.end()
            # punto de insercion: antes de ind, jc ya removida, rPr o sectPr o cierre
            candidatos = [
                nuevo.find("<w:ind", inner_inicio),
                nuevo.find("<w:rPr", inner_inicio),
                nuevo.find("<w:sectPr", inner_inicio),
                nuevo.find("</w:pPr>", inner_inicio),
            ]
            validos = [x for x in candidatos if x != -1]
            pos = min(validos) if validos else nuevo.find("</w:pPr>", inner_inicio)
            bloque = SPACING + ("" if Centro else '<w:jc w:val="both"/>')
            if Centro:
                bloque = SPACING + '<w:jc w:val="center"/>'
            nuevo = nuevo[:pos] + bloque + nuevo[pos:]
        else:
            pm = re.search(r"<w:p(?:[^>]*)>", nuevo)
            fin_tag = pm.end()
            bloque = ('<w:pPr>' + SPACING +
                      ('<w:jc w:val="center"/>' if Centro else '<w:jc w:val="both"/>') +
                      '</w:pPr>')
            nuevo = nuevo[:fin_tag] + bloque + nuevo[fin_tag:]
        salida.append(xml[fin:m.start()])
        salida.append(nuevo)
        fin = m.end()
    salida.append(xml[fin:])
    return "".join(salida)


def armonizar_secciones(xml: str) -> str:
    xml = re.sub(r"<w:pgMar[^/]*/>", PGMAR, xml)
    xml = re.sub(r"<w:pgSz[^/]*/>", PGSZ, xml)
    return xml


def armonizar_styles(xml: str) -> str:
    # docDefaults: Arial Narrow + 11 pt + interlineado sencillo
    xml = re.sub(
        r'(<w:rPrDefault><w:rPr>)<w:rFonts[^/]*/>',
        r'\1<w:rFonts w:ascii="%s" w:hAnsi="%s" w:cs="%s" w:eastAsia="%s"/>' % (FUENTE, FUENTE, FUENTE, FUENTE),
        xml,
    )
    # rFonts y tamanos sueltos en estilos: fuera, heredan de docDefaults
    xml = RFONTS_RE.sub("", xml)
    return xml


def procesar(ruta: Path, respaldo: Path) -> tuple[bool, str]:
    respaldo.mkdir(parents=True, exist_ok=True)
    destino_respaldo = respaldo / ruta.name
    if not destino_respaldo.exists():
        shutil.copy2(ruta, destino_respaldo)

    with zipfile.ZipFile(destino_respaldo) as z:
        entradas = {n: z.read(n) for n in z.namelist()}

    originales = {}
    transformadas = {}
    for nombre, data in entradas.items():
        if not re.match(r"word/(document|footnotes|header\d*|footer\d*)\.xml$", nombre):
            continue
        xml = data.decode("utf-8")
        originales[nombre] = textos_de(xml)
        if nombre == "word/document.xml":
            xml = fijar_fuente_y_tamano(xml, SZ_CUERPO)
            xml = armonizar_parrafos(xml)
            xml = armonizar_secciones(xml)
        elif nombre == "word/footnotes.xml":
            xml = fijar_fuente_y_tamano(xml, SZ_NOTA)
            xml = armonizar_parrafos(xml)
        else:  # headers y pies: solo fuente y cuerpo (posicion institucional intacta)
            xml = fijar_fuente_y_tamano(xml, SZ_NOTA)
        if textos_de(xml) != originales[nombre]:
            return False, "TEXTO ALTERADO en %s — se aborta" % nombre
        transformadas[nombre] = xml.encode("utf-8")

    if "word/styles.xml" in entradas:
        st = entradas["word/styles.xml"].decode("utf-8")
        st = armonizar_styles(st)
        transformadas["word/styles.xml"] = st.encode("utf-8")

    salida = dict(entradas)
    salida.update(transformadas)
    tmp = ruta.with_suffix(".tmp_docx")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for nombre, data in salida.items():
            z.writestr(nombre, data)
    tmp.replace(ruta)
    return True, "OK (%d partes de texto verificadas identicas)" % len(originales)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("carpeta")
    ap.add_argument("--respaldo", default="_originales_sin_armonizar")
    args = ap.parse_args()
    carpeta = Path(args.carpeta)
    respaldo = carpeta / args.respaldo
    fallas = 0
    for ruta in sorted(carpeta.glob("*.docx")):
        ok, msg = procesar(ruta, respaldo)
        print("%-40s %s" % (ruta.name, msg if ok else "FALLA: " + msg))
        fallas += 0 if ok else 1
    return 1 if fallas else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
