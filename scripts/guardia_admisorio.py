#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Guardia de puerta: impide publicar material de expediente y admisorios no aptos.

Uso:
    python scripts/guardia_admisorio.py --staged        # lo que esta por commitear
    python scripts/guardia_admisorio.py --rango A..B    # lo que anade un push
    python scripts/guardia_admisorio.py <archivo> [...]

Dos prohibiciones, en este orden de gravedad:

1. **Ningun documento de expediente entra al repositorio.** Este repositorio es
   publico. Un admisorio real lleva el nombre completo del denunciante, su
   siniestro y su poliza. Publicarlo no se deshace: el historial de git queda, y
   lo que estuvo en una rama publica se considera comprometido.

2. **Ningun admisorio se commitea sin pasar el verificador** (R-109).

Codigo de salida: 0 si todo limpio, 1 si hay violacion.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# Rutas donde nunca debe aparecer un documento de trabajo real.
RUTAS_PROHIBIDAS = ("casos_de_prueba/", "casos/", "expedientes/")

# Señales de que un .docx es un expediente real y no una plantilla anonimizada.
SENALES_PERSONALES = (
    re.compile(r"\bDNI\s*(?:N\.?°|N°)?\s*\d{8}\b", re.I),
    re.compile(r"\b\d{8}\b(?=[^\d])"),  # documento de identidad suelto
    re.compile(
        r"[\w.\-]+@(?!pacifico|rimac|indecopi)[\w.\-]+\.\w+"
    ),  # correo particular
)

NOMBRE_ADMISORIO = re.compile(r"(ADMISORIO|ADM[_ -]|RES[_ ]?\d+)", re.I)

# La guardia solo miraba dentro de los .docx, y por ahi se colo lo que tenia que
# parar. El 14/09/2026 un `mapa.json` de trabajo del agente, con el nombre
# completo del denunciante y el del consumidor de la plantilla, entro al
# repositorio publico en un `git add -A`. Un `.json` o un `.txt` de trabajo lleva
# exactamente los mismos datos que el `.docx`; lo unico que cambia es que es mas
# facil de leer.
TEXTO_REVISABLE = (".json", ".txt", ".md", ".py", ".csv", ".xml", ".yaml", ".yml")

# Nombre propio completo en mayusculas: tres o mas palabras seguidas. Es la forma
# en que un admisorio nombra a las partes y a los consumidores de las plantillas.
NOMBRE_COMPLETO = re.compile(
    r"\b[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ]+(?:\s+[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ]+){2,}\b"
)

# Un nombre propio no lleva preposiciones ni sustantivos institucionales. Basta
# con que una sola palabra de la secuencia este aqui para saber que no es una
# persona: asi «BANCO DE CREDITO» o «DIRECTRICES MAESTRAS DEL SISTEMA» dejan de
# dar falso positivo sin necesidad de mantener una lista de entidades.
PALABRAS_NO_PERSONALES = {
    "DE",
    "DEL",
    "LA",
    "EL",
    "LOS",
    "LAS",
    "Y",
    "O",
    "EN",
    "AL",
    "POR",
    "PARA",
    "CON",
    "SIN",
    "SOBRE",
    "SEGUN",
    "SEGÚN",
    "BANCO",
    "SEGUROS",
    "SEGURO",
    "COMPANIA",
    "COMPAÑIA",
    "COMPAÑÍA",
    "REASEGUROS",
    "COMISION",
    "COMISIÓN",
    "PROTECCION",
    "PROTECCIÓN",
    "CONSUMIDOR",
    "INDECOPI",
    "INSTITUTO",
    "NACIONAL",
    "DEFENSA",
    "COMPETENCIA",
    "PROPIEDAD",
    "INTELECTUAL",
    "CODIGO",
    "CÓDIGO",
    "TEXTO",
    "UNICO",
    "ÚNICO",
    "ORDENADO",
    "LEY",
    "DECRETO",
    "SUPREMO",
    "LEGISLATIVO",
    "RESOLUCION",
    "RESOLUCIÓN",
    "EXPEDIENTE",
    "SISTEMA",
    "GUARDIA",
    "PUERTA",
    "DIRECTRICES",
    "MAESTRAS",
    "MAESTRO",
    "PLANTILLA",
    "SECRETARIA",
    "SECRETARÍA",
    "TECNICA",
    "TÉCNICA",
    "ADMISORIO",
    "DENUNCIA",
    "CASILLA",
    "ELECTRONICA",
    "ELECTRÓNICA",
    "CORREO",
    "DOMICILIO",
    "PROCESAL",
    "POLIZA",
    "PÓLIZA",
    "CERTIFICADO",
    "SINIESTRO",
    "COBERTURA",
    "PRIMERO",
    "SEGUNDO",
    "TERCERO",
    "CUARTO",
    "QUINTO",
    "SEXTO",
    "SEPTIMO",
    "SÉPTIMO",
    "OCTAVO",
    "NOVENO",
    "DECIMO",
    "DÉCIMO",
    "HECHOS",
    "MATERIAS",
    "DENUNCIANTE",
    "DENUNCIADO",
    "LIMA",
    "PERU",
    "PERÚ",
    "SAC",
    "SAA",
    "SA",
}

# Firmas institucionales: son cargos publicos, no datos de un consumidor.
NOMBRES_INSTITUCIONALES = (
    "LUISA ANALI SILVA MALPARTIDA",
    "EVELING ROA QUISPE",
    "MARIA GRACIELA REJAS JIMENEZ",
    "MARÍA GRACIELA REJAS JIMÉNEZ",
)


_TRACKED: set[str] | None = None


def ya_rastreado(norm: str) -> bool:
    """Si el archivo ya estaba en el repositorio, alguien lo reviso en su dia."""
    global _TRACKED
    if _TRACKED is None:
        salida = subprocess.run(
            ["git", "ls-files"], capture_output=True, cwd=RAIZ
        ).stdout.decode("utf-8", "replace")
        _TRACKED = {ln.strip() for ln in salida.splitlines() if ln.strip()}
    return norm in _TRACKED


def revisar_texto(ruta: Path, norm: str) -> list[str]:
    """Busca datos personales en un archivo de texto de trabajo."""
    try:
        contenido = ruta.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    violaciones = []
    for patron in SENALES_PERSONALES:
        if patron.search(contenido):
            return [
                "FUGA: '%s' contiene datos personales identificables (%s). "
                "Los archivos de trabajo del agente no entran al repositorio."
                % (norm, patron.pattern[:34])
            ]

    # La busqueda de nombres propios en prosa libre no sabe distinguir «SOLO ESTE
    # ARCHIVO» de «PABLO SANTIAGO ESPINOZA CANAL», asi que se limita a los
    # archivos que **entran nuevos** al repositorio, que es donde ocurrio la fuga.
    # Lo ya rastreado se reviso en su momento y no se vuelve a poner en duda.
    if ya_rastreado(norm):
        return violaciones

    for m in NOMBRE_COMPLETO.finditer(contenido):
        nombre = m.group(0)
        if any(p in PALABRAS_NO_PERSONALES for p in nombre.split()):
            continue
        if any(inst in nombre or nombre in inst for inst in NOMBRES_INSTITUCIONALES):
            continue
        violaciones.append(
            "FUGA: '%s' nombra a una persona ('%s'). Los mapas, volcados y "
            "borradores de trabajo se quedan fuera del repositorio." % (norm, nombre)
        )
        break
    return violaciones


def texto_docx(ruta: Path) -> str:
    try:
        crudo = (
            zipfile.ZipFile(ruta).read("word/document.xml").decode("utf-8", "replace")
        )
    except Exception:
        return ""
    return re.sub(r"<[^>]+>", " ", crudo)


def archivos_staged() -> list[str]:
    salida = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"],
        capture_output=True,
        cwd=RAIZ,
    ).stdout.decode("utf-8", "replace")
    return [l.strip() for l in salida.splitlines() if l.strip()]


def archivos_rango(rango: str) -> list[str]:
    salida = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=AM", rango],
        capture_output=True,
        cwd=RAIZ,
    ).stdout.decode("utf-8", "replace")
    return [l.strip() for l in salida.splitlines() if l.strip()]


def revisar(rutas: list[str]) -> list[str]:
    violaciones: list[str] = []
    for rel in rutas:
        ruta = RAIZ / rel
        norm = rel.replace("\\", "/")

        if norm.startswith(RUTAS_PROHIBIDAS) and ruta.suffix.lower() in (
            ".docx",
            ".pdf",
            ".doc",
        ):
            violaciones.append(
                "FUGA: '%s' es material de expediente en una ruta de trabajo. "
                "Este repositorio es publico y el historial no se borra." % norm
            )
            continue

        if ruta.suffix.lower() in TEXTO_REVISABLE and ruta.exists():
            # Las plantillas y la documentacion del propio sistema quedan fuera:
            # sus ejemplos ya estan anonimizados y se revisan a mano.
            if not norm.startswith(("plantillas_maestras/", "modelos/", "docs/")):
                violaciones.extend(revisar_texto(ruta, norm))
            continue

        if ruta.suffix.lower() != ".docx" or not ruta.exists():
            continue
        if "plantillas_maestras/" in norm or "modelos/" in norm:
            continue

        texto = texto_docx(ruta)
        if not texto:
            continue

        for patron in SENALES_PERSONALES:
            if patron.search(texto):
                violaciones.append(
                    "FUGA: '%s' contiene datos personales identificables (%s). "
                    "Anonimiza o mantenlo fuera del repositorio."
                    % (norm, patron.pattern[:34])
                )
                break

        if NOMBRE_ADMISORIO.search(ruta.name):
            codigo = subprocess.run(
                [
                    sys.executable,
                    str(RAIZ / "scripts" / "verificar_admisorio.py"),
                    str(ruta),
                ],
                capture_output=True,
                cwd=RAIZ,
            )
            if codigo.returncode != 0:
                violaciones.append(
                    "NO APTO: '%s' no pasa verificar_admisorio.py (R-109). "
                    "Corrigelo antes de commitear." % norm
                )
    return violaciones


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("archivos", nargs="*")
    ap.add_argument("--staged", action="store_true")
    ap.add_argument("--rango", help="Rango git, p. ej. origin/main..HEAD")
    args = ap.parse_args(argv[1:])

    if args.staged:
        rutas = archivos_staged()
    elif args.rango:
        rutas = archivos_rango(args.rango)
    else:
        rutas = args.archivos
    if not rutas:
        print("guardia: nada que revisar.")
        return 0

    violaciones = revisar(rutas)
    if not violaciones:
        print("guardia: %d archivo(s) revisado(s), sin violaciones." % len(rutas))
        return 0

    print("=" * 78)
    print(
        "GUARDIA DE PUERTA: %d VIOLACION(ES). LA OPERACION SE DETIENE."
        % len(violaciones)
    )
    print("=" * 78)
    for v in violaciones:
        print("  - %s" % v)
    print()
    print("  Si de verdad hace falta saltarse esto, es una decision del instructor,")
    print("  no del agente: git commit --no-verify, y se explica por que.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
