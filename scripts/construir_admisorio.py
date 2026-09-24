#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construye un admisorio sobre una plantilla, sin abrir Word, con control de residuos.

Por que existe, con la medicion delante:

En el Expediente 3122-2026 (14/09/2026) el agente intento construir el documento
con `win32com` y escribio **cinco** scratch sucesivos (`scratch_com`, `_com2`,
`_com3`, `_com4`) peleandose con `DisplayAlerts` y `try/except`. Diez de sus
dieciseis minutos se fueron ahi, y el resultado quedo **NO APTO**. Dos causas
distintas, y las dos se arreglan aqui:

1. **Word sobra.** Un `.docx` es un ZIP de XML. Editarlo cuesta ~0,3 s y no deja
   procesos huerfanos. Abrir Word cuesta 8,4 s y es la causa medida de cuelgue.

2. **El reemplazo a ciegas inventa.** Sustituir "Pacifico" por "Interseguro" deja
   intacto **todo lo que el redactor no penso en listar**: fechas, polizas,
   apellidos y hechos del caso de origen se quedan dentro, con aspecto de dato
   verdadero. Es la forma mas silenciosa de inventar que existe en este sistema.

De ahi que la parte importante de este script no sea reemplazar, sino **negarse a
entregar** si quedo residuo. Tras aplicar el mapa, el documento se audita contra:

  - las **claves** del propio mapa (si una sigue presente, el reemplazo fallo);
  - el **numero de expediente de la plantilla** (TPL_2180_2025 -> "2180-2025");
  - cualquier **aseguradora o banco** que no sea parte del caso;
  - los marcadores `[FALTA: ...]` que el redactor haya dejado a proposito.

Uso:
    python scripts/construir_admisorio.py --mapa mapa.json

`mapa.json`:
    {
      "plantilla": "plantillas_maestras/.../TPL_2180_2025_....docx",
      "salida":    "C:/Users/D/Desktop/expedientes/3122-2026/RES_01_....docx",
      "partes":    ["Interseguro", "Cornejo"],
      "reemplazos": {"texto viejo": "texto nuevo", ...},
      "insertar_despues": {"texto del parrafo ancla": ["parrafo nuevo 1", ...]}
    }

`insertar_despues` AÑADE parrafos: cada uno es un clon del parrafo ancla (misma
sangria, numeracion (i)/(ii) y formato de cada tramo) con el texto nuevo, y va
detras del ancla en el orden dado. Sirve para una imputacion o un hecho mas de
los que trae la plantilla. El ancla es un fragmento del texto del parrafo YA
reemplazado, que debe aparecer en un solo parrafo. Las llamadas de nota del
ancla no se copian. (Exp. 2898-2026: sin esto no habia forma de agregar dos
imputaciones por 88.1 y el agente se atasco 300 pasos.)

Los `reemplazos` se aplican en `document.xml`, encabezados, pies y notas al pie,
son sensibles a que el texto este partido en varios `run`, y se aplican de clave
mas larga a mas corta para que los solapamientos tengan una regla unica: manda la
mas especifica.

Una clave que no coincida al caracter con la plantilla --sobra un espacio, falta
una tilde, se colo la llamada de una nota-- se **alinea sola** con el parrafo que
se le parece por encima del 92 %, y la alineacion se imprime. Cazar esa diferencia
a ojo costaba una vuelta entera del bucle del agente por cada clave.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import unicodedata
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

RE_PARRAFO = re.compile(r"<w:p\b[^>]*>.*?</w:p>", re.S)
# `[^>/]`: una etiqueta autocerrada `<w:t xml:space="preserve"/>` no abre texto;
# con `[^>]` se tomaba por apertura y se comia hasta el siguiente </w:t>.
# Correccion detectada por Antigravity en el Exp. 2898-2026 (23/09/2026).
RE_TEXTO = re.compile(r"(<w:t(?:\s[^>/]*)?>)(.*?)(</w:t>)", re.S)
# Ojo: `<w:t[^>]*>` tambien captura `<w:tab>` y `<w:tabs>`, y entonces el "texto"
# del parrafo se llena de XML crudo. Costo medido: 14 reemplazos del Exp. 3122-2026
# declarados inexistentes cuando si estaban.
RE_FALTA = re.compile(r"\[FALTA:[^\]]*\]")

# Aseguradoras, bancos y corredores del corpus. Si en el documento final aparece
# una que no es parte del caso, viene de la plantilla y es residuo.
MARCAS = (
    "RIMAC",
    "PACIFICO",
    "PACÍFICO",
    "MAPFRE",
    "INTERSEGURO",
    "LA POSITIVA",
    "CARDIF",
    "BNP PARIBAS",
    "PROTECTA",
    "VIVIR SEGUROS",
    "SANITAS",
    "CRECER",
    "CHUBB",
    "QUALITAS",
    "QUÁLITAS",
    "BCP",
    "BANCO DE CREDITO",
    "BANCO DE CRÉDITO",
    "INTERBANK",
    "SCOTIABANK",
    "BBVA",
    "FALABELLA",
    "RIPLEY",
    "CREDISCOTIA",
    "PICHINCHA",
    "SANTANDER",
)

PARTES_XML = ("word/document.xml", "word/footnotes.xml", "word/endnotes.xml")


def sin_tildes(t: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn"
    )


def texto_parrafo(parrafo: str) -> str:
    return "".join(m.group(2) for m in RE_TEXTO.finditer(parrafo))


RE_TOKEN = re.compile(r"\w+|\s+|[^\w\s]")


def reescribir_parrafo(parrafo: str, nuevo: str) -> str:
    """Cambia el texto del parrafo conservando el `run` (y su formato) de cada tramo.

    Antes todo el texto nuevo iba al PRIMER `run` y los demas se vaciaban. Si ese
    primer run era el rotulo «SEGUNDO:» en negrita, el parrafo entero salia en
    negrita; si era «A LA POSITIVA» subrayado, el parrafo entero salia subrayado;
    y las llamadas de nota, que viven entre runs, se iban juntas al final.
    Medido en el Exp. 2898-2026 (23/09/2026): las tres quejas del instructor
    tenian esta unica causa.

    Ahora se alinea el texto viejo con el nuevo palabra a palabra: lo que no
    cambia se queda en su run; lo que cambia entra en el run donde empezaba el
    tramo sustituido. Asi la negrita, el subrayado y las notas al pie siguen
    donde estaban. La concatenacion de los runs es siempre exactamente `nuevo`.

    **Si el texto nuevo es vacio, el parrafo entero desaparece.** Vaciarle el
    texto y dejar el `<w:p>` es lo que produce la vineta huerfana: un parrafo con
    numeracion activa y sin contenido, que Word pinta como un numero suelto y que
    R-105 declara falsador. Medido en el Exp. 3122-2026: seis de golpe.
    """
    if not nuevo.strip():
        return ""
    trozos = list(RE_TEXTO.finditer(parrafo))
    if not trozos:
        return parrafo
    viejos = [m.group(2) for m in trozos]
    viejo = "".join(viejos)
    dueno = [k for k, t in enumerate(viejos) for _c in t]
    nuevos = [""] * len(trozos)
    if not viejo:
        nuevos[0] = nuevo
    else:
        a, b = RE_TOKEN.findall(viejo), RE_TOKEN.findall(nuevo)
        pa, pb = [0], [0]
        for t in a:
            pa.append(pa[-1] + len(t))
        for t in b:
            pb.append(pb[-1] + len(t))
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                for c in range(pa[i1], pa[i2]):
                    nuevos[dueno[c]] += viejo[c]
            elif tag == "insert":
                c = pa[i1]
                nuevos[dueno[c] if c < len(viejo) else dueno[-1]] += nuevo[pb[j1] : pb[j2]]
            elif tag == "replace":
                # El run que ocupaba la mayor parte del tramo sustituido: un
                # subrayado corto al inicio del tramo no se extiende a todo.
                cuenta: dict[int, int] = {}
                for c in range(pa[i1], pa[i2]):
                    cuenta[dueno[c]] = cuenta.get(dueno[c], 0) + 1
                k = max(sorted(cuenta), key=lambda d: cuenta[d])
                nuevos[k] += nuevo[pb[j1] : pb[j2]]
    assert "".join(nuevos) == nuevo
    piezas, fin = [], 0
    for m, t in zip(trozos, nuevos):
        piezas.append(parrafo[fin : m.start()])
        piezas.append('<w:t xml:space="preserve">%s</w:t>' % t)
        fin = m.end()
    piezas.append(parrafo[fin:])
    return "".join(piezas)


def por_longitud(reemplazos: dict[str, str]) -> list[tuple[str, str]]:
    """De mas larga a mas corta.

    Sin esto el orden lo decide el JSON y los solapamientos se vuelven un azar:
    si `108059` se aplica antes que la frase que lo contiene, la frase ya no
    encaja; si se aplica despues, es la frase la que se llevo el numero. Con el
    orden fijo, la regla es una sola y explicable: **manda la mas especifica**.
    """
    return sorted(reemplazos.items(), key=lambda kv: -len(kv[0]))


def _en_parrafos(xml: str, viejo: str, nuevo: str) -> tuple[str, int]:
    """Sustituye `viejo` en el texto UNIDO de cada parrafo (sirve aunque la frase
    este partida en varios runs por una negrita o un subrayado)."""
    piezas: list[str] = []
    fin = 0
    n = 0
    for m in RE_PARRAFO.finditer(xml):
        parrafo = m.group(0)
        texto = texto_parrafo(parrafo)
        if viejo not in texto:
            continue
        n += texto.count(viejo)
        piezas.append(xml[fin : m.start()])
        piezas.append(reescribir_parrafo(parrafo, texto.replace(viejo, nuevo)))
        fin = m.end()
    piezas.append(xml[fin:])
    return "".join(piezas), n


def _ventana(texto: str, clave: str) -> tuple[int, int, float] | None:
    """Tramo de `texto` que mas se parece a `clave` (clave = fragmento de parrafo).

    Se ancla en los bloques coincidentes extremos y se ajusta a limites de
    palabra. Devuelve (inicio, fin, parecido) o None."""
    sm = difflib.SequenceMatcher(None, texto, clave, autojunk=False)
    bloques = [b for b in sm.get_matching_blocks() if b.size >= 4]
    if not bloques:
        return None
    ini = max(0, bloques[0].a - bloques[0].b)
    fin = min(len(texto), bloques[-1].a + bloques[-1].size + (len(clave) - bloques[-1].b - bloques[-1].size))
    while ini > 0 and texto[ini - 1].isalnum() and texto[ini].isalnum():
        ini -= 1
    while fin < len(texto) and fin > 0 and texto[fin - 1].isalnum() and texto[fin].isalnum():
        fin += 1
    r = difflib.SequenceMatcher(None, texto[ini:fin], clave, autojunk=False).ratio()
    return ini, fin, r


def _clave_inicio(t: str) -> str:
    return re.sub(r"\s+", " ", t).strip()


def aplicar_parrafos(xml: str, parrafos: dict[str, str]) -> tuple[str, list[str]]:
    """`"parrafos": {"inicio del parrafo": "texto nuevo" | ""}` (v3.1).

    Reemplaza (o borra, con "") el parrafo ENTERO cuyo texto empieza por la
    clave, conservando el formato de cada tramo y sus llamadas de nota. La clave
    debe identificar un solo parrafo. Evita copiar parrafos largos al caracter
    en `reemplazos`, que era donde se iban las vueltas del redactor."""
    fallos = []
    for inicio, nuevo in parrafos.items():
        clave = _clave_inicio(inicio)
        cand = [
            m for m in RE_PARRAFO.finditer(xml)
            if _clave_inicio(texto_parrafo(m.group(0))).startswith(clave)
        ]
        if len(cand) != 1:
            fallos.append(
                "parrafos: «%s…» identifica %d parrafos (debe ser 1): alarga la clave"
                % (clave[:60], len(cand))
            )
            continue
        m = cand[0]
        xml = xml[: m.start()] + reescribir_parrafo(m.group(0), nuevo) + xml[m.end():]
    return xml, fallos


def aplicar(xml: str, reemplazos: dict[str, str]) -> tuple[str, dict[str, int]]:
    """Aplica el mapa clave por clave, de la mas larga a la mas corta (v3.1).

    Por que asi (revision del instructor, 24/09/2026, admisorio 9999-2026):

    - Antes una clave que coincidia contigua en UN sitio se daba por aplicada y
      las demas apariciones --partidas en varios runs por una negrita o un
      subrayado-- se quedaban sin sustituir: «Banco de Crédito del Perú S.A.»
      sobrevivio en el rotulo del requerimiento, TERCERO, QUINTO y SEXTO. Ahora
      cada clave se busca en el XML contiguo Y en el texto unido de cada parrafo.
    - Antes las etapas iban por separado y una clave corta de la primera etapa
      rompia una frase larga que solo casaba en la segunda. Ahora la regla «manda
      la mas especifica» vale en todas las etapas: cada clave hace todas sus
      etapas antes de pasar a la siguiente mas corta.
    - La alineacion aproximada ya no sustituye el parrafo entero cuando la clave
      es un fragmento: sustituye solo el tramo que se parece (el rotulo «A Seguros
      Ficticios S.A.: (i)» se perdia).
    """
    malos = [v for v in reemplazos.values() if re.search(r"__\S|\S__|\*\*[A-Za-zÁÉÍÓÚÑáéíóúñ]", v)]
    if malos:
        raise SystemExit(
            "Reemplazo con marcas de markdown (%r): el subrayado y la negrita ya estan en "
            "el formato de la plantilla; escribe solo el texto (R-177)." % malos[0][:60]
        )
    hechos: dict[str, int] = {}
    alineados: dict[str, tuple[str, float]] = {}

    for viejo, nuevo in por_longitud(reemplazos):
        n = 0
        # 1) Contiguo en el XML: lo barato. Una supresion no se hace aqui: borrar
        # texto a pelo deja el <w:p> vacio con su numeracion viva (R-105).
        if nuevo.strip():
            n = xml.count(viejo)
            if n:
                xml = xml.replace(viejo, nuevo)
        # 2) Partido en varios runs: en el texto unido de cada parrafo. Si el
        # nuevo contiene al viejo y ya se aplico, repetir lo duplicaria.
        if not (n and viejo in nuevo):
            xml, k = _en_parrafos(xml, viejo, nuevo)
            n += k
        if n:
            hechos[viejo] = n
            continue
        # 3) Alineacion: la clave no coincide al caracter (un espacio, una tilde,
        # la llamada de una nota). Solo claves largas: una corta casa con todo.
        if len(viejo) < 40:
            continue
        # Todas las apariciones que se parezcan (la considerativa y su espejo en
        # el resolutivo): alinear solo la mejor dejaba la otra con el residuo.
        candidatos = []
        for m in RE_PARRAFO.finditer(xml):
            texto = texto_parrafo(m.group(0))
            if len(texto.strip()) <= 20:
                continue
            if len(viejo) >= 0.9 * len(texto.strip()):
                r = difflib.SequenceMatcher(None, viejo, texto.strip()).ratio()
                tramo = (0, len(texto), r)
            else:
                tramo = _ventana(texto, viejo)
                if tramo is None:
                    continue
            if tramo[2] >= 0.92:
                candidatos.append((m.start(), m.end(), m.group(0), texto) + tramo)
        for ini, fin_p, parrafo, texto, a, b, r in reversed(candidatos):
            nuevo_texto = texto[:a] + nuevo + texto[b:]
            xml = xml[:ini] + reescribir_parrafo(parrafo, nuevo_texto if nuevo_texto.strip() else "") + xml[fin_p:]
        if candidatos:
            hechos[viejo] = len(candidatos)
            ini, fin_p, parrafo, texto, a, b, r = max(candidatos, key=lambda c: c[-1])
            alineados[viejo] = (texto[a:b].strip() or texto.strip(), r)

    return xml, hechos, alineados


RE_NUMPR = re.compile("<w:numPr[ />]")


RE_INICIALES = re.compile(r"[A-ZÑ]{2,5}(?:/[A-ZÑ]{2,5})+")


def fijar_iniciales(xml: str) -> str:
    """Las iniciales de redaccion («LSQ/DCQ») salen de config/firmas.json, no de la
    plantilla: cada plantilla trae las de su redactor (LSM/JCQ, LGP/JCQ...)."""
    try:
        ini = json.loads((RAIZ / "config/firmas.json").read_text(encoding="utf-8")).get("iniciales")
    except Exception:
        ini = None
    if not ini:
        return xml

    def _p(m):
        p = m.group(0)
        if RE_INICIALES.fullmatch(texto_parrafo(p).strip()):
            return reescribir_parrafo(p, ini)
        return p

    return RE_PARRAFO.sub(_p, xml)


FIRMANTES = ("EVELING ROA QUISPE", "LUISA ANALÍ SILVA MALPARTIDA", "LUISA ANALI SILVA MALPARTIDA")


def fijar_firma(xml: str) -> str:
    """Firmante y cargo segun config/firmas.json y los denunciados del
    encabezado (R-103): Rimac -> Secretaria Tecnica Ad Hoc; los demas -> la
    titular. La plantilla trae la firma de SU caso, no la de este."""
    try:
        cfg = json.loads((RAIZ / "config/firmas.json").read_text(encoding="utf-8"))
    except Exception:
        return xml
    parrafos = list(RE_PARRAFO.finditer(xml))
    textos = [texto_parrafo(m.group(0)).strip() for m in parrafos]
    ini = next((k for k, t in enumerate(textos[:30]) if sin_tildes(t).upper().startswith("DENUNCIAD")), None)
    fin = next((k for k in range(ini or 0, min(len(textos), 30)) if sin_tildes(textos[k]).upper().startswith("MATERIA")), None)
    bloque = sin_tildes(" ".join(textos[ini:fin] if ini is not None and fin else [])).upper()
    firma = cfg["titular"]
    for exc in cfg.get("excepciones", []):
        if any(sin_tildes(c).upper() in bloque for c in exc["si_denunciado_contiene"]):
            firma = exc
    k = next((k for k, t in enumerate(textos) if sin_tildes(t).upper() in {sin_tildes(f) for f in FIRMANTES}), None)
    if k is None:
        return xml
    j = next((j for j in range(k + 1, min(k + 4, len(textos))) if textos[j].startswith("Secretaria")), None)
    cambios = [(k, firma["nombre"])] + ([(j, firma["cargo"])] if j is not None else [])
    for idx, nuevo in sorted(cambios, reverse=True):
        m = parrafos[idx]
        if textos[idx] != nuevo:
            xml = xml[: m.start()] + reescribir_parrafo(m.group(0), nuevo) + xml[m.end():]
    return xml


def insertar_despues(
    xml: str, fx: str, inserciones: dict
) -> tuple[str, str, list[str]]:
    """Clona el parrafo ancla por cada texto nuevo y lo coloca detras de el.

    Cada elemento es un texto o {"texto": ..., "nota": "<norma>"}: con `nota`,
    el parrafo termina con la llamada a la nota normativa del corpus
    (docs/notas_normas.json, p. ej. "numeral 88.1 del artículo 88")."""
    fallos: list[str] = []
    catalogo = {}
    ruta_cat = RAIZ / "docs" / "notas_normas.json"
    if ruta_cat.exists():
        catalogo = json.loads(ruta_cat.read_text(encoding="utf-8"))
    ids = [int(i) for i in re.findall(r'<w:footnote\b[^>]*w:id="(-?\d+)"', fx)]
    siguiente = max([0] + ids) + 1
    ref_modelo = re.search(
        r"<w:r\b(?:(?!</w:r>).)*?<w:footnoteReference\b[^>]*/>(?:(?!</w:r>).)*?</w:r>",
        xml,
        re.S,
    )
    for ancla, nuevos in inserciones.items():
        if isinstance(nuevos, (str, dict)):
            nuevos = [nuevos]
        cand = [m for m in RE_PARRAFO.finditer(xml) if ancla in texto_parrafo(m.group(0))]
        if len(cand) != 1:
            fallos.append(
                "insertar_despues: el ancla %r aparece en %d parrafos (debe ser 1)"
                % (ancla[:60], len(cand))
            )
            continue
        m = cand[0]
        base = re.sub(
            r"<w:r\b(?:(?!</w:r>).)*?<w:footnoteReference\b[^>]*/>(?:(?!</w:r>).)*?</w:r>",
            "",
            m.group(0),
            flags=re.S,
        )
        base = re.sub(r'\s(?:w14:paraId|w14:textId)="[^"]*"', "", base)
        clones = []
        for item in nuevos:
            texto = item.get("texto", "") if isinstance(item, dict) else item
            if not texto.strip():
                continue
            modelo = item.get("modelo") if isinstance(item, dict) else None
            base_item = base
            if modelo:
                # v3.1: clonar OTRO parrafo como molde (p. ej. la linea de
                # continuacion del encabezado para un segundo denunciante).
                mods = [q for q in RE_PARRAFO.finditer(xml) if modelo in texto_parrafo(q.group(0))]
                if len(mods) != 1:
                    fallos.append(
                        "insertar_despues: el modelo %r aparece en %d parrafos (debe ser 1)"
                        % (modelo[:60], len(mods))
                    )
                    continue
                base_item = re.sub(
                    r"<w:r\b(?:(?!</w:r>).)*?<w:footnoteReference\b[^>]*/>(?:(?!</w:r>).)*?</w:r>",
                    "",
                    mods[0].group(0),
                    flags=re.S,
                )
                base_item = re.sub(r'\s(?:w14:paraId|w14:textId)="[^"]*"', "", base_item)
            clon = reescribir_parrafo(base_item, texto)
            nota = item.get("nota") if isinstance(item, dict) else None
            if nota:
                if nota not in catalogo:
                    fallos.append(
                        "insertar_despues: no hay nota catalogada para %r (docs/notas_normas.json: %s)"
                        % (nota, ", ".join(sorted(catalogo)[:12]))
                    )
                    continue
                if not ref_modelo:
                    fallos.append("insertar_despues: la plantilla no tiene llamadas de nota que clonar")
                    continue
                run = re.sub(
                    r'(<w:footnoteReference\b[^>]*w:id=")\d+(")',
                    lambda g: g.group(1) + str(siguiente) + g.group(2),
                    ref_modelo.group(0),
                    count=1,
                )
                clon = clon[: clon.rindex("</w:p>")] + run + "</w:p>"
                fx = fx.replace(
                    "</w:footnotes>",
                    '<w:footnote w:id="%d">%s</w:footnote></w:footnotes>'
                    % (siguiente, catalogo[nota]["xml"]),
                    1,
                )
                siguiente += 1
            clones.append(clon)
        xml = xml[: m.end()] + "".join(clones) + xml[m.end() :]
    return xml, fx, fallos


def limpiar_vinetas_huerfanas(xml: str) -> tuple[str, int]:
    """Quita los parrafos que quedaron con numeracion y sin texto.

    Word pinta esos parrafos como un numero suelto colgando, y `verificar_admisorio`
    los declara falsador (R-105). Da igual como se hayan producido --una supresion,
    una plantilla que ya los traia--: si un parrafo tiene `<w:numPr>` y ni una
    letra, sobra.
    """
    piezas: list[str] = []
    fin = 0
    quitados = 0
    for m in RE_PARRAFO.finditer(xml):
        parrafo = m.group(0)
        if RE_NUMPR.search(parrafo) and not texto_parrafo(parrafo).strip():
            piezas.append(xml[fin : m.start()])
            fin = m.end()
            quitados += 1
    piezas.append(xml[fin:])
    return "".join(piezas), quitados


RE_NOTA = re.compile(r'<w:footnote\b[^>]*w:id="(-?\d+)"[^>]*>.*?</w:footnote>', re.S)
RE_NOTA_DEL_CASO = re.compile(r"^\W*(?:\d+\s*)?Denuncia (?:remitida|desacumulada)")


def texto_plano(datos: dict[str, bytes]) -> str:
    """Texto que puede traer datos del caso de origen.

    De las notas al pie solo cuenta la de la denuncia (traslado o
    desacumulacion): las demas transcriben normas, y sus fechas («publicado el
    2 de setiembre de 2010») no son residuo. Medido en el 9999-2026: cinco
    «datos duros heredados» falsos, todos de notas normativas."""
    trozos = []
    for nombre, crudo in datos.items():
        if not (nombre.startswith("word/") and nombre.endswith(".xml")):
            continue
        xml = crudo.decode("utf-8", "replace")
        if nombre == "word/footnotes.xml":
            xml = " ".join(
                m.group(0)
                for m in RE_NOTA.finditer(xml)
                if RE_NOTA_DEL_CASO.match(re.sub(r"<[^>]+>", "", m.group(0)).strip())
            )
        trozos.append(re.sub(r"<[^>]+>", " ", xml))
    return " ".join(trozos)


MESES = (
    "enero|febrero|marzo|abril|mayo|junio|julio|agosto|"
    "setiembre|septiembre|octubre|noviembre|diciembre"
)
RE_FECHA = re.compile(r"\d{1,2} de (?:%s) de \d{4}" % MESES, re.I)
RE_MONTO = re.compile(r"(?:US\$|S/)\s?[\d][\d\s.,]{2,}\d")
RE_CIFRA = re.compile(r"\b\d{6,}\b")  # polizas, siniestros, RUC, certificados
# Identificadores del caso de origen con menos de 6 cifras («Póliza 49645»,
# «Reclamo 777»): RE_CIFRA no los veia y la Póliza 49645 sobrevivio en SEXTO.
RE_IDENTIFICADOR = re.compile(
    r"\b(?:P[óo]liza|Certificado|Reclamo|Siniestro|Carta|Oficio|Solicitud|Cr[ée]dito)\s+(?:N[°º.]?\s*)?[\w/-]*\d[\w/-]*",
    re.I,
)


def datos_duros(texto: str) -> set[str]:
    """Fechas, montos y numeros largos: lo que un admisorio no puede heredar."""
    duros: set[str] = set()
    for patron in (RE_FECHA, RE_MONTO, RE_CIFRA, RE_IDENTIFICADOR):
        duros.update(
            re.sub(r"\s+", " ", m.group(0)).strip() for m in patron.finditer(texto)
        )
    return duros


def auditar_residuos(
    texto: str,
    reemplazos: dict[str, str],
    hechos: dict[str, int],
    plantilla: Path,
    partes: list[str],
    duros_plantilla: set[str] | None = None,
    conservar: list[str] | None = None,
    parrafos_plantilla: list[str] | None = None,
) -> list[str]:
    fallos: list[str] = []

    # Una clave puede no haberse aplicado porque OTRA mas larga ya se llevo ese
    # texto. Eso no es un fallo: es el solapamiento resolviendose como debe, y
    # reportarlo como fallo hacia iterar al redactor sobre un problema inexistente
    # (medido en el Exp. 3122-2026: 11 de 19 «fallos» eran de esta clase).
    aplicados = [v for v in reemplazos if v in hechos]
    for v in reemplazos:
        if v in hechos:
            continue
        mayor = next((a for a in aplicados if v in a and a != v), None)
        if mayor:
            continue  # consumido por un reemplazo mas especifico
        if "\n" in v:
            # Un `<w:p>` es una unidad: ninguna clave puede cruzarlo. Decirlo por
            # su nombre ahorra la vuelta entera que costaba descubrirlo a ciegas.
            trozos = [t.strip() for t in v.split("\n") if t.strip()]
            fallos.append(
                "el reemplazo '%s...' abarca %d parrafos: una clave no puede cruzar "
                "un salto de parrafo. Divide el reemplazo en %d, uno por parrafo."
                % (v.replace("\n", " / ")[:60], len(trozos), len(trozos))
            )
            continue

        aviso = (
            "el reemplazo '%s' no encontro nada en la plantilla: el texto difiere"
            % v[:80]
        )
        # Decir solo «no encontro nada» obliga a adivinar. Se ensena el parrafo de
        # la plantilla que mas se le parece: con eso el mapa se corrige de una vez
        # en lugar de a base de intentos.
        cercanos = difflib.get_close_matches(
            v, parrafos_plantilla or [], n=1, cutoff=0.5
        )
        if cercanos:
            aviso += "\n           la plantilla dice: '%s'" % cercanos[0][:150]
        else:
            aviso += " (construye el mapa con inspeccionar_docx.py, no de memoria)"
        fallos.append(aviso)

    for v, n in reemplazos.items():
        # Si la clave forma parte de su propio reemplazo (p. ej. «Secretaria
        # Tecnica» -> «Secretaria Tecnica (e)») seguira presente por definicion y
        # no es residuo.
        if v and v in texto and v not in n:
            fallos.append("quedo texto del caso de origen sin sustituir: '%s'" % v[:70])

    m = re.search(r"TPL_(\d{3,4})_(\d{4})", plantilla.name)
    if m:
        origen = "%s-%s" % (m.group(1), m.group(2))
        if origen in texto:
            fallos.append(
                "quedo el numero de expediente de la plantilla (%s) dentro del documento"
                % origen
            )

    alto = sin_tildes(texto).upper()
    permitidas = {sin_tildes(p).upper() for p in partes}
    for marca in MARCAS:
        m_alto = sin_tildes(marca).upper()
        if m_alto in alto and not any(m_alto in p or p in m_alto for p in permitidas):
            fallos.append(
                "aparece '%s', que no es parte de este caso: viene de la plantilla"
                % marca
            )

    for f in sorted(set(RE_FALTA.findall(texto))):
        fallos.append("marcador sin resolver: %s" % f)

    # Lo que ninguna lista de marcas detecta: una fecha, un monto o un numero de
    # poliza del caso de origen que sobrevivio al mapa. Es residuo indistinguible
    # de un dato real, y por eso se declara uno por uno.
    if duros_plantilla:
        permitido = set(conservar or [])
        permitido.update(reemplazos.values())
        sobreviven = sorted(
            d
            for d in duros_plantilla
            if d in texto and not any(d in p for p in permitido)
        )
        for d in sobreviven[:15]:
            fallos.append(
                "dato duro heredado de la plantilla: '%s' — o lo reemplazas, o lo "
                'declaras en "conservar" si de verdad es de este caso' % d
            )
        if len(sobreviven) > 15:
            fallos.append("...y %d datos duros heredados mas" % (len(sobreviven) - 15))

    return fallos


def construir(mapa: dict) -> int:
    plantilla = Path(mapa["plantilla"])
    if not plantilla.is_absolute():
        plantilla = RAIZ / plantilla
    salida = Path(mapa["salida"])
    reemplazos: dict[str, str] = mapa["reemplazos"]
    partes: list[str] = mapa.get("partes", [])

    if not plantilla.exists():
        print("No existe la plantilla: %s" % plantilla)
        return 2

    salida.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(plantilla) as z:
        nombres = z.namelist()
        datos = {n: z.read(n) for n in nombres}
    duros_plantilla = datos_duros(texto_plano(datos))
    parrafos_plantilla = [
        texto_parrafo(m.group(0)).strip()
        for m in RE_PARRAFO.finditer(
            datos["word/document.xml"].decode("utf-8", "replace")
        )
    ]
    parrafos_plantilla = [t for t in parrafos_plantilla if len(t) > 20]

    objetivo = [
        n
        for n in nombres
        if n in PARTES_XML or re.match(r"word/(header|footer)\d+\.xml", n)
    ]
    hechos: dict[str, int] = {}
    alineados: dict[str, tuple[str, float]] = {}
    huerfanas = 0
    if mapa.get("parrafos"):
        x_par, fallos_par = aplicar_parrafos(datos["word/document.xml"].decode("utf-8"), mapa["parrafos"])
        if fallos_par:
            raise SystemExit("\n".join(fallos_par))
        datos["word/document.xml"] = x_par.encode("utf-8")
    for n in objetivo:
        xml = datos[n].decode("utf-8")
        xml, parciales, alin = aplicar(xml, reemplazos)
        if n == "word/document.xml":
            xml, huerfanas = limpiar_vinetas_huerfanas(xml)
            xml = fijar_iniciales(xml)
        datos[n] = xml.encode("utf-8")
        for k, v in parciales.items():
            hechos[k] = hechos.get(k, 0) + v
        alineados.update(alin)

    if mapa.get("insertar_despues"):
        x_ins, fx_ins, fallos_ins = insertar_despues(
            datos["word/document.xml"].decode("utf-8"),
            datos["word/footnotes.xml"].decode("utf-8"),
            mapa["insertar_despues"],
        )
        if fallos_ins:
            raise SystemExit("\n".join(fallos_ins))
        sys.path.insert(0, str(RAIZ / "scripts" / "migraciones"))
        import notas_traslado

        datos["word/document.xml"] = x_ins.encode("utf-8")
        datos["word/footnotes.xml"] = notas_traslado.ordenar_notas(fx_ins, x_ins).encode("utf-8")

    # v3.1: las reglas generales se aplican a TODO documento que sale del
    # constructor, venga de la plantilla que venga (las mismas que la migracion
    # del corpus; cada una tiene su falsador en verificar_admisorio.py).
    sys.path.insert(0, str(RAIZ / "scripts" / "migraciones"))
    import migrar_v3_1
    import notas_pie

    x = fijar_firma(datos["word/document.xml"].decode("utf-8"))
    fx = datos["word/footnotes.xml"].decode("utf-8") if "word/footnotes.xml" in datos else ""
    informe_notas: list[str] = []
    if fx:
        x, fx, informe_notas = notas_pie.nota_de_la_norma(x, fx)
    x, fx, normalizacion = migrar_v3_1.migrar(x, fx)
    datos["word/document.xml"] = x.encode("utf-8")
    if fx:
        datos["word/footnotes.xml"] = fx.encode("utf-8")

    with zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED) as z:
        for n in nombres:
            z.writestr(n, datos[n])

    print("=" * 78)
    print("CONSTRUCCION  %s" % salida.name)
    print("=" * 78)
    print("  Plantilla: %s" % plantilla.name)
    print("  Reemplazos aplicados: %d de %d" % (len(hechos), len(reemplazos)))
    print("  Sin abrir Word. Ningun proceso WINWORD.EXE involucrado.")
    if huerfanas:
        print(
            "  Vinetas huerfanas retiradas: %d (parrafos numerados sin texto, R-105)"
            % huerfanas
        )
    hecho_v31 = {k: v for k, v in normalizacion.items() if v}
    if hecho_v31 or informe_notas:
        print()
        print("  NORMALIZACION v3.1 (reglas generales, sin intervencion del redactor):")
        for k, v in sorted(hecho_v31.items()):
            print("    %4d  %s" % (v, k))
        for linea in informe_notas:
            print("          %s" % linea)
    if alineados:
        print()
        print("  ALINEADOS AUTOMATICAMENTE (tu clave no coincidia al caracter):")
        for viejo_k, (real, r) in alineados.items():
            print("    %.0f%%  tu clave: '%s'" % (r * 100, viejo_k[:66]))
            print("          documento: '%s'" % real[:66])
    print()

    fallos = auditar_residuos(
        texto_plano(datos),
        reemplazos,
        hechos,
        plantilla,
        partes,
        duros_plantilla,
        list(mapa.get("conservar", [])) + list((mapa.get("parrafos") or {}).values()),
        parrafos_plantilla,
    )
    print("AUDITORIA DE RESIDUOS DEL CASO DE ORIGEN")
    print("-" * 78)
    if not fallos:
        print("  Sin residuo. Ningun dato de la plantilla sobrevive en el documento.")
    else:
        for f in fallos:
            print("  FALLA  %s" % f)
        print()
        print("  El documento se escribio, pero NO es entregable: un dato del caso de")
        print("  origen dentro de este admisorio es informacion inventada.")
        print()
        print("  Orden de arreglo: primero los reemplazos que no se aplicaron. Un dato")
        print(
            "  duro suele seguir dentro porque la frase que lo contenia no se sustituyo,"
        )
        print("  asi que arreglar un reemplazo cierra varios falsadores de golpe.")
    print()
    print("  Siguiente paso:")
    print('  python scripts/admisorio.py entregar "%s"' % salida)
    return 1 if fallos else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--mapa", required=True, help="JSON con plantilla, salida y reemplazos"
    )
    args = ap.parse_args(argv[1:])
    mapa = json.loads(Path(args.mapa).read_text(encoding="utf-8"))
    return construir(mapa)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
