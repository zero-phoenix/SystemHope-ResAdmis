"""Apartado de Aprendizaje de Reglas.

Permite que el sistema sea **mejorable a la perflucción**: el usuario sube uno
o varios modelos de resolución reales (PDFs escaneados o imágenes) y el sistema
los analiza con visión para extraer:

- Detalles técnicos (sangrías, fuentes, tamaños, estructura).
- Detalles estilísticos (conectores, fórmulas, boilerplate).
- Nuevas reglas propuestas en formato ``R-XX``.

Las propuestas se acumulan en ``docs/APRENDIZAJE_PROPUESTAS.md`` (editable,
versionado) y, si el usuario lo aprueba, se incorporan a la matriz maestra
``docs/REGLAS_DE_REDACCION.md``.

Este es el mecanismo por el cual el sistema aprende de los documentos reales
del área y se perfecciona continuamente.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from . import ai_client
from .config import USER_DIR


# ---------------------------------------------------------------------------
# Prompts específicos de aprendizaje
# ---------------------------------------------------------------------------

_PROMPT_ANALISIS = """\
Analiza el documento adjunto (es un modelo de resolución admisoria real del
INDECOPI, Comisión de Protección al Consumidor 1). Extrae con precisión
milimétrica:

1. **Detalles técnicos de formato**:
   - Fuentes y tamaños exactos (ej. "Arial Narrow 11" en cuerpo, "Arial Narrow 8"
     en notas al pie).
   - Sangrías observadas (en cm, aproximadas): de romanos, numerales, incisos.
   - Espaciado entre párrafos (simple, doble, SpaceBefore/After).
   - Alineaciones (justificado, izquierda, derecha).

2. **Detalles estilísticos de redacción**:
   - Conectores lógicos usados en la Admisión (Asimismo, Además, etc.).
   - Fórmulas recurrentes o "boilerplate" (frases idénticas entre resoluciones).
   - Forma de citar las normas (con grado °, sin grado, sumilla completa).
   - Verbos rectores en requerimientos (infinitivo, subjuntivo).

3. **Estructura del documento**:
   - Secciones (I. HECHOS, II. ADMISIÓN, III. REQUERIMIENTO, IV. RESOLUCIÓN).
   - Cuántos puntos resolutivos (PRIMERO a DÉCIMO PRIMERO, etc.).
   - Cuántas notas al pie y su contenido normativo.

4. **Nuevas reglas propuestas** (lo más importante):
   Detecta patrones o estilos que NO estén ya en las 80 reglas (R-01..R-80) de
   docs/REGLAS_DE_REDACCION.md, y propónlos como nuevas reglas con el formato:

   ### R-XX · [Nombre corto] `[CRÍTICA|VALIDABLE]`
   [Descripción de la regla, explicando qué debe hacerse o evitarse.]

Devuelve TODO en un único bloque Markdown bien estructurado. Sé exhaustivo y
técnico. No inventes detalles; si no puedes ver algo, dilo.
"""


@dataclass
class ResultadoAprendizaje:
    ok: bool
    analisis: str = ""  # texto markdown devuelto por el LLM
    nuevas_reglas: list = field(default_factory=list)  # lista de "R-XX · ..."
    proveedor_usado: str = ""
    error: str = ""


def analizar_modelo(
    ruta_documento: str | Path,
    proveedor_id: str = "gemini",
) -> ResultadoAprendizaje:
    """Analiza un modelo real con visión y devuelve el análisis + reglas propuestas."""
    res = ai_client.analizar_imagen(ruta_documento, _PROMPT_ANALISIS, proveedor_id=proveedor_id)
    if not res.ok:
        return ResultadoAprendizaje(ok=False, error=res.error)
    # Extraer encabezados de nuevas reglas propuestas (### R-XX · ...)
    nuevas = re.findall(r"###\s*(R-\d+[a-z]?)\s*[·-].*", res.texto)
    return ResultadoAprendizaje(
        ok=True,
        analisis=res.texto,
        nuevas_reglas=nuevas,
        proveedor_usado=res.proveedor_usado,
    )


def guardar_propuesta(analisis: str, ruta_origen: str) -> Path:
    """Acumula el análisis en ``docs/APRENDIZAJE_PROPUESTAS.md``.

    El archivo se versiona con git; el usuario revisa y, si aprueba, mueve las
    reglas a ``docs/REGLAS_DE_REDACCION.md`` (manual o con un PR).
    """
    docs_dir = USER_DIR / "aprendizaje"
    docs_dir.mkdir(parents=True, exist_ok=True)
    ruta = docs_dir / "APRENDIZAJE_PROPUESTAS.md"

    marca = f"## Análisis de `{Path(ruta_origen).name}` — {datetime.now():%Y-%m-%d %H:%M}\n"
    bloque = f"\n\n---\n\n{marca}\n\n{analisis}\n"

    if ruta.exists():
        contenido = ruta.read_text(encoding="utf-8")
    else:
        contenido = (
            "# Aprendizaje de Reglas — Propuestas acumuladas\n\n"
            "Este archivo se genera automáticamente cuando el usuario sube "
            "modelos reales al apartado 'Aprendizaje de Reglas' del ejecutable. "
            "Revisa cada propuesta y, si la apruebas, incorpórala a "
            "`docs/REGLAS_DE_REDACCION.md`.\n"
        )
    contenido += bloque
    ruta.write_text(contenido, encoding="utf-8")
    return ruta


def listar_propuestas() -> str:
    """Devuelve el contenido acumulado de propuestas (vacío si no existe)."""
    ruta = USER_DIR / "aprendizaje" / "APRENDIZAJE_PROPUESTAS.md"
    if ruta.exists():
        return ruta.read_text(encoding="utf-8")
    return "Aún no hay propuestas acumuladas. Sube un modelo real para empezar."
