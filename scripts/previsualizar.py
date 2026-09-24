# -*- coding: utf-8 -*-
"""Vista de cada pagina del admisorio, como la vera el instructor en Word (v3.1).

Por que existe (24/09/2026): la revision pagina por pagina del admisorio de
prueba 9999-2026 encontro 38 defectos; la mayoria (notas corridas, huecos,
negritas, subrayados, firma) no se ven leyendo XML, se ven MIRANDO la pagina.
Este comando deja en `<carpeta>/_vista/` una imagen por pagina del Word y, con
`--contra`, la misma pagina de la plantilla a su lado.

Sin Word ni win32com (prohibidos). Motor, por orden de fidelidad a Word:

1. **ONLYOFFICE Document Builder** (gratuito; su motor de maquetacion imita el
   de Microsoft Word). Medido en el 9998-2026: dibuja las notas al pie como
   Word (llamada a 0, texto a 1 cm) con el Word tal cual.
2. **LibreOffice** sin ventana, solo si ONLYOFFICE no esta. Se come la primera
   tabulacion de cada nota; para que la vista no engañe, en la COPIA temporal
   esa tabulacion se dibuja como un espacio fijo hasta 1 cm. Las imagenes llevan
   el rotulo «VISTA APROXIMADA (LibreOffice)».

El Word del caso nunca se toca: se convierte una copia a un PDF TEMPORAL fuera
de la carpeta del caso (R-125), PyMuPDF lo pasa a imagenes y todo se borra.
Si la letra del documento no esta instalada y el motor la sustituye por otra de
distinta metrica, se avisa: la paginacion de la vista podria no ser la de Word.

`PREVISUALIZAR_MOTOR=libreoffice` fuerza el respaldo (para comparar).

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


RUTAS_DOCBUILDER = (
    r"C:\Program Files\ONLYOFFICE\DocumentBuilder\docbuilder.exe",
    r"C:\Program Files (x86)\ONLYOFFICE\DocumentBuilder\docbuilder.exe",
    "/opt/onlyoffice/documentbuilder/docbuilder",
    "/Applications/ONLYOFFICE DocumentBuilder.app/Contents/MacOS/docbuilder",
)
# Letras que se ven como Arial Narrow (misma metrica): la paginacion se conserva.
LETRAS_FIELES = ("ARIALNARROW", "ARIAL NARROW", "LIBERATIONSANSNARROW", "LIBERATION SANS NARROW")


def docbuilder() -> str | None:
    ruta = shutil.which("docbuilder")
    if ruta:
        return ruta
    return next((r for r in RUTAS_DOCBUILDER if os.path.exists(r)), None)


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


def _pdf_onlyoffice(exe: str, copia: Path, tmp: Path) -> Path:
    pdf = tmp / "vista.pdf"
    guion = tmp / "vista.docbuilder"
    a = copia.resolve().as_posix()
    b = pdf.resolve().as_posix()
    guion.write_text(
        'builder.OpenFile("%s");\nbuilder.SaveFile("pdf", "%s");\nbuilder.CloseFile();\n' % (a, b),
        encoding="utf-8",
    )
    subprocess.run([exe, str(guion)], capture_output=True, timeout=180, cwd=str(tmp))
    return pdf


def _pdf_libreoffice(exe: str, copia: Path, tmp: Path) -> Path:
    _como_word(copia)
    perfil = (tmp / "perfil").resolve().as_uri()
    subprocess.run(
        [exe, "-env:UserInstallation=" + perfil, "--headless", "--convert-to", "pdf", "--outdir", str(tmp), str(copia)],
        capture_output=True,
        timeout=180,
    )
    return tmp / (copia.stem + ".pdf")


def motores() -> list[tuple[str, str]]:
    """(nombre, ejecutable) en orden de fidelidad; PREVISUALIZAR_MOTOR fuerza uno."""
    lista = []
    ob, lo = docbuilder(), soffice()
    if ob:
        lista.append(("ONLYOFFICE", ob))
    if lo:
        lista.append(("LibreOffice", lo))
    forzado = os.environ.get("PREVISUALIZAR_MOTOR", "").lower()
    if forzado:
        lista = [m for m in lista if m[0].lower() == forzado] or lista
    return lista


def letras_sustituidas(pdf: Path) -> list[str]:
    """Familias del PDF que no tienen la metrica de Arial Narrow."""
    import fitz  # PyMuPDF

    raras = set()
    with fitz.open(str(pdf)) as doc:
        for p in doc:
            for f in p.get_fonts():
                nombre = f[3].split("+", 1)[-1]
                clave = re.sub(r"[-,](Bold|Italic|BoldItalic|Regular).*$", "", nombre, flags=re.I).upper()
                if not any(clave.replace(" ", "").startswith(x.replace(" ", "")) for x in LETRAS_FIELES):
                    raras.add(nombre)
    # El membrete institucional lleva su propia letra (cursiva del encabezado):
    # solo se informa, no invalida la vista.
    return sorted(raras)


def paginas_png(docx: Path, destino: Path, prefijo: str, dpi: int = 100) -> tuple[list[Path], str, list[str]]:
    """Word -> PDF temporal -> un PNG por pagina en `destino`.

    Devuelve (imagenes, motor usado, letras sustituidas)."""
    import fitz  # PyMuPDF

    candidatos = motores()
    if not candidatos:
        raise FileNotFoundError(
            "no hay motor de vista: instala ONLYOFFICE Document Builder (recomendado) o LibreOffice"
        )
    with tempfile.TemporaryDirectory(prefix="vista_") as t:
        tmp = Path(t)
        ultimo_error = ""
        for nombre, exe in candidatos:
            copia = tmp / ("vista_%s.docx" % nombre.lower())
            shutil.copyfile(docx, copia)
            try:
                pdf = (_pdf_onlyoffice if nombre == "ONLYOFFICE" else _pdf_libreoffice)(exe, copia, tmp)
            except subprocess.TimeoutExpired:
                ultimo_error = "%s no respondio en 180 s" % nombre
                continue
            if not pdf.exists() or pdf.stat().st_size == 0:
                ultimo_error = "%s no pudo convertir %s" % (nombre, docx.name)
                continue
            raras = letras_sustituidas(pdf)
            salida = []
            with fitz.open(str(pdf)) as doc:
                for p in doc:
                    png = destino / ("%s_%02d.png" % (prefijo, p.number + 1))
                    p.get_pixmap(dpi=dpi).save(str(png))
                    salida.append(png)
            _rotular(salida, nombre)
            return salida, nombre, raras
        raise RuntimeError(ultimo_error or "ningun motor pudo convertir %s" % docx.name)


def _rotular(pngs: list[Path], motor: str) -> None:
    """Rotulo del motor sobre cada imagen: una vista aproximada no se confunde
    con la de Word."""
    from PIL import Image, ImageDraw

    texto = "Vista ONLYOFFICE (fiel a Word)" if motor == "ONLYOFFICE" else "VISTA APROXIMADA (LibreOffice): notas y tabulaciones simuladas"
    for png in pngs:
        img = Image.open(png).convert("RGB")
        lienzo = Image.new("RGB", (img.width, img.height + 22), "white")
        lienzo.paste(img, (0, 22))
        ImageDraw.Draw(lienzo).text((6, 5), texto, fill=(0, 90, 0) if motor == "ONLYOFFICE" else (170, 0, 0))
        lienzo.save(png)


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


def previsualizar(docx: Path, contra: Path | None = None) -> tuple[list[Path], str, list[str]]:
    carpeta = docx.parent
    destino = carpeta / "_vista"
    destino.mkdir(exist_ok=True)
    for viejo in destino.glob("*.png"):
        viejo.unlink()
    propias, motor, raras = paginas_png(docx, destino, "pagina")
    if not contra:
        return propias, motor, raras
    with tempfile.TemporaryDirectory(prefix="vista_base_") as t:
        base, _m, _r = paginas_png(contra, Path(t), "base")
        pares = []
        for k in range(max(len(propias), len(base))):
            a = propias[k] if k < len(propias) else None
            b = base[k] if k < len(base) else None
            pares.append(lado_a_lado(a, b, destino / ("comparada_%02d.png" % (k + 1))))
    for p in propias:
        p.unlink()
    return pares, motor, raras


def main(argv: list[str]) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("docx")
    ap.add_argument("--contra")
    a = ap.parse_args(argv[1:])
    try:
        hechas, motor, raras = previsualizar(Path(a.docx), Path(a.contra) if a.contra else None)
    except (FileNotFoundError, RuntimeError) as exc:
        print("  AVISO  sin vista: %s" % exc)
        return 0
    print("  Motor: %s%s" % (motor, "" if motor == "ONLYOFFICE" else "  (VISTA APROXIMADA: instala ONLYOFFICE Document Builder para una vista fiel a Word)"))
    if raras:
        print("  AVISO  letras sin la metrica de Arial Narrow en la vista: %s" % ", ".join(raras[:6]))
        print("         Si alguna es del cuerpo, la paginacion de la vista puede no ser la de Word.")
    print("  %d imagen(es) en %s" % (len(hechas), Path(a.docx).parent / "_vista"))
    for h in hechas:
        print("    %s" % h.name)
    print("  Miralas TODAS en una vuelta antes de entregar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
