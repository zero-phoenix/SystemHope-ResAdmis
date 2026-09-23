# Estado (23/09/2026)

- Parte 1 (esfuerzo bajo): HECHA, v3.0.0-parte1.
- Parte 2 (esfuerzo medio): HECHA, v3.0.0-parte2. Incluye las correcciones de la parte 1 pedidas por el instructor.
- Parte 3 (esfuerzo alto): pendiente (F2 anonimizacion y purga, F4 modelos canonicos y HECHOS/imputaciones, F9 A/B con Antigravity, F11 incorporacion de admisorios corregidos).

---

# MEGAPLAN — SystemHope-ResAdmis v3 (revisión 2)

**Objetivo:** que Google Antigravity, con **Gemini 3.8 Flash High o el modelo superior que exista**, redacte desde **cualquier computadora** las resoluciones de admisión a trámite e imputación de cargos de la CC1 (seguros), con la mayor precisión de forma y de fondo. El usuario solo pega el enlace del repositorio y adjunta el expediente.

**Papel de Claude:**
- Mejorar el repositorio.
- Supervisar a fondo a Antigravity.
- Redactar admisorios **solo para pruebas y contraste**.

Estado: **BORRADOR v2 PARA REVISIÓN** · 23/09/2026 · base auditada: `main@8b30c51` (v2.3.2)

---

## 0. Qué ya está verificado

| Punto | Resultado |
|---|---|
| **Control de Antigravity** | ✅ Abrí la app y envié un prompt ajeno al proyecto. Gemini 3.8 Flash High respondió «La capital de Australia es Canberra». |
| **Supervisión** | ✅ Puedo leer sus trazas en `~/.gemini/antigravity/conversations/*.db` (SQLite: pasos, comandos, carpeta de trabajo) y medir llamadas, tiempo, errores y modelo. |
| **GitHub** | ✅ La sesión `gh` es `zero-phoenix`, con permisos `repo` y `workflow`. Tengo lectura y escritura en los 12 repos, públicos y privados. |
| **OCR** | ✅ Ningún script vigente usa OCR. |
| **«Google Lens»** | ⚠️ Antigravity no tiene Google Lens. Lee con la visión nativa de Gemini. |
| **Reglas en Antigravity** | ❌ Cada archivo de reglas tiene un límite de 12 000 caracteres y AGENTS.md ronda los 25 000. `.agent/rules.md` y `.antigravity/` no se cargan: la ruta que se carga es `.agents/rules/`. En el flujo «pegar enlace» no se carga nada. |
| **meta-orquesta** y **clon `Code/repos`** | ⚠️ Tienen trabajo sin commitear o sin subir. **No se tocan** (D8). |

---

## 1. Decisiones del usuario (vinculantes)

| # | Decisión |
|---|---|
| **D1** | **R-155 corregida según la ley:** «aprobada por Decreto Legislativo 807», «merituadas», «artículo 26», «artículo 223», sin volada. El resto queda literal. |
| **D2** | **Fecha de emisión:** una sola fuente por remesa (`config/remesa.json`). Si falta, Antigravity la pregunta. |
| **D3** | **Plazo de 20 días hábiles:** se calcula con feriados de Perú y **no se menciona**. Es obligatoria la **nota al pie de la primera página**: «Denuncia remitida a esta Comisión mediante {MEMORANDUM \| Documento de Traslado} {N°} de fecha {fecha}, recibida el {fecha}.» (234 plantillas). En la denuncia directa no hay esta nota (359 plantillas). |
| **D4** | **Imputación conjunta:** solo si la conducta es común a ambos proveedores (p. ej., el banco contratante y la aseguradora emisora no entregan el contrato del desgravamen). Con exactamente **2** denunciados se escribe «los proveedores denunciados no habrían…» (73 de 92 imputaciones conjuntas en el corpus). Con **3 o más**, se nombran completos los dos implicados (12 de 12). **Se prohíbe inventar imputaciones: solo se usan las que existen en las plantillas.** |
| **D5** | **Datos personales:** primero se **extrae y conserva la clasificación**. Después se anonimiza el árbol y se **purga el historial**. El repo sigue público. |
| **D6** | **Enmascarado:** la póliza **nunca** lleva asteriscos. Crédito, tarjeta, cuenta y préstamo se enmascaran **solo en los dígitos del medio** («34\*\*\*83», «100xxxxxx434»). |
| **D7** | **Portabilidad:** las otras PCs no tienen Python ni Git, así que el repositorio **trae Python y Git portátiles integrados**. |
| **D8** | **No se tocan** meta-orquesta ni el clon local con trabajo sin subir. |
| **D9** | **Firma:** el mandato vigente es Eveling Roa Quispe, Secretaria Técnica, en todo, salvo Rímac: **Luisa Analí Silva Malpartida, Secretaria Técnica Ad Hoc**. Que Eveling firmara casos de Rímac era normal antes; ya no. **Se corrigen las plantillas de Rímac** para evitar el error. |
| **D10** | **Se elimina la plantilla de CONFIDENCIALIDAD** y cualquier otro documento que no sea admisorio. |
| **D11** | **Tipografía según la mayoría del corpus (medido):** Arial Narrow en el 100 % del texto; 11 pt de base (`docDefaults sz=22` en 592 de 593); interlineado sencillo (`line=240`) en el 94 % de los párrafos. AGENTS.md está bien y **el README se corrige**. |
| **D12** | **Denunciantes múltiples:** existe más de un consumidor denunciante, p. ej., herederos que denuncian sin acreditarse como sucesión intestada o cónyuges juntos. Se añaden a la clasificación. |
| **D13** | **Cada admisorio corregido por el usuario se incorpora como plantilla nueva.** No basta con que lo haga Antigravity: debe estar corregido por el usuario. |
| **D14** | **Ejecución en 3 partes**, con esfuerzo bajo, medio y alto. Al terminar cada parte **se actualiza todo el repositorio en GitHub**. Al cerrar cada parte, Claude avisa del cambio de esfuerzo. |

---

## 2. Hallazgos y cómo se corrige cada uno

### Críticos

| # | Hallazgo | Corrección | Fase |
|---|---|---|---|
| H1 | R-155 con «8079», «meritadas» y volada, en **594 plantillas**. El verificador **exige** «meritadas» (`verificar_admisorio.py:774`) y acepta «8079» (`:751`, falta el fin de palabra). | D1 en AGENTS, REGLAS, `aplicar_traslado_r155.py`, las 594 plantillas y los modelos. Nuevos falsadores para 8079, «meritadas», «aprobado» y volada, cada uno con su prueba negativa en CI. | F3 |
| H2 | Los 3 modelos base **mezclan 3 o 4 expedientes**: otro denunciante en PRIMERO, notificaciones a partes ajenas, artículos cruzados entre considerativa y resolutivo, TERCERO sin Santander, subsanación con fecha anterior a la denuncia. | Parte 1: se **retiran** de las referencias activas y se marcan como NO USAR. Parte 3: se reemplazan por modelos canónicos, uno por tipo, construidos cada uno desde un solo caso real limpio. | F3 → F4 |
| H3 | Clasificación de denunciados poco fiable. La carpeta dice «2_o_mas» con un solo denunciado (Rímac, Corredores Falabella). `aplicar_traslado_r155.py` elige singular o plural **por el nombre de carpeta**. | **Clasificación por el contenido**, cruzando encabezado, TERCERO, traslado, requerimientos y notificaciones, y no por la carpeta. Ver §3. | F1 |
| H4 | Datos personales en un repo público, en el árbol y en el historial. Incluye **nombres del 2.º, 3.º y 4.º denunciante sin anonimizar** en plantillas con varios denunciantes. | D5. Anonimización que conserva la clasificación, seguida de purga con `git filter-repo`. | F2 |
| H5 | **El flujo «cualquier PC» no existe.** Además, `requirements.txt` está mal: faltan PyMuPDF, pypdf, Pillow y openpyxl, y sobran pywin32, pdfplumber y pydantic. | Parte 1: `requirements.txt` real, con versiones fijadas. Parte 2: el diseño completo de §4. | F7 → F8 |

### Altos

| # | Hallazgo | Corrección | Fase |
|---|---|---|---|
| H6 | `orquestar.py:310` y `preparar_remesa.py:406` escriben «Silva Malpartida (e)» en `_ORDEN_DE_TRABAJO.md`, y ese archivo manda sobre AGENTS.md. | Una sola fuente de firma, `config/firmas.json`, con la regla D9. Los generadores la leen. | F7 |
| H7 | La fecha fija «14 de setiembre de 2026» aparece en 4 archivos. | D2. | F5 |
| H8 | No hay cálculo de plazo ni control de la nota al pie 1. | D3. | F5 |
| H9 | `entregar` exige `_LECTURA.md`, que AGENTS.md no menciona. `preparar` no renderiza páginas, así que el control queda vacío. | Ver §5.2: `preparar` renderiza y pre-crea `_LECTURA.md` con una línea por página real. `entregar` rechaza páginas faltantes, vacías o copiadas del texto embebido. Se documenta en NUCLEO. | F7 |
| H10 | `orquestar.py` lanza Antigravity con el modelo `pro`. | `config/modelo.json` («gemini-3.8-flash-high» o superior) como única fuente. | F7 |

### Medios y bajos

| # | Hallazgo | Corrección | Fase |
|---|---|---|---|
| H11 | El README dice Arial 10 e interlineado 1,15. | D11. README y MATRIZ se corrigen. El verificador ya exige Arial Narrow 11 e interlineado 1,0. | F7 |
| H12 | DIRECTORIO pide acuse de recibo en la vía 3, que ya fue derogado. | Se alinea con AGENTS §2, vía 3: «señale un correo electrónico autorizando…» (37 de 43). | F7 |
| H13 | Numeración de ordinales inconsistente entre documentos. | Parte 1: una sola tabla de ordinales en NUCLEO, con variantes por tipo marcadas «a medir». Parte 3: la tabla definitiva, medida del corpus para 1 y para 2 o más denunciados. | F7 → F4 |
| H14 | El catálogo de imputaciones incluye el art. 3 (prohibido) y basura (`art.29571`, `art.150\|art.29571`). | Se depura: solo quedan las combinaciones con respaldo en el corpus y sin artículos prohibidos. El verificador rechaza cualquier combinación fuera del catálogo. | F3 |
| H15 | REGLAS conserva la R-127 derogada y dice «Ley N° 1033». | R-127 se marca DEROGADA por R-103. Se corrige a «Decreto Legislativo 1033». | F7 |
| H16 | `systemhope_engine.py dump-memory` sobrescribe AGENTS.md y recrea `.cursorrules` y `CLAUDE.md`. Además clasifica a Interbank por Casilla y pide acuse en la vía 3. | `dump-memory` escribirá solo en `dist/`, nunca en la raíz. Interbank va a Correo (7 de 7). Vía 3 = señalar correo. Número de plantillas calculado, no escrito a mano. | F7 |
| H17 | Código muerto: casi todo `src/`, los `.py` de `automatizacion_antigravity/`, `temp_*`, `systemhope-engine.spec` y el `requirements.txt` interno. | Según tu respuesta a P3: se mueve a la rama `archivo-legado` y se elimina de `main`. Se mantiene `src/systemhope_engine.py`, que usan CI y los releases. | F7 |
| H18 | 14 plantillas `.DOCX` en mayúsculas que no ve CI en Linux; 13 pares duplicados. | Todas a `.docx`. En cada duplicado se conserva la versión con mejor puntuación del verificador y el índice se actualiza. | F7 |
| H19 | 1 042 PNG (81 MB) y un historial de 402 MB. | El paquete portátil sale sin capturas ni historial (F8). La purga reduce el historial (F2). Las capturas pasan a un release aparte si hacen falta. | F8, F2 |
| H20 | AGENTS.md mezcla reglas con historial, lo que gasta tokens y genera contradicciones. | AGENTS.md pasa a ser un índice corto. `.agents/rules/NUCLEO.md` (< 12 000 caracteres) contiene solo reglas vigentes. El historial va a CHANGELOG y REGLAS. | F7 (inicio) → F8 (skills) |

---

## 3. Clasificación corregida (F1): denunciantes, denunciados y roles

La clasificación se hace **por el contenido del documento**, nunca por la carpeta. Cada campo se extrae de al menos dos lugares del documento y, si no coinciden, se registra la discrepancia.

**Denunciantes (sujeto activo):**

| Clase | Encabezado | En HECHOS y considerativa | En el resolutivo |
|---|---|---|---|
| varón | `DENUNCIANTE: … (SEÑOR X)` | «el señor X» | nombre completo |
| mujer | `(SEÑORA X)` | «la señora X» | nombre completo |
| sucesión intestada acreditada | `(SUCESIÓN)` | «la Sucesión…» | «Sucesión Intestada de…» |
| **varios herederos no acreditados como sucesión** | varias líneas | «los señores X e Y» / «la señora X y el señor Y» | nombres completos |
| **cónyuges** | dos líneas | «los señores X» / «los cónyuges» | ambos nombres |
| persona jurídica | razón social (ALIAS) | alias | razón social |
| asociación de consumidores | nombre (ALIAS) | alias | nombre completo |
| varios mixtos (persona natural y empresa) | varias líneas | cada uno con su alias | cada uno |

Medido: 575 plantillas con un solo denunciante, al menos 14 con 2 a 4, 4 con persona jurídica y 6 con asociación. Las formas exactas de cada celda se miden en F1 **y no se suponen**. Cuando hay varios denunciantes cambia la concordancia: «denunciaron», «solicitaron», «sus» y la notificación de cada uno por su vía.

**Denunciados:**
- Número real y, para cada uno: tipo (aseguradora, banco, financiera, corredor, AFOCAT, CAFAE, taller u otro), alias, vía de notificación y ordinal de su requerimiento.
- Imputaciones que se le atribuyen: propias o conjuntas, y en qué forma (D4).

**Documento:**
- Si es un admisorio (D10) y su número de resolución.
- Firma y refrendo; tipo de nota al pie 1 (D3); producto y enmascarado (D6); mapa de ordinales.
- Estructura de HECHOS (ver §6) y duplicados.

**Salida:** `docs/indice_plantillas_v3.json`, sin ningún dato personal, que sustituye al índice actual. La elección de plantilla por parte de Antigravity pasa a filtrar por **tipo de denunciante, número real de denunciados, tipo de cada denunciado, rama y conducta**.

---

## 4. Flujo «cualquier PC» (F8)

```
Usuario: conversación nueva en Antigravity (Gemini 3.8 Flash High o superior)
  Prompt único: «Sigue https://github.com/zero-phoenix/SystemHope-ResAdmis/blob/main/ARRANQUE.md»
  + PDF del expediente adjuntos
          │
          ▼
ARRANQUE.md (< 12 000 caracteres; lo primero y lo único que debe leer)
  1. PowerShell nativo de Windows, sin administrador:
     Invoke-WebRequest del paquete de GitHub Releases → Expand-Archive
     → %USERPROFILE%\SystemHope\ { python\ (Python 3.11 embebido + dependencias),
                                   git\ (MinGit), repo\ (sin capturas) }
     Si el paquete ya existe: compara la versión y actualiza solo si hay una nueva.
     Si la red lo bloquea: da al usuario el enlace del ZIP para descargarlo a mano
     y se detiene hasta que esté.
  2. SystemHope\python\python.exe repo\scripts\comprobar_entorno.py
     (versión, dependencias, sin librerías de OCR, remesa.json con fecha, modelo declarado)
  3. Crea SystemHope\casos\<EXPEDIENTE>\ y copia allí los adjuntos
     (si no encuentra su ruta en disco, pide al usuario la carpeta)
  4. Lee repo\.agents\rules\NUCLEO.md y la skill que corresponde
     (1 denunciado / 2 o más; tipo de denunciante)
  5. preparar → lectura visual Gemini (§5) → construir → entregar = APTO
          │
          ▼
ADM <EXP> R<N>.docx + informe (APTO, vencimiento de los 20 días, N llamadas, T reloj)
```

- **Paquete portátil** que genera CI en cada release:
  - Python embebible oficial de Windows x64 con python-docx, lxml, PyMuPDF, pypdf, Pillow y openpyxl.
  - MinGit.
  - El repo sin historial ni capturas.
  - Tamaño estimado: unos 120 MB. No se versionan binarios dentro de git.
- **`.agents/`** (la estructura que lee Antigravity):
  - `rules/NUCLEO.md`
  - `skills/` con una skill por tema: `admisorio-1-denunciado`, `admisorio-2-o-mas-denunciados`, `denunciantes`, `hechos`, `imputaciones`, `notificacion-y-casillas`, `nota-al-pie-traslado`, `lectura-expediente`
  - `workflows/admisorio.md`, que se invoca con `/admisorio`
  - Se eliminan `.agent/` y `.antigravity/`.
- **Modelo:** `config/modelo.json` es la única fuente. ARRANQUE lo declara y el supervisor lo verifica en la traza. Si sale un modelo superior, se cambia solo ese archivo.

---

## 5. Lectura sin OCR y formato

### 5.1 Lectura del expediente
- R-137 pasa a llamarse **«lectura visual Gemini»**: los PDF adjuntos se leen de forma nativa y los PNG que genera `preparar` también. El texto embebido solo sirve de contraste.
- Guardas contra OCR:
  - `autocomprobacion` prohíbe pytesseract, easyocr, paddleocr, ocrmypdf, rapidocr y `get_textpage_ocr`.
  - El paquete portátil no los incluye.
  - `comprobar_entorno` lo verifica en cada PC.

### 5.2 Corrección de `_LECTURA.md` (H9)
1. `admisorio.py preparar` llama a `renderizar_paginas()` para **todas** las páginas, a 170 dpi, en `_paginas/`.
2. Pre-crea `_LECTURA.md` con una fila por página real: archivo, página, tipo de documento y una línea vacía para «lo que vi».
3. Se documenta en NUCLEO y en el workflow.
4. `entregar` rechaza en cualquiera de estos casos:
   - faltan filas;
   - alguna fila está vacía;
   - una fila es idéntica al texto embebido, lo que indica que se copió en vez de leerse;
   - el número de páginas no coincide con el real.
5. Para ahorrar llamadas en expedientes largos, el agente puede leer el PDF adjunto de forma nativa (todas sus páginas en contexto), siempre llenando `_LECTURA.md`.

### 5.3 Medición de formato (F6)
El script `scripts/medir_formato.py` produce una «huella de formato»: tipo, tamaño, negrita, interlineado, espaciado, sangrías, alineación, márgenes, encabezado, pie, posición y notas.
- **DOCX:** lectura del XML (OOXML), que es exacta.
- **PDF digitales:** PyMuPDF `get_text("dict")` da fuente, tamaño, negrita y cursiva y coordenadas en puntos, de donde se derivan márgenes, sangrías, alineación e interlineado. No es OCR: lee los objetos de texto.
- **Escaneados:** visión de Gemini.

**Conclusión de la investigación:** para el formato, lo mejor no es una herramienta de imagen sino leer la estructura del archivo, que es exacta, local y privada. Azure Document Intelligence (*styleFont*), Google Document AI y Docling detectan estilos, pero **son OCR** y enviarían los expedientes a terceros. WhatTheFont y Adobe solo identifican el tipo de letra.

---

## 6. HECHOS e imputaciones: análisis y simulaciones popperianas (F4)

### 6.1 Lo que ya está medido (585 plantillas con HECHOS)
- **583 de 585** abren con «Mediante el escrito/la denuncia del …[^1], subsanada mediante…, el señor X denunció a Y por presuntas infracciones a la Ley 29571, Código… (en adelante, Código)[^2], señalando lo siguiente:».
- **573 de 585** cierran con el párrafo «El señor X solicitó, en calidad de medida correctiva, que Y cumpla con: (i)…; y (ii)…. Asimismo, requirió el reembolso de costos y costas…».
- Hay 5 058 viñetas de hechos. **2 598 (51 %) empiezan con la fecha** («El 16 de agosto de 2024, …»).
- **111 viñetas usan «habría»** y **84 usan «denunciante»**, contra la regla del pasado indicativo y de no nombrar al «denunciante» en la narración. Hay que averiguar si son citas, excepciones o errores del corpus, y decidir la regla con la cifra.

### 6.2 Qué se medirá antes de escribir la regla
Sobre el corpus completo y con cifras:
- **Qué se pone** en HECHOS:
  - contratación, producto y póliza;
  - siniestro o evento;
  - comunicaciones, reclamos, respuestas y cartas;
  - montos en formato monolítico.
- En qué orden va (cronológico estricto o agrupado por tema) y con qué verbos (catálogo de verbos en pretérito).
- **Qué no se pone:**
  - calificaciones jurídicas y artículos;
  - adjetivos valorativos;
  - pruebas;
  - pretensiones fuera del párrafo final.
- Cómo se nombra al proveedor (siempre por su alias del encabezado) y al consumidor según su clase (§3).
- **Imputaciones.** Estructura: «Presunta infracción a {artículo del catálogo} de la Ley 29571, Código…, en tanto {sujeto según D4} habría(n) {conducta en condicional} {objeto: producto o póliza} {circunstancia: fecha o siniestro}».
  - Qué no entra: pruebas, montos de la pretensión, adjetivos y hechos no denunciados.
  - La correspondencia conducta ↔ artículo se toma solo del catálogo depurado (D4).
- **Isomorfismo considerativa ↔ resolutivo:** mismo orden, mismos artículos, mismo núcleo fáctico.

### 6.3 Simulaciones con autocorrección popperiana
Cada regla es una conjetura con su cifra; cada contraejemplo la refuta o la convierte en excepción documentada.
1. **Dejar uno fuera (sobre 593 plantillas).** A partir de los HECHOS de una plantilla, las reglas deben predecir sus imputaciones: conducta, artículo, sujeto y forma conjunta.
   - Se mide precisión y exhaustividad por regla.
   - Cada fallo se clasifica como regla falsa, excepción real o plantilla defectuosa, y se corrige la regla o se anota.
   - Se repite hasta que no haya más cambios.
2. **Mutaciones del verificador.** Por cada regla se generan documentos que la violan: singular en lugar de plural, mezcla de proveedores, «el proveedor denunciado» con 2 o más denunciados, orden cruzado, hecho en condicional, póliza enmascarada, firma de Rímac, «8079», etc. Si una mutación sale APTO, el verificador está refutado y se corrige.
3. **Redacción de contraste (Claude) sobre expedientes reales** de 1 y de 2 o más denunciados, con cada clase de denunciante. Cada salida pasa por el verificador y por tu revisión. Cada error hallado crea una regla o un falsador nuevos.
4. **A/B con Antigravity (F9)** sobre los mismos expedientes.

---

## 7. Incorporación de admisorios corregidos por el usuario (D13) — F11

1. **Solo entra lo corregido por el usuario.** Tú marcas tu versión final de una de dos formas: guardándola en `SystemHope\corregidos\` o con el sufijo «CORREGIDO» (ver P9). Lo que produce Antigravity sin tu corrección **nunca** entra.
2. `python scripts/incorporar_corregido.py <archivo>` hace lo siguiente:
   1. Verificador APTO; si no, rechaza y explica por qué.
   2. Clasificación §3.
   3. **Diff contra el borrador de Antigravity**, si existe. Cada corrección tuya se registra en `docs/correcciones_instructor.jsonl` (qué cambió y en qué sección) como aprendizaje medido para nuevas reglas.
   4. Anonimización que conserva la clasificación y el enmascarado de D6.
   5. Duplicados: si ya existe, se versiona.
   6. Se ubica en la taxonomía y se actualizan el índice v3, el catálogo de imputaciones (solo se amplía por esta vía, porque viene de ti) y las estadísticas.
   7. Guardia de datos personales.
3. **Subida:**
   - Desde esta PC, Claude o `gh` hacen commit y PR automáticos.
   - Desde otra PC, Antigravity deja un paquete **ya anonimizado**; tú lo subes por la web de GitHub a `ingesta/` y un workflow de CI lo valida (guardia, verificador) y lo integra.
   - **Nunca se sube un documento sin anonimizar**, ni siquiera de forma temporal.

---

## 8. Plan de ejecución en 3 partes (D14)

Cada parte se hace en una rama, `parte-N`. Al cerrar la parte:
1. CI en verde.
2. Merge a `main`, con **todo el repositorio actualizado en GitHub**.
3. Tag `v3.0.0-parteN` y release.
4. Informe de lo hecho y de lo que quedó fuera, con su causa.

Luego **te aviso para que cambies el esfuerzo**.

> **Única excepción:** el force-push de la purga (F2) es irreversible y te pediré confirmación explícita en ese momento.

### PARTE 1 — esfuerzo BAJO: F0, F3, F5, F7, F10
- **F0 Salvaguardas:** `git clone --mirror` y bundle verificado fuera del repo; trabajo en un clon limpio nuevo.
- **F3 Correcciones jurídicas y de plantillas:**
  - H1 (R-155, D1) en todo el corpus.
  - Falsadores con prueba negativa.
  - H14 (catálogo depurado).
  - D6 (enmascarado): regla y falsador; revisión de las 56 pólizas enmascaradas.
  - **D9:** firma de Rímac corregida en las plantillas y en el modelo.
  - **D10:** se elimina la plantilla de confidencialidad y cualquier otro documento que no sea admisorio, detectado por la línea de MATERIAS.
  - H2: modelos Frankenstein marcados NO USAR.
- **F5 Fecha, plazo y nota al pie 1:** D2, D3, `config/feriados_peru.json`, `scripts/plazos.py` con pruebas unitarias y falsador de la nota 1.
- **F7 Coherencia y limpieza:**
  - H6, H9, H10, H11, H12, H13 (tabla provisional), H15, H16, H17, H18, H20 (NUCLEO < 12 000 caracteres).
  - `requirements.txt` real.
  - `config/firmas.json` y `config/modelo.json`.
- **F10:** release `v3.0.0-parte1`.
- **Cierre:** «Parte 1 terminada. Cambia el esfuerzo a MEDIO y dime que continúe».

### PARTE 2 — esfuerzo MEDIO: F1, F6, F8
- **F1:** clasificación §3 (denunciantes múltiples, denunciados reales, roles) e índice v3. La elección de plantilla pasa a hacerse por contenido. Muestra de 20 plantillas para tu revisión.
- **F6:** §5.3, `medir_formato.py` y la huella de formato en el verificador.
- **F8:**
  - §4 completo: ARRANQUE, paquete portátil, `comprobar_entorno`, `.agents/`, workflow `/admisorio`.
  - Prueba en una PC virgen: carpeta nueva, sin Python en el PATH, conversación nueva de Antigravity solo con el enlace.
- **Cierre:** release `v3.0.0-parte2` y «cambia el esfuerzo a ALTO».

### PARTE 3 — esfuerzo ALTO: F2, F4, F9 (+ F11 y F10 final)
- **F2:** anonimización del árbol (incluidos los nombres de los denunciantes adicionales) conservando la clasificación, seguida de la purga del historial:
  - Se eliminan las rutas del padrón, `Proyecto admisorios/`, `Modelos al 30-06-26/`, `ADMI + CONFI/`, `build/`.
  - Se reemplazan los nombres detectados.
  - **Pido tu confirmación y hago el force-push.**
  - Se pide a GitHub que purgue su caché y se revisan los forks.
  - **Criterio:** 0 coincidencias de DNI, correos, celulares y nombres del padrón en todo el historial.
- **F4:**
  - §6 completo.
  - Anatomía medida de 1 y de 2 o más denunciados, y tabla definitiva de ordinales.
  - **Modelos canónicos** `MODELO_1_DENUNCIADO.docx` y `MODELO_2_O_MAS_DENUNCIADOS.docx` (y variantes por clase de denunciante si el corpus lo exige), cada uno desde un solo caso real aprobado por ti.
  - Skills de HECHOS e imputaciones.
  - Simulaciones popperianas hasta que no haya más cambios.
- **F9:**
  - A/B de Claude frente a Antigravity sobre tus expedientes reales (1 y 2 o más, distintas clases de denunciante), que nunca se suben.
  - Se mide N, T, pasos saltados y modelo.
  - Bucle de corrección de reglas, skills y verificador.
  - **Salida:** 100 % APTO, 0 errores de fondo en tu revisión y N ≤ 15 en expedientes cortos.
- **F11:** incorporación de admisorios corregidos (§7), probada con al menos uno tuyo.
- **F10 final:** release `v3.0.0`, README corto y guía de uso de una página.

### Por qué el esfuerzo por parte
- **Bajo:** reemplazos ya decididos, con criterios que verifica un script.
- **Medio:** heurísticas sobre 593 documentos heterogéneos y un empaquetado con fallos de entorno difíciles de prever.
- **Alto:** una acción irreversible (la purga), el núcleo de fondo jurídico (1 frente a 2 o más denunciados, HECHOS, imputaciones) y el diagnóstico de causas raíz en Antigravity.

---

## 9. Riesgos

| Riesgo | Mitigación |
|---|---|
| La purga rompe los clones existentes | Respaldo F0. Tus clones no se tocan. Te dejo instrucciones para re-clonar o rebasar. |
| **Los datos personales siguen expuestos hasta la parte 3** (el orden lo decidiste tú) | Si prefieres, en la parte 1 se puede **quitar solo del árbol** lo más grave: `casos/*.json` con correos, `temp_2222.txt` con DNI y `catalogo_modelos_phoenyx.json`, que no se necesitan para clasificar. La purga del historial sigue en la parte 3 (P8). |
| La PC del trabajo bloquea las descargas | Descarga manual del ZIP. ARRANQUE lo detecta y lo pide. |
| Antigravity no expone en disco la ruta de los adjuntos | Se prueba en F8. Alternativa: pedir la carpeta al usuario. |
| Cambio de modelo | `config/modelo.json` y el A/B de F9. |
| Días no laborables no previstos | Archivo de feriados editable y aviso si el año no está cargado. |

---

## 10. Preguntas abiertas

- **P1 — Traslado con 1 denunciado.** La fórmula del instructor dice «…presente sus descargos… declarará en rebeldía **a los denunciados que no lo hubieran presentado**». ¿Queda así (literal) o pasa a «**al denunciado que no lo hubiera presentado**»?
- **P2 — Días hábiles.** ¿Solo feriados nacionales, o también los días no laborables del sector público que decreta el Gobierno? ¿Hay un calendario interno de Indecopi?
- **P3 — Código muerto.** ¿Lo elimino de `main`? Quedaría en la rama `archivo-legado`.
- **P5 — Expedientes para las pruebas.** ¿En qué carpeta están? ¿Cuántos son de 1 denunciado y cuántos de 2 o más? ¿Hay alguno de cónyuges, herederos o persona jurídica denunciante?
- **P6 — Modelos canónicos.** ¿Te propongo en la parte 3 los casos reales que servirán de base para que los apruebes?
- **P7 — Carpeta estándar en otras PCs.** ¿`%USERPROFILE%\SystemHope\` o prefieres otra?
- **P8 — Datos más graves en la parte 1.** ¿Quito ya del árbol, en la parte 1, los archivos con correos y DNI que no hacen falta para clasificar, o espero a la parte 3 como está previsto?
- **P9 — Cómo marcas un admisorio corregido.** ¿Carpeta `corregidos\`, sufijo «CORREGIDO» en el nombre u otra forma?

---

## 11. Qué NO haré sin tu aprobación expresa
- Ejecutar cualquier parte del plan antes de que digas «ejecuta».
- Hacer force-push o purgar el historial sin tu confirmación en ese momento.
- Cambiar la visibilidad del repo o borrar archivos de tu disco.
- Modificar `~/.gemini/GEMINI.md` o la configuración global de Antigravity.
- Tocar meta-orquesta o el clon `Code/repos/SystemHope-ResAdmis`.
- Sacar expedientes reales de tu disco.
