#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Superficie de control de Antigravity: lanzar un caso y corregirlo en caliente.

Por que existe: el 14/09/2026 se superviso una remesa de trece expedientes
interviniendo al agente **mientras trabajaba**, y eso resulto ser la diferencia
entre un caso de 37 minutos y uno de 5. Pero la forma de hacerlo --el puerto, el
token, el identificador de proyecto-- vivia en la cabeza de quien supervisaba esa
tarde. Sin este archivo, el siguiente supervisor no puede repetir nada.

Antigravity expone su API de agente en el propio ejecutable de su language server:

    resources/bin/language_server.exe agentapi new-conversation|send-message|...

Necesita tres datos de entorno que **no hay que pedirle a nadie**: se leen de la
linea de comandos del proceso que ya esta corriendo.

  ANTIGRAVITY_LS_ADDRESS   127.0.0.1:<puerto gRPC en escucha del language_server>
  ANTIGRAVITY_CSRF_TOKEN   el `--csrf_token` con el que arranco
  ANTIGRAVITY_PROJECT_ID   un proyecto existente; sin el, `new-conversation`
                           responde «project_id is required»

Uso:
    python scripts/orquestar.py estado
    python scripts/orquestar.py lanzar 2765-2026
    python scripts/orquestar.py corregir <conversacion> "texto"
    python scripts/orquestar.py corregir <conversacion> --archivo mensaje.txt

Lo que este script **no** hace: decidir. Lanza el encargo canonico y transmite la
correccion que el supervisor escribe. El juicio no se automatiza.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

PROGRAMAS = Path.home() / "AppData" / "Local" / "Programs" / "antigravity"
LS = PROGRAMAS / "resources" / "bin" / "language_server.exe"
DATOS = Path.home() / ".gemini" / "antigravity"
RESUMENES = DATOS / "conversation_summaries.db"
EXPEDIENTES = Path.home() / "Desktop" / "expedientes"


def _powershell(comando: str) -> str:
    return subprocess.run(
        ["powershell", "-NoProfile", "-Command", comando],
        capture_output=True,
    ).stdout.decode("utf-8", "replace")


def entorno() -> dict[str, str]:
    """Descubre direccion, token y proyecto del Antigravity que esta corriendo."""
    linea = _powershell(
        "Get-CimInstance Win32_Process -Filter \"Name='language_server.exe'\" "
        "| Select-Object -First 1 -ExpandProperty CommandLine"
    )
    if not linea.strip():
        raise SystemExit(
            "Antigravity no esta corriendo: no hay language_server.exe.\n"
            "Abre la aplicacion y vuelve a intentarlo."
        )

    m = re.search(r"--csrf_token\s+(\S+)", linea)
    if not m:
        raise SystemExit(
            "El language_server no declara --csrf_token en su linea de comandos."
        )
    token = m.group(1)

    pid = _powershell(
        "(Get-Process language_server -ErrorAction SilentlyContinue "
        "| Select-Object -First 1).Id"
    ).strip()
    puertos = _powershell(
        "Get-NetTCPConnection -State Listen | Where-Object {$_.OwningProcess -eq %s} "
        "| Select-Object -ExpandProperty LocalPort" % pid
    ).split()
    if not puertos:
        raise SystemExit("El language_server no tiene ningun puerto en escucha.")

    # De los puertos en escucha, el bueno es el que contesta el gRPC. El otro
    # corta la conexion nada mas abrirla, asi que se prueban todos y se queda el
    # que responde algo que no sea un error de transporte.
    for puerto in sorted(puertos, reverse=True):
        env = {
            "ANTIGRAVITY_LS_ADDRESS": "127.0.0.1:%s" % puerto,
            "ANTIGRAVITY_CSRF_TOKEN": token,
        }
        salida = _ejecutar(["get-conversation-metadata", "0"], env, tolerante=True)
        if "error reading server preface" not in salida:
            return {**env, "ANTIGRAVITY_PROJECT_ID": proyecto_existente()}
    raise SystemExit("Ninguno de los puertos en escucha respondio al agentapi.")


def proyecto_existente() -> str:
    """Un proyecto cualquiera de los que ya usa Antigravity.

    `new-conversation` exige uno. El workspace de ese proyecto puede no ser el
    repositorio --de hecho no lo es-- y por eso el encargo lleva siempre rutas
    absolutas y fija el Cwd por escrito.
    """
    tmp = Path(tempfile.mkdtemp(prefix="orq_"))
    for suf in ("", "-wal", "-shm"):
        s = Path(str(RESUMENES) + suf)
        if s.exists():
            shutil.copy2(s, tmp / s.name)
    con = sqlite3.connect(str(tmp / RESUMENES.name))
    filas = con.execute(
        "SELECT project_id, COUNT(*) FROM conversation_summaries "
        "WHERE project_id != '' AND project_id != 'outside-of-project' "
        "GROUP BY project_id ORDER BY COUNT(*) DESC"
    ).fetchall()
    con.close()
    if not filas:
        raise SystemExit(
            "No hay ningun proyecto en Antigravity. Abre una carpeta como workspace "
            "en la aplicacion y vuelve a intentarlo."
        )
    return filas[0][0]


def _ejecutar(
    argumentos: list[str], env: dict[str, str], tolerante: bool = False
) -> str:
    import os

    entorno_completo = {**os.environ, **env}
    proc = subprocess.run(
        [str(LS), "agentapi", *argumentos],
        capture_output=True,
        env=entorno_completo,
    )
    salida = proc.stdout.decode("utf-8", "replace") + proc.stderr.decode(
        "utf-8", "replace"
    )
    if not tolerante and '"error"' in salida:
        print(salida[:600])
    return salida


def resolucion_de_cedula(carpeta: Path) -> str:
    import preparar_remesa as PR

    cedulas = sorted(carpeta.glob("ADM*CEDULAS*.docx"))
    if not cedulas:
        raise SystemExit(
            "No hay cedula en %s: sin ella no se sabe el ordinal." % carpeta
        )
    resolucion, _partes = PR.censo_cedula(cedulas[0])
    if not resolucion:
        raise SystemExit(
            "La cedula de %s no declara el numero de resolucion." % carpeta.name
        )
    return resolucion


ENCARGO = """Redacta el admisorio del Expediente {exp}/CC1. Trabajas solo en ESTE expediente.

ORDEN DE TRABAJO (leela entera UNA vez y siguela; el triaje, la cedula, el dossier
anclado y las candidatas de plantilla YA ESTAN HECHOS, no los rehagas):
{carpeta}\\_ORDEN_DE_TRABAJO.md

WORKSPACE: todo comando desde {raiz}
Solo puedes abrir esa carpeta y la del expediente. Nada mas.

LECTURA (R-137): lee TODAS las paginas con Google Lens. Ya estan renderizadas en
{carpeta}\\_paginas\\ y tu orden lista la ruta de cada una. NO las renderices tu.
Cero OCR. El volcado _texto_expediente.txt es CONTRASTE: si discrepa con lo que
ves, manda lo que ves. Deja constancia en {carpeta}\\_LECTURA.md, una linea por
pagina citando el nombre del PNG y lo que viste en ella. Sin ese archivo la
entrega no pasa.

CONSTRUCCION (R-139): PROHIBIDO win32com y PROHIBIDO escribir scratch. Se usa
  python scripts/construir_admisorio.py --mapa <mapa.json>
Tu mapa y cualquier archivo de trabajo van en la carpeta del EXPEDIENTE, nunca en
la raiz del repositorio: es publico y tu mapa lleva nombres de personas.
Tres cosas del constructor que te ahorran vueltas:
 - una clave que no coincida al caracter se alinea sola si se parece >92%;
 - una clave NO puede abarcar dos parrafos: divide el reemplazo;
 - un reemplazo a cadena vacia borra el parrafo entero, sin vineta huerfana.
Arregla primero los reemplazos fallidos: un dato duro suele seguir dentro porque
la frase que lo contenia no se sustituyo.

INVARIANTES: partes procesales exactamente las de la cedula, una sola via cada una
(R-138). Fecha: Lima, 14 de setiembre de 2026. Firma: LUISA ANALI SILVA
MALPARTIDA, Secretaria Tecnica (e). Es la Resolucion N {res}.
NO INVENTES: dato que no veas en una pagina se declara pendiente del instructor.

ENTREGABLE, con este nombre exacto:
{carpeta}\\ADM {exp} R{res}.docx
Nada de PDF. Nada de commitear.

CIERRE:
python scripts/admisorio.py entregar "{carpeta}\\ADM {exp} R{res}.docx" --caso {corto}
Tiene que decir APTO (0 falsadores) y ENTREGABLE. Pega la salida literal, escribe
un _ESTADO.md con la marca CASO CERRADO en la carpeta del expediente, y declarame
cuantas llamadas usaste y cuanto tardo."""


def lanzar(expediente: str, modelo: str) -> int:
    carpeta = EXPEDIENTES / expediente
    if not carpeta.is_dir():
        raise SystemExit("No existe la carpeta %s" % carpeta)
    orden = carpeta / "_ORDEN_DE_TRABAJO.md"
    if not orden.exists():
        raise SystemExit(
            "Falta %s. Ejecuta antes:\n"
            "  python scripts/preparar_remesa.py %s --caso %s"
            % (orden.name, EXPEDIENTES, expediente)
        )
    estado = carpeta / "_ESTADO.md"
    if estado.exists() and "CASO CERRADO" in estado.read_text(
        encoding="utf-8", errors="replace"
    ):
        raise SystemExit("%s esta CERRADO (R-122). No se relanza." % expediente)

    res = resolucion_de_cedula(carpeta)
    env = entorno()
    prompt = ENCARGO.format(
        exp=expediente,
        carpeta=carpeta,
        raiz=RAIZ,
        res=res,
        corto=expediente.split("-")[0],
    )
    salida = _ejecutar(
        [
            "new-conversation",
            "--model=%s" % modelo,
            "--title=ADM %s R%s" % (expediente, res),
            prompt,
        ],
        env,
    )
    try:
        cid = json.loads(salida)["response"]["newConversation"]["conversationId"]
    except Exception:
        print(salida[:400])
        return 1
    print("%s  Resolucion %s  ->  conversacion %s" % (expediente, res, cid))
    print("Vigilalo con:")
    print("  python scripts/vigilar_remesa.py %s:%s:%s" % (cid, expediente, res))
    return 0


def corregir(conversacion: str, mensaje: str) -> int:
    env = entorno()
    salida = _ejecutar(["send-message", conversacion, mensaje], env)
    if '"error"' in salida:
        return 1
    print(
        "Correccion entregada a %s (%d caracteres)." % (conversacion[:8], len(mensaje))
    )
    return 0


def estado() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="orq_"))
    for suf in ("", "-wal", "-shm"):
        s = Path(str(RESUMENES) + suf)
        if s.exists():
            shutil.copy2(s, tmp / s.name)
    con = sqlite3.connect(str(tmp / RESUMENES.name))
    filas = con.execute(
        "SELECT conversation_id, title, status, step_count FROM conversation_summaries "
        "ORDER BY last_modified_time DESC LIMIT 12"
    ).fetchall()
    con.close()
    print("%-10s %-30s %-10s %s" % ("id", "titulo", "estado", "pasos"))
    for cid, titulo, st, pasos in filas:
        print(
            "%-10s %-30s %-10s %d"
            % (
                cid[:8],
                (titulo or "")[:30],
                (st or "").replace("CASCADE_RUN_STATUS_", ""),
                pasos,
            )
        )
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="orden", required=True)
    sub.add_parser("estado", help="Conversaciones y en que estado estan")
    p = sub.add_parser("lanzar", help="Lanza un expediente con el encargo canonico")
    p.add_argument("expediente")
    p.add_argument("--modelo", default="pro", choices=("flash_lite", "flash", "pro"))
    c = sub.add_parser("corregir", help="Envia una correccion a una conversacion viva")
    c.add_argument("conversacion")
    c.add_argument("mensaje", nargs="?", default="")
    c.add_argument("--archivo", help="Lee el mensaje de un archivo")

    args = ap.parse_args(argv[1:])
    if args.orden == "estado":
        return estado()
    if args.orden == "lanzar":
        return lanzar(args.expediente, args.modelo)
    mensaje = (
        Path(args.archivo).read_text(encoding="utf-8") if args.archivo else args.mensaje
    )
    if not mensaje.strip():
        raise SystemExit("No hay mensaje que enviar.")
    return corregir(args.conversacion, mensaje)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
