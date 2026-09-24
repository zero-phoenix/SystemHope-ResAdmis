#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprobaciones que el repositorio se hace a si mismo. Las ejecuta CI.

No son pruebas de la redaccion --de eso se ocupan `verificar_admisorio.py` y
`auditar_admisorio.py` sobre cada documento--. Son las comprobaciones de que **el
propio sistema no esta roto de una forma que nadie notaria**, que es la clase de
defecto que mas caro salio (R-141).

Cuatro, y cada una nace de un fallo real:

1. **Ningun caracter de retroceso en una expresion regular.** Escribir un limite
   de palabra como escape literal se ha colapsado **tres veces** en este
   repositorio, dejando un `0x08` donde debia ir el limite. La peor: los cinco
   patrones de R-110, que estuvieron declarando OK sin comprobar nada.
2. **Ninguna plantilla con datos personales.** El repositorio es publico. El
   15/09/2026 las 630 plantillas llevaban el apellido del consumidor que las
   origino.
3. **Todos los scripts compilan.** Se compila, no se importa: importar los
   ejecuta, y una prueba que modifica el repositorio que comprueba no es una
   prueba. Lo descubri cuando una de ellas reescribio un JSON de `docs/`.
4. **Ningun artefacto de trabajo rastreado.** Mapas, volcados y scratch llevan
   nombres de personas y no entran al repositorio.

Uso:
    python scripts/autocomprobacion.py
"""

from __future__ import annotations

import re
import subprocess
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

RETROCESO = bytes([8])
RE_TRATAMIENTO = re.compile(
    r"(?:señor|señora|señorita)\s+(?!\[)" r"[A-ZÁÉÍÓÚÑ][\wáéíóúñ]{2,}",
    re.I,
)
RE_DNI = re.compile(r"\bDNI\s*(?:N\.?[°º]|N[°º])?\s*\d{8}\b", re.I)

ARTEFACTOS = (
    "mapa*.json",
    "tpl*.txt",
    "scratch*",
    "_texto_expediente.txt",
    "_ORDEN_DE_TRABAJO.md",
    "_CEDULA.md",
    "gen_map.py",
    "make_map.py",
    "temp_*",
)


def texto_docx(ruta: Path) -> str:
    p_str = str(ruta.resolve())
    if sys.platform == "win32" and not p_str.startswith("\\\\?\\"):
        p_str = "\\\\?\\" + p_str
    with zipfile.ZipFile(p_str) as z:
        partes = [
            z.read(n).decode("utf-8", "replace")
            for n in z.namelist()
            if n.startswith("word/") and n.endswith(".xml")
        ]
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", " ".join(partes)))


def sin_retrocesos() -> list[str]:
    fallos = []
    # rglob: el retroceso de `migraciones/notas_traslado.py` (23/09/2026) paso
    # inadvertido porque solo se miraba el primer nivel de scripts/.
    for py in sorted((RAIZ / "scripts").rglob("*.py")) + sorted(
        (RAIZ / "src").glob("*.py")
    ):
        crudo = py.read_bytes()
        if RETROCESO in crudo:
            lineas = [
                str(i) for i, ln in enumerate(crudo.split(b"\n"), 1) if RETROCESO in ln
            ]
            fallos.append(
                "%s tiene un caracter de retroceso (0x08) en la(s) linea(s) %s: "
                "casi seguro es un limite de palabra que se colapso"
                % (py.name, ", ".join(lineas))
            )
    return fallos


def plantillas_anonimas() -> list[str]:
    fallos = []
    plantillas = sorted((RAIZ / "plantillas_maestras").rglob("*.docx"))
    if not plantillas:
        return ["no hay ninguna plantilla en plantillas_maestras/"]
    for p in plantillas:
        try:
            t = texto_docx(p)
        except Exception as exc:
            fallos.append("%s no se puede abrir: %s" % (p.name, exc))
            continue
        m = RE_TRATAMIENTO.search(t) or RE_DNI.search(t)
        if m:
            fallos.append(
                "%s conserva un dato personal ('%s'). Ejecuta "
                "scripts/anonimizar_plantillas.py --aplicar" % (p.name[:60], m.group(0))
            )
    return fallos[:15]


def modulos_compilan() -> list[str]:
    """Compila, no importa.

    La primera version importaba cada modulo y con eso los **ejecutaba**: uno de
    ellos reescribio un JSON de `docs/` durante la comprobacion. Una prueba que
    modifica el repositorio que esta comprobando no es una prueba.
    """
    fallos = []
    for py in sorted((RAIZ / "scripts").glob("*.py")):
        try:
            compile(py.read_text(encoding="utf-8"), str(py), "exec")
        except SyntaxError as exc:
            fallos.append(
                "%s no compila: linea %s, %s" % (py.name, exc.lineno, exc.msg)
            )
    return fallos


def sin_artefactos() -> list[str]:
    rastreados = (
        subprocess.run(["git", "ls-files"], capture_output=True, cwd=RAIZ)
        .stdout.decode("utf-8", "replace")
        .splitlines()
    )
    fallos = []
    for patron in ARTEFACTOS:
        expresion = patron.replace("*", ".*").replace(".", r"\.", 1)
        for r in rastreados:
            nombre = r.split("/")[-1]
            if re.fullmatch(
                expresion.replace(r"\.", ".", 1).replace("*", ".*"), nombre
            ):
                fallos.append("'%s' es un artefacto de trabajo y esta rastreado" % r)
    return fallos


def agents_cabe() -> list[str]:
    """AGENTS.md debe caber en el limite de reglas de Antigravity (12 000
    caracteres): si no, el agente lo lee truncado y la regla que falta no existe
    para el. Medido el 24/09/2026: la v3.1 llego a 15 184 antes de condensarse."""
    n = len((RAIZ / "AGENTS.md").read_text(encoding="utf-8"))
    return [] if n <= 12000 else ["AGENTS.md tiene %d caracteres; el limite de Antigravity es 12 000" % n]


def auditor_meses() -> list[str]:
    """El auditor de fondo ancla una fecha aunque el expediente escriba
    «septiembre» y el admisorio «setiembre» (Exp. 2889-2026: falso «sin ancla»)."""
    sys.path.insert(0, str(RAIZ / "scripts"))
    import auditar_admisorio as A
    if A.normalizar("1 de septiembre de 2025") != A.normalizar("1 de setiembre de 2025"):
        return ["auditar_admisorio: «setiembre» y «septiembre» deben anclar la misma fecha"]
    return []


OCR_PROHIBIDO = re.compile(
    r"\b(?:import|from)\s+(?:pytesseract|easyocr|paddleocr|ocrmypdf|rapidocr\w*|doctr|kraken)\b"
    r"|get_textpage_ocr|\.ocr_page\(|tesseract_cmd"
)


def cero_ocr() -> list[str]:
    """R-137: la lectura es visual (captura completa de cada pagina); nunca OCR.

    Ningun script puede importar un motor de OCR ni pedirselo a PyMuPDF, y
    requirements.txt no puede instalarlo.
    """
    fallos = []
    for ruta in sorted((RAIZ / "scripts").rglob("*.py")) + sorted(
        (RAIZ / "src").rglob("*.py")
    ):
        if ruta.name == "autocomprobacion.py":
            continue
        texto = ruta.read_text(encoding="utf-8", errors="replace")
        m = OCR_PROHIBIDO.search(texto)
        if m:
            fallos.append("%s usa OCR: '%s'" % (ruta.relative_to(RAIZ), m.group(0)))
    req = (
        (RAIZ / "requirements.txt")
        .read_text(encoding="utf-8", errors="replace")
        .lower()
    )
    for lib in (
        "pytesseract",
        "easyocr",
        "paddleocr",
        "ocrmypdf",
        "rapidocr",
        "python-doctr",
    ):
        if re.search(r"^\s*%s\b" % lib, req, re.M):
            fallos.append("requirements.txt instala %s (OCR prohibido)" % lib)
    return fallos


def sin_elementtree_escribiendo() -> list[str]:
    """ElementTree renombra los prefijos (w14 -> ns2) y Word declara el .docx
    «contenido no legible»: fue la causa de las 577 plantillas corruptas de la
    v2.3.0. Leer con ElementTree vale; escribir XML de Word con el, no."""
    fallos = []
    for py in sorted((RAIZ / "scripts").rglob("*.py")):
        t = py.read_text(encoding="utf-8", errors="replace")
        if re.search(r"\b(?:ET|ElementTree)\.tostring\(|\.write\([^)]*xml_declaration", t):
            fallos.append("%s serializa XML con ElementTree" % py.relative_to(RAIZ))
    return fallos


def plantillas_abren_en_word() -> list[str]:
    """R-168 sobre todo el corpus: espacios de nombres completos."""
    import zipfile

    sys.path.insert(0, str(RAIZ / "scripts"))
    import reparar_espacios_nombres as R

    fallos = []
    for d in sorted((RAIZ / "plantillas_maestras").rglob("*.docx")):
        with zipfile.ZipFile(d) as z:
            if R.necesita(z):
                fallos.append("%s: espacios de nombres rotos" % d.name)
    return fallos[:10]


def main() -> int:
    bloques = (
        ("Sin retrocesos en expresiones regulares", sin_retrocesos),
        ("Plantillas sin datos personales", plantillas_anonimas),
        ("Todos los modulos compilan", modulos_compilan),
        ("Sin artefactos de trabajo rastreados", sin_artefactos),
        ("Cero OCR (R-137)", cero_ocr),
        ("AGENTS.md cabe en Antigravity (12 000 caracteres)", agents_cabe),
        ("El auditor ancla setiembre y septiembre por igual", auditor_meses),
        ("Nunca ElementTree escribiendo .docx", sin_elementtree_escribiendo),
        ("Plantillas que Word abre (R-168)", plantillas_abren_en_word),
    )
    print("=" * 78)
    print("AUTOCOMPROBACION DEL REPOSITORIO")
    print("=" * 78)
    total = 0
    for titulo, prueba in bloques:
        fallos = prueba()
        total += len(fallos)
        print("  %-5s %s" % ("FALLA" if fallos else "OK", titulo))
        for f in fallos:
            print("        - %s" % f)
    print()
    if total:
        print("  %d problema(s). El repositorio no esta sano." % total)
        return 1
    print("  Sin problemas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
