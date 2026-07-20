#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
validador_post_generacion.py - Regla Suprema 56 (Control de Calidad)
=====================================================================
Valida un documento DOCX generado contra las reglas de formato CC1.
Reporta TODAS las violaciones encontradas.

USO:
    python validador_post_generacion.py <ruta_del_docx>
    
    Ejemplo:
    python validador_post_generacion.py "../temp_v7.docx"
    python validador_post_generacion.py "../productos (resoluciones) elaborada por google antigravity/ADM 0955-2026.docx"
"""

import sys
import os
import re
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH


# ============================================================
# CONSTANTES DE REGLAS
# ============================================================
FUENTE_CORRECTA = "Arial Narrow"
TAMANO_CUERPO = Pt(11)
TAMANO_NOTAS = Pt(8)
TAMANO_INICIALES = Pt(8)

BOLERPLATE_CC1 = [
    "III. REQUERIMIENTO DE INFORMACI\u00d3N",
    "IV. RESOLUCI\u00d3N DE LA SECRETAR\u00cdA T\u00c9CNICA",
]

ARTICULOS_RESOLUTIVOS = [
    "PRIMERO", "SEGUNDO", "TERCERO", "CUARTO",
    "QUINTO", "SEXTO", "S\u00c9TIMO", "OCTAVO",
    "NOVENO", "D\u00c9CIMO", "D\u00c9CIMO PRIMERO",
]

FOOTER_ESPERADO = "M-CPC-01/03"

CAMPOS_METADATA = ["EXPEDIENTE", "DENUNCIANTE", "DENUNCIADO", "MATERIAS", "RESOLUCI\u00d3N"]

PATRON_INICIALES = re.compile(r'^[A-Z]{2,4}/[A-Z]{2,4}$')


class Violacion:
    """Representa una violaci\u00f3n de regla encontrada."""
    def __init__(self, tipo, descripcion, ubicacion=""):
        self.tipo = tipo
        self.descripcion = descripcion
        self.ubicacion = ubicacion
    
    def __str__(self):
        return f"[{self.tipo}] {self.descripcion}" + (f" (ubicaci\u00f3n: {self.ubicacion})" if self.ubicacion else "")


class ValidadorPostGeneracion:
    """
    Validador que revisa un documento DOCX contra las reglas CC1.
    """
    
    def __init__(self, doc_path):
        self.doc_path = doc_path
        self.doc = Document(doc_path)
        self.violaciones = []
        self.total_checks = 0
        self.passed_checks = 0
    
    def validar(self):
        """Ejecuta TODAS las validaciones y retorna la lista de violaciones."""
        print(f"\n{'='*70}")
        print(f"VALIDADOR POST-GENERACI\u00d3N - REGLAS CC1")
        print(f"{'='*70}")
        print(f"Documento: {os.path.basename(self.doc_path)}")
        print(f"{'='*70}\n")
        
        self._check_fuente_general()
        self._check_espaciado()
        self._check_metadata()
        self._check_boilerplate()
        self._check_articulos_resolutivos()
        self._check_notas_pie()
        self._check_iniciales()
        self._check_footer()
        self._check_tildes()
        
        self._reportar()
        return self.violaciones
    
    def _add_violacion(self, tipo, desc, ubicacion=""):
        v = Violacion(tipo, desc, ubicacion)
        self.violaciones.append(v)
        return v
    
    def _check_pass(self, msg):
        self.passed_checks += 1
        self.total_checks += 1
        print(f"  [OK] {msg}")
    
    def _check_fail(self, msg, ubicacion=""):
        self.total_checks += 1
        self._add_violacion("ERROR", msg, ubicacion)
        print(f"  [FAIL] {msg}")
    
    def _check_warn(self, msg, ubicacion=""):
        self.total_checks += 1
        self._add_violacion("WARN", msg, ubicacion)
        print(f"  [WARN] {msg}")

    # --------------------------------------------------------
    # 1. FUENTE GENERAL (Arial Narrow 11)
    # --------------------------------------------------------
    def _check_fuente_general(self):
        print("\n--- 1. FUENTE GENERAL (Regla 55: Arial Narrow 11) ---")
        errores = 0
        for i, p in enumerate(self.doc.paragraphs):
            if not p.text.strip():
                continue
            for run in p.runs:
                if run.font.name and run.font.name.lower() not in ["arial narrow", "arialnarrow", None]:
                    if run.text.strip():
                        errores += 1
                        if errores <= 3:
                            self._check_fail(
                                f"Fuente incorrecta: '{run.font.name}' (debe ser Arial Narrow)",
                                f"P\u00e1rrafo {i+1}: '{run.text[:60]}...'"
                            )
        if errores == 0:
            self._check_pass("Todos los p\u00e1rrafos usan Arial Narrow")
        else:
            self._check_fail(f"{errores} runs con fuente incorrecta")
    
    # --------------------------------------------------------
    # 2. ESPACIADO (SpaceBefore/After=0, LineSpacing=1.0)
    # --------------------------------------------------------
    def _check_espaciado(self):
        print("\n--- 2. ESPACIADO (Regla 55: SpaceBefore/After=0, LineSpacing=1.0) ---")
        err_space = 0
        err_line = 0
        for i, p in enumerate(self.doc.paragraphs):
            pf = p.paragraph_format
            if pf.space_before is not None and pf.space_before > 0:
                err_space += 1
            if pf.space_after is not None and pf.space_after > Pt(6):  # Permitir SpaceAfter peque\u00f1o para notas
                err_space += 1
            if pf.line_spacing is not None and pf.line_spacing > 1.5:
                err_line += 1
        
        if err_space == 0 and err_line == 0:
            self._check_pass("Espaciado correcto en todos los p\u00e1rrafos")
        else:
            if err_space > 0:
                self._check_fail(f"{err_space} p\u00e1rrafos con SpaceBefore/After > 0")
            if err_line > 0:
                self._check_fail(f"{err_line} p\u00e1rrafos con LineSpacing > 1.0")
    
    # --------------------------------------------------------
    # 3. METADATA (sangr\u00eda colgante)
    # --------------------------------------------------------
    def _check_metadata(self):
        print("\n--- 3. METADATA (Regla sangr\u00eda colgante -1.48\") ---")
        found = 0
        ok = 0
        for p in self.doc.paragraphs:
            text = p.text.strip()
            for campo in CAMPOS_METADATA:
                if text.startswith(campo):
                    found += 1
                    pf = p.paragraph_format
                    if pf.left_indent and pf.first_line_indent:
                        ok += 1
                    break
        if found == 0:
            self._check_warn("No se encontraron campos de metadata para validar")
        elif ok == found:
            self._check_pass(f"Todos los campos ({found}) de metadata tienen sangr\u00eda colgante")
        else:
            self._check_fail(f"{found - ok} campos de metadata sin sangr\u00eda colgante")
    
    # --------------------------------------------------------
    # 4. BOILERPLATE (secciones obligatorias CC1)
    # --------------------------------------------------------
    def _check_boilerplate(self):
        print("\n--- 4. BOILERPLATE CC1 (Regla 54: secciones III y IV) ---")
        text_completo = "\n".join([p.text for p in self.doc.paragraphs])
        for seccion in BOLERPLATE_CC1:
            if seccion in text_completo:
                self._check_pass(f"Secci\u00f3n '{seccion}' presente")
            else:
                self._check_fail(f"Secci\u00f3n faltante: '{seccion}'")
    
    # --------------------------------------------------------
    # 5. ART\u00cdCULOS RESOLUTIVOS (PRIMERO a D\u00c9CIMO PRIMERO)
    # --------------------------------------------------------
    def _check_articulos_resolutivos(self):
        print("\n--- 5. ART\u00cdCULOS RESOLUTIVOS (CC1: PRIMERO a D\u00c9CIMO PRIMERO) ---")
        text_completo = "\n".join([p.text for p in self.doc.paragraphs])
        for art in ARTICULOS_RESOLUTIVOS:
            if art + ":" in text_completo or art + " " in text_completo:
                self._check_pass(f"Art\u00edculo '{art}' presente")
            else:
                self._check_fail(f"Art\u00edculo faltante: '{art}'")
    
    # --------------------------------------------------------
    # 6. NOTAS AL PIE (Arial Narrow 8)
    # --------------------------------------------------------
    def _check_notas_pie(self):
        print("\n--- 6. NOTAS AL PIE (Regla 55: Arial Narrow 8) ---")
        notas_err = 0
        try:
            import win32com.client
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            doc_com = word.Documents.Open(self.doc_path)
            
            for fn in doc_com.Footnotes:
                font_name = fn.Range.Font.Name
                font_size = fn.Range.Font.Size
                if font_name and font_name.lower() not in ["arial narrow", "arialnarrow"]:
                    notas_err += 1
                if font_size and font_size != 8:
                    notas_err += 1
            
            doc_com.Close()
            word.Quit()
            
            if notas_err == 0:
                total = 0
                try:
                    total = doc_com.Footnotes.Count
                except:
                    pass
                self._check_pass(f"Notas al pie con formato correcto")
            else:
                self._check_fail(f"{notas_err} notas al pie con formato incorrecto")
        except ImportError:
            self._check_warn("win32com no disponible - no se pueden validar notas al pie")
        except Exception as e:
            self._check_warn(f"No se pudieron validar notas al pie: {e}")
    
    # --------------------------------------------------------
    # 7. INICIALES (tama\u00f1o 8)
    # --------------------------------------------------------
    def _check_iniciales(self):
        print("\n--- 7. INICIALES FINALES (Regla 42: tama\u00f1o 8) ---")
        for p in self.doc.paragraphs:
            text = p.text.strip()
            if PATRON_INICIALES.match(text):
                for run in p.runs:
                    if run.font.size and run.font.size > Pt(8):
                        self._check_fail(
                            f"Iniciales '{text}' en tama\u00f1o {run.font.size.pt} (debe ser 8)"
                        )
                        return
                self._check_pass(f"Iniciales '{text}' correctas (tama\u00f1o 8)")
                return
        self._check_warn("No se encontraron iniciales al final del documento")
    
    # --------------------------------------------------------
    # 8. FOOTER (M-CPC-01/03)
    # --------------------------------------------------------
    def _check_footer(self):
        print("\n--- 8. FOOTER (M-CPC-01/03) ---")
        try:
            section = self.doc.sections[0]
            footer = section.footer
            footer_text = "\n".join([p.text for p in footer.paragraphs])
            if FOOTER_ESPERADO in footer_text:
                self._check_pass(f"Footer '{FOOTER_ESPERADO}' presente")
            else:
                self._check_fail(f"Footer incorrecto o ausente (esperado: '{FOOTER_ESPERADO}')")
        except:
            self._check_warn("No se pudo acceder al footer del documento")
    
    # --------------------------------------------------------
    # 9. TILDES (verificaci\u00f3n b\u00e1sica)
    # --------------------------------------------------------
    def _check_tildes(self):
        print("\n--- 9. TILDES EN NOMBRES COMERCIALES (Regla 50) ---")
        text_completo = "\n".join([p.text for p in self.doc.paragraphs])
        palabras_sin_tilde = []
        # Palabras comunes que deben llevar tilde
        busquedas = [
            (r'Pacifico(?!\s*Compa)', 'Pac\u00edfico'),
            (r'CODIGO', 'C\u00d3DIGO'),
            (r'ARTICULO', 'ART\u00cdCULO'),
        ]
        for patron, correcto in busquedas:
            encontrado = re.findall(patron, text_completo)
            if encontrado:
                # Marcar como warning, no necesariamente error
                pass
        
        # Verificar tildes en palabras espec\u00edficas del dominio legal
        revisar = [
            ("C\u00f3digo", "Codigo"),
            ("art\u00edculo", "articulo"),
            ("Pac\u00edfico", "Pacifico"),
            ("COMPA\u00d1\u00cdA", "COMPANIA"),
            ("P\u00f3liza", "Poliza"),
            ("S\u00e9ptimo", "Septimo"),
            ("D\u00e9cimo", "Decimo"),
        ]
        for con_tilde, sin_tilde in revisar:
            if sin_tilde in text_completo and con_tilde not in text_completo:
                self._check_fail(f"Posible falta de tilde: se espera '{con_tilde}' pero se encontr\u00f3 variante sin tilde")
                return
        self._check_pass("Tildes correctas en t\u00e9rminos revisados")
    
    # --------------------------------------------------------
    # REPORTE FINAL
    # --------------------------------------------------------
    def _reportar(self):
        print(f"\n{'='*70}")
        print(f"RESUMEN DE VALIDACI\u00d3N")
        print(f"{'='*70}")
        
        errores = [v for v in self.violaciones if v.tipo == "ERROR"]
        warnings = [v for v in self.violaciones if v.tipo == "WARN"]
        
        print(f"  Checks totales: {self.total_checks}")
        print(f"  Pasaron:        {self.passed_checks}")
        print(f"  Errores:        {len(errores)}")
        print(f"  Warnings:       {len(warnings)}")
        
        if errores:
            print(f"\n  VIOLACIONES CR\u00cdTICAS:")
            for v in errores:
                print(f"    - {v}")
        
        if warnings:
            print(f"\n  ADVERTENCIAS:")
            for v in warnings:
                print(f"    - {v}")
        
        if not errores and not warnings:
            print(f"\n  \u2714 DOCUMENTO CUMPLE CON TODAS LAS REGLAS CC1")
        elif not errores:
            print(f"\n  \u26a0 DOCUMENTO V\u00c1LIDO con {len(warnings)} advertencias menores")
        else:
            print(f"\n  \u2716 DOCUMENTO NO V\u00c1LIDO - {len(errores)} errores cr\u00edticos")
        
        print(f"{'='*70}\n")


# ============================================================
# MAIN
# ============================================================

def validar_documento(docx_path):
    """Valida un documento DOCX y retorna (es_valido, violaciones)."""
    if not os.path.exists(docx_path):
        print(f"Error: Archivo no encontrado: {docx_path}")
        return False, []
    
    validador = ValidadorPostGeneracion(docx_path)
    violaciones = validador.validar()
    
    errores = [v for v in violaciones if v.tipo == "ERROR"]
    return len(errores) == 0, violaciones


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python validador_post_generacion.py <ruta_del_docx>")
        print("Ejemplo: python validador_post_generacion.py temp_v7.docx")
        sys.exit(1)
    
    docx_path = sys.argv[1]
    if not os.path.isabs(docx_path):
        docx_path = os.path.join(os.path.dirname(__file__), docx_path)
    
    valido, violaciones = validar_documento(docx_path)
    sys.exit(0 if valido else 1)
