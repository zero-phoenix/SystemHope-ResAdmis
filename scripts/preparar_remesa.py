#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prepara una remesa completa de expedientes en una sola llamada.

Por que existe: la ley de la latencia (R-134) dice que el reloj lo fija el numero
de llamadas, ~7,5 s cada una. Trece expedientes explorados a mano son cientos de
llamadas. Todo lo determinista -- censo de la cedula, triaje, dossier anclado,
candidatas de plantilla -- se hace aqui de una vez y queda escrito en el
`_ORDEN_DE_TRABAJO.md` de cada carpeta. El agente redactor no explora: lee su
orden y redacta.

Lo que este script **no** hace, a proposito: no decide la materia ni el sentido
de la imputacion. Propone candidatas con la evidencia que las sostiene (la
palabra hallada y cuantas veces) para que la decision sea verificable y
refutable. Donde no hay texto, lo dice y manda a vision.

Uso:
    python scripts/preparar_remesa.py <carpeta-remesa>
    python scripts/preparar_remesa.py <carpeta-remesa> --caso 2765-2026
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import extraer_expediente as EX  # noqa: E402

INDICE = RAIZ / "docs" / "plantillas_maestras_index.json"

# Cada rama con las palabras que la delatan. La evidencia se imprime junto con la
# propuesta: una rama elegida sin palabra que la sostenga es una rama inventada.
SENALES: dict[str, tuple[str, ...]] = {
    "01_seguro_vehicular": (
        "vehicular",
        "placa",
        "veh\u00edculo",
        "automotor",
        "choque",
        "siniestro vehicular",
    ),
    "02_seguro_vida": (
        "seguro de vida",
        "vida ley",
        "renta particular",
        "fallecimiento",
        "desamparo s\u00fabito",
    ),
    "03_seguro_desgravamen": ("desgravamen",),
    "04_seguro_proteccion_tarjetas_y_dinero": (
        "protecci\u00f3n de tarjeta",
        "consumos no reconocidos",
        "tarjeta de cr\u00e9dito",
        "cargos no reconocidos",
    ),
    "05_soat_y_afocat": ("soat", "afocat"),
    "06_seguro_hogar_e_inmuebles": (
        "multiriesgo",
        "seguro de hogar",
        "incendio",
        "inmueble asegurado",
    ),
    "07_seguro_sctr": ("sctr", "trabajo de riesgo", "grado de invalidez"),
    "08_seguro_salud_eps_oncologico": (
        "oncol\u00f3gico",
        " eps ",
        "asistencia m\u00e9dica",
        "seguro de salud",
    ),
    "09_seguro_patrimonial_caucion_rc": ("cauci\u00f3n", "responsabilidad civil"),
    "10_seguro_sepelio": ("sepelio",),
    "11_seguro_accidentes_personales": ("accidentes personales",),
    "12_seguro_transporte_y_carga": (
        "transporte de carga",
        "p\u00f3liza de transporte",
    ),
    "13_seguro_multiple_y_equipos": (
        "seguro m\u00faltiple",
        "equipos electr\u00f3nicos",
    ),
    "14_seguro_desempleo": ("desempleo",),
    "15_sistema_previsional_afp_onp": (
        " afp ",
        " onp ",
        "pensi\u00f3n de jubilaci\u00f3n",
    ),
}

BANCOS = ("BANCO", "BCP", "INTERBANK", "SCOTIABANK", "FINANCIERA", "CAJA ", "BBVA")
CORREDORES = ("CORREDOR", "CORREDORES")
ASEGURADORAS = (
    "SEGUROS",
    "ASEGURADORA",
    "RIMAC",
    "PACIFICO",
    "MAPFRE",
    "INTERSEGURO",
    "LA POSITIVA",
    "CARDIF",
    "PROTECTA",
    "VIVIR",
    "SANITAS",
    "CRECER",
)

RE_SENOR = re.compile(r"\b(el se\u00f1or|la se\u00f1ora|la se\u00f1orita)\b", re.I)


def texto_cedula(cedula: Path) -> str:
    import zipfile

    with zipfile.ZipFile(cedula) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    return re.sub(r"<[^>]+>", "", re.sub(r"</w:p>", "\n", xml))


def censo_cedula(cedula: Path) -> tuple[str, list[tuple[str, str, str]]]:
    texto = texto_cedula(cedula)
    lineas = [ln.strip() for ln in texto.split("\n")]
    m = re.search(r"Resoluci\u00f3n\s+N[\u00b0\u00ba.]?\s*(\d+)", texto, re.I)
    resolucion = m.group(1) if m else ""
    partes = []
    for i, ln in enumerate(lineas):
        if not ln.startswith("Se\u00f1or(es)"):
            continue
        nombre = lineas[i + 1] if i + 1 < len(lineas) else ""
        canal = lineas[i + 2] if i + 2 < len(lineas) else ""
        if canal.upper().startswith("CASILLA-E"):
            via, detalle = "Casilla Electr\u00f3nica", canal
        elif canal.upper().startswith("CORREO-E"):
            via, detalle = "correo electr\u00f3nico", canal
        else:
            via = "domicilio f\u00edsico"
            detalle = "%s %s" % (canal, lineas[i + 3] if i + 3 < len(lineas) else "")
        partes.append((nombre, via, detalle.strip()))
    return resolucion, partes


def clasificar(nombre: str) -> str:
    alto = nombre.upper()
    if any(b in alto for b in BANCOS):
        return "banco"
    if any(c in alto for c in CORREDORES):
        return "corredor"
    if any(a in alto for a in ASEGURADORAS):
        return "aseguradora"
    return "persona"


def proveedor_tipo(clases: list[str]) -> str:
    empresas = [c for c in clases if c != "persona"]
    if len(empresas) >= 2:
        if set(empresas) == {"banco", "aseguradora"}:
            return "2_ddos_banco_y_aseguradora"
        return "2_o_mas_ddos_varios"
    if empresas == ["aseguradora"]:
        return "1_ddo_aseguradora"
    if empresas == ["banco"]:
        return "1_ddo_banco_o_financiera"
    if empresas == ["corredor"]:
        return "1_ddo_corredor"
    return ""


def ramas_probables(texto: str) -> list[tuple[str, int, str]]:
    bajo = " " + texto.lower() + " "
    puntajes = []
    for rama, palabras in SENALES.items():
        total = 0
        prueba = ""
        for palabra in palabras:
            n = bajo.count(palabra)
            if n:
                total += n
                prueba = prueba or '"%s" x%d' % (palabra.strip(), n)
        if total:
            puntajes.append((rama, total, prueba))
    return sorted(puntajes, key=lambda x: -x[1])[:3]


def sujeto_probable(texto: str, partes) -> tuple[str, str]:
    if any("SUCESI" in n.upper() for n, _v, _d in partes):
        return "sucesion_intestada", "la cedula nombra una SUCESION INTESTADA"
    m = RE_SENOR.search(texto)
    if m:
        forma = m.group(1).lower()
        if forma.startswith("la se"):
            return "mujer", 'el escrito dice "%s"' % forma
        return "varon", 'el escrito dice "%s"' % forma
    return "", "sin anclaje en el texto: confirmar en el escrito"


MARCAS = (
    "RIMAC",
    "PACIFICO",
    "PACÍFICO",
    "MAPFRE",
    "INTERSEGURO",
    "LA POSITIVA",
    "CARDIF",
    "BNP PARIBAS",
    "PROTECTA",
    "VIVIR SEGUROS",
    "SANITAS",
    "CRECER",
    "BCP",
    "BANCO DE CREDITO",
    "BANCO DE CRÉDITO",
    "INTERBANK",
    "SCOTIABANK",
    "BBVA",
    "FALABELLA",
    "RIPLEY",
    "CREDISCOTIA",
    "PRIMERA CORREDORES",
)


def empresas_sin_cedula(texto: str, partes) -> list[str]:
    """Empresas nombradas en el escrito que no son parte en la cedula.

    No decide nada: una mencion puede ser el banco donde se pago la prima y no un
    denunciado. Se lista para que el redactor lo resuelva contra el petitorio, que
    es donde consta a quien se denuncia, en vez de inferirlo.
    """
    alto = texto.upper()
    en_cedula = " | ".join(n for n, _v, _d in partes).upper()
    fuera = []
    for marca in MARCAS:
        if marca in alto and marca.split()[0] not in en_cedula:
            fuera.append(marca)
    return sorted(set(fuera))


def candidatas(fichas, rama: str, prov: str, sujeto: str) -> list[dict]:
    salida = [f for f in fichas if (not rama or f["rama"] == rama)]
    if prov:
        con_prov = [f for f in salida if f["proveedor_tipo"] == prov]
        salida = con_prov or salida
    if sujeto:
        con_suj = [f for f in salida if f["sujeto_tipo"] == sujeto]
        salida = con_suj or salida
    return salida[:5]


def orden(carpeta: Path, fichas) -> dict:
    cedulas = sorted(carpeta.glob("ADM*CEDULAS*.docx"))
    resolucion, partes = censo_cedula(cedulas[0]) if cedulas else ("", [])

    inventario, dossier = EX.triaje(carpeta)
    paginas = sum(i["paginas"] for i in inventario)
    escaneadas = [(i["archivo"], i["sin_texto"]) for i in inventario if i["sin_texto"]]
    n_vision = sum(len(s) for _a, s in escaneadas)

    texto = "\n".join(
        "\n".join(EX.paginas_de_pdf(p)) for p in sorted(carpeta.glob("*.pdf"))
    )
    clases = [clasificar(n) for n, _v, _d in partes]
    prov = proveedor_tipo(clases)
    ramas = ramas_probables(texto)
    sujeto, prueba_sujeto = sujeto_probable(texto, partes)
    rama = ramas[0][0] if ramas else ""

    return {
        "carpeta": carpeta,
        "resolucion": resolucion,
        "inventario": inventario,
        "fuera_de_cedula": empresas_sin_cedula(texto, partes),
        "partes": list(zip(partes, clases)),
        "paginas": paginas,
        "vision": n_vision,
        "escaneadas": escaneadas,
        "dossier": dossier,
        "ramas": ramas,
        "rama": rama,
        "proveedor_tipo": prov,
        "sujeto": sujeto,
        "prueba_sujeto": prueba_sujeto,
        "candidatas": candidatas(fichas, rama, prov, sujeto),
    }


def escribir_orden(d: dict) -> None:
    carpeta: Path = d["carpeta"]
    filas_partes = "\n".join(
        "| %s | %s | **%s** | %s |"
        % (n, "denunciado" if c != "persona" else "denunciante", v, det[:60])
        for (n, v, det), c in d["partes"]
    )
    filas_docs = "\n".join(
        "- `%s` — **%d página(s)**%s"
        % (
            i["archivo"],
            i["paginas"],
            " · sin capa de texto en p. %s" % i["sin_texto"] if i["sin_texto"] else "",
        )
        for i in d["inventario"]
    )
    bloque_vision = (
        "**Las %d páginas se leen con Google Lens. Todas. Sin excepción (R-137).**\n\n"
        "%s\n\n"
        "No importa si la página trae capa de texto: igual se mira. **Cero OCR** — ni\n"
        "tesseract, ni el OCR de un lector de PDF, ni ningún motor de terceros. La única\n"
        "lectura de imagen autorizada es Google Lens.\n\n"
        "Las %d página(s) marcadas arriba como *sin capa de texto* no tienen texto que\n"
        "contrastar: en ellas Lens es la **única** fuente y hay que mirarlas con especial\n"
        "cuidado.\n" % (d["paginas"], filas_docs, d["vision"])
    )

    filas_cand = (
        "\n".join("- `%s`" % f["archivo"] for f in d["candidatas"])
        or "- (sin candidata: elegir a mano tras leer el escrito)"
    )

    if d["fuera_de_cedula"]:
        bloque_discrepancia = (
            "El escrito **menciona** además a: %s. **No son parte** (R-138): la cédula\n"
            "fija las partes procesales y ninguna otra entra. Esas menciones son contexto\n"
            "del relato (el banco donde se pagó la prima, el corredor que intermedió) y\n"
            "pueden aparecer en los hechos como tales, nunca como denunciados ni en el\n"
            "encabezado ni en la parte resolutiva. No hay nada que elevar: la cédula ya\n"
            "lo resolvió.\n" % ", ".join(d["fuera_de_cedula"])
        )
    else:
        bloque_discrepancia = (
            "El escrito no menciona más empresas que las que la cédula notifica.\n"
        )

    filas_ramas = (
        "\n".join(
            "- `%s` — evidencia: %s (puntaje %d)" % (rama, prueba, puntaje)
            for rama, puntaje, prueba in d["ramas"]
        )
        or "- (el texto disponible no delata la materia; decidir tras la visión)"
    )

    orden_dossier = (
        "expediente",
        "resoluciones_previas",
        "fechas",
        "montos",
        "polizas_siniestros",
        "placas",
        "correos",
        "cartas_notariales",
    )
    bloques = []
    for clave in orden_dossier:
        valores = d["dossier"].get(clave) or {}
        if not valores:
            continue
        filas = "\n".join(
            "| %s | %s |" % (v, ", ".join(sorted(fuentes))[:70])
            for v, fuentes in list(valores.items())[:12]
        )
        bloques.append(
            "### %s\n\n| Valor | Página de origen |\n|---|---|\n%s\n" % (clave, filas)
        )

    texto = f"""# ORDEN DE TRABAJO — Expediente {carpeta.name}/CC1

> Generada por `scripts/preparar_remesa.py` el {datetime.now():%d/%m/%Y %H:%M}.
> **Esta orden manda sobre `AGENTS.md` para este caso.** El triaje, el censo de la
> cédula y las candidatas de plantilla **ya están hechos**: no los rehagas. Rehacer
> trabajo hecho es la causa medida de la demora (R-122, R-134).

## 1. Lo que la cédula fija y no se discute (R-129)

- **Resolución N° {d['resolucion'] or '(no declarado)'}** — el admisorio lleva ese ordinal.
- **Fecha de emisión: 14 de setiembre de 2026** (R-128), sin importar otras fechas.
- **Firma: LUISA ANALI SILVA MALPARTIDA, Secretaria Técnica (e)** (R-127).
- **Partes y vía de notificación — una sola vía por parte:**

| Parte | Rol | Vía de notificación | Canal literal |
|---|---|---|---|
{filas_partes}

Traducción a párrafos de notificación: Casilla Electrónica → TIPO 1 (cinco días);
correo electrónico → TIPO 2 (dos días); domicilio físico → TIPO 3.

### Otras empresas nombradas en el escrito

{bloque_discrepancia}
## 2. Lectura del expediente — Google Lens en todas las páginas (R-137)

{bloque_vision}
`_texto_expediente.txt` (en esta carpeta) trae el texto embebido de las páginas que
lo tienen. **No es la lectura: es el contraste.** Está medido que ese volcado pierde
tildes y corrompe caracteres —«1274 de agosto» donde el documento dice «17 de agosto
de 2026», «MART?N» donde dice «MARTIN» (R-126)—. **Si el volcado y Lens discrepan,
manda Lens.** Léelo una sola vez, entero (R-134/F10).

## 3. Dossier anclado — cada dato con la página de la que salió

{chr(10).join(bloques) if bloques else "(sin datos extraíbles del volcado: la lectura con Lens es la única fuente)"}

> Este dossier sale del volcado de texto, así que **es una pista, no una prueba**.
> Todo dato que uses en el admisorio se confirma contra lo que Lens ve en la página
> citada. Si no aparece ni en la página ni en el dossier, no existe: se eleva al
> instructor, no se inventa.

## 4. Plantilla base — propuesta con su evidencia

- Materia probable:
{filas_ramas}
- Tipo de denunciado: `{d['proveedor_tipo'] or '(indeterminado)'}`
- Sujeto: `{d['sujeto'] or '(a confirmar)'}` — {d['prueba_sujeto']}

Candidatas del índice (`docs/plantillas_maestras_index.json`):

{filas_cand}

La propuesta es refutable: si el escrito dice otra materia, gana el escrito y se
anota aquí por qué.

## 5. Entrega — dos llamadas, ni una más

```bash
python scripts/admisorio.py entregar <RES_0{d['resolucion'] or 'N'}_{carpeta.name}_CC1_ADMISORIO.docx> --caso {carpeta.name.split('-')[0]}
```

Debe decir `APTO (0 falsadores)` y `ENTREGABLE`. Sin esa salida literal el
admisorio no está entregado.

## 6. Prohibido

- **Generar PDF** (R-125). El entregable es `.docx`.
- **Commitear el `.docx` o este archivo**: contienen datos personales y el
  repositorio es público (`guardia_admisorio.py` lo bloquea).
- **Mezclar expedientes**: una conversación por caso (F12). Si en tu contexto
  aparece otro número de expediente, párate.
- **Inventar**: dato sin ancla en el dossier o en el texto = se eleva al instructor.
"""
    (carpeta / "_ORDEN_DE_TRABAJO.md").write_text(texto, encoding="utf-8")


def escribir_cola(base: Path, ordenes: list[dict]) -> None:
    # Todas las paginas van a Lens (R-137), asi que el coste de un caso es su
    # numero de paginas. La cola va de menos a mas: los cortos primero, para que
    # el primer veredicto del supervisor llegue pronto.
    por_coste = sorted(ordenes, key=lambda o: o["paginas"])
    filas = []
    for i, o in enumerate(por_coste, start=1):
        filas.append(
            "| %d | %s | R%s | %d | %d | %d | pendiente |"
            % (
                i,
                o["carpeta"].name,
                o["resolucion"] or "?",
                o["paginas"],
                o["paginas"],
                o["vision"],
            )
        )
    texto = f"""# COLA DE LA REMESA — 13 admisorios

> Generada por `scripts/preparar_remesa.py` el {datetime.now():%d/%m/%Y %H:%M}.
> **Se trabaja de uno en uno, en este orden**: de menos páginas a más, porque
> **todas** las páginas se leen con Google Lens (R-137) y el coste de un caso es
> su número de páginas.

| # | Expediente | Resolución | Páginas | A leer con Lens | Sin capa de texto | Estado |
|---|---|---|---|---|---|---|
{chr(10).join(filas)}

## Reglas de la cola

1. Un expediente por conversación (F12). Al abrirlo se lee **solo** su
   `_ORDEN_DE_TRABAJO.md`.
2. **Google Lens en todas las páginas, cero OCR** (R-137). La velocidad no se
   busca leyendo menos: se busca no releyendo, no repitiendo el triaje y no
   consultando tareas en bucle.
3. Al cerrarlo se declara **N** (llamadas) y **T** (reloj) — R-135.
4. Terminado un caso, su `_ESTADO.md` dice `CASO CERRADO` y no se vuelve a tocar.
5. Ningún `.docx` de expediente entra al repositorio.

## Encargo, uno por conversación

Abrir **una conversación nueva** por expediente y pegar exactamente esto,
cambiando solo el número:

```
Redacta el admisorio del Expediente <EXP>/CC1.

Workspace: C:\\Users\\D\\Code\\repos\\SystemHope-ResAdmis (todo comando corre ahí).
Orden de trabajo: C:\\Users\\D\\Desktop\\expedientes\\<EXP>\\_ORDEN_DE_TRABAJO.md

Lee esa orden y síguela. El triaje, el censo de la cédula, el dossier anclado y
las candidatas de plantilla YA ESTÁN HECHOS: no los rehagas.

Lee TODAS las páginas de TODOS los PDF con Google Lens, tengan o no capa de
texto. Cero OCR. El volcado _texto_expediente.txt es contraste, no reemplazo: si
discrepa con lo que ves, mandas lo que ves. Lee cada archivo una sola vez.

Las partes procesales son exactamente las de la cédula, con una sola vía de
notificación cada una. Ninguna otra empresa mencionada en el escrito es parte.

Entrega con:
python scripts/admisorio.py entregar "<ruta del .docx>" --caso <EXP>

Pega la salida literal (APTO / ENTREGABLE) y declara cuántas llamadas a
herramienta usaste y cuánto tardó. No generes PDF. No commitees el .docx.
Cualquier dato que no veas en una página: no lo inventes, decláralo como
pendiente del instructor.
```
"""
    (base / "_COLA.md").write_text(texto, encoding="utf-8")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("base")
    ap.add_argument("--caso", help="Prepara solo este expediente")
    args = ap.parse_args(argv[1:])

    base = Path(args.base)
    fichas = json.loads(INDICE.read_text(encoding="utf-8"))
    carpetas = sorted(p for p in base.iterdir() if p.is_dir())
    if args.caso:
        carpetas = [p for p in carpetas if p.name == args.caso]

    t0 = time.time()
    print("=" * 78)
    print("PREPARACION DE REMESA  %s" % base)
    print("=" * 78)
    ordenes = []
    for carpeta in carpetas:
        d = orden(carpeta, fichas)
        escribir_orden(d)
        ordenes.append(d)
        print(
            "  %-11s R%-2s %3d pag  vision=%-3d  %-32s %-26s %s"
            % (
                carpeta.name,
                d["resolucion"] or "?",
                d["paginas"],
                d["vision"],
                d["rama"] or "(materia sin anclar)",
                d["proveedor_tipo"] or "(prov. indeterminado)",
                d["sujeto"] or "(sujeto a confirmar)",
            )
        )
    if not args.caso:
        escribir_cola(base, ordenes)

    total_vision = sum(o["vision"] for o in ordenes)
    print()
    print(
        "  %d expediente(s), %d pagina(s), %d requieren vision."
        % (len(ordenes), sum(o["paginas"] for o in ordenes), total_vision)
    )
    print("  Ordenes escritas en cada carpeta. Cola en %s" % (base / "_COLA.md"))
    print("  Preparacion completa en %.1f s y 1 llamada." % (time.time() - t0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
