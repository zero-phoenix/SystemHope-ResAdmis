#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Huella de FORMATO de un documento, medida sin OCR (F6 del plan v3).

Lo mas preciso para el formato no es mirar una imagen: es leer la estructura del
propio archivo, que es exacta, local y privada.

  .docx : OOXML directo -> fuente, tamano, negrita, alineacion, interlineado,
          espaciado antes/despues, sangrias (izquierda, francesa, primera
          linea), margenes y tamano de pagina, encabezado, pie, notas al pie
          (tamano y superindice) y resaltados.
  .pdf  : PyMuPDF get_text("dict") (objetos de texto, NO OCR) -> fuentes,
          tamanos, negrita/cursiva, margenes reales, interlineado medido entre
          lineas, alineacion inferida de los bordes. Una pagina sin capa de texto
          se declara «escaneada: solo lectura visual».

Con --perfil se construye el perfil canonico CC1 a partir de las plantillas
(docs/estilo_formato.json); con --comparar se contrasta un documento con ese perfil.

Uso:
    python scripts/medir_formato.py <archivo.docx|archivo.pdf>
    python scripts/medir_formato.py <archivo.docx> --comparar
    python scripts/medir_formato.py --perfil
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

RAIZ = Path(__file__).resolve().parent.parent
PERFIL = RAIZ / "docs" / "estilo_formato.json"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
TWIP_CM = 1 / 567.0


def _val(el, tag, attr="val"):
    if el is None:
        return None
    x = el.find(W + tag)
    return None if x is None else x.get(W + attr)


def medir_docx(ruta: Path) -> dict:
    z = zipfile.ZipFile(ruta)
    doc = ET.fromstring(z.read("word/document.xml"))
    estilos = (
        ET.fromstring(z.read("word/styles.xml"))
        if "word/styles.xml" in z.namelist()
        else None
    )
    defecto_sz = None
    if estilos is not None:
        dd = estilos.find(f"{W}docDefaults/{W}rPrDefault/{W}rPr")
        defecto_sz = _val(dd, "sz")
    fuentes, tamanos, negrita = Counter(), Counter(), Counter()
    alinea, interl, antes, despues = Counter(), Counter(), Counter(), Counter()
    sangria_izq, sangria_fr, sangria_pl = Counter(), Counter(), Counter()
    resaltados = 0
    for p in doc.iter(W + "p"):
        ppr = p.find(W + "pPr")
        texto = "".join(t.text or "" for t in p.iter(W + "t"))
        if not texto.strip():
            continue
        alinea[_val(ppr, "jc") or "(estilo)"] += 1
        sp = ppr.find(W + "spacing") if ppr is not None else None
        if sp is not None:
            interl[sp.get(W + "line") or "(estilo)"] += 1
            antes[sp.get(W + "before") or "0"] += 1
            despues[sp.get(W + "after") or "0"] += 1
        ind = ppr.find(W + "ind") if ppr is not None else None
        if ind is not None:
            sangria_izq[ind.get(W + "left") or ind.get(W + "start") or "0"] += 1
            sangria_fr[ind.get(W + "hanging") or "0"] += 1
            sangria_pl[ind.get(W + "firstLine") or "0"] += 1
        for r in p.iter(W + "r"):
            t = "".join(x.text or "" for x in r.iter(W + "t"))
            if not t:
                continue
            rpr = r.find(W + "rPr")
            f = rpr.find(W + "rFonts") if rpr is not None else None
            fuentes[(f.get(W + "ascii") if f is not None else None) or "(estilo)"] += (
                len(t)
            )
            tamanos[_val(rpr, "sz") or ("(defecto %s)" % defecto_sz)] += len(t)
            b = rpr.find(W + "b") if rpr is not None else None
            negrita[
                "negrita"
                if b is not None and b.get(W + "val") not in ("0", "false")
                else "normal"
            ] += len(t)
            if rpr is not None and rpr.find(W + "highlight") is not None:
                resaltados += 1
    secciones = []
    for s in doc.iter(W + "sectPr"):
        pg, mar = s.find(W + "pgSz"), s.find(W + "pgMar")
        if mar is None:
            continue
        secciones.append(
            {
                "pagina_cm": [
                    round(int(pg.get(W + "w")) * TWIP_CM, 2),
                    round(int(pg.get(W + "h")) * TWIP_CM, 2),
                ]
                if pg is not None
                else None,
                "margenes_cm": {
                    k: round(int(mar.get(W + k, 0)) * TWIP_CM, 2)
                    for k in ("top", "bottom", "left", "right")
                },
            }
        )
    partes = {
        n: re.sub(
            r"\s+", " ", re.sub(r"<[^>]+>", " ", z.read(n).decode("utf-8", "replace"))
        ).strip()
        for n in z.namelist()
        if re.match(r"word/(header|footer)\d*\.xml", n)
    }
    notas = {}
    if "word/footnotes.xml" in z.namelist():
        fx = z.read("word/footnotes.xml").decode("utf-8", "replace")
        notas = {
            "cantidad": max(0, len(re.findall(r"<w:footnote ", fx)) - 2),
            "tamanos": dict(
                Counter(re.findall(r'<w:sz w:val="(\d+)"', fx)).most_common(3)
            ),
            "referencias_superindice": fx.count('w:val="superscript"'),
        }
    return {
        "tipo": "docx",
        "fuentes_por_caracter": dict(fuentes.most_common(4)),
        "tamanos_medio_punto": dict(tamanos.most_common(4)),
        "negrita_por_caracter": dict(negrita),
        "alineacion": dict(alinea.most_common(4)),
        "interlineado_240=sencillo": dict(interl.most_common(3)),
        "espaciado_antes": dict(antes.most_common(3)),
        "espaciado_despues": dict(despues.most_common(3)),
        "sangria_izquierda_twips": dict(sangria_izq.most_common(4)),
        "sangria_francesa_twips": dict(sangria_fr.most_common(4)),
        "sangria_primera_linea_twips": dict(sangria_pl.most_common(3)),
        "secciones": secciones[:3],
        "encabezados_y_pies": {k: v[:80] for k, v in partes.items() if v},
        "notas_al_pie": notas,
        "resaltados": resaltados,
    }


def medir_pdf(ruta: Path) -> dict:
    import fitz  # PyMuPDF: objetos de texto del PDF, no OCR

    salida = {"tipo": "pdf", "paginas": []}
    with fitz.open(str(ruta)) as doc:
        for pagina in doc:
            d = pagina.get_text("dict")
            spans = [
                s
                for b in d["blocks"]
                if b.get("type") == 0
                for l in b["lines"]
                for s in l["spans"]
                if s["text"].strip()
            ]
            if not spans:
                salida["paginas"].append(
                    {
                        "n": pagina.number + 1,
                        "escaneada": True,
                        "nota": "sin capa de texto: solo lectura visual (captura completa)",
                    }
                )
                continue
            fuentes, tamanos = Counter(), Counter()
            negrita = 0
            x0s, x1s, ys = [], [], []
            for s in spans:
                n = len(s["text"])
                fuentes[s["font"]] += n
                tamanos[round(s["size"], 1)] += n
                negrita += n if (s["flags"] & 16 or "Bold" in s["font"]) else 0
                x0s.append(s["bbox"][0])
                x1s.append(s["bbox"][2])
                ys.append(round(s["bbox"][3], 1))
            ys = sorted(set(ys))
            pasos = [round(b - a, 1) for a, b in zip(ys, ys[1:]) if 0 < b - a < 40]
            ancho, alto = pagina.rect.width, pagina.rect.height
            pt_cm = 2.54 / 72
            bordes_der = Counter(round(x, 0) for x in x1s)
            salida["paginas"].append(
                {
                    "n": pagina.number + 1,
                    "fuentes": dict(fuentes.most_common(3)),
                    "tamanos_pt": dict(tamanos.most_common(3)),
                    "negrita_%": round(
                        100 * negrita / max(1, sum(fuentes.values())), 1
                    ),
                    "margenes_cm": {
                        "izquierdo": round(min(x0s) * pt_cm, 2),
                        "derecho": round((ancho - max(x1s)) * pt_cm, 2),
                        "superior": round(min(ys) * pt_cm, 2),
                        "inferior": round((alto - max(ys)) * pt_cm, 2),
                    },
                    "interlineado_pt": statistics.mode(pasos) if pasos else None,
                    "justificado_probable": bordes_der.most_common(1)[0][1]
                    >= 0.4 * len(x1s)
                    if x1s
                    else None,
                }
            )
    return salida


def moda(dic: dict):
    return max(dic.items(), key=lambda kv: kv[1])[0] if dic else None


def construir_perfil() -> dict:
    agregados: dict[str, Counter] = {}
    rutas = sorted(
        p
        for p in (RAIZ / "plantillas_maestras").rglob("*")
        if p.suffix.lower() == ".docx"
    )
    for r in rutas:
        h = medir_docx(r)
        for campo in (
            "fuentes_por_caracter",
            "tamanos_medio_punto",
            "alineacion",
            "interlineado_240=sencillo",
            "espaciado_antes",
            "espaciado_despues",
            "sangria_izquierda_twips",
            "sangria_francesa_twips",
        ):
            agregados.setdefault(campo, Counter())[moda(h[campo])] += 1
        for s in h["secciones"][:1]:
            agregados.setdefault("margenes_cm", Counter())[
                json.dumps(s["margenes_cm"], sort_keys=True)
            ] += 1
        agregados.setdefault("notas_tamano", Counter())[
            moda(h["notas_al_pie"].get("tamanos", {}))
        ] += 1
    perfil = {
        "fuente": "Moda por documento sobre %d plantillas (scripts/medir_formato.py --perfil)"
        % len(rutas)
    }
    for campo, c in agregados.items():
        total = sum(c.values())
        valor, veces = c.most_common(1)[0]
        perfil[campo] = {
            "canonico": json.loads(valor) if campo == "margenes_cm" else valor,
            "documentos": veces,
            "de": total,
        }
    PERFIL.write_text(
        json.dumps(perfil, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    return perfil


def comparar(h: dict) -> list[str]:
    if not PERFIL.exists():
        return ["(sin perfil: ejecuta --perfil)"]
    p = json.loads(PERFIL.read_text(encoding="utf-8"))
    obs = []
    for campo in (
        "fuentes_por_caracter",
        "tamanos_medio_punto",
        "alineacion",
        "interlineado_240=sencillo",
        "sangria_izquierda_twips",
        "sangria_francesa_twips",
    ):
        if campo in p and moda(h.get(campo, {})) != p[campo]["canonico"]:
            obs.append(
                "%s: el documento usa %s; el corpus %s (%d de %d)"
                % (
                    campo,
                    moda(h.get(campo, {})),
                    p[campo]["canonico"],
                    p[campo]["documentos"],
                    p[campo]["de"],
                )
            )
    if (
        h.get("secciones")
        and "margenes_cm" in p
        and h["secciones"][0]["margenes_cm"] != p["margenes_cm"]["canonico"]
    ):
        obs.append(
            "margenes: %s; el corpus %s"
            % (h["secciones"][0]["margenes_cm"], p["margenes_cm"]["canonico"])
        )
    if h.get("resaltados"):
        obs.append("resaltados: %d (prohibidos)" % h["resaltados"])
    return obs


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("archivo", nargs="?")
    ap.add_argument("--perfil", action="store_true")
    ap.add_argument("--comparar", action="store_true")
    a = ap.parse_args(argv)
    if a.perfil:
        print(json.dumps(construir_perfil(), ensure_ascii=False, indent=1))
        return 0
    if not a.archivo:
        ap.print_help()
        return 2
    ruta = Path(a.archivo)
    h = medir_pdf(ruta) if ruta.suffix.lower() == ".pdf" else medir_docx(ruta)
    print(json.dumps(h, ensure_ascii=False, indent=1))
    if a.comparar and h["tipo"] == "docx":
        obs = comparar(h)
        print("\nCONTRASTE CON EL PERFIL CC1:" + ("" if obs else " sin diferencias"))
        for o in obs:
            print("  - " + o)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
