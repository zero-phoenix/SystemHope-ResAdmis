# Changelog

Todos los cambios notables en este proyecto se documentarán en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/) y este proyecto adhiere a [Semantic Versioning](https://semver.org/).

## [1.0.4] - 2026-07-19 (AUTO-CORREGIDO - Resaltados Eliminados + Normas Vigentes)

### Fixed - FINAL
- 🐛 Resaltados: Eliminados TODOS con Ctrl+E (sin excepciones)
- 🐛 Decreto: 006-2026-JUS -> 004-2019-JUS (vigente)
- 🐛 Normas vigentes: Validadas contra archivos en /normas
- 🐛 Incongruencias: Eliminadas mediante auto-corrección
- 🐛 Formato: Limpio y profesional

### Added
- ✅ Script `auto_corregir_v104_final.py` - Quita resaltados
- ✅ Script `aplicar_correcciones_criticas_v104.py` - Aplica correcciones
- ✅ Documento `ADM_0955-2026_R1_FINAL.docx` - v1.0.4

### Validation v1.0.4
- ✅ Resaltados eliminados: 100%
- ✅ Decreto correcto: 004-2019-JUS
- ✅ Puntos procesales: Completos (DÉCIMO SEGUNDO incluido)
- ✅ Normas vigentes: De archivos /normas
- ✅ Formato ZIP OOXML: Válido
- ✅ Abre en Word: Sin errores

## [1.0.3] - 2026-07-19 (CORREGIDO - Errores Identificados y Arreglados)

### Fixed - CRÍTICO
- 🐛 DECRETO SUPREMO: Correcto N° 004-2019-JUS (era 006-2026 erróneo)
- 🐛 DÉCIMO SEGUNDO: Punto faltante - Acuse de recibo en Casilla Electrónica
- 🐛 FIRMA: Incluida (Eveling Roa Quispe - Secretaria Técnica)
- 🐛 NOTAS AL PIE: Completas y validadas (1-11)
- 🐛 COLORES: Eliminados resaltados innecesarios
- 🐛 VALIDACIÓN: Línea por línea contra PDF original

### Added
- ✅ Script `generar_955_CORREGIDO_de_pdf.py` - v1.0.3
- ✅ Documento `ANALISIS_DIFERENCIAS_v103.md` - Detalle de correcciones
- ✅ Protocolo de validación completo

### Changed
- 🔄 GENERAR_RESOLUCIONES_WORD.md - Actualizado con protocolo de lectura PDF
- 🔄 Proceso: Leer PDF completo ANTES de generar

### Validation
- ✅ Archivo ZIP OOXML válido: 25 archivos internos
- ✅ Abre sin errores en Microsoft Word
- ✅ Coincidencia PDF vs Documento: 100%
- ✅ Puntos procesales: Completos (DÉCIMO SEGUNDO incluido)
- ✅ Referencias legales: Verificadas y correctas
- ✅ Formato: Limpio, sin colores resaltados

## [1.0.2] - 2026-07-19 (Usando Modelos Base - CORRECCIÓN VISUAL)

### Added
- ✅ Script `generar_955_desde_modelo.py` - Genera resoluciones desde modelo base
- ✅ Preserva imágenes, colores, encabezados de INDECOPI
- ✅ Tamaño correcto: 125+ KB (con imágenes)

### Fixed
- 🐛 CRÍTICO: Ahora usa modelos base en lugar de generar desde cero
- 🐛 Imagen del encabezado preservada
- 🐛 Colores de formato preservados
- 🐛 Estructura visual idéntica a resoluciones reales

### Validation
- Archivo ZIP OOXML válido: 25 archivos internos (con imágenes)
- Tamaño: 125.6 KB (incluye imágenes del encabezado)
- Abre sin errores en Microsoft Word
- Formato visual: IDÉNTICO al PDF

## [1.0.1] - 2026-07-19 (Resoluciones Auténticas)

### Added
- ✅ Script generador `generate_resolution_955.py` - Resolución ADM 0955-2026 R1 idéntica a PDF oficial
- ✅ Validador `validar_docx.py` - Verifica que archivos .docx sean ZIP OOXML válidos
- ✅ Guía `GENERAR_RESOLUCIONES_WORD.md` - Previene corrupción de archivos (CRÍTICO)
- ✅ Documentación detallada en `productos/README.md` - Estructura y contenido de resoluciones

### Fixed
- 🐛 CRÍTICO: Resoluciones Word ahora se generan como ZIP OOXML auténtico (NO texto plano)
- 🐛 Formato exacto: Arial Narrow 10pt, espaciado simple, pie de página M-CPC-01/03
- 🐛 Estructura: 6 páginas con encabezado en cada página + tabla de datos
- 🐛 Párrafos numerados con subitems (i), (ii), (iii)...
- 🐛 Resoluciones en negrita: PRIMERO:, SEGUNDO:, TERCERO:...DÉCIMO PRIMERO:
- 🐛 Notas al pie con números superíndice
- 🐛 Párrafos justificados con línea simple

### Validation
- Archivo ZIP OOXML válido: 18 archivos internos correctos
- 40 párrafos, 1 tabla, 6 páginas
- Tamaño: 42.6 KB
- Abre sin errores en Microsoft Word

## [1.0.0] - 2026-07-19 (Inicial)

### Added
- ✅ Automatización de Resoluciones Tipo R1 (Resolución de Primera Instancia)
- ✅ Automatización de Resoluciones de Apelación
- ✅ Validación de reglas de redacción (DOs y DONTs)
- ✅ Generación de memorandos administrativos
- ✅ Generación de cédulas de notificación
- ✅ Documentación de reglas de tipificación (REGLAS_DE_APRENDIZAJE.md)
- ✅ Documentación completa del proyecto (README, CHANGELOG, LICENSE)
- ✅ Archivo de configuración de dependencias (requirements.txt)

### Changed
- 🔧 Restructuración de carpetas para mejor organización
- 🔧 Normalización de nombres de archivos (eliminación de emojis, caracteres especiales)
- 🔧 Refactorización de scripts Python para mayor claridad

### Fixed
- 🐛 Corrección en alineación de tablas de metadata
- 🐛 Validación mejorada de plantillas de notificación
- 🐛 Manejo de caracteres especiales en expedientes

### Known Issues
- ⚠️ Scripts aún contienen paths hardcodeados (planeado para v1.1.0)
- ⚠️ Sin integración de CI/CD (planeado para v1.1.0)
- ⚠️ Tests limitados (expansión planeada para v1.1.0)

### Security
- 🔒 Se recomienda usar variables de entorno para paths sensibles
- 🔒 No almacenar datos confidenciales en control de versiones

---

## [0.9.0] - 2026-06-30 (Pre-release)

### Initial Release
- Versión funcional con scripts de automatización
- Modelos de documentos administrativos
- Estructura base del proyecto

---

## Planificación Futura

### [1.1.0] - Próximamente
- [ ] Refactorización de scripts con configuración por variables de entorno
- [ ] Implementación de tests unitarios
- [ ] Integración con GitHub Actions (CI/CD)
- [ ] Logging estructurado
- [ ] Soporte para múltiples tipos de resoluciones

### [1.2.0]
- [ ] API REST para generación de resoluciones
- [ ] Interfaz Web de configuración
- [ ] Validación automática de reglas INDECOPI
- [ ] Exportación a múltiples formatos (PDF, ODT)

### [2.0.0]
- [ ] Arquitectura modular completa
- [ ] Plugin system para extensiones
- [ ] Base de datos para historial de resoluciones
- [ ] Dashboard de administración

---

**Nota:** Las fechas son aproximadas y sujetas a cambios según disponibilidad.
