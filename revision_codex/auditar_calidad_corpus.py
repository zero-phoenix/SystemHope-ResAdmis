"""Auditoría de procedencia y revisión pendiente; nunca modifica documentos."""

import argparse
import csv
import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
CONTENT = re.compile(r"word/(?:document|footnotes|endnotes|header\d+|footer\d+)\.xml$")


def audit(source):
    rows = []
    for path in sorted(source.rglob("*.docx")):
        if path.name.startswith("~$"):
            continue
        row = {"origen": path.relative_to(source).as_posix(),
               "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "alertas": []}
        with zipfile.ZipFile(path) as package:
            texts, citations, page_sizes = [], [], []
            reference_ids, note_ids = set(), set()
            for name in package.namelist():
                if not CONTENT.fullmatch(name):
                    continue
                tree = ET.fromstring(package.read(name))
                for index, paragraph in enumerate(tree.iter(W + "p")):
                    text = "".join(t.text or "" for t in paragraph.iter(W + "t"))
                    texts.append(text)
                    if re.search(r"004-2019-JUS|006-2026-JUS", text):
                        citations.append({"parte": name, "parrafo": index + 1,
                                          "decretos": sorted(set(re.findall(r"00[46]-(?:2019|2026)-JUS", text))),
                                          "articulos_mencionados": re.findall(r"art[ií]culo\s+(\d+(?:\.\d+)?)", text, re.I)})
                reference_ids.update(x.get(W + "id") for x in tree.iter(W + "footnoteReference"))
                if name == "word/footnotes.xml":
                    note_ids.update(x.get(W + "id") for x in tree.iter(W + "footnote"))
                if name == "word/document.xml":
                    page_sizes.extend({"ancho_twips": int(x.get(W + "w", 0)),
                                       "alto_twips": int(x.get(W + "h", 0))}
                                      for x in tree.iter(W + "pgSz"))
            text = "\n".join(texts)
            old, new = "004-2019-JUS" in text, "006-2026-JUS" in text
            row.update(citas_lpag=citations, lpag_2019=old, lpag_2026=new,
                       paginas_configuradas=page_sizes,
                       notas_sin_destino=sorted(reference_ids - note_ids),
                       menciones_revisables={label: len(re.findall(pattern, text, re.I)) for label, pattern in {
                           "auto_contexto_ambiguo": r"\bautos?\b",
                           "doctor_contexto_ambiguo": r"\bdoctor(?:a|es|as)?\b|\bDr\.",
                           "induccion_no_retipificar_automaticamente": r"\binduc\w*\s+(?:a|al)\s+error\b",
                           "fecha_no_sustituir_globalmente": r"25\s+de\s+enero\s+de\s+2019",
                           "moneda_formato_anglosajon": r"(?:S/|US\$)\s*\d{1,3}(?:,\d{3})*\.\d{2}\b",
                       }.items()})
            if old:
                row["alertas"].append("revisar_vigencia_y_concordancia_segun_fecha_y_finalidad")
            if old and new:
                row["alertas"].append("coexisten_dos_TUO_revisar_cuerpo_y_notas")
            if not old and not new:
                row["alertas"].append("sin_referencia_literal_a_TUO_2019_2026")
            if any(abs(s["ancho_twips"] - 11906) > 5 or abs(s["alto_twips"] - 16838) > 5 for s in page_sizes):
                row["alertas"].append("papel_distinto_de_A4")
            if reference_ids - note_ids:
                row["alertas"].append("referencia_nota_sin_destino")
            row["aptitud"] = "historico_preservado_requiere_revision_para_nuevo_caso"
            rows.append(row)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source, output = args.source.resolve(strict=True), args.output.resolve()
    if source == output or source in output.parents or output in source.parents:
        parser.error("Fuente y salida deben estar separadas.")
    rows = audit(source)
    summary = dict(Counter(flag for row in rows for flag in row["alertas"]))
    summary.update(documentos=len(rows), pdf_referencia=sum(1 for _ in source.rglob("*.pdf")),
                   lpag_2019=sum(r["lpag_2019"] for r in rows),
                   lpag_2026=sum(r["lpag_2026"] for r in rows))
    output.mkdir(parents=True, exist_ok=True)
    (output / "revision_por_documento.json").write_text(json.dumps({"resumen": summary, "documentos": rows},
                                                                  ensure_ascii=False, indent=2), encoding="utf-8")
    with (output / "cola_revision.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["origen", "sha256", "lpag_2019", "lpag_2026", "alertas", "aptitud"])
        writer.writeheader()
        for row in rows:
            writer.writerow({key: "; ".join(row[key]) if key == "alertas" else row[key] for key in writer.fieldnames})
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
