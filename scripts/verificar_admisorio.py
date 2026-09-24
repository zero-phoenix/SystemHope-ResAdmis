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
    __slots__ = ("texto", "runs_bold", "numerado", "notas", "estilo", "ilvl", "numid", "runs_und")

    def __init__(self, texto, runs_bold, numerado, notas, estilo, ilvl, numid="", runs_und=()):
        self.texto = texto
        self.runs_bold = runs_bold
        self.numerado = numerado
        self.notas = notas
        self.estilo = estilo
        self.ilvl = ilvl
        self.numid = numid
        self.runs_und = runs_und

    @property
    def vacio(self) -> bool:
        return not self.texto.strip()


def leer_parrafos(xml: bytes) -> list[Parrafo]:
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        # Espacios de nombres rotos: se lee una copia reparada para poder
        # verificar el contenido; R-168 rechaza el documento igualmente.
        import reparar_espacios_nombres as R

        root = ET.fromstring(
            R.reparar_xml(xml.decode("utf-8", "replace"))[0].encode("utf-8")
        )
    salida = []
    for p in root.iter(W + "p"):
        pr = p.find(W + "pPr")
        estilo = ""
        numerado = False
        ilvl = -1
        numid = ""
        if pr is not None:
            s = pr.find(W + "pStyle")
            estilo = s.get(W + "val") if s is not None else ""
            num = pr.find(W + "numPr")
            numerado = num is not None
            if num is not None:
                nivel = num.find(W + "ilvl")
                ilvl = int(nivel.get(W + "val")) if nivel is not None else 0
                nid = num.find(W + "numId")
                numid = nid.get(W + "val") if nid is not None else ""
        partes, bolds, notas, unds = [], [], [], []
        for r in p.iter(W + "r"):
            rpr = r.find(W + "rPr")
            b = rpr.find(W + "b") if rpr is not None else None
            es_bold = b is not None and b.get(W + "val") not in ("0", "false")
            u = rpr.find(W + "u") if rpr is not None else None
            es_und = u is not None and u.get(W + "val") not in ("none", "0", "false")
            texto = "".join(t.text or "" for t in r.iter(W + "t"))
            for fr in r.iter(W + "footnoteReference"):
                notas.append(fr.get(W + "id"))
            if texto:
                partes.append(texto)
                bolds.append((texto, es_bold))
                unds.append((texto, es_und))
        salida.append(
            Parrafo("".join(partes), bolds, numerado, notas, estilo, ilvl, numid, unds)
        )
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
        crudo = " ".join(p.texto for p in doc).upper()
        if "LUISA ANALI " in crudo:
            fallos.append("R-103: 'ANALÍ' se escribe siempre con tilde")
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
        # Singular y plural (varios denunciantes: «señalaron»), y con ñ: la
        # version anterior buscaba «senal» y nunca reconocia «señaló» (v3.1).
        r"\b(se[nñ]al(?:[oó]|aron)|indic(?:[oó]|aron)|precis(?:[oó]|aron)|manifest(?:[oó]|aron)"
        r"|refiri(?:[oó]|eron)|sostuv(?:o|ieron)|agreg(?:[oó]|aron)"
        r"|aleg(?:[oó]|aron)|cuestion(?:[oó]|aron)|denunci(?:[oó]|aron)|afirm(?:[oó]|aron)|declar(?:[oó]|aron))\b",
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
    import analizar_imputaciones as AI

    catalogo = _json.loads(CATALOGO_IMPUTACIONES.read_text(encoding="utf-8"))
    admitidas = list(catalogo["normas_admitidas"])

    texto = re.sub(r"\s+", " ", " ".join(p.texto for p in doc))
    fallos = []
    vistas = set()
    for m in CI.RE_IMPUTACION.finditer(texto):
        normas = CI.normas_de(m.group(1))
        if not normas:
            continue
        clave = "|".join(normas)
        if AI.admite(clave, admitidas) or clave in vistas:
            continue
        vistas.add(clave)
        if any(x in ("art.50", "art.51") for x in normas) and "num.49.1" not in normas:
            fallos.append(
                "R-143: clausula abusiva sin el numeral 49.1 del articulo 49; se invoca SIEMPRE "
                "junto al literal del articulo 50 o 51: '%s'"
                % re.sub(r"\s+", " ", m.group(0))[:110]
            )
            continue
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
            r"correr traslado de la presente resoluci[oó]n al? .+? para que, de conformidad con lo dispuesto por el art[íi]culo 26 de la Ley sobre Facultades, Normas y Organizaci[oó]n del Indecopi, aprobada por Decreto Legislativo 807\b,",
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
    # Mandato del 23/09/2026: en NINGUN contexto (norma, articulo, expediente,
    # poliza, documento de traslado, memorandum, resolucion...).
    r"\b(?:N[°º]|Nº|N\.\s?º|Nro\.?)\s*\d"
    r"|(?<=[A-Za-zÁÉÍÓÚáéíóú\)] )N\.?\s+\d"
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
    r"de fecha \d{1,2} de [a-z]+ de \d{4}, recibida el \d{1,2} de [a-z]+ de \d{4}\.$"
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
            r'<w:footnote (?:(?!/>)[^>])*?w:id="(\d+)"[^>/]*>(.*?)</w:footnote>', x, re.S
        )
        if int(i) > 0
    ]
    if not notas or not re.match(r"Denuncia remitida", notas[0], re.I):
        return []
    if not RE_NOTA_TRASLADO.match(notas[0]):
        return ["R-159: nota al pie 1 fuera de la forma literal: '%s'" % notas[0][:160]]
    return []


MESES_RE = "enero|febrero|marzo|abril|mayo|junio|julio|agosto|setiembre|septiembre|octubre|noviembre|diciembre"
RE_FECHA_MAL = re.compile(
    r"\b(?:\d{1,2} de )?(?:%s) del (?:19|20)\d\d\b|\brecepcionad[ao]s?\b|\b\d{1,2} de (?:Enero|Febrero|Marzo|Abril|Mayo|Junio|Julio|Agosto|Setiembre|Septiembre|Octubre|Noviembre|Diciembre)\b"
    % MESES_RE
)


def prueba_r161_fechas(doc, z) -> list[str]:
    """R-161 (mandato del instructor, 23/09/2026): 'de 2025', nunca 'del 2025';
    'recibida', nunca 'recepcionada'; el mes en minuscula. En cuerpo y notas."""
    textos = [p.texto for p in doc]
    try:
        x = z.read("word/footnotes.xml").decode("utf-8", "replace")
        textos.append(re.sub(r"<[^>]+>", "", x))
    except KeyError:
        pass
    fallos = []
    for t in textos:
        for m in RE_FECHA_MAL.finditer(t):
            fallos.append(
                "R-161: '%s' (se escribe 'de AAAA', 'recibida' y el mes en minuscula)"
                % m.group(0)
            )
    return fallos[:5]


ORDEN_ORDINALES = [
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
    "DECIMO PRIMERO",
    "DECIMO SEGUNDO",
    "DECIMO TERCERO",
    "DECIMO CUARTO",
    "DECIMO QUINTO",
    "DECIMO SEXTO",
    "DECIMO SETIMO",
]
RE_ORDINAL = re.compile(
    r"^(D[EÉ]CIMO(?:\s+(?:PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|S[EÉ]P?TIMO))?|PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|S[EÉ]P?TIMO|OCTAVO|NOVENO)\s*:"
)


def _ordinales(doc):
    salida = []
    for p in doc:
        m = RE_ORDINAL.match(p.texto.strip())
        if m:
            salida.append(
                (sin_tildes(m.group(1)).upper().replace("SEPTIMO", "SETIMO"), p)
            )
    return salida


def prueba_r163_ordinales_consecutivos(doc) -> list[str]:
    """R-163 (supervision 2898-2026, 23/09/2026): los ordinales del resolutivo van
    seguidos, sin saltos ni repeticiones (549 de 574 plantillas)."""
    vistos = [o for o, _p in _ordinales(doc)]
    esperado = ORDEN_ORDINALES[: len(vistos)]
    if vistos != esperado:
        for i, (a, b) in enumerate(zip(vistos, esperado)):
            if a != b:
                return [
                    "R-163: tras %s viene %s; corresponde %s"
                    % (vistos[i - 1] if i else "(inicio)", a, b)
                ]
    return []


def prueba_r164_negrita_solo_rotulo(doc) -> list[str]:
    """R-164: en TODOS los ordinales del resolutivo, incluido PRIMERO, solo el
    rotulo va en negrita.

    Mandato del instructor (24/09/2026, revision del admisorio de prueba
    9999-2026): «solo la palabra PRIMERO debe estar en negrita». Deroga la moda
    medida del 23/09/2026 (PRIMERO entero en 541 de 574); el corpus se migro
    (migraciones/migrar_v3_1.py).
    """
    fallos = []
    for ordinal, p in _ordinales(doc):
        negrita = sum(len(t) for t, b in p.runs_bold if b)
        rotulo = len(re.match(r"\s*[A-ZÉÍ ]+:\s*", p.texto).group(0))
        if negrita > rotulo + 2:
            fallos.append("R-164: en %s solo el rotulo va en negrita" % ordinal)
    return fallos[:4]


def prueba_r165_expectativas_solo_idoneidad(doc) -> list[str]:
    """R-165: «involucraria una presunta afectacion a sus expectativas…» solo
    califica IDONEIDAD (1 366 veces); en informacion, 88.1 u otras normas no se usa
    (5 de 670, desviacion)."""
    fallos = []
    for p in doc:
        t = p.texto
        if (
            "corresponde calificar" in t
            and "expectativa" in t
            and not re.search(r"deber de idoneidad|art[íi]culos 18 y 19", t)
        ):
            m = re.search(r"presunta infracci[oó]n (.{0,80})", t)
            fallos.append(
                "R-165: frase de expectativas (idoneidad) en una calificacion distinta: '%s'"
                % (m.group(1) if m else t[:80])
            )
    return fallos


def notas_al_pie(z) -> list[str]:
    """Texto de cada nota al pie real (id > 0), en orden."""
    try:
        x = z.read("word/footnotes.xml").decode("utf-8", "replace")
    except KeyError:
        return []
    return [
        re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", n)).strip().lstrip("․ ").strip()
        for i, n in re.findall(
            r'<w:footnote (?:(?!/>)[^>])*?w:id="(\d+)"[^>/]*>(.*?)</w:footnote>', x, re.S
        )
        if int(i) > 0
    ]


def prueba_r167_nota_uno(z) -> list[str]:
    """R-167: la unica nota que habla de la denuncia es la del traslado
    («Denuncia remitida a esta Comision mediante … de fecha …, recibida el …»),
    y solo cuando la denuncia llego derivada (226 plantillas). Una nota sobre la
    presentacion directa («Denuncia presentada el … ante la Mesa de Partes …»)
    no existe en el corpus (0 de 574) y el instructor la prohibio (23/09/2026):
    si la denuncia se presento en CC1, la primera nota es la del Codigo."""
    fallos = []
    for k, n in enumerate(notas_al_pie(z), 1):
        if "Mesa de Partes" in n or (
            n.startswith("Denuncia")
            and not n.startswith(("Denuncia remitida", "Denuncia desacumulada"))
        ):
            fallos.append(
                "R-167: nota %d sobre la presentacion de la denuncia (prohibida): '%s'"
                % (k, n[:120])
            )
        elif n.startswith("Denuncia remitida") and not re.search(
            r"mediante .+ de (?:fecha )?\d{1,2} de [a-z]+ de \d{4}, recibida el \d{1,2} de [a-z]+ de \d{4}\.$",
            n,
        ):
            fallos.append(
                "R-167: nota de traslado incompleta (documento, fecha de emision y 'recibida el'): '%s'"
                % n[:120]
            )
        elif n.startswith("Denuncia remitida") and k != 1:
            fallos.append("R-167: la nota del traslado debe ser la nota 1")
    return fallos


def prueba_r171_encabezado(z) -> list[str]:
    """R-171: cada linea del encabezado es «ETIQUETA<tab>:<tab>VALOR», con los
    dos puntos en su columna. La anonimizacion v2.3.1 dejo «DENUNCIANTE:[...]»
    con las tabulaciones al final y el encabezado salia descuadrado (queja del
    instructor, Exp. 2898-2026)."""
    x = z.read("word/document.xml").decode("utf-8", "replace")
    fallos = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", x, re.S)[:14]:
        t = re.sub(r"<[^>]+>", "", re.sub(r"<w:tab ?/>", "	", p)).strip()
        m = re.match(
            r"^(DENUNCIANTES?|DENUNCIAD[OA]S?(?:\(S\))?|EXPEDIENTE|MATERIAS?)(?![A-Za-z(])",
            t,
        )
        if m and not re.match(r"^%s ?	: *	\S" % re.escape(m.group(1)), t):
            fallos.append("R-171: encabezado descuadrado: %r" % t[:70])
    return fallos


def prueba_r174_tipografia(z) -> list[str]:
    """R-174: cuerpo en Arial Narrow 11 pt (iniciales «LSQ/DCQ» en 8 pt); notas al
    pie en Arial Narrow 8 pt, cada una seguida de una linea en blanco. Mandato del
    instructor (23/09/2026); aplicado a las 577 plantillas."""
    sys.path.insert(0, str(pathlib_Path(__file__).resolve().parent / "migraciones"))
    import uniformar_tipografia as UT

    x = z.read("word/document.xml").decode("utf-8", "replace")
    try:
        fx = z.read("word/footnotes.xml").decode("utf-8", "replace")
    except KeyError:
        fx = ""
    return UT.falsar(x, fx)


def prueba_r177_sin_marcas_markdown(doc) -> list[str]:
    """R-177: el texto no lleva marcas de markdown («__A La Positiva__», «**x**»).
    El subrayado y la negrita son formato del run, no caracteres: en el Exp.
    2898-2026 el agente escribio «__A La Positiva__:» y Word mostro los guiones."""
    fallos = []
    for p in doc:
        m = re.search(r"__\S|\S__|\*\*[A-Za-zÁÉÍÓÚÑáéíóúñ]", p.texto)
        if m:
            fallos.append("R-177: marca de markdown en el texto: '%s'" % p.texto[:80])
    return fallos[:3]


def prueba_r179_numeracion_pegada(z) -> list[str]:
    """R-179: un numeral escrito a mano («9.», «(v)») va seguido de tabulacion.
    En el Exp. 2835-2026 salieron «9.La Secretaria…» y «(v)en caso…»: sin la
    tabulacion el parrafo pierde la sangria francesa. El corpus numera con
    numPr (0 de 574 pegados)."""
    x = z.read("word/document.xml").decode("utf-8", "replace")
    fallos = []
    for p in re.findall(r"<w:p\b.*?</w:p>", x, re.S):
        s = "".join(
            "\t" if m.group(1) else m.group(2)
            for m in re.finditer(r"(<w:tab\s*/>)|<w:t(?:\s[^>]*)?>([^<]*)</w:t>", p)
        )
        if re.match(r"\s*(?:\d{1,2}\.|\((?:[ivxl]+|[a-z])\))[A-Za-zÁÉÍÓÚÑáéíóúñ]", s):
            fallos.append("R-179: numeral pegado al texto: '%s'" % s.strip()[:60])
    return fallos[:5]


def prueba_r180_numeracion_doble(doc) -> list[str]:
    """R-180: un parrafo con numeracion automatica (numPr) no repite el numeral
    escrito a mano. En el Exp. 2835-2026 salieron «1. 1. Mediante…», «(i) (i)
    El 25…» y «3. II. DE LA INADMISIBILIDAD» (0 de 574 en el corpus)."""
    return [
        "R-180: numeral duplicado (automatico + escrito): '%s'" % p.texto[:60]
        for p in doc
        if p.numerado
        and re.match(r"\s*(?:\d{1,2}\.|\((?:[ivxl]+|[a-z])\)|[IVX]{1,4}\.)\s", p.texto)
    ][:5]


def prueba_r181_imputacion_sin_negrita(doc) -> list[str]:
    """R-181: las imputaciones del resolutivo («Presunta infraccion…») no van en
    negrita (0 de 574). En el Exp. 2898-2026 las dos añadidas por 88.1 salieron
    enteras en negrita."""
    fallos = []
    for p in doc:
        if not p.texto.strip().startswith("Presunta infracci"):
            continue
        total = sum(len(t) for t, _b in p.runs_bold)
        negrita = sum(len(t) for t, b in p.runs_bold if b)
        if total and negrita * 2 > total:
            fallos.append("R-181: imputacion en negrita: '%s'" % p.texto[:60])
    return fallos[:3]


# Norma citada en la calificacion -> encabezado de su nota al pie. Solo las que el
# corpus anota siempre (0 de 574 sin nota); 18/19 y 1-2 tienen excepciones.
NORMAS_CON_NOTA = {
    r"numeral 88\.1 del art[ií]culo 88": r"Art[ií]culo 88\b",
    r"literal e\) del art[ií]culo 47": r"Art[ií]culo 47\b",
    r"numeral 49\.1": r"Art[ií]culo 49\b",
}


def prueba_r182_nota_de_la_norma(doc, z) -> list[str]:
    """R-182: la norma con que se califica un hecho (88.1, 47 e), 49.1) tiene su
    nota al pie en el documento. En el Exp. 2898-2026 las dos imputaciones por
    88.1 añadidas no la llevaban (usar `insertar_despues` con `nota`)."""
    try:
        fx = z.read("word/footnotes.xml").decode("utf-8", "replace")
    except KeyError:
        fx = ""
    notas = "".join(re.findall(r"<w:t(?:\s[^>]*)?>([^<]*)</w:t>", fx))
    fallos = set()
    for p in doc:
        if "corresponde calificar" not in p.texto:
            continue
        for norma, cabecera in NORMAS_CON_NOTA.items():
            m = re.search(norma, p.texto)
            if m and not re.search(cabecera, notas):
                fallos.add(
                    "R-182: se califica por «%s» y ninguna nota al pie la transcribe"
                    % m.group(0)
                )
    return sorted(fallos)


def prueba_r176_credito_enmascarado(doc) -> list[str]:
    """R-176: numero de credito, tarjeta o cuenta con los digitos del medio
    enmascarados (en el corpus: «100xxxxxx434», «34****83»). La poliza nunca."""
    fallos = []
    for p in doc:
        for m in re.finditer(
            r"\b(?:[Cc]r[ée]dito(?: [Vv]ehicular| [Hh]ipotecario| [Pp]ersonal)?|[Tt]arjeta(?: de [Cc]r[ée]dito)?|[Cc]uenta)(?: N[°º.]?)? (\d{5,})\b",
            p.texto,
        ):
            fallos.append("R-176: %s sin enmascarar los digitos del medio" % m.group(0))
    return fallos[:3]


def prueba_r173_notas_traslado(z) -> list[str]:
    """R-173: el parrafo resolutivo del traslado lleva SIEMPRE dos notas al pie,
    cada una detras de la norma que anota (art. 26 del D. Leg. 807 y art. 223 del
    TUO de la Ley 27444), con el texto de docs/notas_traslado.json. Mandato del
    instructor, 23/09/2026; aplicado a las 577 plantillas."""
    sys.path.insert(0, str(pathlib_Path(__file__).resolve().parent / "migraciones"))
    import notas_traslado as NT

    x = z.read("word/document.xml").decode("utf-8", "replace")
    try:
        fx = z.read("word/footnotes.xml").decode("utf-8", "replace")
    except KeyError:
        fx = ""
    return NT.notas_ancladas(x, fx)


def prueba_r168_word_abre(z) -> list[str]:
    """R-168: el .docx debe abrir en Word sin «contenido no legible». Causa medida
    (v2.3.0): prefijos de espacio de nombres renombrados (ns0, ns1...) y
    `mc:Ignorable` citando prefijos no declarados. Afecto a las 577 plantillas."""
    import reparar_espacios_nombres as R

    try:
        return (
            [
                "R-168: Word no abrira el documento (espacios de nombres rotos: prefijos nsN o mc:Ignorable sin declarar)"
            ]
            if R.necesita(z)
            else []
        )
    except Exception as exc:
        return ["R-168: no se pudo comprobar la estructura: %s" % exc]


def prueba_r169_un_reclamo_por_imputacion(doc) -> list[str]:
    """R-169: el numeral 88.1 se imputa UN reclamo por imputacion (167 de 167 en
    el corpus). Varios reclamos -> varias imputaciones, cada una con su fecha."""
    fallos = []
    for p in doc:
        t = p.texto.strip()
        cab = t.split(" en tanto ")[0]
        if (
            t.startswith("Presunta infracci")
            and "88.1" in cab
            and re.search(r"\breclamos\b", t)
        ):
            fallos.append(
                "R-169: una imputacion por 88.1 agrupa varios reclamos: '%s'" % t[:140]
            )
    return fallos


def prueba_r170_subrayado_parcial(z) -> list[str]:
    """R-170: el subrayado es parcial (882 parrafos); un parrafo entero subrayado
    es desviacion (3 en el corpus). En el requerimiento solo se subraya «A X»."""
    x = z.read("word/document.xml").decode("utf-8", "replace")
    fallos = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", x, re.S):
        runs = re.findall(r"<w:r[ >].*?</w:r>", p, re.S)
        tot = sum(len(re.sub(r"<[^>]+>", "", r)) for r in runs)
        und = sum(
            len(re.sub(r"<[^>]+>", "", r))
            for r in runs
            if re.search(r'<w:u w:val="(?!none)', r)
        )
        if tot > 80 and und > 0.8 * tot:
            fallos.append(
                "R-170: parrafo entero subrayado: '%s'"
                % re.sub(r"<[^>]+>", "", p)[:100]
            )
    return fallos[:4]


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


# --------------------------------------------------------------------------- #
# v3.1 (revision del instructor del 24/09/2026, admisorio de prueba 9999-2026).
# Cada prueba es la forma GENERAL de un defecto hallado pagina por pagina.
# --------------------------------------------------------------------------- #

sys.path.insert(0, str(pathlib_Path(__file__).resolve().parent))
import notas_pie as _N  # noqa: E402

RE_ASEGURADORA = re.compile(
    r"SEGUROS|REASEGUROS|ASEGURADORA|R[IÍ]MAC|PAC[IÍ]FICO|MAPFRE|INTERSEGURO|"
    r"POSITIVA|CARDIF|PROTECTA|CRECER|CHUBB|Q[UÚ]ALITAS|VIVIR|SANITAS",
    re.I,
)
RE_SOCIEDAD = re.compile(r"\s+(?:S\.A\.A\.|S\.A\.C\.|S\.A\.?|E\.P\.S\.)\s*$")


def _xml(z, nombre: str) -> str:
    try:
        return z.read(nombre).decode("utf-8", "replace")
    except KeyError:
        return ""


def encabezado(doc) -> dict:
    """Partes del encabezado: [(nombre, alias)] de denunciantes y denunciados."""
    textos = [p.texto.strip() for p in doc[:30]]
    salida = {"denunciantes": [], "denunciados": []}
    actual = None
    for t in textos:
        u = sin_tildes(t).upper()
        if re.match(r"DENUNCIANTE", u):
            actual = "denunciantes"
        elif re.match(r"DENUNCIAD", u):
            actual = "denunciados"
        elif re.match(r"(MATERIA|RESOLUCION|EXPEDIENTE|LIMA,)", u):
            actual = None
        if actual is None or not t:
            continue
        cuerpo = re.sub(r"(?i)^DENUNCIA(?:NTE|D[OA])S?\s*(\(S\))?\s*:?\s*", "", t).strip()
        for m in re.finditer(r"([^()]+?)\s*\(([^)]+)\)", cuerpo):
            salida[actual].append((m.group(1).strip(" ,;y"), m.group(2).strip()))
    return salida


def _nucleos(doc) -> list[tuple[str, str]]:
    """(seccion, nucleo) de cada imputacion: considerativa y resolutivo."""
    salida = []
    for p in doc:
        m = re.search(
            r"consistente en que (.+?)(?:;\s*involucrar|\.\s*Por consiguiente)", p.texto, re.S
        )
        if m:
            salida.append(("considerativa", re.sub(r"\s+", " ", m.group(1)).strip()))
        m = re.search(r"Presunta infracci[oó]n .*?, en tanto (.+?)\s*\.\s*$", p.texto, re.S)
        if m:
            salida.append(("resolutivo", re.sub(r"\s+", " ", m.group(1)).strip()))
    return salida


def _clave(t: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9 ]", " ", sin_tildes(t).upper())).strip()


def _nucleo_nombre(nombre: str) -> str:
    return _clave(RE_SOCIEDAD.sub("", nombre))


def prueba_r183_notas_integras(doc, z) -> list[str]:
    """R-183: toda llamada tiene su nota y toda nota su llamada. Falsador medido
    (9999-2026): borrar un parrafo dejo su nota huerfana y el visor corrio el
    texto de todas las notas siguientes una posicion."""
    x, fx = _xml(z, "word/document.xml"), _xml(z, "word/footnotes.xml")
    if not fx:
        return []
    fallos = []
    ns = _N.notas(fx)
    for ll in _N.llamadas(x):
        if ll["id"] not in ns:
            fallos.append("R-183: la llamada %s no tiene nota" % ll["id"])
    _x, _fx, inf = _N.normalizar(x, fx)
    if inf["huerfanas"]:
        fallos.append("R-183: nota(s) sin llamada: %s" % ", ".join(inf["huerfanas"]))
    return fallos


def prueba_r184_anclas(doc, z) -> list[str]:
    """R-184: cada nota canonica va detras de su ancla (docs/anclas_notas.json)."""
    return [
        "R-184: la nota %s (%s) no va tras «%s»; va tras «…%s»"
        % (f["id"], f["tipo"], f["ancla"], f["previo"].strip()[-40:])
        for f in _N.anclas_incumplidas(_xml(z, "word/document.xml"), _xml(z, "word/footnotes.xml"))
    ]


def prueba_r185_llamadas_pegadas(doc, z) -> list[str]:
    """R-185: nunca dos llamadas de nota seguidas («²³»): cada nota va en su ancla."""
    return [
        "R-185: la llamada %s va pegada a la anterior tras «…%s»" % (ll["id"], ll["previo"][-40:])
        for ll in _N.llamadas_pegadas(_xml(z, "word/document.xml"))
    ]


def prueba_r186_nota_corresponde(doc, z) -> list[str]:
    """R-186: la nota transcribe la norma que cita la frase que la llama (la
    imputacion por el literal e) del articulo 47 no lleva la nota de los
    articulos 18 y 19)."""
    return [
        "R-186: la frase «…%s» cita el articulo %s y su nota %s transcribe el %s"
        % (f["tramo"].strip()[-50:], "/".join(f["citados"]), f["id"], "/".join(f["transcritos"]))
        for f in _N.notas_que_no_corresponden(_xml(z, "word/document.xml"), _xml(z, "word/footnotes.xml"))
    ]


def prueba_r187_forma_notas(doc, z) -> list[str]:
    """R-187: forma de cada nota: tabulacion tras la llamada, sin lineas en
    blanco internas, sin dobles espacios, con el titulo de la norma; y la
    transcripcion completa de sus literales (docs/textos_normativos.json)."""
    fx = _xml(z, "word/footnotes.xml")
    fallos = ["R-187: " + f for f in _N.defectos_de_forma(fx)]
    fallos += ["R-187: " + f for f in _N.transcripciones_incompletas(fx)]
    return fallos[:8]


def prueba_r188_denominacion(doc) -> list[str]:
    """R-188: como se nombra a cada parte en las imputaciones (instructor, 24/09/2026).

    - La denunciante, con su nombre completo («la señora María Prueba
      Ficticia»), nunca con la tratativa corta de los hechos («la señora Prueba»).
    - Una aseguradora UNICA denunciada: «la compañía aseguradora», nunca su
      razon social ni su alias.
    - Con dos o mas denunciados: nunca «la compañía aseguradora» ni «el
      proveedor denunciado»; cada proveedor con su razon social completa, no
      con su alias; «los proveedores denunciados» solo si son exactamente dos
      (imputacion conjunta; con tres o mas, los nombres, AGENTS §5).
    """
    enc = encabezado(doc)
    ddos = enc["denunciados"]
    n = len(ddos)
    fallos = []
    for seccion, nucleo in _nucleos(doc):
        clave = _clave(nucleo)
        for nombre, alias in enc["denunciantes"]:
            m = re.match(r"(SENORA?|SENORITA)\s+(.+)", _clave(alias))
            if m and re.search(r"\b%s %s\b" % (m.group(1), re.escape(m.group(2))), clave):
                fallos.append(
                    "R-188: la imputacion (%s) dice «%s %s»: va el nombre completo «%s»"
                    % (seccion, m.group(1).lower(), m.group(2).title(), nombre.title())
                )
        if n == 1 and RE_ASEGURADORA.search(ddos[0][0]):
            nucleo_rs = _nucleo_nombre(ddos[0][0])
            alias = _clave(ddos[0][1])
            if (nucleo_rs and nucleo_rs in clave) or re.search(r"\b%s\b" % re.escape(alias), clave):
                fallos.append(
                    "R-188: aseguradora unica denunciada: en la imputacion (%s) va «la compañía aseguradora»"
                    % seccion
                )
            elif "COMPANIA ASEGURADORA" not in clave:
                fallos.append(
                    "R-188: aseguradora unica denunciada: la imputacion (%s) no dice «la compañía aseguradora»"
                    % seccion
                )
        if n >= 2:
            if "COMPANIA ASEGURADORA" in clave:
                fallos.append("R-188: con %d denunciados no existe «la compañía aseguradora» (%s)" % (n, seccion))
            if "EL PROVEEDOR DENUNCIADO" in clave:
                fallos.append("R-188: con %d denunciados no existe «el proveedor denunciado» (%s)" % (n, seccion))
            for nombre, alias in ddos:
                a = _clave(alias)
                nr = _nucleo_nombre(nombre)
                if a and re.search(r"\b%s\b" % re.escape(a), clave) and nr not in clave:
                    fallos.append(
                        "R-188: la imputacion (%s) nombra a «%s» por su alias: va la razon social completa"
                        % (seccion, alias.title())
                    )
        if n >= 3 and "LOS PROVEEDORES DENUNCIADOS" in clave:
            fallos.append("R-188: con 3 o mas denunciados, los nombres de los implicados (AGENTS §5)")
        if n == 1 and "LOS PROVEEDORES DENUNCIADOS" in clave:
            fallos.append("R-188: con un denunciado no existe «los proveedores denunciados»")
    return sorted(set(fallos))[:6]


def _tramo(doc, desde: str, hasta: str):
    dentro = False
    for p in doc:
        u = sin_tildes(p.texto).upper()
        if desde in u and len(p.texto) < 90:
            dentro = True
            continue
        if dentro and hasta in u and len(p.texto) < 90:
            return
        if dentro:
            yield p


def prueba_r189_rotulo_requerimiento(doc) -> list[str]:
    """R-189: el rotulo del requerimiento de la considerativa es el ALIAS del
    encabezado («Al Banco:», «A Rímac:»), no la razon social (instructor, 24/09/2026)."""
    alias = {_clave(a) for _n, a in encabezado(doc)["denunciados"]}
    if not alias:
        return []
    fallos = []
    for p in _tramo(doc, "REQUERIMIENTO DE INFORMACION", "RESOLUCION DE LA SECRETARIA"):
        m = re.match(r"\s*A(?:l)?\s+(.{2,90}?)\s*:\s*\(i\)", p.texto)
        if m and _clave(m.group(1)) not in alias:
            fallos.append(
                "R-189: rotulo «%s:» del requerimiento: va el alias del encabezado (%s)"
                % (p.texto[: m.end(1)].strip(), ", ".join(sorted(a.title() for a in alias)))
            )
    return fallos


RE_RAZON_SOCIAL = re.compile(
    r"((?:[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÑáéíóúñ&.'-]*\s+)(?:(?:[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÑáéíóúñ&.'-]*|de|del|la|las|los|y|e)\s+){0,8})"
    r"(?:S\.A\.A\.|S\.A\.C\.|S\.A\.?|E\.P\.S\.)(?![\w])"
)


def prueba_r190_partes_y_concordancia(doc) -> list[str]:
    """R-190: el documento solo nombra a sus partes y concuerda con ellas.

    - Ninguna razon social que no este en el encabezado (residuo de plantilla:
      «Pacífico Compañía de Seguros y Reaseguros S.A.» en un caso contra otros).
    - «notificarles» si el ordinal requiere a varias partes («reciban»,
      «efectúen»); «notificarle» si a una.
    - Articulo ante la razon social: «al Banco…», nunca «a Banco…».
    """
    enc = encabezado(doc)
    nucleos = [_nucleo_nombre(n) for n, _a in enc["denunciados"]]
    fallos = []
    cuerpo = doc[12:]
    for p in cuerpo:
        # Las razones sociales se cotejan en los ordinales del resolutivo, que es
        # donde se nombra a quien se admite, requiere, traslada o notifica. En
        # los hechos puede aparecer un tercero real (la empleadora del SCTR).
        entidades = RE_RAZON_SOCIAL.finditer(p.texto) if RE_ORDINAL.match(p.texto.strip()) else ()
        for m in entidades:
            ent = _clave(m.group(1))
            palabras = ent.split()
            ok = any(
                nr and (nr in ent or ent in nr or " ".join(palabras[-3:]) in nr)
                for nr in nucleos
            )
            if not ok and nucleos:
                fallos.append("R-190: «%s» no es parte del caso (residuo)" % m.group(0).strip()[-70:])
        t = p.texto
        if re.search(r"\bnotificarle\b", t) and re.search(r"\b(reciban|efect[uú]en)\b", t):
            fallos.append("R-190: varias partes y «notificarle»: va «notificarles»")
        if re.search(r"\bnotificarles\b", t) and re.search(r"\b(reciba|efect[uú]e)\b", t):
            fallos.append("R-190: una parte y «notificarles»: va «notificarle»")
    return sorted(set(fallos))[:6]


def prueba_r195_articulo_ante_razon_social(doc) -> list[str]:
    """R-195 (observacion): una razon social que empieza por un nombre comun
    lleva articulo: «al Banco…», «de la Caja…», no «a Banco…». El instructor no
    lo fijo como regla (24/09/2026): se eleva, no bloquea."""
    fallos = []
    for p in doc[12:]:
        for m in re.finditer(
            r"(?<![\wáéíóú])(a|de)\s+(Banco|Caja|Financiera|Empresa|Cooperativa|Edpyme|Corporaci[oó]n)\s+[A-ZÁÉÍÓÚ]",
            p.texto,
        ):
            fallos.append("R-195: «%s»: ¿falta el articulo?" % m.group(0)[:-2])
    return sorted(set(fallos))[:4]


def prueba_r191_numeracion_continua(doc) -> list[str]:
    """R-191: la considerativa se numera con UNA sola serie (en el 9999-2026 salio
    «(i)», «3.», «4.»: el primer parrafo heredo la lista de otro nivel)."""
    series = Counter()
    ejemplo = {}
    for p in _tramo(doc, "DE LA ADMISION A TRAMITE", "RESOLUCION DE LA SECRETARIA"):
        t = p.texto.strip()
        if not p.numerado or not t or t.upper() == t:
            continue
        clave = (p.numid, p.ilvl)
        series[clave] += 1
        ejemplo.setdefault(clave, t[:50])
    if len(series) > 1:
        minoritaria = min(series, key=lambda k: series[k])
        return [
            "R-191: la considerativa mezcla %d numeraciones; «%s…» no sigue la serie de los demas"
            % (len(series), ejemplo[minoritaria])
        ]
    return []


def prueba_r192_subrayado(doc) -> list[str]:
    """R-192: solo se subraya el rotulo del requerimiento («A La Positiva:»),
    nunca frases del cuerpo (NOVENO, instructor 24/09/2026)."""
    fallos = []
    for p in doc[8:]:
        sub = "".join(t for t, u in p.runs_und if u)
        if not sub.strip():
            continue
        rotulo = re.match(r"\s*A(?:l| la)?\s+[^:,.]{2,60}:", p.texto)
        if rotulo and sub.strip() and sub.strip() in rotulo.group(0):
            continue
        fallos.append("R-192: subrayado fuera del rotulo del requerimiento: «%s»" % sub.strip()[:60])
    return fallos[:4]


FIRMANTES = ("EVELING ROA QUISPE", "LUISA ANALI SILVA MALPARTIDA")


def prueba_r193_firmado_digitalmente(doc) -> list[str]:
    """R-193: el bloque de firma tiene cuatro lineas; la primera es «Firmado
    digitalmente por» (instructor, 24/09/2026)."""
    for k, p in enumerate(doc):
        if sin_tildes(p.texto).strip().upper() in FIRMANTES:
            previo = next((q.texto.strip() for q in reversed(doc[:k]) if q.texto.strip()), "")
            if previo != "Firmado digitalmente por":
                return ["R-193: falta «Firmado digitalmente por» sobre el nombre de la firmante"]
            return []
    return []


def prueba_r194_separadores(z) -> list[str]:
    """R-194b: cada linea en blanco del cuerpo mide una linea (espaciado 0/0,
    interlineado sencillo), no la herencia de 8 pt del estilo por defecto."""
    x = _xml(z, "word/document.xml")
    ps = list(_N.RE_P.finditer(x))
    textos = [_N.texto(m.group(0)) for m in ps]
    ini = next((k for k, t in enumerate(textos) if sin_tildes(t).strip().upper().startswith("HECHOS")), None)
    ords = [k for k, t in enumerate(textos) if RE_ORDINAL.match(t.strip())]
    if ini is None or not ords:
        return []
    malos = 0
    for k in range(ini + 1, ords[-1]):
        p = ps[k].group(0)
        if textos[k].strip() or re.search(r"<w:numPr>|<w:br\b|<w:sectPr|<w:drawing|footnoteReference", p):
            continue
        sp = re.search(r"<w:spacing\b[^>]*/>", p)
        if not sp or not re.search(r'w:after="0"', sp.group(0)) or re.search(r'w:line="(?!240")', sp.group(0)):
            malos += 1
    return ["R-194: %d linea(s) en blanco con espaciado heredado (miden mas de una linea)" % malos] if malos else []


def prueba_r194_sin_huecos(doc) -> list[str]:
    """R-194: ningun hueco en el cuerpo: nunca dos parrafos vacios seguidos entre
    HECHOS y el ultimo ordinal (el borrado de hechos dejaba sus separadores)."""
    ini = next((k for k, p in enumerate(doc) if sin_tildes(p.texto).strip().upper().startswith("HECHOS")), None)
    ords = [k for k, p in enumerate(doc) if RE_ORDINAL.match(p.texto.strip())]
    if ini is None or not ords:
        return []
    fallos = []
    for k in range(ini, ords[-1]):
        if doc[k].vacio and doc[k + 1].vacio and not doc[k].numerado:
            siguiente = next((q.texto.strip() for q in doc[k + 1 :] if q.texto.strip()), "")
            fallos.append("R-194: dos lineas en blanco seguidas antes de «%s…»" % siguiente[:40])
    return sorted(set(fallos))[:4]



# --------------------------------------------------------------------------
# v3.2 (revision del instructor del 24/09/2026 sobre la remesa de 11 admisorios)
# --------------------------------------------------------------------------

RE_ASEGURADORA_SOLA = re.compile(r"\b(?P<prev>\w+)\s+aseguradora\b")


def prueba_r201_compania_aseguradora(doc) -> list[str]:
    """R-201: nunca «aseguradora» a secas; siempre «compañía aseguradora»
    (tambien en los hechos: «la vendedora de la compañía aseguradora»)."""
    fallos = []
    for p in doc:
        for m in RE_ASEGURADORA_SOLA.finditer(p.texto):
            if m.group("prev").lower() not in ("compañía", "compania"):
                fallos.append("R-201: «%s aseguradora»: va «compañía aseguradora»" % m.group("prev"))
    return fallos[:5]


def prueba_r202_nota_norma_repetida(doc, z) -> list[str]:
    """R-202: la nota de la norma imputada va solo en la PRIMERA imputacion de
    ese articulo; las siguientes imputaciones por la misma norma no la repiten."""
    try:
        fx = z.read("word/footnotes.xml").decode("utf-8", "replace")
        x = z.read("word/document.xml").decode("utf-8", "replace")
    except KeyError:
        return []
    cuerpos = {
        i: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", c))
        for i, c in re.findall(r'<w:footnote (?:(?!/>)[^>])*?w:id="(\d+)"[^>/]*>(.*?)</w:footnote>', fx, re.S)
    }
    vistas, fallos = set(), []
    for par in re.findall(r"<w:p[ >].*?</w:p>", x, re.S):
        t = "".join(re.findall(r"<w:t(?: [^>]*)?>([^<]*)</w:t>", par))
        if not ("considera que el hecho denunciado" in t or t.strip().startswith("Presunta infracci")):
            continue
        for i in re.findall(r'<w:footnoteReference [^>]*w:id="(\d+)"', par):
            c = cuerpos.get(i, "").strip()
            if not c.startswith("LEY 29571") or "culo 105" in c:
                continue
            arts = tuple(re.findall(r"Art[íi]culo (\d+(?:\.\d+)?)\.-", c))
            if arts in vistas:
                fallos.append("R-202: la nota %s repite la norma de una imputacion anterior (arts. %s)" % (i, ", ".join(arts)))
            vistas.add(arts)
    return fallos


RE_SUBJETIVO = re.compile(r"\b(únicamente|solamente|totalmente|absurd[ao]s?|pésim[ao]s?|poco profesionales?)\b", re.I)


def prueba_r203_lexico_objetivo(doc) -> list[str]:
    """R-203: hechos e imputaciones sin palabras valorativas («únicamente»,
    «totalmente», «pésimo», «poco profesionales»): el estilo de las plantillas
    narra lo que consta, sin calificarlo."""
    fallos = []
    for p in list(tramo_hechos(doc)) + [q for q in doc if "consistente en que" in q.texto or q.texto.strip().startswith("Presunta infracci")]:
        m = RE_SUBJETIVO.search(p.texto)
        if m:
            fallos.append("R-203: palabra valorativa «%s»: «…%s…»" % (m.group(1), p.texto[max(0, m.start() - 30) : m.end() + 20]))
    return fallos[:5]


def prueba_r204_adquirio(doc) -> list[str]:
    """R-204: el seguro o la poliza se «adquirió», nunca «contaba con»."""
    return [
        "R-204: «%s»: va «adquirió»" % m.group(0)
        for p in doc
        for m in re.finditer(r"\bcontaba(?:n)? con (?:el|la|un|una) (?:Seguro|seguro|P[óo]liza|p[óo]liza)", p.texto)
    ][:3]


def prueba_r205_la_denunciante(doc) -> list[str]:
    """R-205: en las imputaciones se escribe «la denunciante» (o «el
    denunciante»), nunca «la parte denunciante»."""
    return [
        "R-205: imputacion (%s) con «la parte denunciante»: va «la denunciante»" % seccion
        for seccion, nucleo in _nucleos(doc)
        if re.search(r"\bparte denunciante\b", nucleo)
    ][:3]


RE_FECHAS_UNIDAS = re.compile(
    r"\bsolicitudes\b[^.;]*?\b\d{1,2}(?: de \w+)?(?: de \d{4})?,? (?:y|e|,) (?:el )?\d{1,2} de \w+", re.I
)
RE_COBERTURAS_UNIDAS = re.compile(r"\bcobertura[s]? (?:de )?[^,;.]{3,60}? y (?:de )?la cobertura\b", re.I)


def prueba_r206_una_imputacion_por_hecho(doc) -> list[str]:
    """R-206: una imputacion por cada solicitud y por cada cobertura
    diferenciada, aunque se hayan pedido en una misma solicitud: nunca «pese a
    sus solicitudes del 1 y el 23 de marzo», nunca «la cobertura de sepelio y
    la cobertura oncológica» en un mismo nucleo."""
    fallos = []
    for seccion, nucleo in _nucleos(doc):
        if RE_FECHAS_UNIDAS.search(nucleo):
            fallos.append("R-206: imputacion (%s) que une varias solicitudes: una por solicitud" % seccion)
        if RE_COBERTURAS_UNIDAS.search(nucleo):
            fallos.append("R-206: imputacion (%s) que une varias coberturas: una por cobertura" % seccion)
    return fallos[:4]

PRUEBAS = [
    (
        "R-201 compañía aseguradora, nunca aseguradora a secas",
        lambda d, s, z: prueba_r201_compania_aseguradora(d),
        "falsador",
    ),
    (
        "R-202 nota de la norma imputada solo en la primera imputacion",
        lambda d, s, z: prueba_r202_nota_norma_repetida(d, z),
        "falsador",
    ),
    (
        "R-203 hechos e imputaciones sin palabras valorativas",
        lambda d, s, z: prueba_r203_lexico_objetivo(d),
        "falsador",
    ),
    (
        "R-204 el seguro se adquirio",
        lambda d, s, z: prueba_r204_adquirio(d),
        "falsador",
    ),
    (
        "R-205 la denunciante en las imputaciones",
        lambda d, s, z: prueba_r205_la_denunciante(d),
        "falsador",
    ),
    (
        "R-206 una imputacion por solicitud y por cobertura",
        lambda d, s, z: prueba_r206_una_imputacion_por_hecho(d),
        "falsador",
    ),
    (
        "R-183 notas integras (llamada <-> nota)",
        lambda d, s, z: prueba_r183_notas_integras(d, z),
        "falsador",
    ),
    (
        "R-184 notas canonicas en su ancla",
        lambda d, s, z: prueba_r184_anclas(d, z),
        "falsador",
    ),
    (
        "R-185 sin llamadas de nota pegadas",
        lambda d, s, z: prueba_r185_llamadas_pegadas(d, z),
        "falsador",
    ),
    (
        "R-186 la nota transcribe la norma citada",
        lambda d, s, z: prueba_r186_nota_corresponde(d, z),
        "falsador",
    ),
    (
        "R-187 forma y literales de las notas",
        lambda d, s, z: prueba_r187_forma_notas(d, z),
        "falsador",
    ),
    (
        "R-188 denominacion de las partes en las imputaciones",
        lambda d, s, z: prueba_r188_denominacion(d),
        "falsador",
    ),
    (
        "R-189 rotulo del requerimiento con el alias",
        lambda d, s, z: prueba_r189_rotulo_requerimiento(d),
        "falsador",
    ),
    (
        "R-190 partes del caso y concordancia",
        lambda d, s, z: prueba_r190_partes_y_concordancia(d),
        "falsador",
    ),
    (
        "R-191 numeracion continua de la considerativa",
        lambda d, s, z: prueba_r191_numeracion_continua(d),
        "falsador",
    ),
    (
        "R-192 subrayado solo en el rotulo del requerimiento",
        lambda d, s, z: prueba_r192_subrayado(d),
        "falsador",
    ),
    (
        "R-193 Firmado digitalmente por",
        lambda d, s, z: prueba_r193_firmado_digitalmente(d),
        "falsador",
    ),
    (
        "R-195 articulo ante la razon social",
        lambda d, s, z: prueba_r195_articulo_ante_razon_social(d),
        "observacion",
    ),
    (
        "R-194b lineas en blanco de una linea",
        lambda d, s, z: prueba_r194_separadores(z),
        "falsador",
    ),
    (
        "R-194 sin huecos en el cuerpo",
        lambda d, s, z: prueba_r194_sin_huecos(d),
        "falsador",
    ),
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
        "R-161 fechas 'de AAAA' y 'recibida'",
        lambda d, s, z: prueba_r161_fechas(d, z),
        "falsador",
    ),
    (
        "R-163 ordinales consecutivos",
        lambda d, s, z: prueba_r163_ordinales_consecutivos(d),
        "falsador",
    ),
    (
        "R-164 negrita solo en el rotulo del ordinal",
        lambda d, s, z: prueba_r164_negrita_solo_rotulo(d),
        "falsador",
    ),
    (
        "R-165 expectativas solo en idoneidad",
        lambda d, s, z: prueba_r165_expectativas_solo_idoneidad(d),
        "falsador",
    ),
    (
        "R-167 nota al pie 1 canonica",
        lambda d, s, z: prueba_r167_nota_uno(z),
        "falsador",
    ),
    (
        "R-171 encabezado en columna",
        lambda d, s, z: prueba_r171_encabezado(z),
        "falsador",
    ),
    (
        "R-177 sin marcas de markdown",
        lambda d, s, z: prueba_r177_sin_marcas_markdown(d),
        "falsador",
    ),
    (
        "R-179 numeral seguido de tabulacion",
        lambda d, s, z: prueba_r179_numeracion_pegada(z),
        "falsador",
    ),
    (
        "R-180 numeracion no duplicada",
        lambda d, s, z: prueba_r180_numeracion_doble(d),
        "falsador",
    ),
    (
        "R-181 imputacion sin negrita",
        lambda d, s, z: prueba_r181_imputacion_sin_negrita(d),
        "falsador",
    ),
    (
        "R-182 nota al pie de la norma imputada",
        lambda d, s, z: prueba_r182_nota_de_la_norma(d, z),
        "falsador",
    ),
    (
        "R-176 credito enmascarado",
        lambda d, s, z: prueba_r176_credito_enmascarado(d),
        "falsador",
    ),
    (
        "R-174 tipografia uniforme",
        lambda d, s, z: prueba_r174_tipografia(z),
        "falsador",
    ),
    (
        "R-173 notas al pie del traslado",
        lambda d, s, z: prueba_r173_notas_traslado(z),
        "falsador",
    ),
    (
        "R-168 Word abre el documento",
        lambda d, s, z: prueba_r168_word_abre(z),
        "falsador",
    ),
    (
        "R-169 un reclamo por imputacion (88.1)",
        lambda d, s, z: prueba_r169_un_reclamo_por_imputacion(d),
        "falsador",
    ),
    (
        "R-170 subrayado parcial",
        lambda d, s, z: prueba_r170_subrayado_parcial(z),
        "falsador",
    ),
    (
        "R-143b normas en consulta y articulo 24",
        lambda d, s, z: prueba_r143_consulta(d),
        "observacion",
    ),
    (
        "R-162 huella de formato frente al perfil CC1",
        lambda d, s, z: prueba_r162_huella(z),
        "observacion",
    ),
]


def prueba_r162_huella(z) -> list[str]:
    """R-162 (F6): contraste con docs/estilo_formato.json (moda medida del corpus):
    fuente, tamano, alineacion, interlineado, sangrias, margenes, resaltados."""
    import medir_formato

    return [
        "R-162: " + o
        for o in medir_formato.comparar(
            medir_formato.medir_docx(pathlib_Path(z.filename))
        )
    ]


def verificar(ruta: str) -> bool:
    print("=" * 78)
    print(ruta)
    print("=" * 78)
    try:
        doc, secciones, z = leer_documento(ruta)
    except ET.ParseError as exc:
        # Exp. 2835-2026: document.xml reescrito con ElementTree (ns0:, w14 sin
        # declarar). Se reporta como falsador, no como traza.
        print("  [FALLA] R-168 Word abre el documento")
        print(
            "         - R-168: XML ilegible (%s). Reconstruye con construir_admisorio.py;"
            % exc
        )
        print(
            "           nunca escribas el .docx con ElementTree, python-docx ni scripts propios."
        )
        print("  --> NO APTO (1 falsadores, 0 observaciones)")
        print()
        return False
    falsadores, observaciones = [], []
    for etiqueta, prueba, severidad in PRUEBAS:
        try:
            fallos = prueba(doc, secciones, z)
        except Exception as exc:  # documento ilegible: la prueba no corrobora
            fallos = ["%s: no se pudo leer el documento: %s" % (etiqueta[:5], exc)]
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
