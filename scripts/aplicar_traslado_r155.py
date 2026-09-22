#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Normalizador masivo de la fórmula de traslado y descargos (R-155).

Sustituye las fórmulas derogadas de traslado en todas las plantillas maestras y
modelos del repositorio por la nueva fórmula canónica obligatoria (R-155).

Uso:
    python scripts/aplicar_traslado_r155.py [--aplicar]
"""

from __future__ import annotations

import argparse
import io
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ET.register_namespace("w", W_NS)

FORMULA_1_DDO = (
    "correr traslado de la presente resolución a {denunciado} para que, de "
    "conformidad con lo dispuesto por el artículo 26° de la Ley sobre Facultades, "
    "Normas y Organización del Indecopi, aprobado por Decreto Legislativo N° 8079, "
    "presente sus descargos sobre la imputación de cargos realizada en un plazo no mayor "
    "a cinco (5) días hábiles contado a partir del día siguiente de la notificación "
    "de la presente resolución, vencido el cual, el Secretario Técnico declarará en "
    "rebeldía a los denunciados que no lo hubieran presentado. Debe precisarse que de "
    "conformidad con lo establecido por el artículo 223° del Texto Único Ordenado de "
    "la Ley N° 27444, Ley del Procedimiento Administrativo General, las alegaciones y "
    "los hechos relevantes de la reclamación, salvo que hayan sido específicamente "
    "negadas en la contestación, se tendrán por aceptadas o meritadas como ciertas."
)

FORMULA_2_DDOS = (
    "correr traslado de la presente resolución a {denunciado} para que, de "
    "conformidad con lo dispuesto por el artículo 26° de la Ley sobre Facultades, "
    "Normas y Organización del Indecopi, aprobado por Decreto Legislativo N° 8079, "
    "presenten sus descargos sobre la imputación de cargos realizada en un plazo no mayor "
    "a cinco (5) días hábiles contado a partir del día siguiente de la notificación "
    "de la presente resolución, vencido el cual, el Secretario Técnico declarará en "
    "rebeldía a los denunciados que no lo hubieran presentado. Debe precisarse que de "
    "conformidad con lo establecido por el artículo 223° del Texto Único Ordenado de "
    "la Ley N° 27444, Ley del Procedimiento Administrativo General, las alegaciones y "
    "los hechos relevantes de la reclamación, salvo que hayan sido específicamente "
    "negadas en la contestación, se tendrán por aceptadas o meritadas como ciertas."
)


def extraer_datos_traslado(texto: str, ruta: Path):
    """Extrae el ordinal, el/los denunciados y si es plural del párrafo de traslado."""
    m_ord = re.match(r"^\s*([A-ZÁÉÍÓÚ]+:)", texto)
    ordinal = m_ord.group(1) if m_ord else "CUARTO:"
    body = texto[len(ordinal):].strip() if m_ord else texto.strip()

    # Determinar pluralidad por taxonomía de carpetas o por verbo original
    ruta_str = str(ruta).lower()
    if any(p in ruta_str for p in ["1_ddo", "modelo_1_ddo", "plantilla_base_2026"]):
        es_plural = False
    elif any(p in ruta_str for p in ["2_ddo", "2_o_mas", "modelo_2_ddo"]):
        es_plural = True
    else:
        # Fallback para archivos sueltos
        if "presenten" in body.lower():
            es_plural = True
        elif "presente" in body.lower():
            es_plural = False
        else:
            den_sin_seguros = re.sub(r"seguros\s+y\s+reaseguros", "", body, flags=re.IGNORECASE)
            es_plural = bool(re.search(r"\s+[ye]\s+|,", den_sin_seguros, re.IGNORECASE))

    # Delimitar hasta 'para que' o 'Ello, para que'
    m_end = re.search(r",?\s*(?:ello,?\s*)?para que\b", body, re.IGNORECASE)
    if m_end:
        pre = body[:m_end.start()].strip()
    else:
        pre = body

    # Limpiar cláusulas de confidencialidad o excepciones
    pre = re.sub(r",?\s*con excepci[oó]n.*$", "", pre, flags=re.IGNORECASE).strip()
    pre = pre.rstrip(".,; ")

    # Buscar segmento de denunciados
    m = re.search(
        r"(?:interpuest[oa]s?\s+(?:en\s+contra\s+de|contra)|contra|(?:(?<=\s)a(?=\s))|(?<=[,\.])\s*a\s+|al\s+)\s*(.+)$",
        pre,
        re.IGNORECASE,
    )
    if m:
        den = m.group(1).strip()
    else:
        m2 = re.search(
            r"(?:,\s*|\d{4}\s+)([A-ZÁÉÍÓÚ][^,]+(?:(?:,\s*|\s+[ye]\s+)[A-ZÁÉÍÓÚ][^,]+)*)$",
            pre,
        )
        if m2:
            den = m2.group(1).strip()
        else:
            den = pre

    # Limpieza final de partículas iniciales o finales
    den = re.sub(r"^(?:a\s+|al\s+)", "", den, flags=re.IGNORECASE).strip("., ")
    if not den:
        den = "[DENUNCIADO]"

    return ordinal, den, es_plural


def construir_parrafo_xml(ordinal: str, den: str, es_plural: bool, p_orig: ET.Element) -> ET.Element:
    """Construye un nuevo elemento <w:p> con la fórmula R-155 y formato estricto."""
    formula = FORMULA_2_DDOS if es_plural else FORMULA_1_DDO
    cuerpo = formula.format(denunciado=den)

    nuevo_p = ET.Element(f"{{{W_NS}}}p")

    # Preservar o generar pPr institucional
    pPr_orig = p_orig.find(f"{{{W_NS}}}pPr")
    if pPr_orig is not None:
        nuevo_pPr = ET.fromstring(ET.tostring(pPr_orig))
        jc = nuevo_pPr.find(f"{{{W_NS}}}jc")
        if jc is None:
            jc = ET.SubElement(nuevo_pPr, f"{{{W_NS}}}jc")
        jc.set(f"{{{W_NS}}}val", "both")
        sp = nuevo_pPr.find(f"{{{W_NS}}}spacing")
        if sp is None:
            sp = ET.SubElement(nuevo_pPr, f"{{{W_NS}}}spacing")
        sp.set(f"{{{W_NS}}}line", "240")
        sp.set(f"{{{W_NS}}}lineRule", "auto")
        # Eliminar cualquier highlight
        for hl in list(nuevo_pPr.iter(f"{{{W_NS}}}highlight")):
            nuevo_pPr.remove(hl)
        nuevo_p.append(nuevo_pPr)
    else:
        nuevo_pPr = ET.SubElement(nuevo_p, f"{{{W_NS}}}pPr")
        pStyle = ET.SubElement(nuevo_pPr, f"{{{W_NS}}}pStyle")
        pStyle.set(f"{{{W_NS}}}val", "Parrafodelista")
        ind = ET.SubElement(nuevo_pPr, f"{{{W_NS}}}ind")
        ind.set(f"{{{W_NS}}}left", "567")
        ind.set(f"{{{W_NS}}}hanging", "567")
        jc = ET.SubElement(nuevo_pPr, f"{{{W_NS}}}jc")
        jc.set(f"{{{W_NS}}}val", "both")
        sp = ET.SubElement(nuevo_pPr, f"{{{W_NS}}}spacing")
        sp.set(f"{{{W_NS}}}line", "240")
        sp.set(f"{{{W_NS}}}lineRule", "auto")

    # Run 1: Ordinal con negrita institucional
    r1 = ET.SubElement(nuevo_p, f"{{{W_NS}}}r")
    rPr1 = ET.SubElement(r1, f"{{{W_NS}}}rPr")
    rFonts1 = ET.SubElement(rPr1, f"{{{W_NS}}}rFonts")
    rFonts1.set(f"{{{W_NS}}}ascii", "Arial Narrow")
    rFonts1.set(f"{{{W_NS}}}hAnsi", "Arial Narrow")
    rFonts1.set(f"{{{W_NS}}}cs", "Arial Narrow")
    b1 = ET.SubElement(rPr1, f"{{{W_NS}}}b")
    b1.set(f"{{{W_NS}}}val", "1")
    bCs1 = ET.SubElement(rPr1, f"{{{W_NS}}}bCs")
    bCs1.set(f"{{{W_NS}}}val", "1")
    sz1 = ET.SubElement(rPr1, f"{{{W_NS}}}sz")
    sz1.set(f"{{{W_NS}}}val", "20")
    szCs1 = ET.SubElement(rPr1, f"{{{W_NS}}}szCs")
    szCs1.set(f"{{{W_NS}}}val", "20")

    t1 = ET.SubElement(r1, f"{{{W_NS}}}t")
    t1.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t1.text = f"{ordinal} "

    # Run 2: Cuerpo de la fórmula
    r2 = ET.SubElement(nuevo_p, f"{{{W_NS}}}r")
    rPr2 = ET.SubElement(r2, f"{{{W_NS}}}rPr")
    rFonts2 = ET.SubElement(rPr2, f"{{{W_NS}}}rFonts")
    rFonts2.set(f"{{{W_NS}}}ascii", "Arial Narrow")
    rFonts2.set(f"{{{W_NS}}}hAnsi", "Arial Narrow")
    rFonts2.set(f"{{{W_NS}}}cs", "Arial Narrow")
    sz2 = ET.SubElement(rPr2, f"{{{W_NS}}}sz")
    sz2.set(f"{{{W_NS}}}val", "20")
    szCs2 = ET.SubElement(rPr2, f"{{{W_NS}}}szCs")
    szCs2.set(f"{{{W_NS}}}val", "20")

    t2 = ET.SubElement(r2, f"{{{W_NS}}}t")
    t2.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t2.text = cuerpo

    return nuevo_p


def procesar_documento(ruta: Path, aplicar: bool = False) -> tuple[bool, str]:
    """Procesa un archivo .docx para aplicar R-155."""
    long_path = f"\\\\?\\{ruta.resolve()}"
    try:
        with zipfile.ZipFile(long_path, "r") as z_in:
            namelist = z_in.namelist()
            if "word/document.xml" not in namelist:
                return False, "sin word/document.xml"

            xml_content = z_in.read("word/document.xml")
            tree = ET.fromstring(xml_content)

            body_elem = tree.find(f"{{{W_NS}}}body")
            if body_elem is None:
                return False, "sin w:body"

            parrafo_traslado = None
            indice_traslado = -1

            for idx, p in enumerate(list(body_elem)):
                if p.tag == f"{{{W_NS}}}p":
                    t = "".join(p.itertext())
                    if "correr traslado" in t.lower():
                        parrafo_traslado = p
                        indice_traslado = idx
                        break

            if parrafo_traslado is None:
                return False, "no contiene correr traslado"

            texto_original = "".join(parrafo_traslado.itertext())
            ordinal, den, es_plural = extraer_datos_traslado(texto_original, ruta)

            nuevo_p = construir_parrafo_xml(ordinal, den, es_plural, parrafo_traslado)

            if aplicar:
                body_elem[indice_traslado] = nuevo_p

                buffer = io.BytesIO()
                with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z_out:
                    for item in z_in.infolist():
                        if item.filename == "word/document.xml":
                            nuevo_xml = ET.tostring(tree, encoding="utf-8", xml_declaration=True)
                            z_out.writestr(item, nuevo_xml)
                        else:
                            z_out.writestr(item, z_in.read(item.filename))

                buffer.seek(0)
                with open(long_path, "wb") as f_out:
                    f_out.write(buffer.read())

            return True, f"{ordinal} {den} ({'plural' if es_plural else 'singular'})"
    except Exception as e:
        return False, f"ERROR: {e}"


def main():
    parser = argparse.ArgumentParser(description="Aplica la fórmula obligatoria R-155")
    parser.add_argument("--aplicar", action="store_true", help="Modificar los archivos .docx")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent

    docx_files = [
        p
        for p in repo_root.rglob("*.docx")
        if not p.name.startswith("~$")
        and ("plantillas_maestras" in p.parts or "modelos" in p.parts)
    ]

    print(f"=== NORMALIZADOR R-155 (Modo: {'APLICAR' if args.aplicar else 'DRY-RUN'}) ===")
    print(f"Total plantillas encontradas: {len(docx_files)}")

    actualizados = 0
    omitidos = 0
    singulares = 0
    plurales = 0
    errores = []

    for p in sorted(docx_files):
        ok, detalle = procesar_documento(p, aplicar=args.aplicar)
        if ok:
            actualizados += 1
            if "(singular)" in detalle:
                singulares += 1
            else:
                plurales += 1
        else:
            if "no contiene correr traslado" in detalle:
                omitidos += 1
            else:
                errores.append((p.name, detalle))

    print(f"\nResultados:")
    print(f"  Procesados con R-155: {actualizados} (Singulares: {singulares}, Plurales: {plurales})")
    print(f"  Omitidos (sin traslado): {omitidos}")
    print(f"  Errores: {len(errores)}")

    if errores:
        print("\nDetalle de errores:")
        for name, err in errores[:10]:
            print(f"  - {name}: {err}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
