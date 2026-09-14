#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auditor de trayectoria del agente (solo lectura).

Lee la base de conversaciones de Antigravity, reconstruye la secuencia real de
llamadas del caso y puntua el desperdicio medido. No juzga la calidad del
documento: eso lo hacen `verificar_admisorio.py` y el diff contra el control.
Aqui se juzga **como trabajo el agente**.

Uso:
    python scripts/auditar_trayectoria.py                       # conversacion mas reciente
    python scripts/auditar_trayectoria.py <conversacion.db>
    python scripts/auditar_trayectoria.py <conversacion.db> --caso 3054

Hallazgos que persigue (medidos en el Expediente 3054-2026, 14/09/2026):
  - 21 paginas con capa de texto leidas con vision (R-113/R-95).
  - El mismo archivo de texto releido 4 veces desde el offset 0 (R-114).
  - Comandos con Cwd fuera del repositorio y busqueda recursiva de todo
    C:\\Users para hallar un script del propio repositorio.
  - Espera activa: `manage_task` consultado mas de una vez por comando.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sqlite3
import sys
import tempfile
from collections import Counter
from pathlib import Path

RUTA_CONVERSACIONES = Path.home() / ".gemini" / "antigravity" / "conversations"

TOOL = re.compile(rb"call_\d+.{0,3}?([a-z_]{3,})", re.S)
LLAMADA = re.compile(rb"(call_\d+)")
VIEW = re.compile(rb"view_file.{0,400}?AbsolutePath\":\"(.{4,240}?)\",\"", re.S)
CMD = re.compile(rb"run_command.{0,80}?CommandLine\":\"(.{2,400}?)\",\"", re.S)
CWD = re.compile(rb"Cwd\":\"(.{2,200}?)\",\"")
TASK = re.compile(rb"manage_task")


def conversacion_mas_reciente() -> Path | None:
    if not RUTA_CONVERSACIONES.exists():
        return None
    dbs = sorted(
        RUTA_CONVERSACIONES.glob("*.db"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return dbs[0] if dbs else None


def cargar(db: Path) -> list[tuple]:
    tmp = Path(tempfile.mkdtemp(prefix="audit_ag_"))
    for suf in ("", "-wal", "-shm"):
        s = Path(str(db) + suf)
        if s.exists():
            shutil.copy2(s, tmp / s.name)
    con = sqlite3.connect(str(tmp / db.name))
    filas = con.execute(
        "SELECT idx, step_type, step_payload, task_details, metadata FROM steps ORDER BY idx"
    ).fetchall()
    con.close()
    return filas


def auditar(filas: list[tuple], caso: str | None) -> int:
    desde = 0
    if caso:
        marca = caso.encode()
        for idx, _st, payload, task, meta in filas:
            if marca in (payload or b"") + (task or b"") + (meta or b""):
                desde = idx
                break

    vistos: Counter[str] = Counter()
    cwds: Counter[str] = Counter()
    vision: list[int] = []
    recursivas: list[int] = []
    herramientas: Counter[str] = Counter()
    relecturas = 0
    polls_tarea: Counter[str] = Counter()

    # Una misma llamada aparece en varios pasos de la traza (la invocacion, el
    # resultado y a veces un eco). Contar pasos inflaba el censo ~2,3x: la sesion
    # del Exp. 3054 figuraba con 157 llamadas cuando en realidad fueron 67. La
    # unidad correcta es el identificador de llamada, y cada uno cuenta una vez.
    vistas_llamadas: set[bytes] = set()
    vistas_rutas: set[tuple[bytes, str]] = set()
    vistas_cmds: set[tuple[bytes, str]] = set()

    for idx, step_type, payload, task, _meta in filas:
        if idx < desde:
            continue
        blob = (payload or b"") + (task or b"")
        llamadas_aqui = [m.group(1) for m in LLAMADA.finditer(payload or b"")]
        cid = llamadas_aqui[0] if llamadas_aqui else b""
        nueva = bool(cid) and cid not in vistas_llamadas
        if nueva:
            vistas_llamadas.add(cid)
            m = TOOL.search(payload or b"")
            if m:
                herramientas[m.group(1).decode()] += 1
            if b"manage_task" in blob:
                for tid in set(re.findall(rb"task-(\d+)", blob)):
                    polls_tarea[tid.decode()] += 1
        # Rutas y comandos se atribuyen a su llamada: la misma ruta repetida en el
        # paso de resultado no es una relectura.
        for ruta in set(re.findall(VIEW, blob)):
            r = ruta.decode("utf-8", "replace")
            clave = (cid, r)
            if clave in vistas_rutas:
                continue
            vistas_rutas.add(clave)
            vistos[r] += 1
            if r.lower().endswith(".png"):
                vision.append(idx)
        for cmd in re.findall(CMD, blob):
            c = cmd.decode("utf-8", "replace")
            clave = (cid, c)
            if clave in vistas_cmds:
                continue
            vistas_cmds.add(clave)
            if re.search(r"-Recurse", c, re.I) and re.search(
                r"C:\\\\?Users|C:\\\\?Usuarios", c, re.I
            ):
                recursivas.append(idx)
        if nueva:
            for w in set(re.findall(CWD, blob)):
                cwds[w.decode("utf-8", "replace")] += 1

    relecturas = sum(n - 1 for n in vistos.values() if n > 1)
    repetidos = [r for r, n in vistos.items() if n > 1]
    polls_extra = sum(n - 1 for n in polls_tarea.values() if n > 1)
    total_llamadas = sum(herramientas.values())

    def veredicto(ok: bool) -> str:
        return "OK  " if ok else "FALLA"

    print("=" * 78)
    print("AUDITORIA DE TRAYECTORIA")
    print("=" * 78)
    print("  Pasos auditados desde idx %d" % desde)
    print(
        "  Herramientas:", ", ".join("%s=%d" % kv for kv in herramientas.most_common())
    )
    print()
    print(
        "  %s  vision sobre imagenes ................ %d"
        % (veredicto(not vision), len(vision))
    )
    print(
        "  %s  relecturas del mismo archivo ........ %d"
        % (veredicto(relecturas == 0), relecturas)
    )
    print(
        "  %s  busquedas recursivas de C:\\Users .... %d"
        % (veredicto(not recursivas), len(recursivas))
    )
    print(
        "  %s  espera activa (polls de mas) ........ %d"
        % (veredicto(polls_extra == 0), polls_extra)
    )
    print(
        "  %s  llamadas a herramienta .............. %d (objetivo <= 12 fuera de triaje)"
        % (veredicto(total_llamadas <= 40), total_llamadas)
    )
    print()
    if cwds:
        print("  Cwd usados (fuera del repositorio = sintoma):")
        for w, n in cwds.most_common(6):
            print("     x%-3d %s" % (n, w))
    if repetidos:
        print("  Archivos vistos mas de una vez:")
        for r in sorted(repetidos, key=lambda x: -vistos[x])[:6]:
            print("     %d x %s" % (vistos[r], r))
    if vision:
        print("  Indices con vision:", vision[:25])
    print()
    desperdicio = len(vision) + relecturas + len(recursivas) + polls_extra
    print("  DESPERDICIO TOTAL: %d operacion(es) evitable(s)." % desperdicio)
    print("  Criterio del plan: cero vision con capa de texto, cero relecturas,")
    print("  cero busquedas recursivas, cero espera activa.")
    return 0 if desperdicio == 0 else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Auditor de trayectoria del agente")
    ap.add_argument(
        "db", nargs="?", help="conversacion .db (por defecto, la mas reciente)"
    )
    ap.add_argument(
        "--caso", help="numero de expediente a partir del cual auditar, p. ej. 3054"
    )
    args = ap.parse_args(argv[1:])

    db = Path(args.db) if args.db else conversacion_mas_reciente()
    if not db or not db.exists():
        print("No encontre la base de conversaciones de Antigravity.")
        return 2
    print("Base:", db)
    return auditar(cargar(db), args.caso)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
