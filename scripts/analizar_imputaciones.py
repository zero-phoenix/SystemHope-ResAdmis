#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Catalogo ANALITICO de imputaciones: como se redactan, por que, y que no hacer.

Para cada norma de `docs/tabla_tipificacion.json` mide sobre las plantillas:

  - la forma literal canonica en la considerativa ("... corresponde calificar el
    hecho materia de denuncia como una presunta infraccion al deber de X,
    tipificado en ... del Codigo") y en el resolutivo ("Presunta infraccion a ...
    de la Ley 29571, Codigo de Proteccion y Defensa del Consumidor, en tanto ...");
  - el fundamento (titulo del articulo en el Codigo, leido de normas/);
  - quien es el sujeto de la imputacion y en que forma (nombre, alias, "los
    proveedores denunciados"...), cruzado con el numero real de denunciados;
  - las conductas (verbo en condicional) y ejemplos literales;
  - las VARIANTES MINORITARIAS: lo que aparece en el corpus pero no se debe
    copiar, con su frecuencia. Es la lista de "que no hacer".

Salidas: docs/catalogo_imputaciones.json y docs/IMPUTACIONES_ANALITICO.md.

Uso:
    python scripts/analizar_imputaciones.py
"""

from __future__ import annotations

import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import catalogar_imputaciones as CI  # noqa: E402

TABLA = RAIZ / "docs" / "tabla_tipificacion.json"
SALIDA_JSON = RAIZ / "docs" / "catalogo_imputaciones.json"
SALIDA_MD = RAIZ / "docs" / "IMPUTACIONES_ANALITICO.md"
CODIGO_PDF = RAIZ / "normas" / "codigo proteccion consumidor.pdf"

RE_CONS = re.compile(
    r"considera que el hecho denunciado, consistente en que (?P<hecho>.+?)"
    r"(?:;? involucrar[ií]a (?P<inv>.+?))?\.\s*Por consiguiente, corresponde calificar el hecho materia de "
    r"denuncia como una presunta infracci[oó]n (?P<norma>.+?)(?:\[\^?\d+\]|\s*\.\s|$)",
    re.I,
)
RE_RES = re.compile(
    r"^Presunta infracci[oó]n (?P<norma>.+?),?\s+en tanto (?P<suj>.+?)\s+(?P<neg>no\s+)?habr[ií]a(?P<pl>n)?\s+(?P<conducta>.+)$",
    re.I,
)
LEY = "de la Ley 29571, Código de Protección y Defensa del Consumidor"

FUNDAMENTO_MANUAL = {
    "art.1|art.2|lit.b|num.1": "Derecho a acceder a informacion oportuna, suficiente, veraz y facilmente accesible (art. 1, numeral 1, literal b) y deber de informacion relevante (art. 2).",
    "art.18|art.19": "Deber de idoneidad: correspondencia entre lo que el consumidor espera y lo que recibe (art. 18) y responsabilidad del proveedor por ella (art. 19).",
}


def admite(clave: str, admitidas: list[str]) -> str | None:
    """Devuelve la norma admitida (con comodin lit.*) que cubre `clave`, o None."""
    if clave in admitidas:
        return clave
    partes = clave.split("|")
    for a in admitidas:
        if "lit.*" not in a:
            continue
        fijas = [x for x in a.split("|") if x != "lit.*"]
        resto = [x for x in partes if x not in fijas]
        if (
            all(x in partes for x in fijas)
            and resto
            and all(x.startswith("lit.") for x in resto)
        ):
            return a
    return None


def titulos_codigo() -> dict[str, str]:
    try:
        import fitz
    except ImportError:
        return {}
    try:
        texto = "".join(p.get_text() for p in fitz.open(str(CODIGO_PDF)))
    except Exception:
        return {}
    salida = {}
    for m in re.finditer(r"Art[ií]culo (\d+)\.-\s*([^\n]{3,120})", texto):
        salida.setdefault(m.group(1), m.group(2).strip())
    return salida


def parrafos(ruta: Path) -> list[str]:
    with zipfile.ZipFile(ruta) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    return [
        re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", p)).strip()
        for p in re.findall(r"<w:p[ >].*?</w:p>", xml, re.S)
    ]


def n_denunciados(ps: list[str]) -> int:
    i = next(
        (k for k, t in enumerate(ps[:25]) if re.match(r"DENUNCIAD", t, re.I)), None
    )
    if i is None:
        return 0
    j = next(
        (
            k
            for k in range(i + 1, min(len(ps), 30))
            if re.match(r"MATERIA", ps[k], re.I)
        ),
        i + 1,
    )
    bloque = re.sub(r"(?i)^DENUNCIAD[OA]S?\s*(\(S\))?\s*:?", "", "\n".join(ps[i:j]))
    return len(re.findall(r"\([^)]*\)", bloque))


def tipo_sujeto(suj: str) -> str:
    s = suj.strip()
    low = s.lower()
    if low.startswith("los proveedores denunciados"):
        return "«los proveedores denunciados»"
    if low.startswith(("el proveedor denunciado", "la proveedora denunciada")):
        return "«el proveedor denunciado»"
    if low.startswith(
        (
            "la compañía aseguradora",
            "la aseguradora",
            "la entidad financiera",
            "el banco",
            "la entidad bancaria",
        )
    ):
        return "genérico («la compañía aseguradora», «el banco»…)"
    if re.search(r"\sy\s+(?:el |la |al )?[A-ZÁÉÍÓÚ]", s) and not re.search(
        r"(?i)seguros y reaseguros$", s
    ):
        return "dos proveedores nombrados"
    if s[:1].isupper():
        return "proveedor nombrado"
    return "otro"


def main() -> int:
    tabla = json.loads(TABLA.read_text(encoding="utf-8"))
    admitidas = tabla["normas_admitidas"]
    hechos_por_norma = defaultdict(list)
    for h in tabla["hechos"]:
        for k in h["normas"]:
            hechos_por_norma[k].append(h["hecho"])
    titulos = titulos_codigo()

    datos = {
        k: {
            "res": 0,
            "cons": 0,
            "aperturas": Counter(),
            "deberes": Counter(),
            "sujetos": Counter(),
            "sujetos_por_n": Counter(),
            "conductas": Counter(),
            "ejemplos": [],
            "sin_ley": 0,
            "sin_condicional": 0,
            "yo": 0,
        }
        for k in admitidas
    }
    fuera = Counter()
    fuera_ej = {}
    plantillas = sorted(
        p
        for p in (RAIZ / "plantillas_maestras").rglob("*")
        if p.suffix.lower() == ".docx"
    )
    for ruta in plantillas:
        ps = parrafos(ruta)
        n = n_denunciados(ps)
        texto = " ".join(ps)
        for m in RE_CONS.finditer(texto):
            clave = "|".join(CI.normas_de(m.group("norma")))
            k = admite(clave, admitidas)
            if not k:
                continue
            d = datos[k]
            d["cons"] += 1
            deber = re.split(r",?\s*tipificad[oa]", m.group("norma"), 1)[0].strip()
            d["deberes"][re.sub(r"\s+", " ", deber)[:200]] += 1
        for p in ps:
            if not re.match(r"Presunta infracci", p, re.I):
                continue
            clave = "|".join(CI.normas_de(re.split(r"\sen tanto\s", p, 1)[0]))
            k = admite(clave, admitidas)
            if not k:
                fuera[clave] += 1
                fuera_ej.setdefault(clave, p[:220])
                continue
            d = datos[k]
            d["res"] += 1
            m = RE_RES.match(p)
            if LEY not in p:
                d["sin_ley"] += 1
            if " y/o " in p:
                d["yo"] += 1
            if not m:
                d["sin_condicional"] += 1
                continue
            apertura = (
                "Presunta infracción "
                + re.sub(r"\s+", " ", m.group("norma")).strip()
                + ", en tanto"
            )
            d["aperturas"][apertura] += 1
            t = tipo_sujeto(m.group("suj"))
            d["sujetos"][t] += 1
            d["sujetos_por_n"][
                ("1" if n == 1 else "2" if n == 2 else "3+" if n > 2 else "?")
                + " denunciado(s) → "
                + t
            ] += 1
            verbo = " ".join(m.group("conducta").split()[:4])
            d["conductas"][
                ("no " if m.group("neg") else "")
                + "habría"
                + ("n" if m.group("pl") else "")
                + " "
                + verbo
            ] += 1
            if len(d["ejemplos"]) < 4 and 120 < len(p) < 420:
                d["ejemplos"].append(p)

    catalogo = {
        "fuente": "Medido sobre %d plantillas por scripts/analizar_imputaciones.py; normas de docs/tabla_tipificacion.json."
        % len(plantillas),
        "regla": tabla["regla"],
        "normas_admitidas": admitidas,
        "normas_en_consulta": [],
        "patrones": tabla.get("patrones", {}),
        "normas": {},
        "combinaciones_fuera_de_tabla": [
            {"normas": k, "frecuencia": v, "ejemplo": fuera_ej[k]}
            for k, v in fuera.most_common()
        ],
    }
    for k, d in datos.items():
        arts = sorted(
            {x.split(".")[1] for x in k.split("|") if x.startswith("art.")}, key=int
        )
        fundamento = FUNDAMENTO_MANUAL.get(k) or "; ".join(
            "art. %s: %s" % (a, titulos.get(a, "?")) for a in arts
        )
        canon = d["aperturas"].most_common(1)[0][0] if d["aperturas"] else None
        variantes = [
            {"forma": a, "frecuencia": v} for a, v in d["aperturas"].most_common()[1:8]
        ]
        no_hacer = [v for v in variantes]
        catalogo["normas"][k] = {
            "hechos_de_la_tabla": hechos_por_norma[k],
            "fundamento": fundamento,
            "frecuencia": {"resolutivo": d["res"], "considerativa": d["cons"]},
            "considerativa_canonica": d["deberes"].most_common(1)[0][0]
            if d["deberes"]
            else None,
            "considerativa_variantes": [
                {"forma": a, "frecuencia": v}
                for a, v in d["deberes"].most_common()[1:6]
            ],
            "resolutivo_apertura_canonica": canon,
            "no_usar_aperturas_minoritarias": no_hacer,
            "sujetos": dict(d["sujetos"].most_common()),
            "sujetos_segun_numero_de_denunciados": dict(
                d["sujetos_por_n"].most_common()
            ),
            "conductas_frecuentes": [
                {"conducta": c, "frecuencia": v}
                for c, v in d["conductas"].most_common(12)
            ],
            "defectos_medidos": {
                "sin_'de la Ley 29571, Codigo...'": d["sin_ley"],
                "sin_condicional": d["sin_condicional"],
                "con_'y/o'": d["yo"],
            },
            "ejemplos": d["ejemplos"],
        }
    SALIDA_JSON.write_text(
        json.dumps(catalogo, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    SALIDA_MD.write_text(markdown(catalogo), encoding="utf-8")
    SKILL.parent.mkdir(parents=True, exist_ok=True)
    SKILL.write_text(skill(catalogo), encoding="utf-8")
    usadas = sum(
        1 for v in catalogo["normas"].values() if v["frecuencia"]["resolutivo"]
    )
    print(
        "Catalogo analitico: %d normas admitidas (%d con uso en el corpus), %d combinaciones fuera de tabla."
        % (len(admitidas), usadas, len(fuera))
    )
    return 0


SKILL = RAIZ / ".agents" / "skills" / "imputaciones" / "SKILL.md"
LIMITE = 12000


def skill(c: dict) -> str:
    """SKILL.md de Antigravity (< 12 000 caracteres), generado de las cifras."""
    L = [
        "---",
        "name: imputaciones",
        "description: Redactar y verificar las imputaciones de cargos (considerativa y resolutivo PRIMERO) de un admisorio CC1 de Indecopi, eligiendo la norma de la tabla del instructor y la forma literal de las plantillas.",
        "---",
        "",
        "# Imputaciones de cargos (generado por scripts/analizar_imputaciones.py; no editar a mano)",
        "",
        "## Reglas",
        "- **Mandan las plantillas** (v3.2): se imputa como las plantillas imputan un hecho de igual **sentido y finalidad**, en su forma literal; `docs/tabla_tipificacion.json` es **referencial** y nunca se imputa una norma que las plantillas no usan para ese hecho. Nunca art. 3. Art. 24 solo si el proveedor NO está regulado por el sistema financiero; si lo está, numeral 88.1 del art. 88.",
        "- Cláusulas abusivas: SIEMPRE «numeral 49.1 del artículo 49 y al literal x) del artículo 50» (ineficacia absoluta) o «... del artículo 51» (ineficacia relativa).",
        "- Documentos contractuales: a la FIRMA → literal e) del art. 47. DESPUÉS, cuando el consumidor los pide → art. 1, numeral 1, literal b) y art. 2.",
        "- Solicitud de GESTIÓN mal atendida → idoneidad (arts. 18 y 19). Solicitud de INFORMACIÓN o copias → información. Si la misma carta tiene ambas, dos imputaciones separadas.",
        "- **Una imputación por cada solicitud y por cada cobertura diferenciada**, aunque se hayan pedido en una misma solicitud (Exp. 3092-2026: gastos de sepelio y oncológica pedidas el 1 y el 23 de marzo → cuatro imputaciones). Si el expediente no precisa la cobertura: «coberturas». Nunca «pese a sus solicitudes del 1 y el 23 de marzo» ni «la cobertura de sepelio y la cobertura oncológica» en un núcleo (R-206).",
        "- Núcleo sin palabras valorativas («únicamente», «totalmente», «pésimo»; R-203).",
        "- Considerativa: «… considera que el hecho denunciado, consistente en que [HECHO en condicional]. Por consiguiente, corresponde calificar el hecho materia de denuncia como una presunta infracción al deber de …, tipificado en … del Código».",
        "- **Información (R-207)**: la considerativa cierra el hecho con «; involucraría una presunta afectación al derecho de información de los consumidores. Por consiguiente, …»; el resolutivo, no.",
        "- Resolutivo: «Presunta infracción a [NORMA] de la Ley 29571, Código de Protección y Defensa del Consumidor, en tanto [SUJETO] habría(n) [CONDUCTA] [PRODUCTO] [FECHA/CIRCUNSTANCIA].» Una oración, una conducta.",
        "- Sujeto (R-188, instructor 24/09/2026), idéntico en la considerativa y en el resolutivo:",
        "  - aseguradora ÚNICA denunciada: «la compañía aseguradora» (nunca su razón social ni su alias);",
        "  - dos o más denunciados, imputaciones separadas: la **razón social completa** de cada uno (también la aseguradora), nunca el alias;",
        "  - conducta común a todos: «los proveedores denunciados» solo con EXACTAMENTE 2; con 3 o más, los dos nombres completos;",
        "  - «el proveedor denunciado» solo si hay uno;",
        "  - la denunciante o el denunciante: su **nombre completo** («la señora María Pérez Gómez») o «la denunciante», nunca la tratativa corta de los hechos ni «la parte denunciante» (R-205);",
        "  - nunca «aseguradora» a secas: «la compañía aseguradora» (R-201).",
        "- La **primera** calificación de cada artículo termina con la llamada a la nota que transcribe SU norma (`docs/notas_normas.json`); las siguientes imputaciones por el mismo artículo **no repiten la nota** (R-202). El constructor lo aplica.",
        "- Mismo orden, misma norma y mismo núcleo fáctico en considerativa y resolutivo. Nunca «y/o», nunca «inducción a error», nunca «N°».",
        "",
        "## Por norma (forma canónica medida → úsala; variantes → no)",
    ]
    for k, v in sorted(
        c["normas"].items(), key=lambda kv: -kv[1]["frecuencia"]["resolutivo"]
    ):
        if not v["frecuencia"]["resolutivo"]:
            continue
        L.append("")
        L.append("### %s (%d)" % (k, v["frecuencia"]["resolutivo"]))
        L.append(
            "- Considerativa: «presunta infracción %s, tipificado en …»"
            % (v["considerativa_canonica"] or "—")
        )
        L.append("- Resolutivo: «%s …»" % (v["resolutivo_apertura_canonica"] or "—"))
        conductas = "; ".join(x["conducta"] for x in v["conductas_frecuentes"][:4])
        if conductas:
            L.append("- Conductas típicas: " + conductas)
        if v["no_usar_aperturas_minoritarias"]:
            L.append(
                "- NO: "
                + " | ".join(
                    "«%s»" % x["forma"][:110]
                    for x in v["no_usar_aperturas_minoritarias"][:2]
                )
            )
    L += [
        "",
        "Detalle completo, fundamentos y ejemplos: `docs/IMPUTACIONES_ANALITICO.md`.",
    ]
    texto = "\n".join(L) + "\n"
    while len(texto) > LIMITE:  # recorta las normas menos frecuentes, nunca las reglas
        corte = texto.rfind("\n### ", 0, len(texto) - 200)
        texto = (
            texto[:corte] + "\n\nDetalle completo: `docs/IMPUTACIONES_ANALITICO.md`.\n"
        )
    return texto


def markdown(c: dict) -> str:
    L = [
        "# Imputaciones: cómo se redactan, por qué y qué no hacer",
        "",
        "> Generado por `scripts/analizar_imputaciones.py`. " + c["fuente"],
        "> **Documento de consulta.** Si contradice a `AGENTS.md`, manda `AGENTS.md`.",
        "",
        "## Reglas generales (por qué se redacta así)",
        "",
        "1. **Tipicidad** (principio del numeral 4 del artículo 230 del TUO de la LPAG, D.S. 006-2026-JUS): solo es imputable lo que la ley tipifica. Por eso la norma se toma de como las plantillas imputan un hecho de igual sentido y finalidad (la tabla del instructor es referencial) y se cita completa y sin «N°».",
        "2. **Presunción de licitud** (numeral 9 del mismo artículo 230): la conducta **no está probada**. Por eso la imputación va en **condicional** («habría denegado») y los hechos van en pasado, atribuidos a lo que el consumidor señaló.",
        "3. **Imputación concreta.** El administrado se defiende de lo que se le imputa. Por eso **cada imputación**:",
        "   - dice **quién** (el proveedor nombrado, o «los proveedores denunciados» solo si son exactamente dos y la conducta es de ambos);",
        "   - dice **qué conducta**, en una sola oración;",
        "   - dice **sobre qué producto** (póliza, crédito);",
        "   - dice **cuándo** (siniestro, reclamo, fecha).",
        "4. **Isomorfismo.** El hecho que la considerativa califica es el mismo que el resolutivo imputa, en el mismo orden y con la misma norma. Si difieren, el cargo formulado no es el cargo motivado.",
        "5. **Una solicitud mal gestionada es idoneidad; una solicitud de información o de copias es información.** Si una misma carta contiene ambas, se imputan por separado.",
        "6. **Nunca** el artículo 3 ni «inducción a error». **Nunca** «y/o». **Nunca** mezclar dos conductas distintas en una imputación.",
        "",
    ]
    for k, v in c["normas"].items():
        if not v["frecuencia"]["resolutivo"] and not v["frecuencia"]["considerativa"]:
            continue
        L += [
            "## `%s` — %d en el resolutivo, %d en la considerativa"
            % (k, v["frecuencia"]["resolutivo"], v["frecuencia"]["considerativa"]),
            "",
            "- **Hechos de la tabla:** " + " | ".join(v["hechos_de_la_tabla"]),
            "- **Fundamento:** " + v["fundamento"],
            "- **Considerativa (forma canónica):** «… presunta infracción %s, tipificado en …»"
            % (v["considerativa_canonica"] or "—"),
            "- **Resolutivo (apertura canónica):** «%s …»"
            % (v["resolutivo_apertura_canonica"] or "—"),
            "- **Sujeto según el número de denunciados:** "
            + "; ".join(
                "%s (%d)" % (a, b)
                for a, b in list(v["sujetos_segun_numero_de_denunciados"].items())[:6]
            ),
            "- **Conductas más frecuentes:** "
            + "; ".join(
                "%s (%d)" % (x["conducta"], x["frecuencia"])
                for x in v["conductas_frecuentes"][:6]
            ),
        ]
        if v["no_usar_aperturas_minoritarias"]:
            L.append("- **No usar** (variantes minoritarias del corpus):")
            L += [
                "  - «%s» (%d)" % (x["forma"], x["frecuencia"])
                for x in v["no_usar_aperturas_minoritarias"]
            ]
        defectos = {a: b for a, b in v["defectos_medidos"].items() if b}
        if defectos:
            L.append(
                "- **Defectos medidos en el corpus (no copiar):** "
                + ", ".join("%s: %d" % (a, b) for a, b in defectos.items())
            )
        if v["ejemplos"]:
            L.append("- **Ejemplo literal:** " + v["ejemplos"][0])
        L.append("")
    if c["combinaciones_fuera_de_tabla"]:
        L += ["## Combinaciones del corpus FUERA de la tabla (no usar)", ""]
        L += [
            "- `%s` (%d): %s" % (x["normas"], x["frecuencia"], x["ejemplo"][:160])
            for x in c["combinaciones_fuera_de_tabla"][:40]
        ]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
