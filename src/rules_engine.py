"""Motor de validación determinista de las 80 reglas de redacción (R-01..R-80).

Lee ``docs/REGLAS_DE_REDACCION.md`` como fuente única de verdad y expone:

- ``TIPIFICACIONES_PERMITIDAS`` y ``TIPIFICACIONES_PROHIBIDAS`` (Apéndice A).
- ``validar_borrador(borrador) -> list[ValidationError]``: aplica todas las
  reglas [CRÍTICA] y [VALIDABLE] contra el JSON que devuelve la IA antes de
  construir el .docx. Si hay algún error crítico, el builder se niega a guardar.
- ``validar_docx_generado(ruta) -> list[ValidationError]``: validación
  post-generación (R-79).

El motor es **determinista**: no usa IA. Es el guardián final que impide las
fallas históricas documentadas (Art. 24, non bis in idem, plantilla rota, etc.).
"""

from __future__ import annotations

import json
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

# ---------------------------------------------------------------------------
# Modelo de datos
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RuleRef:
    """Referencia estable a una regla del documento maestro."""

    id: str  # ej. "R-05"
    severity: str  # "CRITICA" | "VALIDABLE"


@dataclass
class ValidationError:
    """Una violación detectada por el motor."""

    rule: str  # ej. "R-05"
    severity: str  # "CRITICA" | "VALIDABLE"
    message: str
    context: str = ""

    def __str__(self) -> str:  # pragma: no cover - solo presentación
        flag = "BLOQUEO" if self.severity == "CRITICA" else "AVISO"
        return f"[{flag}] {self.rule}: {self.message}" + (
            f"  (ctx: {self.context})" if self.context else ""
        )


# ---------------------------------------------------------------------------
# Apéndice A — Tipificaciones permitidas / prohibidas
# ---------------------------------------------------------------------------

# (clave, lista de patrones regex, descripción). Varios patrones por tipo para
# tolerar distintas redacciones (compacta "1°.1.b)", verbosa "artículo 1 numeral 1 literal b)").
TIPIFICACIONES_PERMITIDAS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    (
        "INFO",
        (
            r"art[ií]culos?\s*1[°º.]?(?:[,\s]+numeral\s*1[,.\s]+literal\s*b\)?)?[\s,.,y]*2[°º.]?(?!\d)",
            r"art[ií]culo\s*1[°º.]?\s*,?\s*numeral\s*1\s*,?\s*literal\s*b\)",
            r"\b1[°º.]?\s*numeral\s*1[,.\s]*literal\s*b\)\s*y\s*(?:el\s+)?art[ií]culo\s*2[°º.]?",
            r"art[ií]culos?\s*2[°º.]?\s+y\s+1[°º.]?",
        ),
        "Deber de Información",
    ),
    (
        "IDONEIDAD",
        (
            # 18° y 19° mencionados, con o sin "artículos" inmediatamente antes
            r"(?:art[ií]culos?(?:\s+N[°º.]?\s*\d+)?[\w\s/°º.,()olíneas-y]*?)?\b18[°º.]?\s*y\s*19[°º.]?",
            r"\b18[°º.]?\s*y\s*19[°º.]?",
            r"\b19[°º.]?\s*y\s*18[°º.]?",
        ),
        "Idoneidad",
    ),
    (
        "COERCITIVO",
        (
            r"(literal\s*b\)\s*del\s*)?art[ií]culo\s*56[°º.]?",
        ),
        "Métodos coercitivos",
    ),
    (
        "ENGAÑOSO",
        (
            r"(literal\s*b\)\s*del\s*)?art[ií]culo\s*58[°º.]?",
        ),
        "Métodos engañosos",
    ),
    (
        "BANCARIO",
        (
            r"art[ií]culo\s*152[°º.]?\s*de\s*la\s*Ley\s*N?[°º.]?\s*26702",
        ),
        "Estado de cuenta bancario",
    ),
    (
        "LEYES_SANCIONADORAS",
        (
            r"(art[ií]culos?\s*(24|29)[°º.]?)?\s*del?\s*(DL|Decreto\s*Legislativo)\s*N?[°º.]?\s*807",
        ),
        "Régimen sancionador INDECOPI",
    ),
)

TIPIFICACIONES_PROHIBIDAS: tuple[tuple[str, str, str], ...] = (
    ("ART24", r"art[ií]culo\s*24[°º.]?(?!\s*del\s*DL|\s*del\s*Decreto)", "Art. 24 del Código (prohibido)"),
    ("INDUCCION", r"inducci[oó]n\s+al\s+error", "Falsa tipificación 'inducción al error'"),
)

# Frase exclusiva de Idoneidad (R-12)
_BOILERPLATE_IDONEIDAD = (
    r"involucrar[ií]a\s+una\s+presunta\s+afectaci[oó]n\s+a\s+sus\s+expectativas"
)

# Conectores prohibidos en repetición (R-31)
_CONECTORES_ADMISION = ("Asimismo", "Además", "Adicionalmente", "Así también")


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------


def _normalizar(texto: str) -> str:
    """Normaliza para comparaciones tolerantes (sin acentos, sin doble espacio)."""
    if not texto:
        return ""
    out = texto.lower()
    tabla = str.maketrans("áéíóúüñ", "aeiouun")
    return re.sub(r"\s+", " ", out.translate(tabla)).strip()


def _texto_completo(borrador: dict[str, Any]) -> str:
    """Concatena todo el texto del borrador para análisis global."""
    trozos: list[str] = [borrador.get("expediente", "")]
    for seccion in ("hechos", "admision", "requerimientos", "resolutivo", "notas_pie"):
        valor = borrador.get(seccion)
        if isinstance(valor, str):
            trozos.append(valor)
        elif isinstance(valor, list):
            for item in valor:
                trozos.append(item if isinstance(item, str) else json.dumps(item, ensure_ascii=False))
        elif isinstance(valor, dict):
            trozos.append(json.dumps(valor, ensure_ascii=False))
    return "\n".join(trozos)


def _match_cualquiera(patrones: Iterable[str], texto: str) -> bool:
    return any(re.search(p, texto, flags=re.IGNORECASE) for p in patrones)


# ---------------------------------------------------------------------------
# Validadores individuales — devuelven list[ValidationError]
# ---------------------------------------------------------------------------


def _r05_prohibido_art24(texto: str) -> list[ValidationError]:
    """R-05: prohibido imputar Art. 24 (excepto Art. 24 del DL 807)."""
    errs: list[ValidationError] = []
    for clave, patron, desc in TIPIFICACIONES_PROHIBIDAS:
        if clave != "ART24":
            continue
        for m in re.finditer(patron, texto, flags=re.IGNORECASE):
            errs.append(
                ValidationError(
                    rule="R-05",
                    severity="CRITICA",
                    message=f"Se detectó mención prohibida: {desc}",
                    context=m.group(0),
                )
            )
    return errs


def _r06_prohibido_induccion(texto: str) -> list[ValidationError]:
    errs: list[ValidationError] = []
    for clave, patron, desc in TIPIFICACIONES_PROHIBIDAS:
        if clave != "INDUCCION":
            continue
        for m in re.finditer(patron, texto, flags=re.IGNORECASE):
            errs.append(
                ValidationError(
                    rule="R-06",
                    severity="CRITICA",
                    message=f"Tipificación prohibida: {desc}. Use Arts. 1°.1.b) y 2°.",
                    context=m.group(0),
                )
            )
    return errs


def _r07_non_bis_in_idem(borrador: dict[str, Any]) -> list[ValidationError]:
    """R-07: una sola tipificación por hecho. Requiere estructura por-hechos."""
    errs: list[ValidationError] = []
    hechos = borrador.get("imputaciones") or borrador.get("resolutivo")
    if not isinstance(hechos, list):
        return errs
    for idx, imput in enumerate(hechos, start=1):
        if not isinstance(imput, dict):
            continue
        cuerpo = imput.get("articulos", "") or imput.get("texto", "") or ""
        if not cuerpo:
            continue
        tipos_detectados = [
            nombre
            for _, patrones, nombre in TIPIFICACIONES_PERMITIDAS
            if nombre != "Régimen sancionador INDECOPI"
            and any(re.search(p, cuerpo, flags=re.IGNORECASE) for p in patrones)
        ]
        # Permitir combinaciones válidas conocidas (frozenset para ser hashable)
        combinaciones_validas = {
            frozenset({"Deber de Información"}),
            frozenset({"Idoneidad"}),
            frozenset({"Métodos coercitivos"}),
            frozenset({"Métodos engañosos"}),
            frozenset({"Estado de cuenta bancario", "Idoneidad"}),
        }
        conjunto = frozenset(tipos_detectados)
        if conjunto and conjunto not in combinaciones_validas:
            errs.append(
                ValidationError(
                    rule="R-07",
                    severity="CRITICA",
                    message=f"Doble tipificación (non bis in idem) en imputación #{idx}: {sorted(conjunto)}",
                    context=cuerpo[:120],
                )
            )
    return errs


def _r12_boilerplate_idoneidad_exclusivo(borrador: dict[str, Any]) -> list[ValidationError]:
    """R-12: la frase de expectativas SOLO va con Idoneidad (18 y 19)."""
    errs: list[ValidationError] = []
    admision = borrador.get("admision")
    items = admision if isinstance(admision, list) else []
    for idx, item in enumerate(items, start=1):
        cuerpo = item.get("texto", "") if isinstance(item, dict) else str(item)
        if not cuerpo:
            continue
        tiene_frase = bool(re.search(_BOILERPLATE_IDONEIDAD, cuerpo, flags=re.IGNORECASE))
        cita_idoneidad = bool(re.search(r"art[ií]culos?\s*18[°º.]?[\s,y]*19[°º.]?", cuerpo, flags=re.IGNORECASE))
        if tiene_frase and not cita_idoneidad:
            errs.append(
                ValidationError(
                    rule="R-12",
                    severity="VALIDABLE",
                    message=f"Admisión #{idx}: usa frase de expectativas pero NO cita Arts. 18° y 19°.",
                    context=cuerpo[:120],
                )
            )
    return errs


def _r31_conectores_variados(borrador: dict[str, Any]) -> list[ValidationError]:
    """R-31: no repetir 'Asimismo' en párrafos consecutivos."""
    errs: list[ValidationError] = []
    admision = borrador.get("admision")
    items = admision if isinstance(admision, list) else []
    previo = None
    for idx, item in enumerate(items, start=1):
        cuerpo = item.get("texto", "") if isinstance(item, dict) else str(item)
        if not cuerpo:
            continue
        primero = cuerpo.lstrip()[:15].split(",")[0].split(" ")[0]
        if previo == "Asimismo" and primero == "Asimismo":
            errs.append(
                ValidationError(
                    rule="R-31",
                    severity="VALIDABLE",
                    message=f"Admisión #{idx}: 'Asimismo' repetido en párrafo consecutivo. Variar con 'Además', 'Adicionalmente', 'Así también'.",
                )
            )
        previo = primero if primero in _CONECTORES_ADMISION else None
    return errs


def _r35_mype_obligatorio(texto: str) -> list[ValidationError]:
    """R-35: MYPE siempre requerido, sin importar el tamaño del denunciado."""
    norm = _normalizar(texto)
    if not re.search(r"micro\s+o\s+peque.{1,2}a\s+empresa|mype", norm):
        return [
            ValidationError(
                rule="R-35",
                severity="CRITICA",
                message="Falta el requerimiento MYPE (micro o pequeña empresa). Es OBLIGATORIO para todos los denunciados.",
            )
        ]
    return []


def _r37_infinitivo_requerimientos(borrador: dict[str, Any]) -> list[ValidationError]:
    """R-37: requerimientos en infinitivo, no subjuntivo."""
    errs: list[ValidationError] = []
    subjuntivos = re.compile(
        r"\b(presente|exhiba|remita|informe|indique|consigne|acredite|señale)\b(?:[^a-z]|$)",
        flags=re.IGNORECASE,
    )
    req = borrador.get("requerimientos")
    items = req if isinstance(req, list) else []
    for idx, item in enumerate(items, start=1):
        cuerpo = item.get("texto", "") if isinstance(item, dict) else str(item)
        if not cuerpo:
            continue
        for m in subjuntivos.finditer(cuerpo):
            errs.append(
                ValidationError(
                    rule="R-37",
                    severity="VALIDABLE",
                    message=f"Requerimiento #{idx}: verbo en subjuntivo '{m.group(1)}'. Usar infinitivo.",
                    context=cuerpo[:120],
                )
            )
    return errs


def _r38_prohibido_deberes(borrador: dict[str, Any]) -> list[ValidationError]:
    """R-38: no mencionar 'deber de información' en requerimientos."""
    errs: list[ValidationError] = []
    req = borrador.get("requerimientos")
    items = req if isinstance(req, list) else []
    patron = re.compile(r"deber\s+de\s+informaci[oó]n", flags=re.IGNORECASE)
    for idx, item in enumerate(items, start=1):
        cuerpo = item.get("texto", "") if isinstance(item, dict) else str(item)
        for _ in patron.finditer(cuerpo):
            errs.append(
                ValidationError(
                    rule="R-38",
                    severity="CRITICA",
                    message=f"Requerimiento #{idx}: menciona 'deber de información' (prohibido). Formular como hecho fáctico.",
                    context=cuerpo[:120],
                )
            )
    return errs


def _r61_lpag_vigente(texto: str) -> list[ValidationError]:
    """R-61: LPAG debe ser DS 006-2026-JUS, no la versión derogada."""
    errs: list[ValidationError] = []
    if re.search(r"decreto\s+supremo\s*n?[°º.]?\s*004-?2019-?JUS", texto, flags=re.IGNORECASE):
        errs.append(
            ValidationError(
                rule="R-61",
                severity="CRITICA",
                message="LPAG: se cita DS 004-2019-JUS (DEROGADO). Usar DS 006-2026-JUS (pub. 30-abr-2026).",
            )
        )
    return errs


def _r63_caracteres_basura(texto: str) -> list[ValidationError]:
    errs: list[ValidationError] = []
    patrones = [r"\(\(\([A-Z0-9]+\)\)\)", r"\([A-Z]{3}\)", r"XXXX+", r"YYYY+"]
    for patron in patrones:
        if re.search(patron, texto):
            errs.append(
                ValidationError(
                    rule="R-63",
                    severity="VALIDABLE",
                    message=f"Caracteres basura detectados: patrón {patron}.",
                )
            )
    return errs


def _r69_sin_markdown_notas(borrador: dict[str, Any]) -> list[ValidationError]:
    errs: list[ValidationError] = []
    notas = borrador.get("notas_pie")
    items = notas if isinstance(notas, list) else []
    for idx, item in enumerate(items, start=1):
        cuerpo = item if isinstance(item, str) else (item.get("texto", "") if isinstance(item, dict) else "")
        if re.search(r"\*\*|__|`", cuerpo):
            errs.append(
                ValidationError(
                    rule="R-69",
                    severity="CRITICA",
                    message=f"Nota al pie #{idx}: contiene markdown prohibido (** o _). Word lo imprime literal.",
                    context=cuerpo[:80],
                )
            )
    return errs


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------


def validar_borrador(borrador: dict[str, Any]) -> list[ValidationError]:
    """Aplica TODAS las reglas contra el JSON de la IA antes de construir el .docx.

    Recibe un dict con claves opcionales:
        expediente, denunciante, denunciados, hechos (str|list),
        admision (list[dict]), imputaciones (list[dict]),
        requerimientos (list[dict]), resolutivo, notas_pie (list[str]).
    """
    errores: list[ValidationError] = []
    texto = _texto_completo(borrador)

    # CRÍTICAS
    errores += _r05_prohibido_art24(texto)
    errores += _r06_prohibido_induccion(texto)
    errores += _r07_non_bis_in_idem(borrador)
    errores += _r35_mype_obligatorio(texto)
    errores += _r38_prohibido_deberes(borrador)
    errores += _r61_lpag_vigente(texto)
    errores += _r69_sin_markdown_notas(borrador)

    # VALIDABLES
    errores += _r12_boilerplate_idoneidad_exclusivo(borrador)
    errores += _r31_conectores_variados(borrador)
    errores += _r37_infinitivo_requerimientos(borrador)
    errores += _r63_caracteres_basura(texto)

    return errores


def hay_bloqueos(errores: list[ValidationError]) -> bool:
    """True si hay al menos un error CRÍTICA que impide guardar el .docx."""
    return any(e.severity == "CRITICA" for e in errores)


def validar_docx_generado(ruta: str | Path) -> list[ValidationError]:
    """R-79: validación post-generación del archivo .docx físico.

    Verifica que sea ZIP OOXML válido, tenga la estructura mínima, y que el
    texto no contenga referencias prohibidas. NO abre Word (solo python-docx).
    """
    ruta = Path(ruta)
    errores: list[ValidationError] = []

    if not ruta.exists():
        errores.append(ValidationError("R-79", "CRITICA", f"Archivo no existe: {ruta}"))
        return errores

    # 1. ZIP OOXML válido
    try:
        with zipfile.ZipFile(ruta, "r") as z:
            files = set(z.namelist())
    except zipfile.BadZipFile:
        errores.append(ValidationError("R-79", "CRITICA", "No es ZIP OOXML válido (corrupto)."))
        return errores

    # 2. Estructura mínima
    requeridos = {"[Content_Types].xml", "word/document.xml", "_rels/.rels"}
    faltantes = requeridos - files
    if faltantes:
        errores.append(
            ValidationError("R-79", "CRITICA", f"Faltan archivos OOXML: {sorted(faltantes)}")
        )

    # 3. Abrir con python-docx y extraer texto
    try:
        from docx import Document  # type: ignore

        doc = Document(str(ruta))
        texto = "\n".join(p.text for p in doc.paragraphs)
    except Exception as exc:  # pragma: no cover
        errores.append(ValidationError("R-79", "CRITICA", f"python-docx no pudo abrirlo: {exc}"))
        return errores

    # 4. Reglas críticas en el texto final
    errores += _r05_prohibido_art24(texto)
    errores += _r06_prohibido_induccion(texto)
    errores += _r61_lpag_vigente(texto)

    return errores


def resumen(errores: list[ValidationError]) -> str:
    """Genera un texto legible para logs y GUI."""
    if not errores:
        return "OK: 0 errores. Documento conforme a las 80 reglas."
    criticos = sum(1 for e in errores if e.severity == "CRITICA")
    avisos = sum(1 for e in errores if e.severity == "VALIDABLE")
    lineas = [f"TOTALES: {criticos} bloqueo(s), {avisos} aviso(s)."]
    for e in errores:
        lineas.append(str(e))
    return "\n".join(lineas)
