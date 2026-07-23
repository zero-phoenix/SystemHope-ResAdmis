"""Extracción automática de datos del expediente desde PDFs/escaneos.

Flujo "cero input manual":
1. El usuario arrastra PDFs (denuncia, anexos, escritos adicionales) a una carpeta.
2. Este módulo los lee, los envía al proveedor con visión (Gemini preferido),
   y devuelve el JSON del expediente listo para construir el .docx.
3. El builder toma ese JSON y genera la resolución.

No se pide al usuario que complete ningún formulario.
"""

from __future__ import annotations

import base64
import json
import mimetypes
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import ai_client, system_prompt


# ---------------------------------------------------------------------------
# Prompt de extracción (visión)
# ---------------------------------------------------------------------------

_PROMPT_EXTRACCION = """\
Analiza los documentos adjuntos (son PDFs/escaneos de un expediente: escrito de
denuncia, anexos, escritos adicionales). Tu tarea es extraer TODA la información
necesaria para redactar una resolución admisoria.

Devuelve EXCLUSIVAMENTE un objeto JSON con esta estructura exacta (sin texto
antes ni después, sin markdown):

{
  "expediente": "XXXX-2026/CC1",
  "denunciante": "NOMBRE COMPLETO",
  "denunciados": [
    {"razon_social": "...", "abreviatura": "...", "rubro": "aseguradora|banco|otro"}
  ],
  "resolucion_numero": 1,
  "documento_traslado": {"numero": "...", "fecha": "...", "recepcion": "..."},
  "descripcion_hechos": "Narracion cronologica y objetiva de los hechos segun el escrito de denuncia, incluyendo numeros de poliza/contrato, fechas, montos reclamados, documentos mencionados y acciones del consumidor frente a los proveedores. Sin adjetivos emocionales.",
  "instrucciones_extra": ""
}

REGLAS DE EXTRACCION:
- Si un dato no esta en los documentos, deja el campo como string vacio "" o null.
- NO INVENTES informacion que no este en los PDFs.
- Para "denunciados", clasifica el rubro: si es empresa de seguros pon "aseguradora",
  si es banco pon "banco", si es otro rubro pon "otro".
- La abreviatura debe ser corta (ej. "PACIFICO", "BCP").
- "descripcion_hechos" debe ser la narracion mas fiel y completa posible, en
  orden cronologico, mencionando explicitamente los numeros de póliza/contrato,
  las fechas relevantes, los documentos que el denunciante dice haber presentado,
  y los hechos controvertidos.
- Si hay descripcion de audios/videos (contratacion telefonica, videollamada,
  entrevista poligrafica), incluyelos en descripcion_hechos.
"""


# ---------------------------------------------------------------------------
# Tipos
# ---------------------------------------------------------------------------


@dataclass
class ResultadoExtraccion:
    ok: bool
    datos: dict[str, Any] | None = None
    texto: str = ""  # respuesta cruda
    proveedor_usado: str = ""
    error: str = ""
    archivos_procesados: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Lógica
# ---------------------------------------------------------------------------


def _es_pdf(ruta: Path) -> bool:
    return ruta.suffix.lower() == ".pdf"


def _es_imagen(ruta: Path) -> bool:
    return ruta.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif", ".tiff"}


def descubrir_documentos(carpeta: str | Path) -> list[Path]:
    """Descubre PDFs e imágenes en una carpeta (no recursivo por defecto)."""
    carpeta = Path(carpeta)
    if not carpeta.exists():
        return []
    docs = []
    for p in sorted(carpeta.iterdir()):
        if p.is_file() and (_es_pdf(p) or _es_imagen(p)):
            docs.append(p)
    return docs


def _generar_prompt_extraccion(n_archivos: int) -> str:
    plural = "s" if n_archivos != 1 else ""
    return (
        f"A continuacion se procesan {n_archivos} documento{plural} del expediente. "
        + _PROMPT_EXTRACCION
    )


def extraer_desde_carpeta(
    carpeta: str | Path,
    proveedor_id: str = "gemini",
    timeout: int = 300,
) -> ResultadoExtraccion:
    """Lee todos los PDFs/imágenes de una carpeta y devuelve el JSON del expediente.

    Estrategia:
    - Si hay 1 documento, se envía solo (más rápido).
    - Si hay varios, se concatenan en una sola llamada multimodal (Gemini acepta).
    - El proveedor debe soportar visión. Si no, devuelve error con instrucción.
    """
    carpeta = Path(carpeta)
    docs = descubrir_documentos(carpeta)
    if not docs:
        return ResultadoExtraccion(
            ok=False,
            error=f"No se encontraron PDFs ni imágenes en: {carpeta}. "
            "Arrastra allí el escrito de denuncia, anexos y escritos adicionales.",
        )

    if proveedor_id not in ai_client.PROVEEDORES:
        return ResultadoExtraccion(ok=False, error=f"Proveedor '{proveedor_id}' desconocido.")
    prov = ai_client.PROVEEDORES[proveedor_id]
    if not prov.soporta_vision:
        return ResultadoExtraccion(
            ok=False,
            error=f"{prov.nombre} no soporta visión. Usa Google Antigravity (Gemini).",
        )
    if not prov.api_key():
        return ResultadoExtraccion(
            ok=False,
            error=f"Falta API key ({prov.api_key_env}). Configúrala antes de generar.",
        )

    # Construir payload según familia del proveedor
    try:
        texto_respuesta = _enviar_documentos(prov, docs, timeout=timeout)
    except RuntimeError as exc:
        return ResultadoExtraccion(ok=False, error=str(exc), archivos_procesados=[str(p) for p in docs])

    datos = ai_client._extraer_json(texto_respuesta)
    if datos is None:
        return ResultadoExtraccion(
            ok=False,
            error="El proveedor no devolvió JSON válido. Intenta nuevamente.",
            texto=texto_respuesta,
            archivos_procesados=[str(p) for p in docs],
        )
    return ResultadoExtraccion(
        ok=True,
        datos=datos,
        texto=texto_respuesta,
        proveedor_usado=prov.nombre,
        archivos_procesados=[str(p) for p in docs],
    )


def _enviar_documentos(prov, docs: list[Path], timeout: int) -> str:
    """Despacha la llamada multimodal según la familia del proveedor."""
    
    import urllib.request
    import urllib.error
    import pdfplumber

    api_key = prov.api_key()
    partes_data = []  # cada item: dict listo para la API

    for doc in docs:
        mime, _ = mimetypes.guess_type(str(doc))
        if mime is None:
            mime = "application/pdf" if _es_pdf(doc) else "image/jpeg"
            
        texto_extraido = ""
        if _es_pdf(doc):
            try:
                with pdfplumber.open(doc) as pdf:
                    paginas_texto = []
                    for i, page in enumerate(pdf.pages):
                        t = page.extract_text()
                        if t:
                            paginas_texto.append(f"--- Pagina {i+1} ---\n{t}")
                    texto_extraido = "\n".join(paginas_texto)
            except Exception as e:
                print(f"pdfplumber fallo en {doc.name}: {e}")
                texto_extraido = ""
        
        if texto_extraido.strip():
            # Si se pudo extraer texto digital, enviamos texto puro a Gemini en vez de imagen
            texto_formateado = f"--- Documento PDF: {doc.name} ---\n{texto_extraido}\n--- Fin de Documento ---"
            if prov.familia == "gemini":
                partes_data.append({"text": texto_formateado})
            else:
                partes_data.append({"type": "text", "text": texto_formateado})
        else:
            # Fallback a vision (imagen/binario)
            b64 = base64.b64encode(doc.read_bytes()).decode("ascii")
            if prov.familia == "gemini":
                partes_data.append({"inline_data": {"mime_type": mime, "data": b64}})
            else:  # openai-compatible
                partes_data.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{b64}"},
                })


    instruccion = _generar_prompt_extraccion(len(docs))

    if prov.familia == "gemini":
        url = f"{prov.base_url.rstrip('/')}/models/{prov.modelo}:generateContent?key={api_key}"
        payload = {
            "system_instruction": {"parts": [{"text": "Eres un asistente jurídico experto en extracción de datos."}]},
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": instruccion}] + partes_data,
                }
            ],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"},
        }
    else:
        url = (prov.base_url or "").rstrip("/") + "/chat/completions"
        payload = {
            "model": prov.modelo,
            "messages": [
                {"role": "system", "content": "Eres un asistente jurídico experto en extracción de datos."},
                {"role": "user", "content": [{"type": "text", "text": instruccion}] + partes_data},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }

    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if prov.familia == "openai":
        headers["Authorization"] = f"Bearer {api_key}"

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detalle = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"HTTP {exc.code}: {detalle}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Error de red: {exc.reason}") from exc

    out = json.loads(raw)
    if prov.familia == "gemini":
        return out["candidates"][0]["content"]["parts"][0]["text"]
    return out["choices"][0]["message"]["content"]
