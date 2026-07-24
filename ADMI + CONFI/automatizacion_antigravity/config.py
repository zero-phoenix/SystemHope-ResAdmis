import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = Path(os.environ.get("RESADMI_TEMPLATE_DIR", REPO_ROOT / "Modelos al 30-06-26"))
PRODUCTOS_DIR = Path(os.environ.get(
    "RESADMI_OUTPUT_DIR",
    REPO_ROOT / "productos (resoluciones) elaborada por google antigravity",
))
SCRATCH_DIR = REPO_ROOT / "automatizacion_antigravity" / ".scratch"
SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
PRODUCTOS_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATE_PATH = TEMPLATE_DIR / "MODELO xxxx exp. ADM ver. David 1 DDO,  VARIAS IMPUTACIONES.docx"
