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
    python scripts/admisorio.py previsualizar <generado.docx> [--contra <plantilla.docx>]
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

import comprobar_anclaje  # noqa: E402
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


def _exigir_anclaje() -> None:
    """Puerta de R-142: sin anclaje no se prepara nada."""
    problemas = comprobar_anclaje.comprobar(estricto=False)
    if problemas:
        print(comprobar_anclaje.REMEDIO.replace("{raiz}", f"{str(RAIZ):<70}"))
        for x in problemas:
            print(f"  - {x}")
        raise SystemExit(2)


def preparar(
    carpeta: Path,
    contiene: str | None,
    rama: str | None,
    sujeto: str | None,
    denunciados: int | None = None,
    subtipo: str | None = None,
) -> int:
    _exigir_anclaje()
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

    # Inventario de lo que el USUARIO entrego: todo documento nuevo que aparezca
    # despues (una cedula, un escrito) lo fabrico el agente, y `entregar` lo
    # rechaza. Medido en el Exp. 2898-2026: el agente creo una «CEDULAS.docx»
    # con el RUC de la aseguradora como numero de casilla.
    inv = carpeta / "_INVENTARIO.json"
    if not inv.exists():
        import hashlib

        inv.write_text(
            json.dumps(
                {
                    p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sorted(carpeta.iterdir())
                    if p.is_file() and not p.name.startswith("_")
                },
                ensure_ascii=False,
                indent=1,
            ),
            encoding="utf-8",
        )

    extraer_expediente.informe(carpeta, volcar=True)
    inventario, _dossier = extraer_expediente.triaje(carpeta)
    sin_texto = sum(len(i["sin_texto"]) for i in inventario)

    _titulo("FECHAS DE FIRMA DIGITAL (fecha de los escritos de parte)")
    for pdf in sorted(carpeta.glob("*.pdf")):
        firmas = extraer_expediente.firmas_digitales(pdf)
        print("  %s" % pdf.name)
        for fecha, motivo in firmas or [("sin firma digital", "")]:
            print("      %-26s %s" % (fecha, motivo))
    print("  Escrito de parte: su fecha es la de la firma de mesa de partes (Fedatario).")
    print("  Documento de Indecopi: la fecha de emision escrita en su texto, no la de firma.")

    _titulo("LECTURA VISUAL - CAPTURA COMPLETA DE CADA PAGINA (R-137)")
    # Mandato del instructor (23/09/2026): cada pagina se mira ENTERA como imagen,
    # tenga o no texto seleccionable. El texto embebido omite sellos, firmas,
    # resaltados, tachados y todo lo que no esta en la capa de texto, y no dice
    # nada de formato, estilo, alineacion ni encuadre. Cero OCR.
    paginas = extraer_expediente.renderizar_paginas(carpeta)
    if not paginas and any(carpeta.glob("*.pdf")):
        print("  FALLA  no se pudieron renderizar las paginas (falta PyMuPDF).")
        return 4
    import formato_paginas

    formato = formato_paginas.escribir(carpeta)
    lectura = carpeta / "_LECTURA.md"
    if not lectura.exists():
        filas = "\n".join(
            "| %s | %s | %d | | | |" % (png.name, pdf, n) for pdf, n, png in paginas
        )
        lectura.write_text(
            "# Lectura visual del expediente (R-137)\n\n"
            "Una fila por pagina. Abre cada PNG de `_paginas/` y anota con TUS palabras\n"
            "el tipo de documento y lo que VES: fechas, montos, numeros, sellos, firmas,\n"
            "resaltados y todo lo que no este en la capa de texto. Copiar el texto\n"
            "embebido no cuenta como lectura: `entregar` lo rechaza.\n"
            "En «Formato que vi» anota la forma de la hoja (letra, negritas, subrayados,\n"
            "alineacion, encabezado, pie, sellos, firma); `_FORMATO.md` trae las medidas.\n\n"
            "| Imagen | PDF | Pagina | Tipo de documento | Lo que vi | Formato que vi |\n"
            "|---|---|---|---|---|---|\n" + filas + "\n",
            encoding="utf-8",
        )
    print(
        "  %d paginas en _paginas/ y plantilla de constancia en %s."
        % (len(paginas), lectura.name)
    )
    if formato:
        print("  Formato medido de cada pagina (sin OCR) en %s." % formato.name)

    _titulo("FICHA DEL CASO (comandos exactos, firmas, proveedores, tipificacion)")
    import ficha_caso

    ficha = ficha_caso.escribir(carpeta)
    print("  %s y %s/ (paginas de dos en dos)." % (ficha.name, "_hojas"))
    print("  LEE SOLO _FICHA.md: no uses -h ni abras scripts o JSON del repositorio.")

    _titulo("FECHA DE LA REMESA (D2)")
    import config_sistema

    if config_sistema.fecha_emision():
        print("  Lima, %s  (config/remesa.json)" % config_sistema.fecha_emision())
    else:
        print(
            "  SIN FIJAR. Pregunta la fecha de emision al instructor ANTES de redactar"
        )
        print(
            '  y fijala con: python scripts/config_sistema.py --fecha "D de mes de AAAA"'
        )

    _titulo("PLANTILLA BASE - CANDIDATAS DEL INDICE (F4)")
    fichas = json.loads(INDICE.read_text(encoding="utf-8"))
    candidatas = fichas
    if rama:
        candidatas = [f for f in candidatas if rama.lower() in f["rama"].lower()]
    if sujeto:
        candidatas = [
            f for f in candidatas if sujeto.lower() == f["sujeto_tipo"].lower()
        ]
    if denunciados:
        candidatas = [
            f
            for f in candidatas
            if (
                f.get("denunciados", {}).get("n", 0) >= 3
                if denunciados >= 3
                else f.get("denunciados", {}).get("n", 0) == denunciados
            )
        ]
    if subtipo:
        candidatas = [f for f in candidatas if subtipo in f.get("subtipos", [])]
    elif fichas and "subtipos" in fichas[0]:
        candidatas = [f for f in candidatas if not f.get("subtipos")]
    candidatas.sort(
        key=lambda f: (not f.get("apta_como_base", False), len(f.get("falsadores", [])))
    )
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
        print(
            "    %s %-22s %-30s ddos=%s %-24s %s"
            % (
                "APTA" if f.get("apta_como_base") else "    ",
                f["rama"],
                f["materia"][:30],
                f.get("denunciados", {}).get("n", "?"),
                f["sujeto_tipo"][:24],
                f["archivo"],
            )
        )
    if len(candidatas) > 10:
        print("    ... y %d mas (afina el filtro)" % (len(candidatas) - 10))

    _titulo("SIGUIENTE PASO - UNA SOLA LLAMADA MAS")
    print("  1. Redactar con el constructor del caso sobre la plantilla elegida.")
    print("  2. Entregar:  python scripts/admisorio.py entregar <generado.docx>")
    print(
        "  Lectura visual OBLIGATORIA de las %d paginas (captura completa en _paginas/),"
        % sum(i["paginas"] for i in inventario)
    )
    print(
        "  tengan o no capa de texto. Cero OCR. %d no tienen texto que contrastar."
        % sin_texto
    )
    print("  Llena _LECTURA.md: una fila por pagina con lo que viste.")
    print("  Prohibido generar PDF (R-125). El entregable es el .docx.")
    print("  Preparacion completa en %.1f s y 1 llamada." % (time.time() - t0))
    return 0


def _lecturas_copiadas(carpeta: Path, vistas: dict[str, str]) -> list[str]:
    """PNG cuya fila de _LECTURA.md reproduce el texto embebido de su pagina.

    Se compara lo anotado con la capa de texto normalizada: si 60 o mas
    caracteres seguidos de la anotacion estan literalmente en la capa, la fila se
    copio del volcado y no de la imagen.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return []

    def norm(t: str) -> str:
        return re.sub(r"\s+", " ", t).strip().lower()

    copiadas = []
    for pdf in sorted(carpeta.glob("*.pdf")):
        try:
            doc = fitz.open(str(pdf))
        except Exception:
            continue
        with doc:
            for pagina in doc:
                png = "%s_p%02d.png" % (
                    pdf.stem[:40].replace(" ", "_"),
                    pagina.number + 1,
                )
                vista = norm(vistas.get(png, ""))
                capa = norm(pagina.get_text())
                if len(vista) >= 60 and any(
                    vista[i : i + 60] in capa for i in range(0, len(vista) - 59, 20)
                ):
                    copiadas.append(png)
    return copiadas


PERMITIDOS_CASO = {
    "_INVENTARIO.json",
    "_LECTURA.md",
    "_paginas",
    "_texto_expediente.txt",
    "_CASO.json",
    "_SIMILARES.md",
    "mapa.json",
    "_FICHA.md",
    "_hojas",
    "_FORMATO.md",
    "_vista",
}


def _control_nota_denuncia(caso: dict, z) -> list[str]:
    """Nota al pie de la denuncia (instructor, 23/09/2026): SOLO cuando la
    denuncia llego de otro organo por MEMORANDUM o Documento de Traslado, con el
    numero, la fecha de emision del documento y la fecha de recibido en CC1.
    Denuncia presentada directamente: NINGUNA nota sobre su presentacion."""
    if not caso:
        return []
    if "traslado" not in caso:
        return [
            "_CASO.json sin 'traslado': null si la denuncia se presento en CC1; "
            '{"documento": "MEMORANDUM 001950-2025-PS1/INDECOPI", "fecha": "...", "recibida": "..."} '
            "si llego derivada (solo si el usuario entrego ese documento)"
        ]
    notas = verificar_admisorio.notas_al_pie(z)
    tr = caso["traslado"]
    if tr:
        esperada = (
            "Denuncia remitida a esta Comisión mediante %s de fecha %s, recibida el %s."
            % (
                tr.get("documento", "?"),
                tr.get("fecha", "?"),
                tr.get("recibida", "?"),
            )
        )
        # Casos particulares de las plantillas (instructor, 23/09/2026): denuncia
        # desacumulada de un expediente previo, o recibida por Hoja de Tramite.
        # `nota` da el texto literal, pero debe contener los tres datos
        # declarados: nada que no venga de un documento del expediente.
        if tr.get("nota"):
            esperada = tr["nota"].strip()
            if not esperada.startswith(
                (
                    "Denuncia remitida a esta Comisión mediante",
                    "Denuncia desacumulada mediante",
                )
            ) or not all(
                tr.get(k) and tr[k] in esperada
                for k in ("documento", "fecha", "recibida")
            ):
                return [
                    "_CASO.json traslado.nota debe seguir la forma de las plantillas y contener documento, fecha y recibida"
                ]
        if not notas or notas[0] != esperada:
            return [
                "la nota al pie 1 debe ser exactamente: «%s» (hay: «%s»)"
                % (esperada, (notas[0] if notas else "")[:120])
            ]
        return []
    malas = [n for n in notas if n.startswith("Denuncia") or "Mesa de Partes" in n]
    if malas:
        return [
            "denuncia presentada en CC1 (traslado null): prohibida toda nota sobre su presentacion: «%s»"
            % malas[0][:120]
        ]
    return []


def _control_iniciales(textos: list[str]) -> list[str]:
    ini = json.loads((RAIZ / "config/firmas.json").read_text(encoding="utf-8")).get("iniciales")
    if ini and ini not in [t.strip() for t in textos]:
        return ["las iniciales de redaccion deben ser «%s» (config/firmas.json)" % ini]
    return []


def _control_reclamos(carpeta: Path, textos: list[str], caso: dict) -> list[str]:
    """Si el expediente cita reclamos numerados y el admisorio no imputa ninguno
    (88.1 o articulo 24), se detiene: en el Exp. 2898-2026 el agente paso de
    agrupar tres reclamos en una imputacion a omitirlos todos. Una imputacion
    por reclamo; si de verdad no corresponde, se declara en _CASO.json
    («reclamos_no_imputados»: motivo)."""
    txt = carpeta / "_texto_expediente.txt"
    if not txt.exists() or caso.get("reclamos_no_imputados"):
        return []
    numeros = set(re.findall(r"[Rr]eclamo[s]?\s*(?:N\.?\s*[°º]?\s*)?(\d{4,})", txt.read_text(encoding="utf-8", errors="replace")))
    imputa = any(
        t.strip().startswith("Presunta infracci") and ("88.1" in t or "artículo 24" in t)
        for t in textos
    )
    if numeros and not imputa:
        return [
            "el expediente cita reclamos (%s) y no hay imputacion por 88.1 ni articulo 24: "
            "una imputacion por reclamo, o declara en _CASO.json «reclamos_no_imputados» con el motivo"
            % ", ".join(sorted(numeros)[:4])
        ]
    return []


def _copiar_a_origen(docx: Path) -> None:
    """El Word entregable va a la carpeta donde el usuario tiene los documentos."""
    import shutil

    caso_p = docx.parent / "_CASO.json"
    if not caso_p.exists():
        return
    destino = json.loads(caso_p.read_text(encoding="utf-8")).get("carpeta_origen")
    if not destino:
        return
    d = Path(destino)
    if not d.is_dir():
        print("  AVISO  carpeta_origen no existe: %s" % d)
        return
    if d.resolve() == docx.parent.resolve():
        return
    shutil.copy2(docx, d / docx.name)
    print("  Copiado a la carpeta del usuario: %s" % (d / docx.name))


def _norm_fecha(t: str) -> str:
    """«setiembre» y «septiembre» son la misma fecha (R-161)."""
    return t.replace("septiembre", "setiembre")


def _sin_enumerador(t: str) -> str:
    """El enumerador literal del parrafo («1.», «2)») es maquetacion, no texto."""
    return re.sub(r"^\s*\d+[.)]\s*", "", t)


def _control_fechas_escritos(caso: dict, textos: list[str]) -> list[str]:
    """Las fechas van en HECHOS y en la admision, cualquiera sea su ordinal."""
    from migraciones.traslado_denuncia import cita_admision

    apertura = _norm_fecha(
        next((t for t in textos if _sin_enumerador(t).strip().startswith("Mediante")), "")
    )
    admision = _norm_fecha(next((c for t in textos if (c := cita_admision(t))), ""))
    fallos = []
    for e in caso.get("escritos", []):
        f = _norm_fecha(e.get("fecha", ""))
        if f and f not in apertura:
            fallos.append(
                "el escrito '%s' del %s no se cita en la apertura de HECHOS"
                % (e.get("tipo", "?"), f)
            )
        if f and f not in admision:
            fallos.append(
                "el escrito '%s' del %s no se cita en el ordinal de admision"
                % (e.get("tipo", "?"), f)
            )
    return fallos


def _control_del_caso(docx: Path) -> list[str]:
    """Controles que dependen del caso y no solo del .docx (supervision 2898-2026).

    - integridad: el agente no modifico el sistema;
    - _CASO.json: existe y declara los escritos y los denunciados definitivos;
    - todos los escritos (denuncia, subsanacion, complementarios) se citan con su
      fecha en la apertura de HECHOS y en el ordinal que admite la denuncia;
    - _SIMILARES.md: 10 plantillas REALES del indice, cada una justificada;
    - ningun documento del expediente fabricado (cedulas, escritos).
    """

    import integridad
    import similares

    carpeta = docx.parent
    fallos: list[str] = []
    _titulo("CONTROLES DEL CASO")
    mods = integridad.comprobar()
    if mods:
        fallos.append(
            "el sistema fue modificado (%s): reinstala y REPORTA el error en vez de editar"
            % ", ".join(mods[:3])
        )
    caso_p = carpeta / "_CASO.json"
    if not caso_p.exists():
        fallos.append("falta _CASO.json (ver scripts/similares.py -h)")
        caso = {}
    else:
        caso = json.loads(caso_p.read_text(encoding="utf-8"))
    doc, _s, _z = verificar_admisorio.leer_documento(str(docx))
    textos = [p.texto for p in doc]
    fallos += _control_fechas_escritos(caso, textos)
    fallos += similares.justificacion_completa(carpeta)
    sim = carpeta / "_SIMILARES.md"
    if sim.exists():
        reales = {f["archivo"] for f in json.loads(INDICE.read_text(encoding="utf-8"))}
        citadas = re.findall(r"(TPL_[A-Z0-9_]+\.docx)", sim.read_text(encoding="utf-8"))
        falsas = sorted({c for c in citadas if c not in reales})
        if falsas:
            fallos.append(
                "_SIMILARES.md cita plantillas que NO existen: %s"
                % ", ".join(falsas[:4])
            )
    fallos += _control_nota_denuncia(caso, _z)
    fallos += _control_iniciales(textos)
    fallos += _control_reclamos(carpeta, textos, caso)
    if caso and not caso.get("carpeta_origen"):
        fallos.append(
            "_CASO.json sin 'carpeta_origen' (la carpeta donde el usuario tiene los documentos)"
        )
    inv = carpeta / "_INVENTARIO.json"
    originales = json.loads(inv.read_text(encoding="utf-8")) if inv.exists() else {}
    if not inv.exists():
        fallos.append("falta _INVENTARIO.json: ejecuta primero 'admisorio.py preparar'")
    # Lista CERRADA (instructor, 23/09/2026: «tiene que hacer lo que se hace»).
    # En la carpeta del caso solo existen los documentos del usuario, lo que
    # producen los scripts y UN entregable. Cualquier otra cosa (cedulas,
    # borradores, scripts propios, copias) la fabrico el agente.
    for p in carpeta.iterdir():
        if (
            p.name in originales
            or p.name in PERMITIDOS_CASO
            or p.resolve() == docx.resolve()
        ):
            continue
        if p.name.startswith("~$"):
            fallos.append(
                "'%s': el agente abrio Word; prohibido (se construye y verifica con scripts)"
                % p.name
            )
        else:
            fallos.append(
                "archivo no permitido en la carpeta del caso: %s (prohibido fabricar documentos, cedulas, borradores o scripts)"
                % p.name
            )
    if not re.fullmatch(r"ADM \d{3,5}-\d{4} R\d+\.docx", docx.name):
        fallos.append(
            "el entregable se llama 'ADM <EXPEDIENTE> R<N>.docx', no '%s'" % docx.name
        )
    for f in fallos:
        print("  FALLA  " + f)
    if not fallos:
        print(
            "  OK     integridad, _CASO.json, escritos citados, 10 similares reales y justificadas, sin documentos fabricados."
        )
    return fallos


def entregar(docx: Path, caso: str | None, recepcion: str | None = None) -> int:
    t0 = time.time()
    docx = docx.resolve()
    fallas: list[str] = []

    if not verificar_admisorio.verificar(str(docx)):
        fallas.append("verificar_admisorio: NO APTO")

    fallas += _control_del_caso(docx)

    _titulo("GUARDIA DE DATOS PERSONALES")
    fugas = guardia_admisorio.revisar([str(docx)])
    if fugas:
        print("  El documento NO se commitea (contiene datos del expediente):")
        for f in fugas:
            print("    - %s" % f)
    else:
        print("  Sin fuga detectada.")

    _titulo("LECTURA VISUAL DE CADA PAGINA (R-137)")
    # La pasada de vision no se puede comprobar mirando el .docx, y la traza del
    # agente no sirve con varios casos en paralelo: `conversacion_mas_reciente()`
    # devuelve la de otro expediente. Medido el 14/09/2026: los tres agentes de la
    # segunda tanda entregaron con CERO toques a imagen y nadie lo habria sabido.
    # Asi que la evidencia la deja el propio agente, por escrito y por pagina.
    lectura = docx.parent / "_LECTURA.md"
    paginas = sorted((docx.parent / "_paginas").glob("*.png"))
    if not lectura.exists():
        fallas.append(
            "no hay _LECTURA.md: sin constancia de la lectura con Lens no hay entrega (R-137)"
        )
        print("  FALLA  falta %s" % lectura.name)
        print("         Escribe una linea por pagina con lo que viste en ella.")
    else:
        texto_lectura = lectura.read_text(encoding="utf-8", errors="replace")
        vistas = {}
        for linea in texto_lectura.splitlines():
            celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
            if len(celdas) >= 5 and celdas[0].endswith(".png"):
                vistas[celdas[0]] = celdas[4]
        faltan = [p.name for p in paginas if not vistas.get(p.name)]
        copiadas = _lecturas_copiadas(docx.parent, vistas)
        if copiadas:
            fallas.append(
                "_LECTURA.md copia el texto embebido en %d pagina(s): eso no es lectura visual (R-137)"
                % len(copiadas)
            )
            print(
                "  FALLA  lectura copiada del texto embebido: %s"
                % ", ".join(copiadas[:6])
            )
        if not paginas and any(docx.parent.glob("*.pdf")):
            fallas.append(
                "no hay capturas en _paginas/: ejecuta primero 'admisorio.py preparar' (R-137)"
            )
            print("  FALLA  sin capturas de pagina.")
        if faltan:
            fallas.append(
                "_LECTURA.md no cubre %d de %d paginas (R-137)"
                % (len(faltan), len(paginas))
            )
            print("  FALLA  sin constancia de lectura: %s" % ", ".join(faltan[:6]))
        else:
            print("  OK     constancia de lectura de las %d paginas." % len(paginas))

    _titulo("RESTRICCIONES DURAS DEL PLAN")
    # Solo cuenta como PDF del pipeline el que nace del propio entregable: mismo
    # nombre, o escrito despues del .docx. Los PDF del expediente son la entrada.
    corte = docx.stat().st_mtime
    pdfs = [
        p.name
        for p in docx.parent.glob("*.pdf")
        if p.stem == docx.stem or p.stat().st_mtime > corte
    ]
    # Scratch en la raiz del repositorio: sintoma de que el documento se construyo
    # improvisando un script en vez de usar construir_admisorio.py (R-139). En el
    # Exp. 3122-2026 fueron cinco, y cuatro de ellos peleandose con Word por COM.
    scratch = sorted(p.name for p in RAIZ.glob("scratch*.py"))
    if scratch:
        fallas.append(
            "scratch en la raiz del repositorio: %s (R-139)" % ", ".join(scratch)
        )
        print("  FALLA  scratch sin borrar: %s" % ", ".join(scratch))
        print("         Se construye con scripts/construir_admisorio.py, no a mano.")
    else:
        print("  OK     sin scratch en la raiz del repositorio.")

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

    _titulo("AUDITORIA DE FONDO: TODO DATO ANCLADO")
    import auditar_admisorio  # import diferido

    if auditar_admisorio.auditar(docx.parent, False) != 0:
        fallas.append("hay datos del admisorio sin ancla en el expediente")

    if recepcion:
        _titulo("PLAZO DE 20 DIAS HABILES (D3) - SE INFORMA, NO VA EN LA RESOLUCION")
        import plazos

        informe = plazos.informe(plazos.leer_fecha(recepcion), plazos.date.today())
        for linea in informe.splitlines():
            print("  " + linea)

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
    _copiar_a_origen(docx)
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
    p.add_argument(
        "--sujeto",
        help="varon | mujer | sucesion_intestada | herederos_no_acreditados | conyuges | persona_juridica | asociacion | varios | mixto",
    )
    p.add_argument(
        "--denunciados", type=int, help="Numero real de denunciados (1, 2, 3 = 3 o mas)"
    )
    p.add_argument(
        "--subtipo",
        help="confidencialidad | inclusion_de_oficio (sin esto se excluyen)",
    )

    v = sub.add_parser(
        "previsualizar", help="Cada pagina del Word como imagen en _vista/ (con --contra, junto a la plantilla)"
    )
    v.add_argument("docx")
    v.add_argument("--contra", help="Plantilla base, para verla pagina a pagina al lado")

    e = sub.add_parser(
        "entregar", help="Verificador + guardia + restricciones, en una llamada"
    )
    e.add_argument("docx")
    e.add_argument("--caso", help="Numero de expediente para el scorecard")
    e.add_argument(
        "--recepcion",
        help="Fecha de recepcion en CC1 (DD/MM/AAAA) para informar el plazo de 20 dias habiles",
    )

    args = ap.parse_args(argv[1:])
    if args.orden == "preparar":
        return preparar(
            Path(args.carpeta),
            args.contiene,
            args.rama,
            args.sujeto,
            args.denunciados,
            args.subtipo,
        )
    if args.orden == "previsualizar":
        import previsualizar

        contra = Path(args.contra) if args.contra else None
        if contra and not contra.is_absolute():
            contra = RAIZ / contra
        return previsualizar.main(
            ["previsualizar", str(args.docx)] + (["--contra", str(contra)] if contra else [])
        )
    return entregar(Path(args.docx), args.caso, args.recepcion)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
