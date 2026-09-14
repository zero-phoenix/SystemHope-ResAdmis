#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Edita las cedulas de notificacion de una remesa y levanta su censo.

Mandato del instructor (14/09/2026):
  - todas las cedulas llevan `Lima, 14 de setiembre de 2026`;
  - ninguna firma EVELING ROA QUISPE: todas firman LUISA ANALI SILVA MALPARTIDA
    con el cargo `Secretaria Tecnica (e)`.

Ademas, la cedula es la **fuente de verdad** de dos datos del admisorio (R-129):
el **numero de resolucion** y la **via de notificacion de cada parte**, que es
una sola por parte: Casilla Electronica, correo electronico o domicilio fisico.
Por eso el script no solo edita: deja un `_CEDULA.md` por expediente con el censo
anclado, que es lo que despues consume el `_ORDEN_DE_TRABAJO.md` del caso.

No abre Word: reescribe el OOXML. Las fechas y el nombre estan contiguos en el
XML y se sustituyen literalmente; el cargo esta partido en varios `run` con el
mismo formato, asi que ese parrafo se reescribe entero sobre el primer `run`.

Uso:
    python scripts/editar_cedulas.py <carpeta-remesa>            # simulacion
    python scripts/editar_cedulas.py <carpeta-remesa> --aplicar
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

FECHA_MANDATO = "14 de setiembre de 2026"
FIRMA_NUEVA = "LUISA ANALI SILVA MALPARTIDA"
FIRMA_VIEJA = "EVELING ROA QUISPE"
CARGO_NUEVO = "Secretaria Técnica (e)"

MESES = (
    "enero|febrero|marzo|abril|mayo|junio|julio|agosto|"
    "setiembre|septiembre|octubre|noviembre|diciembre"
)
RE_FECHA = re.compile(r"\d{1,2} de (?:%s) de \d{4}" % MESES, re.I)
RE_PARRAFO = re.compile(r"<w:p\b[^>]*>.*?</w:p>", re.S)
RE_TEXTO = re.compile(r"(<w:t(?:\s[^>]*)?>)(.*?)(</w:t>)", re.S)
# Ojo: `<w:t[^>]*>` tambien captura `<w:tab>` y `<w:tabs>`, y entonces el "texto"
# del parrafo se llena de XML crudo. Costo medido: 14 reemplazos del Exp. 3122-2026
# declarados inexistentes cuando si estaban.
RE_CARGO = re.compile(r"^secretar[ií]a? t[eé]cnica\s*$", re.I)
# La cedula escribe el ordinal con la ordinal masculina (Nº), no con el
# simbolo de grado (N°). Se aceptan ambos, y tambien 'N.' o 'N' a secas.
RE_RESOLUCION = re.compile(r"Resolución\s+N[°º.⁰]?\s*(\d+)", re.I)

VIAS = (
    ("CASILLA-E", "casilla electronica"),
    ("CORREO-E", "correo electronico"),
)


def texto_parrafo(parrafo: str) -> str:
    return "".join(m.group(2) for m in RE_TEXTO.finditer(parrafo))


def reescribir_parrafo(parrafo: str, nuevo: str) -> str:
    """Deja todo el texto en el primer run y vacia los demas.

    Solo se usa en el parrafo del cargo, donde los cuatro runs comparten
    exactamente el mismo `rPr`: colapsarlos es indistinguible a la vista.
    """
    visto = {"primero": True}

    def _sub(m: re.Match) -> str:
        if visto["primero"]:
            visto["primero"] = False
            return '<w:t xml:space="preserve">%s</w:t>' % nuevo
        return m.group(1) + "" + m.group(3)

    return RE_TEXTO.sub(_sub, parrafo)


def editar_xml(xml: str) -> tuple[str, dict[str, int]]:
    cuenta = {"fechas": 0, "firma": 0, "cargo": 0}

    xml, cuenta["fechas"] = RE_FECHA.subn(FECHA_MANDATO, xml)
    xml, cuenta["firma"] = re.subn(re.escape(FIRMA_VIEJA), FIRMA_NUEVA, xml)

    piezas: list[str] = []
    fin = 0
    for m in RE_PARRAFO.finditer(xml):
        parrafo = m.group(0)
        if RE_CARGO.match(texto_parrafo(parrafo).strip()):
            piezas.append(xml[fin : m.start()])
            piezas.append(reescribir_parrafo(parrafo, CARGO_NUEVO))
            fin = m.end()
            cuenta["cargo"] += 1
    piezas.append(xml[fin:])
    return "".join(piezas), cuenta


def censo(xml: str) -> tuple[str, list[tuple[str, str, str]]]:
    texto = re.sub(r"</w:p>", "\n", xml)
    texto = re.sub(r"<[^>]+>", "", texto)
    lineas = [ln.strip() for ln in texto.split("\n")]

    resolucion = ""
    m = RE_RESOLUCION.search(texto)
    if m:
        resolucion = m.group(1)

    partes: list[tuple[str, str, str]] = []
    for i, ln in enumerate(lineas):
        if not ln.startswith("Señor(es)"):
            continue
        nombre = lineas[i + 1] if i + 1 < len(lineas) else ""
        canal = lineas[i + 2] if i + 2 < len(lineas) else ""
        via = "domicilio fisico"
        for marca, etiqueta in VIAS:
            if canal.upper().startswith(marca):
                via = etiqueta
                break
        if via == "domicilio fisico":
            # el domicilio ocupa dos lineas: calle y distrito
            canal = "%s %s" % (canal, lineas[i + 3] if i + 3 < len(lineas) else "")
        partes.append((nombre, via, canal.strip()))
    return resolucion, partes


def ficha(carpeta: Path, cedula: Path, resolucion: str, partes, cuenta) -> str:
    filas = "\n".join(
        "| %s | **%s** | %s |" % (n, v, c.replace("|", "/")) for n, v, c in partes
    )
    return f"""# Cédula del Expediente {carpeta.name} — censo anclado

> Generado por `scripts/editar_cedulas.py` el {datetime.now():%d/%m/%Y %H:%M}.
> Archivo fuente: `{cedula.name}`.
> **La cédula manda** sobre la plantilla en número de resolución, partes
> procesales y vía de notificación (R-129).

## Número de resolución

**Resolución N° {resolucion or "(no declarado en la cédula)"}** — el admisorio de
este expediente se emite con ese ordinal, no con otro.

## Partes y vía de notificación (una sola vía por parte)

| Parte | Vía | Canal literal de la cédula |
|---|---|---|
{filas}

## Fecha y firma (mandato del instructor)

- `Lima, {FECHA_MANDATO}` — {cuenta['fechas']} fecha(s) sustituida(s).
- `{FIRMA_NUEVA}` / `{CARGO_NUEVO}` — {cuenta['firma']} firma(s) y
  {cuenta['cargo']} cargo(s) sustituido(s). Ninguna cédula firma {FIRMA_VIEJA}.

## Prohibido

Este archivo y la cédula contienen datos personales: **no se commitean**
(`guardia_admisorio.py` lo bloquea). El entregable es `.docx`, nunca PDF.
"""


def procesar(base: Path, aplicar: bool, respaldo: Path | None) -> int:
    carpetas = sorted(p for p in base.iterdir() if p.is_dir())
    if not carpetas:
        print("No hay carpetas de expediente en %s" % base)
        return 1

    print("=" * 78)
    print(
        "CEDULAS DE LA REMESA  %s   (%s)"
        % (base, "APLICANDO" if aplicar else "SIMULACION")
    )
    print("=" * 78)

    problemas = 0
    for carpeta in carpetas:
        cedulas = sorted(carpeta.glob("ADM*CEDULAS*.docx"))
        if not cedulas:
            print("  %-11s SIN CEDULA" % carpeta.name)
            problemas += 1
            continue
        cedula = cedulas[0]

        with zipfile.ZipFile(cedula) as z:
            nombres = z.namelist()
            datos = {n: z.read(n) for n in nombres}
        xml = datos["word/document.xml"].decode("utf-8")

        nuevo, cuenta = editar_xml(xml)
        resolucion, partes = censo(nuevo)

        if aplicar:
            if respaldo:
                respaldo.mkdir(parents=True, exist_ok=True)
                shutil.copy2(
                    cedula, respaldo / ("%s__%s" % (carpeta.name, cedula.name))
                )
            datos["word/document.xml"] = nuevo.encode("utf-8")
            with zipfile.ZipFile(cedula, "w", zipfile.ZIP_DEFLATED) as z:
                for n in nombres:
                    z.writestr(n, datos[n])
            (carpeta / "_CEDULA.md").write_text(
                ficha(carpeta, cedula, resolucion, partes, cuenta), encoding="utf-8"
            )

        estado = "OK"
        if (
            FIRMA_VIEJA in nuevo
            or RE_FECHA.search(nuevo)
            and FECHA_MANDATO not in nuevo
        ):
            estado = "REVISAR"
            problemas += 1
        print(
            "  %-11s R%s  fechas=%d firma=%d cargo=%d  partes=%d  %s"
            % (
                carpeta.name,
                resolucion or "?",
                cuenta["fechas"],
                cuenta["firma"],
                cuenta["cargo"],
                len(partes),
                estado,
            )
        )
        for n, v, c in partes:
            print("       -> %-46s %-20s %s" % (n[:46], v, c[:46]))

    print()
    print("  %d expediente(s). %d con observacion." % (len(carpetas), problemas))
    if not aplicar:
        print("  Simulacion: no se escribio nada. Repite con --aplicar.")
    return 1 if problemas else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("base", help="Carpeta que contiene una subcarpeta por expediente")
    ap.add_argument("--aplicar", action="store_true", help="Escribe los cambios")
    ap.add_argument("--respaldo", help="Carpeta donde copiar las cedulas originales")
    args = ap.parse_args(argv[1:])
    respaldo = Path(args.respaldo) if args.respaldo else None
    return procesar(Path(args.base), args.aplicar, respaldo)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
