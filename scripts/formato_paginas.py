# -*- coding: utf-8 -*-
"""Formato de cada pagina del expediente, medido sin OCR (v3.1).

Mandato del instructor (24/09/2026): de cada hoja no solo el texto, tambien
«tamaño de letra, pie de página, negritas, tipo de letra, encuadre,
alineamiento». Lo exacto no sale de mirar una imagen: sale de la estructura del
PDF (PyMuPDF `get_text("dict")`, objetos de texto, NO reconocimiento optico).
La captura completa de la pagina sigue siendo la lectura (R-137); esta ficha le
pone cifras a lo que se ve y dice lo que la imagen no dice (la familia y el
cuerpo de la letra en puntos).

Lo que una pagina escaneada no tiene (capa de texto) no se inventa: se declara
«escaneada: formato solo visual» y se lee en la captura.

Uso (lo llama `admisorio.py preparar`; tambien suelto):
    python scripts/formato_paginas.py <carpeta_o_pdf>
"""

from __future__ import annotations

import re
import statistics
import sys
from collections import Counter
from pathlib import Path

PT_CM = 2.54 / 72


def _familia(fuente: str) -> str:
    """«ABCDEF+ArialNarrow-Bold» -> «ArialNarrow»."""
    f = fuente.split("+", 1)[-1]
    return re.sub(r"[-,](?:Bold?|Bol|Ital\w*|Obl\w*|Regular|Roman|MT|PSMT|Black|Light|Medium)+$", "", f, flags=re.I) or f


def _estilo(span: dict) -> set[str]:
    e = set()
    nombre = span["font"].lower()
    if span["flags"] & 16 or "bold" in nombre or "black" in nombre:
        e.add("negrita")
    if span["flags"] & 2 or "italic" in nombre or "oblique" in nombre:
        e.add("cursiva")
    if span["flags"] & 1:
        e.add("superindice")
    return e


def _posicion(r, ancho: float, alto: float) -> str:
    cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
    v = "arriba" if cy < alto / 3 else ("abajo" if cy > 2 * alto / 3 else "centro")
    h = "izquierda" if cx < ancho / 3 else ("derecha" if cx > 2 * ancho / 3 else "centro")
    return v if h == "centro" and v != "centro" else ("%s-%s" % (v, h) if v != "centro" else h)


def _alineacion(lineas: list, izq: float, der: float) -> str:
    """Alineacion de un bloque por las cajas de sus lineas (tolerancia 3 pt)."""
    tol = 3.0
    if not lineas:
        return "?"
    x0 = [l[0] for l in lineas]
    x1 = [l[2] for l in lineas]
    centro_pagina = (izq + der) / 2
    centrado = all(abs((a + b) / 2 - centro_pagina) < 8 for a, b in zip(x0, x1))
    if len(lineas) == 1:
        a, b = x0[0], x1[0]
        if centrado and a - izq > 20:
            return "centrado"
        if abs(b - der) < tol and a - izq > 20:
            return "derecha"
        return "izquierda"
    if centrado and min(x0) - izq > 20:
        return "centrado"
    cuerpo = x1[:-1]
    if all(abs(b - max(x1)) < tol for b in cuerpo) and max(x0[1:], default=x0[0]) - min(x0[1:], default=x0[0]) < tol:
        return "justificado"
    if all(abs(b - max(x1)) < tol for b in x1) and max(x0) - min(x0) > tol:
        return "derecha"
    return "izquierda"


def _norm_linea(t: str) -> str:
    return re.sub(r"\d+", "#", re.sub(r"\s+", " ", t)).strip()


def lineas_de_margen(pagina) -> tuple[list[str], list[str]]:
    """Lineas de la franja superior (15 %) e inferior (10 %) de la hoja."""
    alto = pagina.rect.height
    cab, pie = [], []
    for b in pagina.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for l in b["lines"]:
            t = "".join(s["text"] for s in l["spans"]).strip()
            if not t:
                continue
            if l["bbox"][3] < alto * 0.15:
                cab.append(t)
            elif l["bbox"][1] > alto * 0.90:
                pie.append(t)
    return cab, pie


def formato_pagina(pagina, repetidas: set | None = None) -> dict:
    ancho, alto = pagina.rect.width, pagina.rect.height
    d = pagina.get_text("dict")
    bloques = [b for b in d["blocks"] if b.get("type") == 0]
    spans = [
        (s, l["bbox"], b)
        for b in bloques
        for l in b["lines"]
        for s in l["spans"]
        if s["text"].strip()
    ]
    salida: dict = {
        "pagina": pagina.number + 1,
        "tamano": "%s %s (%.1f x %.1f cm)"
        % (
            "A4" if abs(ancho - 595) < 6 and abs(alto - 842) < 6 else ("Carta" if abs(ancho - 612) < 6 and abs(alto - 792) < 6 else "otro"),
            "vertical" if alto >= ancho else "horizontal",
            ancho * PT_CM,
            alto * PT_CM,
        ),
        "rotacion": pagina.rotation,
    }
    imagenes = []
    for info in pagina.get_image_info():
        r = info["bbox"]
        area = (r[2] - r[0]) * (r[3] - r[1]) / (ancho * alto)
        imagenes.append(
            {"posicion": _posicion(r, ancho, alto), "cm": "%.1f x %.1f" % ((r[2] - r[0]) * PT_CM, (r[3] - r[1]) * PT_CM), "area": area}
        )
    salida["imagenes"] = imagenes
    firmas = []
    try:
        for w in pagina.widgets() or []:
            if "sign" in (w.field_type_string or "").lower():
                firmas.append(_posicion(w.rect, ancho, alto))
    except Exception:
        pass
    salida["campos_de_firma"] = firmas
    anot = Counter()
    for a in pagina.annots() or []:
        anot[a.type[1]] += 1
    salida["anotaciones"] = dict(anot)
    if len("".join(s["text"] for s, _l, _b in spans).strip()) < 20:
        salida["escaneada"] = any(i["area"] > 0.6 for i in imagenes) or not spans
        return salida

    # Encabezado y pie: lo que SE REPITE en las paginas del mismo PDF dentro de
    # las franjas de margen («Página # de #», el membrete). Una franja fija se
    # tragaba el cuerpo de las hojas que empiezan arriba. Con una sola pagina,
    # franja del 9 % / 8 %.
    def _linea(l):
        return _norm_linea("".join(sp["text"] for sp in l["spans"]))

    lineas_margen = {
        id(l): _linea(l)
        for b in bloques
        for l in b["lines"]
        if l["bbox"][3] < alto * 0.15 or l["bbox"][1] > alto * 0.90
    }
    if repetidas:
        es_margen = lambda l: lineas_margen.get(id(l)) in repetidas  # noqa: E731
    else:
        es_margen = lambda l: l["bbox"][3] < alto * 0.09 or l["bbox"][1] > alto * 0.92  # noqa: E731
    linea_de = {}
    for b in bloques:
        for l in b["lines"]:
            for sp in l["spans"]:
                linea_de[id(sp)] = l
    cuerpo = [(s, l, b) for s, l, b in spans if not es_margen(linea_de[id(s)])]
    cab = [s["text"].strip() for s, l, _b in spans if es_margen(linea_de[id(s)]) and l[3] < alto / 2]
    pie = [s["text"].strip() for s, l, _b in spans if es_margen(linea_de[id(s)]) and l[1] >= alto / 2]
    cab_lim, pie_lim = 0, alto
    base = cuerpo or spans
    izq = min(l[0] for _s, l, _b in base)
    der = max(l[2] for _s, l, _b in base)
    sup = min(l[1] for _s, l, _b in base)
    inf = max(l[3] for _s, l, _b in base)
    salida["margenes_cm"] = {
        "superior": round(sup * PT_CM, 1),
        "inferior": round((alto - inf) * PT_CM, 1),
        "izquierdo": round(izq * PT_CM, 1),
        "derecho": round((ancho - der) * PT_CM, 1),
    }
    salida["encabezado"] = " / ".join(cab)[:120]
    salida["pie"] = " / ".join(pie)[:120]

    letras = Counter()
    for s, _l, _b in base:
        e = _estilo(s)
        clave = "%s %.1f pt%s" % (
            _familia(s["font"]),
            s["size"],
            (" " + "+".join(sorted(e - {"superindice"}))) if e - {"superindice"} else "",
        )
        letras[clave] += len(s["text"])
    total = sum(letras.values()) or 1
    salida["letra"] = [(k, round(100 * v / total)) for k, v in letras.most_common(4)]

    # Interlineado: paso entre lineas CONSECUTIVAS de un mismo bloque (la moda);
    # el salto entre parrafos no es interlineado (medir_pdf lo confundia).
    lineas = []
    for b in bloques:
        for l in b["lines"]:
            t = "".join(sp["text"] for sp in l["spans"]).strip()
            if t and not es_margen(l):
                tam = max((sp["size"] for sp in l["spans"] if sp["text"].strip()), default=0)
                lineas.append((l["bbox"], tam))
    lineas.sort(key=lambda lt: (round(lt[0][3]), lt[0][0]))
    # Varios «bloques» de PyMuPDF pueden ser una misma linea (tabulaciones): se
    # fusionan las cajas de la misma linea de base.
    fusion = []
    for bb, tam in lineas:
        if fusion and abs(fusion[-1][0][3] - bb[3]) < 2:
            a = fusion[-1][0]
            fusion[-1] = ((min(a[0], bb[0]), min(a[1], bb[1]), max(a[2], bb[2]), max(a[3], bb[3])), max(fusion[-1][1], tam))
        else:
            fusion.append((bb, tam))
    pasos = [
        round(c[0][3] - a[0][3], 1)
        for a, c in zip(fusion, fusion[1:])
        if 0 < c[0][3] - a[0][3] < 40 and abs(a[1] - c[1]) < 0.6
    ]
    paso = statistics.mode(pasos) if pasos else None
    if paso:
        cuerpo_pt = statistics.median([t for _b, t in fusion]) or 1
        salida["interlineado"] = "%.1f pt (%.2f x la letra)" % (paso, paso / cuerpo_pt)
    # Parrafos: lineas seguidas al paso del interlineado y con la misma letra.
    parrafos, actual = [], []
    for bb, tam in fusion:
        if actual and (
            not paso
            or bb[3] - actual[-1][0][3] > paso * 1.35
            or abs(tam - actual[-1][1]) > 0.6
        ):
            parrafos.append(actual)
            actual = []
        actual.append((bb, tam))
    if actual:
        parrafos.append(actual)
    alineaciones = Counter()
    sangrias = 0
    for par in parrafos:
        cajas = [bb for bb, _t in par]
        alineaciones[_alineacion(cajas, izq, der)] += 1
        if len(cajas) > 1 and cajas[0][0] - cajas[1][0] > 10:
            sangrias += 1
    salida["parrafos"] = dict(alineaciones)
    salida["sangria_primera_linea"] = sangrias

    def muestras(cond, n=6):
        vistos = []
        for s, _l, _b in base:
            t = s["text"].strip()
            if cond(s) and t and t not in vistos:
                vistos.append(t[:40])
            if len(vistos) >= n:
                break
        return vistos

    salida["negritas"] = muestras(lambda s: "negrita" in _estilo(s))
    salida["cursivas"] = muestras(lambda s: "cursiva" in _estilo(s), 4)
    salida["color"] = muestras(lambda s: s.get("color", 0) not in (0, 0x000000) and s.get("color", 0) < 0xF0F0F0, 4)

    # Subrayado y resaltado: trazos y rellenos del dibujo bajo el texto.
    subr, resal = [], []
    try:
        dibujos = pagina.get_drawings()
    except Exception:
        dibujos = []
    for dib in dibujos:
        r = dib.get("rect")
        if r is None:
            continue
        horizontal = r.height < 1.6 and r.width > 8
        relleno = dib.get("fill")
        for s, l, _b in base:
            sb = s["bbox"]
            if horizontal and abs(r.y0 - sb[3]) < 3 and r.x0 < sb[2] and r.x1 > sb[0]:
                subr.append(s["text"].strip()[:40])
                break
            if relleno and relleno != (1, 1, 1) and r.height > 4 and r.contains(((sb[0] + sb[2]) / 2, (sb[1] + sb[3]) / 2)):
                resal.append(s["text"].strip()[:40])
                break
    salida["subrayados"] = list(dict.fromkeys(subr))[:6]
    salida["resaltados"] = list(dict.fromkeys(resal))[:6]
    return salida


def medir(pdf: Path) -> list[dict]:
    import fitz  # PyMuPDF: objetos del PDF, no OCR

    with fitz.open(str(pdf)) as doc:
        vistas: Counter = Counter()
        for p in doc:
            cab, pie = lineas_de_margen(p)
            vistas.update({_norm_linea(t) for t in cab + pie})
        umbral = max(2, (doc.page_count + 1) // 2)
        repetidas = {t for t, n in vistas.items() if n >= umbral} if doc.page_count > 1 else set()
        return [formato_pagina(p, repetidas) for p in doc]


def _md_pagina(nombre: str, f: dict) -> str:
    l = ["### %s — página %d — %s" % (nombre, f["pagina"], f["tamano"])]
    if f.get("rotacion"):
        l.append("- Rotada %d°" % f["rotacion"])
    if f.get("escaneada") is not None:
        l.append("- **Sin capa de texto (escaneada o imagen): el formato se lee solo en la captura.**")
    else:
        m = f["margenes_cm"]
        l.append(
            "- Letra: %s" % "; ".join("%s (%d %%)" % (k, v) for k, v in f["letra"])
        )
        l.append(
            "- Encuadre del texto: sup %.1f · inf %.1f · izq %.1f · der %.1f cm"
            % (m["superior"], m["inferior"], m["izquierdo"], m["derecho"])
        )
        if f.get("interlineado"):
            l.append("- Interlineado: %s" % f["interlineado"])
        if f["parrafos"]:
            l.append(
                "- Párrafos: %s%s"
                % (
                    ", ".join("%d %s" % (v, k) for k, v in sorted(f["parrafos"].items(), key=lambda kv: -kv[1])),
                    "; %d con sangría de primera línea" % f["sangria_primera_linea"] if f["sangria_primera_linea"] else "",
                )
            )
        l.append("- Encabezado: %s" % (f["encabezado"] or "—"))
        l.append("- Pie: %s" % (f["pie"] or "—"))
        for clave, rotulo in (("negritas", "Negritas"), ("subrayados", "Subrayados"), ("cursivas", "Cursivas"), ("color", "Texto en color"), ("resaltados", "Resaltados")):
            if f.get(clave):
                l.append("- %s: %s" % (rotulo, " · ".join("«%s»" % t for t in f[clave])))
    if f["imagenes"]:
        l.append(
            "- Imágenes: %s"
            % "; ".join("%s cm %s%s" % (i["cm"], i["posicion"], " (página completa)" if i["area"] > 0.6 else "") for i in f["imagenes"][:6])
        )
    if f["campos_de_firma"]:
        l.append("- Campo de firma digital: %s" % ", ".join(f["campos_de_firma"]))
    if f["anotaciones"]:
        l.append("- Anotaciones: %s" % ", ".join("%s %d" % kv for kv in f["anotaciones"].items()))
    return "\n".join(l)


def escribir(carpeta: Path) -> Path | None:
    pdfs = sorted(carpeta.glob("*.pdf"))
    if not pdfs:
        return None
    partes = [
        "# Formato de cada página del expediente (v3.1)",
        "",
        "Medido en la **estructura del PDF** (objetos de texto; cero OCR). Complementa la",
        "lectura de las capturas: lo que aquí no aparece se mira en `_paginas/`. Una",
        "página escaneada no tiene capa de texto: su formato se describe con la vista.",
        "",
    ]
    for pdf in pdfs:
        try:
            paginas = medir(pdf)
        except Exception as exc:  # PDF ilegible: se informa, no se inventa
            partes.append("### %s\n- No se pudo medir: %s\n" % (pdf.name, exc))
            continue
        for f in paginas:
            partes.append(_md_pagina(pdf.name, f))
            partes.append("")
    destino = carpeta / "_FORMATO.md"
    destino.write_text("\n".join(partes), encoding="utf-8")
    return destino


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    ruta = Path(argv[1])
    if ruta.is_dir():
        print(escribir(ruta))
        return 0
    for f in medir(ruta):
        print(_md_pagina(ruta.name, f))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
