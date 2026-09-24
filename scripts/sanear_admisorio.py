#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Saneamiento final de un admisorio construido (v3.2, revision del instructor 24/09/2026).

`construir_admisorio.py` lo llama al terminar; tambien se puede ejecutar a mano:

    python scripts/sanear_admisorio.py <ADM ... .docx>

Aplica al documento los normalizadores del corpus (los mismos que migraron las
574 plantillas) y cierra defectos medidos en la remesa del 24/09/2026 que el
verificador no veia o que el constructor producia:

  - nota sobre la presentacion de la denuncia en CC1 (R-167);
  - llamadas duplicadas a una misma nota; parrafos alineados a la izquierda (R-144);
    segunda linea de MATERIAS con sangria francesa; «N°» en notas repetidas (R-156);
    separadores de notas autocerrados (rompian el conteo de notas: R-183);
  - linea en blanco entre imputaciones contiguas (las insertadas iban pegadas);
  - parrafo del traslado con el texto partido en tramos (el ancla de sus dos
    notas no se hallaba) y notas sobrantes de la version anterior (R-173);
  - nota del Codigo y nota de competencia (art. 105) perdidas o con id repetido
    al reanclarse: se restituyen desde una plantilla maestra (R-184);
  - la nota de la norma imputada va SOLO en la primera imputacion de ese
    articulo: las siguientes no la repiten (mandato del instructor, R-202);
  - la considerativa de cada imputacion por el deber de informacion cierra con
    «; involucraría una presunta afectación al derecho de información de los
    consumidores. Por consiguiente, …» (v3.3, R-207);
  - renumeracion de notas en dos fases (sin colisiones de ids).

Todo se hace sobre el XML como texto; ningun proceso WINWORD.EXE.
"""

import re
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(RAIZ / "scripts"), str(RAIZ / "scripts" / "migraciones")]

import normalizar_plantillas_popperianas as NP
import notas_traslado as NT
import migrar_v3_1 as M31
import uniformar_tipografia as UT
import afectacion_derecho_informacion as ADI

RUN = re.compile(
    r"<w:r\b[^>]*>(<w:rPr>.*?</w:rPr>)?<w:t(?: [^>]*)?>([^<]*)</w:t></w:r>", re.S
)


def visual(rpr):
    rpr = rpr or ""
    return tuple(
        bool(re.search(r"<w:%s(?: [^>]*)?/>" % e, rpr))
        and not re.search(r'<w:%s w:val="(?:0|false|none)"' % e, rpr)
        for e in ("b", "i", "u", "vertAlign", "highlight", "strike")
    )


def unir_runs(p: str) -> str:
    """Solo en el parrafo del traslado: quita proofErr, borra runs vacios y une runs
    contiguos de texto con el MISMO formato (no se pierde ninguna negrita)."""
    p = re.sub(r"<w:proofErr[^>]*/>|<w:lastRenderedPageBreak/>", "", p)
    p = re.sub(
        r"<w:r(?: [^>]*)?>(?:<w:rPr>(?:(?!</w:r>).)*?</w:rPr>)?<w:t(?: [^>]*)?></w:t></w:r>",
        "",
        p,
        flags=re.S,
    )
    R = re.compile(
        r"<w:r(?: [^>]*)?>(<w:rPr>(?:(?!</w:r>).)*?</w:rPr>)?<w:t(?: [^>]*)?>([^<]*)</w:t></w:r>",
        re.S,
    )
    pos = 0
    while True:
        a = R.search(p, pos)
        if not a:
            return p
        b = R.match(p, a.end())
        if b and visual(a.group(1)) == visual(b.group(1)):
            nuevo = '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (
                a.group(1) or "",
                a.group(2) + b.group(2),
            )
            p = p[: a.start()] + nuevo + p[b.end() :]
            pos = a.start()
        else:
            pos = a.end()


def preparar_traslado(ruta: Path):
    with zipfile.ZipFile(ruta) as z:
        infos = z.infolist()
        datos = {i.filename: z.read(i.filename) for i in infos}
    x = datos["word/document.xml"].decode("utf-8")
    ps = [
        m
        for m in re.finditer(r"<w:p[ >].*?</w:p>", x, re.S)
        if "correr traslado" in NT.texto(m.group(0)) and "223" in NT.texto(m.group(0))
    ]
    if len(ps) != 1:
        print("  AVISO: %d parrafos de traslado" % len(ps))
        return
    m = ps[0]
    x = x[: m.start()] + unir_runs(m.group(0)) + x[m.end() :]
    datos["word/document.xml"] = x.encode("utf-8")
    tmp = ruta.with_suffix(".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
        for i in infos:
            zo.writestr(i, datos[i.filename])
    tmp.replace(ruta)


def depurar(ruta: Path):
    """Llamadas duplicadas a una misma nota (queda la primera) y jc=left -> both (R-144)."""
    with zipfile.ZipFile(ruta) as z:
        infos = z.infolist()
        datos = {i.filename: z.read(i.filename) for i in infos}
    x = datos["word/document.xml"].decode("utf-8")
    vistos = set()

    def _ref(m):
        i = re.search(r'w:id="(\d+)"', m.group(0)).group(1)
        if i in vistos:
            print("  llamada duplicada a la nota %s quitada" % i)
            return ""
        vistos.add(i)
        return m.group(0)

    x2 = re.sub(
        r"<w:r(?: [^>]*)?>(?:(?!</w:r>).)*?<w:footnoteReference [^>]*/>(?:(?!</w:r>).)*?</w:r>",
        _ref,
        x,
        flags=re.S,
    )
    x2 = x2.replace('<w:jc w:val="left"/>', '<w:jc w:val="both"/>')
    # encabezado: la 2.a linea de MATERIAS va en la columna (sin sangria francesa)
    x2 = re.sub(
        r'(<w:p[ >](?:(?!</w:p>).)*?)<w:ind w:left="(\d+)" w:hanging="\2"/>((?:(?!</w:p>).)*?<w:t>REQUERIMIENTO DE INFORMACI)',
        r'\1<w:ind w:left="\2"/>\3',
        x2,
        flags=re.S,
    )
    # R-156 en notas repetidas (el constructor solo sustituye la primera aparicion)
    fx = datos["word/footnotes.xml"].decode("utf-8")
    fx2 = re.sub(r"(<w:t(?: [^>]*)?>[^<]*?)\bN[°º]\s*(?=\d)", r"\1", fx)
    while fx2 != fx:
        fx, fx2 = fx2, re.sub(r"(<w:t(?: [^>]*)?>[^<]*?)\bN[°º]\s*(?=\d)", r"\1", fx2)
    fx = re.sub(
        r"(Legislativo|LEGISLATIVO|Ley|LEY|Supremo|SUPREMO) N\s+(?=\d)", r"\1 ", fx
    )
    x2 = re.sub(
        r"(Legislativo|LEGISLATIVO|Ley|LEY|Supremo|SUPREMO) N\s+(?=\d)", r"\1 ", x2
    )
    # separadores autocerrados -> forma estandar de Word (equivalente)
    fx = re.sub(
        r'<w:footnote w:type="separator" w:id="(-?\d+)"\s*/>',
        r'<w:footnote w:type="separator" w:id="\1"><w:p><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr><w:r><w:separator/></w:r></w:p></w:footnote>',
        fx,
    )
    fx = re.sub(
        r'<w:footnote w:type="continuationSeparator" w:id="(-?\d+)"\s*/>',
        r'<w:footnote w:type="continuationSeparator" w:id="\1"><w:p><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr><w:r><w:continuationSeparator/></w:r></w:p></w:footnote>',
        fx,
    )
    datos["word/footnotes.xml"] = fx.encode("utf-8")
    if True:
        datos["word/document.xml"] = x2.encode("utf-8")
        tmp = ruta.with_suffix(".tmp")
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
            for inf in infos:
                zo.writestr(inf, datos[inf.filename])
        tmp.replace(ruta)


def separar(ruta: Path):
    """Entre dos imputaciones contiguas (considerativa o resolutiva) va la misma linea
    en blanco que usa la plantilla entre sus parrafos: se clona la existente."""
    with zipfile.ZipFile(ruta) as z:
        infos = z.infolist()
        datos = {i.filename: z.read(i.filename) for i in infos}
    x = datos["word/document.xml"].decode("utf-8")
    ps = list(re.finditer(r"<w:p[ >].*?</w:p>", x, re.S))
    es = lambda m: bool(
        re.search(
            r"considera que el hecho denunciado|^\s*Presunta infracci",
            NT.texto(m.group(0)),
        )
    )
    vacio = next(
        (
            ps[k + 1].group(0)
            for k in range(len(ps) - 1)
            if es(ps[k]) and not NT.texto(ps[k + 1].group(0)).strip()
        ),
        None,
    )
    if not vacio:
        return
    n = 0
    for k in range(len(ps) - 2, -1, -1):
        if es(ps[k]) and es(ps[k + 1]):
            x = x[: ps[k].end()] + vacio + x[ps[k].end() :]
            n += 1
    if n:
        datos["word/document.xml"] = x.encode("utf-8")
        tmp = ruta.with_suffix(".tmp")
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
            for inf in infos:
                zo.writestr(inf, datos[inf.filename])
        tmp.replace(ruta)
        print("  %d separadores añadidos entre imputaciones" % n)


def notas_repetidas(ruta: Path):
    """La nota de una norma imputada va solo en su primera calificacion; las
    siguientes imputaciones por la misma norma no la repiten (instructor)."""
    infos, datos = _leer(ruta)
    x = datos["word/document.xml"].decode("utf-8")
    fx = datos["word/footnotes.xml"].decode("utf-8")
    cuerpo = dict(
        re.findall(
            r'<w:footnote (?:(?!/>)[^>])*?w:id="([1-9]\d*)"[^>/]*>(.*?)</w:footnote>',
            fx,
            re.S,
        )
    )

    def norma(i):
        t = re.sub(r"\s+", " ", NT.texto(cuerpo.get(i, "")))
        if "culo 105" in t or not t.startswith("LEY 29571"):
            return None
        arts = tuple(re.findall(r"Art[íi]culo (\d+(?:\.\d+)?)\.-", t))
        return arts or None

    vistas, quitar = set(), []
    for pm in re.finditer(r"<w:p[ >].*?</w:p>", x, re.S):
        tp = NT.texto(pm.group(0))
        if not (
            "considera que el hecho denunciado" in tp
            or tp.strip().startswith("Presunta infracci")
        ):
            continue
        for r in RE_REF.finditer(pm.group(0)):
            n = norma(r.group(1))
            if n is None:
                continue
            if n in vistas:
                quitar.append(r.group(1))
            vistas.add(n)
    if not quitar:
        return
    for i in quitar:
        x = re.sub(
            r'<w:r(?: [^>]*)?>(?:(?!</w:r>).)*?<w:footnoteReference [^>]*w:id="%s"[^>]*/>(?:(?!</w:r>).)*?</w:r>'
            % i,
            "",
            x,
            count=1,
            flags=re.S,
        )
        fx = re.sub(
            r'<w:footnote [^>]*w:id="%s"[^>/]*>.*?</w:footnote>' % i,
            "",
            fx,
            count=1,
            flags=re.S,
        )
    x, fx = renumerar(x, fx)
    datos["word/document.xml"] = x.encode("utf-8")
    datos["word/footnotes.xml"] = fx.encode("utf-8")
    _escribir(ruta, infos, datos)
    print("  %d notas repetidas de la norma imputada quitadas" % len(quitar))


def _leer(ruta):
    with zipfile.ZipFile(ruta) as z:
        infos = z.infolist()
        return infos, {i.filename: z.read(i.filename) for i in infos}


def _escribir(ruta, infos, datos):
    tmp = ruta.with_suffix(".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
        for inf in infos:
            zo.writestr(inf, datos[inf.filename])
    tmp.replace(ruta)


RE_REF = re.compile(
    r'<w:r(?: [^>]*)?>(?:(?!</w:r>).)*?<w:footnoteReference [^>]*w:id="(\d+)"[^>]*/>(?:(?!</w:r>).)*?</w:r>',
    re.S,
)


def traslado_sobrantes(ruta: Path):
    """En el parrafo del traslado solo quedan las dos notas canonicas (R-173):
    una llamada que no va tras «807» ni tras «Administrativo General» es un resto
    de la version anterior y se quita con su nota."""
    infos, datos = _leer(ruta)
    x = datos["word/document.xml"].decode("utf-8")
    fx = datos["word/footnotes.xml"].decode("utf-8")
    m = NT.parrafo_traslado(x)
    if not m:
        return
    p = m.group(0)
    quitar = []
    for r in RE_REF.finditer(p):
        previo = NT.texto(p[: r.start()]).rstrip()
        if not (previo.endswith("807") or previo.endswith("Administrativo General")):
            quitar.append(r)
    if not quitar:
        return
    for r in reversed(quitar):
        p = p[: r.start()] + p[r.end() :]
        fx = re.sub(
            r'<w:footnote [^>]*w:id="%s"[^>/]*>.*?</w:footnote>' % r.group(1),
            "",
            fx,
            count=1,
            flags=re.S,
        )
        print("  nota sobrante %s del traslado quitada" % r.group(1))
    x = x[: m.start()] + p + x[m.end() :]
    datos["word/document.xml"] = x.encode("utf-8")
    datos["word/footnotes.xml"] = NT.ordenar_notas(fx, x).encode("utf-8")
    _escribir(ruta, infos, datos)


def nota_competencia(ruta: Path):
    restituir(
        ruta,
        "culo 105",
        "culo 105.- Autoridad competente",
        "en ejercicio de sus facultades",
        "en ejercicio de sus facultades",
        "de competencia (art. 105)",
    )


def nota_codigo(ruta: Path):
    restituir(
        ruta,
        "Publicado el 2 de setiembre de 2010",
        "Publicado el 2 de setiembre de 2010",
        "Defensa del Consumidor",
        "(en adelante, Código)",
        "del Codigo",
    )


def restituir(ruta: Path, marca, clave_fuente, ancla, filtro, etiqueta):
    """Si falta una nota canonica, se toma de una plantilla maestra y se ancla (R-184)."""
    infos, datos = _leer(ruta)
    x = datos["word/document.xml"].decode("utf-8")
    fx = datos["word/footnotes.xml"].decode("utf-8")
    cuerpos = re.findall(
        r'<w:footnote [^>]*w:id="(\d+)"[^>/]*>(.*?)</w:footnote>', fx, re.S
    )
    es = (
        lambda c: (marca in NT.texto(c))
        if marca.startswith("culo")
        else NT.texto(c).strip().startswith(marca)
    )
    ids = [i for i, _ in cuerpos]
    refs = re.findall(r'footnoteReference [^>]*w:id="(\d+)"', x)
    if any(es(c) and ids.count(i) == 1 and i in refs for i, c in cuerpos):
        return
    # nota canonica huerfana o con id duplicado: fuera, y se restituye bien anclada
    for i, c in cuerpos:
        if es(c):
            fx = fx.replace('<w:footnote w:id="%s">%s</w:footnote>' % (i, c), "", 1)
            fx = re.sub(
                r'<w:footnote [^>]*w:id="%s"[^>/]*>%s</w:footnote>' % (i, re.escape(c)),
                "",
                fx,
                count=1,
                flags=re.S,
            )
    cuerpos = re.findall(
        r'<w:footnote [^>]*w:id="(\d+)"[^>/]*>(.*?)</w:footnote>', fx, re.S
    )
    fuente = None
    for t in sorted((RAIZ / "plantillas_maestras").rglob("*.docx")):
        tf = zipfile.ZipFile(t).read("word/footnotes.xml").decode("utf-8")
        fuente = next(
            (
                c
                for _, c in re.findall(
                    r'<w:footnote [^>]*w:id="(\d+)"[^>/]*>(.*?)</w:footnote>', tf, re.S
                )
                if NT.texto(c).strip().startswith(clave_fuente)
                or (clave_fuente.startswith("culo") and clave_fuente in NT.texto(c))
            ),
            None,
        )
        if fuente:
            break
    pm = next((m for m in NT.RE_P.finditer(x) if filtro in NT.texto(m.group(0))), None)
    ref = RE_REF.search(x)
    if not (fuente and pm and ref and ancla in NT.texto(pm.group(0))):
        return
    nuevo = max([0] + [int(i) for i, _ in cuerpos]) + 1
    run_ref = ref.group(0)
    run_ref = re.sub(
        r'(w:footnoteReference [^>]*w:id=")\d+', r"\g<1>%d" % nuevo, run_ref
    )
    try:
        p, _ = NT.anclar(pm.group(0), ancla, run_ref)
    except ValueError:
        return
    x = x[: pm.start()] + p + x[pm.end() :]
    fx = fx.replace(
        "</w:footnotes>",
        '<w:footnote w:id="%d">%s</w:footnote></w:footnotes>' % (nuevo, fuente),
        1,
    )
    x, fx = renumerar(x, fx)
    datos["word/document.xml"] = x.encode("utf-8")
    datos["word/footnotes.xml"] = fx.encode("utf-8")
    _escribir(ruta, infos, datos)
    print("  nota %s restituida tras «%s»" % (etiqueta, ancla))


def renumerar(x: str, fx: str):
    """Ids 1..N en orden de llamada, en dos fases (sin colisiones) y notas ordenadas."""
    orden = []
    for i in re.findall(r'footnoteReference [^>]*w:id="(\d+)"', x):
        if i not in orden:
            orden.append(i)
    nuevo = {v: str(k + 1) for k, v in enumerate(orden)}
    x = re.sub(
        r'(footnoteReference [^>]*w:id=")(\d+)"',
        lambda m: '%sT%s"' % (m.group(1), nuevo.get(m.group(2), m.group(2))),
        x,
    )
    x = x.replace('w:id="T', 'w:id="')
    elems = list(
        re.finditer(
            r'<w:footnote (?:(?!/>)[^>])*?w:id="([1-9]\d*)"[^>/]*>.*?</w:footnote>',
            fx,
            re.S,
        )
    )
    cuerpos = {}
    for m in elems:
        i = nuevo.get(m.group(1))
        if i and i not in cuerpos:
            cuerpos[i] = re.sub(r'w:id="\d+"', 'w:id="%s"' % i, m.group(0), count=1)
    for m in reversed(elems):
        fx = fx[: m.start()] + fx[m.end() :]
    fx = fx.replace(
        "</w:footnotes>",
        "".join(cuerpos[k] for k in sorted(cuerpos, key=int)) + "</w:footnotes>",
        1,
    )
    return x, fx



def nota_presentacion(ruta: Path):
    """R-167: denuncia presentada en CC1 -> ninguna nota sobre su presentacion
    («Denuncia presentada el …», «La denuncia se encuentra fechada …»). Se quitan
    la llamada y la nota, y se renumera (medido en dos borradores del 24/09/2026)."""
    infos, datos = _leer(ruta)
    x = datos["word/document.xml"].decode("utf-8")
    fx = datos["word/footnotes.xml"].decode("utf-8")
    quitar = [
        i
        for i, n in re.findall(r'<w:footnote (?:(?!/>)[^>])*?w:id="([1-9]\d*)"[^>/]*>(.*?)</w:footnote>', fx, re.S)
        if re.match(r"\W*(?:La )?[Dd]enuncia (?:presentada|se encuentra fechada)", NT.texto(n).strip())
    ]
    if not quitar:
        return
    for i in quitar:
        x = re.sub(r'<w:r(?: [^>]*)?>(?:(?!</w:r>).)*?<w:footnoteReference [^>]*w:id="%s"[^>]*/>(?:(?!</w:r>).)*?</w:r>' % i, "", x, count=1, flags=re.S)
        fx = re.sub(r'<w:footnote (?:(?!/>)[^>])*?w:id="%s"[^>/]*>.*?</w:footnote>' % i, "", fx, count=1, flags=re.S)
    x, fx = renumerar(x, fx)
    datos["word/document.xml"] = x.encode("utf-8")
    datos["word/footnotes.xml"] = fx.encode("utf-8")
    _escribir(ruta, infos, datos)
    print("  nota sobre la presentacion de la denuncia quitada (R-167)")


def sanear(ruta) -> None:
    """Orden medido: cada paso deja el documento listo para el siguiente."""
    p = Path(ruta)
    depurar(p)
    nota_presentacion(p)
    separar(p)
    NP.process_docx(p, aplicar=True)
    preparar_traslado(p)
    NT.main([str(p), "--aplicar"])
    traslado_sobrantes(p)
    M31.procesar(p, True)
    nota_codigo(p)
    nota_competencia(p)
    notas_repetidas(p)
    ADI.migrar_docx(p, True)
    UT.main([str(p), "--aplicar"])


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    for a in argv:
        sanear(a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
