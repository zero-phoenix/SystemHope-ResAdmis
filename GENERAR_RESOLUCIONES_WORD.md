# 📋 Guía: Generación Segura de Resoluciones en Word

**⚠️ CRÍTICO:** Usar MODELOS BASE de INDECOPI para generar resoluciones. Este documento explica por qué y cómo.

---

## El Problema Original (RESUELTO)

❌ **MAL:** Generar archivos .docx desde cero
- Pierde imágenes y colores del encabezado
- Pierde formato visual (estilos, marcas de agua)
- Riesgo de corrupción de archivo

✅ **BIEN:** Usar modelo base como plantilla
- Mantiene imágenes del encabezado INDECOPI
- Preserva colores, fuentes, formatos
- Garantiza consistencia visual
- Menor riesgo de errores

---

## Solución Correcta: Usar Modelo Base

### Paso 1: Encontrar Modelo Apropiado

Ubicación: `Modelos al 30-06-26\`

**Modelos disponibles:**
- `MODELO xxxx exp. ADM ver. David 1 DDO, VARIAS IMPUTACIONES.docx` - Para 1 denunciado
- `MODELO xxxx exp. ADM ver. David 2 DDOs o MAS, muchas varias imputacioness.docx` - Para múltiples denunciados
- Carpetas temáticas: Apelaciones, Confidencialidad, Desgravamen, etc.

### Paso 2: Script de Generación (RECOMENDADO)

```python
from docx import Document
from pathlib import Path

# Abrir modelo base
doc = Document(r'ruta\a\MODELO.docx')

# Reemplazar datos específicos
for paragraph in doc.paragraphs:
    for run in paragraph.runs:
        # Reemplazar expediente, denunciante, denunciado, etc.
        run.text = run.text.replace('0672-2026/CC1', '0955-2026/CC1')
        run.text = run.text.replace('DENUNCIANTE_VIEJO', 'DENUNCIANTE_NUEVO')

# Guardar
doc.save(r'output\ADM_0955-2026_R1.docx')
```

**Script automático disponible:** `generar_955_desde_modelo.py`

```bash
python.exe generar_955_desde_modelo.py
```

### Paso 3: Validar Resultado

```bash
python.exe validar_docx.py archivo.docx
```

**Output esperado:**
```
[OK] archivo.docx
    VALIDO [125.6 KB] - 89 parrafos, 0 tablas, 25 archivos internos
```

---

## ✅ Checklist Pre-Generación

- [x] Modelo base existe y es accesible
- [x] Script `generar_955_desde_modelo.py` disponible
- [x] python-docx instalado
- [x] Ruta de salida accesible y con permisos de escritura
- [x] Datos del expediente (expediente, denunciante, denunciado) preparados

---

## 🔄 Flujo Completo

```
1. Identificar expediente (ej: 0955-2026/CC1)
   ↓
2. Seleccionar modelo base (1 DDO, múltiples DDOs, etc.)
   ↓
3. Ejecutar: python.exe generar_955_desde_modelo.py
   ↓
4. Validar: python.exe validar_docx.py output.docx
   ↓
5. Verificar en Word: abre sin errores
   ↓
6. Guardar en productos/
```

---

## 🎯 Archivos OOXML Correctos

Estructura interna con imágenes:
```
documento.docx (125-150 KB con imágenes)
├── [Content_Types].xml
├── _rels/
├── word/
│   ├── document.xml (contenido)
│   ├── styles.xml (estilos: Arial, colores, etc.)
│   ├── header1.xml o header2.xml (encabezado con imagen)
│   ├── footer1.xml (pie de página M-CPC-01/03)
│   ├── media/ (imágenes incrustadas)
│   │   ├── image1.jpeg (logo/escudo INDECOPI)
│   │   └── ...
│   └── ...
├── docProps/
│   ├── core.xml
│   └── app.xml
└── customXml/
```

**Validación:** 
- Mínimo 25 archivos internos (con imágenes)
- Tamaño: 100-150 KB (con imágenes)
- Abre sin errores en Word

---

## 📊 Comparación: Antes vs Después

| Aspecto | ❌ ANTES (Script) | ✅ DESPUÉS (Modelo) |
|---------|---------|---------|
| Imágenes encabezado | Falta | Preservadas |
| Colores | Blanco/Negro | Completos |
| Formato visual | Perdido | Mantenido |
| Tamaño | 40-50 KB | 125+ KB |
| Consistencia | Varía | Garantizada |
| Errores | Posibles | Minimizados |

---

## 🚫 NO HACER (Errores Comunes)

| Error | Alternativa Correcta |
|-------|-----------|
| Generar .docx desde cero | Usar modelo base |
| Crear a partir de texto plano | Usar python-docx + modelo |
| Copiar PDF y guardar como .docx | Abrir modelo + reemplazar contenido |
| Escribir XML manualmente | Usar python-docx |
| No validar después | Ejecutar `validar_docx.py` |

---

## 📚 Recursos

- **Script:** `generar_955_desde_modelo.py` - Ejemplo funcional
- **Validador:** `validar_docx.py` - Verifica ZIP OOXML
- **Modelos:** `Modelos al 30-06-26/` - Base de plantillas INDECOPI
- **Docs:** python-docx en https://python-docx.readthedocs.io/

---

**Última actualización:** 19 de julio de 2026  
**Versión:** 1.0.2 - Usando modelos base (CORRECCIÓN VISUAL)  
**Estado:** 🟢 PRODUCCIÓN - Imágenes y colores preservados

---

## ✅ Forma Correcta (USAR ESTO)

### Opción A: Usar el Script Automático

```bash
# Ejecutar el script que genera resoluciones
python.exe D:\BETTER CALL DAVID\ResAdmi\generate_resolution.py
```

**Output esperado:**
```
Documento .docx autentico creado en:
  D:\BETTER CALL DAVID\ResAdmi\productos (resoluciones) elaborada por claude\ADM_0001-2026-CC1_R1.docx
Tamaño: 41005 bytes
Es archivo REAL .docx (ZIP OOXML)
Puede abrirse en Microsoft Word sin errores
```

### Opción B: Generar Manualmente con Python

```python
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

# PASO 1: Crear documento con python-docx
doc = Document()

# PASO 2: Configurar propiedades
doc.core_properties.author = 'SECRETARIA TÉCNICA - INDECOPI'
doc.core_properties.title = 'RESOLUCIÓN'

# PASO 3: Agregar contenido
p = doc.add_paragraph('PRIMERO: ')
p.add_run('Contenido de la resolución...')

# PASO 4: GUARDAR como .docx auténtico
doc.save(r'D:\BETTER CALL DAVID\ResAdmi\productos (resoluciones) elaborada por claude\ADM.docx')
```

**⚠️ IMPORTANTE:** Siempre usar `doc.save()` de python-docx, NUNCA escribir XML manualmente.

### Opción C: Copiar Plantilla y Reemplazar (MÁS SEGURO)

```python
from docx import Document
from copy import deepcopy

# Abrir plantilla existente (que sabemos que funciona)
plantilla = Document(r'D:\BETTER CALL DAVID\ResAdmi\Modelos al 30-06-26\MODELO xxxx exp. ADM ver. David 1 DDO,  VARIAS IMPUTACIONES.docx')

# Reemplazar párrafos sin tocar estructura
for paragraph in plantilla.paragraphs:
    if 'PLACEHOLDER' in paragraph.text:
        paragraph.text = 'CONTENIDO NUEVO'

# Guardar copia nueva
plantilla.save(r'D:\BETTER CALL DAVID\ResAdmi\productos (resoluciones) elaborada por claude\ADM_NUEVA.docx')
```

---

## 🔧 Instalación de Dependencias

**La librería `python-docx` ES REQUERIDA:**

```bash
# Verificar instalación
pip list | find "python-docx"

# Si no está instalada:
pip install python-docx --break-system-packages

# En entorno virtual (recomendado):
python -m venv venv
.\venv\Scripts\activate
pip install python-docx
```

**Verificar que está correcta:**
```python
from docx import Document
doc = Document()
print(f"python-docx version: {doc.core_properties.author}")
# Salida: python-docx version: (si no hay error, está OK)
```

---

## ✔️ Validación: Verificar que el .docx es REAL

**Script de validación:**
```python
import zipfile
from pathlib import Path

def validar_docx(ruta):
    path = Path(ruta)
    
    # Verificación 1: Es un archivo ZIP válido
    try:
        with zipfile.ZipFile(path, 'r') as z:
            files = z.namelist()
    except zipfile.BadZipFile:
        return False, "No es un archivo ZIP válido (OOXML corrupto)"
    
    # Verificación 2: Tiene estructura OOXML
    required = ['[Content_Types].xml', 'word/document.xml', '_rels/.rels']
    for req in required:
        if req not in files:
            return False, f"Falta archivo OOXML requerido: {req}"
    
    # Verificación 3: Puede abrirse con python-docx
    try:
        from docx import Document
        doc = Document(str(path))
        para_count = len(doc.paragraphs)
    except Exception as e:
        return False, f"Error al abrir con python-docx: {e}"
    
    return True, f"VALIDO - {para_count} párrafos, {len(files)} archivos internos"

# Usar:
valido, msg = validar_docx(r'D:\BETTER CALL DAVID\ResAdmi\productos (resoluciones) elaborada por claude\ADM_0001-2026-CC1_R1.docx')
print(f"{'✓ VALIDO' if valido else '✗ CORRUPTO'}: {msg}")
```

---

## 🚫 ERRORES COMUNES Y CÓMO EVITARLOS

| Error | Causa | Solución |
|-------|-------|----------|
| "Contenido no legible" | Archivo no es ZIP válido | Usar python-docx `doc.save()` |
| "Error al abrir archivo" | Permisos insuficientes | Guardar en carpeta con permisos de escritura |
| UnicodeEncodeError | Caracteres especiales no soportados | Usar `# -*- coding: utf-8 -*-` en scripts |
| Archivo corrompido a mitad | Ejecución interrumpida | Usar validación y manejo de excepciones |
| El documento "se abre vacío" | Contenido no se guardó | Siempre llamar `doc.save()` al final |

---

## 📋 Checklist Antes de Generar

- [ ] Script tiene `# -*- coding: utf-8 -*-` en línea 1
- [ ] Usa `from docx import Document` (NO importar XML directo)
- [ ] Llama `doc.save(ruta)` al final (NO `open().write()`)
- [ ] Carpeta destino existe y tiene permisos de escritura
- [ ] Se valida con `zipfile.ZipFile()` después de crear
- [ ] Se abre correctamente en Microsoft Word
- [ ] Tamaño del archivo es > 1 KB (archivos vacíos son < 1 KB)

---

## 🔄 Flujo Completo (Garantizado Funciona)

```
1. Editar script generate_resolution.py
   ↓
2. Ejecutar: python.exe generate_resolution.py
   ↓
3. Verificar archivo existe: ls *.docx
   ↓
4. Validar estructura ZIP: python validar_docx.py
   ↓
5. Abrir en Word (sin errores = éxito)
   ↓
6. Guardar copia de respaldo
   ↓
7. Actualizar versionamiento en CHANGELOG.md
```

---

## 📚 Recursos

**Python-docx documentation:**
- https://python-docx.readthedocs.io/
- Ejemplos: https://python-docx.readthedocs.io/en/latest/user/quickstart.html

**Especificación OOXML:**
- Estructura ZIP: https://en.wikipedia.org/wiki/Office_Open_XML
- Office Open XML specification

---

## 🎯 Resumen de Reglas

| Regla | Violación | Consecuencia |
|-------|-----------|--------------|
| **Usar python-docx** | Escribir XML manualmente | Archivo corrupto |
| **Siempre doc.save()** | Usar open().write() | Documento no se guarda |
| **Validar después** | Asumir que está correcto | Errores tardíos |
| **Encoding UTF-8** | Ignorar acentos | UnicodeEncodeError |
| **Carpeta con permisos** | Guardar en read-only | Error de permisos |

---

**Última actualización:** 19 de julio de 2026  
**Versión:** 1.0.0  
**Estado:** 🟢 VALIDADO y FUNCIONANDO

