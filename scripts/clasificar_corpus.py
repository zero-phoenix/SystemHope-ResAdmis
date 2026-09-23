#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Clasificacion POR CONTENIDO de las plantillas (F1 del plan v3).

La clasificacion anterior venia de la carpeta, y la carpeta mentia: plantillas
de un solo denunciado archivadas como «2_o_mas_ddos». Aqui cada campo se lee del
documento y, cuando se puede, de dos lugares distintos del documento:

  denunciantes : numero y clase (varon, mujer, sucesion_intestada,
                 herederos_no_acreditados, conyuges, persona_juridica,
                 asociacion, varios, mixto) y la TRATATIVA con que el
                 documento los nombra en hechos y en el resolutivo (forma, sin
                 datos personales: «el señor [X]», «la Sucesión [X]»...).
  denunciados  : numero real (alias del encabezado) contrastado con el
                 traslado; tipo y via de notificacion de cada uno.
  subtipos     : confidencialidad, inclusion de oficio.
  imputaciones : normas, forma del sujeto y si es conjunta.
  nota_traslado: directa | memorandum | documento_traslado.
  calidad      : falsadores del verificador; `apta_como_base` si no tiene
                 ninguno. Antigravity elige primero entre las aptas.

Los campos historicos (rama, materia, proveedor_tipo, sujeto_tipo) se conservan
para no romper a quien los lee; proveedor_tipo y sujeto_tipo se RECALCULAN desde
el contenido.

Uso:
    python scripts/clasificar_corpus.py            # informe
    python scripts/clasificar_corpus.py --guardar  # reescribe el indice
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import catalogar_imputaciones as CI  # noqa: E402
import verificar_admisorio as V  # noqa: E402

INDICE = RAIZ / "docs" / "plantillas_maestras_index.json"
PJ = re.compile(
    r"S\.A\.?|S\.A\.C|S\.A\.A|E\.I\.R\.L|S\.R\.L|S\.C\.R\.L|SOCIEDAD|EMPRESA", re.I
)


def parrafos(ruta: Path) -> list[str]:
    with zipfile.ZipFile(ruta) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    salida = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", xml, re.S):
        p = re.sub(r"<w:br[^>]*/>", "\n", p)
        salida.append(re.sub(r"[ \t]+", " ", re.sub(r"<[^>]+>", "", p)).strip())
    return salida


def bloque(ps: list[str], inicio: str, fin: str) -> list[str]:
    i = next((k for k, t in enumerate(ps[:25]) if re.match(inicio, t, re.I)), None)
    if i is None:
        return []
    j = next(
        (k for k in range(i + 1, min(len(ps), 30)) if re.match(fin, ps[k], re.I)), i + 1
    )
    texto = "\n".join(ps[i:j])
    texto = re.sub(r"(?i)^%s\s*(\(S\))?\s*:?" % inicio, "", texto)
    return [l.strip() for l in texto.split("\n") if l.strip()]


def forma(t: str) -> str:
    """Forma de la tratativa sin datos: nombres propios -> [X]."""
    t = re.sub(r"\[[A-Z]+\]", "[X]", t)
    t = re.sub(r"\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\b", "[X]", t)
    t = re.sub(r"(\[X\]\s*)+", "[X] ", t).strip()
    return t


def tipo_denunciado(linea: str) -> str:
    u = V.sin_tildes(linea).upper()
    if re.search(r"AFOCAT|FONDO REGIONAL|FONDO CONTRA ACCIDENTES", u):
        return "afocat"
    if re.search(r"CAFAE|COMITE DE ADMINISTRACION", u):
        return "cafae"
    if "CORREDOR" in u:
        return "corredor"
    if re.search(
        r"SEGUROS|REASEGUROS|ASEGURADORA|CARDIF|CHUBB|MAPFRE|PACIFICO|INTERSEGURO|PROTECTA|QUALITAS|CRECER|VIVIR",
        u,
    ):
        return "aseguradora"
    if re.search(r"\bBANCO\b|SCOTIABANK|INTERBANK|BBVA|MIBANCO|\bBCP\b|DINERS", u):
        return "banco"
    if re.search(r"CAJA|COOPERATIVA|FINANCIERA|CREDITOS|EDPYME|CREDISCOTIA", u):
        return "financiera"
    if re.search(r"\(SEÑOR|\(SEÑORA|\(SENOR|\(SENORA", u):
        return "persona_natural"
    return "otro"


def clase_denunciantes(lineas: list[str], texto: str, sujeto_previo: str) -> str:
    alias = [re.findall(r"\(([^)]*)\)", l) for l in lineas]
    n = sum(1 for a in alias if a)
    u = V.sin_tildes(" ".join(lineas)).upper()
    if n <= 1:
        if "SUCESION" in u:
            return "sucesion_intestada"
        if "ASOCIACION" in u:
            return "asociacion"
        if PJ.search(" ".join(lineas)):
            return "persona_juridica"
        if "SENORA" in u or "SEÑORA" in " ".join(lineas).upper():
            return "mujer"
        if "SENOR" in u or "SEÑOR" in " ".join(lineas).upper():
            return "varon"
        return {
            "varon": "varon",
            "mujer": "mujer",
            "sucesion_intestada": "sucesion_intestada",
        }.get(sujeto_previo, "indeterminado")
    if any(PJ.search(l) for l in lineas):
        return "mixto"
    low = texto.lower()
    if "cónyuge" in low or "conyuge" in low:
        return "conyuges"
    if "heredero" in low or "sucesión" in low or "sucesion" in low:
        return "herederos_no_acreditados"
    return "varios"


GENERICAS = {
    "SEGUROS",
    "REASEGUROS",
    "COMPANIA",
    "PERU",
    "BANCO",
    "CAJA",
    "MUNICIPAL",
    "AHORRO",
    "CREDITO",
    "COOPERATIVA",
    "FONDO",
    "COMITE",
    "ADMINISTRACION",
    "ENTIDAD",
    "EMPRESA",
    "CREDITOS",
    "SOCIEDAD",
    "ANONIMA",
    "CERRADA",
}


def via_de(nombre: str, notificaciones: list[tuple[str, str]]) -> str:
    u = V.sin_tildes(nombre).upper()
    claves = [w for w in re.findall(r"[A-Z]{4,}", u) if w not in GENERICAS][
        :2
    ] or re.findall(r"[A-Z]{4,}", u)[:2]
    for via, texto in notificaciones:
        t = V.sin_tildes(texto).upper()
        if claves and all(c in t for c in claves):
            return via
    return "?"


def clasificar(ficha: dict) -> dict:
    ruta = RAIZ / ficha["ruta_relativa"]
    ps = parrafos(ruta)
    texto = " ".join(ps)
    den_l = bloque(ps, r"DENUNCIANTES?", r"DENUNCIAD")
    ddo_l = [
        l for l in bloque(ps, r"DENUNCIAD[OA]S?", r"MATERIA") if re.search(r"\(", l)
    ]
    notifs = []
    for p in ps:
        if "requerir" not in p or not re.search(
            r"Casilla|correo electr|domicilio procesal", p
        ):
            continue
        via = (
            "casilla"
            if "Casilla" in p
            else "domicilio"
            if "domicilio procesal" in p
            else "correo"
            if "correo electrónico" in p
            else "?"
        )
        notifs.append((via, p))
    denunciados = []
    for l in ddo_l:
        nombre = re.sub(r"\([^)]*\)", "", l).strip()
        denunciados.append(
            {
                "tipo": tipo_denunciado(l),
                "alias": re.findall(r"\(([^)]*)\)", l)[0].strip(),
                "via": via_de(nombre, notifs),
            }
        )
    tr = next((p for p in ps if "correr traslado" in p), "")
    tr_dest = [("traslado", tr.split(" para que")[0])]
    omitidos = [
        d["alias"]
        for d, l in zip(denunciados, ddo_l)
        if via_de(re.sub(r"\([^)]*\)", "", l), tr_dest) == "?"
    ]
    n_tr = len(ddo_l) - len(omitidos)
    # tratativas
    try:
        a = next(k for k, t in enumerate(ps) if re.fullmatch(r"HECHOS\s*", t))
        apertura = ps[a + 1] if a + 1 < len(ps) else ""
        if not apertura:
            apertura = next((t for t in ps[a + 1 : a + 5] if t), "")
    except StopIteration:
        apertura = ""
    m = re.search(
        r",\s*((?:el|la|los|las)\s+(?:señor|señora|señores|señoras|Sucesión|sucesión|cónyuges)[^,]{0,40}?)\s+denunci",
        apertura,
    )
    trat_hechos = forma(m.group(1)) if m else None
    prim = next((p for p in ps if p.startswith("PRIMERO")), "")
    m = re.search(r"interpuesta por\s+(.{3,90}?)\s+contra", prim)
    trat_res = forma(m.group(1)) if m else None
    # imputaciones
    imps = []
    for p in ps:
        if not re.match(r"Presunta infracci", p, re.I):
            continue
        normas = "|".join(CI.normas_de(re.split(r"\sen tanto\s", p, 1)[0]))
        suj = re.search(r"en tanto (.+?)\s+(?:no\s+)?habr[ií]an?\b", p)
        s = suj.group(1) if suj else ""
        imps.append(
            {
                "normas": normas,
                "sujeto": "los_proveedores_denunciados"
                if s.lower().startswith("los proveedores denunciados")
                else "el_proveedor_denunciado"
                if s.lower().startswith("el proveedor denunciado")
                else "dos_nombrados"
                if re.search(
                    r"\sy\s+(?:el |la )?[A-ZÁÉÍÓÚ]",
                    re.sub(r"(?i)seguros y reaseguros", "", s),
                )
                else "nombrado_o_generico",
                "conjunta": bool(re.search(r"habr[ií]an\b", p)),
            }
        )
    notas = ""
    try:
        with zipfile.ZipFile(ruta) as z:
            notas = re.sub(
                r"<[^>]+>", " ", z.read("word/footnotes.xml").decode("utf-8", "replace")
            )
    except KeyError:
        pass
    nota1 = (
        "memorandum"
        if re.search(r"Denuncia remitida[^.]{0,60}MEMOR", notas, re.I)
        else "documento_traslado"
        if re.search(r"Denuncia remitida[^.]{0,60}Documento de traslado", notas, re.I)
        else "directa"
    )
    doc, secc, z = V.leer_documento(str(ruta))
    falsadores = sorted(
        {n.split()[0] for n, fn, t in V.PRUEBAS if t == "falsador" and fn(doc, secc, z)}
    )
    n_ddo = len(ddo_l)
    clase = clase_denunciantes(den_l, texto, ficha.get("sujeto_tipo", ""))
    materias = " ".join(ps[:12]).upper()
    ficha = dict(ficha)
    ficha.update(
        {
            "denunciantes": {
                "n": sum(1 for l in den_l if "(" in l) or 1,
                "clase": clase,
                "tratativa_hechos": trat_hechos,
                "tratativa_resolutivo": trat_res,
            },
            "denunciados": {
                "n": n_ddo,
                "n_en_traslado": n_tr,
                "omitidos_en_traslado": omitidos,
                "detalle": denunciados,
            },
            "subtipos": [
                s
                for s, c in (
                    (
                        "confidencialidad",
                        "CONFIDENCIAL" in materias or "confidencial" in prim.lower(),
                    ),
                    (
                        "inclusion_de_oficio",
                        "INCLUSIÓN DE OFICIO" in materias
                        or "INCLUSION DE OFICIO" in materias,
                    ),
                )
                if c
            ],
            "imputaciones": imps,
            "nota_traslado": nota1,
            "firma": "ad_hoc" if "Ad Hoc" in texto else "titular",
            "falsadores": falsadores,
            "apta_como_base": not falsadores,
            "proveedor_tipo": (
                "1_ddo_" + (denunciados[0]["tipo"] if denunciados else "otro")
            )
            if n_ddo == 1
            else "2_ddos"
            if n_ddo == 2
            else "3_o_mas_ddos",
            "sujeto_tipo": clase,
        }
    )
    return ficha


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--guardar", action="store_true")
    a = ap.parse_args(argv)
    fichas = json.loads(INDICE.read_text(encoding="utf-8"))
    nuevas = [clasificar(f) for f in fichas]
    C = Counter()
    for f in nuevas:
        C["denunciados=%s" % min(f["denunciados"]["n"], 3)] += 1
        C["denunciante=%s" % f["denunciantes"]["clase"]] += 1
        C["discrepa_traslado"] += (
            f["denunciados"]["n"] != f["denunciados"]["n_en_traslado"]
        )
        C["apta_como_base"] += f["apta_como_base"]
        for s in f["subtipos"]:
            C["subtipo=" + s] += 1
        C["nota=" + f["nota_traslado"]] += 1
        for d in f["denunciados"]["detalle"]:
            C["via=" + d["via"]] += 1
    for k, v in sorted(C.items()):
        print("  %-38s %d" % (k, v))
    if a.guardar:
        INDICE.write_text(
            json.dumps(nuevas, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        print("Indice v3 guardado: %d fichas." % len(nuevas))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
