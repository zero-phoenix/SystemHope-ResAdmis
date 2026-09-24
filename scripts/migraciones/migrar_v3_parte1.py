#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Migracion v3, parte 1: correcciones deterministas sobre el corpus de plantillas.

Cada correccion nace de un mandato del instructor (23/09/2026) o de un error medido:

  1. R-155 corregida segun la ley (D1): "aprobada por Decreto Legislativo 807",
     "merituadas", "articulo 26", "articulo 223", "Ley 27444"; sin "N°" ni volada.
  2. Numero del traslado por el numero REAL de denunciados (alias del
     encabezado), no por la carpeta: 369 plantillas de un solo denunciado
     llevaban "presenten" por el error del normalizador R-155 original.
     Singular: "al denunciado que no lo hubiera presentado" (P1).
  3. Firma segun el mandato vigente (R-103, D9): Rimac -> LUISA ANALI SILVA
     MALPARTIDA, Secretaria Tecnica Ad Hoc; el resto -> EVELING ROA QUISPE,
     Secretaria Tecnica. Sin "(e)".
  4. Nunca "N°", "Nro.", "N." ni volada ante una norma o articulo.
  5. Nunca "denunciante" en la narracion de HECHOS: se sustituye por la
     tratativa del encabezado ("el señor [APELLIDO]" / "la señora [APELLIDO]").
     Lo que no se puede resolver con certeza (varios denunciantes, genero
     desconocido) se lista y no se toca.

Uso:
    python scripts/migraciones/migrar_v3_parte1.py            # simulacion + informe
    python scripts/migraciones/migrar_v3_parte1.py --aplicar  # reescribe los .docx
"""

from __future__ import annotations

import argparse
import os
import json
import re
import shutil
import sys
import tempfile
import zipfile
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

# HISTORICO (v3.0). Desde v3.5 (R-212) el traslado es «correr traslado de la denuncia del …»:
# lo pone y sincroniza scripts/migraciones/traslado_denuncia.py (tambien desde sanear_admisorio.py).
FORMULA = (
    "correr traslado de la presente resolución a {den} para que, de conformidad con lo "
    "dispuesto por el artículo 26 de la Ley sobre Facultades, Normas y Organización del "
    "Indecopi, aprobada por Decreto Legislativo 807, {verbo} sus descargos sobre la "
    "imputación de cargos realizada en un plazo no mayor a cinco (5) días hábiles contado "
    "a partir del día siguiente de la notificación de la presente resolución, vencido el "
    "cual, el Secretario Técnico declarará en rebeldía {rebeldia}. Debe precisarse que de "
    "conformidad con lo establecido por el artículo 223 del Texto Único Ordenado de la Ley "
    "27444, Ley del Procedimiento Administrativo General, las alegaciones y los hechos "
    "relevantes de la reclamación, salvo que hayan sido específicamente negadas en la "
    "contestación, se tendrán por aceptadas o merituadas como ciertas."
)
SINGULAR = {
    "verbo": "presente",
    "rebeldia": "al denunciado que no lo hubiera presentado",
}
PLURAL = {
    "verbo": "presenten",
    "rebeldia": "a los denunciados que no lo hubieran presentado",
}

FIRMA_TITULAR = ("EVELING ROA QUISPE", "Secretaria Técnica")
FIRMA_RIMAC = ("LUISA ANALÍ SILVA MALPARTIDA", "Secretaria Técnica Ad Hoc")

# Destinatarios de traslado corrompidos por el normalizador R-155 original,
# corregidos segun el encabezado del propio documento (verificado a mano).
DESTINATARIO_CORREGIDO = {
    "TPL_2487_2026": "La Positiva Seguros y Reaseguros S.A.",
    "TPL_2843_2025": "Quálitas Compañía de Seguros S.A.",
    "TPL_0708_2025": "Mapfre Perú Compañía de Seguros y Reaseguros S.A.",
    "TPL_2579_2025": "Rímac Seguros y Reaseguros S.A.",
    "TPL_2271_2026": "Rímac Seguros y Reaseguros S.A. y al Banco BBVA Perú S.A.",
}

RE_P = re.compile(r"<w:p[ >].*?</w:p>", re.S)
RE_T = re.compile(r"(<w:t(?:\s[^>]*)?>)([^<]*)(</w:t>)")
RE_NORMA_N = re.compile(
    r"\b((?:Ley|Decreto\s+(?:Supremo|Legislativo|de\s+Urgencia)|Directiva|Resoluci[oó]n|art[íi]culo|numeral|inciso)\s+)"
    r"(?:N[°º]|Nº|N\.º|Nro\.?|nro\.?|N\.|N(?=[\s ]*\d))[\s ]*(?=\d)"
)
RE_VOLADA = re.compile(r"\b((?:art[íi]culo|numeral)\s+\d+(?:\.\d+)*)\s*[°º]")


def texto(p: str) -> str:
    return "".join(m.group(2) for m in RE_T.finditer(p))


def reemplazar_en_parrafo(p: str, patron: re.Pattern, sustituto) -> tuple[str, int]:
    """Reemplaza coincidencias sobre el texto concatenado de los runs, conservando formato.

    El texto nuevo queda en el run donde empieza la coincidencia; lo que la
    coincidencia ocupaba en runs siguientes se borra.
    """
    trozos = list(RE_T.finditer(p))
    if not trozos:
        return p, 0
    textos = [m.group(2) for m in trozos]
    plano = "".join(textos)
    coincidencias = list(patron.finditer(plano))
    if not coincidencias:
        return p, 0
    limites, acc = [], 0
    for t in textos:
        limites.append((acc, acc + len(t)))
        acc += len(t)
    for m in reversed(coincidencias):
        nuevo = sustituto(m) if callable(sustituto) else m.expand(sustituto)
        ini, fin = m.start(), m.end()
        primero = True
        for i, (a, b) in enumerate(limites):
            if b <= ini or a >= fin:
                continue
            lo, hi = max(ini, a) - a, min(fin, b) - a
            t = textos[i]
            textos[i] = t[:lo] + (nuevo if primero else "") + t[hi:]
            primero = False
    salida, pos = [], 0
    for m, t in zip(trozos, textos):
        abre = m.group(1)
        if t != m.group(2) and "xml:space" not in abre:
            abre = abre.replace("<w:t", '<w:t xml:space="preserve"', 1)
        salida.append(p[pos : m.start()] + abre + t + m.group(3))
        pos = m.end()
    salida.append(p[pos:])
    return "".join(salida), len(coincidencias)


def fijar_texto(p: str, nuevo: str) -> str:
    """Pone `nuevo` en el primer run con texto y vacia los demas (parrafos de una linea)."""
    primero = [True]

    def sub(m):
        if primero[0]:
            primero[0] = False
            abre = (
                m.group(1)
                if "xml:space" in m.group(1)
                else m.group(1).replace("<w:t", '<w:t xml:space="preserve"', 1)
            )
            return abre + nuevo + m.group(3)
        return m.group(1) + m.group(3)

    return RE_T.sub(sub, p)


def contar_entidades(den: str) -> int:
    d = re.sub(r"(?i)seguros\s+y\s+reaseguros", "SEGUROS_REASEGUROS", den)
    d = re.sub(r"(?i)servicios\s+y\s+", "SERVICIOS_", d)
    partes = [
        x
        for x in re.split(
            r",\s*(?:y\s+)?|\s+y\s+(?=(?:a\s+|al\s+|a\s+la\s+)?[A-ZÁÉÍÓÚÑ])", d
        )
        if x.strip()
    ]
    return len(partes)


def bloque(ps_txt: list[str], inicio: str, fin: str) -> str:
    i = next((k for k, t in enumerate(ps_txt[:20]) if re.match(inicio, t, re.I)), None)
    if i is None:
        return ""
    j = next(
        (
            k
            for k in range(i + 1, min(len(ps_txt), 25))
            if re.match(fin, ps_txt[k], re.I)
        ),
        i + 1,
    )
    return "\n".join(ps_txt[i:j])


def tratativa(ps_txt: list[str], sujeto_tipo: str | None):
    """Devuelve (genero, nombre) del unico denunciante, o None si no hay certeza."""
    blk = re.sub(
        r"(?i)^DENUNCIANTES?\s*(\(S\))?\s*:?",
        "",
        bloque(ps_txt, r"DENUNCIANTE", r"DENUNCIAD"),
    )
    alias = re.findall(r"\(([^)]*)\)", blk)
    if len(alias) != 1:
        return None
    a = alias[0].strip()
    m = re.match(r"(?i)SEÑORA\s+(.+)$", a)
    if m:
        return "f", m.group(1).strip().title().replace("[Apellido]", "[APELLIDO]")
    m = re.match(r"(?i)SEÑOR\s+(.+)$", a)
    if m:
        return "m", m.group(1).strip().title().replace("[Apellido]", "[APELLIDO]")
    if re.fullmatch(r"\[APELLIDO\]", a) and sujeto_tipo in ("varon", "mujer"):
        return ("m" if sujeto_tipo == "varon" else "f"), "[APELLIDO]"
    return None


RE_DENUNCIANTE = re.compile(
    r"\b(?P<prep>[Dd]e la parte|[Dd]e la|[Dd]el|[Aa] la parte|[Aa] la|[Aa]l|[Ll]a parte|[Ll]a|[Ee]l)\s+denunciante\b"
)


def sustituto_denunciante(genero: str, nombre: str):
    def sub(m):
        prep = m.group("prep")
        low = prep.lower()
        if low.startswith("de"):
            base = "del señor" if genero == "m" else "de la señora"
        elif low.startswith("a"):
            base = "al señor" if genero == "m" else "a la señora"
        else:
            base = "el señor" if genero == "m" else "la señora"
        if prep[0].isupper():
            base = base[0].upper() + base[1:]
        return f"{base} {nombre}"

    return sub


def migrar(
    xml: str, ruta: Path, sujeto_tipo: str | None, informe: Counter, pendientes: list
):
    parrafos = RE_P.findall(xml)
    ps_txt = [re.sub(r"\s+", " ", texto(p)).strip() for p in parrafos]
    hdr_den = re.sub(
        r"(?i)^DENUNCIAD[OA]S?\s*(\(S\))?\s*:?",
        "",
        bloque(ps_txt, r"DENUNCIAD", r"MATERIA"),
    )
    n_hdr = len(re.findall(r"\([^)]*\)", hdr_den))
    es_rimac = "RÍMAC" in hdr_den.upper() or "RIMAC" in hdr_den.upper()
    cambios = {}

    # HECHOS: tramo entre el titulo y la admision
    try:
        a = next(k for k, t in enumerate(ps_txt) if re.fullmatch(r"HECHOS\s*", t))
        b = next(
            k
            for k, t in enumerate(ps_txt)
            if k > a and re.match(r"DE LA ADMISI|ADMISI", t)
        )
    except StopIteration:
        a = b = -1
    trat = tratativa(ps_txt, sujeto_tipo)

    idx_cargo = max(
        (
            k
            for k, t in enumerate(ps_txt)
            if re.match(r"Secretari[ao]\s+T[ée]cnic[ao]", t)
        ),
        default=None,
    )

    for k, p in enumerate(parrafos):
        t = ps_txt[k]
        nuevo = p
        # 1-2. Traslado
        if "correr traslado" in t:
            m = re.search(
                r"correr traslado de la presente resolución a (.+?),? para que", t
            )
            if m:
                den = m.group(1).strip()
                for pref, fijo in DESTINATARIO_CORREGIDO.items():
                    if ruta.name.startswith(pref):
                        den = fijo
                        informe["destinatario_corregido"] += 1
                if re.search(r"(?<![\w.])S\.A(\.A|\.C)?$", den):
                    den += "."
                    informe["punto_sa_restituido"] += 1
                n_tr = contar_entidades(den)
                if n_hdr and n_tr != n_hdr:
                    pendientes.append(
                        f"{ruta.name}: encabezado {n_hdr} denunciado(s) y traslado {n_tr}; se usa el encabezado"
                    )
                    informe["traslado_discrepancia"] += 1
                n = n_hdr or n_tr
                forma = PLURAL if n > 1 else SINGULAR
                antes_plural = "presenten sus" in t
                if antes_plural != (n > 1):
                    informe["traslado_numero_corregido"] += 1
                cuerpo = FORMULA.format(den=den, **forma)
                pre = re.match(r"(.*?)correr traslado", t).group(1)
                runs = list(RE_T.finditer(p))
                # el cuerpo vive en el run que contiene "correr traslado"
                objetivo = next(
                    i for i, r in enumerate(runs) if "correr traslado" in r.group(2)
                )
                acumulado = "".join(r.group(2) for r in runs[:objetivo])
                resto = runs[objetivo].group(2)
                prefijo = resto[: resto.index("correr traslado")]
                trozos, pos = [], 0
                for i, r in enumerate(runs):
                    if i < objetivo:
                        continue
                    abre = (
                        r.group(1)
                        if "xml:space" in r.group(1)
                        else r.group(1).replace("<w:t", '<w:t xml:space="preserve"', 1)
                    )
                    contenido = prefijo + cuerpo if i == objetivo else ""
                    trozos.append((r.start(), r.end(), abre + contenido + r.group(3)))
                for s, e, rep in reversed(trozos):
                    nuevo = nuevo[:s] + rep + nuevo[e:]
                informe["traslado_reescrito"] += 1
            else:
                pendientes.append(
                    f"{ruta.name}: traslado con forma no canonica, no se toca: {t[:90]}"
                )
        # 3. Firma
        if idx_cargo is not None and k in (idx_cargo - 1, idx_cargo):
            nombre, cargo = FIRMA_RIMAC if es_rimac else FIRMA_TITULAR
            deseado = cargo if k == idx_cargo else nombre
            if t != deseado:
                nuevo = fijar_texto(nuevo, deseado)
                informe["firma_normalizada"] += 1
        # 4. N° / Nro. / volada ante normas
        nuevo, c1 = reemplazar_en_parrafo(nuevo, RE_NORMA_N, r"\1")
        nuevo, c2 = reemplazar_en_parrafo(nuevo, RE_VOLADA, r"\1")
        informe["norma_numero_limpiado"] += c1 + c2
        # 5. "denunciante" en HECHOS
        if a < k < b and re.search(r"\bdenunciantes?\b", t):
            if trat:
                nuevo, c = reemplazar_en_parrafo(
                    nuevo, RE_DENUNCIANTE, sustituto_denunciante(*trat)
                )
                informe["denunciante_sustituido"] += c
            resto_t = texto(nuevo)
            if re.search(r"\bdenunciantes?\b", resto_t):
                informe["denunciante_pendiente"] += 1
                pendientes.append(
                    f"{ruta.name}: 'denunciante' sin resolver en HECHOS: ...{re.search(r'.{0,60}denunciantes?.{0,30}', resto_t).group(0)}..."
                )
        if nuevo != p:
            cambios[p] = nuevo
    for viejo, nuevo in cambios.items():
        xml = xml.replace(viejo, nuevo, 1)
    return xml


def reescribir_docx(ruta: Path, nuevo_xml: str):
    fd, nombre = tempfile.mkstemp(suffix=".docx")
    os.close(fd)
    tmp = Path(nombre)
    with zipfile.ZipFile(ruta) as zin, zipfile.ZipFile(
        tmp, "w", zipfile.ZIP_DEFLATED
    ) as zout:
        for item in zin.infolist():
            datos = (
                nuevo_xml.encode("utf-8")
                if item.filename == "word/document.xml"
                else zin.read(item.filename)
            )
            zout.writestr(item, datos)
    shutil.move(str(tmp), ruta)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true")
    args = ap.parse_args()
    indice = {
        Path(i["ruta_relativa"]).name: i
        for i in json.loads(
            (RAIZ / "docs/plantillas_maestras_index.json").read_text(encoding="utf-8")
        )
    }
    archivos = sorted(
        {
            p
            for p in (RAIZ / "plantillas_maestras").rglob("*")
            if p.suffix.lower() == ".docx"
        }
    )
    archivos += sorted((RAIZ / "automatizacion_antigravity/modelos").glob("*.docx"))
    informe, pendientes, tocados = Counter(), [], 0
    for ruta in archivos:
        with zipfile.ZipFile(ruta) as z:
            xml = z.read("word/document.xml").decode("utf-8")
        nuevo = migrar(
            xml, ruta, indice.get(ruta.name, {}).get("sujeto_tipo"), informe, pendientes
        )
        if nuevo != xml:
            tocados += 1
            if args.aplicar:
                reescribir_docx(ruta, nuevo)
    print(
        f"{'APLICADO' if args.aplicar else 'SIMULACION'}: {len(archivos)} documentos, {tocados} modificados"
    )
    for k, v in sorted(informe.items()):
        print(f"  {k:28s} {v}")
    salida = RAIZ / "docs/migracion_v3_parte1_pendientes.txt"
    salida.write_text("\n".join(pendientes) + "\n", encoding="utf-8")
    print(
        f"  pendientes para revision: {len(pendientes)} -> {salida.relative_to(RAIZ)}"
    )


if __name__ == "__main__":
    sys.exit(main())
