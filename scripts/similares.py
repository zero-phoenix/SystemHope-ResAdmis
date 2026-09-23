#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Las 10 plantillas modelo MAS SIMILARES a la denuncia (mandato del instructor, 23/09/2026).

Obligatorio antes de redactar. El agente describe el caso en `<carpeta>/_CASO.json`
(lo que leyo en las paginas, no lo que supone). Fechas de los escritos de parte =
fecha de su FIRMA DIGITAL (mesa de partes virtual o presencial); denunciados =
los DEFINITIVOS tras la resolucion de requerimiento y el escrito que la absuelve:

    {
      "resolucion": 2,
      "carpeta_origen": "C:/Users/.../Expedientes/2898-2026",
      "traslado": null,
      "escritos": [{"tipo": "denuncia", "fecha": "12 de agosto de 2026"},
                   {"tipo": "subsanacion", "fecha": "22 de setiembre de 2026"}],
      "rama": "01_seguro_vehicular",
      "denunciante_clase": "mujer",
      "denunciados": [{"nombre": "Empresa de Creditos ...", "tipo": "financiera"},
                      {"nombre": "La Positiva Seguros ...", "tipo": "aseguradora"}],
      "subtipos": [],
      "conductas": [
        {"proveedor": "Santander", "texto": "no informo oportunamente el fin de vigencia de la poliza vehicular",
         "norma": "art.1|art.2|lit.b|num.1"},
        {"proveedor": "La Positiva", "texto": "nego la cobertura del siniestro del 15 de mayo de 2026",
         "norma": "art.18|art.19"}
      ]
    }

`carpeta_origen`: donde el usuario tiene los documentos; `entregar` copia alli
el Word. `traslado`: null si la denuncia se presento en CC1 (entonces NINGUNA
nota al pie sobre su presentacion); si llego derivada y el usuario entrego el
documento: {"documento": "MEMORANDUM 001950-2025-PS1/INDECOPI", "fecha":
"3 de setiembre de 2025", "recibida": "3 de setiembre de 2025"}. Caso
particular (desacumulacion, Hoja de Tramite): ademas "nota" con el texto literal
en la forma de las plantillas, que debe contener documento, fecha y recibida.

`norma` es opcional: la norma de docs/tabla_tipificacion.json que el agente
propone para esa conducta; si se da, pesa la coincidencia de norma.

El script puntua las 574 plantillas del indice v3 por:
  imputaciones (similitud del texto de cada conducta con las imputaciones de la
  plantilla, 40 %), numero y tipo de denunciados (25 %), rama (15 %), clase de
  denunciante (5 %), subtipo (5 %) y calidad (apta como base, 10 %);
y escribe `<carpeta>/_SIMILARES.md` con las 10 primeras, el desglose del
puntaje y, por cada conducta del caso, la imputacion de la plantilla que mas se
le parece (norma + texto). La columna «Por que» la escribe el agente: sin ella,
`admisorio.py entregar` no entrega.

Uso:
    python scripts/similares.py <carpeta_del_caso> [--top 10]
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
import zipfile
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import catalogar_imputaciones as CI  # noqa: E402

INDICE = RAIZ / "docs" / "plantillas_maestras_index.json"
VACIAS = set(
    "a al ante bajo con contra de del desde el en entre hacia hasta la las lo los para por segun sin sobre tras y o u e que se su sus un una unos unas es fue ha habria habrian no mas como le les dicho dicha este esta ese esa cual cuales donde cuando".split()
)


SINONIMOS = {
    "deneg": "negar",
    "negad": "negar",
    "nego": "negar",
    "negar": "negar",
    "negat": "negar",
    "rechaz": "negar",
    "recha": "negar",
    "infor": "inform",
    "comun": "inform",
    "comuni": "inform",
    "avisa": "inform",
    "notif": "inform",
    "reclam": "reclam",
    "queja": "reclam",
    "respue": "respue",
    "atend": "atenc",
    "atenc": "atenc",
    "cobert": "cobert",
    "sinies": "sinies",
    "accide": "sinies",
    "choque": "sinies",
    "poliza": "poliza",
    "seguro": "seguro",
    "vigenc": "vigenc",
    "vencim": "vigenc",
    "vencio": "vigenc",
    "venci": "vigenc",
    "termin": "vigenc",
    "entreg": "entreg",
    "remiti": "entreg",
    "envio": "entreg",
    "copia": "entreg",
    "cobro": "cobro",
    "cobrad": "cobro",
    "cargos": "cobro",
    "cuota": "cuota",
    "prima": "cuota",
    "primas": "cuota",
    "anula": "anula",
    "resolv": "anula",
    "cancel": "anula",
    "renova": "renova",
    "credit": "credit",
    "financ": "credit",
    "prest": "credit",
}


def normalizar(t: str) -> list[str]:
    t = "".join(
        c
        for c in unicodedata.normalize("NFD", t.lower())
        if unicodedata.category(c) != "Mn"
    )
    salida = []
    for w in re.findall(r"[a-z]{3,}", t):
        if w in VACIAS:
            continue
        r = w[:6]
        salida.append(SINONIMOS.get(r, SINONIMOS.get(w[:5], r)))
    return salida


def imputaciones_de(ruta: Path) -> list[tuple[str, str]]:
    with zipfile.ZipFile(ruta) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    salida = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", xml, re.S):
        t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", p)).strip()
        if re.match(r"Presunta infracci", t, re.I):
            norma = "|".join(CI.normas_de(re.split(r"\sen tanto\s", t, 1)[0]))
            conducta = t.split(" en tanto ", 1)[1] if " en tanto " in t else t
            salida.append((norma, conducta))
    return salida


def _plano(t: str) -> str:
    t = "".join(
        c
        for c in unicodedata.normalize("NFD", t.upper())
        if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"\s+", " ", t).strip()


class Tfidf:
    def __init__(self, documentos: list[list[str]]):
        self.n = len(documentos)
        self.df = Counter(tok for d in documentos for tok in set(d))

    def idf(self, t: str) -> float:
        return math.log((1 + self.n) / (1 + self.df.get(t, 0)))

    def vector(self, toks: list[str]) -> set:
        return set(toks)

    def cobertura(self, caso: set, plantilla: set) -> float:
        """Parte (ponderada por rareza) de la conducta del caso presente en la imputacion."""
        total = sum(self.idf(t) for t in caso) or 1.0
        return sum(self.idf(t) for t in caso & plantilla) / total


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("carpeta")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument(
        "--forzar", action="store_true", help="rehacer aunque ya este justificado"
    )
    a = ap.parse_args(argv)
    carpeta = Path(a.carpeta).resolve()
    caso_p = carpeta / "_CASO.json"
    if not caso_p.exists():
        print(
            "Falta %s. Describe el caso (ver el docstring: python scripts/similares.py -h)."
            % caso_p
        )
        return 2
    caso = json.loads(caso_p.read_text(encoding="utf-8"))
    previo = carpeta / "_SIMILARES.md"
    if previo.exists() and not a.forzar and not justificacion_completa(carpeta):
        print("_SIMILARES.md ya esta justificado: no se sobrescribe (usa --forzar).")
        return 0
    fichas = json.loads(INDICE.read_text(encoding="utf-8"))
    imps = {
        f["ruta_relativa"]: imputaciones_de(RAIZ / f["ruta_relativa"]) for f in fichas
    }
    docs = [normalizar(c) for lista in imps.values() for _n, c in lista]
    modelo = Tfidf(docs)
    conductas = [
        (
            c.get("proveedor", ""),
            c["texto"],
            modelo.vector(normalizar(c["texto"])),
            c.get("norma", ""),
        )
        for c in caso.get("conductas", [])
    ]
    n_caso = len(caso.get("denunciados", []))
    tipos_caso = sorted(d.get("tipo", "") for d in caso.get("denunciados", []))
    resultados = []
    for f in fichas:
        vec_imps = [
            (n, c, modelo.vector(normalizar(c))) for n, c in imps[f["ruta_relativa"]]
        ]
        pares = []
        for prov, texto, v, norma_caso in conductas:
            candidatos = []
            for n, c, vi in vec_imps:
                cob = modelo.cobertura(v, vi)
                if norma_caso:
                    cob = cob * (1.0 if n == norma_caso else 0.5) + (
                        0.25 if n == norma_caso else 0.0
                    )
                candidatos.append((min(cob, 1.0), n, c))
            pares.append((prov, texto, max(candidatos, default=(0.0, "", ""))))
        s_imp = sum(p[2][0] for p in pares) / max(1, len(pares))
        n_f = f.get("denunciados", {}).get("n", 0)
        tipos_f = sorted(d["tipo"] for d in f.get("denunciados", {}).get("detalle", []))
        s_n = 1.0 if n_f == n_caso else (0.5 if min(n_f, 3) == min(n_caso, 3) else 0.0)
        comunes = sum((Counter(tipos_f) & Counter(tipos_caso)).values())
        s_tipos = comunes / max(1, len(tipos_caso))
        s_rama = 1.0 if f["rama"] == caso.get("rama") else 0.0
        s_clase = (
            1.0
            if f.get("denunciantes", {}).get("clase") == caso.get("denunciante_clase")
            else 0.0
        )
        s_sub = (
            1.0
            if sorted(f.get("subtipos", [])) == sorted(caso.get("subtipos", []))
            else 0.0
        )
        s_apta = 1.0 if f.get("apta_como_base") else 0.0
        alias = [
            _plano(d.get("alias", ""))
            for d in f.get("denunciados", {}).get("detalle", [])
        ]
        nombres = [_plano(d.get("nombre", "")) for d in caso.get("denunciados", [])]
        s_prov = sum(1 for nm in nombres if any(al and al in nm for al in alias)) / max(
            1, len(nombres)
        )
        total = (
            0.40 * s_imp
            + 0.15 * s_n
            + 0.05 * s_tipos
            + 0.10 * s_prov
            + 0.15 * s_rama
            + 0.05 * s_clase
            + 0.05 * s_sub
            + 0.05 * s_apta
        )
        resultados.append(
            (
                total,
                f,
                {
                    "imputaciones": s_imp,
                    "n_denunciados": s_n,
                    "tipos": s_tipos,
                    "rama": s_rama,
                    "proveedores": s_prov,
                    "denunciante": s_clase,
                    "subtipo": s_sub,
                    "apta": s_apta,
                },
                pares,
            )
        )
    resultados.sort(key=lambda r: -r[0])
    top = resultados[: a.top]

    L = [
        "# Las %d plantillas más similares — %s" % (a.top, carpeta.name),
        "",
        "Generado por `scripts/similares.py` desde `_CASO.json`. Pesos: imputaciones 40 %, número de denunciados 15 %, rama 15 %, mismos proveedores 10 %, tipos 5 %, denunciante 5 %, subtipo 5 %, apta 5 %.",
        "**El agente completa la columna «Por qué» de cada fila** (qué imputaciones, hechos y partes coinciden o difieren y qué se tomará de ella). Sin eso, `entregar` no entrega.",
        "",
        "| # | Plantilla | Puntaje | Imput. | N ddos | Tipos | Rama | Denunc. | Apta | Por qué |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for i, (t, f, s, _p) in enumerate(top, 1):
        L.append(
            "| %d | %s | %.2f | %.2f | %s | %.2f | %s | %s | %s |  |"
            % (
                i,
                f["archivo"],
                t,
                s["imputaciones"],
                f.get("denunciados", {}).get("n", "?"),
                s["tipos"],
                "sí" if s["rama"] else "no",
                f.get("denunciantes", {}).get("clase", "?"),
                "sí" if s["apta"] else "no",
            )
        )
    L += [
        "",
        "## Imputación de cada plantilla más parecida a cada conducta del caso",
        "",
    ]
    for i, (_t, f, _s, pares) in enumerate(top, 1):
        L.append("### %d. %s" % (i, f["archivo"]))
        for prov, texto, (sim, norma, cond) in pares:
            L.append(
                "- Caso [%s] «%s» → `%s` (similitud %.2f): «%s»"
                % (prov, texto[:140], norma or "—", sim, cond[:260])
            )
        L.append("")
    (carpeta / "_SIMILARES.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[: 7 + a.top]))
    print(
        "\nEscrito %s. Completa la columna «Por qué» de las %d filas."
        % (carpeta / "_SIMILARES.md", a.top)
    )
    return 0


def justificacion_completa(carpeta: Path, minimo: int = 10) -> list[str]:
    """Para `entregar`: exige _SIMILARES.md con `minimo` filas y su «Por qué»."""
    p = carpeta / "_SIMILARES.md"
    if not p.exists():
        return [
            "falta _SIMILARES.md: ejecuta scripts/similares.py y justifica las 10 plantillas"
        ]
    filas = [
        l
        for l in p.read_text(encoding="utf-8").splitlines()
        if re.match(r"\|\s*\d+\s*\|", l)
    ]
    vacias = [
        l.split("|")[2].strip()
        for l in filas
        if len(l.split("|")) < 12 or len(l.split("|")[10].strip()) < 25
    ]
    fallos = []
    if len(filas) < minimo:
        fallos.append(
            "_SIMILARES.md tiene %d plantillas; se exigen %d" % (len(filas), minimo)
        )
    if vacias:
        fallos.append(
            "_SIMILARES.md sin justificacion suficiente en: %s" % ", ".join(vacias[:4])
        )
    return fallos


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
