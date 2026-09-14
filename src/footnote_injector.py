"""Inyección de notas al pie nativas vía win32com (Reglas R-27, R-68 a R-75).

Este módulo SOLO funciona en Windows con Microsoft Word instalado. Aplica:

- R-68: argumentos posicionales ``document.Footnotes.Add(rng, "", texto)``.
- R-70: fuerza Arial Narrow 8 y justificado en todas las notas.
- R-72: usa PUNTOS (28.35) no twips.
- R-73: limpia tabs/spaces heredados; Bold=False antes de aplicar lógica.
- R-74: hanging indent + Bold automático en párrafos que empiecen con "LEY " o "Artículo ".
- R-75: prepend ``\\t`` y reemplaza ``\\n`` por ``\\r\\t``.
- R-62: elimina resaltados residuales (HighlightColorIndex = 0).
- R-66: usa ``\\r`` para saltos de párrafo duros.

El flujo es: ``python-docx`` (en ``builder.py``) escribe el cuerpo y marca con
marcadores especiales dónde van las notas; luego este módulo abre Word vía COM,
reemplaza los marcadores por notas reales y aplica formato.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# Marcador que builder.py inserta en el cuerpo para indicar "nota al pie aquí".
# Formato:  [[FN:Texto de la nota...]]
MARCADOR_NOTA = re.compile(r"\[\[FN:(.*?)\]\]", re.DOTALL)


def _requiere_windows() -> None:
    if sys.platform != "win32":
        raise RuntimeError(
            "La inyección de notas al pie nativas requiere Microsoft Word en Windows. "
            "En Linux/Mac se conserva el marcador como texto (editable manualmente)."
        )


def _pids_word_sin_ventana() -> list[int]:
    """PIDs de WINWORD.EXE sin ventana principal (residuo de un DispatchEx sin Quit).

    Se consulta **antes** de abrir Word. Una instancia huerfana deja el .docx
    bloqueado y el siguiente ``Documents.Open`` espera sin limite: es la causa
    medida de que una generacion de minutos se convierta en una espera
    indefinida (R-116). Detectar y fallar rapido convierte esa espera en un
    error con instruccion.
    """
    if sys.platform != "win32":
        return []
    ps = (
        "Get-Process -Name WINWORD -ErrorAction SilentlyContinue | "
        "Where-Object { -not $_.MainWindowTitle } | "
        "ForEach-Object { $_.Id }"
    )
    try:
        salida = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
            capture_output=True,
            timeout=30,
        ).stdout.decode("utf-8", "replace")
    except Exception:
        return []
    return [int(x) for x in salida.split() if x.strip().isdigit()]


def _verificar_word_sano() -> None:
    """Aborta con instruccion si hay un Word huerfano, en vez de esperar (R-123)."""
    pids = _pids_word_sin_ventana()
    if pids:
        lista = ", ".join(str(p) for p in pids)
        raise RuntimeError(
            "Hay WINWORD.EXE huerfano(s) sin ventana (PID %s). Mantienen el .docx "
            "abierto y la inyeccion de notas esperaria sin limite. Cierralos con "
            "conocimiento de causa: Stop-Process -Id %s" % (lista, lista.split(",")[0])
        )


def procesar_notas(ruta_docx: str | Path, visible: bool = False) -> dict[str, Any]:
    """Abre el .docx con Word, reemplaza marcadores [[FN:...]] por notas reales.

    Retorna un dict con: ``notas_insertadas``, ``errores``, ``resaltados_limpiados``.
    """
    _requiere_windows()
    try:
        import win32com.client  # type: ignore
        import pywintypes  # type: ignore # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "pywin32 no está instalado. Ejecuta: pip install pywin32"
        ) from exc

    ruta_abs = str(Path(ruta_docx).resolve())
    _limpiar_bloqueo(Path(ruta_docx))
    _verificar_word_sano()
    word = None
    doc = None
    stats = {"notas_insertadas": 0, "errores": [], "resaltados_limpiados": False}

    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = visible
        # Word repinta la ventana en cada operacion COM. Apagar el repintado
        # es la diferencia mas grande de toda la automatizacion y no altera
        # el resultado: se restaura antes de cerrar.
        try:
            word.ScreenUpdating = False
        except Exception:  # pragma: no cover
            pass
        word.DisplayAlerts = 0  # wdAlertsNone
        doc = word.Documents.Open(ruta_abs)

        # 1. Extraer lista de notas del contenido del cuerpo
        contenido = doc.Content.Text
        notas_texto: list[str] = []
        for m in MARCADOR_NOTA.finditer(contenido):
            texto = m.group(1).strip()
            # R-75: prepend \t y reemplaza \n por \r\t
            texto = _sanitizar_nota(texto)
            notas_texto.append(texto)

        # 2. Reemplazo robusto: iteramos por cada marcador EXACTO (texto completo).
        # Esto evita el problema de la sintaxis wildcard de Word.
        # Para cada nota, buscamos literalmente el marcador completo y lo
        # reemplazamos por una inserción de Footnote.
        for nota_saneada in notas_texto:
            # Reconstruir el marcador original (sin sanitizar) para buscarlo tal cual
            # El texto en el doc es [[FN:TEXTO_ORIGINAL]]; nosotros guardamos la versión saneada.
            # Buscamos con wildcard pero escapando correctamente.
            ok = _reemplazar_primer_marcador(doc, nota_saneada)
            if ok:
                stats["notas_insertadas"] += 1
            else:
                stats["errores"].append(f"No se encontró marcador para nota.")

        # 2. Formatear TODAS las notas al pie (R-70, R-74)
        _formatear_notas(doc)

        # 3. R-62: limpiar resaltados globales
        try:
            doc.Content.HighlightColorIndex = 0  # wdNoHighlight
            stats["resaltados_limpiados"] = True
        except Exception as exc:  # pragma: no cover
            stats["errores"].append(f"Limpiando resaltados: {exc}")

        doc.Save()
    finally:
        if doc is not None:
            try:
                doc.Close(SaveChanges=-1)  # wdSaveChanges
            except Exception:  # pragma: no cover
                pass
        if word is not None:
            try:
                word.ScreenUpdating = True
            except Exception:  # pragma: no cover
                pass
            try:
                word.Quit()
            except Exception:  # pragma: no cover
                pass

    return stats


def _reemplazar_primer_marcador(doc: Any, texto_nota_saneado: str) -> bool:
    """Busca el primer marcador ``[[FN:...]]`` en el cuerpo y lo reemplaza por
    una nota al pie nativa. Retorna True si tuvo éxito.

    Estrategia robusta: usa ``Find.Execute`` con búsqueda literal (sin wildcards)
    de la cadena ``[[FN:``, luego expande el rango manualmente hasta ``]]``.
    """
    find = doc.Content.Find
    find.ClearFormatting()
    find.Text = "[[FN:"
    find.Forward = True
    find.Wrap = 0  # wdFindStop
    find.MatchWildcards = False
    find.MatchCase = False

    if not find.Execute():
        return False

    # find.Parent es el Range donde se encontró "[[FN:"
    rng = find.Parent
    # Extender el rango hasta encontrar "]]"
    fin_doc = doc.Content.End
    rng_ext = doc.Range(rng.End, min(rng.End + 4000, fin_doc))  # ventana amplia pero acotada
    txt_ventana = rng_ext.Text or ""
    pos_fin = txt_ventana.find("]]")
    if pos_fin == -1:
        return False
    # rng.End se mueve al final del marcador completo
    rng.End = rng.End + pos_fin + 2

    try:
        rng.Text = ""  # elimina el marcador; rng colapsa al punto
        doc.Footnotes.Add(rng, "", texto_nota_saneado)
        return True
    except Exception:
        return False


def _sanitizar_nota(texto: str) -> str:
    """R-73: limpia espacios/tabs heredados; R-75: prepend \\t; R-66: \\r duro."""
    # Eliminar espacios/tabs al inicio de cada línea, dejar UN solo \t maestro.
    lineas = [ln.lstrip(" \t") for ln in texto.splitlines()]
    texto_limpio = "\r".join(lineas)
    # R-75: que cada salto de párrafo interno también empiece con tab
    texto_limpio = texto_limpio.replace("\r", "\r\t")
    # R-75: el primer carácter debe ser \t
    if not texto_limpio.startswith("\t"):
        texto_limpio = "\t" + texto_limpio
    # Sanitizar residuales: dobles tabs
    texto_limpio = re.sub(r"\t{2,}", "\t", texto_limpio)
    return texto_limpio


def _formatear_notas(doc: Any) -> None:
    """Aplica Arial Narrow 8, justificado, hanging indent y Bold a leyes.

    El formato comun se aplica de una sola vez sobre el story range de notas al
    pie (``wdFootnotesStory``): una operacion COM en lugar de siete por nota. Si
    esa via falla en alguna version de Word, cae al recorrido nota por nota, que
    produce exactamente el mismo resultado.
    """
    try:
        footnotes = doc.Footnotes
    except Exception:  # pragma: no cover
        return
    if footnotes.Count == 0:
        return

    try:
        story = doc.StoryRanges(2)  # wdFootnotesStory
        story.Font.Name = "Arial Narrow"
        story.Font.Size = 8
        story.Font.Bold = False  # R-73: limpiar herencia antes de aplicar logica
        fmt = story.Format
        fmt.Alignment = 3  # wdAlignParagraphJustify
        fmt.LeftIndent = 28.35  # R-72: PUNTOS no twips. 1 cm = 28.35 pt.
        fmt.FirstLineIndent = -28.35
        _bold_a_leyes(story)
        return
    except Exception:  # pragma: no cover
        pass

    for i in range(1, footnotes.Count + 1):
        try:
            rango = footnotes(i).Range
            fmt = rango.Format
            rango.Font.Name = "Arial Narrow"
            rango.Font.Size = 8
            fmt.Alignment = 3
            fmt.LeftIndent = 28.35
            fmt.FirstLineIndent = -28.35
            rango.Font.Bold = False
            _bold_a_leyes(rango)
        except Exception:  # pragma: no cover
            continue


def _bold_a_leyes(rango: Any) -> None:
    """R-74: pone en negrita los parrafos que abren con 'LEY ' o 'Articulo '."""
    try:
        total = rango.Paragraphs.Count
    except Exception:  # pragma: no cover
        return
    for j in range(1, total + 1):
        try:
            par = rango.Paragraphs(j)
            txt = par.Range.Text.lstrip(" 	").strip()
            if txt.startswith(("LEY ", "Ley ", "ARTÍCULO ", "Artículo ", "Articulo ")):
                par.Range.Font.Bold = True
        except Exception:  # pragma: no cover
            continue

def _limpiar_bloqueo(destino: Path) -> None:
    """Borra el archivo de bloqueo ``~$nombre.docx`` si quedo huerfano.

    Word deja ese archivo mientras tiene el documento abierto y lo retira al
    cerrar. Si el proceso que lo automatizaba murio entre medias, el bloqueo
    sobrevive y la siguiente apertura sale en solo lectura o se queda
    esperando. Si otro Word lo tiene tomado de verdad, el borrado falla y no
    pasa nada: se sigue adelante."""
    bloqueo = destino.parent / ("~$" + destino.name)
    try:
        if bloqueo.exists():
            bloqueo.unlink()
    except OSError:  # pragma: no cover - lo tiene abierto un Word vivo
        pass
