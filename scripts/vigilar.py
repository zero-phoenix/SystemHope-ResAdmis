#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vigila en vivo una conversacion del agente y su entregable (solo lectura).

El supervisor no puede permitirse enterarse al final. Este script sigue la
trayectoria mientras ocurre y escribe una linea por sondeo con lo unico que
importa para intervenir a tiempo: cuantas llamadas lleva, en que herramienta esta,
cuanto desperdicio acumula y si el `.docx` ya existe.

Se apoya en `auditar_trayectoria.py` para el censo de desperdicio, de modo que el
criterio en vivo y el criterio de cierre sean el mismo.

Uso:
    python scripts/vigilar.py <conversation_id> <carpeta_expediente> [--segundos 20] [--minutos 20]
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import auditar_trayectoria as AT  # noqa: E402

RESUMENES = Path.home() / ".gemini" / "antigravity" / "conversation_summaries.db"
CONVERSACIONES = Path.home() / ".gemini" / "antigravity" / "conversations"


def estado(cid: str) -> tuple[str, int]:
    filas = AT.cargar(RESUMENES) if False else None  # no aplica: esquema distinto
    import shutil
    import tempfile

    tmp = Path(tempfile.mkdtemp(prefix="vig_"))
    for suf in ("", "-wal", "-shm"):
        s = Path(str(RESUMENES) + suf)
        if s.exists():
            shutil.copy2(s, tmp / s.name)
    con = sqlite3.connect(str(tmp / RESUMENES.name))
    fila = con.execute(
        "SELECT status, step_count FROM conversation_summaries WHERE conversation_id = ?",
        (cid,),
    ).fetchone()
    con.close()
    return (fila[0], fila[1]) if fila else ("(sin registro)", 0)


def censo(cid: str) -> dict:
    db = CONVERSACIONES / ("%s.db" % cid)
    if not db.exists():
        return {}
    try:
        filas = AT.cargar(db)
    except Exception:
        return {}
    import re
    from collections import Counter

    # La unidad es el identificador de llamada, no el paso: una misma llamada
    # aparece en la invocacion y en el resultado, y contar pasos infla el censo
    # ~2,3x. El comando del propio encargo tambien aparece en la traza, asi que
    # las busquedas recursivas solo se cuentan dentro de un `run_command`.
    TOOL = re.compile(rb"call_\d+.{0,3}?([a-z_]{3,})", re.S)
    LLAMADA = re.compile(rb"(call_\d+)")
    CMD = re.compile(rb"run_command.{0,80}?CommandLine\":\"(.{2,400}?)\",\"", re.S)
    VIEW = re.compile(rb"view_file.{0,400}?AbsolutePath\":\"(.{4,240}?)\",\"", re.S)
    herramientas: Counter[str] = Counter()
    vision = recursivas = 0
    vistos: Counter[str] = Counter()
    llamadas_vistas: set[bytes] = set()
    ultima = ""
    for _idx, _st, payload, _task, _meta in filas:
        p = payload or b""
        ids = LLAMADA.findall(p)
        if not ids or ids[0] in llamadas_vistas:
            continue
        llamadas_vistas.add(ids[0])
        m = TOOL.search(p)
        if m:
            ultima = m.group(1).decode(errors="replace")
            herramientas[ultima] += 1
        for ruta in set(VIEW.findall(p)):
            r = ruta.decode(errors="replace")
            vistos[r] += 1
            if r.lower().endswith((".png", ".jpg", ".jpeg")):
                vision += 1
        for cmd in CMD.findall(p):
            c = cmd.decode(errors="replace")
            if re.search(r"-Recurse", c, re.I) and re.search(r"C:\\\\?Users", c, re.I):
                recursivas += 1
    relecturas = sum(v - 1 for v in vistos.values() if v > 1)
    return {
        "herramientas": herramientas,
        "llamadas": sum(herramientas.values()),
        "vision": vision,
        "relecturas": relecturas,
        "recursivas": recursivas,
        "ultima": ultima,
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("conversacion")
    ap.add_argument("carpeta")
    ap.add_argument("--segundos", type=int, default=20)
    ap.add_argument("--minutos", type=int, default=20)
    args = ap.parse_args(argv[1:])

    carpeta = Path(args.carpeta)
    t0 = time.time()
    limite = args.minutos * 60
    print("VIGILANCIA  %s  ->  %s" % (args.conversacion[:8], carpeta.name), flush=True)
    print(
        "%-8s %-6s %-26s %5s %5s %5s %5s  %s"
        % ("hora", "min", "estado", "llam", "vis", "rele", "recu", "entregable"),
        flush=True,
    )
    while time.time() - t0 < limite:
        st, pasos = estado(args.conversacion)
        c = censo(args.conversacion)
        docs = sorted(carpeta.glob("*ADMISORIO*.docx")) + sorted(
            carpeta.glob("RES_*.docx")
        )
        pdfs_nuevos = [p.name for p in carpeta.glob("*.pdf") if p.stat().st_mtime > t0]
        marca = docs[0].name if docs else "-"
        if pdfs_nuevos:
            marca += "  !!PDF GENERADO: %s" % ", ".join(pdfs_nuevos)
        print(
            "%-8s %-6.1f %-26s %5d %5d %5d %5d  %s"
            % (
                datetime.now().strftime("%H:%M:%S"),
                (time.time() - t0) / 60,
                st.replace("CASCADE_RUN_STATUS_", ""),
                c.get("llamadas", 0),
                c.get("vision", 0),
                c.get("relecturas", 0),
                c.get("recursivas", 0),
                marca,
            ),
            flush=True,
        )
        if st.endswith("IDLE") and pasos > 5:
            print(
                "  -> conversacion IDLE. Herramientas: %s"
                % dict(c.get("herramientas", {})),
                flush=True,
            )
            return 0
        time.sleep(args.segundos)
    print("  -> limite de vigilancia alcanzado", flush=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
