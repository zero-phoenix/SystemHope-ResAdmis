#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contrasta un admisorio contra SU expediente: todo dato tiene que estar anclado.

`verificar_admisorio.py` comprueba la **forma** (firma, negritas, espejos, modo
verbal). `construir_admisorio.py` comprueba que no sobreviva nada de la plantilla.
Faltaba lo tercero y es lo que de verdad importa: que cada dato del admisorio
**exista en el expediente**.

Una fecha, un monto, una poliza o un numero de siniestro que no aparezca en
ninguna pagina del expediente es informacion inventada, y ninguna de las otras dos
comprobaciones lo ve: la forma es correcta y el dato no viene de la plantilla,
viene de la nada.

Contrasta cuatro cosas contra la carpeta del expediente:

1. **Datos duros.** Cada fecha, monto y cifra larga del admisorio se busca en el
   texto del expediente. Lo que no aparezca se declara sin ancla.
2. **Partes y via.** Las partes del admisorio y su via de notificacion tienen que
   ser exactamente las de la cedula (R-138), una via por parte.
3. **Ordinal.** El numero de resolucion es el que fija la cedula (R-129).
4. **Nombre del entregable.** `ADM <EXPEDIENTE> R<N>.docx` (mandato 14/09/2026).

Uso:
    python scripts/auditar_admisorio.py <carpeta_del_expediente>
    python scripts/auditar_admisorio.py <carpeta> --ver-anclados
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import extraer_expediente as EX  # noqa: E402
import preparar_remesa as PR  # noqa: E402

MESES = (
    "enero|febrero|marzo|abril|mayo|junio|julio|agosto|"
    "setiembre|septiembre|octubre|noviembre|diciembre"
)
RE_FECHA = re.compile(r"\d{1,2}\s+de\s+(?:%s)\s+de\s+\d{4}" % MESES, re.I)
RE_MONTO = re.compile(r"(?:US\$|S/)\s?\d[\d\s.,]*\d")
RE_CIFRA = re.compile(r"\b\d{5,}\b")

# Datos que son del procedimiento o de la norma citada, no del expediente: no
# necesitan ancla. Sin esta lista, las fechas de publicacion de las leyes que todo
# admisorio cita en sus notas al pie se declaran inventadas y ahogan los hallazgos
# de verdad. Medido: 8 de los 12 «sin ancla» del Exp. 3122-2026 eran normativos.
import config_sistema  # noqa: E402

FECHAS_PROPIAS = tuple(f for f in (
    config_sistema.fecha_emision(),  # fecha de emision de la remesa (D2, config/remesa.json)
    "2 de setiembre de 2010",    # publicacion de la Ley 29571
    "2 de julio de 2013",        # publicacion de la Ley 30056
    "30 de abril de 2026",       # publicacion del D.S. 006-2026-JUS
    "18 de abril de 1996",       # Decreto Legislativo 807
) if f)
CIFRAS_PROPIAS = (
    "29571",   # Codigo de Proteccion y Defensa del Consumidor
    "30056",   # Ley de impulso al desarrollo productivo
    "20101",   # Ley del contrato de seguro
    "006-2026",  # TUO de la LPAG
    "00807", "807",  # Decreto Legislativo 807
    "27444",   # LPAG
)


def sin_tildes(t: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn"
    )


def normalizar(t: str) -> str:
    """Un numero puede escribirse S/ 28 049,00 o S/28,049.00 y ser el mismo."""
    return re.sub(r"[\s.,]", "", sin_tildes(t).lower())


def texto_docx(ruta: Path) -> str:
    with zipfile.ZipFile(ruta) as z:
        partes = [
            z.read(n).decode("utf-8", "replace")
            for n in z.namelist()
            if n.startswith("word/") and n.endswith(".xml")
        ]
    plano = re.sub(r"<[^>]+>", " ", " ".join(partes))
    return re.sub(r"\s+", " ", plano)


def texto_expediente(carpeta: Path) -> str:
    volcado = carpeta / "_texto_expediente.txt"
    if volcado.exists():
        fuente = volcado.read_text(encoding="utf-8", errors="replace")
    else:
        fuente = "\n".join(
            "\n".join(EX.paginas_de_pdf(p)) for p in sorted(carpeta.glob("*.pdf"))
        )
    # En paginas escaneadas los datos duros solo existen en la imagen; la
    # constancia de la lectura con Lens (_LECTURA.md, R-137) es la que los
    # registra. Sin ella como fuente, todo dato verdadero de una pagina sin capa
    # de texto seria un falso «sin ancla» (mismo defecto de raiz que R-136
    # corrigio en el triaje). La fidelidad de la constancia la garantiza la
    # relectura del supervisor.
    lectura = carpeta / "_LECTURA.md"
    if lectura.exists():
        fuente += "\n" + lectura.read_text(encoding="utf-8", errors="replace")
    return fuente


def datos_duros(texto: str) -> list[tuple[str, str]]:
    salida = []
    for etiqueta, patron in (
        ("fecha", RE_FECHA),
        ("monto", RE_MONTO),
        ("cifra", RE_CIFRA),
    ):
        for m in patron.finditer(texto):
            salida.append((etiqueta, re.sub(r"\s+", " ", m.group(0)).strip()))
    return salida


def auditar(carpeta: Path, ver_anclados: bool) -> int:
    carpeta = carpeta.resolve()
    fallos: list[str] = []

    cedulas = sorted(carpeta.glob("ADM*CEDULAS*.docx"))
    if not cedulas:
        print("No hay cedula en %s: sin ella no hay contra que contrastar." % carpeta)
        return 2
    resolucion, partes = PR.censo_cedula(cedulas[0])

    esperado = "ADM %s R%s.docx" % (carpeta.name, resolucion)
    entregables = [
        p for p in carpeta.glob("ADM*.docx") if "CEDULAS" not in p.name.upper()
    ]
    if not entregables:
        print("Todavia no hay entregable en %s." % carpeta)
        return 2
    doc = entregables[0]

    print("=" * 78)
    print("AUDITORIA DE FONDO  %s" % doc.name)
    print("=" * 78)

    if doc.name != esperado:
        fallos.append(
            "el entregable se llama '%s' y debe llamarse '%s'" % (doc.name, esperado)
        )

    cuerpo = texto_docx(doc)
    fuente = texto_expediente(carpeta)
    fuente_norm = normalizar(fuente)

    # 1. Ordinal
    m = re.search(r"RESOLUCI[OÓ]N\s*:?\s*(\d+)", cuerpo, re.I)
    ordinal = m.group(1) if m else ""
    if resolucion and ordinal and ordinal != resolucion:
        fallos.append(
            "el admisorio dice Resolucion %s y la cedula fija la %s (R-129)"
            % (ordinal, resolucion)
        )
    print("  Resolucion: admisorio=%s  cedula=%s" % (ordinal or "?", resolucion or "?"))

    # 2. Partes y via
    print("  Partes segun la cedula:")
    for nombre, via, _canal in partes:
        apellidos = [w for w in sin_tildes(nombre).upper().split() if len(w) > 2]
        presente = any(a in sin_tildes(cuerpo).upper() for a in apellidos)
        marca = "OK  " if presente else "AUSENTE"
        if not presente:
            fallos.append(
                "la parte '%s' de la cedula no aparece en el admisorio" % nombre
            )
        print("     %-8s %-46s %s" % (marca, nombre[:46], via))

    # 3. Nombres de persona ajenos al caso.
    #
    # El auditor de residuos del constructor vigila aseguradoras y datos duros,
    # pero no apellidos, y por ahi se cuela lo peor: el Exp. 3122-2026 salio
    # certificado APTO nombrando a «Pablo Santiago Cornejo Canal», una quimera del
    # consumidor de la plantilla (Espinoza Canal) y del de este caso (Cornejo); y
    # el 2820-2026 atribuia la denuncia a «el senor Nanez», que no existe en el
    # expediente. Un apellido que no es de ninguna parte procesal ni consta en el
    # expediente es residuo de plantilla con forma de dato verdadero.
    print("  Nombres de persona:")
    autorizados = set()
    for nombre, _via, _canal in partes:
        autorizados.update(w for w in sin_tildes(nombre).upper().split() if len(w) > 2)
    autorizados.update(
        "LUISA ANALI SILVA MALPARTIDA COMISION PROTECCION CONSUMIDOR INDECOPI "
        "SECRETARIA TECNICA SUCESION INTESTADA SENOR SENORA".split()
    )
    fuente_alto = sin_tildes(fuente).upper()
    tratamiento = re.compile(
        r"(?:señor|señora|señorita)\s+([A-ZÁÉÍÓÚÑ][\wáéíóúñ]+)",
        re.I,
    )
    ajenos = []
    for m in tratamiento.finditer(cuerpo):
        apellido = sin_tildes(m.group(1)).upper()
        if apellido in autorizados or apellido in fuente_alto:
            continue
        if apellido not in [a for a, _ in ajenos]:
            ajenos.append((apellido, m.group(0)))
    if not ajenos:
        print("     OK     ningun apellido ajeno al caso.")
    for apellido, frase in ajenos:
        fallos.append(
            "el admisorio nombra a '%s' ('%s'), que no es parte procesal ni consta "
            "en el expediente: es residuo de plantilla" % (apellido.title(), frase)
        )
        print("     AJENO  %s" % frase)

    # 4. Datos duros sin ancla
    duros = datos_duros(cuerpo)
    sin_ancla: list[tuple[str, str]] = []
    anclados = 0
    for etiqueta, valor in duros:
        if any(p in valor for p in FECHAS_PROPIAS + CIFRAS_PROPIAS):
            continue
        if normalizar(valor) and normalizar(valor) in fuente_norm:
            anclados += 1
            if ver_anclados:
                print("     ancla  %-8s %s" % (etiqueta, valor))
            continue
        sin_ancla.append((etiqueta, valor))

    print()
    print(
        "  Datos duros del admisorio: %d anclados, %d sin ancla"
        % (anclados, len(sin_ancla))
    )
    vistos: set[str] = set()
    for etiqueta, valor in sin_ancla:
        if valor in vistos:
            continue
        vistos.add(valor)
        n = sum(1 for _e, v in sin_ancla if v == valor)
        fallos.append(
            "%s '%s' no aparece en ninguna pagina del expediente%s"
            % (etiqueta, valor, " (x%d)" % n if n > 1 else "")
        )

    print()
    print("VEREDICTO DE FONDO")
    print("-" * 78)
    if not fallos:
        print("  Sin dato sin ancla. Todo lo que afirma el admisorio consta en el")
        print("  expediente o es del propio procedimiento.")
        return 0
    for f in fallos:
        print("  FALLA  %s" % f)
    print()
    print("  Un dato que no consta en el expediente es informacion inventada, por")
    print("  correcta que sea la forma del documento.")
    return 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("carpeta")
    ap.add_argument("--ver-anclados", action="store_true")
    args = ap.parse_args(argv[1:])
    return auditar(Path(args.carpeta), args.ver_anclados)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
