#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Migracion v3.1 del corpus: lleva a las 574 plantillas las correcciones del
instructor del 24/09/2026 (revision pagina por pagina del admisorio de prueba
9999-2026). Cada paso es la forma general de un defecto, y cada uno tiene su
falsador en `verificar_admisorio.py`:

  R-183  notas huerfanas fuera; notas renumeradas en orden de llamada
  R-184  nota del Codigo tras «Código de Protección y Defensa del Consumidor»;
         nota de competencia tras «en ejercicio de sus facultades»
  R-187  forma de las notas: tabulacion tras la llamada, sin lineas en blanco
         internas, sin dobles espacios; literales h. e i. del 115.1 con su letra
  R-164  PRIMERO: solo el rotulo en negrita
  R-192  subrayado solo en el rotulo del requerimiento
  R-190  «notificarles» cuando el ordinal requiere a varias partes
  R-191  una sola numeracion en la considerativa
  R-193  «Firmado digitalmente por» sobre el nombre de la firmante
  R-194  nunca dos lineas en blanco seguidas en el cuerpo

Se trabaja sobre el XML como texto (nunca ElementTree escribiendo, R-168) y
cada documento se relee al final: si no es XML valido, no se escribe.

Uso:
    python scripts/migraciones/migrar_v3_1.py            # informe, sin escribir
    python scripts/migraciones/migrar_v3_1.py --escribir
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "scripts"))

import notas_pie as N  # noqa: E402

RE_P = N.RE_P
RE_RUN = N.RE_RUN
RE_ORDINAL = re.compile(
    r"^\s*(D[EÉ]CIMO(?:\s+(?:PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|S[EÉ]P?TIMO))?|"
    r"PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|S[EÉ]P?TIMO|OCTAVO|NOVENO)\s*:"
)
FIRMANTES = ("EVELING ROA QUISPE", "LUISA ANALÍ SILVA MALPARTIDA", "LUISA ANALI SILVA MALPARTIDA")


def txt(p: str) -> str:
    return N.desescapar(N.texto(p))


def _sin_tildes(t: str) -> str:
    return t.translate(str.maketrans("áéíóúÁÉÍÓÚ", "aeiouAEIOU"))


# --------------------------------------------------------------------------- #
# Cuerpo
# --------------------------------------------------------------------------- #


def _quitar_prop(run: str, etiquetas: tuple[str, ...]) -> str:
    m = re.search(r"<w:rPr>.*?</w:rPr>", run, re.S)
    if not m:
        return run
    rpr = m.group(0)
    for e in etiquetas:
        rpr = re.sub(r"<w:%s(?:\s[^>]*)?/>" % e, "", rpr)
    return run[: m.start()] + rpr + run[m.end():]


def primero_solo_rotulo(x: str) -> tuple[str, int]:
    n = 0

    def _p(m):
        nonlocal n
        p = m.group(0)
        t = txt(p)
        r = RE_ORDINAL.match(t)
        if not r:
            return p
        partido = N._partir_run_tras(p, r.group(0).strip())
        if partido is None:
            return p
        q, pos = partido
        cola = RE_RUN.sub(lambda g: _quitar_prop(g.group(0), ("b", "bCs")), q[pos:])
        if cola != q[pos:]:
            n += 1
        return q[:pos] + cola

    return RE_P.sub(_p, x), n


RE_ROTULO = re.compile(r"\s*A(?:l| la)?\s+[^:,.]{2,60}:")


def subrayado_solo_rotulo(x: str) -> tuple[str, int]:
    """El subrayado es solo del rotulo del requerimiento («Al Banco:»): se quita
    de todo lo demas, incluido lo que sigue al rotulo en su propio parrafo."""
    n = 0

    def _p(m):
        nonlocal n
        p = m.group(0)
        if "<w:u " not in p:
            return p
        rot = RE_ROTULO.match(txt(p))
        if rot:
            partido = N._partir_run_tras(p, rot.group(0).strip())
            if partido is None:
                return p
            q, pos = partido
            q = q[:pos] + RE_RUN.sub(lambda g: _quitar_prop(g.group(0), ("u",)), q[pos:])
        else:
            q = RE_RUN.sub(lambda g: _quitar_prop(g.group(0), ("u",)), p)
        if q != p:
            n += 1
        return q

    return RE_P.sub(_p, x), n


def notificarles(x: str) -> tuple[str, int]:
    n = 0

    def _p(m):
        nonlocal n
        p = m.group(0)
        t = txt(p)
        if re.search(r"\bnotificarle\b", t) and re.search(r"\b(reciban|efect[uú]en)\b", t):
            q = re.sub(r"(<w:t(?:\s[^>/]*)?>[^<]*?)\bnotificarle\b", r"\1notificarles", p)
            if q != p:
                n += 1
            return q
        return p

    return RE_P.sub(_p, x), n


def numeracion_continua(x: str) -> tuple[str, int]:
    """La considerativa (de «DE LA ADMISIÓN A TRÁMITE» a «RESOLUCIÓN DE LA
    SECRETARÍA») usa la numeracion de la mayoria de sus parrafos."""
    ps = list(RE_P.finditer(x))
    ini = fin = None
    for k, m in enumerate(ps):
        t = _sin_tildes(txt(m.group(0))).upper()
        if ini is None and "DE LA ADMISION A TRAMITE" in t and len(t) < 90:
            ini = k
        elif ini is not None and "RESOLUCION DE LA SECRETARIA" in t and len(t) < 90:
            fin = k
            break
    if ini is None or fin is None:
        return x, 0
    cuerpo = []
    for k in range(ini + 1, fin):
        p = ps[k].group(0)
        t = txt(p).strip()
        num = re.search(r"<w:numPr>.*?</w:numPr>", p, re.S)
        if num and t and t.upper() != t:
            cuerpo.append((k, num.group(0)))
    series = Counter(n for _k, n in cuerpo)
    if len(series) < 2:
        return x, 0
    mayoria = series.most_common(1)[0][0]
    cambios = 0
    for k, n in reversed(cuerpo):
        if n != mayoria:
            p = ps[k].group(0).replace(n, mayoria, 1)
            x = x[: ps[k].start()] + p + x[ps[k].end():]
            cambios += 1
    return x, cambios


def firmado_digitalmente(x: str) -> tuple[str, int]:
    ps = list(RE_P.finditer(x))
    for k, m in enumerate(ps):
        if txt(m.group(0)).strip().upper() in FIRMANTES:
            previo = next((txt(q.group(0)).strip() for q in reversed(ps[:k]) if txt(q.group(0)).strip()), "")
            if previo == "Firmado digitalmente por":
                return x, 0
            clon = re.sub(r'\s(?:w14:paraId|w14:textId)="[^"]*"', "", m.group(0))
            trozos = list(N.RE_T.finditer(clon))
            if not trozos:
                return x, 0
            primero, ultimo = trozos[0], trozos[-1]
            clon = (
                clon[: primero.start()]
                + '<w:t xml:space="preserve">Firmado digitalmente por</w:t>'
                + re.sub(r"<w:t(?:\s[^>/]*)?>.*?</w:t>", "", clon[primero.end(): ultimo.end()], flags=re.S)
                + clon[ultimo.end():]
            )
            return x[: m.start()] + clon + x[m.start():], 1
    return x, 0


def _vacio_puro(p: str) -> bool:
    return (
        not txt(p).strip()
        and "<w:numPr>" not in p
        and not re.search(r"<w:br\b|<w:sectPr|<w:drawing|<w:pict|footnoteReference", p)
    )


def sin_huecos(x: str) -> tuple[str, int]:
    ps = list(RE_P.finditer(x))
    ini = next((k for k, m in enumerate(ps) if _sin_tildes(txt(m.group(0))).strip().upper().startswith("HECHOS")), None)
    ords = [k for k, m in enumerate(ps) if RE_ORDINAL.match(txt(m.group(0)))]
    if ini is None or not ords:
        return x, 0
    quitar = [
        k for k in range(ini + 1, ords[-1])
        if _vacio_puro(ps[k].group(0)) and _vacio_puro(ps[k - 1].group(0))
    ]
    for k in reversed(quitar):
        x = x[: ps[k].start()] + x[ps[k].end():]
    return x, len(quitar)


SEPARADOR = '<w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>'


def separadores_sencillos(x: str) -> tuple[str, int]:
    """R-194: una linea en blanco mide UNA linea. El separador sin espaciado
    propio hereda el del documento (8 pt despues, interlineado 1,08) y el hueco
    antes de SEGUNDO parecia doble (9999-2026, pagina 3)."""
    ps = list(RE_P.finditer(x))
    ini = next((k for k, m in enumerate(ps) if _sin_tildes(txt(m.group(0))).strip().upper().startswith("HECHOS")), None)
    ords = [k for k, m in enumerate(ps) if RE_ORDINAL.match(txt(m.group(0)))]
    if ini is None or not ords:
        return x, 0
    n = 0
    for k in reversed(range(ini + 1, ords[-1] + 1)):
        p = ps[k].group(0)
        if not _vacio_puro(p) or SEPARADOR in p:
            continue
        if re.search(r"<w:pPr>", p):
            q = re.sub(r"<w:spacing\b[^>]*/>", "", p, count=1)
            ppr = re.search(r"<w:pPr>(?:<w:pStyle\b[^>]*/>)?", q)
            q = q[: ppr.end()] + SEPARADOR + q[ppr.end():]
        elif p.endswith("/>"):
            q = p[:-2] + "><w:pPr>" + SEPARADOR + "</w:pPr></w:p>"
        else:
            q = re.sub(r"(<w:p\b[^>]*>)", r"\1<w:pPr>" + SEPARADOR + "</w:pPr>", p, count=1)
        x = x[: ps[k].start()] + q + x[ps[k].end():]
        n += 1
    return x, n


# --------------------------------------------------------------------------- #
# Notas
# --------------------------------------------------------------------------- #


def literales_con_letra(fx: str) -> tuple[str, int]:
    """Da a cada literal de una disposicion transcrita la numeracion (letra) de
    los demas literales de su nota (docs/textos_normativos.json)."""
    exigencias = N.cargar_textos()
    n = 0

    def _nota(m):
        nonlocal n
        cuerpo = m.group(0)
        todo = N.desescapar(N.texto(cuerpo))
        for ex in exigencias:
            if not re.search(ex["si_contiene"], todo):
                continue
            ps = list(RE_P.finditer(cuerpo))
            modelo = None
            for p in ps:
                t = txt(p.group(0)).strip()
                if any(t.startswith(l) for l in ex["literales"]) and "<w:numPr>" in p.group(0):
                    modelo = re.search(r"<w:pPr>.*?</w:pPr>", p.group(0), re.S)
                    modelo = modelo.group(0) if modelo else None
            if not modelo:
                continue
            for p in reversed(ps):
                t = txt(p.group(0)).strip()
                if any(t.startswith(l) for l in ex["literales"]) and "<w:numPr>" not in p.group(0):
                    q = p.group(0)
                    actual = re.search(r"<w:pPr>.*?</w:pPr>|<w:pPr/>", q, re.S)
                    if actual:
                        q = q[: actual.start()] + modelo + q[actual.end():]
                    else:
                        q = re.sub(r"(<w:p\b[^>]*>)", r"\1" + modelo, q, count=1)
                    cuerpo = cuerpo[: p.start()] + q + cuerpo[p.end():]
                    n += 1
        return cuerpo

    return N.RE_FN.sub(_nota, fx), n


# --------------------------------------------------------------------------- #


def migrar(x: str, fx: str) -> tuple[str, str, Counter]:
    c = Counter()
    if fx:
        x, fx, inf = N.normalizar(x, fx)
        c["R-183 notas huerfanas retiradas"] += len(inf["huerfanas"])
        x, hechos = N.reanclar(x, fx)
        c["R-184 notas reancladas"] += len(hechos)
        # Mover una llamada cambia el orden de lectura: se renumera otra vez
        # (sin esto la nota del traslado dejaba de ser la nota 1, R-167).
        x, fx, _inf = N.normalizar(x, fx)
        fx, inf = N.formatear_notas(fx)
        c["R-187 notas con forma corregida"] += len(inf)
        fx, k = literales_con_letra(fx)
        c["R-187 literales con su letra"] += k
        fx, hechos = N.titular_notas(x, fx)
        for h in hechos:
            c["R-187 " + h.split(": ", 1)[1]] += 1
    for nombre, f in (
        ("R-164 ordinal: solo el rotulo en negrita", primero_solo_rotulo),
        ("R-192 subrayado retirado", subrayado_solo_rotulo),
        ("R-190 notificarles", notificarles),
        ("R-191 numeracion unificada", numeracion_continua),
        ("R-193 Firmado digitalmente por", firmado_digitalmente),
        ("R-194 lineas en blanco retiradas", sin_huecos),
        ("R-194 separadores de una linea", separadores_sencillos),
    ):
        x, k = f(x)
        c[nombre] += k
    return x, fx, c


def procesar(ruta: Path, escribir: bool) -> Counter:
    with zipfile.ZipFile(ruta) as z:
        nombres = z.namelist()
        datos = {n: z.read(n) for n in nombres}
        infos = {i.filename: i for i in z.infolist()}
    x = datos["word/document.xml"].decode("utf-8")
    fx = datos["word/footnotes.xml"].decode("utf-8") if "word/footnotes.xml" in datos else ""
    x2, fx2, c = migrar(x, fx)
    for parte in (x2, fx2):
        if parte:
            ET.fromstring(parte.encode("utf-8"))  # solo lectura: valida el XML
    if escribir and (x2 != x or fx2 != fx):
        datos["word/document.xml"] = x2.encode("utf-8")
        if fx:
            datos["word/footnotes.xml"] = fx2.encode("utf-8")
        tmp = ruta.with_suffix(".tmp")
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
            for n in nombres:
                z.writestr(infos[n], datos[n])
        tmp.replace(ruta)
    return c


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--escribir", action="store_true")
    ap.add_argument("archivos", nargs="*")
    a = ap.parse_args(argv[1:])
    if a.archivos:
        rutas = [Path(r) for r in a.archivos]
    else:
        indice = json.loads((RAIZ / "docs" / "plantillas_maestras_index.json").read_text(encoding="utf-8"))
        rutas = [RAIZ / e["ruta_relativa"] for e in indice]
    total, fallidas = Counter(), []
    for r in rutas:
        try:
            c = procesar(r, a.escribir)
        except ET.ParseError as exc:
            fallidas.append("%s: XML invalido tras migrar (%s): NO se escribio" % (r.name, exc))
            continue
        total.update(c)
        total["documentos"] += 1
    print("MIGRACION v3.1 %s" % ("(escrita)" if a.escribir else "(informe; usa --escribir)"))
    for k, v in sorted(total.items()):
        print("  %6d  %s" % (v, k))
    for f in fallidas:
        print("  FALLA  " + f)
    return 1 if fallidas else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
