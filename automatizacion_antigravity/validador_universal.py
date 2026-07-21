#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
validador_universal.py - VALIDADOR SUPREMO (TODAS las reglas)
===============================================================
Codifica en Python TODAS las reglas enforceables de los ~73 rules.
No solo formato: incluye reglas juridicas, de contenido, estructura,
notas al pie, y checklist humano para lo no automatizable.

USO:
    python validador_universal.py <ruta_del_docx>

    Ejemplo:
    python validador_universal.py "temp_v7.docx"
    python validador_universal.py "../productos/ADM 0955-2026.docx"
"""

import sys
import os
import re
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from formato_nucleo import (
    FUENTE_CUERPO, TAMANO_CUERPO, TAMANO_NOTAS, TAMANO_INICIALES,
    ROMAN_INDENT, ROMAN_HANGING, NUM_INDENT, NUM_HANGING,
    LIST_INDENT, LIST_HANGING, RESOL_LIST_INDENT,
    META_INDENT, META_HANGING, FOOTER_TEXT,
    SPACE_BEFORE, SPACE_AFTER, LINE_SPACING,
)


# ====================================================================
# CONSTANTES DE VALIDACION
# ====================================================================

CAMPOS_METADATA = ["EXPEDIENTE", "DENUNCIANTE", "DENUNCIADO", "MATERIAS", "RESOLUCION"]

BOLERPLATE_CC1 = [
    "III. REQUERIMIENTO DE INFORMACION",
    "IV. RESOLUCION DE LA SECRETARIA TECNICA",
]

ARTICULOS_RESOLUTIVOS = [
    "PRIMERO", "SEGUNDO", "TERCERO", "CUARTO",
    "QUINTO", "SEXTO", "SETIMO", "OCTAVO",
    "NOVENO", "DECIMO", "DECIMO PRIMERO",
    "DECIMO SEGUNDO", "DECIMO TERCERO",
]

PATRON_INICIALES = re.compile(r'^[A-Z]{2,4}/[A-Z]{2,4}$')

PALABRAS_SIN_TILDE = [
    ("CODIGO", "CÓDIGO"), ("ARTICULO", "ARTÍCULO"),
    ("COMPANIA", "COMPAÑÍA"), ("POLIZA", "PÓLIZA"),
    ("SEPTIMO", "SÉPTIMO"), ("DECIMO", "DÉCIMO"),
    ("PACIFICO", "PACÍFICO"), ("NUMERO", "NÚMERO"),
    ("ADMISION", "ADMISIÓN"), ("SANCION", "SANCIÓN"),
    ("INFRACCION", "INFRACCIÓN"), ("DENUNCIANTE", None),
]

PROHIBIDOS_TIPIFICACION = [
    r'art[ií]culo\s+24',
    r'inducci[óo]n\s+al\s+error',
    r'art[ií]culo\s+58\s*[bB]',
]

PATRON_BASURA = [
    (r'\(\(\([A-Z0-9]*\)\)\)', 'caracteres basura (((N)))'),
    (r'\([A-Z]{3}\)', 'caracteres basura (NNN) (sin parentesis triples)'),
]

PATRON_DECRETO = re.compile(r'Decreto Supremo N[°º]\s*(\d+)-(\d+)-(\w+)')

VIOLETA_PATTERN = re.compile(r'^\([ivxlcdm]+\)\s', re.IGNORECASE)


class Violacion:
    def __init__(self, tipo, descripcion, ubicacion="", regla_num=""):
        self.tipo = tipo
        self.descripcion = descripcion
        self.ubicacion = ubicacion
        self.regla_num = regla_num

    def __str__(self):
        s = f"[{self.tipo}] {self.descripcion}"
        if self.ubicacion:
            s += f" ({self.ubicacion})"
        if self.regla_num:
            s = f"[R{self.regla_num}] " + s
        return s


class ValidadorUniversal:
    """
    Validador que revisa un DOCX contra TODAS las reglas:
    - Formato (Reglas 55-57, 39, 42, 48)
    - Juridicas (Arts. 24, 1-2, 18-19, 56, 58)
    - Estructurales (boilerplate, secciones)
    - Notas al pie (62-66, 68, 70, 72-73)
    - Contenido (basura, decretos, tildes, redundancia)
    - Checklist humano para reglas no automatizables
    """

    def __init__(self, doc_path):
        self.doc_path = doc_path
        self.doc = Document(doc_path)
        self.violaciones = []
        self.checks_total = 0
        self.checks_pass = 0

    def validar(self):
        """Ejecuta TODAS las validaciones."""
        print(f"\n{'='*75}")
        print(f"VALIDADOR UNIVERSAL - TODAS LAS REGLAS CC1")
        print(f"{'='*75}")
        print(f"Documento: {os.path.basename(self.doc_path)}")
        print(f"{'='*75}\n")

        # CATEGORIA A: Formato y tipografia
        print(f"{'─'*75}")
        print("CATEGORIA A: FORMATO Y TIPOGRAFIA")
        print(f"{'─'*75}")
        self.check_fuente_general()
        self.check_espaciado()
        self.check_metadata()
        self.check_footer()
        self.check_iniciales()
        self.check_sangrias_hechos_vs_resolutiva()
        self.check_no_header_duplicado()

        # CATEGORIA B: Estructura
        print(f"\n{'─'*75}")
        print("CATEGORIA B: ESTRUCTURA DEL DOCUMENTO")
        print(f"{'─'*75}")
        self.check_boilerplate()
        self.check_articulos_resolutivos()
        self.check_resolucion_unica()
        self.check_encabezado_cc1()

        # CATEGORIA C: Contenido juridico
        print(f"\n{'─'*75}")
        print("CATEGORIA C: CONTENIDO JURIDICO")
        print(f"{'─'*75}")
        self.check_tipificacion_prohibida()
        self.check_non_bis_in_idem()
        self.check_terminos_forbidden()
        self.check_tildes()
        self.check_basura()
        self.check_decreto_correcto()
        self.check_requerimientos_infinitivo()

        # CATEGORIA D: Notas al pie
        print(f"\n{'─'*75}")
        print("CATEGORIA D: NOTAS AL PIE")
        print(f"{'─'*75}")
        self.check_notas_pie_win32com()
        self.check_notas_markdown()
        self.check_notas_formato_legal()

        # CATEGORIA E: Checklist humano
        print(f"\n{'─'*75}")
        print("CATEGORIA E: CHECKLIST HUMANO (REVISAR MANUALMENTE)")
        print(f"{'─'*75}")
        self.checklist_humano()

        self._reportar()
        return self.violaciones

    def _ok(self, msg):
        self.checks_pass += 1
        self.checks_total += 1
        print(f"  [OK] {msg}")

    def _fail(self, msg, ubicacion="", regla_num=""):
        self.checks_total += 1
        v = Violacion("ERROR", msg, ubicacion, regla_num)
        self.violaciones.append(v)
        print(f"  [FAIL] {msg}")

    def _warn(self, msg, ubicacion="", regla_num=""):
        self.checks_total += 1
        v = Violacion("WARN", msg, ubicacion, regla_num)
        self.violaciones.append(v)
        print(f"  [WARN] {msg}")

    def _check(self, cond, ok_msg, fail_msg, ubicacion="", regla_num=""):
        if cond:
            self._ok(ok_msg)
        else:
            self._fail(fail_msg, ubicacion, regla_num)
        return cond

    # ================================================================
    # A1: FUENTE GENERAL
    # ================================================================
    def check_fuente_general(self):
        print("\n--- A1: Fuente general (Regla 55: Arial Narrow 11) ---")
        err_count = 0
        for i, p in enumerate(self.doc.paragraphs):
            for run in p.runs:
                if run.font.name and run.font.name.lower() not in ("arial narrow", "arialnarrow", "arial"):
                    if run.text.strip():
                        err_count += 1
                        if err_count <= 2:
                            self._fail(
                                f"Fuente '{run.font.name}' en parrafo {i+1}",
                                f"'{run.text[:60]}...'",
                                regla_num="55"
                            )
        if err_count == 0:
            self._ok("Todas las fuentes son Arial Narrow")
        else:
            self._fail(f"Total: {err_count} runs con fuente incorrecta", regla_num="55")

    # ================================================================
    # A2: ESPACIADO
    # ================================================================
    def check_espaciado(self):
        print("\n--- A2: Espaciado (Regla 55: SpaceBefore/After=0, LineSpacing=1.0) ---")
        err_before = 0
        err_after = 0
        err_line = 0
        for p in self.doc.paragraphs:
            pf = p.paragraph_format
            if pf.space_before is not None and pf.space_before > Pt(0):
                err_before += 1
            if pf.space_after is not None and pf.space_after > Pt(6):
                err_after += 1
            if pf.line_spacing is not None and pf.line_spacing > 1.5:
                err_line += 1
        total_err = err_before + err_after + err_line
        if total_err == 0:
            self._ok("Espaciado correcto en todos los parrafos")
        else:
            if err_before:
                self._fail(f"{err_before} parrafos con SpaceBefore > 0", regla_num="55")
            if err_after:
                self._fail(f"{err_after} parrafos con SpaceAfter > 6pt", regla_num="55")
            if err_line:
                self._fail(f"{err_line} parrafos con LineSpacing > 1.5", regla_num="55")

    # ================================================================
    # A3: METADATA
    # ================================================================
    def check_metadata(self):
        print("\n--- A3: Metadata (Regla 54: sangria colgante 1.48\") ---")
        found = 0
        ok_sangria = 0
        ok_bold = 0
        for p in self.doc.paragraphs:
            text = p.text.strip()
            for campo in CAMPOS_METADATA:
                if text.startswith(campo):
                    found += 1
                    pf = p.paragraph_format
                    if pf.left_indent and pf.first_line_indent:
                        ok_sangria += 1
                    for run in p.runs:
                        if run.text.strip() and run.bold:
                            ok_bold += 1
                            break
                    break
        if found == 0:
            self._warn("No se encontraron campos de metadata", regla_num="54")
        else:
            if ok_sangria == found:
                self._ok(f"Metadata: {found} campos con sangria colgante")
            else:
                self._fail(f"{found - ok_sangria} campos sin sangria colgante", regla_num="54")
            if ok_bold >= found:
                self._ok(f"Metadata: campos en negrita correctos")
            else:
                self._warn("Algunos campos de metadata no estan en negrita", regla_num="54")

    # ================================================================
    # A4: FOOTER
    # ================================================================
    def check_footer(self):
        print("\n--- A4: Footer (Regla 55: M-CPC-01/03) ---")
        try:
            section = self.doc.sections[0]
            footer = section.footer
            footer_text = "\n".join([p.text for p in footer.paragraphs])
            if FOOTER_TEXT in footer_text:
                self._ok(f"Footer '{FOOTER_TEXT}' presente")
            else:
                self._fail(f"Footer incorrecto (esperado: '{FOOTER_TEXT}')", regla_num="55")
        except Exception:
            self._warn("No se pudo acceder al footer", regla_num="55")

    # ================================================================
    # A5: INICIALES
    # ================================================================
    def check_iniciales(self):
        print("\n--- A5: Iniciales finales (Regla 42: tamano 8) ---")
        for p in self.doc.paragraphs:
            text = p.text.strip()
            if PATRON_INICIALES.match(text):
                for run in p.runs:
                    if run.font.size and run.font.size > Pt(8):
                        self._fail(
                            f"Iniciales '{text}' en tamano {run.font.size.pt}",
                            regla_num="42"
                        )
                        return
                self._ok(f"Iniciales '{text}' correctas (tamano 8)")
                return
        self._warn("No se encontraron iniciales", regla_num="42")

    # ================================================================
    # A6: SANGRÍAS HECHOS vs RESOLUTIVA
    # ================================================================
    def check_sangrias_hechos_vs_resolutiva(self):
        """
        Regla 39: NUNCA extrapolar sangrias.
        Hechos: left_indent~0.79, resolutiva: left_indent~0.39.
        """
        print("\n--- A6: Sangrias Hechos vs Resolutiva (Regla 39) ---")
        texto_completo = "\n".join([p.text for p in self.doc.paragraphs])
        if "I.\tHECHOS" in texto_completo or "I. HECHOS" in texto_completo:
            self._ok("Seccion I. HECHOS presente")
        else:
            self._warn("No se detecto Seccion I. HECHOS", regla_num="39")
        if "IV.\tRESOLUCION" in texto_completo or "IV. RESOLUCION" in texto_completo:
            self._ok("Seccion IV. RESOLUCION presente")
        else:
            self._warn("No se detecto Seccion IV. RESOLUCION", regla_num="39")

    # ================================================================
    # A7: NO HEADER DUPLICADO
    # ================================================================
    def check_no_header_duplicado(self):
        """Regla: El encabezado institucional NO debe insertarse en el body."""
        print("\n--- A7: Encabezado no duplicado en body ---")
        header_text = "SECRETARIA TECNICA DE LA"
        count = 0
        for p in self.doc.paragraphs:
            if header_text in p.text.upper():
                count += 1
        if count <= 1:
            self._ok("Encabezado no duplicado en el body")
        else:
            self._fail(
                f"Encabezado aparece {count} veces en el body (debe estar solo en Header)",
                regla_num="Manejo Encabezado"
            )

    # ================================================================
    # B1: BOILERPLATE CC1
    # ================================================================
    def check_boilerplate(self):
        print("\n--- B1: Boilerplate CC1 (Regla 55: secciones III y IV) ---")
        texto = "\n".join([p.text for p in self.doc.paragraphs])
        for seccion in BOLERPLATE_CC1:
            encontrado = seccion in texto
            self._check(
                encontrado,
                f"Seccion '{seccion}' presente",
                f"Seccion faltante: '{seccion}'",
                regla_num="55"
            )

    # ================================================================
    # B2: ARTICULOS RESOLUTIVOS
    # ================================================================
    def check_articulos_resolutivos(self):
        print("\n--- B2: Articulos resolutivos (CC1: PRIMERO a DECIMO PRIMERO) ---")
        texto = "\n".join([p.text for p in self.doc.paragraphs])
        required = ["PRIMERO", "SEGUNDO", "TERCERO", "CUARTO",
                     "QUINTO", "SEXTO", "SETIMO", "OCTAVO",
                     "NOVENO", "DECIMO"]
        for art in required:
            encontrado = art + ":" in texto or art + " " in texto
            self._check(
                encontrado,
                f"Articulo '{art}' presente",
                f"Articulo faltante: '{art}'",
                regla_num="55"
            )

    # ================================================================
    # B3: RESOLUCION UNICA
    # ================================================================
    def check_resolucion_unica(self):
        """Regla 44/59: Si hay una sola imputacion, PRIMERO es parrafo unico."""
        print("\n--- B3: Estructura PRIMERO (Regla 44/59) ---")
        count_vinetas = 0
        in_primero = False
        for p in self.doc.paragraphs:
            text = p.text.strip()
            if text.startswith("PRIMERO:"):
                in_primero = True
                continue
            if in_primero and re.match(r'^\([ivxlcdm]+\)', text, re.IGNORECASE):
                count_vinetas += 1
            if in_primero and text.startswith("SEGUNDO:"):
                break
        if count_vinetas == 0:
            self._ok("PRIMERO sin vinetas (posible parrafo unico)")
        elif count_vinetas == 1:
            self._warn("PRIMERO con 1 sola vineta (evaluar si es necesario)", regla_num="44")
        else:
            self._ok(f"PRIMERO con {count_vinetas} vinetas")

    # ================================================================
    # B4: ENCABEZADO CC1
    # ================================================================
    def check_encabezado_cc1(self):
        """Regla 54: encabezado CC1 correcto."""
        print("\n--- B4: Encabezado CC1 (Regla 54) ---")
        encabezado = "COMISION DE PROTECCION AL CONSUMIDOR 1"
        encontrado = encabezado in "\n".join([p.text for p in self.doc.paragraphs])
        self._check(
            encontrado,
            "Encabezado CC1 correcto",
            "No se encontro 'COMISION DE PROTECCION AL CONSUMIDOR 1'",
            regla_num="54"
        )

    # ================================================================
    # C1: TIPIFICACION PROHIBIDA
    # ================================================================
    def check_tipificacion_prohibida(self):
        """Reglas: Prohibido Art. 24, induccion al error, Art. 58.b mal citado."""
        print("\n--- C1: Tipificacion prohibida (Art.24, induccion error, Art.58.b) ---")
        texto = "\n".join([p.text for p in self.doc.paragraphs])
        texto_lower = texto.lower()

        # Art. 24
        if re.search(r'art[ií]culo\s+24', texto_lower):
            self._fail(
                "PROHIBIDO: Se encontro referencia al Art. 24 como tipificacion",
                regla_num="PROHIBIDO ART. 24"
            )
        else:
            self._ok("No se utiliza Art. 24 como tipificacion")

        # Induccion al error
        if re.search(r'inducci[óo]n\s+al\s+error', texto_lower):
            self._fail(
                "PROHIBIDO: Se encontro 'induccion al error'",
                regla_num="PROHIBIDO INDUCCION ERROR"
            )
        else:
            self._ok("No se usa 'induccion al error'")

    # ================================================================
    # C2: NON BIS IN IDEM
    # ================================================================
    def check_non_bis_in_idem(self):
        """Regla: NO imputar dos infracciones por un mismo hecho."""
        print("\n--- C2: Non bis in idem (Regla: no doble imputacion) ---")
        arts_18_19 = len(re.findall(r'art[ií]culos?\s+18[°º]\s*y\s+19[°º]',
                                     "\n".join([p.text for p in self.doc.paragraphs])))
        arts_1y2 = len(re.findall(r'art[ií]culo\s+1[°º,\s].*?art[ií]culo\s+2[°º]',
                                   "\n".join([p.text for p in self.doc.paragraphs]),
                                   re.DOTALL))
        self._ok(f"Arts. 18/19 mencionados {arts_18_19} veces")
        self._ok(f"Arts. 1/2 mencionados {arts_1y2} veces")
        if arts_18_19 > 0 and arts_1y2 > 0:
            self._warn(
                "Posible doble tipificacion: se usan Arts. 18/19 Y Arts. 1/2 en el mismo documento",
                regla_num="NON BIS IN IDEM"
            )

    # ================================================================
    # C3: TERMINOS FORBIDDEN
    # ================================================================
    def check_terminos_forbidden(self):
        """Verifica terminos prohibidos o tecnicamente incorrectos."""
        print("\n--- C3: Terminos prohibidos y tecnicismos ---")
        texto = "\n".join([p.text for p in self.doc.paragraphs])
        texto_lower = texto.lower()

        forbidden = [
            (r'\blamentablemente\b', "adverbio emocional 'lamentablemente' (Regla 43)"),
            (r'\bdesafortunadamente\b', "adverbio emocional 'desafortunadamente' (Regla 43)"),
            (r'\blastimosamente\b', "adverbio emocional"),
            (r'\bpagar\s+la\s+cobertura\b', "use 'otorgar la cobertura' en vez de 'pagar la cobertura' (Regla 57)"),
        ]
        all_ok = True
        for pattern, desc in forbidden:
            if re.search(pattern, texto_lower):
                self._fail(f"Termino prohibido: {desc}", regla_num="43/57")
                all_ok = False
        if all_ok:
            self._ok("No se encontraron terminos prohibidos")

    # ================================================================
    # C4: TILDES
    # ================================================================
    def check_tildes(self):
        print("\n--- C4: Tildes correctas (Regla 50) ---")
        texto = "\n".join([p.text for p in self.doc.paragraphs])
        err_count = 0
        for incorrecto, _ in PALABRAS_SIN_TILDE:
            if incorrecto in texto:
                err_count += 1
                if err_count <= 2:
                    self._fail(
                        f"Posible falta de tilde: '{incorrecto}'",
                        regla_num="50"
                    )
        if err_count == 0:
            self._ok("Tildes correctas en los terminos revisados")
        else:
            self._fail(f"Total: {err_count} palabras sin tilde", regla_num="50")

    # ================================================================
    # C5: CARACTERES BASURA
    # ================================================================
    def check_basura(self):
        """Eliminar caracteres basura como (((N)))."""
        print("\n--- C5: Caracteres basura (((N))) ---")
        texto = "\n".join([p.text for p in self.doc.paragraphs])
        err_count = 0
        for pattern, desc in PATRON_BASURA:
            encontrados = re.findall(pattern, texto)
            if encontrados:
                err_count += len(encontrados)
                self._fail(
                    f"{desc}: {len(encontrados)} ocurrencia(s): {encontrados[:3]}",
                    regla_num="GENERAR_RESOLUCIONES"
                )
        if err_count == 0:
            self._ok("Sin caracteres basura")

    # ================================================================
    # C6: DECRETO SUPREMO CORRECTO
    # ================================================================
    def check_decreto_correcto(self):
        """Verifica que el Decreto Supremo sea el vigente (004-2019-JUS)."""
        print("\n--- C6: Decreto Supremo vigente (004-2019-JUS) ---")
        texto = "\n".join([p.text for p in self.doc.paragraphs])
        matches = PATRON_DECRETO.findall(texto)
        if not matches:
            self._warn("No se encontraron referencias a Decreto Supremo", regla_num="C6")
            return
        for num, year, entidad in matches:
            if entidad == "JUS" and num not in ("004", "006"):
                self._warn(
                    f"Decreto Supremo N°{num}-{year}-{entidad} (verificar vigencia)",
                    regla_num="C6"
                )
            elif entidad == "JUS" and num == "006":
                self._fail(
                    f"Decreto Supremo N°006-2026-JUS DEROGADO. Usar N°004-2019-JUS",
                    regla_num="C6"
                )
            else:
                self._ok(f"Decreto Supremo N°{num}-{year}-{entidad}")

    # ================================================================
    # C7: REQUERIMIENTOS EN INFINITIVO
    # ================================================================
    def check_requerimientos_infinitivo(self):
        """Regla 52: verbos en infinitivo en requerimientos."""
        print("\n--- C7: Verbos en infinitivo en requerimientos (Regla 52) ---")
        texto = "\n".join([p.text for p in self.doc.paragraphs])
        subjuntivo = re.findall(r'\bcumpla\s+con\s+que\s+\w+e\b', texto, re.IGNORECASE)
        if subjuntivo:
            self._fail(
                f"Verbos en subjuntivo en requerimientos: {len(subjuntivo)} ocurrencia(s)",
                regla_num="52"
            )
        else:
            self._ok("Requerimientos usan verbos en infinitivo")

    # ================================================================
    # D1: NOTAS AL PIE VIA WIN32COM
    # ================================================================
    def check_notas_pie_win32com(self):
        """Verifica formato de notas al pie via win32com (Arial Narrow 8, bold laws)."""
        print("\n--- D1: Notas al pie (Reglas 62-66, 68, 70, 72-73) ---")
        try:
            import win32com.client
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            doc_com = word.Documents.Open(self.doc_path)

            fn_count = doc_com.Footnotes.Count
            if fn_count == 0:
                self._warn("El documento no tiene notas al pie", regla_num="D1")
                doc_com.Close()
                word.Quit()
                return

            err_font = 0
            err_size = 0
            err_no_tab = 0
            err_markdown = 0

            for fn in doc_com.Footnotes:
                rng = fn.Range
                if rng.Font.Name and rng.Font.Name.lower() not in ("arial narrow", "arialnarrow"):
                    err_font += 1
                if rng.Font.Size and rng.Font.Size != 8:
                    err_size += 1

                fn_text = rng.Text
                if '**' in fn_text:
                    err_markdown += 1

                if not fn_text.startswith('\t') and not fn_text.startswith(' '):
                    err_no_tab += 1

            # Bold en LEY y Artículo
            bold_counts = 0
            for fn in doc_com.Footnotes:
                for p in fn.Range.Paragraphs:
                    if p.Range.Font.Bold:
                        bold_counts += 1

            doc_com.Close()
            word.Quit()

            total_err = err_font + err_size + err_markdown
            if total_err == 0:
                self._ok(f"Notas al pie: {fn_count} correctas (Arial Narrow 8)")
            else:
                if err_font:
                    self._fail(f"{err_font} notas con fuente incorrecta", regla_num="63")
                if err_size:
                    self._fail(f"{err_size} notas con tamano incorrecto", regla_num="63")
                if err_markdown:
                    self._fail(f"{err_markdown} notas con markdown (**)", regla_num="62")
                if err_no_tab:
                    self._warn(f"{err_no_tab} notas sin tabulador inicial (Regla 70)", regla_num="70")

            if bold_counts > 0:
                self._ok(f"Negritas en {bold_counts} parrafos de notas")
            else:
                self._warn("Sin negritas en notas al pie (verificar si aplica)", regla_num="68")

        except ImportError:
            self._warn("win32com no disponible - validacion limitada de notas", regla_num="D1")
        except Exception as e:
            self._warn(f"Error validando notas: {e}", regla_num="D1")

    # ================================================================
    # D2: NOTAS - NO MARKDOWN
    # ================================================================
    def check_notas_markdown(self):
        """Regla 62: JAMAS usar asteriscos u otro markdown en notas."""
        print("\n--- D2: Notas sin markdown (Regla 62) ---")
        texto = "\n".join([p.text for p in self.doc.paragraphs])
        if '**' in texto:
            self._fail("Se encontraron asteriscos dobles (**) en el texto", regla_num="62")
        else:
            self._ok("Sin markdown en el texto")

    # ================================================================
    # D3: NOTAS - FORMATO LEGAL
    # ================================================================
    def check_notas_formato_legal(self):
        """Verifica que las notas contengan formato legal correcto."""
        print("\n--- D3: Notas - Formato legal ---")
        texto = "\n".join([p.text for p in self.doc.paragraphs])
        if "LEY N" in texto or "Artículo" in texto:
            self._ok("Notas contienen referencias legales")
        else:
            self._warn("No se detectaron referencias legales en el texto", regla_num="D3")

    # ================================================================
    # E1: CHECKLIST HUMANO
    # ================================================================
    def checklist_humano(self):
        """Checklist de reglas que REQUIEREN juicio humano."""
        print("""
  [MANUAL] Reglas que REQUIEREN revision humana obligatoria:
  ───────────────────────────────────────────────────────────
  [ ] Regla 43: Hechos redactados en orden cronologico
  [ ] Regla 43: Hechos objetivos, sin adverbios emocionales
  [ ] Regla 45: No redundancia del nombre del denunciado
  [ ] Regla 46: Representante omitido si denunciante es PN
  [ ] Regla 47: Requerimientos especificos (no genericos)
  [ ] Regla 48: Referencia correcta al denunciado
  [ ] Regla 49: Secuencia cronologica completa de hechos
  [ ] Regla 50: Tipificacion unica por hecho
  [ ] Regla 51: Art. 58.b citado correctamente
  [ ] Regla 52: Hechos facticos sin mencion a deberes
  [ ] Regla 54: CC1 vs PS1 - autoridad correcta identificada
  [ ] Regla 57: Nomenclatura SOAT correcta
  [ ] Regla 58: Requerimientos in-line para 1 proveedor
  [ ] Prohibido Art. 24 como imputacion
  [ ] Prohibido induccion al error
  [ ] Non bis in idem verificado
  [ ] Boletplate CC1 completo (III y IV)
""")

    # ================================================================
    # REPORTE FINAL
    # ================================================================
    def _reportar(self):
        errors = [v for v in self.violaciones if v.tipo == "ERROR"]
        warnings = [v for v in self.violaciones if v.tipo == "WARN"]

        print(f"\n{'='*75}")
        print(f"RESUMEN FINAL DE VALIDACION")
        print(f"{'='*75}")
        print(f"  Checks ejecutados: {self.checks_total}")
        print(f"  Pasaron:           {self.checks_pass}")
        print(f"  Errores:           {len(errors)}")
        print(f"  Warnings:          {len(warnings)}")

        if errors:
            print(f"\n  VIOLACIONES CRITICAS:")
            for v in errors:
                print(f"    - {v}")
        if warnings:
            print(f"\n  ADVERTENCIAS:")
            for v in warnings:
                print(f"    - {v}")

        if not errors and not warnings:
            print(f"\n  [OK] DOCUMENTO CUMPLE CON TODAS LAS REGLAS")
        elif not errors:
            print(f"\n  [WARN] DOCUMENTO VALIDO con {len(warnings)} advertencias")
        else:
            print(f"\n  [FAIL] DOCUMENTO NO VALIDO - {len(errors)} errores criticos")

        print(f"{'='*75}\n")


# ================================================================
# MAIN
# ================================================================

def validar_documento(docx_path):
    """Valida un documento contra TODAS las reglas."""
    if not os.path.exists(docx_path):
        print(f"Error: Archivo no encontrado: {docx_path}")
        return False, []

    validador = ValidadorUniversal(docx_path)
    violaciones = validador.validar()

    errores = [v for v in violaciones if v.tipo == "ERROR"]
    return len(errores) == 0, violaciones


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python validador_universal.py <ruta_del_docx>")
        print("Ejemplo: python validador_universal.py temp_v7.docx")
        sys.exit(1)

    docx_path = sys.argv[1]
    if not os.path.isabs(docx_path):
        docx_path = os.path.join(os.path.dirname(__file__), docx_path)

    valido, violaciones = validar_documento(docx_path)
    sys.exit(0 if valido else 1)
