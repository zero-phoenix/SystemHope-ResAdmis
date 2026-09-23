#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Falsador automatico de admisorios CC1.

Uso:
    python scripts/verificar_admisorio.py <archivo.docx> [...]

Cada prueba corresponde a una regla de `automatizacion_antigravity/REGLAS_DE_APRENDIZAJE.md`
y esta escrita para FALLAR, no para confirmar. Un admisorio se entrega solo con
salida `APTO`. La salida es determinista y apta para CI.

Codigo de salida: 0 si todos los documentos son APTOS, 1 si alguno falla.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path as pathlib_Path
import sys
import zipfile
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

ORDINALES = [
    "PRIMERO",
    "SEGUNDO",
    "TERCERO",
    "CUARTO",
    "QUINTO",
    "SEXTO",
    "SETIMO",
    "OCTAVO",
    "NOVENO",
    "DECIMO",
]  # R-146: UNDECIMO y DUODECIMO no existen en el corpus (0 de 593);
# se componen DECIMO PRIMERO y DECIMO SEGUNDO

# La matriz de firma vigente (R-103, 18/09/2026) vive en prueba_r103_firma y en
# config/firmas.json. La firma unica del 14/09/2026 (R-127) esta DEROGADA.


def sin_tildes(texto: str) -> str:
    tabla = str.maketrans("áéíóúÁÉÍÓÚñÑüÜ", "aeiouAEIOUnNuU")
    return texto.translate(tabla)


class Parrafo:
    __slots__ = ("texto", "runs_bold", "numerado", "notas", "estilo", "ilvl")

    def __init__(self, texto, runs_bold, numerado, notas, estilo, ilvl):
        self.texto = texto
        self.runs_bold = runs_bold
        self.numerado = numerado
        self.notas = notas
        self.estilo = estilo
        self.ilvl = ilvl

    @property
    def vacio(self) -> bool:
        return not self.texto.strip()


def leer_parrafos(xml: bytes) -> list[Parrafo]:
    root = ET.fromstring(xml)
    salida = []
    for p in root.iter(W + "p"):
        pr = p.find(W + "pPr")
        estilo = ""
        numerado = False
        ilvl = -1
        if pr is not None:
            s = pr.find(W + "pStyle")
            estilo = s.get(W + "val") if s is not None else ""
            num = pr.find(W + "numPr")
            numerado = num is not None
            if num is not None:
                nivel = num.find(W + "ilvl")
                ilvl = int(nivel.get(W + "val")) if nivel is not None else 0
        partes, bolds, notas = [], [], []
        for r in p.iter(W + "r"):
            rpr = r.find(W + "rPr")
            b = rpr.find(W + "b") if rpr is not None else None
            es_bold = b is not None and b.get(W + "val") not in ("0", "false")
            texto = "".join(t.text or "" for t in r.iter(W + "t"))
            for fr in r.iter(W + "footnoteReference"):
                notas.append(fr.get(W + "id"))
            if texto:
                partes.append(texto)
                bolds.append((texto, es_bold))
        salida.append(Parrafo("".join(partes), bolds, numerado, notas, estilo, ilvl))
    return salida


def leer_documento(ruta: str):
    z = zipfile.ZipFile(ruta)
    doc = leer_parrafos(z.read("word/document.xml"))
    crudo = z.read("word/document.xml").decode("utf-8", "replace")
    secciones = re.findall(r"<w:(?:header|footer)Reference[^>]*>", crudo)
    return doc, secciones, z


# --------------------------------------------------------------------------- #
# Pruebas. Cada una devuelve una lista de fallos (vacia = corroborada).
# --------------------------------------------------------------------------- #


def prueba_r97_isomorfismo(doc) -> list[str]:
    """El nucleo factico de la considerativa debe repetirse palabra por palabra
    en el articulo de imputacion correspondiente."""
    nucleos_cons = []
    for p in doc:
        m = re.search(
            r"consistente en que (.+?)(?:;\s*involucrar|\.\s*Por consiguiente)",
            p.texto,
            re.S,
        )
        if m:
            nucleos_cons.append(re.sub(r"\s+", " ", m.group(1)).strip())
    nucleos_res = []
    for p in doc:
        # Formato A/B (458 de 593): la imputacion va en vineta propia.
        m = re.search(
            r"Presunta infracci[oó]n .*?, en tanto (.+?)\s*\.\s*$", p.texto, re.S
        )
        if m:
            nucleos_res.append(re.sub(r"\s+", " ", m.group(1)).strip())
            continue
        # Formato C (121 de 593): imputacion unica EMBEBIDA en el propio PRIMERO.
        # Medido el 18/09/2026: la version anterior de esta prueba solo veia el
        # formato de vineta y daba NO APTO a uno de cada cinco admisorios validos
        # del corpus. Falsador de la correccion: un admisorio en formato C cuyo
        # nucleo sea verbatim y que aun asi sea rechazado por R-97.
        m = re.search(
            r"^\s*PRIMERO\s*:.*?\bpor\s+(?:la\s+)?presunta[s]?\s+infracci[oó]n(?:es)?\b"
            r".*?,\s*en tanto (.+?)\s*\.\s*$",
            p.texto,
            re.S | re.I,
        )
        if m:
            nucleos_res.append(re.sub(r"\s+", " ", m.group(1)).strip())
    fallos = []
    if not nucleos_cons:
        return ["R-97: no se hallo ningun nucleo factico en la considerativa"]
    if len(nucleos_cons) != len(nucleos_res):
        fallos.append(
            "R-97: %d nucleos en considerativa vs %d imputaciones en resolutiva"
            % (len(nucleos_cons), len(nucleos_res))
        )
    for i, nucleo in enumerate(nucleos_cons):
        if nucleo not in nucleos_res:
            fallos.append(
                "R-97: el nucleo %d no aparece verbatim en la resolutiva: %.90s..."
                % (i + 1, nucleo)
            )
    return fallos


def prueba_r108_requerimiento(doc) -> list[str]:
    """La lista de incisos del REQUERIMIENTO DE INFORMACION (considerativa) debe
    repetirse verbatim en el articulo resolutivo que la ordena. Soporta requerimiento
    unico o individualizado por proveedor (QUINTO y SEXTO)."""

    def incisos(texto):
        t_norm = texto.replace("–", "-").replace("—", "-")
        return [
            re.sub(r"\s+", " ", x).strip()
            for x in re.findall(r"\((?:i|ii|iii|iv)\)\s*([^;]+)", t_norm)
        ]

    cons = []
    res = []
    en_considerativa = False
    en_requerimiento_cons = False
    for p in doc:
        t = sin_tildes(p.texto)
        if "DE LA ADMISION A TRAMITE" in t.upper():
            en_considerativa = True
        if en_considerativa and (
            "REQUERIMIENTO DE INFORMACION" in t.upper()
            or ("conviene requerir" in t and ("cumpla con" in t or "cumplan con" in t))
        ):
            en_requerimiento_cons = True
        if en_requerimiento_cons:
            if "RESOLUCION DE LA SECRETARIA TECNICA" in t.upper() or t.startswith(
                "PRIMERO"
            ):
                en_requerimiento_cons = False
            else:
                cons.extend(incisos(p.texto))
        if re.match(r"\s*(QUINTO|CUARTO|SEXTO)\s*:", t) and (
            "cumpla con" in t or "cumplan con" in t
        ):
            res.extend(incisos(p.texto))

    if not cons:
        return [
            "R-108: no existe el parrafo de REQUERIMIENTO DE INFORMACION en la considerativa"
        ]
    if not res:
        return [
            "R-108: no existe el articulo resolutivo espejo del requerimiento probatorio"
        ]
    faltan = [c for c in cons if c not in res]
    return [
        "R-108: inciso de la considerativa ausente en la resolutiva: %.70s..." % c
        for c in faltan
    ]


def prueba_r151_casilla_habilitada(doc) -> list[str]:
    """R-151 (mandato del instructor, 18/09/2026): la Casilla Electronica exige
    padron ACTIVO, numero de e-casilla y telefono movil no vacio.

    Es condicion NECESARIA, no suficiente: la cedula sigue fijando la via
    (R-129), pero notificar a casilla a quien no cumple los tres requisitos es
    un acto de notificacion invalido.

    Fuente: docs/casillas_habilitadas.json, derivado del padron de aceptacion de
    TyC. El padron no se versiona porque trae datos personales.

    Falsador: un ordinal que notifique a Casilla Electronica a un proveedor que
    docs/casillas_habilitadas.json marca como no habilitado.
    """
    ruta = (
        pathlib_Path(__file__).resolve().parent.parent
        / "docs"
        / "casillas_habilitadas.json"
    )
    if not ruta.exists():
        return []  # sin padron filtrado no se puede falsar: no se inventa una infraccion
    import json as _json

    try:
        datos = _json.loads(ruta.read_text(encoding="utf-8"))
    except Exception:
        return []
    vetados = [
        n
        for n, v in datos.get("proveedores", {}).items()
        if not v.get("casilla_habilitada")
    ]
    fallos = []
    for p in doc:
        t = p.texto
        if "Casilla Electr" not in t:
            continue
        # un mismo ordinal puede nombrar a varias partes: se miran todas
        for m in re.finditer(r"requerir a(?:l)?\s+(.{3,140}?)\s+para que", t):
            crudo = m.group(1).strip()
            parte = re.sub(
                r"\s+", " ", re.sub(r"[^A-Z0-9 ]", " ", sin_tildes(crudo).upper())
            ).strip()
            for veto in vetados:
                nucleo = " ".join(veto.split()[:3])
                if nucleo and nucleo in parte:
                    motivo = datos["proveedores"][veto].get("motivo", "no habilitado")
                    fallos.append(
                        "R-151: se notifica a Casilla Electronica a '%s', que no la tiene "
                        "habilitada (%s)" % (crudo, motivo)
                    )
                    break
    return fallos


def prueba_r103_firma(doc) -> list[str]:
    """R-103 (mandato del instructor, 18/09/2026): matriz de firma.

    Eveling Roa Quispe firma como Secretaria Tecnica TODOS los admisorios,
    salvo las denuncias contra Rimac, que firma Luisa Anali Silva Malpartida
    como Secretaria Tecnica Ad Hoc. El sufijo '(e)' queda suprimido.

    Este mandato deroga la firma unica del 14/09/2026 (R-127), que ademas el
    corpus nunca corroboro: 494 de 593 plantillas firman Eveling Roa Quispe.

    Falsador: un admisorio contra Rimac firmado por la titular, un admisorio
    contra cualquier otro proveedor firmado Ad Hoc, o la aparicion de '(e)'.
    """
    texto_doc = sin_tildes(" ".join(p.texto for p in doc)).upper()
    textos = [sin_tildes(p.texto).upper().strip() for p in doc[:25]]
    i = next((k for k, t in enumerate(textos) if t.startswith("DENUNCIADO")), None)
    j = (
        next(
            (k for k in range(i + 1, len(textos)) if textos[k].startswith("MATERIA")),
            (i or 0) + 1,
        )
        if i is not None
        else 0
    )
    denunciado = " ".join(textos[i:j]) if i is not None else ""
    es_rimac = "RIMAC" in denunciado
    fallos = []
    if "SECRETARIA TECNICA (E)" in texto_doc:
        fallos.append(
            "R-103: el cargo lleva '(e)', suprimido por mandato del 18/09/2026"
        )
    if es_rimac:
        if "LUISA ANALI SILVA MALPARTIDA" not in texto_doc:
            fallos.append(
                "R-103: denuncia contra Rimac y no firma LUISA ANALI SILVA MALPARTIDA"
            )
        if "SECRETARIA TECNICA AD HOC" not in texto_doc:
            fallos.append(
                "R-103: denuncia contra Rimac sin el cargo 'Secretaria Tecnica Ad Hoc'"
            )
        if "EVELING ROA QUISPE" in texto_doc:
            fallos.append("R-103: denuncia contra Rimac firmada por EVELING ROA QUISPE")
    else:
        if "EVELING ROA QUISPE" not in texto_doc:
            fallos.append("R-103: no firma EVELING ROA QUISPE (mandato del 18/09/2026)")
        if "AD HOC" in texto_doc:
            fallos.append(
                "R-103: designacion 'Ad Hoc' fuera de una denuncia contra Rimac"
            )
    return fallos


def prueba_r104_negritas(doc) -> list[str]:
    """El rotulo ordinal de todo articulo resolutivo va en negrita, sin excepcion."""
    fallos = []
    for p in doc:
        t = sin_tildes(p.texto).lstrip()
        for ordinal in ORDINALES:
            prefix = ordinal + ":"
            if t.startswith(prefix):
                chars_bold = []
                for texto, b in p.runs_bold:
                    for ch in sin_tildes(texto):
                        chars_bold.append((ch, b))
                start_idx = 0
                while (
                    start_idx < len(chars_bold) and chars_bold[start_idx][0].isspace()
                ):
                    start_idx += 1
                prefix_chars = chars_bold[start_idx : start_idx + len(prefix)]
                bold_rotulo = len(prefix_chars) == len(prefix) and all(
                    b for ch, b in prefix_chars
                )
                if not bold_rotulo:
                    fallos.append("R-104: el rotulo %s: no esta en negrita" % ordinal)
                break
    encabezado = [
        p
        for p in doc[:8]
        if sin_tildes(p.texto)
        .upper()
        .startswith(("EXPEDIENTE", "DENUNCIANTE", "DENUNCIADO", "RESOLUCION"))
    ]
    for p in encabezado:
        if not any(b for _, b in p.runs_bold):
            fallos.append(
                "R-104: la linea de encabezado '%.28s' no esta en negrita"
                % p.texto.strip()
            )
    return fallos


def prueba_r105_vacios(doc) -> list[str]:
    huerfanos = sum(1 for p in doc if p.numerado and p.vacio)
    if huerfanos:
        return [
            "R-105: %d parrafo(s) con numeracion activa y sin texto (viñeta huerfana en Word)"
            % huerfanos
        ]
    return []


def prueba_r106_notas(doc, z) -> list[str]:
    usadas = {n for p in doc for n in p.notas}
    definidas = set()
    if "word/footnotes.xml" in z.namelist():
        root = ET.fromstring(z.read("word/footnotes.xml"))
        for fn in root.iter(W + "footnote"):
            fid = fn.get(W + "id")
            tipo = fn.get(W + "type")
            if tipo in ("separator", "continuationSeparator", "continuationNotice"):
                continue
            if "".join(t.text or "" for t in fn.iter(W + "t")).strip():
                definidas.add(fid)
    huerfanas = sorted(definidas - usadas, key=lambda v: int(v))
    if huerfanas:
        return [
            "R-106: nota(s) al pie definidas sin ancla en el cuerpo: %s"
            % ", ".join(huerfanas)
        ]
    return []


def prueba_r107_membrete(z) -> list[str]:
    """Lo invariante del modelo institucional es el CONTENIDO del encabezado y del
    pie, no el numero de referencias de seccion: el corpus de control incluye
    documentos con seis referencias y documentos con dos."""

    def compacta(texto):
        return re.sub(r"[^A-Z0-9/]", "", sin_tildes(texto).upper())

    cab_xml = pie_xml = ""
    for n in z.namelist():
        if re.match(r"word/header\d+\.xml", n):
            cab_xml += z.read(n).decode("utf-8", "replace")
        if re.match(r"word/footer\d+\.xml", n):
            pie_xml += z.read(n).decode("utf-8", "replace")
    cab = compacta(re.sub(r"<[^>]+>", " ", cab_xml))
    pie = compacta(re.sub(r"<[^>]+>", " ", pie_xml))
    fallos = []
    for etiqueta, esperado in (
        ("membrete linea 1", "SECRETARIATECNICADELA"),
        ("membrete linea 2", "COMISIONDEPROTECCIONALCONSUMIDOR1"),
        ("membrete linea 3", "SEDECENTRAL"),
    ):
        if esperado not in cab:
            fallos.append("R-107: falta el %s en el encabezado" % etiqueta)
    if "MCPC01/03" not in pie:
        fallos.append(
            "R-107: falta el codigo de calidad M-CPC-01/03 en el pie de pagina"
        )
    # El campo dinamico de numero de pagina NO se exige: el control ADM 2723-2026 R2
    # carece de el y es un documento valido. Presente en 2 de 3 controles.
    return fallos


def prueba_r110_modo_verbal(doc) -> list[str]:
    """En los incisos de hechos, toda conducta del proveedor se enuncia bajo
    atribucion al denunciante (estilo indirecto) o en modo potencial. Afirmarla
    en indicativo asertivo prejuzga el fondo antes de los descargos."""
    atribucion = re.compile(
        r"\b(senal[oó]|indic[oó]|precis[oó]|manifest[oó]|refiri[oó]|sostuvo|agreg[oó]"
        r"|aleg[oó]|cuestion[oó]|denunci[oó]|afirm[oó]|declar[oó])\b",
        re.I,
    )
    potencial = re.compile(r"\bhabr[ií]a\b", re.I)
    proveedor_activo = re.compile(
        r"\b(R[ií]mac|Pac[ií]fico|el Banco|la compa[nñ][ií]a aseguradora|la aseguradora|el proveedor)\b"
        r"\s+(?:no\s+)?(?:se\s+)?(?:le\s+)?[a-záéíóú]+"
        r"(?:[oó]|aron|ieron|uvo|izo|ab[ií]a)\b"
    )
    fallos = []
    dentro = False
    atribucion_contextual = False
    for p in doc:
        t = p.texto.strip()
        if sin_tildes(t).upper().startswith("HECHOS"):
            dentro = True
            continue
        if sin_tildes(t).upper().startswith("DE LA ADMISION A TRAMITE"):
            break
        if not dentro or p.vacio:
            continue
        if atribucion.search(t):
            if t.endswith(":") or "denunci" in t.lower():
                atribucion_contextual = True
            continue
        if p.ilvl != 2 and not p.numerado:
            continue
        if atribucion_contextual or potencial.search(t):
            continue
        m = proveedor_activo.search(t)
        if m:
            fallos.append(
                "R-110: inciso de hechos afirma en indicativo la conducta del proveedor "
                "('%s') sin atribucion ni modo potencial: %.60s..." % (m.group(0), t)
            )
    return fallos


CATALOGO_IMPUTACIONES = (
    pathlib_Path(__file__).resolve().parent.parent
    / "docs"
    / "catalogo_imputaciones.json"
)


def prueba_r143_imputaciones(doc) -> list[str]:
    """Solo se imputa como imputan los modelos (mandato del instructor, 15/09/2026).

    Una imputacion no es una frase: es la pieza que fija el objeto del
    procedimiento, y de ella dependen los descargos, la carga de la prueba y el
    marco sancionador. Una combinacion de articulos que no existe en ninguna
    resolucion del corpus crea un cargo que la Comision nunca ha formulado, y el
    administrado tiene que defenderse de algo que en la practica no existe.

    El corpus admite **35 combinaciones** de normas, extraidas de 630 plantillas
    por `catalogar_imputaciones.py`. Cualquier otra --aunque cada articulo suelto
    sea correcto-- es una mezcla inventada.
    """
    import json as _json
    import sys as _sys

    _sys.path.insert(0, str(pathlib_Path(__file__).resolve().parent))
    import catalogar_imputaciones as CI

    if not CATALOGO_IMPUTACIONES.exists():
        return []  # sin catalogo no se puede juzgar; no se inventa un veredicto
    catalogo = _json.loads(CATALOGO_IMPUTACIONES.read_text(encoding="utf-8"))
    admitidas = set(catalogo["normas_admitidas"]) | set(
        catalogo.get("normas_en_consulta", [])
    )

    texto = re.sub(r"\s+", " ", " ".join(p.texto for p in doc))
    fallos = []
    vistas = set()
    for m in CI.RE_IMPUTACION.finditer(texto):
        normas = CI.normas_de(m.group(1))
        if not normas:
            continue
        clave = "|".join(normas)
        if clave in admitidas or clave in vistas:
            continue
        vistas.add(clave)
        fallos.append(
            "R-143: la combinacion de normas '%s' no esta en docs/tabla_tipificacion.json. "
            "Solo se imputa por la tabla del instructor y en la forma de las plantillas; "
            "si hace falta otra, se eleva al instructor. Enunciado: '%s'"
            % (clave, re.sub(r"\s+", " ", m.group(0))[:110])
        )
    return fallos


def prueba_r143_consulta(doc) -> list[str]:
    """Observaciones: normas en consulta (art. 49) y articulo 24 excepcional."""
    import json as _json
    import sys as _sys

    _sys.path.insert(0, str(pathlib_Path(__file__).resolve().parent))
    import catalogar_imputaciones as CI

    if not CATALOGO_IMPUTACIONES.exists():
        return []
    consulta = set(
        _json.loads(CATALOGO_IMPUTACIONES.read_text(encoding="utf-8")).get(
            "normas_en_consulta", []
        )
    )
    texto = re.sub(r"\s+", " ", " ".join(p.texto for p in doc))
    obs = []
    for m in CI.RE_IMPUTACION.finditer(texto):
        clave = "|".join(CI.normas_de(m.group(1)))
        if clave in consulta:
            obs.append(
                "R-143b: '%s' esta en consulta al instructor (clausulas abusivas, art. 49)"
                % clave
            )
        if clave == "art.24":
            obs.append(
                "R-143b: articulo 24 solo procede si el reclamo se interpuso ante un proveedor NO regulado por el sistema financiero; si lo esta, numeral 88.1 del articulo 88"
            )
    return sorted(set(obs))


# Invariantes de forma, MEDIDOS sobre 120 plantillas del corpus el 15/09/2026, no
# copiados de la memoria documentada. Importa la diferencia: la memoria afirmaba un
# margen derecho de 2,50 cm y el corpus mide 3,00 cm en 113 de 116 secciones. Donde
# la memoria y el corpus discrepan, manda el corpus.
FUENTE_CC1 = "Arial Narrow"  # 59 337 de 59 370 runs con fuente declarada
FUENTES_TOLERADAS = {"Arial Narrow", "Segoe UI Symbol", None}
ALINEACIONES = {
    "both",
    "center",
}  # 10 412 justificados, 421 centrados, 0 a la izquierda
INTERLINEADO = "240"  # sencillo; 276 aparece en el 1 % y es desviacion
MARGENES = ("1701", "1701", "1417", "1417")  # izq, der, sup, inf = 3,0/3,0/2,5/2,5 cm


def prueba_r144_formato(z) -> list[str]:
    """Fuente, alineacion, interlineado y encuadre, contra lo que hace el corpus.

    El desalineamiento es el falsador mas visible de todos: un parrafo a la
    izquierda en un cuerpo justificado se ve desde el otro lado de la sala y delata
    que el documento se manipulo fuera del flujo.
    """
    try:
        raiz = ET.fromstring(z.read("word/document.xml"))
    except Exception as exc:
        return ["R-144: no se pudo leer el documento: %s" % exc]

    fallos = []

    ajenas = Counter()
    for rpr in raiz.iter(W + "rPr"):
        f = rpr.find(W + "rFonts")
        if f is not None and f.get(W + "ascii") not in FUENTES_TOLERADAS:
            ajenas[f.get(W + "ascii")] += 1
    for fuente, veces in ajenas.most_common(3):
        fallos.append(
            "R-144: %d run(s) en '%s'; el corpus usa %s" % (veces, fuente, FUENTE_CC1)
        )

    malas = Counter()
    for ppr in raiz.iter(W + "pPr"):
        j = ppr.find(W + "jc")
        if j is not None and j.get(W + "val") not in ALINEACIONES:
            malas[j.get(W + "val")] += 1
    for alineacion, veces in malas.most_common(3):
        fallos.append(
            "R-144: %d parrafo(s) alineados a '%s'. El corpus solo justifica o "
            "centra: un parrafo desalineado delata manipulacion fuera del flujo"
            % (veces, alineacion)
        )

    otros = Counter()
    for ppr in raiz.iter(W + "pPr"):
        sp = ppr.find(W + "spacing")
        if sp is not None and sp.get(W + "line") and sp.get(W + "line") != INTERLINEADO:
            otros[sp.get(W + "line")] += 1
    for valor, veces in otros.most_common(2):
        fallos.append(
            "R-144: %d parrafo(s) con interlineado %s; el corpus usa %s (sencillo)"
            % (veces, valor, INTERLINEADO)
        )

    for mar in raiz.iter(W + "pgMar"):
        actual = tuple(mar.get(W + k) for k in ("left", "right", "top", "bottom"))
        if actual != MARGENES:
            fallos.append(
                "R-144: margenes %s; el corpus usa %s (3,0/3,0/2,5/2,5 cm)"
                % ("/".join(str(a) for a in actual), "/".join(MARGENES))
            )
            break

    return fallos


# Esqueleto resolutivo, MEDIDO sobre los 603 admisorios reales del corpus (de 630
# plantillas, 27 son resoluciones de confidencialidad o decretos cortos: por eso
# ninguna medicion de anatomia llega al 100 %).
ESQUELETO = [
    ("PRIMERO", "admitir a tramite", 90.0),
    ("SEGUNDO", "medios probatorios ofrecidos", 91.4),
    ("TERCERO", "personeria y condicion MYPE", 89.6),
    ("CUARTO", "correr traslado", 88.7),
    ("QUINTO", "requerimiento de informacion", 86.6),
    ("SEXTO", "sancion hasta 450 UIT (art. 110)", 90.9),
    ("SÉTIMO", "costas y gastos (art. 39 D.L. 807)", 0),
    ("OCTAVO", "conciliacion (art. 29 D.L. 807)", 72.3),
    ("NOVENO", "reserva o medida complementaria", 0),
    ("DÉCIMO", "acuse de recibo de la notificacion", 92.9),
]

# Ortografia de los ordinales: el corpus escribe SETIMO (uso forense peruano), no
# SEPTIMO --579 contra 12--, y compone el undecimo y el duodecimo como DECIMO
# PRIMERO (485) y DECIMO SEGUNDO (152). UNDECIMO y DUODECIMO: cero apariciones.
ORDINAL_PROHIBIDO = {
    "SÉPTIMO": "SÉTIMO",
    "SEPTIMO": "SÉTIMO",
    "UNDÉCIMO": "DÉCIMO PRIMERO",
    "UNDECIMO": "DÉCIMO PRIMERO",
    "DUODÉCIMO": "DÉCIMO SEGUNDO",
    "DUODECIMO": "DÉCIMO SEGUNDO",
}


def prueba_r146_esqueleto(doc) -> list[str]:
    """El orden de los ordinales y su ortografia, tal como los escribe el corpus.

    No comprueba el contenido de cada articulo --eso lo hacen R-97 y R-108--, sino
    que la resolutiva siga la secuencia del corpus y que los ordinales se escriban
    como los escribe la Comision.
    """
    texto = re.sub(r"\s+", " ", " ".join(p.texto for p in doc))
    alto = sin_tildes(texto).upper()
    fallos = []

    for malo, bueno in ORDINAL_PROHIBIDO.items():
        if re.search(r"\b%s\b" % sin_tildes(malo).upper(), alto):
            fallos.append(
                "R-146: escribe '%s'; el corpus usa '%s' (medido: 579 contra 12)"
                % (malo, bueno)
            )

    # Solo cuentan los ordinales que ENCABEZAN un parrafo resolutivo. Buscarlos en
    # el texto corrido hacia saltar la regla con la palabra «tercero» de la prosa:
    # 7 de 57 plantillas del corpus daban falso positivo por eso.
    posiciones = []
    for i, parrafo in enumerate(doc):
        cabeza = sin_tildes(parrafo.texto.strip()).upper()
        for ordinal, _tema, _pct in ESQUELETO:
            if re.match(r"%s\s*:" % sin_tildes(ordinal).upper(), cabeza):
                posiciones.append((ordinal, i))
                break
    orden_hallado = [o for o, _pos in sorted(posiciones, key=lambda x: x[1])]
    orden_esperado = [o for o, _t, _p in ESQUELETO if o in orden_hallado]
    if orden_hallado != orden_esperado:
        fallos.append(
            "R-146: los ordinales no siguen la secuencia del corpus. Hallado: %s"
            % " < ".join(orden_hallado)
        )
    return fallos


# Lexico prohibido, por NIVELES y con la frecuencia medida sobre los 593
# admisorios del corpus. La diferencia entre niveles importa: una prohibicion que
# el propio corpus incumple en el 25 % de los casos no es una prohibicion, es una
# preferencia mal enunciada.
LEXICO_ABSOLUTO = {  # 0 apariciones en 593 admisorios
    "tras": ("luego de", 0),
    "esposo": ("conyuge", 0),
    "esposa": ("conyuge", 0),
    "induccion a error": ("arts. 1.1.b y 2", 0),
    "004-2019-JUS": ("006-2026-JUS", 0),
}
LEXICO_CUASI_ABSOLUTO = {  # 1 aparicion (0,17 %): desviacion, no uso
    "doctor": ("medico", 1),
    "occiso": ("el causante", 1),
    "finado": ("el causante", 1),
    "difunto": ("el causante", 1),
}


def prueba_r148_lexico(doc) -> list[str]:
    """Las invariantes lexicas, con la frecuencia que las sostiene.

    Se comprueban solo las que el corpus respeta de forma absoluta o casi. Las
    demas se dejan fuera a proposito: «indebidamente» estaba enunciado como
    prohibido y aparece en **149 de 593** admisorios (25,1 %). Prohibirlo seria
    hacer fallar al propio corpus, que es la senal de que la regla estaba mal.
    """
    texto = sin_tildes(" ".join(p.texto for p in doc)).lower()
    fallos = []
    for termino, (correcto, _freq) in LEXICO_ABSOLUTO.items():
        if re.search(r"\b%s\b" % re.escape(sin_tildes(termino).lower()), texto):
            fallos.append(
                "R-148: usa '%s'; el corpus no lo usa ni una vez en 593 admisorios. "
                "Escribe '%s'" % (termino, correcto)
            )
    for termino, (correcto, freq) in LEXICO_CUASI_ABSOLUTO.items():
        if re.search(r"\b%s\b" % re.escape(sin_tildes(termino).lower()), texto):
            fallos.append(
                "R-148: usa '%s'; aparece %d vez en 593 admisorios (0,2 %%), que es "
                "desviacion y no uso. Escribe '%s'" % (termino, freq, correcto)
            )
    return fallos


def prueba_r153_superindice_notas(doc, z) -> list[str]:
    """R-153: Superindices obligatorios en notas al pie.

    Tanto la llamada de nota al pie en el cuerpo (document.xml) como la
    referencia en el pie (footnotes.xml) deben tener vertAlign="superscript"
    y estilo Refdenotaalpie para renderizar como potencia pequeña superior
    y no en la linea base al tamano regular del texto.
    """
    fallos = []
    try:
        doc_xml = z.read("word/document.xml").decode("utf-8", "replace")
        for m in re.finditer(
            r"<w:r\b[^>]*>(?:(?!</w:r>).)*?<w:footnoteReference\b[^>]*>(?:(?!</w:r>).)*?</w:r>",
            doc_xml,
            re.S,
        ):
            run = m.group(0)
            if 'w:val="superscript"' not in run:
                fallos.append(
                    "R-153: llamada de nota al pie sin superindice explicito en document.xml"
                )
                break
    except Exception as exc:
        fallos.append("R-153: error leyendo document.xml: %s" % exc)

    if "word/footnotes.xml" in z.namelist():
        try:
            fn_xml = z.read("word/footnotes.xml").decode("utf-8", "replace")
            for m in re.finditer(
                r"<w:r\b[^>]*>(?:(?!</w:r>).)*?<w:footnoteRef\b[^>]*>(?:(?!</w:r>).)*?</w:r>",
                fn_xml,
                re.S,
            ):
                run = m.group(0)
                if 'w:val="superscript"' not in run:
                    fallos.append(
                        "R-153: numero de nota al pie sin superindice explicito en footnotes.xml"
                    )
                    break
        except Exception as exc:
            fallos.append("R-153: error leyendo footnotes.xml: %s" % exc)

    return fallos


def prueba_r154_cero_resaltados(z) -> list[str]:
    """R-154: Cero resaltados en todo el documento.

    Queda estrictamente prohibida cualquier etiqueta <w:highlight> en
    cualquier parte XML del documento (document.xml, footnotes, headers, footers).
    """
    fallos = []
    for nombre in z.namelist():
        if nombre.startswith("word/") and nombre.endswith(".xml"):
            try:
                xml = z.read(nombre).decode("utf-8", "replace")
                cuantos = len(re.findall(r"<w:highlight\b", xml))
                if cuantos:
                    fallos.append(
                        "R-154: se encontraron %d etiqueta(s) <w:highlight> en %s (todo resaltado esta prohibido)"
                        % (cuantos, nombre)
                    )
            except Exception:
                pass
    return fallos


def contar_denunciados(doc) -> int:
    """Numero de denunciados = alias entre parentesis del bloque DENUNCIADO(S)."""
    textos = [p.texto.strip() for p in doc[:25]]
    i = next((k for k, t in enumerate(textos) if re.match(r"DENUNCIAD", t, re.I)), None)
    if i is None:
        return 0
    j = next(
        (k for k in range(i + 1, len(textos)) if re.match(r"MATERIA", textos[k], re.I)),
        i + 1,
    )
    bloque = re.sub(r"(?i)^DENUNCIAD[OA]S?\s*(\(S\))?\s*:?", "", "\n".join(textos[i:j]))
    return len(re.findall(r"\([^)]*\)", bloque))


def prueba_r155_formula_traslado(doc) -> list[str]:
    """R-155 (21/09/2026), corregida segun la ley el 23/09/2026 (D1, P1).

    Formula literal: "... articulo 26 de la Ley sobre Facultades, Normas y
    Organizacion del Indecopi, aprobada por Decreto Legislativo 807,
    presente[n] sus descargos ... declarara en rebeldia al denunciado que no lo
    hubiera presentado / a los denunciados que no lo hubieran presentado ...
    articulo 223 del Texto Unico Ordenado de la Ley 27444 ... aceptadas o
    merituadas como ciertas." Singular o plural segun el numero REAL de
    denunciados del encabezado, nunca segun la carpeta.
    """
    p_traslado = next((p for p in doc if "correr traslado" in p.texto.lower()), None)
    if p_traslado is None:
        return ["R-155: no se hallo el articulo resolutivo de correr traslado"]
    t = re.sub(r"\s+", " ", p_traslado.texto)
    fallos = []
    if re.search(
        r"8079|meritadas|aprobado por Decreto Legislativo|N[°º]\s*(807|27444)|\b(26|223)\s*[°º]",
        t,
    ):
        fallos.append(
            "R-155: errata derogada (8079, 'meritadas', 'aprobado', 'N°' o volada); la ley dice 'aprobada por Decreto Legislativo 807' y 'merituadas'"
        )
    if re.search(
        r"contados?\s+desde\s+la\s+notificaci[oó]n|\bart[íi]culo\s+233\b|numeral\s+233\.1",
        t,
        re.I,
    ):
        fallos.append(
            "R-155: contiene una formula derogada (A: 'contados desde la notificacion'; B: articulo 233)"
        )
    exigidos = [
        (
            r"correr traslado de la presente resoluci[oó]n a .+? para que, de conformidad con lo dispuesto por el art[íi]culo 26 de la Ley sobre Facultades, Normas y Organizaci[oó]n del Indecopi, aprobada por Decreto Legislativo 807\b,",
            "inicio literal: '... articulo 26 ..., aprobada por Decreto Legislativo 807,'",
        ),
        (
            r"sus descargos sobre la imputaci[oó]n de cargos realizada en un plazo no mayor a cinco \(5\) d[íi]as h[áa]biles contado a partir del d[íi]a siguiente de la notificaci[oó]n de la presente resoluci[oó]n, vencido el cual, el Secretario T[ée]cnico declarar[áa] en rebeld[íi]a",
            "plazo y apercibimiento literales",
        ),
        (
            r"art[íi]culo 223 del Texto [UÚ]nico Ordenado de la Ley 27444, Ley del Procedimiento Administrativo General, las alegaciones y los hechos relevantes de la reclamaci[oó]n, salvo que hayan sido espec[íi]ficamente negadas en la contestaci[oó]n, se tendr[áa]n por aceptadas o merituadas como ciertas\.",
            "presuncion literal del articulo 223 ('merituadas')",
        ),
    ]
    for patron, que in exigidos:
        if not re.search(patron, t):
            fallos.append("R-155: falta " + que)
    n = contar_denunciados(doc)
    plural = (
        "presenten sus descargos" in t
        and "a los denunciados que no lo hubieran presentado" in t
    )
    singular = (
        "presente sus descargos" in t
        and "al denunciado que no lo hubiera presentado" in t
    )
    if n == 1 and not singular:
        fallos.append(
            "R-155: hay 1 denunciado; exige 'presente sus descargos' y 'al denunciado que no lo hubiera presentado'"
        )
    if n > 1 and not plural:
        fallos.append(
            "R-155: hay %d denunciados; exige 'presenten sus descargos' y 'a los denunciados que no lo hubieran presentado'"
            % n
        )
    return fallos


RE_N_NORMA = re.compile(
    r"\b(?:Ley|Decreto\s+(?:Supremo|Legislativo|de\s+Urgencia)|Directiva|Resoluci[oó]n|art[íi]culos?|numeral|inciso|literal)\s+(?:N[°º]|Nº|N\.º|Nro\.?|N\.|N)\s*\d"
    r"|\b(?:art[íi]culos?|numeral)\s+\d+(?:\.\d+)*\s*[°º]",
    re.I,
)


def prueba_r156_numero_de_norma(doc) -> list[str]:
    """R-156 (mandato del instructor, 23/09/2026): nunca 'N°', 'N', '°', 'Nro.'
    ni similares ante una norma o articulo: 'Ley 29571', 'articulo 26',
    'numeral 1.1 del articulo 51'."""
    fallos = []
    for p in doc:
        for m in RE_N_NORMA.finditer(p.texto):
            fallos.append("R-156: numero de norma con 'N°'/volada: '%s'" % m.group(0))
    return fallos[:5]


def tramo_hechos(doc):
    textos = [p.texto.strip() for p in doc]
    try:
        a = next(k for k, t in enumerate(textos) if re.fullmatch(r"HECHOS\s*", t))
        b = next(
            k
            for k, t in enumerate(textos)
            if k > a and re.match(r"DE LA ADMISI|ADMISI", t)
        )
    except StopIteration:
        return []
    return doc[a + 1 : b]


def prueba_r157_denunciante_en_hechos(doc) -> list[str]:
    """R-157 (mandato del instructor, 23/09/2026): nunca 'denunciante' en la
    narracion de los hechos; se usa la tratativa del encabezado ('el senor X',
    'la senora X', 'la Sucesion...')."""
    fallos = []
    for p in tramo_hechos(doc):
        m = re.search(r".{0,40}\bdenunciantes?\b.{0,30}", p.texto)
        if m:
            fallos.append("R-157: 'denunciante' en HECHOS: '...%s...'" % m.group(0))
    return fallos


RE_POLIZA_ENMASCARADA = re.compile(
    r"P[óo]liza[^.;]{0,25}?\b\w*\d\w*[\*xX]{2,}\w*", re.I
)
RE_CUENTA_ABIERTA = re.compile(
    r"(?:Tarjeta|Cr[ée]dito|Cuenta|Pr[ée]stamo)(?:(?!P[óo]liza)[^.;]){0,30}?(?<![\d*xX])(\d[\d\s-]{11,}\d)(?![\d*xX])",
    re.I,
)


def prueba_r158_enmascarado(doc) -> list[str]:
    """R-158 (D6, 23/09/2026): la poliza nunca se enmascara; tarjeta, credito,
    cuenta y prestamo llevan enmascarados SOLO los digitos del medio."""
    fallos = []
    for p in doc:
        for m in RE_POLIZA_ENMASCARADA.finditer(p.texto):
            fallos.append(
                "R-158: poliza enmascarada (la poliza va completa): '%s'" % m.group(0)
            )
        for m in RE_CUENTA_ABIERTA.finditer(p.texto):
            fallos.append(
                "R-158: numero de tarjeta/credito/cuenta sin enmascarar el tramo medio: '%s'"
                % m.group(0)
            )
    return fallos[:5]


RE_NOTA_TRASLADO = re.compile(
    r"^Denuncia remitida a (?:esta Comisi[oó]n|la Comisi[oó]n de Protecci[oó]n al Consumidor 1) mediante "
    r"(?:MEMORANDUM|MEMOR[AÁ]NDUM|Memor[aá]ndum|DOCUMENTO DE TRASLADO|Documento de [Tt]raslado) \S+ "
    r"de fecha \d{1,2} de [a-z]+ del? \d{4}, (?:recibida|recepcionada) el \d{1,2} de [a-z]+ del? \d{4}\.$"
)


def prueba_r159_nota_traslado(z) -> list[str]:
    """R-159 (D3, 23/09/2026): si la denuncia llego derivada de otro organo, la
    primera nota al pie consigna el documento, su fecha de emision y la fecha de
    recepcion en CC1, en la forma literal del corpus (234 plantillas):
    'Denuncia remitida a esta Comision mediante MEMORANDUM|Documento de Traslado
    <numero> de fecha <fecha>, recibida el <fecha>.'"""
    try:
        x = z.read("word/footnotes.xml").decode("utf-8", "replace")
    except KeyError:
        return []
    notas = [
        re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", n)).strip().lstrip("․ ").strip()
        for i, n in re.findall(
            r'<w:footnote [^>]*w:id="(\d+)"[^>]*>(.*?)</w:footnote>', x, re.S
        )
        if int(i) > 0
    ]
    if not notas or not re.match(r"Denuncia remitida", notas[0], re.I):
        return []
    if not RE_NOTA_TRASLADO.match(notas[0]):
        return ["R-159: nota al pie 1 fuera de la forma literal: '%s'" % notas[0][:160]]
    return []


def prueba_r160_fecha_remesa(doc) -> list[str]:
    """R-160 (D2, 23/09/2026): la fecha de emision es la de config/remesa.json."""
    import json as _json

    cfg = pathlib_Path(__file__).resolve().parent.parent / "config" / "remesa.json"
    try:
        fecha = (
            _json.loads(cfg.read_text(encoding="utf-8"))
            .get("fecha_emision", "")
            .strip()
        )
    except Exception:
        return []
    if not fecha:
        return []
    linea = next(
        (p.texto.strip() for p in doc[:20] if p.texto.strip().startswith("Lima,")), ""
    )
    if linea != "Lima, " + fecha:
        return [
            "R-160: la fecha de emision debe ser 'Lima, %s' (config/remesa.json); el documento dice '%s'"
            % (fecha, linea)
        ]
    return []


PRUEBAS = [
    (
        "R-97  isomorfismo considerativa/resolutiva",
        lambda d, s, z: prueba_r97_isomorfismo(d),
        "falsador",
    ),
    (
        "R-103 firma segun proveedor denunciado",
        lambda d, s, z: prueba_r103_firma(d),
        "falsador",
    ),
    (
        "R-104 negritas de ordinales y encabezado",
        lambda d, s, z: prueba_r104_negritas(d),
        "falsador",
    ),
    (
        "R-105 parrafos numerados vacios",
        lambda d, s, z: prueba_r105_vacios(d),
        "falsador",
    ),
    (
        "R-106 anclas de nota al pie",
        lambda d, s, z: prueba_r106_notas(d, z),
        "falsador",
    ),
    (
        "R-107 membrete y pie institucional",
        lambda d, s, z: prueba_r107_membrete(z),
        "falsador",
    ),
    # R-108 es observacion, no falsador: el control ADM 2723-2026 R2 diverge en una
    # clausula entre considerativa y resolutiva y sigue siendo un documento valido.
    (
        "R-108 espejo del requerimiento de informacion",
        lambda d, s, z: prueba_r108_requerimiento(d),
        "observacion",
    ),
    (
        "R-110 modo verbal en hechos",
        lambda d, s, z: prueba_r110_modo_verbal(d),
        "falsador",
    ),
    (
        "R-143 imputaciones del catalogo",
        lambda d, s, z: prueba_r143_imputaciones(d),
        "falsador",
    ),
    (
        "R-151 casilla electronica habilitada",
        lambda d, s, z: prueba_r151_casilla_habilitada(d),
        "falsador",
    ),
    (
        "R-144 fuente, alineacion, interlineado y encuadre",
        lambda d, s, z: prueba_r144_formato(z),
        "falsador",
    ),
    (
        "R-146 esqueleto y ortografia de ordinales",
        lambda d, s, z: prueba_r146_esqueleto(d),
        "falsador",
    ),
    ("R-148 lexico invariante", lambda d, s, z: prueba_r148_lexico(d), "falsador"),
    (
        "R-153 superindice en llamadas y notas al pie",
        lambda d, s, z: prueba_r153_superindice_notas(d, z),
        "falsador",
    ),
    (
        "R-154 cero resaltados en el documento",
        lambda d, s, z: prueba_r154_cero_resaltados(z),
        "falsador",
    ),
    (
        "R-155 formula canonica de traslado y descargos",
        lambda d, s, z: prueba_r155_formula_traslado(d),
        "falsador",
    ),
    (
        "R-156 numero de norma sin N ni volada",
        lambda d, s, z: prueba_r156_numero_de_norma(d),
        "falsador",
    ),
    (
        "R-157 sin 'denunciante' en los hechos",
        lambda d, s, z: prueba_r157_denunciante_en_hechos(d),
        "falsador",
    ),
    (
        "R-158 enmascarado de numeros",
        lambda d, s, z: prueba_r158_enmascarado(d),
        "falsador",
    ),
    (
        "R-159 nota al pie del traslado a CC1",
        lambda d, s, z: prueba_r159_nota_traslado(z),
        "falsador",
    ),
    (
        "R-160 fecha de emision de la remesa",
        lambda d, s, z: prueba_r160_fecha_remesa(d),
        "falsador",
    ),
    (
        "R-143b normas en consulta y articulo 24",
        lambda d, s, z: prueba_r143_consulta(d),
        "observacion",
    ),
]


def verificar(ruta: str) -> bool:
    doc, secciones, z = leer_documento(ruta)
    print("=" * 78)
    print(ruta)
    print("=" * 78)
    falsadores, observaciones = [], []
    for etiqueta, prueba, severidad in PRUEBAS:
        fallos = prueba(doc, secciones, z)
        if not fallos:
            estado = "OK   "
        else:
            estado = "FALLA" if severidad == "falsador" else "AVISO"
        print("  [%s] %s" % (estado, etiqueta))
        for f in fallos:
            print("         - %s" % f)
        (falsadores if severidad == "falsador" else observaciones).extend(fallos)
    print(
        "  --> %s (%d falsadores, %d observaciones)"
        % ("APTO" if not falsadores else "NO APTO", len(falsadores), len(observaciones))
    )
    if observaciones:
        print(
            "      Las observaciones no bloquean la entrega: se elevan al instructor."
        )
    print()
    return not falsadores


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    return 0 if all([verificar(a) for a in argv[1:]]) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
