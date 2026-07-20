#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gestor_reglas.py - Motor de Reglas Vivo (Regla Suprema 56)
===========================================================
Lee REGLAS_APRENDIZAJE.md, extrae las reglas y las usa para validar
documentos DOCX generados. Convierte el archivo de markdown en un
motor de validaci\u00f3n ejecutable.

USO:
    from gestor_reglas import GestorReglas
    
    gestor = GestorReglas()
    gestor.cargar("REGLAS_APRENDIZAJE.md")
    
    # Buscar reglas
    reglas = gestor.buscar("MYPE")
    for r in reglas:
        print(f"Regla {r.numero}: {r.titulo}")
    
    # Validar documento
    resultado = gestor.validar_documento("temp.docx")
    print(resultado.informe())
"""

import os
import re
import json
from datetime import datetime


class Regla:
    """Representa una regla extra\u00edda del archivo markdown."""
    def __init__(self, numero, titulo, tipo, contenido, contexto=""):
        self.numero = numero
        self.titulo = titulo
        self.tipo = tipo  # "DO", "DONT", "FORMATO", "REGLAMENTO"
        self.contenido = contenido
        self.contexto = contexto
        self.palabras_clave = self._extraer_palabras_clave()
    
    def _extraer_palabras_clave(self):
        """Extrae palabras clave del t\u00edtulo y contenido."""
        texto = f"{self.titulo} {self.contexto} {self.contenido}"
        # Palabras relevantes de 4+ caracteres
        palabras = re.findall(r'\b[A-Za-z\u00c0-\u024f]{4,}\b', texto.upper())
        return set(palabras)
    
    def coincide(self, consulta):
        """Verifica si la regla coincide con una consulta."""
        consulta = consulta.upper()
        return (
            consulta in self.titulo.upper()
            or consulta in self.contenido.upper()
            or consulta in self.palabras_clave
        )
    
    def __str__(self):
        return f"R{self.numero:02d} [{self.tipo}] {self.titulo}"
    
    def a_dict(self):
        return {
            "numero": self.numero,
            "titulo": self.titulo,
            "tipo": self.tipo,
            "contenido": self.contenido[:200],
            "contexto": self.contexto[:200],
        }


class ResultadoValidacion:
    """Resultado de validar un documento contra las reglas."""
    def __init__(self, doc_path=""):
        self.doc_path = doc_path
        self.reglas_aplicadas = []
        self.reglas_cumplidas = []
        self.reglas_violadas = []
        self.reglas_no_verificables = []
        self.timestamp = datetime.now()
    
    def agregar_cumplida(self, regla, detalle=""):
        self.reglas_aplicadas.append(regla)
        self.reglas_cumplidas.append((regla, detalle))
    
    def agregar_violada(self, regla, detalle=""):
        self.reglas_aplicadas.append(regla)
        self.reglas_violadas.append((regla, detalle))
    
    def agregar_no_verificable(self, regla, razon=""):
        self.reglas_no_verificables.append((regla, razon))
    
    def es_valido(self):
        return len(self.reglas_violadas) == 0
    
    def informe(self):
        lines = []
        lines.append(f"\n{'='*70}")
        lines.append(f"INFORME DE VALIDACI\u00d3N CONTRA REGLAS DE APRENDIZAJE")
        lines.append(f"{'='*70}")
        lines.append(f"Documento: {os.path.basename(self.doc_path) if self.doc_path else 'N/A'}")
        lines.append(f"Fecha: {self.timestamp.strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"{'='*70}")
        
        if self.reglas_cumplidas:
            lines.append(f"\n\u2714 REGLAS CUMPLIDAS ({len(self.reglas_cumplidas)}):")
            for r, d in self.reglas_cumplidas:
                lines.append(f"  \u2714 R{r.numero:02d}: {r.titulo}")
        
        if self.reglas_violadas:
            lines.append(f"\n\u2716 REGLAS VIOLADAS ({len(self.reglas_violadas)}):")
            for r, d in self.reglas_violadas:
                lines.append(f"  \u2716 R{r.numero:02d}: {r.titulo}")
                if d:
                    lines.append(f"     Detalle: {d}")
        
        if self.reglas_no_verificables:
            lines.append(f"\n\u26a0 REGLAS NO VERIFICABLES ({len(self.reglas_no_verificables)}):")
            for r, razon in self.reglas_no_verificables:
                lines.append(f"  \u26a0 R{r.numero:02d}: {r.titulo} - {razon}")
        
        lines.append(f"\n{'='*70}")
        lines.append(f"RESUMEN: {len(self.reglas_cumplidas)} cumplidas, "
                     f"{len(self.reglas_violadas)} violadas, "
                     f"{len(self.reglas_no_verificables)} no verificables")
        if self.es_valido():
            lines.append(f"\u2714 DOCUMENTO V\u00c1LIDO seg\u00fan reglas de aprendizaje")
        else:
            lines.append(f"\u2716 DOCUMENTO NO V\u00c1LIDO - revisar violaciones")
        lines.append(f"{'='*70}\n")
        
        return "\n".join(lines)


class GestorReglas:
    """
    Motor de reglas que lee REGLAS_APRENDIZAJE.md y permite
    validar documentos contra ellas.
    """
    
    def __init__(self):
        self.reglas = []
        self.ultima_carga = None
        self.ruta_origen = ""
    
    def cargar(self, ruta=None):
        """
        Carga las reglas desde el archivo markdown.
        Si no se especifica ruta, busca en ubicaciones por defecto.
        """
        if ruta is None:
            # Buscar en ubicaciones por defecto
            candidatos = [
                "REGLAS_APRENDIZAJE.md",
                os.path.join(os.path.dirname(__file__), "REGLAS_APRENDIZAJE.md"),
                os.path.join(os.path.dirname(__file__), "..", "automatizacion_antigravity", "REGLAS_APRENDIZAJE.md"),
            ]
            for c in candidatos:
                if os.path.exists(c):
                    ruta = c
                    break
        
        if not ruta or not os.path.exists(ruta):
            raise FileNotFoundError(f"No se encontr\u00f3 REGLAS_APRENDIZAJE.md en: {ruta}")
        
        self.ruta_origen = os.path.abspath(ruta)
        with open(self.ruta_origen, "r", encoding="utf-8") as f:
            contenido = f.read()
        
        self.reglas = self._parsear(contenido)
        self.ultima_carga = datetime.now()
        
        print(f"GestorReglas: {len(self.reglas)} reglas cargadas desde {os.path.basename(self.ruta_origen)}")
        return self.reglas
    
    def _parsear(self, contenido):
        """
        Parsea el markdown y extrae las reglas estructuradas.
        Reconoce:
        - Reglas numeradas (39., 40., etc.)
        - Secciones: LO QUE SE DEBE HACER, LO QUE NO SE DEBE HACER, REGLAS ESTRICTAS
        - Reglas con t\u00edtulos en may\u00fasculas (ej. SIEMPRE EXIGIR LA ACREDITACI\u00d3N MYPE...)
        """
        reglas = []
        lineas = contenido.split("\n")
        
        i = 0
        contexto_actual = ""
        
        # Determinar el tipo de secci\u00f3n basado en headers
        tipo_seccion = "REGLAMENTO"
        
        while i < len(lineas):
            linea = lineas[i].strip()
            
            # Detectar secciones por headers
            if "LO QUE SE DEBE HACER" in linea.upper():
                tipo_seccion = "DO"
                i += 1
                continue
            elif "LO QUE NO SE DEBE HACER" in linea.upper():
                tipo_seccion = "DONT"
                i += 1
                continue
            elif "REGLAS ESTRICTAS DE ESTRUCTURA" in linea.upper():
                tipo_seccion = "FORMATO"
                i += 1
                continue
            
            # Detectar regla numerada (ej. "39. TITULO" o "39. NUNCA EXTRAPOLAR...")
            match_num = re.match(r'^(\d+)\.\s+(.+)$', linea)
            if match_num:
                num = int(match_num.group(1))
                titulo = match_num.group(2).strip()
                
                # Extraer contexto (primer p\u00e1rrafo despu\u00e9s de "Contexto")
                contexto = ""
                contenido = ""
                j = i + 1
                while j < len(lineas):
                    sig = lineas[j].strip()
                    if re.match(r'^\d+\.\s+', sig):
                        break
                    if sig.upper().startswith("CONTEXTO"):
                        # Leer contexto
                        k = j + 1
                        ctx_lines = []
                        while k < len(lineas) and lineas[k].strip() and not lineas[k].strip().upper().startswith("LA REGLA DEFINITIVA") and not re.match(r'^\d+\.\s+', lineas[k].strip()):
                            ctx_lines.append(lineas[k].strip())
                            k += 1
                        contexto = " ".join(ctx_lines)
                        j = k
                        continue
                    if sig.upper().startswith("LA REGLA DEFINITIVA") or sig.upper().startswith("LA REGLA DEFINTIVA"):
                        k = j + 1
                        cont_lines = []
                        while k < len(lineas) and lineas[k].strip() and not lineas[k].strip().upper().startswith("CONTEXTO") and not re.match(r'^\d+\.\s+', lineas[k].strip()):
                            cont_lines.append(lineas[k].strip())
                            k += 1
                        contenido = " ".join(cont_lines)
                        j = k
                        continue
                    j += 1
                
                regla = Regla(
                    numero=num,
                    titulo=titulo,
                    tipo=tipo_seccion,
                    contenido=contenido or titulo,
                    contexto=contexto,
                )
                reglas.append(regla)
                i = j
                continue
            
            # Detectar reglas en formato de lista (DOs/DONTs con vi\u00f1etas)
            if linea.startswith("- **") and ":**" in linea:
                # Extraer como regla
                pass  # Por ahora ignoramos las vi\u00f1etas sueltas
            
            i += 1
        
        return reglas
    
    def buscar(self, consulta):
        """Busca reglas que coincidan con la consulta."""
        consulta_lower = consulta.lower()
        resultados = []
        for r in self.reglas:
            if (consulta_lower in r.titulo.lower()
                or consulta_lower in r.contenido.lower()
                or consulta_lower in r.contexto.lower()):
                resultados.append(r)
        return resultados
    
    def obtener_por_numero(self, numero):
        """Obtiene una regla por su n\u00famero."""
        for r in self.reglas:
            if r.numero == numero:
                return r
        return None
    
    def listar_por_tipo(self, tipo):
        """Lista reglas de un tipo espec\u00edfico (DO, DONT, FORMATO, REGLAMENTO)."""
        return [r for r in self.reglas if r.tipo == tipo]
    
    def validar_documento(self, docx_path, verbose=True):
        """
        Valida un documento DOCX contra las reglas cargadas.
        
        NOTA: Esta validaci\u00f3n es sem\u00e1ntica - usa el validador_post_generacion
        para las reglas t\u00e9cnicas y aqu\u00ed hacemos validaci\u00f3n de reglas de contenido.
        """
        from validador_post_generacion import ValidadorPostGeneracion
        
        resultado = ResultadoValidacion(docx_path)
        
        if verbose:
            print(f"\nValidando contra {len(self.reglas)} reglas de aprendizaje...")
        
        if not os.path.exists(docx_path):
            resultado.agregar_violada(
                Regla(0, "Existencia del archivo", "REGLAMENTO", ""),
                f"Archivo no encontrado: {docx_path}"
            )
            return resultado
        
        # Primero, validaci\u00f3n t\u00e9cnica
        validador = ValidadorPostGeneracion(docx_path)
        violaciones = validador.validar()
        
        # Registrar cada violaci\u00f3n t\u00e9cnica contra reglas relevantes
        for v in violaciones:
            # Buscar reglas relevantes
            relevantes = self.buscar(v.descripcion[:30])
            if not relevantes:
                relevantes = [Regla(0, "Regla t\u00e9cnica general", "FORMATO", v.descripcion)]
            
            for r in relevantes[:2]:
                if v.tipo == "ERROR":
                    resultado.agregar_violada(r, v.descripcion)
                else:
                    resultado.agregar_cumplida(r, v.descripcion)
        
        # Verificar reglas espec\u00edficas por contenido
        from docx import Document
        doc = Document(docx_path)
        texto_completo = "\n".join([p.text for p in doc.paragraphs])
        
        # Regla 50: Non bis in idem
        r50 = self.obtener_por_numero(50)
        if r50:
            # Verificar si hay m\u00faltiples imputaciones para el mismo hecho
            arts_mencionados = re.findall(r'art\u00edculos?\s+(\d+)[\u00b0\s]*', texto_completo, re.IGNORECASE)
            if len(set(arts_mencionados)) >= 2:
                # Podr\u00eda ser v\u00e1lido si son hechos distintos, solo advertimos
                resultado.agregar_no_verificable(
                    r50,
                    "Verificar manualmente que no se imputen dos infracciones por un mismo hecho"
                )
        
        # Regla 48: Compa\u00f1\u00eda aseguradora vs proveedor denunciado
        r48 = self.obtener_por_numero(48)
        if r48 and ("LA POSITIVA" in texto_completo or "PAC\u00cdFICO" in texto_completo or "INTERSEGURO" in texto_completo):
            if "proveedor denunciado" in texto_completo.lower():
                resultado.agregar_violada(
                    r48,
                    "Usar 'proveedor denunciado' cuando la empresa es una aseguradora (debe ser 'compa\u00f1\u00eda aseguradora')"
                )
        
        # Regla 36: MYPE obligatorio
        r36 = self.obtener_por_numero(36)
        if r36 and "caso califique" not in texto_completo.lower() and "mype" in texto_completo.lower():
            resultado.agregar_no_verificable(r36, "Verificar que el inciso MYPE est\u00e9 presente en TERCERO")
        
        if verbose:
            print(resultado.informe())
        
        return resultado
    
    def exportar_json(self, ruta_salida="reglas_export.json"):
        """Exporta las reglas a JSON para uso en otros sistemas."""
        data = {
            "metadata": {
                "fuente": self.ruta_origen,
                "carga": self.ultima_carga.isoformat() if self.ultima_carga else "",
                "total_reglas": len(self.reglas),
            },
            "reglas": [r.a_dict() for r in self.reglas],
        }
        with open(ruta_salida, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Reglas exportadas a {ruta_salida}")
        return ruta_salida


# ============================================================
# MAIN
# ============================================================

def main():
    import sys
    
    gestor = GestorReglas()
    
    # Cargar reglas
    try:
        gestor.cargar()
    except FileNotFoundError:
        print("Error: No se encontr\u00f3 REGLAS_APRENDIZAJE.md")
        print("Buscando en el directorio actual...")
        for f in os.listdir("."):
            if "REGLAS" in f.upper() and f.endswith(".md"):
                gestor.cargar(f)
                break
        else:
            print("No se encontr\u00f3 el archivo de reglas.")
            sys.exit(1)
    
    if len(sys.argv) < 2:
        print(f"\nGestorReglas: {len(gestor.reglas)} reglas cargadas")
        print("\nUSO:")
        print("  python gestor_reglas.py buscar <consulta>     - Buscar reglas")
        print("  python gestor_reglas.py listar [tipo]          - Listar reglas")
        print("  python gestor_reglas.py validar <docx>         - Validar documento")
        print("  python gestor_reglas.py exportar [ruta.json]   - Exportar a JSON")
        print("\nTipos: DO, DONT, FORMATO, REGLAMENTO")
        print("\nEjemplos:")
        print("  python gestor_reglas.py buscar MYPE")
        print("  python gestor_reglas.py listar FORMATO")
        print("  python gestor_reglas.py validar temp_v7.docx")
        print("  python gestor_reglas.py exportar")
        return
    
    comando = sys.argv[1]
    
    if comando == "buscar" and len(sys.argv) > 2:
        resultados = gestor.buscar(sys.argv[2])
        print(f"\nReglas encontradas para '{sys.argv[2]}': {len(resultados)}")
        for r in resultados:
            print(f"\n  R{r.numero:02d} [{r.tipo}] {r.titulo}")
            if r.contexto:
                print(f"  Contexto: {r.contexto[:100]}...")
        if not resultados:
            print("  (sin resultados)")
    
    elif comando == "listar":
        tipo = sys.argv[2].upper() if len(sys.argv) > 2 else None
        if tipo:
            reglas = gestor.listar_por_tipo(tipo)
            print(f"\nReglas tipo '{tipo}': {len(reglas)}")
        else:
            reglas = gestor.reglas
            print(f"\nTodas las reglas: {len(reglas)}")
        for r in reglas:
            print(f"  R{r.numero:02d} [{r.tipo}] {r.titulo}")
    
    elif comando == "validar" and len(sys.argv) > 2:
        docx_path = sys.argv[2]
        resultado = gestor.validar_documento(docx_path)
    
    elif comando == "exportar":
        ruta = sys.argv[2] if len(sys.argv) > 2 else "reglas_export.json"
        gestor.exportar_json(ruta)
    
    else:
        print(f"Comando no reconocido: {comando}")


if __name__ == "__main__":
    main()
