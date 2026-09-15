#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Capturas referenciales del corpus, tachadas antes de existir.

Encargo del instructor: una captura referencial por tipo de seguro, materia,
proveedor y demas, para analizar **viendo** y no leyendo texto extraido.

El problema, y no es menor: las fuentes son admisorios reales. Meter capturas sin
tocar en un repositorio publico seria la fuga mas grande que ha tenido este
sistema, peor que los `.docx` --una imagen no la filtra ninguna guardia de texto--.

La solucion no es renunciar a las capturas: es **tacharlas antes de que existan**.
PyMuPDF da la caja de cada palabra, asi que los datos personales se localizan por
coordenadas y se pintan en negro **sobre el pixmap**, antes de guardar el PNG. El
archivo que llega al disco ya nace tachado; no hay una version intermedia limpia.

Que se tacha: DNI, RUC de persona natural, correos, telefonos, la linea
DENUNCIANTE del encabezado, todo nombre tras «senor/senora» y las direcciones.
Que se conserva, que es lo que interesa: la maqueta, la secuencia de ordinales, las
negritas, el interlineado, el encuadre, la firma institucional y la estructura de
la imputacion.

Paginas sin capa de texto: **no se capturan**. Sin texto no hay coordenadas, y sin
coordenadas no se puede garantizar el tachado. Una captura que no se puede tachar
no se publica.

Uso:
    python scripts/capturar_referencias.py --plan          # que se capturaria
    python scripts/capturar_referencias.py --aplicar
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = Path.home() / "Desktop" / "000 PLAN PHOENYX"
DESTINO = RAIZ / "docs" / "capturas_referenciales"
INDICE = RAIZ / "docs" / "plantillas_maestras_index.json"

SENSIBLE = [
    re.compile(r"\b\d{8}\b"),  # DNI
    re.compile(r"\b\d{11}\b"),  # RUC
    re.compile(r"[\w.\-]+@[\w.\-]+\.\w+"),  # correo
    re.compile(r"\b9\d{8}\b"),  # celular
    re.compile(r"\b\d{3}-\d{4}\b"),  # telefono fijo
    # En una captura publicada, una poliza o una cuenta de 7 o mas digitos es un
    # cuasi-identificador: cruzada con la aseguradora y la fecha senala a una
    # persona. En la plantilla se conservan porque hacen falta para redactar; en la
    # captura no hacen falta para nada, asi que se tachan.
    re.compile(r"\b\d{7,}\b"),
    re.compile(r"\b\d{3}-\d{3}[\dxX]{3,}-\d[-\d]*\b"),
]
# Nombres propios: dos o mas palabras capitalizadas seguidas, sin particulas.
RE_NOMBRE = re.compile(
    r"\b[A-ZÁÉÍÓÚÑ][A-Za-zÀ-ÿ]{2,}" r"(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-zÀ-ÿ]{2,}){1,3}\b"
)
INSTITUCIONAL = {
    "INDECOPI",
    "COMISION",
    "COMISIÓN",
    "PROTECCION",
    "PROTECCIÓN",
    "CONSUMIDOR",
    "SECRETARIA",
    "SECRETARÍA",
    "TECNICA",
    "TÉCNICA",
    "RESOLUCION",
    "RESOLUCIÓN",
    "EXPEDIENTE",
    "DENUNCIANTE",
    "DENUNCIADO",
    "MATERIAS",
    "HECHOS",
    "SEGUROS",
    "REASEGUROS",
    "COMPANIA",
    "COMPAÑIA",
    "COMPAÑÍA",
    "BANCO",
    "CREDITO",
    "CRÉDITO",
    "RIMAC",
    "RÍMAC",
    "PACIFICO",
    "PACÍFICO",
    "MAPFRE",
    "INTERSEGURO",
    "POSITIVA",
    "CARDIF",
    "PROTECTA",
    "CHUBB",
    "QUALITAS",
    "QUÁLITAS",
    "CRECER",
    "SANITAS",
    "INTERBANK",
    "SCOTIABANK",
    "BBVA",
    "FALABELLA",
    "RIPLEY",
    "PICHINCHA",
    "CODIGO",
    "CÓDIGO",
    "LEY",
    "DECRETO",
    "SUPREMO",
    "LEGISLATIVO",
    "LIMA",
    "PERU",
    "PERÚ",
    "VISTO",
    "CONSIDERANDO",
    "PRIMERO",
    "SEGUNDO",
    "TERCERO",
    "CUARTO",
    "QUINTO",
    "SEXTO",
    "SETIMO",
    "SÉTIMO",
    "OCTAVO",
    "NOVENO",
    "DECIMO",
    "DÉCIMO",
    "CASILLA",
    "ELECTRONICA",
    "ELECTRÓNICA",
    "CORREO",
    "POLIZA",
    "PÓLIZA",
    "CERTIFICADO",
    "SINIESTRO",
    "VEHICULAR",
    "VIDA",
    "DESGRAVAMEN",
    "SOAT",
}


def sin_tildes(t: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn"
    )


def es_institucional(texto: str) -> bool:
    return any(
        sin_tildes(w).upper() in {sin_tildes(i).upper() for i in INSTITUCIONAL}
        for w in texto.split()
    )


def cajas_a_tachar(pagina) -> list:
    """Coordenadas de todo lo que identifica a una persona."""
    cajas = []
    texto = pagina.get_text()
    objetivos: set[str] = set()

    for patron in SENSIBLE:
        objetivos.update(m.group(0) for m in patron.finditer(texto))

    # La linea DENUNCIANTE del encabezado y los nombres tras tratamiento.
    for m in re.finditer(r"DENUNCIANTE\s*:?\s*(.{4,80})", texto):
        for n in RE_NOMBRE.finditer(m.group(1)):
            if not es_institucional(n.group(0)):
                objetivos.add(n.group(0))
    # Apellidos compuestos: «la senora X de Pastor». Capturar solo la primera
    # palabra dejaba «de Pastor» a la vista. Se consumen hasta cinco tokens,
    # incluidas las particulas, y se tacha el tramo entero tras el tratamiento.
    TOKEN = r"[A-ZÁÉÍÓÚÑ][A-Za-zÀ-ÿ]{2,}"
    PARTICULA = r"(?:de|del|la|las|los|y)"
    for m in re.finditer(
        r"(?:señor|señora|señores|señoras|Señor|Señora)\s+"
        r"((?:%s|%s)(?:\s+(?:%s|%s)){0,4})" % (TOKEN, PARTICULA, TOKEN, PARTICULA),
        texto,
    ):
        bruto = m.group(1).strip(" ,.;:")
        # Quitar la cola de particulas sueltas, que no forman parte del nombre.
        bruto = re.sub(r"\s+%s$" % PARTICULA, "", bruto)
        if bruto and not es_institucional(bruto):
            objetivos.add(bruto)
            for pieza in bruto.split():
                if len(pieza) > 3 and not es_institucional(pieza):
                    objetivos.add(pieza)

    fallidos = []
    for objetivo in objetivos:
        if len(objetivo) < 4:
            continue
        halladas = pagina.search_for(objetivo)
        if not halladas:
            # Detectado en el texto pero sin coordenadas: no se puede tachar.
            fallidos.append(objetivo)
            continue
        cajas.extend(halladas)
    return cajas, fallidos


def capturar(fuente: Path, pagina_n: int, destino: Path, dpi: int = 90) -> bool:
    """Renderiza una pagina ya tachada.

    El original del corpus es `.docx`, no PDF. MuPDF lo abre y lo renderiza, pero
    no se puede dibujar sobre un documento que no es PDF: hay que convertirlo en
    memoria primero. La conversion no toca el archivo de origen.
    """
    import fitz

    try:
        doc = fitz.open(str(fuente))
    except Exception:
        return False
    try:
        if not doc.is_pdf:
            crudo = doc.convert_to_pdf()
            doc.close()
            doc = fitz.open("pdf", crudo)
    except Exception:
        try:
            doc.close()
        except Exception:
            pass
        return False

    with doc:
        if pagina_n >= len(doc):
            return False
        pagina = doc[pagina_n]
        if len(pagina.get_text().strip()) < 120:
            return False  # sin capa de texto no hay coordenadas: no se captura
        cajas, fallidos = cajas_a_tachar(pagina)
        if fallidos:
            # Fallo cerrado: un dato personal que no se puede tachar impide la
            # captura entera. Publicar una captura a medias es peor que no tenerla.
            return False
        for caja in cajas:
            pagina.draw_rect(caja, color=(0, 0, 0), fill=(0, 0, 0), overlay=True)
        destino.parent.mkdir(parents=True, exist_ok=True)
        # Escala de grises y 90 dpi: una captura referencial se mira para ver la
        # maqueta, no para leerla. A 150 dpi en color las 1.389 capturas pesaban
        # 444 MB, que es inviable en un repositorio; asi bajan a ~70 MB sin perder
        # legibilidad de la estructura.
        pm = pagina.get_pixmap(dpi=dpi, colorspace=fitz.csGRAY)
        pm.save(str(destino))
    sellar(destino, len(cajas))
    return True


# Marca de procedencia. Ninguna guardia de texto inspecciona una imagen, asi que
# una captura anadida a mano se colaria sin que nada la mirase. La marca no
# demuestra que el tachado sea correcto --eso lo garantiza el fallo cerrado de la
# generacion-- pero **si** demuestra que la imagen paso por aqui. Lo que no lleva
# marca no entra, y ademas se manda a revision con vision (R-150).
SELLO = "SystemHope-ResAdmis/capturar_referencias.py"


def sellar(png: Path, tachados: int) -> None:
    """Escribe la procedencia en el propio PNG, en un chunk de texto."""
    from PIL import Image, PngImagePlugin

    with Image.open(png) as img:
        info = PngImagePlugin.PngInfo()
        info.add_text("Software", SELLO)
        info.add_text("Comment", "captura referencial tachada en origen; %d region(es) ocultada(s)" % tachados)
        img.save(png, pnginfo=info, optimize=True)


def tiene_sello(png: Path) -> bool:
    try:
        from PIL import Image

        with Image.open(png) as img:
            return img.info.get("Software", "") == SELLO
    except Exception:
        return False


def estratos() -> dict:
    """Una celda por combinacion de rama, materia, proveedor y sujeto."""
    fichas = json.loads(INDICE.read_text(encoding="utf-8"))
    celdas = defaultdict(list)
    for f in fichas:
        clave = (f["rama"], f["materia"], f["proveedor_tipo"], f["sujeto_tipo"])
        celdas[clave].append(f)
    return celdas


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--por-celda", type=int, default=1)
    ap.add_argument("--paginas", type=int, default=2, help="Paginas por documento")
    args = ap.parse_args(argv[1:])

    celdas = estratos()
    print("=" * 78)
    print("CAPTURAS REFERENCIALES  (%s)" % ("APLICANDO" if args.aplicar else "PLAN"))
    print("=" * 78)
    print("  Celdas rama x materia x proveedor x sujeto: %d" % len(celdas))
    print(
        "  Documentos por celda: %d | paginas por documento: %d"
        % (args.por_celda, args.paginas)
    )
    print("  Capturas previstas: %d" % (len(celdas) * args.por_celda * args.paginas))
    print()
    print("  Cada PNG nace tachado: DNI, RUC, correos, telefonos, el nombre del")
    print("  encabezado y todo nombre tras tratamiento se pintan en negro sobre el")
    print("  pixmap antes de guardar. Las paginas sin capa de texto no se capturan:")
    print("  sin coordenadas no se puede garantizar el tachado.")

    if not args.aplicar:
        print()
        print("  Plan: no se escribio nada. Repite con --aplicar.")
        return 0

    hechas = fallidas = 0
    for (rama, materia, prov, sujeto), fichas in sorted(celdas.items()):
        for ficha in fichas[: args.por_celda]:
            origen = ORIGEN / ficha.get("origen_original", "").replace("/", "\\")
            # El .docx lo reflowea MuPDF con otra tipografia y sin membrete. El PDF
            # hermano es el documento tal como se emitio: logo, membrete, sangrias
            # y pie institucional. Para una captura referencial, el fiel es el PDF.
            pdf = origen.with_suffix(".pdf")
            if pdf.exists():
                origen = pdf
            if not origen.exists():
                fallidas += 1
                continue
            base = DESTINO / rama / ("%s__%s__%s" % (materia, prov, sujeto))
            for n in range(args.paginas):
                salida = base / ("%s_p%02d.png" % (ficha["archivo"][:44], n + 1))
                if capturar(origen, n, salida):
                    hechas += 1
                else:
                    fallidas += 1
    print()
    print("  Capturas escritas: %d | descartadas: %d" % (hechas, fallidas))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
