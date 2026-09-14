#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vigila varios expedientes a la vez (solo lectura).

Con la remesa corriendo en paralelo, abrir un vigilante por caso multiplica los
procesos y el ruido. Este sigue todas las conversaciones activas de una vez y
escribe una linea por caso y sondeo: llamadas reales, pasadas de vision,
relecturas y si el entregable con el nombre mandado ya existe.

Uso:
    python scripts/vigilar_remesa.py <conv_id>:<EXP>:<RES> [...] [--segundos 30]
"""

from __future__ import annotations

import argparse
import shutil
import sqlite3
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import vigilar as V  # noqa: E402

RESUMENES = Path.home() / ".gemini" / "antigravity" / "conversation_summaries.db"
EXPEDIENTES = Path.home() / "Desktop" / "expedientes"


def estados(ids: list[str]) -> dict[str, tuple[str, int]]:
    tmp = Path(tempfile.mkdtemp(prefix="vigr_"))
    for suf in ("", "-wal", "-shm"):
        s = Path(str(RESUMENES) + suf)
        if s.exists():
            shutil.copy2(s, tmp / s.name)
    con = sqlite3.connect(str(tmp / RESUMENES.name))
    salida = {}
    for cid in ids:
        fila = con.execute(
            "SELECT status, step_count FROM conversation_summaries WHERE conversation_id = ?",
            (cid,),
        ).fetchone()
        salida[cid] = (
            (fila[0].replace("CASCADE_RUN_STATUS_", ""), fila[1]) if fila else ("?", 0)
        )
    con.close()
    return salida


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("casos", nargs="+", help="conv_id:EXPEDIENTE:RESOLUCION")
    ap.add_argument("--segundos", type=int, default=30)
    ap.add_argument("--minutos", type=int, default=40)
    args = ap.parse_args(argv[1:])

    casos = []
    for c in args.casos:
        cid, exp, res = c.split(":")
        casos.append(
            (cid, exp, res, EXPEDIENTES / exp / ("ADM %s R%s.docx" % (exp, res)))
        )

    t0 = time.time()
    while time.time() - t0 < args.minutos * 60:
        st = estados([c[0] for c in casos])
        vivos = 0
        linea = [datetime.now().strftime("%H:%M:%S")]
        for cid, exp, _res, entregable in casos:
            estado, _pasos = st[cid]
            censo = V.censo(cid)
            if estado == "RUNNING":
                vivos += 1
            linea.append(
                "%s %s n=%-3d vis=%-2d rel=%-2d %s"
                % (
                    exp.split("-")[0],
                    estado[:4],
                    censo.get("llamadas", 0),
                    censo.get("vision", 0),
                    censo.get("relecturas", 0),
                    "DOCX" if entregable.exists() else "----",
                )
            )
        print("  |  ".join(linea), flush=True)
        if not vivos:
            print("  -> todas las conversaciones estan IDLE", flush=True)
            return 0
        time.sleep(args.segundos)
    print("  -> limite de vigilancia alcanzado", flush=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
