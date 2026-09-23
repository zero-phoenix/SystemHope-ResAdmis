#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nota al pie de la denuncia en las plantillas (instructor, 23/09/2026).

La unica nota sobre la denuncia es la del traslado: «Denuncia remitida a esta
Comisión mediante [documento] de fecha [emision], recibida el [recepcion en CC1].»
y solo cuando la denuncia llego derivada. Este script:

1. elimina la nota «Denuncia presentada mediante escrito ...» (7 plantillas) y
   su llamada: si la denuncia se presento en CC1 no lleva nota sobre ello;
2. normaliza las erratas de la nota del traslado sin inventar datos: «del» ->
   «de fecha», «recibido»/«recibida por el»/«recibida X» -> «recibida el»,
   «a la Comisión de Protección al Consumidor 1» -> «a esta Comisión», punto
   final unico. Una nota sin fecha de recibido NO se completa: queda marcada por
   R-167 y la plantilla deja de ser apta como base.

Uso:
    python scripts/migraciones/notas_denuncia.py [--aplicar]
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "scripts"))

import construir_admisorio as C  # noqa: E402

RE_FN = re.compile(r'(<w:footnote\b[^>]*w:id="(\d+)"[^>]*>)(.*?)(</w:footnote>)', re.S)
FECHA = r"\d{1,2} de [a-záéíóú]+ de \d{4}"


def plano(xml: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", xml)).strip()


def normalizar(t: str) -> str:
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(
        r"^Denuncia remitida mediante ",
        "Denuncia remitida a esta Comisión mediante ",
        t,
    )
    t = re.sub(
        r"^Denuncia remitida a (?:la|esta) Comisión de Protección al Consumidor 1 mediante ",
        "Denuncia remitida a esta Comisión mediante ",
        t,
    )
    t = re.sub(r"(/INDECOPI) del (%s)" % FECHA, r"\1 de fecha \2", t)
    t = re.sub(r"(%s) recibida" % FECHA, r"\1, recibida", t)
    t = re.sub(r"recibid[oa](?: por)?(?: el)? (%s)" % FECHA, r"recibida el \1", t)
    t = re.sub(r"\s+", " ", t).strip().rstrip(".").rstrip(",") + "."
    return t


def procesar(x: str, fx: str) -> tuple[str, str, list[str]]:
    hechos = []
    for m in list(RE_FN.finditer(fx)):
        fid, cuerpo = m.group(2), m.group(3)
        t = plano(cuerpo)
        if t.startswith("Denuncia presentada"):
            x2 = re.sub(
                r'<w:r\b[^>]*>(?:(?!</w:r>).)*?<w:footnoteReference\b[^>]*w:id="%s"[^>]*/>(?:(?!</w:r>).)*?</w:r>'
                % fid,
                "",
                x,
                count=1,
                flags=re.S,
            )
            if x2 != x:
                x = x2
                fx = fx.replace(m.group(0), "", 1)
                hechos.append("eliminada: " + t[:60])
        elif t.startswith("Denuncia remitida"):
            ps = list(C.RE_PARRAFO.finditer(cuerpo))
            p = next(
                (q for q in ps if "Denuncia remitida" in C.texto_parrafo(q.group(0))),
                None,
            )
            if not p:
                continue
            viejo = C.texto_parrafo(p.group(0))
            k = viejo.index("Denuncia remitida")
            nuevo = viejo[:k] + normalizar(viejo[k:])
            if nuevo != viejo:
                cuerpo2 = cuerpo.replace(
                    p.group(0), C.reescribir_parrafo(p.group(0), nuevo), 1
                )
                fx = fx.replace(m.group(0), m.group(1) + cuerpo2 + m.group(4), 1)
                hechos.append("normalizada: " + normalizar(viejo[k:])[:90])
    return x, fx, hechos


def main(argv: list[str]) -> int:
    aplicar = "--aplicar" in argv
    rutas = sorted((RAIZ / "plantillas_maestras").rglob("*.docx")) + sorted(
        (RAIZ / "automatizacion_antigravity/modelos").glob("*.docx")
    )
    tocados = 0
    for ruta in rutas:
        with zipfile.ZipFile(ruta) as z:
            infos = z.infolist()
            datos = {i.filename: z.read(i.filename) for i in infos}
        x = datos["word/document.xml"].decode("utf-8")
        fx = datos["word/footnotes.xml"].decode("utf-8")
        x2, fx2, hechos = procesar(x, fx)
        if not hechos:
            continue
        tocados += 1
        for h in hechos:
            print("  %s: %s" % (ruta.name[:9], h))
        if aplicar:
            datos["word/document.xml"] = x2.encode("utf-8")
            datos["word/footnotes.xml"] = fx2.encode("utf-8")
            tmp = ruta.with_suffix(".tmp")
            with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
                for i in infos:
                    zout.writestr(i, datos[i.filename])
            tmp.replace(ruta)
    print("%s: %d documentos" % ("APLICADO" if aplicar else "SIMULACION", tocados))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
