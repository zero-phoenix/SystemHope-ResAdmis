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
# Reglas Master Phoenyx (Sistema Popperiano: Invariantes y Prohibiciones)
# ---------------------------------------------------------------------------


def _extraer_texto_hechos(borrador: dict[str, Any]) -> list[str]:
    """Extrae los párrafos individuales de hechos (soporta lista de strings o dicts)."""
    hechos_raw = borrador.get("hechos", [])
    if isinstance(hechos_raw, str):
        return [hechos_raw]
    if not isinstance(hechos_raw, list):
        return []
    parrafos = []
    for item in hechos_raw:
        if isinstance(item, str):
            parrafos.append(item)
        elif isinstance(item, dict):
            texto = item.get("texto", "")
            if texto:
                parrafos.append(texto)
            for sub in item.get("subincisos", []):
                if isinstance(sub, str):
                    parrafos.append(sub)
    return parrafos


def _r_phoenyx_sin_palabra_denunciante_en_hechos(borrador: dict[str, Any]) -> list[ValidationError]:
    """PHOENYX-01 [CRITICA]: En los hechos está TERMINANTEMENTE PROHIBIDO escribir 'denunciante'
    o el nombre del denunciante, pues van precedidos de 'el/la denunciante señaló lo siguiente:'.
    Deben usarse verbos en tercera persona directamente (ej. 'presentó', no 'se presentó')."""
    errs: list[ValidationError] = []
    parrafos = _extraer_texto_hechos(borrador)
    for idx, p in enumerate(parrafos, start=1):
        if re.search(r"\bdenunciantes?\b", p, flags=re.IGNORECASE):
            errs.append(
                ValidationError(
                    rule="PHOENYX-01",
                    severity="CRITICA",
                    message=f"Hechos párrafo #{idx}: contiene la palabra prohibida 'denunciante'. Debe usar verbo en 3ra persona directo.",
                    context=p[:100],
                )
            )
    return errs


def _r_phoenyx_sin_habria_en_hechos(borrador: dict[str, Any]) -> list[ValidationError]:
    """PHOENYX-02 [CRITICA]: En los hechos está PROHIBIDO usar 'habría' o 'habrían'.
    Los hechos se narran en tiempo pasado afirmativo según la versión del denunciante ('presentó', 'denegó').
    El condicional 'habría' es EXCLUSIVO de las imputaciones resolutivas de la Comisión."""
    errs: list[ValidationError] = []
    parrafos = _extraer_texto_hechos(borrador)
    for idx, p in enumerate(parrafos, start=1):
        m = re.search(r"\bhabr[ií]an?\b", p, flags=re.IGNORECASE)
        if m:
            errs.append(
                ValidationError(
                    rule="PHOENYX-02",
                    severity="CRITICA",
                    message=f"Hechos párrafo #{idx}: usa condicional '{m.group(0)}'. En hechos solo se usa pasado afirmativo.",
                    context=p[:100],
                )
            )
    return errs


def _r_phoenyx_terminologia_estricta(texto: str) -> list[ValidationError]:
    """PHOENYX-03 [CRITICA/VALIDABLE]: Reglas léxicas popperianas obligatorias:
    - PROHIBIDO 'esposo/esposa/esposos': usar 'cónyuge' o 'cónyuges'.
    - PROHIBIDO 'tras': usar 'luego de'.
    - PROHIBIDO 'ésta'/'éstas'/'éste'/'éstos': 'esta' NUNCA lleva tilde.
    - PROHIBIDO 'Dr.'/'doctor'/'doctora': usar 'médico'.
    - PROHIBIDO 'carro'/'auto': usar 'vehículo' (o 'vehículo con Placa de Rodaje...').
    """
    errs: list[ValidationError] = []

    # Cónyuge
    for m in re.finditer(r"\b(espos[oa]s?)\b", texto, flags=re.IGNORECASE):
        errs.append(
            ValidationError(
                rule="PHOENYX-03A",
                severity="CRITICA",
                message=f"Término prohibido '{m.group(0)}'. Debe usar estrictamente 'cónyuge' o 'cónyuges'.",
                context=m.group(0),
            )
        )

    # Luego de (no tras)
    for m in re.finditer(r"\btras\s+(el|la|los|las|un|una|haber|constatar|sufrir|recibir|el\s+siniestro)\b", texto, flags=re.IGNORECASE):
        errs.append(
            ValidationError(
                rule="PHOENYX-03B",
                severity="VALIDABLE",
                message=f"Uso de 'tras' detectado ('{m.group(0)}'). Debe reemplazarse por 'luego de'.",
                context=m.group(0),
            )
        )

    # 'esta' sin tilde
    for m in re.finditer(r"\b([eé]st[ae]s?)\b", texto):
        if m.group(0) in ("ésta", "éstas", "éste", "éstos"):
            errs.append(
                ValidationError(
                    rule="PHOENYX-03C",
                    severity="VALIDABLE",
                    message=f"Tilde prohibida en '{m.group(0)}'. La palabra 'esta/estas/este/estos' nunca lleva tilde.",
                    context=m.group(0),
                )
            )

    # Médico (no doctor)
    for m in re.finditer(r"\b(Dr\.|doctora?)\b", texto, flags=re.IGNORECASE):
        # Excepción si es parte de un nombre propio registrado como 'Dr. Ley'
        if "dr. ley" in texto[max(0, m.start()-5):m.end()+10].lower():
            continue
        errs.append(
            ValidationError(
                rule="PHOENYX-03D",
                severity="VALIDABLE",
                message=f"Término '{m.group(0)}' prohibido para profesionales de la salud. Usar siempre 'médico'.",
                context=m.group(0),
            )
        )

    # Vehículo (no carro / auto)
    for m in re.finditer(r"\b(carros?|autos?|autom[oó]vil(?:es)?)\b", texto, flags=re.IGNORECASE):
        errs.append(
            ValidationError(
                rule="PHOENYX-03E",
                severity="VALIDABLE",
                message=f"Término '{m.group(0)}' prohibido. Debe referirse siempre como 'vehículo' o 'vehículo con Placa de Rodaje [número]'.",
                context=m.group(0),
            )
        )

    return errs


def _r_phoenyx_formato_moneda(texto: str) -> list[ValidationError]:
    """PHOENYX-04 [VALIDABLE]: Formato monetario estricto INDECOPI CC1:
    - Símbolos: 'S/' o 'US$'.
    - Solo coma ',' para decimales (prohibido '.' como separador decimal).
    - Espacio cada 3 enteros (prohibido ',' como separador de miles). Ej: 'S/ 2 618,00'.
    """
    errs: list[ValidationError] = []
    # Detecta S/ o US$ seguido de número con punto decimal (ej: S/ 2,618.00 o S/ 1500.50)
    for m in re.finditer(r"(?:S/|US\$)\s*(\d+[\d,]*\.\d{2})\b", texto):
        errs.append(
            ValidationError(
                rule="PHOENYX-04",
                severity="VALIDABLE",
                message=f"Monto con punto decimal '{m.group(0)}'. Debe usar exclusivamente coma decimal (ej. 'S/ 2 618,00').",
                context=m.group(0),
            )
        )
    # Detecta comas como separador de miles (ej: S/ 2,618 o US$ 10,000)
    for m in re.finditer(r"(?:S/|US\$)\s*(\d{1,3}(?:,\d{3})+)", texto):
        errs.append(
            ValidationError(
                rule="PHOENYX-04",
                severity="VALIDABLE",
                message=f"Monto con coma de miles '{m.group(0)}'. En miles se usa espacio (ej. 'S/ 2 618,00').",
                context=m.group(0),
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
    # Master Phoenyx Críticas
    errores += _r_phoenyx_sin_palabra_denunciante_en_hechos(borrador)
    errores += _r_phoenyx_sin_habria_en_hechos(borrador)
    errores += [e for e in _r_phoenyx_terminologia_estricta(texto) if e.severity == "CRITICA"]

    # VALIDABLES
    errores += _r12_boilerplate_idoneidad_exclusivo(borrador)
    errores += _r31_conectores_variados(borrador)
    errores += _r37_infinitivo_requerimientos(borrador)
    errores += _r63_caracteres_basura(texto)
    # Master Phoenyx Validables
    errores += [e for e in _r_phoenyx_terminologia_estricta(texto) if e.severity == "VALIDABLE"]
    errores += _r_phoenyx_formato_moneda(texto)

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
    errores += _r_phoenyx_terminologia_estricta(texto)
    errores += _r_phoenyx_formato_moneda(texto)

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
def _r_phoenyx_parrafos_notificacion(texto: str) -> list[ValidationError]:
    """PHOENYX-05: Valida que la seccion resolutiva final contenga los parrafos
    literales de notificacion segun las 3 vias de CC1 (Casilla, Correo o Domicilio),
    sin parafrasear y con el D.S. 006-2026-JUS cuando corresponda."""
    errores = []
    if any(k in texto for k in ["DECIMO", "DÉCIMO", "UNDÉCIMO", "DUODÉCIMO", "NOTIFICAR"]):
        has_casilla = "acuse de recibo mediante la confirmación de recepción" in texto and "Casilla" in texto
        has_correo = "bandeja de correo electrónico" in texto or "bandejas de correo electrónico" in texto
        has_domicilio = "en su domicilio procesal" in texto or "en sus domicilios procesales" in texto
        
        if not (has_casilla or has_correo or has_domicilio):
            errores.append(
                ValidationError(
                    "PHOENYX-05",
                    "CRITICA",
                    "La resolucion debe contener al menos uno de los 3 parrafos literales de notificacion CC1 (Casilla Electronica, Correo Electronico o Domicilio Procesal) sin parafraseo."
                )
            )
        if (has_correo or has_domicilio) and "confirmación de recepción" in texto:
            if "006-2026" not in texto:
                errores.append(
                    ValidationError(
                        "PHOENYX-05",
                        "CRITICA",
                        "El requerimiento de confirmacion de notificacion debe citar expresamente el Decreto Supremo N° 006-2026-JUS."
                    )
                )
    return errores
