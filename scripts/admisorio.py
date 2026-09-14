#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Punto de entrada unico del admisorio (frentes F8, F9 y F14 del mega plan).

Por que existe, con la medida delante:

En la traza real del Expediente 3054-2026 (14/09/2026) la sesion duro 1178 s de
reloj y gasto 157 llamadas a herramienta: 7,5 s por llamada, hiciera o no
trabajo. Un `manage_task` que no produce nada costo la misma mediana que generar
el documento. El computo util de un admisorio completo es ~12 s. Luego el tiempo
total no lo fija la maquina sino el numero de llamadas:

    T ~= 7,5 s x N

Este script existe para bajar N. Agrupa en una llamada lo que antes eran seis
(`preparar`) y en una lo que antes eran cuatro (`entregar`), y fija el Cwd en la
raiz del repositorio para que nadie vuelva a buscar un script propio con
`-Recurse` sobre `C:\\Users`.

Uso:
    python scripts/admisorio.py preparar <carpeta-del-expediente> [--contiene "texto"]
                                          [--rama 02_seguro_vida] [--sujeto varon]
    python scripts/admisorio.py entregar <generado.docx> [--caso 3054]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import estado_word  # noqa: E402
import extraer_expediente  # noqa: E402
import guardia_admisorio  # noqa: E402
import verificar_admisorio  # noqa: E402

INDICE = RAIZ / "docs" / "plantillas_maestras_index.json"
MARCA_CIERRE = "CASO CERRADO"
ETIQUETAS = ("_ESTADO.md", "_ORDEN_DE_TRABAJO.md")


def _titulo(texto: str) -> None:
    print("=" * 78)
    print(texto)
    print("=" * 78)


def _caso_cerrado(carpeta: Path) -> str | None:
    """R-122/F6: una carpeta marcada como cerrada no se vuelve a trabajar."""
    for nombre in ETIQUETAS:
        ruta = carpeta / nombre
        if ruta.exists() and MARCA_CIERRE in ruta.read_text(
            encoding="utf-8", errors="replace"
        ):
            return nombre
    return None


def _word_huerfano() -> list[dict]:
    """F1: Word sin ventana es la causa medida de cuelgue; se reporta con el PID."""
    try:
        return [w for w in estado_word.instancias_word() if not w.get("ventana")]
    except Exception as exc:  # el entorno puede no tener Word
        print("  (no se pudo consultar Word: %s)" % exc)
        return []


def _texto_plantilla(ruta: Path) -> str:
    with zipfile.ZipFile(ruta) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    return re.sub(r"<[^>]+>", "", xml)


def preparar(
    carpeta: Path, contiene: str | None, rama: str | None, sujeto: str | None
) -> int:
    t0 = time.time()
    carpeta = carpeta.resolve()

    cerrado = _caso_cerrado(carpeta)
    if cerrado:
        _titulo("PARO - CASO CERRADO (R-122)")
        print("  %s declara el caso cerrado. No se genera nada." % (carpeta / cerrado))
        print("  Regenerar trabajo cerrado es la causa medida de la demora.")
        return 2

    huerfanos = _word_huerfano()
    if huerfanos:
        _titulo("PARO - WORD HUERFANO (R-123)")
        for w in huerfanos:
            print(
                "  WINWORD.EXE PID %s sin ventana. Cierralo antes de seguir."
                % w.get("pid")
            )
        return 3

    extraer_expediente.informe(carpeta, volcar=True)
    inventario, _dossier = extraer_expediente.triaje(carpeta)
    sin_texto = sum(len(i["sin_texto"]) for i in inventario)

    _titulo("PLANTILLA BASE - CANDIDATAS DEL INDICE (F4)")
    fichas = json.loads(INDICE.read_text(encoding="utf-8"))
    candidatas = fichas
    if rama:
        candidatas = [f for f in candidatas if rama.lower() in f["rama"].lower()]
    if sujeto:
        candidatas = [
            f for f in candidatas if sujeto.lower() == f["sujeto_tipo"].lower()
        ]
    if contiene:
        aguja = contiene.lower()
        filtradas = []
        for f in candidatas:
            ruta = RAIZ / f["ruta_relativa"]
            if not ruta.exists():
                continue
            if aguja in _texto_plantilla(ruta).lower():
                filtradas.append(f)
        candidatas = filtradas
        print('  Filtro por texto: "%s"' % contiene)
    print("  %d de %d plantillas cumplen el filtro." % (len(candidatas), len(fichas)))
    for f in candidatas[:10]:
        print("    %-22s %-34s %s" % (f["rama"], f["materia"][:34], f["archivo"]))
    if len(candidatas) > 10:
        print("    ... y %d mas (afina el filtro)" % (len(candidatas) - 10))

    _titulo("SIGUIENTE PASO - UNA SOLA LLAMADA MAS")
    print("  1. Redactar con el constructor del caso sobre la plantilla elegida.")
    print("  2. Entregar:  python scripts/admisorio.py entregar <generado.docx>")
    print("  Vision multimodal autorizada: %d pagina(s)." % sin_texto)
    print("  Prohibido generar PDF (R-125). El entregable es el .docx.")
    print("  Preparacion completa en %.1f s y 1 llamada." % (time.time() - t0))
    return 0


def entregar(docx: Path, caso: str | None) -> int:
    t0 = time.time()
    docx = docx.resolve()
    fallas: list[str] = []

    if not verificar_admisorio.verificar(str(docx)):
        fallas.append("verificar_admisorio: NO APTO")

    _titulo("GUARDIA DE DATOS PERSONALES")
    fugas = guardia_admisorio.revisar([str(docx)])
    if fugas:
        print("  El documento NO se commitea (contiene datos del expediente):")
        for f in fugas:
            print("    - %s" % f)
    else:
        print("  Sin fuga detectada.")

    _titulo("RESTRICCIONES DURAS DEL PLAN")
    # Solo cuenta como PDF del pipeline el que nace del propio entregable: mismo
    # nombre, o escrito despues del .docx. Los PDF del expediente son la entrada.
    corte = docx.stat().st_mtime
    pdfs = [
        p.name
        for p in docx.parent.glob("*.pdf")
        if p.stem == docx.stem or p.stat().st_mtime > corte
    ]
    if pdfs:
        fallas.append("PDF generado: %s (R-125 lo prohibe)" % ", ".join(pdfs))
        print("  FALLA  PDF reciente en la carpeta: %s" % ", ".join(pdfs))
    else:
        print("  OK     ningun PDF producido por el pipeline.")

    huerfanos = _word_huerfano()
    if huerfanos:
        pids = ", ".join(str(w.get("pid")) for w in huerfanos)
        fallas.append("WINWORD.EXE huerfano: %s" % pids)
        print("  FALLA  Word sin ventana vivo: %s" % pids)
    else:
        print("  OK     ningun WINWORD.EXE vivo.")

    if caso:
        _titulo("SCORECARD DE TRAYECTORIA (F13)")
        import auditar_trayectoria  # import diferido: solo si se pide

        try:
            db = auditar_trayectoria.conversacion_mas_reciente()
            if db:
                auditar_trayectoria.auditar(auditar_trayectoria.cargar(db), caso)
            else:
                print("  (no hay base de conversaciones que auditar)")
        except Exception as exc:
            print("  (no se pudo auditar la trayectoria: %s)" % exc)

    _titulo("VEREDICTO")
    if fallas:
        for f in fallas:
            print("  FALLA  %s" % f)
        print("  --> NO ENTREGABLE.")
        return 1
    print(
        "  --> ENTREGABLE. Verificacion completa en %.1f s y 1 llamada."
        % (time.time() - t0)
    )
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="orden", required=True)

    p = sub.add_parser(
        "preparar", help="Triaje + plantilla + presupuesto de vision, en una llamada"
    )
    p.add_argument("carpeta")
    p.add_argument("--contiene", help="Filtra plantillas cuyo texto contenga la frase")
    p.add_argument("--rama", help="Rama taxonomica, p. ej. 02_seguro_vida")
    p.add_argument("--sujeto", help="varon | mujer | persona_juridica")

    e = sub.add_parser(
        "entregar", help="Verificador + guardia + restricciones, en una llamada"
    )
    e.add_argument("docx")
    e.add_argument("--caso", help="Numero de expediente para el scorecard")

    args = ap.parse_args(argv[1:])
    if args.orden == "preparar":
        return preparar(Path(args.carpeta), args.contiene, args.rama, args.sujeto)
    return entregar(Path(args.docx), args.caso)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
