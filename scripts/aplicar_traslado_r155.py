#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Normalizador de la formula de traslado y descargos (R-155).

La version anterior de este script horneo en 594 plantillas "Decreto Legislativo
N° 8079", "meritadas" y la volada, y decidia singular o plural por el NOMBRE DE
LA CARPETA: 369 plantillas de un solo denunciado quedaron con "presenten". La
formula corregida (D1, P1 del 23/09/2026) y el numero real de denunciados viven
ahora en un solo sitio, `scripts/migraciones/migrar_v3_parte1.py`; este script
solo delega en el para no mantener dos copias de la formula.

Uso:
    python scripts/aplicar_traslado_r155.py [--aplicar]
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "migraciones"))

# HISTORICO (v3.0). Desde v3.5 (R-212) el traslado es «correr traslado de la denuncia del …»:
# lo pone y sincroniza scripts/migraciones/traslado_denuncia.py (tambien desde sanear_admisorio.py).
import migrar_v3_parte1  # noqa: E402

FORMULA = migrar_v3_parte1.FORMULA
SINGULAR = migrar_v3_parte1.SINGULAR
PLURAL = migrar_v3_parte1.PLURAL

if __name__ == "__main__":
    sys.exit(migrar_v3_parte1.main())
