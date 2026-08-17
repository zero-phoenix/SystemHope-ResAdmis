# ResAdmi - Sistema de Automatización de Resoluciones Administrativas

> Herramienta profesional para generar resoluciones conformes a estándares INDECOPI (Comisión de Protección al Consumidor - Perú)

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Repository Status](https://img.shields.io/badge/status-active-brightgreen)](https://github.com/davidchaveznge-wq/ResAdmi)

---

## 📋 Descripción

**ResAdmi** es un sistema de automatización que simplifica la creación de resoluciones administrativas para procesos legales. Permite generar documentos conformes a estándares específicos de redacción legal mediante la combinación de:

- **Plantillas Word profesionales** pre-diseñadas
- **Scripts Python** que aplican reglas de redacción automáticamente
- **Validación integrada** de normas INDECOPI
- **Documentación exhaustiva** de procedimientos

### Características Principales

✅ Generación automatizada de Resoluciones de Primera Instancia (R1)  
✅ Generación de Resoluciones de Apelación  
✅ Validación de reglas de tipificación de infracciones  
✅ Manejo de notificaciones por múltiples canales  
✅ Generación de memorandos administrativos  
✅ Respeto automático de formatos y estilos legales  

---

## 🚀 Inicio Rápido

### Requisitos Previos

- **Python 3.8+**
- **Microsoft Word** (para integración via `win32com`)
- **Sistema Operativo:** Windows (recomendado) o Linux/Mac (requiere ajustes)

### 1. Instalación

```bash
# Clonar el repositorio
git clone https://github.com/davidchaveznge-wq/ResAdmi.git
cd ResAdmi

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración Inicial

```bash
# Crear archivo de configuración local
cp config/.env.example .env

# Editar .env con tus rutas
# TEMPLATE_PATH=/ruta/a/tus/plantillas
# OUTPUT_PATH=/ruta/para/documentos/generados
```

### 3. Primer Uso

```python
from scripts.builder import DocumentBuilder
from config import Config

# Cargar configuración
config = Config.from_env()

# Crear instancia del builder
builder = DocumentBuilder(
    template_path=config.TEMPLATE_PATH,
    rules_path="automatizacion_antigravity/REGLAS_DE_APRENDIZAJE.md"
)

# Generar resolución
resultado = builder.build(
    expediente="2190-2026",
    denunciante="Nombre del Denunciante",
    denunciado="Empresa Denunciada",
    hechos=[
        "Primer hecho alegado",
        "Segundo hecho alegado"
    ],
    output_path=config.OUTPUT_PATH
)

print(f"✅ Documento generado: {resultado}")
```

---

## 📁 Estructura del Proyecto

```
ResAdmi/
├── README.md                              # Este archivo
├── LICENSE                                # Licencia MIT
├── CHANGELOG.md                           # Historial de versiones
├── requirements.txt                       # Dependencias Python
├── .gitignore                             # Archivos ignorados por Git
│
├── docs/                                  # 📚 Documentación
│   └── REGLAS_DE_REDACCION.md            # Guía de reglas administrativas
│
├── templates/                             # 📄 Plantillas Word
│   ├── resoluciones/
│   │   ├── base_ordinaria.docx           # Modelo base
│   │   ├── apelacion_r1.docx             # Resolución de apelación
│   │   └── ...
│   ├── memos/
│   └── oficios/
│
├── scripts/                               # 🐍 Scripts Python
│   ├── __init__.py
│   ├── builder.py                         # Módulo principal
│   ├── utils/
│   │   ├── docx_handler.py               # Manipulación de .docx
│   │   ├── rules_validator.py            # Validación de reglas
│   │   └── config.py                     # Configuración
│   └── test_builder.py                    # Tests unitarios
│
├── automatizacion_antigravity/            # 🤖 Automatización específica
│   ├── build_exp2190.py                  # Script para expediente 2190
│   ├── build_r4.py                       # Script para Resolución R4
│   ├── insert_footnotes.py               # Insertor de notas al pie
│   └── REGLAS_DE_APRENDIZAJE.md          # Base de conocimiento
│
├── config/                                # ⚙️ Configuración
│   ├── config.example.yaml               # Plantilla config
│   └── .env.example                      # Plantilla variables entorno
│
└── expedientes/                           # 📂 Datos de casos (GITIGNORED)
    └── [caso-id]/
        ├── input.json                    # Datos del caso
        └── output/
            └── ADM_[numero]_v1.docx      # Documento generado
```

---

## 📖 Documentación

### Guías Disponibles

| Documento | Descripción |
|-----------|------------|
| [REGLAS_DE_APRENDIZAJE.md](automatizacion_antigravity/REGLAS_DE_APRENDIZAJE.md) | Matriz de DOs y DONTs para redacción legal |
| [GENERAR_RESOLUCIONES_WORD.md](GENERAR_RESOLUCIONES_WORD.md) | 🔴 **CRÍTICO** - Usar modelos base INDECOPI para generar .docx (preserva imágenes y colores) |
| [ANALISIS_Y_MEJORAS.md](ANALISIS_Y_MEJORAS.md) | Análisis técnico y roadmap de mejoras |
| [CHANGELOG.md](CHANGELOG.md) | Historial de versiones y cambios |

### Ejemplos de Uso

Consulta la carpeta `expedientes/` para ver ejemplos de cómo se estructuran los datos de entrada.

---

## 🛠️ Desarrollo

### Instalación para Desarrolladores

```bash
# Instalar con extras de desarrollo
pip install -r requirements.txt

# Instalar pre-commit hooks (opcional)
pip install pre-commit
pre-commit install
```

### Ejecutar Tests

```bash
pytest tests/ -v
pytest tests/ --cov=scripts/ # Con cobertura
```

### Estilo de Código

El proyecto usa:
- **Black** para formatting
- **Flake8** para linting
- **Type hints** para seguridad de tipos

```bash
black scripts/
flake8 scripts/
```

---

## 🔐 Consideraciones de Seguridad

⚠️ **IMPORTANTE:** Este proyecto maneja documentos legales que pueden contener:
- Nombres de personas
- Números de expedientes confidenciales
- Información financiera sensible

### Mejores Prácticas

- ✅ **Nunca** commitear datos reales al repositorio
- ✅ Usar `.gitignore` para excluir documentos generados
- ✅ Usar variables de entorno para rutas sensibles
- ✅ Anonimizar documentos antes de compartirlos
- ✅ Almacenar datos en directorios excluidos (`expedientes/` está gitignored)

---

## 📞 Soporte

### Problemas Comunes

**P: "Word encontró contenido no legible" / "Error al abrir archivo .docx"**  
R: **⚠️ CRÍTICO** - El archivo está corrupto. Lee [GENERAR_RESOLUCIONES_WORD.md](GENERAR_RESOLUCIONES_WORD.md) para la solución. Causa: archivo no era ZIP OOXML válido. Usa siempre `python-docx` y `doc.save()`.

**P: "Module 'win32com' not found"**  
R: Ejecuta `pip install pywin32` y reinicia Python.

**P: "Cannot find template file"**  
R: Verifica que la ruta en `.env` sea correcta y accesible.

**P: "Documento generado con formato incorrecto"**  
R: Asegúrate de que la plantilla base contiene todos los estilos (Arial Narrow 11pt).

**P: "UnicodeEncodeError al generar .docx"**  
R: Agrega `# -*- coding: utf-8 -*-` en la primera línea del script Python.

### Reportar Problemas

Abre un [issue en GitHub](https://github.com/davidchaveznge-wq/ResAdmi/issues) con:
- Descripción clara del problema
- Steps para reproducir
- Versión de Python y dependencias
- Logs de error (si aplica)

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📜 Licencia

Este proyecto está bajo licencia **MIT**. Ver [LICENSE](LICENSE) para más detalles.

### Nota Legal

- Código: Libre de usar bajo MIT
- Documentos generados: Responsabilidad del usuario
- INDECOPI: Marca registrada (no afiliado)

---

## 👨‍💻 Autor

**David Chavez** ([@davidchaveznge-wq](https://github.com/davidchaveznge-wq))

---

## 🗺️ Roadmap

- [x] v1.0.0: Core functionality
- [ ] v1.1.0: Refactoring y CI/CD
- [ ] v1.2.0: API REST
- [ ] v2.0.0: Interfaz web

Consulta [CHANGELOG.md](CHANGELOG.md) para el roadmap completo.

---

## ⭐ Agradecimientos

- INDECOPI por estandarización de procesos
- Comunidad Python por excelentes librerías
- Usuarios por feedback y mejoras

---

**Última actualización:** 19 de Julio de 2026  
**Versión:** 1.0.0

## 🚀 Actualización V1000: Modelos Dinámicos

El sistema ahora integra nativamente dos modelos de resoluciones admisorias:
1. **MODELO_1_DDO.docx:** Modelo optimizado para casos con un solo proveedor denunciado.
2. **MODELO_2_DDOS.docx:** Modelo optimizado para casos con dos o más proveedores denunciados (pluralización, división de requerimientos probatorios).

El orquestador de *Google Antigravity* analiza dinámicamente el AST JSON y enruta al modelo adecuado sin intervención humana.
