# -*- coding: utf-8 -*-
"""Vista de cada pagina del admisorio, como la vera el instructor (v3.1).

Por que existe (24/09/2026): la revision pagina por pagina del admisorio de
prueba 9999-2026 encontro 38 defectos; la mayoria (notas corridas, huecos,
negritas, subrayados, firma) no se ven leyendo XML, se ven MIRANDO la pagina.
Este comando deja en `<carpeta>/_vista/` una imagen por pagina del Word y, con
`--contra`, la misma pagina de la plantilla a su lado.

Sin Word ni win32com (prohibidos): LibreOffice en modo sin ventana convierte el
Word a un PDF TEMPORAL fuera de la carpeta del caso (R-125: ningun PDF en la
carpeta), PyMuPDF lo pasa a imagenes y el PDF se borra. Arial Narrow se sustituye
por Liberation Sans Narrow cuando no esta instalada (mismas metricas: la
paginacion no cambia).

Uso (lo llama `admisorio.py previsualizar`):
    python scripts/previsualizar.py <admisorio.docx> [--contra <plantilla.docx>]
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RUTAS_SOFFICE = (
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    "/usr/bin/soffice",
    "/usr/lib/libreoffice/program/soffice",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
)


def soffice() -> str | None:
    for nombre in ("soffice", "libreoffice"):
        ruta = shutil.which(nombre)
        if ruta:
            return ruta
    return next((r for r in RUTAS_SOFFICE if os.path.exists(r)), None)


def _como_word(copia: Path) -> None:
    """Solo en la copia temporal de la vista, nunca en el Word del caso.

    LibreOffice se come la PRIMERA tabulacion de cada nota al pie (medido: con
    la marca canonica de Word --llamada, tabulacion, texto-- el texto queda
    pegado al numero; si se quita esa tabulacion, se come la del parrafo
    siguiente). Word lleva ambas al tope de 1 cm. Para que la vista muestre lo
    que vera el instructor en Word, cada tabulacion inicial de un parrafo de nota
    se dibuja como un espacio de ancho fijo hasta 1 cm."""
    import zipfile

    with zipfile.ZipFile(copia) as z:
        items = [(i, z.read(i.filename)) for i in z.infolist()]
    datos = dict((i.filename, d) for i, d in items)
    fx = datos.get("word/footnotes.xml", b"").decode("utf-8")
    if not fx:
        return
    token = re.compile(r"<w:tab/>|<w:t(?:\s[^>/]*)?>([^<]*)</w:t>")

    def _espacio(pt: float) -> str:
        return (
            '<w:r><w:rPr><w:sz w:val="16"/><w:spacing w:val="%d"/></w:rPr>'
            '<w:t xml:space="preserve"> </w:t></w:r>' % max(0, int((pt - 1.8) * 20))
        )

    def _parrafo(p: str, digitos: int) -> str:
        ini = 0
        marca = p.find("<w:footnoteRef/>")
        if marca >= 0:
            ini = p.find("</w:r>", marca) + len("</w:r>")
        t = next(
            (m for m in token.finditer(p, ini) if m.group(0) == "<w:tab/>" or m.group(1).strip()),
            None,
        )
        if not t or t.group(0) != "<w:tab/>":
            return p
        ancho = 28.35 - (3.0 * digitos if marca >= 0 else 0)
        # el espacio va delante del run que contenia la tabulacion
        aperturas = [m.start() for m in re.finditer(r"<w:r(?:\s[^>]*)?>", p[:t.start()]) if m.start() >= ini]
        run_ini = aperturas[-1] if aperturas else t.start()
        return p[:run_ini] + _espacio(ancho) + p[run_ini:t.start()] + p[t.end():]

    def _nota(m):
        cuerpo = m.group(0)
        nid = re.search(r'w:id="(-?\d+)"', cuerpo).group(1)
        if int(nid) <= 0:
            return cuerpo
        return re.sub(
            r"<w:p\b[^>]*>.*?</w:p>",
            lambda q: _parrafo(q.group(0), len(nid)),
            cuerpo,
            flags=re.S,
        )

    fx = re.sub(r"<w:footnote\b[^>]*>.*?</w:footnote>", _nota, fx, flags=re.S)
    with zipfile.ZipFile(copia, "w", zipfile.ZIP_DEFLATED) as z:
        for info, d in items:
            if info.filename == "word/footnotes.xml":
                d = fx.encode("utf-8")
            z.writestr(info, d)


def paginas_png(docx: Path, destino: Path, prefijo: str, dpi: int = 100) -> list[Path]:
    """Word -> PDF temporal -> un PNG por pagina en `destino`."""
    import fitz  # PyMuPDF

    exe = soffice()
    if not exe:
        raise FileNotFoundError(
            "LibreOffice no esta instalado: sin el no hay vista (instalalo o revisa en Word a mano)"
        )
    with tempfile.TemporaryDirectory(prefix="vista_") as t:
        tmp = Path(t)
        copia = tmp / "vista.docx"
        shutil.copyfile(docx, copia)
        _como_word(copia)
        perfil = (tmp / "perfil").resolve().as_uri()
        subprocess.run(
            [exe, "-env:UserInstallation=" + perfil, "--headless", "--convert-to", "pdf", "--outdir", str(tmp), str(copia)],
            capture_output=True,
            timeout=180,
        )
        pdf = tmp / "vista.pdf"
        if not pdf.exists():
            raise RuntimeError("LibreOffice no pudo convertir %s" % docx.name)
        salida = []
        with fitz.open(str(pdf)) as doc:
            for p in doc:
                png = destino / ("%s_%02d.png" % (prefijo, p.number + 1))
                p.get_pixmap(dpi=dpi).save(str(png))
                salida.append(png)
    return salida


def lado_a_lado(izq: Path | None, der: Path | None, salida: Path) -> Path:
    from PIL import Image, ImageDraw

    imgs = [Image.open(p) if p else None for p in (izq, der)]
    ancho = max(i.width for i in imgs if i)
    alto = max(i.height for i in imgs if i)
    lienzo = Image.new("RGB", (ancho * 2 + 24, alto + 30), "white")
    d = ImageDraw.Draw(lienzo)
    for k, (img, rotulo) in enumerate(zip(imgs, ("ADMISORIO", "PLANTILLA BASE"))):
        x = k * (ancho + 24)
        d.text((x + 8, 8), rotulo, fill="black")
        if img:
            lienzo.paste(img, (x, 30))
        else:
            d.text((x + 8, 60), "(sin pagina)", fill="gray")
    lienzo.save(salida)
    return salida


def previsualizar(docx: Path, contra: Path | None = None) -> list[Path]:
    carpeta = docx.parent
    destino = carpeta / "_vista"
    destino.mkdir(exist_ok=True)
    for viejo in destino.glob("*.png"):
        viejo.unlink()
    propias = paginas_png(docx, destino, "pagina")
    if not contra:
        return propias
    with tempfile.TemporaryDirectory(prefix="vista_base_") as t:
        base = paginas_png(contra, Path(t), "base")
        pares = []
        for k in range(max(len(propias), len(base))):
            a = propias[k] if k < len(propias) else None
            b = base[k] if k < len(base) else None
            pares.append(lado_a_lado(a, b, destino / ("comparada_%02d.png" % (k + 1))))
    for p in propias:
        p.unlink()
    return pares


def main(argv: list[str]) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("docx")
    ap.add_argument("--contra")
    a = ap.parse_args(argv[1:])
    try:
        hechas = previsualizar(Path(a.docx), Path(a.contra) if a.contra else None)
    except (FileNotFoundError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print("  AVISO  sin vista: %s" % exc)
        return 0
    print("  %d imagen(es) en %s" % (len(hechas), Path(a.docx).parent / "_vista"))
    for h in hechas:
        print("    %s" % h.name)
    print("  Miralas TODAS en una vuelta antes de entregar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
