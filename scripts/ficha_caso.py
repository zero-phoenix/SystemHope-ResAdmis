#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ficha del caso: todo lo que el agente iba a buscar suelto, en un solo archivo.

Por que existe (traza del Exp. 2898-2026, 23/09/2026): el tiempo no lo gastan los
scripts (similares.py tarda 7 s) sino las DECISIONES del modelo, 45-70 s cada
una. De unas 50 decisiones, ~25 eran evitables:
  - 5 llamadas `-h` para aprender la sintaxis de los scripts;
  - 3 lecturas de docs/tabla_tipificacion.json, 2 de casillas_habilitadas.json,
    la lectura del codigo de similares.py y 6 busquedas grep;
  - 13 capturas vistas una a una.
`preparar` escribe `<carpeta>/_FICHA.md` con los comandos exactos, las fechas de
firma digital, los proveedores detectados (casilla y via historica) y la tabla de
tipificacion; y `<carpeta>/_hojas/` con las paginas de dos en dos.

Uso (lo llama preparar):
    python scripts/ficha_caso.py <carpeta>
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import extraer_expediente  # noqa: E402


def _norm(t: str) -> str:
    t = unicodedata.normalize("NFD", t.upper())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^A-Z0-9]+", " ", t).strip()


def proveedores(texto: str) -> list[str]:
    """Proveedores del padron de casillas cuyo nombre aparece en el expediente."""
    cas = json.loads(
        (RAIZ / "docs/casillas_habilitadas.json").read_text(encoding="utf-8")
    )
    dire = json.loads(
        (RAIZ / "docs/directorio_proveedores_domicilios.json").read_text(
            encoding="utf-8"
        )
    )
    t = " %s " % _norm(texto)
    filas = []
    for nombre, v in cas.get("proveedores", {}).items():
        clave = _norm(nombre)
        clave = re.sub(r"\b(S A A|S A C|S A|SA|EAFC)$", "", clave).strip()
        if len(clave) >= 8 and (" %s " % clave) in t:
            via = "?"
            for d in dire.values():
                if (
                    isinstance(d, dict)
                    and _norm(d.get("denominacion", ""))[:18] == clave[:18]
                ):
                    via = d.get("via_notificacion_oficial", "?")
                    break
            filas.append(
                "| %s | %s | %s | %s |"
                % (
                    nombre,
                    "HABILITADA" if v.get("casilla_habilitada") else "PROHIBIDA",
                    v.get("motivo", ""),
                    via,
                )
            )
    return filas


def tipificacion() -> list[str]:
    t = json.loads((RAIZ / "docs/tabla_tipificacion.json").read_text(encoding="utf-8"))
    lineas = ["Regla: " + t["regla"], "Prohibidas: " + ", ".join(t["prohibidas"])]
    lineas += ["Excepcional: %s — %s" % kv for kv in t["excepcionales"].items()]
    lineas.append("")
    for h in t["hechos"]:
        lineas.append(
            "- %s. %s → %s" % (h["item"], h["hecho"], " / ".join(h["normas"]))
        )
    return lineas


def hojas(carpeta: Path, por_hoja: int = 2) -> list[Path]:
    """Une las capturas de pagina de dos en dos: menos imagenes, misma lectura."""
    from PIL import Image

    pags = sorted(
        p for p in (carpeta / "_paginas").glob("*.png") if not p.name.startswith("_")
    )
    destino = carpeta / "_hojas"
    destino.mkdir(exist_ok=True)
    for viejo in destino.glob("*.png"):
        viejo.unlink()
    salida = []
    for k in range(0, len(pags), por_hoja):
        grupo = [Image.open(p).convert("RGB") for p in pags[k : k + por_hoja]]
        alto = 1500
        grupo = [g.resize((int(g.width * alto / g.height), alto)) for g in grupo]
        hoja = Image.new(
            "RGB", (sum(g.width for g in grupo) + 20 * (len(grupo) - 1), alto), "white"
        )
        x = 0
        for g in grupo:
            hoja.paste(g, (x, 0))
            x += g.width + 20
        r = destino / ("hoja_%02d.png" % (k // por_hoja + 1))
        hoja.save(r)
        salida.append((r, [p.name for p in pags[k : k + por_hoja]]))
    return salida


def escribir(carpeta: Path) -> Path:
    carpeta = carpeta.resolve()
    py = Path(sys.executable)
    txt = carpeta / "_texto_expediente.txt"
    texto = txt.read_text(encoding="utf-8", errors="replace") if txt.exists() else ""
    L = ["# Ficha del caso — %s" % carpeta.name, ""]
    L += [
        "Todo lo necesario para redactar sin buscar nada más en el repositorio.",
        "**No uses `-h`, no leas scripts ni JSON del repositorio: está aquí.**",
        "",
        "## Comandos exactos (cópialos tal cual; `run_command` con WaitMsBeforeAsync 120000)",
        "```",
        '& "%s" "%s" "%s"' % (py, RAIZ / "scripts/similares.py", carpeta),
        '& "%s" "%s" --mapa "%s"'
        % (py, RAIZ / "scripts/construir_admisorio.py", carpeta / "mapa.json"),
        '& "%s" "%s" "%s" --diff "<plantilla base>"'
        % (py, RAIZ / "scripts/inspeccionar_docx.py", carpeta / "ADM <EXP> R<N>.docx"),
        '& "%s" "%s" previsualizar "%s" --contra "<plantilla base>"'
        % (py, RAIZ / "scripts/admisorio.py", carpeta / "ADM <EXP> R<N>.docx"),
        '& "%s" "%s" entregar "%s" --recepcion DD/MM/AAAA'
        % (py, RAIZ / "scripts/admisorio.py", carpeta / "ADM <EXP> R<N>.docx"),
        "```",
        "`previsualizar` deja en `_vista/` cada página del Word como imagen, al lado de la misma página de la "
        "plantilla: míralas TODAS en una vuelta antes de entregar (notas, huecos, negritas, subrayados, firma).",
        'mapa.json: {"plantilla": "plantillas_maestras/...docx", "salida": "<carpeta>/ADM <EXP> R<N>.docx", '
        '"partes": ["alias", ...], "reemplazos": {"texto de la plantilla": "texto del caso", ...}}. '
        "Reemplaza párrafos enteros o frases; el formato de cada tramo se conserva. "
        "Para AÑADIR una imputación o un hecho: \"insertar_despues\": {\"fragmento del párrafo ancla\": [{\"texto\": \"...\", \"nota\": \"numeral 88.1 del artículo 88\"}]} "
        "(clona el párrafo ancla con su numeración; `nota` pone la nota normativa del corpus: docs/notas_normas.json).",
        "",
        "## Fechas de firma digital (escritos de parte = firma de mesa de partes)",
    ]
    for pdf in sorted(carpeta.glob("*.pdf")):
        f = extraer_expediente.firmas_digitales(pdf)
        L.append(
            "- `%s`: %s"
            % (pdf.name, "; ".join("%s (%s)" % x for x in f) or "sin firma digital")
        )
    L += [
        "",
        "## Proveedores detectados en el expediente",
        "",
        "| Padrón de casillas | Casilla | Motivo | Vía histórica |",
        "|---|---|---|---|",
    ]
    L += proveedores(texto) or [
        "| (ninguno reconocido: revisa el nombre en las páginas) | | | |"
    ]
    L += [
        "",
        "## Hojas de lectura visual (dos páginas por imagen)",
        "Ábrelas **todas en una misma vuelta** y llena una fila por página en `_LECTURA.md`.",
        "El formato medido de cada página (letra, tamaños, negritas, subrayados, alineación, encuadre, "
        "encabezado, pie, imágenes y campos de firma; estructura del PDF, cero OCR) está en `_FORMATO.md`: "
        "úsalo para la columna «Formato que vi».",
        "",
    ]
    for r, nombres in hojas(carpeta):
        L.append("- `_hojas/%s`: %s" % (r.name, ", ".join(nombres)))
    L += ["", "## Tabla de tipificación (referencial: mandan las plantillas)", ""] + tipificacion()
    destino = carpeta / "_FICHA.md"
    destino.write_text("\n".join(L) + "\n", encoding="utf-8")
    return destino


if __name__ == "__main__":
    print(escribir(Path(sys.argv[1])))
