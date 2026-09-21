#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Normalizador Popperiano de Formato y Diseno para Plantillas del Corpus CC1.

Aplica de forma sistematica y determinista las invariantes formales del corpus:
1. Purga total de etiquetas <w:highlight> (R-154).
2. Calibracion de llamadas de nota al pie en document.xml con vertAlign='superscript' y estilo Refdenotaalpie (R-153).
3. Calibracion de referencias de nota al pie en footnotes.xml con vertAlign='superscript', Refdenotaalpie y tamano 8 pt (16 medias puntas) (R-153).
4. Aseguramiento de estilos Refdenotaalpie y FootnoteReference en styles.xml con vertAlign='superscript'.
5. Normalizacion de margenes institucionales (3,0 cm izq/der, 2,5 cm sup/inf = 1701/1701/1417/1417) (R-144).
6. Normalizacion de tipografia en ascii/hAnsi a Arial Narrow (R-144).
7. Normalizacion de interlineado sencillo (line="240") (R-144).

NUNCA modifica el contenido sustantivo o fondo juridico de las plantillas.

Uso:
    python scripts/normalizar_plantillas_popperianas.py [--aplicar]
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def to_long_path(p: Path) -> str:
    s = str(p.resolve())
    if sys.platform == "win32" and not s.startswith("\\\\?\\"):
        return "\\\\?\\" + s
    return s


def normalize_xml_document(xml: str) -> tuple[str, dict[str, int]]:
    stats = {"highlights": 0, "fn_refs": 0, "margins": 0, "spacing": 0, "fonts": 0}

    # 1. Highlights
    hl_count = len(re.findall(r'<w:highlight\b', xml))
    if hl_count:
        stats["highlights"] += hl_count
        xml = re.sub(r'<w:highlight\b[^>]*/>', '', xml)
        xml = re.sub(r'<w:highlight\b[^>]*>.*?</w:highlight>', '', xml, flags=re.S)

    # 2. Footnote references in document.xml
    def repl_fn(m):
        run = m.group(0)
        changed = False
        if '<w:rPr' not in run:
            m_open = re.match(r'(<w:r\b[^>]*>)', run)
            if m_open:
                stats["fn_refs"] += 1
                return run[:m_open.end()] + '<w:rPr><w:rStyle w:val="Refdenotaalpie"/><w:vertAlign w:val="superscript"/></w:rPr>' + run[m_open.end():]
        if re.search(r'<w:rPr\s*/>', run):
            stats["fn_refs"] += 1
            return re.sub(r'<w:rPr\s*/>', '<w:rPr><w:rStyle w:val="Refdenotaalpie"/><w:vertAlign w:val="superscript"/></w:rPr>', run)
        rpr_match = re.search(r'(<w:rPr\b[^>]*>)(.*?)(</w:rPr>)', run, re.S)
        if rpr_match:
            open_tag, inside, close_tag = rpr_match.groups()
            if '<w:rStyle' in inside:
                if 'w:val="Refdenotaalpie"' not in inside:
                    inside = re.sub(r'<w:rStyle\b[^>]*/>', '<w:rStyle w:val="Refdenotaalpie"/>', inside)
                    changed = True
            else:
                inside = '<w:rStyle w:val="Refdenotaalpie"/>' + inside
                changed = True
            if '<w:vertAlign' in inside:
                if 'w:val="superscript"' not in inside:
                    inside = re.sub(r'<w:vertAlign\b[^>]*/>', '<w:vertAlign w:val="superscript"/>', inside)
                    changed = True
            else:
                inside = inside + '<w:vertAlign w:val="superscript"/>'
                changed = True
            if changed:
                stats["fn_refs"] += 1
            return run[:rpr_match.start()] + open_tag + inside + close_tag + run[rpr_match.end():]
        return run

    xml = re.sub(r'<w:r\b[^>]*>(?:(?!</w:r>).)*?<w:footnoteReference\b[^>]*>(?:(?!</w:r>).)*?</w:r>', repl_fn, xml, flags=re.S)

    # 3. Margins
    def repl_mar(m):
        tag = m.group(0)
        changed = False
        for attr, val in [("w:top", "1417"), ("w:bottom", "1417"), ("w:left", "1701"), ("w:right", "1701")]:
            if f'{attr}=' in tag:
                cur_val = re.search(f'{attr}="([^"]*)"', tag)
                if cur_val and cur_val.group(1) not in (val, "1418"):
                    tag = re.sub(f'{attr}="[^"]*"', f'{attr}="{val}"', tag)
                    changed = True
            else:
                tag = tag[:-2] + f' {attr}="{val}"/>'
                changed = True
        if changed:
            stats["margins"] += 1
        return tag
    xml = re.sub(r'<w:pgMar\b[^>]*/>', repl_mar, xml)

    # 4. Spacing
    sp_count = len(re.findall(r'<w:spacing\b[^>]*w:line="276"', xml))
    if sp_count:
        stats["spacing"] += sp_count
        xml = re.sub(r'(<w:spacing\b[^>]*w:line=")276(")', r'\g<1>240\g<2>', xml)

    # 5. Fonts (only ascii / hAnsi)
    def repl_font(m):
        tag = m.group(0)
        orig = tag
        tag = re.sub(r'(w:(?:ascii|hAnsi)=)"Arial"', r'\1"Arial Narrow"', tag)
        tag = re.sub(r'(w:(?:ascii|hAnsi)=)"Times New Roman"', r'\1"Arial Narrow"', tag)
        tag = re.sub(r'(w:(?:ascii|hAnsi)=)"Calibri"', r'\1"Arial Narrow"', tag)
        tag = re.sub(r'(w:(?:ascii|hAnsi)=)"Aptos"', r'\1"Arial Narrow"', tag)
        tag = re.sub(r'(w:(?:ascii|hAnsi)=)"Segoe UI"(?! Symbol)', r'\1"Arial Narrow"', tag)
        tag = re.sub(r'(w:(?:ascii|hAnsi)=)"Cambria Math"', r'\1"Arial Narrow"', tag)
        if tag != orig:
            stats["fonts"] += 1
        return tag
    xml = re.sub(r'<w:rFonts\b[^>]*/>', repl_font, xml)

    return xml, stats


def normalize_xml_footnotes(xml: str) -> tuple[str, dict[str, int]]:
    stats = {"highlights": 0, "fn_notes": 0, "fonts": 0}

    # 1. Highlights
    hl_count = len(re.findall(r'<w:highlight\b', xml))
    if hl_count:
        stats["highlights"] += hl_count
        xml = re.sub(r'<w:highlight\b[^>]*/>', '', xml)
        xml = re.sub(r'<w:highlight\b[^>]*>.*?</w:highlight>', '', xml, flags=re.S)

    # 2. FootnoteRef
    def repl_fnref(m):
        run = m.group(0)
        changed = False
        if '<w:rPr' not in run:
            m_open = re.match(r'(<w:r\b[^>]*>)', run)
            if m_open:
                stats["fn_notes"] += 1
                return run[:m_open.end()] + '<w:rPr><w:rStyle w:val="Refdenotaalpie"/><w:vertAlign w:val="superscript"/><w:sz w:val="16"/></w:rPr>' + run[m_open.end():]
        if re.search(r'<w:rPr\s*/>', run):
            stats["fn_notes"] += 1
            return re.sub(r'<w:rPr\s*/>', '<w:rPr><w:rStyle w:val="Refdenotaalpie"/><w:vertAlign w:val="superscript"/><w:sz w:val="16"/></w:rPr>', run)
        rpr_match = re.search(r'(<w:rPr\b[^>]*>)(.*?)(</w:rPr>)', run, re.S)
        if rpr_match:
            open_tag, inside, close_tag = rpr_match.groups()
            if '<w:rStyle' in inside:
                if 'w:val="Refdenotaalpie"' not in inside:
                    inside = re.sub(r'<w:rStyle\b[^>]*/>', '<w:rStyle w:val="Refdenotaalpie"/>', inside)
                    changed = True
            else:
                inside = '<w:rStyle w:val="Refdenotaalpie"/>' + inside
                changed = True
            if '<w:vertAlign' in inside:
                if 'w:val="superscript"' not in inside:
                    inside = re.sub(r'<w:vertAlign\b[^>]*/>', '<w:vertAlign w:val="superscript"/>', inside)
                    changed = True
            else:
                inside = inside + '<w:vertAlign w:val="superscript"/>'
                changed = True
            if '<w:sz' in inside:
                if 'w:val="16"' not in inside:
                    inside = re.sub(r'<w:sz\b[^>]*/>', '<w:sz w:val="16"/>', inside)
                    changed = True
            else:
                inside = inside + '<w:sz w:val="16"/>'
                changed = True
            if changed:
                stats["fn_notes"] += 1
            return run[:rpr_match.start()] + open_tag + inside + close_tag + run[rpr_match.end():]
        return run

    xml = re.sub(r'<w:r\b[^>]*>(?:(?!</w:r>).)*?<w:footnoteRef\b[^>]*>(?:(?!</w:r>).)*?</w:r>', repl_fnref, xml, flags=re.S)

    # 3. Fonts in footnotes (only ascii / hAnsi)
    def repl_font(m):
        tag = m.group(0)
        orig = tag
        tag = re.sub(r'(w:(?:ascii|hAnsi)=)"Arial"', r'\1"Arial Narrow"', tag)
        tag = re.sub(r'(w:(?:ascii|hAnsi)=)"Times New Roman"', r'\1"Arial Narrow"', tag)
        tag = re.sub(r'(w:(?:ascii|hAnsi)=)"Calibri"', r'\1"Arial Narrow"', tag)
        tag = re.sub(r'(w:(?:ascii|hAnsi)=)"Aptos"', r'\1"Arial Narrow"', tag)
        tag = re.sub(r'(w:(?:ascii|hAnsi)=)"Segoe UI"(?! Symbol)', r'\1"Arial Narrow"', tag)
        if tag != orig:
            stats["fonts"] += 1
        return tag
    xml = re.sub(r'<w:rFonts\b[^>]*/>', repl_font, xml)

    return xml, stats


def normalize_xml_styles(xml: str) -> tuple[str, dict[str, int]]:
    stats = {"highlights": 0, "styles_fixed": 0}

    # 1. Highlights
    hl_count = len(re.findall(r'<w:highlight\b', xml))
    if hl_count:
        stats["highlights"] += hl_count
        xml = re.sub(r'<w:highlight\b[^>]*/>', '', xml)
        xml = re.sub(r'<w:highlight\b[^>]*>.*?</w:highlight>', '', xml, flags=re.S)

    # 2. Refdenotaalpie
    if 'styleId="Refdenotaalpie"' in xml:
        def repl_ref(m):
            style_content = m.group(0)
            if '<w:rPr>' in style_content:
                if '<w:vertAlign' not in style_content:
                    style_content = style_content.replace('<w:rPr>', '<w:rPr><w:vertAlign w:val="superscript"/>')
                    stats["styles_fixed"] += 1
            elif '<w:rPr/>' in style_content:
                style_content = style_content.replace('<w:rPr/>', '<w:rPr><w:vertAlign w:val="superscript"/></w:rPr>')
                stats["styles_fixed"] += 1
            else:
                style_content = re.sub(r'(</w:style>)', r'<w:rPr><w:vertAlign w:val="superscript"/></w:rPr>\1', style_content)
                stats["styles_fixed"] += 1
            return style_content
        xml = re.sub(r'<w:style\b[^>]*styleId="Refdenotaalpie"[^>]*>.*?</w:style>', repl_ref, xml, flags=re.S)
    else:
        style_xml = (
            '<w:style w:type="character" w:styleId="Refdenotaalpie">'
            '<w:name w:val="footnote reference"/>'
            '<w:basedOn w:val="Fuentedeprrafopredeter"/>'
            '<w:uiPriority w:val="99"/>'
            '<w:semiHidden/>'
            '<w:unhideWhenUsed/>'
            '<w:rPr>'
            '<w:rFonts w:ascii="Arial Narrow" w:hAnsi="Arial Narrow"/>'
            '<w:vertAlign w:val="superscript"/>'
            '</w:rPr>'
            '</w:style>'
        )
        xml = xml.replace('</w:styles>', style_xml + '</w:styles>')
        stats["styles_fixed"] += 1

    # 3. FootnoteReference
    if 'styleId="FootnoteReference"' in xml:
        def repl_fnref(m):
            style_content = m.group(0)
            if '<w:rPr>' in style_content:
                if '<w:vertAlign' not in style_content:
                    style_content = style_content.replace('<w:rPr>', '<w:rPr><w:vertAlign w:val="superscript"/>')
                    stats["styles_fixed"] += 1
            elif '<w:rPr/>' in style_content:
                style_content = style_content.replace('<w:rPr/>', '<w:rPr><w:vertAlign w:val="superscript"/></w:rPr>')
                stats["styles_fixed"] += 1
            else:
                style_content = re.sub(r'(</w:style>)', r'<w:rPr><w:vertAlign w:val="superscript"/></w:rPr>\1', style_content)
                stats["styles_fixed"] += 1
            return style_content
        xml = re.sub(r'<w:style\b[^>]*styleId="FootnoteReference"[^>]*>.*?</w:style>', repl_fnref, xml, flags=re.S)
    else:
        style_xml = (
            '<w:style w:type="character" w:styleId="FootnoteReference">'
            '<w:name w:val="footnote reference"/>'
            '<w:basedOn w:val="Fuentedeprrafopredeter"/>'
            '<w:uiPriority w:val="99"/>'
            '<w:semiHidden/>'
            '<w:unhideWhenUsed/>'
            '<w:rPr>'
            '<w:rFonts w:ascii="Arial Narrow" w:hAnsi="Arial Narrow"/>'
            '<w:vertAlign w:val="superscript"/>'
            '</w:rPr>'
            '</w:style>'
        )
        xml = xml.replace('</w:styles>', style_xml + '</w:styles>')
        stats["styles_fixed"] += 1

    return xml, stats


def normalize_other_xml(xml: str) -> tuple[str, dict[str, int]]:
    stats = {"highlights": 0, "fonts": 0}
    hl_count = len(re.findall(r'<w:highlight\b', xml))
    if hl_count:
        stats["highlights"] += hl_count
        xml = re.sub(r'<w:highlight\b[^>]*/>', '', xml)
        xml = re.sub(r'<w:highlight\b[^>]*>.*?</w:highlight>', '', xml, flags=re.S)

    def repl_font(m):
        tag = m.group(0)
        orig = tag
        tag = re.sub(r'(w:(?:ascii|hAnsi)=)"Arial"', r'\1"Arial Narrow"', tag)
        tag = re.sub(r'(w:(?:ascii|hAnsi)=)"Times New Roman"', r'\1"Arial Narrow"', tag)
        tag = re.sub(r'(w:(?:ascii|hAnsi)=)"Calibri"', r'\1"Arial Narrow"', tag)
        tag = re.sub(r'(w:(?:ascii|hAnsi)=)"Aptos"', r'\1"Arial Narrow"', tag)
        tag = re.sub(r'(w:(?:ascii|hAnsi)=)"Segoe UI"(?! Symbol)', r'\1"Arial Narrow"', tag)
        if tag != orig:
            stats["fonts"] += 1
        return tag
    xml = re.sub(r'<w:rFonts\b[^>]*/>', repl_font, xml)

    return xml, stats


def process_docx(path: Path, aplicar: bool = False) -> tuple[bool, dict[str, int]]:
    long_path = to_long_path(path)
    totals = {
        "highlights": 0,
        "fn_refs": 0,
        "fn_notes": 0,
        "styles_fixed": 0,
        "margins": 0,
        "spacing": 0,
        "fonts": 0,
    }

    try:
        with zipfile.ZipFile(long_path, "r") as z_in:
            infolist = z_in.infolist()
            contents = {}
            modified = False

            for item in infolist:
                raw_data = z_in.read(item.filename)
                if item.filename == "word/document.xml":
                    xml_str = raw_data.decode("utf-8", "replace")
                    norm_xml, st = normalize_xml_document(xml_str)
                    for k, v in st.items():
                        totals[k] += v
                    if norm_xml != xml_str:
                        modified = True
                        raw_data = norm_xml.encode("utf-8")
                elif item.filename == "word/footnotes.xml":
                    xml_str = raw_data.decode("utf-8", "replace")
                    norm_xml, st = normalize_xml_footnotes(xml_str)
                    for k, v in st.items():
                        totals[k] += v
                    if norm_xml != xml_str:
                        modified = True
                        raw_data = norm_xml.encode("utf-8")
                elif item.filename == "word/styles.xml":
                    xml_str = raw_data.decode("utf-8", "replace")
                    norm_xml, st = normalize_xml_styles(xml_str)
                    for k, v in st.items():
                        totals[k] += v
                    if norm_xml != xml_str:
                        modified = True
                        raw_data = norm_xml.encode("utf-8")
                elif (
                    item.filename.startswith("word/header")
                    or item.filename.startswith("word/footer")
                    or item.filename in ("word/endnotes.xml", "word/settings.xml")
                ):
                    xml_str = raw_data.decode("utf-8", "replace")
                    norm_xml, st = normalize_other_xml(xml_str)
                    for k, v in st.items():
                        totals[k] += v
                    if norm_xml != xml_str:
                        modified = True
                        raw_data = norm_xml.encode("utf-8")

                contents[item] = raw_data

        if modified and aplicar:
            # Atomic rewrite using temporary file
            fd, tmp_file = tempfile.mkstemp(prefix="norm_docx_", suffix=".docx")
            os.close(fd)
            with zipfile.ZipFile(tmp_file, "w", zipfile.ZIP_DEFLATED) as z_out:
                for item, data in contents.items():
                    z_out.writestr(item, data)
            shutil.copyfile(tmp_file, long_path)
            try:
                os.remove(tmp_file)
            except OSError:
                pass

        return modified, totals

    except Exception as exc:
        print(f"Error procesando {path.name}: {exc}", file=sys.stderr)
        return False, totals


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalizador Popperiano de plantillas CC1")
    parser.add_argument("--aplicar", action="store_true", help="Aplica los cambios directamente a los archivos")
    args = parser.parse_args()

    rutas = [
        RAIZ / "plantillas_maestras",
        RAIZ / "automatizacion_antigravity" / "modelos",
    ]

    todos_docx: list[Path] = []
    for r in rutas:
        if r.exists():
            todos_docx.extend(sorted(r.rglob("*.docx")))

    print("=" * 78)
    print("NORMALIZADOR POPPERIANO DE PLANTILLAS Y MODELOS CC1")
    print("=" * 78)
    print(f"Total de archivos .docx detectados: {len(todos_docx)}")
    print(f"Modo: {'APLICAR CAMBIOS' if args.aplicar else 'SOLO VERIFICACION (dry-run)'}")
    print("-" * 78)

    archivos_modificados = 0
    resumen = {
        "highlights": 0,
        "fn_refs": 0,
        "fn_notes": 0,
        "styles_fixed": 0,
        "margins": 0,
        "spacing": 0,
        "fonts": 0,
    }

    for idx, p in enumerate(todos_docx, 1):
        mod, totals = process_docx(p, aplicar=args.aplicar)
        if mod:
            archivos_modificados += 1
            for k in resumen:
                resumen[k] += totals[k]
        if idx % 100 == 0 or idx == len(todos_docx):
            print(f"  [{idx:3d}/{len(todos_docx)}] Procesados... ({archivos_modificados} con calibraciones pendientes/aplicadas)")

    print("-" * 78)
    print("RESUMEN DE CALIBRACION POPPERIANA:")
    print(f"  Archivos que requerian calibracion: {archivos_modificados} de {len(todos_docx)}")
    print(f"  Resaltados purgados (<w:highlight>): {resumen['highlights']}")
    print(f"  Llamadas de nota al pie elevadas a superindice (document.xml): {resumen['fn_refs']}")
    print(f"  Numeros de pie calibrados a superindice 8pt (footnotes.xml): {resumen['fn_notes']}")
    print(f"  Definiciones de estilo calibradas (styles.xml): {resumen['styles_fixed']}")
    print(f"  Margenes normalizados a 3,0/3,0/2,5/2,5 cm: {resumen['margins']}")
    print(f"  Parrafos con interlineado corregido a sencillo (240): {resumen['spacing']}")
    print(f"  Runs con tipografia ascii/hAnsi normalizada a Arial Narrow: {resumen['fonts']}")
    print("=" * 78)

    if not args.aplicar and archivos_modificados > 0:
        print("Para escribir las correcciones en el repositorio ejecuta:")
        print("    python scripts/normalizar_plantillas_popperianas.py --aplicar")
    elif args.aplicar:
        print("Calibracion popperiana aplicada con exito en todos los archivos.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
