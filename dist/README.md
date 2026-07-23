# ResAdmi — Generador de Admisorios INDECOPI (CC1)

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Reglas: 80](https://img.shields.io/badge/reglas-80%20consolidadas-success)](docs/REGLAS_DE_REDACCION.md)
[![Tests: 15/15](https://img.shields.io/badge/tests-15%2F15-brightgreen)](tests/)
[![Build EXE](https://github.com/davidchaveznge-wq/ResAdmi/actions/workflows/build-release.yml/badge.svg)](https://github.com/davidchaveznge-wq/ResAdmi/actions)
[![Release](https://img.shields.io/badge/download-ResAdmi.exe-blue)](https://github.com/davidchaveznge-wq/ResAdmi/releases)

> Sistema profesional para generar **resoluciones admisorias** de la Comisión de
> Protección al Consumidor 1 (**CC1**) del INDECOPI (Sede Central, Perú),
> respetando con fidelidad milimétrica el modelo maestro institucional.

ResAdmi toma los datos de un expediente, genera el borrador con un LLM
(**Google Antigravity / Gemini** por defecto — el mejor lector de imágenes
escaneadas), lo valida contra **80 reglas consolidadas** en un motor
determinista, y produce un archivo `.docx` que clona la plantilla maestra CC1.

---

## 📋 Tabla de contenidos

- [¿Por qué ResAdmi?](#-por-qu%C3%A9-resadmi)
- [Características](#-caracter%C3%ADsticas)
- [Arquitectura](#-arquitectura)
- [Instalación](#-instalaci%C3%B3n)
- [Uso](#-uso)
- [Las 80 reglas](#-las-80-reglas)
- [Configuración de proveedores IA](#-configuraci%C3%B3n-de-proveedores-ia)
- [Compilar el ejecutable (.exe)](#-compilar-el-ejecutable-exe)
- [Troubleshooting](#-troubleshooting)
- [Estructura del repositorio](#-estructura-del-repositorio)

---

## 🎯 ¿Por qué ResAdmi?

Las iteraciones anteriores de este proyecto (documentadas en el chat
Antigravity → Z.ai) mostraron **fallas recurrentes**: notas al pie vacías,
formatos colapsados (documentos de 150 páginas en lugar de 6), tipificaciones
prohibidas (Art. 24), doble imputación (non bis in idem), pérdida del escudo
institucional, sangrías extrapoladas, etc.

ResAdmi v2.0 resuelve esto con **tres capas de defensa**:

1. **System prompt blindado** — el LLM recibe TODAS las reglas operativas
   inyectadas en cada llamada, no depende de su memoria.
2. **Motor determinista de reglas** (`src/rules_engine.py`) — 15 tests unitarios
   validan que las tipificaciones prohibidas y los errores históricos se
   detecten ANTES de construir el documento. Si hay una regla `[CRÍTICA]`
   violada, el .docx no se guarda.
3. **Clonado de plantilla maestra** — nunca se genera desde cero; el header
   institucional, el footer `M-CPC-01/03` y los estilos se preservan.

---

## ✨ Características

- ✅ **`.exe` ONEFILE** — todo embebido (código + plantilla + docs + dependencias). Doble click y listo.
- ✅ **Google Antigravity (Gemini)** como proveedor PRINCIPAL — mejor lector de
  imágenes escaneadas (fundamental para PDFs de denuncias y anexos).
- ✅ **Fallback automático** a Z.ai GLM, BigModel, DeepSeek, Kimi si Gemini falla.
- ✅ **80 reglas consolidadas** (`docs/REGLAS_DE_REDACCION.md`) con IDs estables
  `R-01..R-80` y tabla de conflictos resueltos.
- ✅ **Validación determinista** pre y post generación (rules_engine).
- ✅ **Notas al pie nativas** vía win32com con formato Arial Narrow 8 + sangría
  francesa + bold automático en leyes (Reglas R-68 a R-75).
- ✅ **Chat por expediente** — mantén conversación e instrucciones específicas
  para cada caso, integrables en la generación.
- ✅ **Aprendizaje de reglas** — sube modelos reales (PDF/imagen) y el sistema
  extrae con visión detalles técnicos/estilísticos y propone nuevas reglas
  (`R-XX`) que se acumulan en `APRENDIZAJE_PROPUESTAS.md`.
- ✅ **Selector de carpeta de salida** — elige dónde guardar cada resolución.
- ✅ **GUI moderna** (ttk custom theme, NO PowerShell) — Segoe UI, paleta cuidada.
- ✅ **GitHub Actions** — build automático del .exe en cada push, publicado en Releases.
- ✅ **CLI** para integración con workflows automatizados.

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    GUI Tkinter (src/main.py)                │
│  Formulario + reporte de validación + selección de IA       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Orquestador (src/app.py)                   │
│  generar_resolucion(): coordina el flujo completo           │
└───┬───────────────────┬───────────────────┬─────────────────┘
    │                   │                   │
    ▼                   ▼                   ▼
┌────────┐      ┌──────────────┐      ┌──────────────┐
│ IA     │      │ Motor reglas │      │ Builder      │
│ client │      │ (determinista)│     │ (.docx)      │
│        │      │              │      │              │
│ Z.ai   │──▶   │ R-01..R-80   │──▶   │ Clona        │
│ GLM    │ JSON │ 15 tests     │ OK?  │ plantilla    │
└────────┘      └──────────────┘      └──────┬───────┘
                                              │
                                              ▼
                                     ┌──────────────────┐
                                     │ Footnote injector│
                                     │ (win32com)       │
                                     │ Notas nativas    │
                                     └──────────────────┘
```

### Capas de defensa

| Capa | Qué hace | Archivo |
|------|----------|---------|
| 1. System prompt blindado | Inyecta las 80 reglas operativas al LLM | `src/system_prompt.py` |
| 2. Motor determinista | Valida el JSON antes de construir | `src/rules_engine.py` |
| 3. Clonado de plantilla | Preserva header/footer/imágenes | `src/builder.py` |
| 4. Notas nativas vía COM | Convierte `[[FN:...]]` a notas reales | `src/footnote_injector.py` |
| 5. Validación post | Verifica OOXML + reglas en el archivo final | `src/rules_engine.py` |

---

## 🚀 Instalación

### Opción A: Descargar el .exe (recomendado para usuarios)

1. Ve a <https://github.com/davidchaveznge-wq/ResAdmi/releases>
2. Descarga **`ResAdmi.exe`** (onefile, ~35 MB)
3. Doble click para abrir la GUI. No requiere Python ni carpetas externas.

### Opción B: Desde el código fuente

### Requisitos

- **Windows 10/11** (la inyección de notas nativas requiere Microsoft Word).
- **Python 3.10+** (probado con 3.10.11 y 3.14).
- **Microsoft Word** instalado (para notas al pie; opcional para el resto).
- **API key** de al menos un proveedor IA (Google Antigravity / Gemini recomendado).

### Paso a paso

```bash
# 1. Clonar el repo
git clone https://github.com/davidchaveznge-wq/ResAdmi.git
cd ResAdmi

# 2. Crear entorno virtual (recomendado)
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar al menos una API key (Gemini recomendado)
setx GEMINI_API_KEY "tu_api_key_aqui"            # CMD (persistente)
$env:GEMINI_API_KEY="tu_api_key_aqui"            # PowerShell (sesión)

# 5. Lanzar la GUI
python -m src.main

# 6. Opcional: compilar tu propio .exe
python build_exe.py
```

---

## 💻 Uso

### GUI

1. Pestaña **Expediente**: completa los campos (expediente, denunciante,
   denunciados, descripción de hechos).
2. Pestaña **Ajustes**: selecciona el proveedor IA y la plantilla maestra
   (por defecto `templates/PLANTILLA_MAESTRA_CC1.docx`).
3. Click **⚡ Generar resolución**.
4. Revisa el **reporte de validación** (errores críticos bloquean el guardado;
   avisos no).
5. Abre el archivo generado en la carpeta de salida.

### CLI

```bash
python -m src.cli \
  --expediente "0955-2026/CC1" \
  --denunciante "JUAN PÉREZ" \
  --denunciados "COMPAÑÍA DE SEGUROS X S.A.|aseguradora" \
  --resolucion 1 \
  --hechos hechos.txt \
  --proveedor zai
```

---

## 📜 Las 80 reglas

La fuente única de verdad es [`docs/REGLAS_DE_REDACCION.md`](docs/REGLAS_DE_REDACCION.md),
organizada en 6 ejes:

| Eje | Reglas | Tema |
|-----|--------|------|
| 1. Tipificación | R-01..R-15 | Arts. 1, 2, 18, 19, 56, 58, 152; prohibición Art. 24 e Inducción al error |
| 2. Estructura | R-16..R-30 | CC1 vs PS1, metadata, boilerplate, MYPE |
| 3. Redacción | R-31..R-45 | Conectores, infinitivos, requerimientos |
| 4. Hechos y referencias | R-46..R-55 | Espejo del escrito, nomenclatura SOAT |
| 5. Formato Word | R-56..R-75 | Arial Narrow, sangrías escalonadas, notas al pie |
| 6. Arquitectura | R-76..R-80 | Código modular, validación |

Cada regla tiene un **ID estable** (`R-XX`) referenciado por `src/rules_engine.py`
y los tests. Tabla de conflictos resueltos (LPAG vigente, Art. 56 vs 58, etc.)
al inicio del documento.

---

## 🔌 Configuración de proveedores IA

ResAdmi soporta cualquier API compatible con el esquema OpenAI
`/chat/completions`:

| Proveedor | Variable de entorno | Modelo por defecto |
|-----------|---------------------|--------------------|
| **Z.ai GLM** (recomendado) | `ZAI_API_KEY` | `glm-5.2` |
| BigModel | `BIGMODEL_API_KEY` | `glm-5.2` |
| DeepSeek | `DEEPSEEK_API_KEY` | `deepseek-v4-pro` |
| Kimi (Moonshot) | `KIMI_API_KEY` | `kimi-k2.6` |
| OpenAI-compatible | `OPENAI_API_KEY` + `OPENAI_BASE_URL` | configurable |

Configura cuál usar y el orden de fallback en `%APPDATA%/ResAdmi/settings.json`.

---

## 📦 Compilar el ejecutable (.exe)

```bash
pip install pyinstaller
python build_exe.py
```

El ejecutable queda en `dist/ResAdmi/ResAdmi.exe`. Distribuye la carpeta
completa (incluye `templates/` y `docs/`).

---

## 🛠️ Troubleshooting

| Problema | Causa | Solución |
|----------|-------|----------|
| "No se pudo generar el borrador con la IA" | Falta API key | Configura `ZAI_API_KEY` (u otra) en el entorno |
| "Hay N reglas CRÍTICAS violadas" | La IA devolvió algo que viola una regla dura | Revisa el reporte; regenera |
| Las notas al pie quedan como `[[FN:...]]` | Word no disponible o Linux/Mac | Abre en Word y conviértelas, o usa Windows |
| "Plantilla maestra no encontrada" | Falta `templates/PLANTILLA_MAESTRA_CC1.docx` | Ejecuta `python src/crear_plantilla_maestra.py` o coloca tu MODELO real |
| Fuente se ve mal (no Arial Narrow) | Estilo heredado de Word 365 | La app fuerza Arial Narrow vía win32com automáticamente |

---

## 📁 Estructura del repositorio

```
ResAdmi/
├── src/                         # Código fuente
│   ├── __init__.py
│   ├── main.py                  # GUI Tkinter (entrada del .exe)
│   ├── cli.py                   # CLI alternativo
│   ├── app.py                   # Orquestador
│   ├── ai_client.py             # Cliente multi-proveedor IA
│   ├── system_prompt.py         # Prompt blindado
│   ├── rules_engine.py          # Motor determinista (15 tests)
│   ├── builder.py               # Constructor .docx (clona plantilla)
│   ├── footnote_injector.py     # Notas nativas vía win32com
│   ├── config.py                # Settings persistente
│   └── crear_plantilla_maestra.py
├── docs/
│   └── REGLAS_DE_REDACCION.md   # ⭐ Las 80 reglas consolidadas
├── templates/
│   └── PLANTILLA_MAESTRA_CC1.docx
├── tests/
│   ├── test_rules_engine.py     # 15/15 tests
│   └── muestra_borrador.json
├── config/
│   ├── .env.example
│   └── config.example.yaml
├── build_exe.py                 # Compila el .exe
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 📄 Licencia

MIT — ver [LICENSE](LICENSE).

---

## 🙋 Soporte

- Issues: <https://github.com/davidchaveznge-wq/ResAdmi/issues>
- Documentación de reglas: [`docs/REGLAS_DE_REDACCION.md`](docs/REGLAS_DE_REDACCION.md)
