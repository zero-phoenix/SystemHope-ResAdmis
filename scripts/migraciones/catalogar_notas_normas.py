#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Catalogo de notas al pie normativas, sacado del corpus (docs/notas_normas.json).

En la considerativa, cada calificacion («... tipificado en el numeral 88.1 del
artículo 88 del Código») lleva una nota que transcribe la norma. Cuando el agente
AÑADE una imputacion (construir_admisorio, `insertar_despues`), el parrafo nuevo
necesita esa misma nota. Aqui se guarda, por cada norma citada, la nota mas
frecuente del corpus (XML de sus parrafos, ya con la tipografia uniforme).

Uso:
    python scripts/migraciones/catalogar_notas_normas.py
"""

from __future__ import annotations

import collections
import json
import re
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
RE_P = re.compile(r"<w:p\b[^>]*>.*?</w:p>", re.S)
RE_T = re.compile(r"<w:t(?:\s[^>/]*)?>([^<]*)</w:t>")
RE_FN = re.compile(r'<w:footnote\b[^>]*w:id="(\d+)"[^>]*>(.*?)</w:footnote>', re.S)
RE_CITA = re.compile(
    r"tipificad[oa]s? en (?:el |la |los |las )?(.{6,140}?) del Código\s*\[\[N(\d+)\]\]"
)


def main() -> int:
    cuenta: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter
    )
    for ruta in sorted((RAIZ / "plantillas_maestras").rglob("*.docx")):
        with zipfile.ZipFile(ruta) as z:
            x = z.read("word/document.xml").decode("utf-8", "replace")
            fx = z.read("word/footnotes.xml").decode("utf-8", "replace")
        notas = {i: c for i, c in RE_FN.findall(fx)}
        for p in RE_P.findall(x):
            marcado = re.sub(
                r'<w:footnoteReference\b[^>]*w:id="(\d+)"[^>]*/>',
                lambda m: "<w:t>[[N%s]]</w:t>" % m.group(1),
                p,
            )
            texto = "".join(RE_T.findall(marcado))
            for m in RE_CITA.finditer(texto):
                cuerpo = notas.get(m.group(2))
                if cuerpo and "<w:footnoteRef" in cuerpo:
                    frase = re.sub(r"\s+", " ", m.group(1)).strip()
                    cuenta[frase][cuerpo] += 1
    salida = {
        frase: {"veces": sum(c.values()), "xml": c.most_common(1)[0][0]}
        for frase, c in cuenta.items()
        if sum(c.values()) >= 3
    }
    (RAIZ / "docs/notas_normas.json").write_text(
        json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    for frase, v in sorted(salida.items(), key=lambda kv: -kv[1]["veces"])[:25]:
        print("%5d  %s" % (v["veces"], frase))
    print("%d normas catalogadas en docs/notas_normas.json" % len(salida))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
