"""ResAdmi - Motor determinista para generación de resoluciones admisorias INDECOPI (CC1).

Paquete principal. Los módulos clave son:
- ``rules_engine``  — validación determinista de las 80 reglas (R-01..R-80).
- ``system_prompt`` — prompt blindado inyectado a la IA.
- ``ai_client``     — cliente Z.ai GLM (con fallback configurable).
- ``builder``       — clonado de plantilla base + inyección de texto.
- ``footnote_injector`` — notas al pie nativas vía win32com.
- ``gui``           — interfaz Tkinter para el ejecutable.
"""

__version__ = "2.0.0"
__all__ = [
    "rules_engine",
    "system_prompt",
    "ai_client",
    "builder",
    "footnote_injector",
    "aprendizaje_reglas",
    "extractor_pdfs",
]
