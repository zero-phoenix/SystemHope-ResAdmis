#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Filtra el padrón de Términos y Condiciones de la Casilla Electrónica y deja,
en `docs/casillas_habilitadas.json`, qué proveedores admiten notificación por
casilla y cuáles no.

REGLA (mandato del instructor, 18/09/2026):
    Solo procede notificar a Casilla Electrónica cuando el registro está
    **ACTIVA**, tiene **número de e-casilla** y tiene **teléfono móvil
    registrado y no vacío**. Si falta cualquiera de los tres, la casilla NO
    procede y la parte se notifica por correo electrónico o por domicilio
    procesal, según lo que indique la cédula.

    Es una condición NECESARIA, no suficiente: que un proveedor esté habilitado
    no obliga a usar la casilla —eso lo fija la cédula (R-129)—, pero que NO lo
    esté prohíbe usarla.

EL PADRÓN NO ENTRA AL REPOSITORIO. Trae 30 105 registros con DNI, nombres,
correos y teléfonos de consumidores, y este repositorio es público. Este script
lo lee de donde esté y publica **solo**: razón social de personas jurídicas que
son proveedores de la CC1, y el veredicto. Ni un teléfono, ni un correo, ni un
número de casilla, ni una sola persona natural.

Uso:
    python scripts/filtrar_casillas.py <ReportePersonas....xlsx>
    python scripts/filtrar_casillas.py <xlsx> --verificar   # no escribe: compara
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "docs" / "casillas_habilitadas.json"

# Proveedores que la CC1 ve en sus expedientes. La lista acota QUÉ se publica:
# todo lo que no sea uno de estos no sale del padrón.
CLAVES_PROVEEDOR = [
    "RIMAC SEGUROS", "RIMAC S A ENTIDAD PRESTADORA", "PACIFICO COMPANIA",
    "PACIFICO SEGUROS", "MAPFRE PERU", "INTERSEGURO", "LA POSITIVA",
    "CHUBB PERU", "PROTECTA", "QUALITAS", "BNP PARIBAS CARDIF", "CRECER SEGUROS",
    "VIVIR SEGUROS", "INSUR ", "BANCO BBVA", "BBVA CONSUMER FINANCE",
    "SCOTIABANK", "BANCO INTERNACIONAL DEL PERU", "BANCO DE CREDITO DEL PERU",
    "BANCO FALABELLA", "BANCO RIPLEY", "BANCO PICHINCHA", "BANCO GNB",
    "BANCO SANTANDER", "EMPRESA DE CREDITOS SANTANDER", "SANTANDER FINANCIAMIENTOS",
    "BANCO DE LA NACION", "BANCO INTERAMERICANO DE FINANZAS", "DINERS CLUB PERU",
    "AUTOPLAN", "PANDERO", "FINANCIERA PROEMPRESA", "FONDO DE VIVIENDA POLICIAL",
    "ASOCIACION FONDO CONTRA ACCIDENTES DE TRANSITO",
    "ASOC DE FONDOS CONTRA ACCIDENTES DE TRANSITO",
    "ASOCIAC  FONDO CONTRA ACCIDEN", "SUB CAFAE", "CAJA MUNICIPAL",
]

# Marcas de persona jurídica. Se exige una, pero las claves de CLAVES_PROVEEDOR
# ya son razones sociales de empresas: sin ellas no se llega hasta aquí. Esta
# comprobación es el segundo cerrojo, no el primero.
JURIDICA = re.compile(
    r"\b(S\s?A\s?C|S\s?A\s?A|S\s?A|S\s?R\s?L|E\s?I\s?R\s?L|E\s?A\s?F\s?C|"
    r"ASOCIACION|ASOC|BANCO|COMPANIA|FONDO|COOPERATIVA|CAFAE|CAJA|EMPRESA|"
    r"FINANCIERA|ENTIDAD|SEGUROS|REASEGUROS|CREDITOS|CLUB)\b")


def norm(s) -> str:
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Z0-9 ]", " ", re.sub(r"\s+", " ", s.upper())).strip()


def con_valor(v) -> bool:
    return v is not None and str(v).strip() not in ("", "None", "NULL", "0")


def leer(ruta: Path):
    try:
        import openpyxl
    except ImportError:
        sys.exit("Falta openpyxl: pip install openpyxl")
    wb = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
    for hoja in wb.sheetnames:
        if hoja.upper() not in ("ACTIVA", "DE BAJA"):
            continue
        ws = wb[hoja]
        it = ws.iter_rows(values_only=True)
        cab = next(it)
        idx = {str(c).strip(): i for i, c in enumerate(cab) if c}
        for f in it:
            if not f or not any(f):
                continue
            yield hoja.upper(), {k: f[i] for k, i in idx.items()}


def construir(ruta: Path) -> dict:
    proveedores: dict[str, dict] = {}
    universo = {"ACTIVA": 0, "DE BAJA": 0, "con_telefono": 0, "sin_telefono": 0}

    for hoja, r in leer(ruta):
        universo[hoja] = universo.get(hoja, 0) + 1
        universo["con_telefono" if con_valor(r.get("TELEFONO MOVIL")) else "sin_telefono"] += 1

        # persona natural -> jamás sale de aquí
        if con_valor(r.get("DNI")) or con_valor(r.get("APELLIDO PATERNO")):
            continue
        rs = norm(r.get("RAZON SOCIAL"))
        if not rs or not JURIDICA.search(rs):
            continue
        if not any(re.search(r"\b" + re.escape(k), rs) for k in CLAVES_PROVEEDOR):
            continue
        # además de no traer DNI ni apellido, no puede traer nombres de pila
        if con_valor(r.get("NOMBRES")):
            continue

        habilitado = (hoja == "ACTIVA"
                      and con_valor(r.get("E-CASILLA"))
                      and con_valor(r.get("TELEFONO MOVIL")))
        motivo = ("activa, con casilla y con teléfono" if habilitado else
                  "de baja en el padrón" if hoja == "DE BAJA" else
                  "sin teléfono móvil registrado" if not con_valor(r.get("TELEFONO MOVIL")) else
                  "sin número de casilla")
        anterior = proveedores.get(rs)
        if anterior is None or (habilitado and not anterior["casilla_habilitada"]):
            proveedores[rs] = {"casilla_habilitada": habilitado, "motivo": motivo}

    hab = sum(1 for v in proveedores.values() if v["casilla_habilitada"])
    return {
        "_regla": ("Solo procede la Casilla Electronica con estado ACTIVA, numero de "
                   "e-casilla y telefono movil no vacio. Condicion NECESARIA: la cedula "
                   "decide la via (R-129), pero sin los tres requisitos la casilla esta "
                   "prohibida."),
        "_fuente": ("Padron de aceptacion de TyC de la Casilla Electronica del Indecopi. "
                    "El padron NO se versiona: contiene datos personales y este "
                    "repositorio es publico. Aqui solo constan personas juridicas "
                    "proveedoras de la CC1 y su veredicto."),
        "_universo": universo,
        "_habilitados": hab,
        "_no_habilitados": len(proveedores) - hab,
        "proveedores": dict(sorted(proveedores.items())),
    }


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    ruta = Path(argv[1])
    if not ruta.exists():
        print(f"No existe: {ruta}")
        return 1
    datos = construir(ruta)

    if "--verificar" in argv:
        if not SALIDA.exists():
            print("FALLA: no existe docs/casillas_habilitadas.json")
            return 1
        viejo = json.loads(SALIDA.read_text(encoding="utf-8"))
        if viejo.get("proveedores") != datos["proveedores"]:
            print("FALLA: el padron y docs/casillas_habilitadas.json discrepan")
            return 1
        print("OK: el padron y el fichero publicado coinciden")
        return 0

    SALIDA.write_text(json.dumps(datos, ensure_ascii=False, indent=1) + "\n",
                      encoding="utf-8")
    u = datos["_universo"]
    print(f"Padron leido: {u.get('ACTIVA', 0)} activas, {u.get('DE BAJA', 0)} de baja; "
          f"{u['sin_telefono']} sin telefono movil.")
    print(f"Proveedores de la CC1 publicados: {len(datos['proveedores'])} "
          f"({datos['_habilitados']} con casilla habilitada, "
          f"{datos['_no_habilitados']} sin ella).")
    print(f"Escrito: {SALIDA.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
