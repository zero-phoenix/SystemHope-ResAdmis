#!/usr/bin/env python
"""Catálogo OOXML verificable. No modifica documentos ni certifica validez."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import io
import json
import os
from pathlib import Path
import re
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
import zipfile

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = Path(r"C:\Users\D\Desktop\000 PLAN PHOENYX")
READINESS = "requiere_revision_juridica_visual"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def normalizar_cadena(value):
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def contained(path, root):
    resolved = Path(path).resolve()
    if not resolved.is_relative_to(Path(root).resolve()):
        raise ValueError("Ruta fuera de la frontera autorizada")
    return resolved


def disjoint(source, output):
    source, output = Path(source).resolve(), Path(output).resolve()
    if source.is_relative_to(output) or output.is_relative_to(source):
        raise ValueError("Fuente y salida no pueden contenerse entre sí")


def publish_bytes(path, data, root):
    """Publicación completa sin reemplazar contenido distinto."""
    path = contained(path, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    contained(path, root)
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError("Destino existente con contenido diferente")
        return "ya_verificado"
    fd, temporary = tempfile.mkstemp(prefix=".phoenyx-", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        contained(path, root)
        try:
            os.link(temporary, path)
        except FileExistsError:
            if path.read_bytes() != data:
                raise FileExistsError("Destino concurrente con contenido diferente")
            return "ya_verificado"
        return "copiado"
    finally:
        temporary.unlink(missing_ok=True)


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def document_paths(source):
    source = Path(source).resolve(strict=True)
    for directory, dirs, files in os.walk(source, followlinks=False):
        dirs[:] = sorted(d for d in dirs if not (Path(directory) / d).is_symlink()
                         and not getattr(Path(directory) / d, "is_junction", lambda: False)()
                         and (Path(directory) / d).resolve().is_relative_to(source))
        for name in sorted(files):
            if name.lower().endswith(".docx") and not name.startswith("~$"):
                yield Path(directory) / name


def paragraph_text(paragraph):
    text = []
    for node in paragraph.iter():
        if node.tag == W + "t":
            text.append(node.text or "")
        elif node.tag == W + "tab":
            text.append("\t")
        elif node.tag in (W + "br", W + "cr"):
            text.append("\n")
    return "".join(text)


def extract_ooxml(data):
    roots, paragraphs = {}, []
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Paquete ZIP con miembros duplicados")
        if "word/document.xml" not in names or "[Content_Types].xml" not in names:
            raise ValueError("Paquete sin componentes DOCX obligatorios")
        if sum(item.file_size for item in archive.infolist()) > 256 * 1024 * 1024:
            raise ValueError("Paquete supera límite de lectura de 256 MiB")
        if archive.testzip():
            raise ValueError("Paquete ZIP con CRC inválido")
        for name in names:
            if not re.fullmatch(r"word/(?:document|footnotes|endnotes|header\d*|footer\d*)\.xml", name):
                continue
            if archive.getinfo(name).file_size > 20 * 1024 * 1024:
                raise ValueError("Componente XML supera límite de 20 MiB")
            xml = archive.read(name)
            if b"<!DOCTYPE" in xml.upper() or b"<!ENTITY" in xml.upper():
                raise ValueError("Declaraciones XML no permitidas")
            root = ET.fromstring(xml)
            roots[name] = root
            for number, paragraph in enumerate(root.iter(W + "p"), 1):
                text = paragraph_text(paragraph)
                if text.strip():
                    paragraphs.append((name, number, text))
    return roots, paragraphs, sorted(names)


def extract_metadata(root):
    metadata = {k: "" for k in ("expediente", "denunciante", "denunciado", "resolucion", "fecha")}
    label = re.compile(r"^(EXPEDIENTE|DENUNCIANTES?|DENUNCIADOS?|RESOLUCI[ÓO]N)\s*:\s*(.+)$", re.I)
    lines = [paragraph_text(p) for p in root.iter(W + "p")]
    lines += [" ".join(" ".join(paragraph_text(p) for p in c.iter(W + "p"))
                       for c in row.findall(W + "tc")) for row in root.iter(W + "tr")]
    for line in lines:
        clean = re.sub(r"\s+", " ", line).strip()
        match = label.match(clean)
        if match:
            key = normalizar_cadena(match.group(1)).removesuffix("s")
            if key in metadata and not metadata[key]:
                metadata[key] = match.group(2)
        if re.match(r"^Lima,\s*\d{1,2}\s+de\s+", clean, re.I) and not metadata["fecha"]:
            metadata["fecha"] = clean
    return metadata


def historical_date(text):
    months = {name: i for i, name in enumerate(("enero", "febrero", "marzo", "abril", "mayo", "junio",
               "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"), 1)}
    months["setiembre"] = 9
    match = re.search(r"\b(\d{1,2})\s+de\s+(\w+)\s+del?\s+(\d{4})\b", text, re.I)
    if not match or match[2].lower() not in months:
        return None
    from datetime import date
    try:
        return date(int(match[3]), months[match[2].lower()], int(match[1])).isoformat()
    except ValueError:
        return None


def subject_type(folder):
    words = set(normalizar_cadena(folder).split("_"))
    if words & {"sucesion", "herederos"}:
        return "sucesion_intestada"
    if words & {"varios", "varias", "plural", "mujeres"}:
        return "varios"
    if "mujer" in words:
        return "mujer"
    if words & {"varon", "hombre"}:
        return "varon"
    return "no_determinado"


def provider_type(text, folder=""):
    full = " " + normalizar_cadena(text or folder).replace("_", " ") + " "
    banks = bool(re.search(r"\b(?:banco|bbva|bcp|interbank|scotiabank|mibanco)\b", full))
    insurers = bool(re.search(r"\b(?:seguros|aseguradora|rimac|pacifico|mapfre|interseguro|cardif|chubb|protecta)\b", full))
    broker = bool(re.search(r"\b(?:corredor|corredores|broker|marsh|aon)\b", full))
    # Una conjunción dentro de la razón social no prueba pluralidad.
    multiple = bool(re.search(r";\s*\S", text)) or (banks and insurers)
    if multiple:
        kind = "banco_y_aseguradora" if banks and insurers else "multiples_por_confirmar"
    elif broker:
        kind = "corredor"
    elif banks:
        kind = "banco_o_financiera"
    elif insurers:
        kind = "aseguradora"
    else:
        kind = "no_determinado"
    return {"tipo_sugerido": kind, "multiple_sugerido": True if multiple else None,
            "certeza": "indicio_textual_requiere_revision"}


def analizar_archivo(path, source):
    source = Path(source).resolve(strict=True)
    row = {"ruta_relativa": path.relative_to(source).as_posix(), "estado": "error",
           "readiness": READINESS, "errores": [], "sha256_fuente": None}
    try:
        data = contained(path, source).read_bytes()
        row.update(sha256_fuente=sha256_bytes(data), bytes_fuente=len(data))
        roots, paragraphs, members = extract_ooxml(data)
        metadata = extract_metadata(roots["word/document.xml"])
        parts = Path(row["ruta_relativa"]).parts
        folder = parts[-2] if len(parts) > 1 else ""
        mojibake, citations, notifications = [], [], []
        for part, number, text in paragraphs:
            if re.search(r"\ufffd|Ã[\u0080-\u00bf]|Â[\u0080-\u00bf]|â[€™œ]", text):
                mojibake.append({"parte": part, "parrafo": number})
            for decree in sorted(set(re.findall(r"\b\d{3,4}-\d{4}-JUS\b", text, re.I))):
                citations.append({"decreto": decree.upper(), "parte": part, "parrafo": number})
            kinds = [kind for token, kind in (("correo electr", "correo"), ("casilla electr", "casilla"),
                     ("domicilio procesal", "domicilio_procesal"), ("domicilio real", "domicilio_real"))
                     if token in text.lower()]
            if kinds:
                notifications.append({"tipos_mencionados": kinds, "parte": part, "parrafo": number})
        row.update(estado="leido", metadata_doc=metadata, fecha_documento_iso=historical_date(metadata["fecha"]),
                   taxonomia={"rama_fuente": parts[0] if len(parts) > 1 else "",
                              "cobertura_fuente": parts[1] if len(parts) > 2 else "",
                              "materia_fuente": parts[2] if len(parts) > 3 else "",
                              "sujeto_sugerido": subject_type(folder),
                              "proveedor": provider_type(metadata["denunciado"], parts[3] if len(parts) > 4 else "")},
                   posibles_errores_codificacion=mojibake, tiene_mojibake=bool(mojibake),
                   menciones_decretos=citations, menciones_notificacion=notifications,
                   notificacion_advertencia="Menciones textuales; no acreditan autorización ni vía aplicable.",
                   partes_ooxml=members, parrafos_por_parte=dict(Counter(p[0] for p in paragraphs)),
                   contenido_modificado=False, revision_visual_realizada=False,
                   nota_temporal="Fecha extraída del documento histórico; no se actualizan fechas ni normas.")
    except (OSError, ValueError, zipfile.BadZipFile, RuntimeError, ET.ParseError) as exc:
        row["errores"].append({"tipo": type(exc).__name__, "detalle": str(exc)})
    return row


def audit(source):
    source = Path(source).resolve(strict=True)
    rows = [analizar_archivo(path, source) for path in sorted(document_paths(source))]
    return {"schema_version": 2, "source_root": str(source), "readiness": READINESS,
            "metodo": "Lectura OOXML y SHA-256; sin modificación ni validación jurídica/visual.",
            "resumen": {"total": len(rows), "leidos": sum(r["estado"] == "leido" for r in rows),
                        "errores": sum(r["estado"] == "error" for r in rows),
                        "posible_mojibake": sum(r.get("tiene_mojibake", False) for r in rows)},
            "archivos": rows}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-root", type=Path, default=REPO_ROOT / "revision_codex" / "corpus_clasificado")
    parser.add_argument("--catalog", type=Path, help="JSON de salida dentro de --output-root")
    args = parser.parse_args(argv)
    try:
        source, output = args.source.resolve(strict=True), args.output_root.resolve()
        disjoint(source, output)
        catalog = contained(args.catalog or output / "catalogo_fuente.json", output)
        result = audit(source)
        publish_bytes(catalog, json_bytes(result), output)
        print(json.dumps(result["resumen"], ensure_ascii=False))
        return 1 if result["resumen"]["errores"] else 0
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
