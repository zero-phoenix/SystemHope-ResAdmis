"""CLI mínimo para ResAdmi (alternativa a la GUI).

Uso:
    python -m src.cli --expediente 0955-2026/CC1 --hechosHechos archivo.txt

Útil para automatización o testing sin Tkinter.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .app import generar_resolucion
from .config import Settings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generar resolución admisoria INDECOPI (CC1).")
    parser.add_argument("--expediente", required=True, help="ej. 0955-2026/CC1")
    parser.add_argument("--denunciante", required=True)
    parser.add_argument("--denunciados", nargs="+", required=True,
                        help='Lista "Razón Social|rubro" donde rubro=aseguradora|banco|otro')
    parser.add_argument("--resolucion", type=int, default=1)
    parser.add_argument("--hechos", help="Archivo de texto con la descripción de hechos")
    parser.add_argument("--proveedor", default="zai")
    parser.add_argument("--borrador-json", help="Saltar IA y usar este JSON como borrador")
    parser.add_argument("--salida", help="Sobrescribir directorio de salida")
    args = parser.parse_args(argv)

    settings = Settings.cargar()
    settings.proveedor_ia = args.proveedor
    if args.salida:
        settings.directorio_salida = args.salida

    if args.borrador_json:
        borrador = json.loads(Path(args.borrador_json).read_text(encoding="utf-8"))
        datos = {}
        reporte = generar_resolucion(datos, settings, saltar_ia=True, borrador_predefinido=borrador)
    else:
        if not args.hechos:
            print("ERROR: --hechos es requerido salvo en modo --borrador-json", file=sys.stderr)
            return 2
        descripcion = Path(args.hechos).read_text(encoding="utf-8")
        denunciados = []
        for d in args.denunciados:
            if "|" in d:
                rs, rubro = d.rsplit("|", 1)
            else:
                rs, rubro = d, "otro"
            denunciados.append({"razon_social": rs, "rubro": rubro})
        datos = {
            "expediente": args.expediente,
            "denunciante": args.denunciante,
            "denunciados": denunciados,
            "resolucion_numero": args.resolucion,
            "descripcion_hechos": descripcion,
        }
        reporte = generar_resolucion(datos, settings)

    print(json.dumps(reporte.to_dict(), indent=2, ensure_ascii=False))
    return 0 if reporte.ok else 1


if __name__ == "__main__":
    sys.exit(main())
