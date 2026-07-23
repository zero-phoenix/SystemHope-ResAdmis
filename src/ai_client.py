"""Cliente de IA multi-proveedor para generar el borrador JSON del admisorio.

Soporta dos familias de proveedores:

1. **OpenAI-compatible** (Z.ai, BigModel, DeepSeek, Kimi, OpenAI-compat):
   endpoint ``/chat/completions`` estándar.
2. **Google Gemini** (vía Google AI Studio / Vertex):
   endpoint ``/models/{model}:generateContent``. Es el proveedor **principal**
   recomendado (etiquetado como "Google Antigravity (Gemini)" en la GUI) porque
   tiene el mejor lector de imágenes escaneadas (fundamental para PDFs
   escaneados de denuncias y anexos).

Toda llamada va por :func:`generar_borrador`, que inyecta el system prompt
blindado y normaliza la respuesta a ``dict``. Si la respuesta no es JSON
válido, se reintentan hasta ``max_reintentos`` veces con un mensaje de
corrección. Nunca lanza: devuelve ``ResultadoIA`` con ``ok``, ``borrador`` y
``error``.

Para análisis de imágenes (aprendizaje de reglas desde modelos reales) usar
:func:`analizar_imagen`, que envía una imagen codificada en base64 al
proveedor con capacidad de visión.
"""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import system_prompt


# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

DEFAULT_TIMEOUT = 180  # segundos (vision y respuestas largas tardan más)


@dataclass
class ProveedorConfig:
    """Configuración de un proveedor de IA.

    ``familia`` determina el formato del request:
    - ``"openai"``  → esquema /chat/completions.
    - ``"gemini"``  → esquema /models/{model}:generateContent.
    """

    nombre: str
    familia: str  # "openai" | "gemini"
    base_url: str
    modelo: str
    api_key_env: str
    soporta_vision: bool = False
    header_auth: str = "Bearer"  # Gemini usa "x-goog-api-key"

    def api_key(self) -> str:
        return os.environ.get(self.api_key_env, "")


# Tabla de proveedores soportados. Para añadir uno nuevo, basta con
# registrarlo aquí. El cliente se despacha por ``familia``.
#
# ORDEN DE PRIORIDAD (como pidió el usuario):
#   1. Google Antigravity (Gemini) — PRINCIPAL, mejor lector de imágenes.
#   2. Z.ai GLM                    — SECUNDARIO por defecto.
#   3. BigModel, DeepSeek, Kimi    — fallback.
PROVEEDORES: dict[str, ProveedorConfig] = {
    # --- PRINCIPAL ---
    "gemini": ProveedorConfig(
        nombre="Google Antigravity (Gemini)",
        familia="gemini",
        base_url="https://generativelanguage.googleapis.com/v1beta",
        modelo="gemini-2.5-pro",
        api_key_env="GEMINI_API_KEY",
        soporta_vision=True,
        header_auth="x-goog-api-key",
    ),
    # --- SECUNDARIO ---
    "zai": ProveedorConfig(
        nombre="Z.ai GLM",
        familia="openai",
        base_url="https://api.z.ai/api/paas/v4",
        modelo="glm-5.2",
        api_key_env="ZAI_API_KEY",
    ),
    # --- FALLBACKS ---
    "bigmodel": ProveedorConfig(
        nombre="BigModel (open.bigmodel.cn)",
        familia="openai",
        base_url="https://open.bigmodel.cn/api/paas/v4",
        modelo="glm-5.2",
        api_key_env="BIGMODEL_API_KEY",
    ),
    "deepseek": ProveedorConfig(
        nombre="DeepSeek",
        familia="openai",
        base_url="https://api.deepseek.com/v1",
        modelo="deepseek-v4-pro",
        api_key_env="DEEPSEEK_API_KEY",
    ),
    "kimi": ProveedorConfig(
        nombre="Kimi (Moonshot)",
        familia="openai",
        base_url="https://api.moonshot.cn/v1",
        modelo="kimi-k2.6",
        api_key_env="KIMI_API_KEY",
    ),
    "openai_compat": ProveedorConfig(
        nombre="OpenAI-compatible (custom)",
        familia="openai",
        base_url="",  # se setea vía OPENAI_BASE_URL
        modelo="gpt-4o",
        api_key_env="OPENAI_API_KEY",
        soporta_vision=True,
    ),
}

# Orden de preferencia por defecto (Gemini primero, Z.ai segundo, etc.).
ORDEN_PREFERENCIA: list[str] = ["gemini", "zai", "bigmodel", "deepseek", "kimi"]


@dataclass
class ResultadoIA:
    ok: bool
    borrador: dict[str, Any] | None = None
    texto: str = ""  # texto crudo devuelto (útil para chat/aprendizaje)
    error: str = ""
    proveedor_usado: str = ""
    intentos: int = 0


# ---------------------------------------------------------------------------
# Llamadas HTTP (sin dependencias externas — stdlib)
# ---------------------------------------------------------------------------


def _post_json(url: str, headers: dict[str, str], payload: bytes, timeout: int) -> dict:
    req = urllib.request.Request(
        url, data=payload, headers={**headers, "Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detalle = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"HTTP {exc.code}: {detalle}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Error de red: {exc.reason}") from exc
    return json.loads(raw)


# ---------------------------------------------------------------------------
# OpenAI-compatible (Z.ai, BigModel, DeepSeek, Kimi, OpenAI)
# ---------------------------------------------------------------------------


def _chat_openai(
    prov: ProveedorConfig, system: str, user: str, temperature: float, timeout: int
) -> str:
    base = prov.base_url or os.environ.get("OPENAI_BASE_URL", "")
    if not base:
        raise RuntimeError(f"Proveedor '{prov.nombre}' sin base_url.")
    url = base.rstrip("/") + "/chat/completions"
    payload = {
        "model": prov.modelo,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }
    headers = {"Authorization": f"Bearer {prov.api_key()}"}
    data = json.dumps(payload).encode("utf-8")
    out = _post_json(url, headers, data, timeout)
    try:
        return out["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Respuesta inesperada: {json.dumps(out)[:500]}") from exc


def _vision_openai(
    prov: ProveedorConfig, system: str, user: str, imagen_b64: str, mime: str, timeout: int
) -> str:
    """OpenAI-compatible con imagen (esquema multimodal de OpenAI)."""
    base = prov.base_url or os.environ.get("OPENAI_BASE_URL", "")
    if not base:
        raise RuntimeError(f"Proveedor '{prov.nombre}' sin base_url.")
    url = base.rstrip("/") + "/chat/completions"
    payload = {
        "model": prov.modelo,
        "messages": [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{imagen_b64}"},
                    },
                ],
            },
        ],
        "temperature": 0.1,
    }
    headers = {"Authorization": f"Bearer {prov.api_key()}"}
    data = json.dumps(payload).encode("utf-8")
    out = _post_json(url, headers, data, timeout)
    try:
        return out["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Respuesta inesperada: {json.dumps(out)[:500]}") from exc


# ---------------------------------------------------------------------------
# Gemini (Google Antigravity)
# ---------------------------------------------------------------------------


def _chat_gemini(
    prov: ProveedorConfig, system: str, user: str, temperature: float, timeout: int
) -> str:
    api_key = prov.api_key()
    url = f"{prov.base_url.rstrip('/')}/models/{prov.modelo}:generateContent?key={api_key}"
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {
            "temperature": temperature,
            "responseMimeType": "application/json",
        },
    }
    headers = {"Content-Type": "application/json"}  # la key va en query (?key=)
    data = json.dumps(payload).encode("utf-8")
    out = _post_json(url, headers, data, timeout)
    try:
        return out["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Respuesta Gemini inesperada: {json.dumps(out)[:500]}") from exc


def _vision_gemini(
    prov: ProveedorConfig,
    system: str,
    user: str,
    imagen_b64: str,
    mime: str,
    timeout: int,
) -> str:
    """Gemini con imagen (inline_data)."""
    api_key = prov.api_key()
    url = f"{prov.base_url.rstrip('/')}/models/{prov.modelo}:generateContent?key={api_key}"
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": user},
                    {"inline_data": {"mime_type": mime, "data": imagen_b64}},
                ],
            }
        ],
        "generationConfig": {"temperature": 0.1},
    }
    headers = {"Content-Type": "application/json"}
    data = json.dumps(payload).encode("utf-8")
    out = _post_json(url, headers, data, timeout)
    try:
        return out["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Respuesta Gemini vision inesperada: {json.dumps(out)[:500]}") from exc


# ---------------------------------------------------------------------------
# Despachador unificado
# ---------------------------------------------------------------------------


def _chat(prov: ProveedorConfig, system: str, user: str, temperature: float, timeout: int) -> str:
    if prov.familia == "gemini":
        return _chat_gemini(prov, system, user, temperature, timeout)
    return _chat_openai(prov, system, user, temperature, timeout)


def _vision(prov: ProveedorConfig, system: str, user: str, imagen_b64: str, mime: str, timeout: int) -> str:
    if not prov.soporta_vision:
        raise RuntimeError(f"{prov.nombre} no soporta visión. Usa Gemini o Z.ai con vision.")
    if prov.familia == "gemini":
        return _vision_gemini(prov, system, user, imagen_b64, mime, timeout)
    return _vision_openai(prov, system, user, imagen_b64, mime, timeout)


# ---------------------------------------------------------------------------
# Parseo defensivo del JSON devuelto
# ---------------------------------------------------------------------------

_BLOQUE_JSON = re.compile(r"\{[\s\S]*\}")


def _extraer_json(texto: str) -> dict[str, Any] | None:
    texto = texto.strip()
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        pass
    m = _BLOQUE_JSON.search(texto)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return None
    return None


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------


def generar_borrador(
    datos_expediente: dict[str, Any],
    proveedor_id: str = "gemini",
    max_reintentos: int = 2,
    preferidos: list[str] | None = None,
) -> ResultadoIA:
    """Genera el borrador JSON llamando al LLM con el system prompt blindado.

    Orden de intento:
    1. ``proveedor_id`` explícito (por defecto ``gemini``).
    2. Si falla y ``preferidos`` está dado, prueba cada uno en orden.
    3. Si ``preferidos`` es None, usa ORDEN_PREFERENCIA global.
    """
    system = system_prompt.construir_system_prompt()
    user = system_prompt.construir_user_prompt(datos_expediente)

    if preferidos is None:
        preferidos = ORDEN_PREFERENCIA
    cola: list[str] = [proveedor_id] + [p for p in preferidos if p != proveedor_id]
    # Desduplicar preservando orden y filtra válidos
    vistos: set[str] = set()
    orden: list[str] = []
    for p in cola:
        if p in PROVEEDORES and p not in vistos:
            vistos.add(p)
            orden.append(p)

    ultimo_error = ""
    intentos = 0

    for pid in orden:
        prov = PROVEEDORES[pid]
        if not prov.api_key():
            continue
        for _ in range(max_reintentos):
            intentos += 1
            try:
                texto = _chat(prov, system, user, temperature=0.2, timeout=DEFAULT_TIMEOUT)
            except RuntimeError as exc:
                ultimo_error = f"[{prov.nombre}] {exc}"
                time.sleep(1.5)
                continue

            borrador = _extraer_json(texto)
            if borrador is None:
                # Reintento con mensaje de corrección
                system_fix = system + (
                    "\n\n# CORRECCIÓN URGENTE\n"
                    "Tu respuesta anterior NO fue JSON válido. Devuelve EXCLUSIVAMENTE "
                    "el objeto JSON, sin texto antes ni después, sin markdown."
                )
                try:
                    texto = _chat(prov, system_fix, user, temperature=0.0, timeout=DEFAULT_TIMEOUT)
                    borrador = _extraer_json(texto)
                except RuntimeError as exc:
                    ultimo_error = f"[{prov.nombre}] {exc}"
                    continue

            if borrador is not None:
                return ResultadoIA(
                    ok=True, borrador=borrador, texto=texto,
                    proveedor_usado=prov.nombre, intentos=intentos,
                )
            ultimo_error = f"[{prov.nombre}] No produjo JSON parseable."

    return ResultadoIA(ok=False, error=ultimo_error or "Sin proveedor con API key.", intentos=intentos)


def chat_conversacional(
    mensajes: list[dict[str, str]],
    proveedor_id: str = "gemini",
    timeout: int = DEFAULT_TIMEOUT,
) -> ResultadoIA:
    """Chat libre multi-turno. ``mensajes`` = [{role, content}, ...].

    Usado por el apartado "Chat por expediente" de la GUI. No fuerza JSON.
    """
    if proveedor_id not in PROVEEDORES:
        return ResultadoIA(ok=False, error=f"Proveedor '{proveedor_id}' desconocido.")
    prov = PROVEEDORES[proveedor_id]
    if not prov.api_key():
        return ResultadoIA(ok=False, error=f"Falta API key ({prov.api_key_env}).")

    # Concatenar en system + user (simplificación multi-turno compatible con ambos)
    system = mensajes[0]["content"] if mensajes and mensajes[0]["role"] == "system" else ""
    user_parts = [m["content"] for m in mensajes if m["role"] != "system"]
    user = "\n\n---\n\n".join(
        f"[{m.get('role', 'user')}]: {m['content']}" for m in mensajes if m["role"] != "system"
    ) or (user_parts[-1] if user_parts else "")

    try:
        texto = _chat(prov, system or "Eres un asistente útil.", user, temperature=0.4, timeout=timeout)
        return ResultadoIA(ok=True, texto=texto, proveedor_usado=prov.nombre)
    except RuntimeError as exc:
        return ResultadoIA(ok=False, error=str(exc))


def analizar_imagen(
    ruta_imagen: str | Path,
    instruccion: str,
    proveedor_id: str = "gemini",
    timeout: int = DEFAULT_TIMEOUT,
) -> ResultadoIA:
    """Envía una imagen (PDF escaneado, JPG, PNG) a un proveedor con visión.

    Usado por el apartado "Aprendizaje de reglas" para analizar modelos reales
    y proponer nuevas reglas a partir del estilo y los detalles técnicos.
    """
    if proveedor_id not in PROVEEDORES:
        return ResultadoIA(ok=False, error=f"Proveedor '{proveedor_id}' desconocido.")
    prov = PROVEEDORES[proveedor_id]
    if not prov.api_key():
        return ResultadoIA(ok=False, error=f"Falta API key ({prov.api_key_env}).")
    if not prov.soporta_vision:
        return ResultadoIA(
            ok=False,
            error=f"{prov.nombre} no soporta visión. Usa Google Antigravity (Gemini).",
        )

    ruta = Path(ruta_imagen)
    if not ruta.exists():
        return ResultadoIA(ok=False, error=f"Archivo no existe: {ruta}")

    # Detectar MIME
    mime, _ = mimetypes.guess_type(str(ruta))
    if mime is None:
        ext = ruta.suffix.lower()
        mime = {
            ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
            ".gif": "image/gif", ".webp": "image/webp", ".bmp": "image/bmp",
        }.get(ext, "application/octet-stream")

    # PDFs no son imágenes nativas; Gemini los acepta como inline_data con
    # application/pdf, pero OpenAI-compat requiere otro enfoque. Por ahora
    # advertimos si es PDF y el proveedor no es Gemini.
    if mime == "application/pdf" and prov.familia != "gemini":
        return ResultadoIA(
            ok=False,
            error="Sólo Google Antigravity (Gemini) acepta PDFs directamente. "
            "Convierte a imagen o usa Gemini.",
        )

    try:
        b64 = base64.b64encode(ruta.read_bytes()).decode("ascii")
    except Exception as exc:
        return ResultadoIA(ok=False, error=f"Leyendo archivo: {exc}")

    system = (
        "Eres un experto redactor jurídico de INDECOPI y un analista de estilo. "
        "Extrae con precisión milimétrica los detalles técnicos, estilísticos y "
        "de formato del documento proporcionado."
    )
    try:
        texto = _vision(prov, system, instruccion, b64, mime, timeout=timeout)
        return ResultadoIA(ok=True, texto=texto, proveedor_usado=prov.nombre)
    except RuntimeError as exc:
        return ResultadoIA(ok=False, error=str(exc))


def listar_proveedores_disponibles() -> list[tuple[str, str, bool, bool]]:
    """Devuelve [(id, nombre, disponible, soporta_vision)] para la GUI."""
    out: list[tuple[str, str, bool, bool]] = []
    for pid in ORDEN_PREFERENCIA:
        if pid in PROVEEDORES:
            prov = PROVEEDORES[pid]
            out.append((pid, prov.nombre, bool(prov.api_key()), prov.soporta_vision))
    # Proveedores fuera del orden preferido (openai_compat)
    for pid, prov in PROVEEDORES.items():
        if pid not in ORDEN_PREFERENCIA:
            out.append((pid, prov.nombre, bool(prov.api_key()), prov.soporta_vision))
    return out
