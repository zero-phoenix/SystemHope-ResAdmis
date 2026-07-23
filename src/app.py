"""Orquestador de alto nivel: GUI + CLI llaman a esta función.

Flujo completo de generación:
    datos GUI -> ai_client.generar_borrador -> rules_engine.validar_borrador
    -> (si hay bloqueos, reportar y abortar) -> builder.construir_doc
    -> footnote_injector.procesar_notas -> rules_engine.validar_docx_generado
"""

from __future__ import annotations

import json
import sys
import traceback
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from . import ai_client, builder, extractor_pdfs, footnote_injector, rules_engine
from .config import Settings, USER_DIR


@dataclass
class Reporte:
    ok: bool
    archivo_salida: str = ""
    proveedor_usado: str = ""
    errores_validacion: list[dict[str, str]] = field(default_factory=list)
    errores_post: list[dict[str, str]] = field(default_factory=list)
    error_fatal: str = ""
    advertencias: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def generar_resolucion(
    datos_expediente: dict[str, Any],
    settings: Settings | None = None,
    *,
    saltar_ia: bool = False,
    borrador_predefinido: dict[str, Any] | None = None,
) -> Reporte:
    """Genera una resolución admistoria de extremo a extremo.

    Modos:
    - Normal: llama a la IA con ``datos_expediente``.
    - ``saltar_ia=True`` + ``borrador_predefinido``: usa el borrador dado (para tests).
    """
    settings = settings or Settings.cargar()
    reporte = Reporte(ok=False)

    # 1. Obtener el borrador JSON
    if saltar_ia:
        if not borrador_predefinido:
            reporte.error_fatal = "Modo saltar_ia requiere borrador_predefinido."
            return reporte
        borrador = borrador_predefinido
        reporte.proveedor_usado = "manual"
    else:
        resultado = ai_client.generar_borrador(
            datos_expediente,
            proveedor_id=settings.proveedor_ia,
            max_reintentos=settings.reintentos_ia,
            preferidos=settings.proveedores_preferidos,
        )
        if not resultado.ok:
            reporte.error_fatal = (
                f"No se pudo generar el borrador con la IA. Último error: {resultado.error}\n"
                "Verifica tu API key en las variables de entorno "
                f"(ZAI_API_KEY, BIGMODEL_API_KEY, DEEPSEEK_API_KEY, KIMI_API_KEY)."
            )
            return reporte
        borrador = resultado.borrador or {}
        reporte.proveedor_usado = resultado.proveedor_usado

    if borrador.get("_advertencias"):
        reporte.advertencias.extend(borrador["_advertencias"])

    # 2. Validar contra las 80 reglas (determinista)
    errores = rules_engine.validar_borrador(borrador)
    reporte.errores_validacion = [
        {"rule": e.rule, "severity": e.severity, "message": e.message, "context": e.context}
        for e in errores
    ]
    if rules_engine.hay_bloqueos(errores):
        # Guardamos el borrador para depuración
        dump = USER_DIR / f"borrador_fallido_{datetime.now():%Y%m%d_%H%M%S}.json"
        dump.write_text(json.dumps(borrador, indent=2, ensure_ascii=False), encoding="utf-8")
        reporte.error_fatal = (
            f"Hay {sum(1 for e in errores if e.severity == 'CRITICA')} reglas CRÍTICAS "
            f"violadas. Documento NO guardado. Borrador en: {dump}"
        )
        return reporte

    # 3. Construir el .docx
    if not settings.plantilla_maestra:
        reporte.error_fatal = (
            "No hay plantilla maestra configurada. Coloca un .docx modelo en "
            f"{settings.directorio_plantillas} o edita settings.json."
        )
        return reporte

    expediente_safe = borrador.get("expediente", "expediente").replace("/", "-")
    nombre_archivo = f"ADM_{expediente_safe}_R{borrador.get('resolucion_numero', 1)}.docx"
    salida = Path(settings.directorio_salida) / nombre_archivo

    try:
        builder.construir_doc(borrador, settings.plantilla_maestra, salida, inyectar_notas=True)
    except Exception as exc:
        reporte.error_fatal = f"Error construyendo .docx: {exc}\n{traceback.format_exc()[-400:]}"
        return reporte

    # 4. Inyectar notas al pie nativas vía win32com (R-71)
    if sys.platform == "win32":
        try:
            stats = footnote_injector.procesar_notas(salida, visible=settings.word_visible)
            if stats["errores"]:
                reporte.advertencias.append(
                    f"Notas al pie: {stats['notas_insertadas']} insertadas, "
                    f"{len(stats['errores'])} errores menores."
                )
            else:
                reporte.advertencias.append(
                    f"Notas al pie: {stats['notas_insertadas']} insertadas correctamente."
                )
        except RuntimeError as exc:
            # Si Word no está disponible, el doc ya tiene los marcadores como texto
            reporte.advertencias.append(
                f"Notas al pie no convertidas (Word no disponible): {exc}. "
                "El documento contiene marcadores [[FN:...]] editables."
            )
    else:
        reporte.advertencias.append(
            "Notas al pie: en Linux/Mac quedan como marcadores [[FN:...]]. "
            "Convertir manualmente o usar Windows con Word instalado."
        )

    # 5. Validación post-generación
    errores_post = rules_engine.validar_docx_generado(salida)
    reporte.errores_post = [
        {"rule": e.rule, "severity": e.severity, "message": e.message}
        for e in errores_post
    ]

    reporte.archivo_salida = str(salida)
    reporte.ok = not rules_engine.hay_bloqueos(errores_post)
    return reporte


def generar_desde_carpeta(
    carpeta_entrada: str | Path,
    settings: Settings | None = None,
    *,
    proveedor_id: str | None = None,
) -> Reporte:
    """Flujo 'cero input manual': carpeta con PDFs -> .docx.

    1. Extrae datos del expediente desde los PDFs/imágenes (visión).
    2. Llama a la IA con esos datos + system prompt blindado.
    3. Valida + construye + notas al pie + validación post.
    """
    settings = settings or Settings.cargar()
    reporte = Reporte(ok=False)
    proveedor = proveedor_id or settings.proveedor_ia

    # 1. Extracción
    ext = extractor_pdfs.extraer_desde_carpeta(carpeta_entrada, proveedor_id=proveedor)
    if not ext.ok:
        reporte.error_fatal = ext.error
        return reporte
    reporte.proveedor_usado = ext.proveedor_usado
    reporte.advertencias.append(
        f"Documentos procesados: {len(ext.archivos_procesados)} archivo(s)."
    )

    # 2. Generación (reusa generar_resolucion con datos extraídos)
    return generar_resolucion(ext.datos, settings)

