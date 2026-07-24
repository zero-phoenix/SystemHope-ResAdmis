"""Compatibilidad: use ``python generar.py casos/2142-2026.json``."""
from generar import main


if __name__ == "__main__":
    raise SystemExit(main(["casos/2142-2026.json"]))
