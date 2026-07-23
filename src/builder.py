"""Constructor del .docx final (Reglas R-56, R-57, R-64, R-76).

Filosofía (R-56): **NUNCA generar desde cero**. Se clona una plantilla .docx
maestra preservando headers/footers/imágenes; se vacía el cuerpo y se inyecta
el nuevo texto con formato forzado vía funciones encapsuladas (R-76).

Las notas al pie se insertan como marcadores ``[[FN:...]]`` en el cuerpo; el
módulo ``footnote_injector`` las convierte en notas nativas vía win32com (R-71).
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Inches, Pt

# ---------------------------------------------------------------------------
# Constantes de formato (Reglas R-57, R-64)
# ---------------------------------------------------------------------------

FUENTE_CUERPO = "Arial Narrow"
TAM_CUERPO = Pt(11)
TAM_NOTAS = Pt(8)
TAM_INICIALES = Pt(8)

# Sangrías (R-64)
INDENT_ROMANOS = Inches(0)  # I., II. al margen
INDENT_NUMERALES_LEFT = Inches(0.39)  # 1., 2.
INDENT_NUMERALES_HANG = Inches(-0.39)
INDENT_INCISOS_HECHOS_LEFT = Inches(0.79)  # (i),(ii) en HECHOS, 2 cm
INDENT_INCISOS_HECHOS_HANG = Inches(-0.39)
INDENT_INCISOS_RESOL_LEFT = Inches(0.39)  # (i),(ii) en RESOLUTIVO, 1 cm
INDENT_INCISOS_RESOL_HANG = Inches(-0.39)
INDENT_META_LEFT = Inches(1.48)
INDENT_META_HANG = Inches(-1.48)


# ---------------------------------------------------------------------------
# Utilidades de bajo nivel (R-76: encapsulamiento obligatorio)
# ---------------------------------------------------------------------------


def _forzar_formato_parrafo(parrafo) -> None:
    """R-58 + R-76: fuerza SpaceBefore=0, SpaceAfter=0, LineSpacing=1.0."""
    pf = parrafo.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.0


def _add_run(parrafo, texto: str, *, bold: bool = False, size=TAM_CUERPO) -> Any:
    run = parrafo.add_run(texto)
    run.font.name = FUENTE_CUERPO
    # En python-docx, también hay que setear rFonts para que Arial Narrow aplique
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:ascii"), FUENTE_CUERPO)
    rFonts.set(qn("w:hAnsi"), FUENTE_CUERPO)
    rFonts.set(qn("w:cs"), FUENTE_CUERPO)
    run.font.size = size
    run.bold = bold
    return run


def _nuevo_parrafo(doc, *, align=WD_ALIGN_PARAGRAPH.JUSTIFY, left=None, hang=None) -> Any:
    p = doc.add_paragraph()
    p.alignment = align
    _forzar_formato_parrafo(p)
    pf = p.paragraph_format
    if left is not None:
        pf.left_indent = left
    if hang is not None:
        pf.first_line_indent = hang
    return p


def _limpiar_shd_highlight(parrafo) -> None:
    """R-62: limpia tags w:shd y w:highlight del parrafo XML."""
    pPr = parrafo._element.find(qn("w:pPr"))
    if pPr is not None:
        for tag in ("w:shd",):
            for elem in pPr.findall(qn(tag)):
                pPr.remove(elem)
    for run in parrafo.runs:
        rPr = run._element.find(qn("w:rPr"))
        if rPr is not None:
            for tag in ("w:shd", "w:highlight", "w:color"):
                for elem in rPr.findall(qn(tag)):
                    rPr.remove(elem)


def _vaciar_cuerpo(doc) -> None:
    """Elimina todos los párrafos y tablas del cuerpo, preservando headers/footers."""
    cuerpo = doc.element.body
    # Conservar sectPr (propiedades de sección al final)
    sectPr = cuerpo.find(qn("w:sectPr"))
    for hijo in list(cuerpo):
        if hijo is sectPr:
            continue
        cuerpo.remove(hijo)


# ---------------------------------------------------------------------------
# Construcción por secciones
# ---------------------------------------------------------------------------


def _construir_metadata(doc, borrador: dict[str, Any]) -> None:
    """R-18: metadata con sangría francesa, etiqueta y valor en negrita."""
    p = _nuevo_parrafo(
        doc,
        align=WD_ALIGN_PARAGRAPH.LEFT,
        left=INDENT_META_LEFT,
        hang=INDENT_META_HANG,
    )
    p.paragraph_format.tab_stops.add_tab_stop(Inches(1.18), WD_ALIGN_PARAGRAPH.LEFT)
    p.paragraph_format.tab_stops.add_tab_stop(Inches(1.48), WD_ALIGN_PARAGRAPH.LEFT)

    denunciantes = borrador.get("denunciante", "")
    denunciados = borrador.get("denunciados", [])
    if isinstance(denunciados, list):
        denun_texto = "; ".join(
            f"{d.get('razon_social','')} ({d.get('abreviatura','')})"
            if isinstance(d, dict)
            else str(d)
            for d in denunciados
        )
    else:
        denun_texto = str(denunciados)

    p2 = _nuevo_parrafo(doc, align=WD_ALIGN_PARAGRAPH.LEFT, left=INDENT_META_LEFT, hang=INDENT_META_HANG)
    p2.paragraph_format.tab_stops.add_tab_stop(Inches(1.18), WD_ALIGN_PARAGRAPH.LEFT)
    p2.paragraph_format.tab_stops.add_tab_stop(Inches(1.48), WD_ALIGN_PARAGRAPH.LEFT)
    _add_run(p2, "EXPEDIENTE\t:\t", bold=True)
    _add_run(p2, str(borrador.get("expediente", "")), bold=True)

    for etiqueta, valor in (
        ("DENUNCIANTE", denunciantes),
        ("DENUNCIADO", denun_texto),
        ("MATERIAS", "ADMISIÓN A TRÁMITE\rREQUERIMIENTO DE INFORMACIÓN"),
        ("RESOLUCIÓN", str(borrador.get("resolucion_numero", "1"))),
    ):
        pm = _nuevo_parrafo(doc, align=WD_ALIGN_PARAGRAPH.LEFT, left=INDENT_META_LEFT, hang=INDENT_META_HANG)
        pm.paragraph_format.tab_stops.add_tab_stop(Inches(1.18), WD_ALIGN_PARAGRAPH.LEFT)
        pm.paragraph_format.tab_stops.add_tab_stop(Inches(1.48), WD_ALIGN_PARAGRAPH.LEFT)
        _add_run(pm, f"{etiqueta}\t:\t", bold=True)
        _add_run(pm, str(valor), bold=True)


def _construir_hechos(doc, borrador: dict[str, Any]) -> None:
    """R-17, R-29: I. HECHOS en orden cronológico unificado."""
    p = _nuevo_parrafo(doc, align=WD_ALIGN_PARAGRAPH.LEFT, left=INDENT_ROMANOS)
    _add_run(p, "I. HECHOS", bold=True)

    hechos = borrador.get("hechos", [])
    if not isinstance(hechos, list):
        return
    for h in hechos:
        if not isinstance(h, dict):
            continue
        num = h.get("numeral", "")
        texto = h.get("texto", "")
        # Numeral principal (1., 2., ...)
        pn = _nuevo_parrafo(
            doc,
            align=WD_ALIGN_PARAGRAPH.JUSTIFY,
            left=INDENT_NUMERALES_LEFT,
            hang=INDENT_NUMERALES_HANG,
        )
        pn.paragraph_format.tab_stops.add_tab_stop(Inches(0.39), WD_ALIGN_PARAGRAPH.LEFT)
        _add_run(pn, f"{num}.\t", bold=True)
        _add_run(pn, texto, bold=False)
        # Subincisos (i), (ii)...
        for sub in h.get("subincisos", []):
            ps = _nuevo_parrafo(
                doc,
                align=WD_ALIGN_PARAGRAPH.JUSTIFY,
                left=INDENT_INCISOS_HECHOS_LEFT,
                hang=INDENT_INCISOS_HECHOS_HANG,
            )
            ps.paragraph_format.tab_stops.add_tab_stop(Inches(0.79), WD_ALIGN_PARAGRAPH.LEFT)
            _add_run(ps, f"{sub}\t") if False else _add_run(ps, sub)


def _construir_admision(doc, borrador: dict[str, Any]) -> None:
    """R-17, R-32: II. DE LA ADMISIÓN — cada imputación en párrafo numerado independiente."""
    p = _nuevo_parrafo(doc, align=WD_ALIGN_PARAGRAPH.LEFT, left=INDENT_ROMANOS)
    _add_run(p, "II. DE LA ADMISIÓN A TRÁMITE DE LA DENUNCIA", bold=True)

    admision = borrador.get("admision", [])
    if not isinstance(admision, list):
        return
    for item in admision:
        if not isinstance(item, dict):
            continue
        num = item.get("numeral", "")
        texto = item.get("texto", "")
        pn = _nuevo_parrafo(
            doc,
            align=WD_ALIGN_PARAGRAPH.JUSTIFY,
            left=INDENT_NUMERALES_LEFT,
            hang=INDENT_NUMERALES_HANG,
        )
        pn.paragraph_format.tab_stops.add_tab_stop(Inches(0.39), WD_ALIGN_PARAGRAPH.LEFT)
        _add_run(pn, f"{num}.\t", bold=True)
        _add_run(pn, texto)


def _construir_requerimientos(doc, borrador: dict[str, Any]) -> None:
    """R-17: III. REQUERIMIENTO DE INFORMACIÓN — desglosado por proveedor."""
    p = _nuevo_parrafo(doc, align=WD_ALIGN_PARAGRAPH.LEFT, left=INDENT_ROMANOS)
    _add_run(p, "III. REQUERIMIENTO DE INFORMACIÓN", bold=True)

    reqs = borrador.get("requerimientos", [])
    if not isinstance(reqs, list):
        return
    for req in reqs:
        if not isinstance(req, dict):
            continue
        # Encabezado proveedor
        enc = req.get("encabezado", "")
        if enc:
            pe = _nuevo_parrafo(
                doc,
                align=WD_ALIGN_PARAGRAPH.JUSTIFY,
                left=INDENT_NUMERALES_LEFT,
                hang=INDENT_NUMERALES_HANG,
            )
            _add_run(pe, enc, bold=True)
        # Items (i), (ii)...
        for item in req.get("items", []):
            pi = _nuevo_parrafo(
                doc,
                align=WD_ALIGN_PARAGRAPH.JUSTIFY,
                left=INDENT_INCISOS_HECHOS_LEFT,
                hang=INDENT_INCISOS_HECHOS_HANG,
            )
            _add_run(pi, str(item))


def _construir_resolutivo(doc, borrador: dict[str, Any]) -> None:
    """R-24: IV. RESOLUCIÓN — PRIMERO a DÉCIMO PRIMERO."""
    p = _nuevo_parrafo(doc, align=WD_ALIGN_PARAGRAPH.LEFT, left=INDENT_ROMANOS)
    _add_run(p, "IV. RESOLUCIÓN DE LA SECRETARÍA TÉCNICA", bold=True)

    res = borrador.get("resolutivo", {})
    if not isinstance(res, dict):
        return
    # Orden canónico CC1
    orden = [
        "primero", "segundo", "tercero", "cuarto", "quinto", "sexto",
        "setimo", "octavo", "noveno", "decimo", "decimo_primero",
    ]
    for clave in orden:
        texto = res.get(clave, "")
        if not texto:
            continue
        # Línea en blanco ANTES de cada resolutivo (R-59: solo entre grandes bloques)
        _nuevo_parrafo(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        pr = _nuevo_parrafo(
            doc,
            align=WD_ALIGN_PARAGRAPH.JUSTIFY,
            left=INDENT_NUMERALES_LEFT,
            hang=INDENT_NUMERALES_HANG,
        )
        pr.paragraph_format.tab_stops.add_tab_stop(Inches(0.39), WD_ALIGN_PARAGRAPH.LEFT)
        # Detectar el "PRIMERO:", "SEGUNDO:" al inicio y ponerlo en bold
        mayuscula = clave.upper().replace("_", " ")
        if texto.strip().startswith(mayuscula):
            # Separar la etiqueta del resto
            resto = texto[len(mayuscula):].lstrip(":").lstrip()
            _add_run(pr, f"{mayuscula}:\t", bold=True)
            _add_run(pr, resto)
        else:
            etiqueta = {
                "primero": "PRIMERO", "segundo": "SEGUNDO", "tercero": "TERCERO",
                "cuarto": "CUARTO", "quinto": "QUINTO", "sexto": "SEXTO",
                "setimo": "SÉTIMO", "octavo": "OCTAVO", "noveno": "NOVENO",
                "decimo": "DÉCIMO", "decimo_primero": "DÉCIMO PRIMERO",
            }.get(clave, mayuscula)
            _add_run(pr, f"{etiqueta}:\t", bold=True)
            _add_run(pr, texto)


def _construir_iniciales(doc, borrador: dict[str, Any]) -> None:
    """R-54: iniciales finales en tamaño 8."""
    _nuevo_parrafo(doc)
    p = _nuevo_parrafo(doc, align=WD_ALIGN_PARAGRAPH.RIGHT)
    _add_run(p, borrador.get("iniciales", "LGP/JCQ"), size=TAM_INICIALES)


def _inyectar_notas_markers(doc, borrador: dict[str, Any]) -> None:
    """R-71: inserta marcadores [[FN:...]] en el primer párrafo de Hechos.

    El módulo footnote_injector los convierte en notas nativas vía win32com.
    En Linux/Mac queda como texto editable.
    """
    notas = borrador.get("notas_pie", [])
    if not isinstance(notas, list) or not notas:
        return

    # Anclar al final del primer párrafo de hechos (lo más simple y robusto)
    # Buscar el primer párrafo cuyo texto contenga "I. HECHOS" o empiece con "1."
    parrafo_ancla = None
    for p in doc.paragraphs:
        if "I. HECHOS" in p.text or p.text.strip().startswith("1."):
            parrafo_ancla = p
            break
    if parrafo_ancla is None and doc.paragraphs:
        parrafo_ancla = doc.paragraphs[0]
    if parrafo_ancla is None:
        return

    # Añadir los marcadores al final del párrafo ancla
    # (se convertirán a notas reales; el texto base del párrafo se conserva)
    marcadores = "".join(
        f"[[FN:{(n.get('texto','') if isinstance(n, dict) else str(n)).strip()}]]"
        for n in notas
    )
    if parrafo_ancla.runs:
        # Append al último run para no romper formato
        parrafo_ancla.runs[-1].text += marcadores
    else:
        _add_run(parrafo_ancla, marcadores)


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------


def construir_doc(
    borrador: dict[str, Any],
    plantilla_path: str | Path,
    salida_path: str | Path,
    *,
    inyectar_notas: bool = True,
) -> Path:
    """Construye el .docx final a partir del borrador JSON.

    1. Abre la plantilla (R-56).
    2. Vacía el cuerpo preservando headers/footers.
    3. Inyecta texto con formato (R-57, R-64).
    4. Inserta marcadores de notas al pie (R-71).
    5. Limpia resaltados y shd (R-62).
    6. Guarda.

    La conversión de marcadores a notas nativas requiere win32com (Word). Esa
    parte la orquesta ``app.generar_resolucion`` llamando a ``footnote_injector``.
    """
    plantilla_path = Path(plantilla_path)
    salida_path = Path(salida_path)
    salida_path.parent.mkdir(parents=True, exist_ok=True)

    if not plantilla_path.exists():
        raise FileNotFoundError(
            f"Plantilla maestra no encontrada: {plantilla_path}\n"
            "Coloca una plantilla .docx en templates/ o configura settings.json."
        )

    doc = Document(str(plantilla_path))
    _vaciar_cuerpo(doc)

    # Encabezado institucional NO se toca (R-22). Sólo construimos el cuerpo.

    # Fecha (R-55)
    fecha = borrador.get("fecha", "Lima, 20 de abril de 2026")
    pf = _nuevo_parrafo(doc, align=WD_ALIGN_PARAGRAPH.LEFT)
    _add_run(pf, fecha)

    # Metadata (R-18)
    _construir_metadata(doc, borrador)

    # Línea separadora
    _nuevo_parrafo(doc)

    # Secciones
    _construir_hechos(doc, borrador)
    _construir_admision(doc, borrador)
    _construir_requerimientos(doc, borrador)
    _construir_resolutivo(doc, borrador)

    # Iniciales (R-54)
    _construir_iniciales(doc, borrador)

    # Marcadores de notas al pie (R-71)
    if inyectar_notas:
        _inyectar_notas_markers(doc, borrador)

    # R-62: limpieza de resaltados a nivel XML
    for p in doc.paragraphs:
        _limpiar_shd_highlight(p)

    doc.save(str(salida_path))
    return salida_path
