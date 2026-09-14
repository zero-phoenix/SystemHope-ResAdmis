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
      "reemplazos": {"texto viejo": "texto nuevo", ...}
    }

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
RE_TEXTO = re.compile(r"(<w:t(?:\s[^>]*)?>)(.*?)(</w:t>)", re.S)
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


def reescribir_parrafo(parrafo: str, nuevo: str) -> str:
    """Deja el texto del parrafo en su primer `run` y vacia los demas.

    Es lo que permite sustituir una frase partida en varios `run`, que es el caso
    normal en documentos que han pasado por Word.

    **Si el texto nuevo es vacio, el parrafo entero desaparece.** Vaciarle el
    texto y dejar el `<w:p>` es lo que produce la vineta huerfana: un parrafo con
    numeracion activa y sin contenido, que Word pinta como un numero suelto y que
    R-105 declara falsador. Medido en el Exp. 3122-2026: seis de golpe.
    """
    if not nuevo.strip():
        return ""

    primero = {"si": True}

    def _sub(m: re.Match) -> str:
        if primero["si"]:
            primero["si"] = False
            return '<w:t xml:space="preserve">%s</w:t>' % nuevo
        return m.group(1) + m.group(3)

    return RE_TEXTO.sub(_sub, parrafo)


def por_longitud(reemplazos: dict[str, str]) -> list[tuple[str, str]]:
    """De mas larga a mas corta.

    Sin esto el orden lo decide el JSON y los solapamientos se vuelven un azar:
    si `108059` se aplica antes que la frase que lo contiene, la frase ya no
    encaja; si se aplica despues, es la frase la que se llevo el numero. Con el
    orden fijo, la regla es una sola y explicable: **manda la mas especifica**.
    """
    return sorted(reemplazos.items(), key=lambda kv: -len(kv[0]))


def aplicar(xml: str, reemplazos: dict[str, str]) -> tuple[str, dict[str, int]]:
    hechos: dict[str, int] = {}

    # 1) Lo que este contiguo se sustituye directo: es lo barato y lo mas comun.
    for viejo, nuevo in por_longitud(reemplazos):
        if not nuevo.strip():
            # Borrar texto a pelo deja el <w:p> vacio con su numeracion viva, que
            # es la vineta huerfana de R-105. Las supresiones se resuelven a nivel
            # de parrafo, donde el parrafo entero se puede quitar.
            continue
        n = xml.count(viejo)
        if n:
            xml = xml.replace(viejo, nuevo)
            hechos[viejo] = hechos.get(viejo, 0) + n

    # 2) Lo que quede se busca a nivel de parrafo, donde el texto ya esta unido.
    pendientes = {v: n for v, n in reemplazos.items() if v not in hechos}
    if pendientes:
        piezas: list[str] = []
        fin = 0
        for m in RE_PARRAFO.finditer(xml):
            parrafo = m.group(0)
            texto = texto_parrafo(parrafo)
            nuevo_texto = texto
            tocado = False
            for viejo, nuevo in pendientes.items():
                if viejo in nuevo_texto:
                    nuevo_texto = nuevo_texto.replace(viejo, nuevo)
                    hechos[viejo] = hechos.get(viejo, 0) + 1
                    tocado = True
            if tocado:
                piezas.append(xml[fin : m.start()])
                piezas.append(reescribir_parrafo(parrafo, nuevo_texto))
                fin = m.end()
        piezas.append(xml[fin:])
        xml = "".join(piezas)

    # 3) Alineacion. Una clave copiada a mano de un volcado casi nunca coincide al
    # caracter con la plantilla: sobra un espacio, falta una tilde, se colo el
    # numero de una nota al pie. Obligar al redactor a cazar esa diferencia a ojo
    # cuesta una vuelta entera del bucle (~30 s). Si la clave se parece a UN solo
    # parrafo por encima del 92 %, se usa ese parrafo y se dice en voz alta.
    pendientes = {v: n for v, n in reemplazos.items() if v not in hechos}
    alineados: dict[str, tuple[str, float]] = {}
    if pendientes:
        parrafos = [
            (m.start(), m.end(), m.group(0), texto_parrafo(m.group(0)).strip())
            for m in RE_PARRAFO.finditer(xml)
        ]
        candidatos = [p for p in parrafos if len(p[3]) > 20]
        # Se decide todo primero y se aplica despues de atras hacia delante: si se
        # sustituyera sobre la marcha, la primera sustitucion desplazaria los
        # offsets de las siguientes y el XML acabaria partido por la mitad.
        planeados: list[tuple[int, int, str, str]] = []
        usados: set[int] = set()
        for viejo, nuevo in pendientes.items():
            if len(viejo) < 40:
                continue  # una clave corta se alinea con cualquier cosa
            mejor = None
            for ini, fin_p, parrafo, texto in candidatos:
                if ini in usados:
                    continue
                r = difflib.SequenceMatcher(None, viejo, texto).ratio()
                if r >= 0.92 and (mejor is None or r > mejor[0]):
                    mejor = (r, ini, fin_p, parrafo, texto)
            if mejor:
                r, ini, fin_p, parrafo, texto = mejor
                usados.add(ini)
                planeados.append((ini, fin_p, parrafo, nuevo))
                hechos[viejo] = hechos.get(viejo, 0) + 1
                alineados[viejo] = (texto, r)
        for ini, fin_p, parrafo, nuevo in sorted(planeados, reverse=True):
            xml = xml[:ini] + reescribir_parrafo(parrafo, nuevo) + xml[fin_p:]

    return xml, hechos, alineados


RE_NUMPR = re.compile("<w:numPr[ />]")


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


def texto_plano(datos: dict[str, bytes]) -> str:
    trozos = []
    for nombre, crudo in datos.items():
        if nombre.startswith("word/") and nombre.endswith(".xml"):
            trozos.append(re.sub(r"<[^>]+>", " ", crudo.decode("utf-8", "replace")))
    return " ".join(trozos)


MESES = (
    "enero|febrero|marzo|abril|mayo|junio|julio|agosto|"
    "setiembre|septiembre|octubre|noviembre|diciembre"
)
RE_FECHA = re.compile(r"\d{1,2} de (?:%s) de \d{4}" % MESES, re.I)
RE_MONTO = re.compile(r"(?:US\$|S/)\s?[\d][\d\s.,]{2,}\d")
RE_CIFRA = re.compile(r"\b\d{6,}\b")  # polizas, siniestros, RUC, certificados


def datos_duros(texto: str) -> set[str]:
    """Fechas, montos y numeros largos: lo que un admisorio no puede heredar."""
    duros: set[str] = set()
    for patron in (RE_FECHA, RE_MONTO, RE_CIFRA):
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
    for n in objetivo:
        xml = datos[n].decode("utf-8")
        xml, parciales, alin = aplicar(xml, reemplazos)
        if n == "word/document.xml":
            xml, huerfanas = limpiar_vinetas_huerfanas(xml)
        datos[n] = xml.encode("utf-8")
        for k, v in parciales.items():
            hechos[k] = hechos.get(k, 0) + v
        alineados.update(alin)

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
        mapa.get("conservar", []),
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
