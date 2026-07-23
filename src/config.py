"""Configuración de ResAdmi.

Carga desde ``settings.json`` (en el directorio del usuario o junto al exe) o
variables de entorno. Nunca lanza; usa defaults razonables.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path


def _directorio_app() -> Path:
    """Directorio base para config/plantillas.

    - Si estamos en un exe PyInstaller: junto al exe.
    - Si no: directorio del repo (subiendo un nivel desde src/).
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def _directorio_usuario() -> Path:
    """Directorio %APPDATA%/ResAdmi para preferencias persistentes."""
    base = os.environ.get("APPDATA") or str(Path.home())
    p = Path(base) / "ResAdmi"
    p.mkdir(parents=True, exist_ok=True)
    return p


APP_DIR = _directorio_app()
USER_DIR = _directorio_usuario()


@dataclass
class Settings:
    # Rutas
    plantilla_maestra: str = ""  # path absoluto a la plantilla .docx
    directorio_salida: str = ""
    directorio_plantillas: str = ""

    # IA — Gemini (Google Antigravity) es el PRINCIPAL por su capacidad de visión.
    # Z.ai GLM es el SECUNDARIO por defecto.
    proveedor_ia: str = "gemini"
    proveedores_preferidos: list[str] = field(
        default_factory=lambda: ["gemini", "zai", "bigmodel", "deepseek", "kimi"]
    )
    reintentos_ia: int = 2

    # Word
    word_visible: bool = False

    # Proyectista
    iniciales: str = "LGP/JCQ"

    @classmethod
    def cargar(cls) -> "Settings":
        """Carga desde settings.json (directorio usuario), fallback a defaults."""
        s = cls()
        ruta_json = USER_DIR / "settings.json"
        if ruta_json.exists():
            try:
                data = json.loads(ruta_json.read_text(encoding="utf-8"))
                for k, v in data.items():
                    if hasattr(s, k):
                        setattr(s, k, v)
            except Exception:
                pass

        # Defaults sensibles si no seteados
        if not s.directorio_plantillas:
            s.directorio_plantillas = str(APP_DIR / "templates")
        if not s.directorio_salida:
            s.directorio_salida = str(USER_DIR / "salida")
        Path(s.directorio_salida).mkdir(parents=True, exist_ok=True)

        # Auto-detectar plantilla maestra en templates/
        if not s.plantilla_maestra:
            tpl_dir = Path(s.directorio_plantillas)
            if tpl_dir.exists():
                candidatos = sorted(tpl_dir.glob("*.docx"))
                # Preferir la que tenga "MODELO" o "MAESTRA" en el nombre
                prioritarios = [c for c in candidatos if "MAESTRA" in c.stem.upper()]
                if prioritarios:
                    s.plantilla_maestra = str(prioritarios[0])
                elif candidatos:
                    s.plantilla_maestra = str(candidatos[0])

        # Variables de entorno pisan (ej. RESADMI_PROVEEDOR_IA)
        if v := os.environ.get("RESADMI_PROVEEDOR_IA"):
            s.proveedor_ia = v
        if v := os.environ.get("RESADMI_PLANTILLA"):
            s.plantilla_maestra = v
        return s

    def guardar(self) -> None:
        ruta = USER_DIR / "settings.json"
        data = {
            "plantilla_maestra": self.plantilla_maestra,
            "directorio_salida": self.directorio_salida,
            "directorio_plantillas": self.directorio_plantillas,
            "proveedor_ia": self.proveedor_ia,
            "proveedores_preferidos": self.proveedores_preferidos,
            "reintentos_ia": self.reintentos_ia,
            "word_visible": self.word_visible,
            "iniciales": self.iniciales,
        }
        ruta.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
