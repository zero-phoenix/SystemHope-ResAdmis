#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprueba que el verificador rechaza lo que debe rechazar.

Una regla que nunca falla no es una regla que se cumple: es una regla que no se
esta ejecutando. R-110 estuvo exactamente asi --sus cinco patrones tenian un
caracter de retroceso donde debia ir un limite de palabra-- declarando `OK` sobre
todos los documentos sin comprobar nada, hasta que se leyeron sus bytes.

Esta prueba toma una plantilla buena, le rompe la firma a proposito y exige que el
verificador la rechace. Si la aprueba, el verificador miente y CI se detiene.

Uso:
    python scripts/prueba_verificador.py
"""

from __future__ import annotations

import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import verificar_admisorio as V  # noqa: E402

FIRMA = "LUISA ANALI SILVA MALPARTIDA"


def main() -> int:
    plantillas = sorted((RAIZ / "plantillas_maestras").rglob("*.docx"))
    modelo = next((p for p in plantillas if FIRMA in _texto(p)), None)
    if modelo is None:
        print("Ninguna plantilla lleva la firma mandada: no hay con que probar.")
        return 1

    destino = Path(tempfile.mkdtemp(prefix="prueba_ver_")) / "roto.docx"
    shutil.copy2(modelo, destino)

    with zipfile.ZipFile(destino) as z:
        nombres = z.namelist()
        datos = {n: z.read(n) for n in nombres}
    xml = datos["word/document.xml"].decode("utf-8")
    datos["word/document.xml"] = xml.replace(FIRMA, "QUIEN SEA").encode("utf-8")
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for n in nombres:
            z.writestr(n, datos[n])

    print("Documento de prueba: %s con la firma rota a proposito." % modelo.name[:50])
    if V.verificar(str(destino)):
        print()
        print("  FALLA  el verificador aprobo un documento que debia rechazar.")
        return 1
    print()
    print("  OK     el verificador rechaza lo que debe rechazar.")
    return 0


def _texto(ruta: Path) -> str:
    try:
        with zipfile.ZipFile(ruta) as z:
            return z.read("word/document.xml").decode("utf-8", "replace")
    except Exception:
        return ""


if __name__ == "__main__":
    raise SystemExit(main())
