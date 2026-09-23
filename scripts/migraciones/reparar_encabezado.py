#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repara el encabezado desalineado de las plantillas (supervision 2898-2026).

La anonimizacion de la v2.3.1 reescribio la linea del denunciante como
«DENUNCIANTE:[DENUNCIANTE] (SEÑOR [APELLIDO])» y dejo sus tabulaciones vacias al
final del parrafo. Las demas lineas son «ETIQUETA<tab>:<tab>VALOR», asi que los
dos puntos del denunciante quedaban fuera de columna en TODO admisorio
construido sobre esas plantillas.

Uso:
    python scripts/migraciones/reparar_encabezado.py [--aplicar]
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
RE_P = re.compile(r"<w:p[ >].*?</w:p>", re.S)
ETIQUETA = re.compile(
    r"^(DENUNCIANTES?|DENUNCIAD[OA]S?(?:\(S\))?|EXPEDIENTE|MATERIAS?|RESOLUCI[ÓO]N)(?:\s*:\s*(.*)|(\[.+))$",
    re.S,
)


def reparar_parrafo(p: str) -> str | None:
    runs = list(re.finditer(r"<w:r[ >].*?</w:r>", p, re.S))
    if not runs:
        return None
    primero = runs[0]
    m_t = re.search(r"<w:t(?:\s[^>/]*)?>([^<]*)</w:t>", primero.group(0))
    if not m_t:
        return None
    m = ETIQUETA.match(m_t.group(1))
    if not m:
        return None
    etiqueta, valor = m.group(1), (m.group(2) if m.group(2) is not None else m.group(3))
    nuevo_t = (
        '<w:t>%s</w:t><w:tab/><w:t>:</w:t><w:tab/><w:t xml:space="preserve">%s</w:t>'
        % (etiqueta, valor)
    )
    run_nuevo = primero.group(0).replace(m_t.group(0), nuevo_t, 1)
    salida = p[: primero.start()] + run_nuevo
    pos = primero.end()
    for r in runs[1:]:
        cuerpo = re.sub(r"<w:rPr>.*?</w:rPr>", "", r.group(0), flags=re.S)
        vacio = not re.search(r"<w:t(?:\s[^>/]*)?>[^<]+</w:t>", cuerpo)
        salida += p[pos : r.start()] + ("" if vacio else r.group(0))
        pos = r.end()
    return salida + p[pos:]


def main(argv: list[str]) -> int:
    aplicar = "--aplicar" in argv
    archivos = sorted((RAIZ / "plantillas_maestras").rglob("*.docx")) + sorted(
        (RAIZ / "automatizacion_antigravity/modelos").glob("*.docx")
    )
    tocados = 0
    for ruta in archivos:
        with zipfile.ZipFile(ruta) as z:
            infos = z.infolist()
            datos = {i.filename: z.read(i.filename) for i in infos}
        x = datos["word/document.xml"].decode("utf-8")
        cambio = False
        for p in RE_P.findall(x)[:14]:
            texto = re.sub(r"<[^>]+>", "", re.sub(r"<w:tab ?/>", "\t", p)).strip()
            if re.match(
                r"^(DENUNCIANTES?|DENUNCIAD[OA]S?(?:\(S\))?|EXPEDIENTE|MATERIAS?|RESOLUCI[ÓO]N)(\s*:|\[)",
                texto,
            ):
                nuevo = reparar_parrafo(p)
                # «MATERIAS<tab>: ADMISIÓN»: falta la segunda tabulacion y el
                # valor queda fuera de columna (4 plantillas).
                nuevo = re.sub(
                    r"(<w:tab ?/>)<w:t>: ([^<]+)</w:t>",
                    r'\1<w:t>:</w:t><w:tab/><w:t xml:space="preserve">\2</w:t>',
                    nuevo or p,
                )
                if nuevo and nuevo != p:
                    x = x.replace(p, nuevo, 1)
                    cambio = True
        if cambio:
            tocados += 1
            if aplicar:
                datos["word/document.xml"] = x.encode("utf-8")
                tmp = ruta.with_suffix(".tmp")
                with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
                    for i in infos:
                        zout.writestr(i, datos[i.filename])
                tmp.replace(ruta)
    print(
        "%s: %d de %d documentos con la etiqueta pegada a los dos puntos"
        % ("APLICADO" if aplicar else "SIMULACION", tocados, len(archivos))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
