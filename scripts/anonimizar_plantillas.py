#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quita de las plantillas maestras los datos del consumidor que las origino.

Motivo, medido el 15/09/2026 sobre una muestra de 40 de las 605 plantillas
publicadas: **39 llevaban el apellido de un consumidor real**. Las plantillas son
admisorios reales despersonalizados solo a medias, y estan en un repositorio
publico. Es la fuga mas grande del sistema y estaba dentro justo de lo que se
queria conservar.

Anonimizar no las degrada: las **mejora como plantillas**. Un modelo cuyo texto
dice «el senor Espinoza» invita a un reemplazo a ciegas --y de ahi salieron los
apellidos quimera tipo «Pablo Santiago Cornejo Canal»--. Un modelo que dice
«el senor [APELLIDO]» obliga a rellenar desde la cedula, que es la fuente correcta.

Que sustituye:
  - el nombre completo del denunciante que declara el encabezado -> [DENUNCIANTE]
  - cada apellido suyo, alli donde aparezca                      -> [APELLIDO]
  - «el senor X» / «la senora X» de cualquier otro apellido      -> [APELLIDO]
  - numeros de DNI de ocho digitos                               -> [DNI]
  - correos particulares (no institucionales)                    -> [CORREO]

Que NO toca: razones sociales, numeros de poliza, fechas, montos y articulos. Una
plantilla sin sus hechos no sirve de plantilla.

Uso:
    python scripts/anonimizar_plantillas.py                # simulacion
    python scripts/anonimizar_plantillas.py --aplicar
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

from construir_admisorio import (  # noqa: E402
    RE_PARRAFO,
    reescribir_parrafo,
    sin_tildes,
    texto_parrafo,
)

PLANTILLAS = RAIZ / "plantillas_maestras"

RE_DENUNCIANTE = re.compile(r"DENUNCIANTE\s*:?\s*(.{4,90}?)(?:\(|$)", re.I)
RE_TRATAMIENTO = re.compile(
    "(señor|señora|señorita|señores|señoras"
    "|Señor|Señora|Señores|Señoras|SEÑOR|SEÑORA|SEÑORES|SEÑORAS)"
    "\s+((?:[A-ZÁÉÍÓÚÑ][\wáéíóúñ]{2,}\s*){1,4})"
)
RE_DNI = re.compile(r"(DNI\s*(?:N\.?[°º]|N[°º]|No\.?)?\s*)\d{8}\b", re.I)
RE_CORREO = re.compile(
    r"[\w.\-]+@(?!pacifico|rimac|indecopi|vivirseguros)[\w.\-]+\.\w+", re.I
)

# Palabras que siguen a «senor/senora» sin ser un apellido.
NO_APELLIDO = {
    "PRESIDENTE",
    "VOCAL",
    "MIEMBRO",
    "COMISIONADO",
    "SECRETARIO",
    "SECRETARIA",
    "JUEZ",
    "DE",
    "DEL",
    "LA",
    "EL",
    "APELLIDO",
    "DENUNCIANTE",
}


RE_PARTICULA = re.compile(
    "(señor|señora|señorita|Señor|Señora|SEÑOR|SEÑORA)"
    "(\\s+)(?:De la|De los|De las|Del|De|DEL|DE LA)\\s+"
    "[A-Za-zÀ-ÿ]{3,}"
)


def anonimizar_texto(texto: str, nombres: set[str]) -> tuple[str, int]:
    cambios = 0

    # El nombre completo aparece en el encabezado en mayusculas y en la resolutiva
    # en capitalizacion normal. Sustituir solo la forma del encabezado dejaba
    # medio nombre dentro: «el senor [APELLIDO] Santiago Espinoza Canal».
    for nombre in sorted(nombres, key=len, reverse=True):
        if not nombre:
            continue
        patron = re.compile(re.escape(nombre), re.I)
        texto, n = patron.subn("[DENUNCIANTE]", texto)
        cambios += n

    # Y cada palabra suelta de ese nombre, alla donde quede.
    piezas_nombre = {
        w
        for nombre in nombres
        for w in nombre.split()
        if len(w) > 2 and sin_tildes(w).upper() not in NO_APELLIDO
    }
    for palabra in sorted(piezas_nombre, key=len, reverse=True):
        limite = chr(92) + "b"  # asi a proposito: el escape literal ya se
        # colapso tres veces en este repositorio y dejo un retroceso (R-141)
        patron = re.compile(limite + re.escape(palabra) + limite, re.I)
        texto, n = patron.subn("[APELLIDO]", texto)
        cambios += n
    # Dos o mas marcadores seguidos son el mismo nombre partido: se colapsan.
    texto = re.sub(r"(\[APELLIDO\]\s*){2,}", "[APELLIDO] ", texto)

    # Apellido compuesto: «el senor Del Aguila». La particula va en mayuscula,
    # lo que lo distingue de «el senor de la casa», que no es un nombre.
    texto, n = RE_PARTICULA.subn(lambda m: m.group(1) + m.group(2) + "[APELLIDO]", texto)
    cambios += n

    def _trato(m: re.Match) -> str:
        nonlocal cambios
        bloque = m.group(2).strip()
        apellido = sin_tildes(bloque.split()[0]).upper()
        if apellido in NO_APELLIDO or apellido.startswith("["):
            return m.group(0)
        cambios += 1
        return "%s [APELLIDO] " % m.group(1)

    texto = RE_TRATAMIENTO.sub(_trato, texto)

    # Codenunciantes: «los senores X y Z». La regla de tratamiento solo alcanza
    # al primero; el segundo va detras de la conjuncion y hay que ir a por el.
    texto, n = re.subn(
        "\[APELLIDO\]\s*y\s+(?:[A-ZÁÉÍÓÚÑ][\wáéíóúñ]{2,}\s*){1,4}",
        "[APELLIDO] y [APELLIDO] ",
        texto,
    )
    cambios += n
    texto = re.sub("\s{2,}", " ", texto)

    texto, n = RE_DNI.subn(lambda m: m.group(1) + "[DNI]", texto)
    cambios += n
    # Apellidos compuestos: «Del Aguila» deja «Del [APELLIDO]» porque la
    # particula no es un identificador por si sola. Se colapsa para no dejar
    # media forma de tratamiento colgando.
    texto, n = re.subn(
        r"(?:De la|De los|De las|Del|De|Los|Las)\s+\[APELLIDO\]",
        "[APELLIDO]",
        texto,
        flags=re.I,
    )
    cambios += n
    texto, n = RE_CORREO.subn("[CORREO]", texto)
    cambios += n
    return texto, cambios


def nombres_del_encabezado(parrafos: list[str]) -> set[str]:
    """El nombre completo que declara la linea DENUNCIANTE, y sus apellidos."""
    nombres: set[str] = set()
    for t in parrafos[:14]:
        m = RE_DENUNCIANTE.search(t)
        if not m:
            continue
        completo = m.group(1).strip(" \t:-")
        if len(completo.split()) >= 2 and completo.upper() == completo:
            nombres.add(completo)
    return nombres


def procesar(ruta: Path, aplicar: bool) -> tuple[int, int]:
    with zipfile.ZipFile(ruta) as z:
        nombres_zip = z.namelist()
        datos = {n: z.read(n) for n in nombres_zip}

    objetivo = [
        n
        for n in nombres_zip
        if n in ("word/document.xml", "word/footnotes.xml")
        or re.match(r"word/(header|footer)\d+\.xml", n)
    ]
    total = 0
    tocados = 0
    for n in objetivo:
        xml = datos[n].decode("utf-8")
        parrafos = [texto_parrafo(m.group(0)) for m in RE_PARRAFO.finditer(xml)]
        nombres = (
            nombres_del_encabezado(parrafos) if n == "word/document.xml" else set()
        )

        piezas: list[str] = []
        fin = 0
        for m in RE_PARRAFO.finditer(xml):
            parrafo = m.group(0)
            texto = texto_parrafo(parrafo)
            if not texto.strip():
                continue
            nuevo, cambios = anonimizar_texto(texto, nombres)
            if cambios:
                piezas.append(xml[fin : m.start()])
                piezas.append(reescribir_parrafo(parrafo, nuevo))
                fin = m.end()
                total += cambios
        if fin:
            piezas.append(xml[fin:])
            datos[n] = "".join(piezas).encode("utf-8")
            tocados += 1

    if aplicar and total:
        with zipfile.ZipFile(ruta, "w", zipfile.ZIP_DEFLATED) as z:
            for n in nombres_zip:
                z.writestr(n, datos[n])
    return total, tocados


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--limite", type=int, default=0, help="Procesa solo N plantillas")
    args = ap.parse_args(argv[1:])

    rutas = sorted(PLANTILLAS.rglob("*.docx"))
    if args.limite:
        rutas = rutas[: args.limite]

    print("=" * 78)
    print(
        "ANONIMIZACION DE PLANTILLAS  (%s)  %d archivos"
        % ("APLICANDO" if args.aplicar else "SIMULACION", len(rutas))
    )
    print("=" * 78)

    con_datos = 0
    total = 0
    for ruta in rutas:
        try:
            cambios, _tocados = procesar(ruta, args.aplicar)
        except Exception as exc:
            print("  ERROR  %s: %s" % (ruta.name[:60], exc))
            continue
        if cambios:
            con_datos += 1
            total += cambios
    print()
    print("  Plantillas con datos personales: %d de %d" % (con_datos, len(rutas)))
    print("  Sustituciones: %d" % total)
    if not args.aplicar:
        print("  Simulacion: no se escribio nada. Repite con --aplicar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
