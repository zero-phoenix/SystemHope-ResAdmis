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
        "- Solo normas de `docs/tabla_tipificacion.json`. Nunca art. 3. Art. 24 solo si el proveedor NO está regulado por el sistema financiero; si lo está, numeral 88.1 del art. 88.",
        "- Cláusulas abusivas: SIEMPRE «numeral 49.1 del artículo 49 y al literal x) del artículo 50» (ineficacia absoluta) o «... del artículo 51» (ineficacia relativa).",
        "- Documentos contractuales: a la FIRMA → literal e) del art. 47. DESPUÉS, cuando el consumidor los pide → art. 1, numeral 1, literal b) y art. 2.",
        "- Solicitud de GESTIÓN mal atendida → idoneidad (arts. 18 y 19). Solicitud de INFORMACIÓN o copias → información. Si la misma carta tiene ambas, dos imputaciones separadas.",
        '- Reclamo ante aseguradora o banco (regulados por la SBS) que pide el sustento de un cobro o incremento y recibe una respuesta sin él → numeral 88.1 del art. 88, UNA imputación por reclamo, con su código y fecha: «habría brindado una respuesta inadecuada al reclamo REC-3094 presentado por la denunciante el 3 de marzo de 2026, al no haberle entregado …». No se duplica como información (Exp. 2889-2026).',
        '- Comunicación remitida a un domicilio en el que el consumidor no reside (notificación deficiente) → idoneidad (arts. 18 y 19), UNA imputación por comunicación y fecha: «no habría cumplido con notificar a la denunciante en su domicilio la comunicación del [fecha] sobre …, al haberla remitido a un domicilio en el que no residía». Nunca información: el corpus lo imputa por idoneidad (TPL_2088_2025: liquidación no notificada al domicilio; TPL_0600_2026: boletas no remitidas al domicilio); información es el CONTENIDO de lo informado, no el lugar de envío (Exp. 2889-2026).',
        "- Considerativa: «… considera que el hecho denunciado, consistente en que [HECHO en condicional]. Por consiguiente, corresponde calificar el hecho materia de denuncia como una presunta infracción al deber de …, tipificado en … del Código».",
        "- Resolutivo: «Presunta infracción a [NORMA] de la Ley 29571, Código de Protección y Defensa del Consumidor, en tanto [SUJETO] habría(n) [CONDUCTA] [PRODUCTO] [FECHA/CIRCUNSTANCIA].» Una oración, una conducta.",
        "- Sujeto: nombre del proveedor; «los proveedores denunciados» solo con EXACTAMENTE 2 denunciados y conducta común; con 3 o más, los dos nombres completos. «El proveedor denunciado» solo si hay uno.",
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
        "1. **Tipicidad** (principio del numeral 4 del artículo 230 del TUO de la LPAG, D.S. 006-2026-JUS): solo es imputable lo que la ley tipifica. Por eso la norma se toma **solo** de la tabla del instructor y se cita completa y sin «N°».",
        "2. **Presunción de licitud** (numeral 9 del mismo artículo 230): la conducta **no está probada**. Por eso la imputación va en **condicional** («habría denegado») y los hechos van en pasado, atribuidos a lo que el consumidor señaló.",
        "3. **Imputación concreta.** El administrado se defiende de lo que se le imputa. Por eso **cada imputación**:",
        "   - dice **quién** (el proveedor nombrado, o «los proveedores denunciados» solo si son exactamente dos y la conducta es de ambos);",
        "   - dice **qué conducta**, en una sola oración;",
        "   - dice **sobre qué producto** (póliza, crédito);",
        "   - dice **cuándo** (siniestro, reclamo, fecha).",
        "4. **Isomorfismo.** El hecho que la considerativa califica es el mismo que el resolutivo imputa, en el mismo orden y con la misma norma. Si difieren, el cargo formulado no es el cargo motivado.",
        "5. **Una solicitud mal gestionada es idoneidad; una solicitud de información o de copias es información.** Si una misma carta contiene ambas, se imputan por separado.",
        "6. **Nunca** el artículo 3 ni «inducción a error». **Nunca** «y/o». **Nunca** mezclar dos conductas distintas en una imputación.",
        '7. **El lugar de envío no es información.** Una comunicación remitida a un domicilio en el que el consumidor no reside es un servicio mal prestado: idoneidad (artículos 18 y 19), una imputación por comunicación y fecha. La información (artículo 1, numeral 1, literal b) y artículo 2) califica el contenido de lo informado. Medido: TPL_2088_2025 y TPL_0600_2026; aplicado en el Exp. 2889-2026.',
        '8. **Un reclamo es 88.1 aunque pida información.** Ante un proveedor supervisado por la SBS, la respuesta que no entrega lo que el reclamo pedía se imputa por el numeral 88.1 del artículo 88, una imputación por reclamo, con su código y fecha; no se duplica como información.',
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
