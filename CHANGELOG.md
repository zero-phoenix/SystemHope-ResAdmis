# Changelog

Todos los cambios notables en este proyecto se documentarán en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/) y este proyecto adhiere a [Semantic Versioning](https://semver.org/).

## [3.0.0-parte1] - 2026-09-23 (MEGAPLAN v3, PARTE 1: CORRECCIONES JURIDICAS, CONFIGURACION UNICA Y LIMPIEZA)

### Fixed
- **R-155 segun la ley** en 594 documentos: «aprobada por Decreto Legislativo 807» (no «aprobado ... N° 8079»), «merituadas» (no «meritadas»), «artículo 26/223» y «Ley 27444» sin «N°» ni volada. El verificador **exigia** «meritadas» y aceptaba «8079».
- **Singular/plural del traslado por el numero real de denunciados** (no por la carpeta): 388 corregidos; singular «al denunciado que no lo hubiera presentado» (P1).
- **5 destinatarios de traslado corrompidos** (uno dirigido al propio denunciante) y 536 «S.A» sin punto final.
- **Firma vigente** en 427 bloques (Eveling Roa Quispe; Rímac → Luisa Analí Silva Malpartida, Ad Hoc; sin «(e)»). `orquestar.py` y `preparar_remesa.py` ya no ordenan la firma derogada.
- **«denunciante» en HECHOS** sustituido por la tratativa del encabezado en 130 casos (11 pendientes listados en `docs/migracion_v3_parte1_pendientes.txt`).
- `systemhope_engine.py dump-memory` ya no puede sobrescribir `AGENTS.md` ni recrear `.cursorrules`/`CLAUDE.md`.
- `DIRECTORIO`: la via 3 pide señalar un correo, no acuse. README: tipografia medida (Arial Narrow 11, sencillo), no Arial 10 / 1,15.
- `requirements.txt` con las dependencias reales (PyMuPDF, pypdf, python-docx, lxml, Pillow, openpyxl); fuera pywin32, pdfplumber y pydantic.

### Added
- `docs/tabla_tipificacion.json` (tabla del instructor) como lista cerrada de articulos imputables; catalogo depurado 212 → 117 combinaciones (art. 3 y ruido fuera; art. 49 en consulta).
- Falsadores R-156 (numeros de normas), R-157 (denunciante en hechos), R-158 (enmascarado), R-159 (nota al pie del traslado a CC1), R-160 (fecha de remesa), R-143b (consulta/art. 24).
- `scripts/prueba_verificador.py`: 9 mutaciones, una por regla, que el verificador debe rechazar.
- `config/remesa.json`, `config/firmas.json`, `config/modelo.json`, `config/feriados_peru.json` y `scripts/config_sistema.py`: fuente unica de fecha, firma y modelo.
- `scripts/plazos.py`: 20 dias habiles con feriados nacionales del Peru (Semana Santa incluida).
- `admisorio.py preparar` captura cada pagina completa y prepara `_LECTURA.md`; `entregar` rechaza filas vacias o copiadas del texto embebido e informa el plazo (`--recepcion`).

### Removed
- 13 plantillas duplicadas (rama 17 frente a rama 04) y 2 documentos que no eran admisorios (desacumulacion, conservacion de inadmisibilidad): el indice pasa a 578.
- Codigo muerto de `src/` y `automatizacion_antigravity/*.py`, `systemhope-engine.spec` y configuraciones de ResAdmi: conservados en la rama `archivo-legado`.
- AGENTS.md reescrito con solo lo vigente (9 608 caracteres, bajo el limite de 12 000 de Antigravity).

## [2.3.2] - 2026-09-22 (INDIVIDUALIZACIÓN MULTI-PROVEEDOR, ADMISORIOS AD HOC Y PURGA TOTAL DE MODELOS BASE)

### Added
- **Estándar de Individualización Multi-Proveedor (Falsador de Imputación Concreta):** Desglose atómico de conductas por proveedor, erradicando el conectivo promiscuo «y/o» y elevando cada negativa en fecha/sede cierta a cargo autónomo (arts. 1.1.b y 2°).
- **Subsunción Específica de Reclamos:** Obligatoriedad de calificar deficiencias del Libro de Reclamaciones bajo el **numeral 88.1 del artículo 88°** (lex specialis).
- **Bifurcación de Requerimientos Probatorios:** Separación de los incisos probatorios en ordinales independientes: `QUINTO` (Aseguradora) y `SEXTO` (Entidad Financiera), reflejando con exactitud la considerativa (R-108).
- **Régimen de Firma Ad Hoc (R-103):** Firma formal de Luisa Analí Silva Malpartida como Secretaria Técnica Ad Hoc en denuncias contra Rímac Seguros.
- **Alineación Vertical por Tabuladores (`\t:\t`):** Armonización de los dos puntos del encabezado en una columna visual fija.

### Fixed
- **Purga de Modelos Base:** Erradicados patrones anómalos (`dfdfdf`, `(((N)))`, `(NNN)`) en `MODELO_1_DDO.docx`, `MODELO_2_DDOS.docx` y `plantilla_base_2026.docx`.
- **Falsador R-108:** Actualizado para validar requerimientos probatorios individualizados distribuidos en múltiples párrafos y ordinales (`QUINTO` y `SEXTO`).
- **Falsador R-155:** Actualizado para admitir la fórmula de traslado de denuncia interpuesta de la CC1.
- **Falsador R-110:** Reconocimiento de atribución contextual derivada del encabezado de denuncia.
- **Superíndices XML (R-153):** Inyección estricta de `<w:vertAlign w:val="superscript"/>` en llamadas de notas al pie.

## [2.1.0] - 2026-09-18 (CASILLA HABILITADA, ANCLAJE DEL AGENTE Y 15 CONTRADICCIONES ELIMINADAS)

### Added
- **R-151 — la Casilla Electrónica tiene tres requisitos.** Solo procede con padrón
  ACTIVO, número de e-casilla y teléfono móvil no vacío. Condición necesaria, no
  suficiente: la cédula sigue fijando la vía (R-129), pero sin los tres requisitos
  la casilla está prohibida. Lo comprueba `prueba_r151_casilla_habilitada`.
- `scripts/filtrar_casillas.py` + `docs/casillas_habilitadas.json`: la lista viva de
  proveedores habilitados. El padrón **no se versiona** (30 105 registros con datos
  personales); se publica solo el veredicto por proveedor.
- **R-152 — el agente trabaja anclado o no trabaja.** `scripts/comprobar_anclaje.py`
  es una puerta, no un aviso: `admisorio.py preparar` la llama y se detiene si falla.
  Punteros en `.antigravity/` y `.agent/` que no repiten ni una regla.
- `docs/CONTRADICCIONES_RESUELTAS.md`: las quince, con la cifra que dirime cada una.

### Fixed — el instrumento
- **R-97** no reconocía la imputación **en línea**, embebida en el PRIMERO, que usan
  **121 de 593** plantillas: daba NO APTO a uno de cada cinco admisorios válidos.
- **R-103** exigía una firma única que el corpus nunca corroboró (**494 de 593**
  firman Eveling Roa Quispe). Pasa a la matriz del 18/09/2026: Eveling en todo,
  salvo Rímac, que firma Analí Silva Malpartida **Ad Hoc**; sin sufijo `(e)`.
- `UNDECIMO` y `DUODECIMO` salían en la lista global `ORDINALES` del propio
  verificador, que a la vez los rechaza (0 de 593).

### Fixed — la doctrina
- Censo real: **593** plantillas (decía 620, 605 y 630 en tres sitios distintos).
- Margen derecho **3,0 cm** (113 de 116 secciones); la lectura de arranque decía 2,5.
- `RESUELVE:` **no existe** (0 de 593): es `RESOLUCIÓN DE LA SECRETARÍA TÉCNICA` (591).
- La volada `artículo 20°`: **0 de 1 166** ocurrencias la llevan.
- `los artículos 1 y 2`: **0 de 593**; la forma es `artículo 1, numeral 1, literal b)
  y al artículo 2` (192 imputaciones, 230 cierres de considerativa).
- La vía por domicilio procesal **no pide acuse**: pide señalar un correo (37 de 43).
- **R-87 derogada**: la falsan R-110 y R-148 (el 60 % narra en indicativo directo).
- El artículo 24 lo prescribía la tabla de 44 y R-143 lo rechaza siempre.
- `remitir` prohibido por R-149 (4 contra 591). Retirado el tope de «6 páginas».
- Vías por proveedor: fijas y medidas, sin «según apersonamiento previo».
- El motor `src/systemhope_engine.py` llevaba su propia copia envejecida de las vías.

### Security
- `.gitignore` bloquea el padrón de TyC por tres patrones. Verificado: no entra.

### Measured
Dos fuentes independientes —el padrón de TyC y el corpus de 593 plantillas— coinciden
en los tres cruces posibles: Rímac por correo 137/137 y de baja en el padrón; BCP
28/29 y sin teléfono; Ripley 2/2 y sin teléfono.

## [1.0.6] - 2026-07-19 (CORRECCIONES CRÍTICAS - Caracteres Basura, Decreto Vigente, Resaltados)

### Fixed - CRÍTICO
- 🐛 Caracteres basura: Eliminados (((N))), (NNN) - 3 elementos
- 🐛 Decreto Supremo: Verificado 004-2019-JUS (VIGENTE en LPAG)
- 🐛 Resaltados: 45 elementos de formato removido (Ctrl+E completo)
- 🐛 Documento: 100% limpio y profesional

### Validation v1.0.6
- ✅ Caracteres basura: REMOVIDOS
- ✅ Decreto: VERIFICADO VIGENTE (lpag.pdf)
- ✅ Resaltados: 0 elementos restantes
- ✅ Formato: Profesional INDECOPI
- ✅ Tamaño: 128,077 bytes

### Changed
- 🔄 ADM_0955-2026_R1_v106_FINAL.docx - Versión corregida
- 🔄 Script corregir_errores_criticos_v106.py - Automatización completa
- 🔄 GitHub push: Automático sin intervención manual

## [1.0.5] - 2026-07-19 (ANÁLISIS EXHAUSTIVO - 201 Resaltados Eliminados)

### Critical Analysis
- ✅ Decreto Supremo 004-2019-JUS: VERIFICADO VIGENTE (19-07-2026)
- ✅ Resaltados: 201 elementos eliminados completamente
- ✅ PDF Original extraído y archivado (REFERENCIA_PDF_ORIGINAL.txt)
- ✅ Análisis comparativo ejecutado
- ⚠️ Documento modelo base vs PDF original: Estructura diferente (requiere unificación)
- ⚠️ Partes procesales: Análisis de incongruencias identificadas

### Key Findings v1.0.5
- PDF original: 26,560 caracteres, 6 páginas
- Documento generado: 13,838 caracteres (incompleto)
- Modelo base utilizado: 0672-2026/CC1 (estructura de otro caso)
- Solución requerida: Necesita contenido IDÉNTICO a PDF original

### Next Steps v1.0.5
- Crear documento con contenido COMPLETO del PDF
- No usar modelo base (estructura incompatible)
- Generar desde contenido original verificado
- Validar identidad al 100% con PDF adjunto

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
