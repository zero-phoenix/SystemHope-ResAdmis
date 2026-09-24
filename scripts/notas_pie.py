# -*- coding: utf-8 -*-
"""Notas al pie: una sola fuente para construir, migrar y verificar (v3.1).

Por que existe (revision del instructor, 24/09/2026, admisorio de prueba 9999-2026):
cada defecto de notas que se encontro tenia su causa en un sitio distinto del
sistema, y cada sitio lo resolvia (o no) a su manera. Aqui vive la regla una vez;
`construir_admisorio.py` la aplica, `migraciones/migrar_v3_1.py` la lleva al
corpus y `verificar_admisorio.py` la falsa.

Conjeturas que este modulo sostiene (R-183 a R-187):

  R-183  Toda nota tiene su llamada y toda llamada su nota; los identificadores
         van 1..n en el orden en que se llaman y footnotes.xml en ese orden.
         Falsador medido: una nota huerfana (su parrafo se borro) hace que el
         visor asigne a cada llamada el texto de la nota vecina.
  R-184  Las notas canonicas van en su ancla (docs/anclas_notas.json): la del
         Codigo detras de «Código de Protección y Defensa del Consumidor»; la de
         competencia detras de «en ejercicio de sus facultades».
  R-185  Nunca dos llamadas seguidas sin texto entre ellas.
  R-186  La nota transcribe la norma que cita la frase que la llama.
  R-187  Forma: tabulacion tras la llamada (todas las lineas alineadas a 1 cm),
         sin lineas en blanco internas (una sola al final, R-174), sin dobles
         espacios, sin parrafos de solo puntuacion, titulo de la norma presente.

Todo se hace sobre el XML como texto: nunca ElementTree escribiendo (R-168).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ANCLAS = RAIZ / "docs" / "anclas_notas.json"
TEXTOS = RAIZ / "docs" / "textos_normativos.json"

RE_FN = re.compile(r'<w:footnote\b[^>]*w:id="(-?\d+)"[^>]*>.*?</w:footnote>', re.S)
RE_REF = re.compile(r'<w:footnoteReference\b[^>]*w:id="(\d+)"[^>]*/>')
RE_P = re.compile(r"<w:p\b[^>]*>.*?</w:p>|<w:p\b[^>]*/>", re.S)
RE_RUN = re.compile(r"<w:r\b[^>]*>(?:(?!</w:r>).)*?</w:r>", re.S)
RE_T = re.compile(r"(<w:t(?:\s[^>/]*)?>)(.*?)(</w:t>)", re.S)


def texto(xml: str) -> str:
    return "".join(m.group(2) for m in RE_T.finditer(xml))


def plano(xml: str) -> str:
    return re.sub(r"\s+", " ", texto(xml)).strip()


def desescapar(t: str) -> str:
    return t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")


# --------------------------------------------------------------------------- #
# Lectura
# --------------------------------------------------------------------------- #


def notas(fx: str) -> dict[str, str]:
    """id -> texto plano de cada nota real (id > 0)."""
    return {
        m.group(1): desescapar(plano(m.group(0)))
        for m in RE_FN.finditer(fx)
        if int(m.group(1)) > 0
    }


def llamadas(x: str) -> list[dict]:
    """Cada llamada del cuerpo: id, texto previo en su parrafo (desde la llamada
    anterior del mismo parrafo) y si va pegada a la llamada anterior."""
    salida = []
    for p in RE_P.finditer(x):
        previo, desde_ultima, hubo = "", "", False
        for m in re.finditer(
            r'<w:footnoteReference\b[^>]*w:id="(\d+)"[^>]*/>|(<w:t(?:\s[^>/]*)?>)(.*?)</w:t>',
            p.group(0),
            re.S,
        ):
            if m.group(1):
                salida.append(
                    {
                        "id": m.group(1),
                        "previo": desescapar(previo),
                        "tramo": desescapar(desde_ultima),
                        "pegada": hubo and not desde_ultima.strip(),
                        "parrafo": desescapar(texto(p.group(0))),
                    }
                )
                desde_ultima, hubo = "", True
            else:
                previo += m.group(3)
                desde_ultima += m.group(3)
    return salida


def cargar_anclas() -> list[dict]:
    try:
        return json.loads(ANCLAS.read_text(encoding="utf-8"))["anclas"]
    except Exception:
        return []


def cargar_textos() -> list[dict]:
    try:
        return json.loads(TEXTOS.read_text(encoding="utf-8"))["exigencias"]
    except Exception:
        return []


def _norm(t: str) -> str:
    return re.sub(r"\s+", " ", t).strip()


# --------------------------------------------------------------------------- #
# R-183: integridad y orden
# --------------------------------------------------------------------------- #


def normalizar(x: str, fx: str) -> tuple[str, str, dict]:
    """Quita las notas huerfanas y renumera 1..n en orden de llamada.

    Devuelve (document.xml, footnotes.xml, informe). Una llamada sin nota se
    deja (la falsa el verificador): inventar el texto de una nota es peor.
    """
    orden: list[str] = []
    for i in RE_REF.findall(x):
        if i not in orden:
            orden.append(i)
    elems = list(RE_FN.finditer(fx))
    if not elems:
        return x, fx, {"huerfanas": [], "renumeradas": False}
    sep = [m.group(0) for m in elems if int(m.group(1)) <= 0]
    reales = {m.group(1): m.group(0) for m in elems if int(m.group(1)) > 0}
    huerfanas = [i for i in reales if i not in orden]
    nuevo = {viejo: str(k + 1) for k, viejo in enumerate(i for i in orden if i in reales)}
    renumerar = any(k != v for k, v in nuevo.items())
    x2 = re.sub(
        r'(<w:footnoteReference\b[^>]*w:id=")(\d+)(")',
        lambda g: g.group(1) + nuevo.get(g.group(2), g.group(2)) + g.group(3),
        x,
    )
    cuerpo = []
    for viejo in orden:
        if viejo not in reales:
            continue
        cuerpo.append(
            re.sub(
                r'(<w:footnote\b[^>]*w:id=")(\d+)(")',
                lambda g: g.group(1) + nuevo[viejo] + g.group(3),
                reales[viejo],
                count=1,
            )
        )
    fx2 = fx[: elems[0].start()] + "".join(sep) + "".join(cuerpo) + fx[elems[-1].end():]
    return x2, fx2, {"huerfanas": huerfanas, "renumeradas": renumerar}


# --------------------------------------------------------------------------- #
# R-187: forma de cada nota
# --------------------------------------------------------------------------- #


def _colapsar_espacios_parrafo(p: str) -> str:
    """Dobles espacios dentro de un parrafo, tambien entre runs contiguos."""
    trozos = list(RE_T.finditer(p))
    if not trozos:
        return p
    textos = [m.group(2) for m in trozos]
    for k in range(len(textos)):
        textos[k] = re.sub(r"(?<=\S) {2,}(?=\S)", " ", textos[k])
        textos[k] = re.sub(r" {2,}", " ", textos[k])
    for k in range(1, len(textos)):
        j = k - 1
        while j >= 0 and textos[j] == "":
            j -= 1
        if j >= 0 and textos[j].endswith(" ") and textos[k].startswith(" "):
            textos[k] = textos[k].lstrip(" ")
    piezas, fin = [], 0
    for m, t in zip(trozos, textos):
        piezas.append(p[fin : m.start()])
        apertura = m.group(1)
        if t != t.strip() and "xml:space" not in apertura:
            apertura = '<w:t xml:space="preserve">'
        piezas.append(apertura + t + m.group(3))
        fin = m.end()
    piezas.append(p[fin:])
    return "".join(piezas)


def _tope_de_tabulacion(p: str) -> str:
    """Con sangria francesa, el tope de tabulacion explicito en la sangria: Word
    lo supone, LibreOffice no (medido: «¹⁰DECRETO…» pegado en la vista)."""
    ppr = re.search(r"<w:pPr>.*?</w:pPr>", p, re.S)
    if not ppr or "<w:tabs>" in ppr.group(0):
        return p
    ind = re.search(r'<w:ind\b[^>]*w:hanging="(\d+)"', ppr.group(0))
    izq = re.search(r'<w:ind\b[^>]*w:(?:left|start)="(\d+)"', ppr.group(0))
    if not ind or not izq:
        return p
    tabs = '<w:tabs><w:tab w:val="left" w:pos="%s"/></w:tabs>' % izq.group(1)
    cuerpo = ppr.group(0)
    m = re.search(r"<w:(?:spacing|ind|jc|rPr)\b", cuerpo)
    cuerpo = cuerpo[: m.start()] + tabs + cuerpo[m.start():] if m else cuerpo.replace("</w:pPr>", tabs + "</w:pPr>")
    return p[: ppr.start()] + cuerpo + p[ppr.end():]


RE_TOKEN_NOTA = re.compile(r"<w:tab/>|(<w:t(?:\s[^>/]*)?>)(.*?)</w:t>", re.S)


def _tokens_tras_llamada(p: str) -> tuple[int, list]:
    """(inicio, tokens) de lo que sigue a la llamada: tabulaciones y textos,
    hasta el primer texto con letras."""
    i = p.find("<w:footnoteRef/>")
    if i < 0:
        return -1, []
    fin_run = p.find("</w:r>", i)
    if fin_run < 0:
        return -1, []
    ini = fin_run + len("</w:r>")
    toks = []
    for m in RE_TOKEN_NOTA.finditer(p, ini):
        toks.append(m)
        if m.group(0) != "<w:tab/>" and m.group(2).strip():
            break
    return ini, toks


def _tab_tras_llamada(p: str) -> str:
    """Tras la llamada va EXACTAMENTE una tabulacion y luego el texto: con la
    sangria francesa de 567 (8 330 de 8 472 notas) es lo que alinea todas las
    lineas a 1 cm. Con un espacio (7 268 notas) la primera linea queda corrida;
    con dos tabulaciones, el texto salta al tope siguiente."""
    ini, toks = _tokens_tras_llamada(p)
    if ini < 0 or not toks or toks[-1].group(0) == "<w:tab/>" or not toks[-1].group(2).strip():
        return p
    tabs = [m for m in toks if m.group(0) == "<w:tab/>"]
    blancos = [m for m in toks[:-1] if m.group(0) != "<w:tab/>" and m.group(2)]
    texto_m = toks[-1]
    if len(tabs) == 1 and not blancos and not texto_m.group(2)[:1].isspace():
        return p
    # Se reescribe de atras hacia delante: el texto sin espacios iniciales,
    # los blancos intermedios vacios, las tabulaciones sobrantes fuera, y una
    # sola tabulacion justo antes del texto.
    nuevo = p
    rel_ini, rel_fin = texto_m.start(), texto_m.end()
    nuevo = (
        nuevo[:rel_ini]
        + "<w:tab/>" + texto_m.group(1) + texto_m.group(2).lstrip() + "</w:t>"
        + nuevo[rel_fin:]
    )
    for m in reversed(toks[:-1]):
        if m.group(0) == "<w:tab/>":
            nuevo = nuevo[: m.start()] + nuevo[m.end():]
        elif m.group(2):
            nuevo = nuevo[: m.start()] + m.group(1) + "</w:t>" + nuevo[m.end():]
    if 'xml:space="preserve"' not in texto_m.group(1) and texto_m.group(2) != texto_m.group(2).lstrip():
        pass
    return nuevo


RE_FRANCESA = re.compile(r'<w:ind\b([^>]*)w:hanging="(\d+)"([^>]*)/>')


def _francesa_sin_tab(p: str) -> bool:
    """Parrafo interior de una nota con sangria francesa y sin tabulacion al
    inicio: su primera linea queda a 0 y las demas a 1 cm (nota 18 del
    9998-2026, «20.4. El administrado…»)."""
    m = RE_FRANCESA.search(p)
    if not m or m.group(2) == "0" or "footnoteRef" in p or not texto(p).strip() or _con_etiqueta(p):
        return False
    primero = re.search(r"<w:tab/>|<w:t(?:\s[^>/]*)?>([^<]*)</w:t>", p[p.find("</w:pPr>") + 1 if "</w:pPr>" in p else 0:])
    while primero and primero.group(0) != "<w:tab/>" and not primero.group(1).strip():
        resto = p[primero.end():]
        siguiente = re.search(r"<w:tab/>|<w:t(?:\s[^>/]*)?>([^<]*)</w:t>", resto)
        if not siguiente:
            break
        p, primero = resto, siguiente
    return bool(primero) and primero.group(0) != "<w:tab/>"


RE_ETIQUETA_TAB = re.compile(r"^(?:<[^>]+>|\s)*?<w:t(?:\s[^>/]*)?>\s*[\w.()ºª-]{1,10}\s*</w:t>(?:<[^>]+>|\s)*?<w:tab/>", re.S)


def _con_etiqueta(p: str) -> bool:
    """«20.4.<tab>El administrado…», «a.<tab>…»: etiqueta corta y tabulacion.
    Ese parrafo SI lleva sangria francesa (la etiqueta cuelga a 0 y el texto
    va a 1 cm): quitarsela lo desalineaba (9998-2026, vista ONLYOFFICE)."""
    cuerpo = p.split("</w:pPr>", 1)[1] if "</w:pPr>" in p else p
    return bool(RE_ETIQUETA_TAB.match(cuerpo))


def _alinear_interior(p: str) -> str:
    if _con_etiqueta(p):
        ind = re.search(r"<w:ind\b[^>]*/>", p)
        if ind and "w:hanging" not in ind.group(0):
            izq = re.search(r'w:(?:left|start)="(\d+)"', ind.group(0))
            val = izq.group(1) if izq and izq.group(1) != "0" else "567"
            nuevo = '<w:ind w:left="%s" w:hanging="%s"/>' % (val, val)
            return p.replace(ind.group(0), nuevo, 1)
        return p
    if not _francesa_sin_tab(p):
        return p
    return RE_FRANCESA.sub(lambda m: "<w:ind%s%s/>" % (m.group(1), m.group(3)), p, count=1)


def _vacio(p: str) -> bool:
    return not texto(p).strip() and "<w:drawing" not in p and "footnoteRef" not in p


def formatear_nota(cuerpo: str) -> tuple[str, list[str]]:
    """Aplica R-187 a una nota (el XML entre <w:footnote> y </w:footnote>)."""
    cambios = []
    ps = list(RE_P.finditer(cuerpo))
    if not ps:
        return cuerpo, cambios
    nuevos = []
    for k, m in enumerate(ps):
        p = m.group(0)
        if k == 0:
            q = _tope_de_tabulacion(_tab_tras_llamada(p))
            if q != p:
                cambios.append("tabulacion tras la llamada")
                p = q
        else:
            q = _alinear_interior(p)
            if q != p:
                cambios.append("parrafo interior alineado a 1 cm")
                p = q
        q = _colapsar_espacios_parrafo(p)
        if q != p:
            cambios.append("dobles espacios")
            p = q
        nuevos.append(p)
    # Parrafos de solo puntuacion (un «.» suelto) y vacios internos.
    utiles = [
        k
        for k, p in enumerate(nuevos)
        if not re.fullmatch(r"[\s.,;:]*", texto(p)) or "footnoteRef" in p or "<w:drawing" in p
    ]
    if not utiles:
        return cuerpo, cambios
    ultimo = utiles[-1]
    conservar = [nuevos[k] for k in utiles]
    sueltos_internos = [k for k in range(len(nuevos)) if k not in utiles and k < ultimo]
    if sueltos_internos:
        cambios.append("%d linea(s) vacia(s) o suelta(s) interna(s)" % len(sueltos_internos))
    # Exactamente una linea en blanco al final de cada nota (R-174).
    final = next((nuevos[k] for k in range(ultimo + 1, len(nuevos)) if _vacio(nuevos[k])), None)
    if final is None:
        final = re.sub(r"<w:r\b.*?</w:r>", "", conservar[-1], flags=re.S)
        final = re.sub(r'\s(?:w14:paraId|w14:textId)="[^"]*"', "", final)
        cambios.append("linea en blanco final")
    elif len(nuevos) - 1 - ultimo > 1:
        cambios.append("lineas en blanco finales de mas")
    conservar.append(final)
    salida = cuerpo[: ps[0].start()] + "".join(conservar) + cuerpo[ps[-1].end() :]
    return salida, cambios


def formatear_notas(fx: str) -> tuple[str, dict]:
    informe: dict[str, list[str]] = {}

    def _una(m):
        if int(m.group(1)) <= 0:
            return m.group(0)
        apertura = re.match(r"<w:footnote\b[^>]*>", m.group(0)).group(0)
        cuerpo = m.group(0)[len(apertura) : -len("</w:footnote>")]
        nuevo, cambios = formatear_nota(cuerpo)
        if cambios:
            informe[m.group(1)] = cambios
        return apertura + nuevo + "</w:footnote>"

    return RE_FN.sub(_una, fx), informe


# --------------------------------------------------------------------------- #
# R-184 / R-185: anclas y llamadas pegadas
# --------------------------------------------------------------------------- #


def _partir_run_tras(p: str, ancla: str) -> tuple[str, int] | None:
    """Parte el run donde termina la PRIMERA aparicion de `ancla` en el parrafo y
    devuelve (parrafo, posicion donde insertar un run nuevo)."""
    plano_p = ""
    trozos = []
    for m in RE_T.finditer(p):
        trozos.append((m, len(plano_p)))
        plano_p += m.group(2)
    idx = desescapar(plano_p).find(ancla)
    if idx < 0:
        return None
    # desescapar puede acortar el texto: se trabaja sobre el crudo si difiere.
    if desescapar(plano_p) != plano_p:
        idx = plano_p.find(ancla)
        if idx < 0:
            return None
    fin = idx + len(ancla)
    for m, ini in trozos:
        if ini < fin <= ini + len(m.group(2)):
            corte = fin - ini
            run = next((r for r in RE_RUN.finditer(p) if r.start() <= m.start() < r.end()), None)
            if run is None:
                return None
            if corte == len(m.group(2)):
                return p, run.end()
            rx = run.group(0)
            rel = m.start() - run.start()
            antes_t, despues_t = m.group(2)[:corte], m.group(2)[corte:]
            cabeza = (
                rx[:rel]
                + '<w:t xml:space="preserve">'
                + antes_t
                + "</w:t>"
                + "</w:r>"
            )
            rpr = re.search(r"<w:rPr>.*?</w:rPr>", rx, re.S)
            apertura = re.match(r"<w:r\b[^>]*>", rx).group(0)
            cola = (
                apertura
                + (rpr.group(0) if rpr else "")
                + '<w:t xml:space="preserve">'
                + despues_t
                + "</w:t>"
                + rx[rel + len(m.group(0)) :]
            )
            # `cola` hereda lo que seguia al <w:t> dentro del run (p. ej. otro <w:t>)
            nuevo = p[: run.start()] + cabeza + cola + p[run.end() :]
            return nuevo, run.start() + len(cabeza)
    return None


def mover_llamada(p: str, nota_id: str, ancla: str) -> str | None:
    """Mueve el run de la llamada `nota_id` detras de la primera aparicion de
    `ancla` en el mismo parrafo. None si no se puede."""
    run = next(
        (
            r
            for r in RE_RUN.finditer(p)
            if re.search(r'<w:footnoteReference\b[^>]*w:id="%s"' % re.escape(nota_id), r.group(0))
        ),
        None,
    )
    if run is None:
        return None
    sin = p[: run.start()] + p[run.end() :]
    partido = _partir_run_tras(sin, ancla)
    if partido is None:
        return None
    q, pos = partido
    return q[:pos] + run.group(0) + q[pos:]


def tipo_de_nota(texto_nota: str, anclas: list[dict], parrafo: str = "") -> dict | None:
    for a in anclas:
        if a.get("parrafo") and a["parrafo"] not in parrafo:
            continue
        if re.search(a["nota"], texto_nota):
            return a
    return None


def anclas_incumplidas(x: str, fx: str) -> list[dict]:
    """Llamadas de una nota canonica que no estan detras de su ancla."""
    anclas = cargar_anclas()
    ns = notas(fx)
    fuera = []
    for ll in llamadas(x):
        a = tipo_de_nota(ns.get(ll["id"], ""), anclas, ll["parrafo"])
        if not a:
            continue
        if a.get("ancla_regex"):
            bien = re.fullmatch(r"\s*(?:%s)" % a["ancla_regex"], _norm(ll["previo"])) is not None
        else:
            bien = _norm(ll["previo"]).endswith(a["ancla"])
        if not bien:
            fuera.append({"id": ll["id"], "tipo": a["id"], "ancla": a.get("ancla") or a["ancla_regex"], "previo": ll["previo"][-50:]})
    return fuera


def reanclar(x: str, fx: str) -> tuple[str, list[str]]:
    """Lleva cada nota canonica a su ancla (primera aparicion en el documento)."""
    anclas = cargar_anclas()
    ns = notas(fx)
    hechos = []
    for f in anclas_incumplidas(x, fx):
        a = next(a for a in anclas if a["id"] == f["tipo"])
        # parrafo de la llamada
        pm = next(
            (m for m in RE_P.finditer(x) if re.search(r'<w:footnoteReference\b[^>]*w:id="%s"' % f["id"], m.group(0))),
            None,
        )
        if pm is None:
            continue
        destino = pm
        if a.get("ancla_regex"):
            hallado = re.search(a["ancla_regex"], desescapar(texto(pm.group(0))))
            if not hallado:
                continue
            a = dict(a, ancla=hallado.group(0))
        if a.get("parrafo") and a["ancla"] not in desescapar(texto(pm.group(0))):
            continue
        if a["ancla"] not in desescapar(texto(pm.group(0))):
            destino = next(
                (m for m in RE_P.finditer(x) if a["ancla"] in desescapar(texto(m.group(0)))),
                None,
            )
            if destino is None:
                continue
        if destino.start() == pm.start():
            q = mover_llamada(pm.group(0), f["id"], a["ancla"])
            if q is None:
                continue
            x = x[: pm.start()] + q + x[pm.end():]
        else:
            run = next(
                r for r in RE_RUN.finditer(pm.group(0))
                if re.search(r'<w:footnoteReference\b[^>]*w:id="%s"' % f["id"], r.group(0))
            )
            origen = pm.group(0)[: run.start()] + pm.group(0)[run.end():]
            partido = _partir_run_tras(destino.group(0), a["ancla"])
            if partido is None:
                continue
            q, pos = partido
            q = q[:pos] + run.group(0) + q[pos:]
            if destino.start() < pm.start():
                x = x[: destino.start()] + q + x[destino.end(): pm.start()] + origen + x[pm.end():]
            else:
                x = x[: pm.start()] + origen + x[pm.end(): destino.start()] + q + x[destino.end():]
        hechos.append("%s -> tras «%s»" % (f["tipo"], a["ancla"][-40:]))
        ns = notas(fx)
    return x, hechos


RE_TITULO_CODIGO = re.compile(r"^\W*LEY\s+29571,\s*C[ÓO]DIGO DE PROTECCI[ÓO]N Y DEFENSA DEL CONSUMIDOR", re.I)


def titular_notas(x: str, fx: str) -> tuple[str, list[str]]:
    """Una nota que empieza en «Artículo N» sin decir de que norma es recibe el
    titulo de la norma que cita la frase que la llama. Solo el Codigo se infiere
    («Código», «Ley 29571», «referida norma» en esa frase); lo demas se informa."""
    donante = None
    for m in RE_FN.finditer(fx):
        ps = [p.group(0) for p in RE_P.finditer(m.group(0))]
        if ps and "footnoteRef" in ps[0]:
            t = _norm(desescapar(texto(ps[0])))
            if RE_TITULO_CODIGO.match(t) and not re.search(r"Art[íi]culo\s+\d", t):
                donante = ps[0]
                break
    tramos = {ll["id"]: ll["tramo"] for ll in llamadas(x)}
    hechos = []

    def _una(m):
        if int(m.group(1)) <= 0:
            return m.group(0)
        cuerpo = m.group(0)
        ps = list(RE_P.finditer(cuerpo))
        if not ps:
            return cuerpo
        p0 = ps[0].group(0)
        if not re.match(r"Art[íi]culo\s+\d+", _norm(desescapar(texto(p0)))):
            return cuerpo
        if not donante or not re.search(r"C[óo]digo|29571|referida norma", tramos.get(m.group(1), "")):
            hechos.append("nota %s: sin titulo y sin norma inferible (se eleva)" % m.group(1))
            return cuerpo
        sin_ref = re.sub(r"<w:r\b(?:(?!</w:r>).)*?<w:footnoteRef/>(?:(?!</w:r>).)*?</w:r>", "", p0, count=1, flags=re.S)
        sin_ref = re.sub(r"<w:r\b(?:(?!</w:r>).)*?<w:tab/>\s*</w:r>", "", sin_ref, count=1, flags=re.S)
        sin_ref = sin_ref.replace("<w:tab/>", "", 1) if texto(sin_ref)[:1] == "" else sin_ref
        cabeza = re.sub(r'\s(?:w14:paraId|w14:textId)="[^"]*"', "", donante)
        hechos.append("nota %s: titulo del Codigo" % m.group(1))
        return cuerpo[: ps[0].start()] + cabeza + sin_ref + cuerpo[ps[0].end():]

    return RE_FN.sub(_una, fx), hechos


def llamadas_pegadas(x: str) -> list[dict]:
    return [ll for ll in llamadas(x) if ll["pegada"]]


# --------------------------------------------------------------------------- #
# R-186: la nota transcribe la norma citada
# --------------------------------------------------------------------------- #

RE_ARTS = re.compile(
    r"art[íi]culos?\s+(\d+)((?:\s*(?:,|y)\s*(?:al\s+art[íi]culo\s+)?\d+)*)", re.I
)


def articulos_citados(tramo: str) -> set[str]:
    """Articulos que cita el tramo de texto que precede a una llamada (desde la
    llamada anterior del parrafo): los de las DOS ultimas menciones."""
    menciones = list(RE_ARTS.finditer(tramo))
    if not menciones:
        return set()
    salida: set[str] = set()
    for m in menciones[-2:]:
        salida.add(m.group(1))
        salida.update(re.findall(r"\d+", m.group(2)))
    return salida


def articulos_transcritos(texto_nota: str) -> set[str]:
    return set(re.findall(r"Art[íi]culos?\s+(\d+)", texto_nota))


def notas_que_no_corresponden(x: str, fx: str) -> list[dict]:
    ns = notas(fx)
    fallos = []
    for ll in llamadas(x):
        citados = articulos_citados(ll["tramo"][-320:])
        if not citados:
            continue
        n = ns.get(ll["id"], "")
        transcritos = articulos_transcritos(n)
        if not transcritos:
            continue  # nota no normativa (MYPE, publicacion): la vigilan las anclas
        if not (citados & transcritos):
            fallos.append(
                {
                    "id": ll["id"],
                    "citados": sorted(citados, key=int),
                    "transcritos": sorted(transcritos, key=int),
                    "tramo": ll["tramo"][-70:],
                }
            )
    return fallos


# --------------------------------------------------------------------------- #
# R-187 (lectura): defectos de forma de una nota ya escrita
# --------------------------------------------------------------------------- #


def defectos_de_forma(fx: str) -> list[str]:
    salida = []
    for m in RE_FN.finditer(fx):
        if int(m.group(1)) <= 0:
            continue
        cuerpo = m.group(0)
        ps = [p.group(0) for p in RE_P.finditer(cuerpo)]
        if not ps:
            continue
        nid = m.group(1)
        p0 = ps[0]
        _ini, toks = _tokens_tras_llamada(p0)
        if toks and toks[-1].group(0) != "<w:tab/>" and toks[-1].group(2).strip():
            n_tabs = sum(1 for m in toks if m.group(0) == "<w:tab/>")
            if n_tabs != 1 or any(m.group(2) for m in toks if m.group(0) != "<w:tab/>" and m is not toks[-1]):
                salida.append(
                    "nota %s: %s tras la llamada (lineas desalineadas)"
                    % (nid, "sin tabulacion" if n_tabs == 0 else ("%d tabulaciones" % n_tabs if n_tabs > 1 else "espacio y tabulacion"))
                )
        if any(_con_etiqueta(p) and _alinear_interior(p) != p for p in ps[1:]):
            salida.append("nota %s: parrafo con etiqueta («20.4.», «a.») sin sangria francesa (el texto no se alinea a 1 cm)" % nid)
        if any(_francesa_sin_tab(p) for p in ps[1:]):
            salida.append("nota %s: parrafo interior con sangria francesa (primera linea a 0 y el resto a 1 cm)" % nid)
        if "footnoteRef" in p0 and _tope_de_tabulacion(p0) != p0:
            salida.append("nota %s: sangria francesa sin tope de tabulacion (lineas desalineadas)" % nid)
        utiles = [k for k, p in enumerate(ps) if not re.fullmatch(r"[\s.,;:]*", texto(p)) or "footnoteRef" in p]
        if utiles:
            internos = [k for k in range(utiles[0], utiles[-1]) if k not in utiles]
            if internos:
                salida.append("nota %s: %d linea(s) en blanco o sueltas dentro de la nota" % (nid, len(internos)))
        for p in ps:
            t = desescapar(texto(p))
            d = re.search(r".{0,18}\S {2,}\S.{0,10}", t)
            if d:
                salida.append("nota %s: dobles espacios («%s»)" % (nid, d.group(0).strip()))
                break
        primero = _norm(desescapar(texto(p0)))
        if re.match(r"Art[íi]culo\s+\d+", primero):
            salida.append("nota %s: empieza en «%s» sin el titulo de la norma" % (nid, primero[:30]))
    return salida


def _numeracion(p: str) -> str | None:
    m = re.search(r'<w:numId w:val="(\d+)"', p)
    return m.group(1) if m else None


def transcripciones_incompletas(fx: str) -> list[str]:
    """Exigencias de docs/textos_normativos.json: si la nota transcribe una
    disposicion, trae todos sus literales, cada uno en su parrafo y con la misma
    numeracion (letra) que los demas. Medido: 574 de 574 plantillas transcribian
    el 115.1 con «h.» e «i.» sin numeracion, es decir, sin letra."""
    salida = []
    for m in RE_FN.finditer(fx):
        if int(m.group(1)) <= 0:
            continue
        ps = [p.group(0) for p in RE_P.finditer(m.group(0))]
        todo = desescapar("".join(texto(p) for p in ps))
        for ex in cargar_textos():
            if not re.search(ex["si_contiene"], todo):
                continue
            nums = []
            for lit in ex["literales"]:
                p = next((p for p in ps if re.sub(r"^[a-z]\.\s*", "", desescapar(texto(p)).strip()).startswith(lit)), None)
                if p is None:
                    salida.append("nota %s: %s sin el literal «%s»" % (m.group(1), ex["disposicion"], lit))
                    continue
                letra = re.match(r"^[a-z]\.\s", desescapar(texto(p)).strip())
                nums.append((lit, _numeracion(p) or ("texto" if letra else None)))
            vistas = {n for _l, n in nums if n}
            for lit, n in nums:
                if n is None or len(vistas) > 1:
                    salida.append("nota %s: %s: el literal «%s» no lleva la letra de los demas" % (m.group(1), ex["disposicion"], lit))
    return salida


# --------------------------------------------------------------------------- #
# B4: la nota de la norma imputada se genera desde la norma, nunca se hereda
# --------------------------------------------------------------------------- #

CATALOGO = RAIZ / "docs" / "notas_normas.json"


def _clave_norma(t: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"(\d+\.\d+)\.", r"\1", t)).strip().lower()


def nota_de_la_norma(x: str, fx: str) -> tuple[str, str, list[str]]:
    """Cada calificacion («corresponde calificar … tipificado en <norma>») termina
    con la llamada a la nota que transcribe ESA norma (docs/notas_normas.json).

    Si la nota que heredo de la plantilla transcribe otra norma, se sustituye
    por la del catalogo; si no tiene nota, se le pone. Medido en el 9999-2026:
    la imputacion por el literal e) del articulo 47 salio con la nota de los
    articulos 18 y 19 que traia la plantilla."""
    try:
        catalogo = json.loads(CATALOGO.read_text(encoding="utf-8"))
    except Exception:
        return x, fx, []
    claves = sorted(((_clave_norma(k), k) for k in catalogo), key=lambda kv: -len(kv[0]))
    ns = notas(fx)
    ids = [int(i) for i in re.findall(r'<w:footnote\b[^>]*w:id="(-?\d+)"', fx)]
    siguiente = max([0] + ids) + 1
    modelo = re.search(
        r"<w:r\b(?:(?!</w:r>).)*?<w:footnoteReference\b[^>]*/>(?:(?!</w:r>).)*?</w:r>", x, re.S
    )
    informe = []
    piezas, fin = [], 0
    for m in RE_P.finditer(x):
        p = m.group(0)
        t = desescapar(texto(p))
        if "corresponde calificar" not in t or "tipificad" not in t:
            continue
        cola = _clave_norma(t[t.index("tipificad"):])
        k = next((orig for c, orig in claves if c in cola), None)
        if k is None:
            informe.append("sin nota catalogada para «%s»" % t[t.index("tipificad"):][:80])
            continue
        citados = articulos_citados(t[t.index("tipificad"):])
        refs = RE_REF.findall(p)
        cuerpo_catalogo = catalogo[k]["xml"]
        if refs:
            ultima = refs[-1]
            if citados & articulos_transcritos(ns.get(ultima, "")):
                continue
            fx = re.sub(
                r'(<w:footnote\b[^>]*w:id="%s"[^>]*>).*?(</w:footnote>)' % ultima,
                lambda g: g.group(1) + cuerpo_catalogo + g.group(2),
                fx,
                count=1,
                flags=re.S,
            )
            informe.append("nota de «%s» sustituida por la del catalogo" % k)
        else:
            if not modelo:
                informe.append("sin llamada modelo para anotar «%s»" % k)
                continue
            run = re.sub(r'(w:id=")\d+(")', lambda g: g.group(1) + str(siguiente) + g.group(2), modelo.group(0), count=1)
            p2 = p[: p.rindex("</w:p>")] + run + "</w:p>"
            piezas.append(x[fin : m.start()])
            piezas.append(p2)
            fin = m.end()
            fx = fx.replace(
                "</w:footnotes>",
                '<w:footnote w:id="%d">%s</w:footnote></w:footnotes>' % (siguiente, cuerpo_catalogo),
                1,
            )
            siguiente += 1
            informe.append("nota de «%s» añadida" % k)
    piezas.append(x[fin:])
    return "".join(piezas), fx, informe
