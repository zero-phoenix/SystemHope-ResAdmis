# DIRECTRICES MAESTRAS DEL SISTEMA (AGENTS.md)
# SISTEMA DE EMISION DE RESOLUCIONES ADMISORIAS INDECOPI CC1

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ANCLAJE OBLIGATORIO — LÉELO ANTES DE CUALQUIER OTRA COSA                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Este archivo solo gobierna si lo has cargado DESDE LA RAÍZ DE ESTE          ║
║  REPOSITORIO. Antigravity arrancaba en `_ConfigIA/.resadmi`, una carpeta     ║
║  con una sola subcarpeta, y desde ahí no existen ni AGENTS.md, ni scripts/,  ║
║  ni plantillas_maestras/. Esa raíz equivocada es la causa raíz MEDIDA de     ║
║  casi todos los fallos del agente (R-142).                                   ║
║                                                                              ║
║      Antigravity  →  Add Workspace  →  la raíz de SystemHope-ResAdmis        ║
║                                                                              ║
║  PRIMER COMANDO DE TODA SESIÓN, SIN EXCEPCIÓN:                               ║
║      python scripts/comprobar_anclaje.py                                     ║
║                                                                              ║
║  Si devuelve error, PARA. No redactes. No busques los scripts con -Recurse.  ║
║  No abras otro proyecto. Arregla el workspace y vuelve.                      ║
║                                                                              ║
║  `admisorio.py preparar` llama a esa comprobación y se detiene si falla:     ║
║  no es un aviso que puedas olvidar, es una puerta cerrada.                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
```


> **AUTORIDAD:** Indecopi Comisión de Protección al Consumidor  1 (CC1)  
> **NORMA MARCO:** Decreto Supremo 006-2026-JUS  
> **PROTOCOLO DE LECTURA (R-137):** cero OCR, **Google Lens en todas las páginas**, tengan o no capa de texto. `scripts/extraer_expediente.py` va primero, pero no para ahorrar lectura: da el número real de páginas (R-136), el dossier anclado y el texto embebido, que sirve de **contraste**. Si el volcado y lo que Lens ve discrepan, **manda Lens**.  
> **NOMBRE DEL ENTREGABLE (mandato del instructor, 14/09/2026):** `ADM <EXPEDIENTE> R<N>.docx`, donde `<N>` es el número de resolución **que fija la cédula** del expediente. Ejemplo: `ADM 3122-2026 R1.docx`.  
> **PROTOCOLO DE ENTREGA:** `scripts/verificar_admisorio.py` debe decir `APTO`. Sin esa salida, el admisorio no está entregado.  
> **REPOSITORIO:** https://github.com/zero-phoenix/SystemHope-ResAdmis
> **COMO NO SE REDACTA:** `docs/COMO_NO_SE_REDACTA.md` — las prohibiciones por apartado, cada una con la frecuencia medida que la sostiene. Una prohibición sin cifra detrás es una opinión.
> **ANATOMIA DEL DOCUMENTO:** `docs/ANATOMIA_DEL_ADMISORIO.md` — el esqueleto de diez ordinales, qué comparten los 603 admisorios del corpus y **por qué difieren** los que difieren.
> **SI EL AGENTE NO OBEDECE:** mira de donde arranca antes de escribir otra corrección (R-142). `python scripts/orquestar.py sanear` y `docs/PLAN_WORKSPACE_ANTIGRAVITY.md`.
> **SI SUPERVISAS A UN AGENTE:** `docs/SUPERVISION_DE_AGENTES.md` — superficie de control (`scripts/orquestar.py`), qué medir, cuándo intervenir, y el catálogo de fallos medidos del agente **y del supervisor**.

---

## LECTURA DE ARRANQUE: SOLO ESTE ARCHIVO

Para redactar un admisorio **basta con este archivo**. `REGLAS_DE_APRENDIZAJE.md` (79 KB) y
`MATRIZ_MAESTRA_PHOENYX_POPPERIANA.md` (45 KB) son corpus de **consulta dirigida**: se abren
para buscar una regla concreta, no se leen enteros antes de empezar.

**Los cuatro pasos, en orden. Dos de ellos son una sola llamada cada uno (R-134):**

1. `python scripts/admisorio.py preparar <carpeta> [--contiene "frase"] [--rama X]`
   — paro si el caso esta cerrado, aviso si hay Word huerfano, triaje con dossier
   anclado, inventario de paginas y candidatas de plantilla. **Todo en una llamada.**
2. **Google Lens en todas las paginas del expediente** (R-137), con o sin capa de
   texto. Cero OCR. El volcado de texto es contraste, no reemplazo.
3. Redaccion. El documento se construye **siempre** con
   `python scripts/construir_admisorio.py --mapa <mapa.json>` (R-139): sin Word, sin
   `win32com` y sin scratch, y con auditoria de residuos del caso de origen — se niega
   a dar por bueno un documento en el que sobreviva un dato de la plantilla. Si hay
   control: `python scripts/inspeccionar_docx.py <generado> --diff <control>`.
4. `python scripts/admisorio.py entregar <generado> [--caso <n>]` — verificador,
   guardia de datos personales, control de PDF y de Word vivo, y scorecard.
   **Todo en una llamada.** Se entrega pegando la salida literal `APTO` /
   `ENTREGABLE`. Sin eso, el admisorio no esta entregado.

Los scripts sueltos (`extraer_expediente.py`, `verificar_admisorio.py`,
`guardia_admisorio.py`) siguen existiendo, pero llamarlos por separado gasta llamadas de
mas: **cada llamada a herramienta cuesta ~17,6 s de reloj, haga o no trabajo** (medido, ver
§10 de `docs/PLAN_VELOCIDAD_SIN_COLGARSE.md`).

**Si la carpeta del expediente trae un `_ORDEN_DE_TRABAJO.md`, ese archivo manda sobre este
para ese caso concreto:** significa que el triaje, la eleccion de plantilla y el anclaje de
datos ya estan hechos y no hay que rehacerlos.

---

## 1. REGLAS NO NEGOCIABLES (AXIOMAS POPPERIANOS)
1. **PROHIBICIÓN ESTRICTA DE OCR (R-137):** Jamás transcribir denuncias con OCR clásico ni extractores que rompan coordenadas o inventen datos. **Toda** página de **todo** PDF del expediente se analiza con Google Lens / visión directa, esté escaneada o no, tenga capa de texto o no. No existe la excepción del «PDF nativo».
2. **SOLO SE IMPUTA COMO IMPUTAN LOS MODELOS (R-143):** prohibido inventar combinaciones de artículos o mezclar imputaciones distintas en una sola. El corpus admite **64 combinaciones**, catalogadas en `docs/catalogo_imputaciones.json`. Si la que hace falta no está, se eleva al instructor.
2. **TUO LPAG ACTUALIZADO:** Siempre citar el **Decreto Supremo 006-2026-JUS**. Prohibida cualquier mención al D.S. 004-2019-JUS.
3. **PROHIBICIÓN DE 'INDUCCIÓN A ERROR':** Nunca imputar por el artículo 3 ni emplear la frase 'inducción a error'. Todas las fallas de información se canalizan por el **artículo 1, numeral 1, literal b) y al artículo 2** del Código, que es la forma literal del corpus (192 imputaciones y 230 cierres de considerativa; «los artículos 1 y 2» aparece **0 veces en 593**). Prohibida la volada ordinal pegada a un número.
4. **TIEMPOS VERBALES OBLIGATORIOS:**
   - **En Antecedentes / Hechos:** Pasado indicativo afirmativo ("señaló", "contrató", "solicitó"). PROHIBIDO usar la palabra 'denunciante' en el cuerpo narrativo; usar el nombre de pila o 'el señor / la señora [Apellido]'.
   - **En Imputación de Cargos:** Condicional obligatorio ("habría denegado", "habría omitido", "habría realizado cobros").
5. **INVARIANTES LÉXICAS:**
   - Usar `cónyuge` / `cónyuges` (PROHIBIDO: esposo/a).
   - Usar `luego de` (PROHIBIDO: tras).
   - Usar `esta` / `este` sin tilde diacrítica.
   - Usar `médico` (PROHIBIDO: doctor/a o Dr.).
   - Usar `vehículo con Placa de Rodaje []` (PROHIBIDO: carro, auto).
6. **FORMATO MONETARIO MONOLÍTICO:**
   - `S/ X XXX,XX` o `US$ X XXX,XX` (espacio para miles, coma decimal, nunca punto ni apóstrofe).

---

## 2. LOS TRES PÁRRAFOS RESOLUTIVOS LITERALES DE NOTIFICACIÓN (SIN PARAFRASEAR)
En la sección resolutiva final de todo admisorio, se coloca indefectiblemente el párrafo correspondiente a la vía legal de notificación:

### TIPO 1: VÍA CASILLA ELECTRÓNICA (SINE INDECOPI - 5 DÍAS)
*Para compañías de seguros y bancos afiliados obligatoriamente:*
> *"requerir a [PROVEEDOR(ES)] para que efectúe[n] el acuse de recibo mediante la confirmación de recepción de la notificación remitida por este despacho a su[s] Casilla[s] Electrónica[s], dentro de los cinco (5) primeros días hábiles siguientes a la fecha en que recibe[n] la notificación."*

### TIPO 2: VÍA CORREO ELECTRÓNICO (AUTORIZACIÓN EXPRESA - 2 DÍAS)
*Para consumidores y proveedores con dirección electrónica autorizada:*
> *"requerir a [PARTE(S)] para que, dentro del plazo de dos (2) días hábiles siguientes a la fecha en que reciba[n] la notificación en su[s] bandeja[s] de correo electrónico, efectúe[n] la confirmación de recepción de la notificación remitida por este despacho a su[s] correo[s] electrónico[s], de conformidad con el segundo párrafo del numeral 4 del artículo 20 del Texto Único Ordenado de la Ley del Procedimiento Administrativo General, aprobado mediante Decreto Supremo 006-2026-JUS, bajo apercibimiento de rehacer el acto de notificación y notificarle[s] conforme al numeral 1 del artículo 20 del citado cuerpo normativo."*

### TIPO 3: VÍA DOMICILIO PROCESAL / CÉDULA FÍSICA (2 DÍAS)
*Para denunciantes sin correo, AFOCATs, fondos especiales (CAFAE) o proveedores sin casilla:*
> *"requerir a [PARTE(S)] para que, dentro del plazo de dos (2) días hábiles siguientes a la fecha en que reciba[n] la notificación en su domicilio procesal, señale[n] un correo electrónico autorizando recibir las notificaciones correspondientes por dicho medio."*

> **Corrección medida (18/09/2026):** la versión anterior de este párrafo pedía un
> **acuse de recibo** en el domicilio procesal. El corpus lo desmiente: de los 43
> párrafos por domicilio procesal, **37 (86 %)** piden *señalar un correo
> electrónico* y solo 6 piden acuse, tres de ellos malformados. Los modelos
> `MODELO_1_DDO.docx` y `MODELO_2_DDOS.docx` confirman la forma correcta.
> **La vía 3 no pide acuse: pide que se designe un correo.**

### 2.1 FÓRMULA OBLIGATORIA DE TRASLADO DE RESOLUCIÓN Y DESCARGOS (R-155)
> **Mandato del instructor (21/09/2026):** Quedan derogadas de forma absoluta e irrevocable las fórmulas históricas previas (A: contados desde la notificación; y B: cita al artículo 233 / numeral 233.1).
> El artículo de traslado (`CUARTO:` o `QUINTO:`) **NUNCA debe quedar vacío**, empleando obligatoria y literalmente la fórmula canónica R-155:
>
> - **Para 1 denunciado (Singular):**
>   `CUARTO: correr traslado de la presente resolución a [DENUNCIADO] para que, de conformidad con lo dispuesto por el artículo 26° de la Ley sobre Facultades, Normas y Organización del Indecopi, aprobado por Decreto Legislativo N° 8079, presente sus descargos sobre la imputación de cargos realizada en un plazo no mayor a cinco (5) días hábiles contado a partir del día siguiente de la notificación de la presente resolución, vencido el cual, el Secretario Técnico declarará en rebeldía a los denunciados que no lo hubieran presentado. Debe precisarse que de conformidad con lo establecido por el artículo 223° del Texto Único Ordenado de la Ley N° 27444, Ley del Procedimiento Administrativo General, las alegaciones y los hechos relevantes de la reclamación, salvo que hayan sido específicamente negadas en la contestación, se tendrán por aceptadas o meritadas como ciertas.`
>
> - **Para 2 o más denunciados (Plural):**
>   `[CUARTO o QUINTO]: correr traslado de la presente resolución a [DENUNCIADO 1] y [DENUNCIADO 2] para que, de conformidad con lo dispuesto por el artículo 26° de la Ley sobre Facultades, Normas y Organización del Indecopi, aprobado por Decreto Legislativo N° 8079, presenten sus descargos sobre la imputación de cargos realizada en un plazo no mayor a cinco (5) días hábiles contado a partir del día siguiente de la notificación de la presente resolución, vencido el cual, el Secretario Técnico declarará en rebeldía a los denunciados que no lo hubieran presentado. Debe precisarse que de conformidad con lo establecido por el artículo 223° del Texto Único Ordenado de la Ley N° 27444, Ley del Procedimiento Administrativo General, las alegaciones y los hechos relevantes de la reclamación, salvo que hayan sido específicamente negadas en la contestación, se tendrán por aceptadas o meritadas como ciertas.`

---

## 3. DOMICILIOS PROCESALES Y VÍAS OFICIALES POR PROVEEDOR

> **Mandato del instructor (18/09/2026), corroborado por el corpus:** la vía de
> cada proveedor es **fija**, no depende de apersonamiento previo.

- **Casilla Electrónica (SINE Indecopi) — 5 días:** **Pacífico Compañía de Seguros
  (152 de 152)**, **Interseguro Compañía de Seguros (67 de 67)**, Mapfre Perú
  Compañía de Seguros (100 de 100), La Positiva Seguros y Reaseguros (48 de 48),
  La Positiva Vida (12 de 12), Chubb Perú (11 de 11), Protecta (3 de 3), Quálitas,
  BNP Paribas Cardif, Crecer Seguros, Vivir Seguros, Banco BBVA Perú, Empresa de
  Créditos Santander Consumo Perú, Banco Falabella, Diners Club Perú.
- **Correo electrónico autorizado — 2 días:** **Rímac Seguros y Reaseguros
  (137 de 137)**, Banco de Crédito del Perú — BCP (28 de 29), Scotiabank Perú
  (7 de 7), Interbank (7 de 7), Banco Ripley (2 de 2).
- **Domicilio Procesal / Cédula Física — 2 días:** AFOCATs provinciales y
  regionales, Comités de Administración CAFAE, corredores de seguros, talleres y
  personas naturales denunciadas sin canal electrónico.

> **Corrección medida (18/09/2026):** la versión anterior clasificaba a Rímac y al
> BCP como «Correo Electrónico / Casilla, según apersonamiento previo». El corpus
> no es ambiguo: **Rímac va por correo en 137 de 137** y el BCP en 28 de 29. La
> ambigüedad no describía la práctica. Rímac figuraba además, por error, en la
> lista de Casilla Electrónica.

### La Casilla Electrónica tiene tres requisitos, y son condición NECESARIA (R-151)

> **Mandato del instructor (18/09/2026).** Solo procede notificar a Casilla
> Electrónica cuando el registro en el padrón de Términos y Condiciones está
> **ACTIVO**, tiene **número de e-casilla** y tiene **teléfono móvil registrado y
> no vacío**. Si falta cualquiera de los tres, **la casilla está prohibida** y la
> parte se notifica por correo electrónico o por domicilio procesal.

Es condición **necesaria, no suficiente**: estar habilitado no obliga a usar la
casilla —eso lo fija la cédula (R-129)—, pero **no estarlo la prohíbe**.

La lista viva está en **`docs/casillas_habilitadas.json`**, que produce
`scripts/filtrar_casillas.py` desde el padrón. `verificar_admisorio.py` la lee y
falsa cualquier admisorio que notifique a casilla a quien no la tiene habilitada.

**El padrón no se versiona.** Trae 30 105 registros con DNI, nombres, correos y
teléfonos de consumidores, y este repositorio es público. Solo se publica el
veredicto por proveedor: ni una persona natural, ni un dato de contacto.

Medido sobre el padrón del 17/09/2026: de 30 005 registros activos, **13 244
(44 %) no tienen teléfono móvil**, luego no admiten casilla. Entre ellos:
**Rímac Seguros y Reaseguros (de baja en el padrón)**, Banco de Crédito del Perú,
Banco Ripley, Banco Pichincha (de baja), Financiera Proempresa, Fovipol y varias
AFOCAT y Sub CAFAE. Los tres cruces coinciden con lo que el corpus ya medía: Rímac
por correo en 137 de 137, el BCP en 28 de 29, Ripley en 2 de 2.

Actualizar la lista tras recibir un padrón nuevo:

```bash
python scripts/filtrar_casillas.py <ReportePersonas....xlsx>
python scripts/filtrar_casillas.py <ReportePersonas....xlsx> --verificar
```

- **La cédula de notificación de la carpeta manda sobre esta lista (R-129):** de ella se
  toman las partes y el domicilio procesal; la vía que indique es la que se usa,
  **siempre que R-151 la permita**.
- **Un ordinal por VÍA, no por parte (R-147, corregida el 18/09/2026):** dos partes
  que comparten vía van **en el mismo ordinal**, con el verbo en plural y unidas
  por «y a»/«y al» (93 plantillas). Dos vías distintas, dos ordinales (362
  plantillas). Fundir dos vías distintas con «; y,» **no ocurre ni una sola vez en
  1 087 párrafos de notificación**.

---

## 4. TAXONOMÍA Y LOCALIZACIÓN DE PLANTILLAS
El repositorio contiene **593 plantillas Word (.docx) depuradas** en `plantillas_maestras/`:
- `01_seguro_vehicular` (174) | `02_seguro_vida` (134) | `03_seguro_desgravamen` (66)
- `04_seguro_proteccion_tarjetas_y_dinero` (37) | `05_soat_y_afocat` (43) | `06_seguro_hogar_e_inmuebles` (20)
- `07_seguro_sctr` (18) | `08_seguro_salud_eps_oncologico` (12) | `09_seguro_patrimonial_caucion_rc` (10)
- `10_seguro_sepelio` (8) | `11_seguro_accidentes_personales` (7) | `12_seguro_transporte_y_carga` (6)
- `13_seguro_multiple_y_equipos` (4) | `14_seguro_desempleo` (2) | `15_sistema_previsional_afp_onp` (2)
- `16_temas_administrativos_financieros` (4) | `17_seguro_no_especificado` (58)

---

## 5. PARÁMETROS DE ESTILO VISUAL CC1
- **Fuente:** `Arial Narrow` (11 pt cuerpo de texto, 8 pt notas al pie y encabezados).
- **Márgenes A4:** Superior 2,5 cm, Inferior 2,5 cm, Izquierdo 3,0 cm, **Derecho 3,0 cm**
  (medido: 113 de 116 secciones del corpus; el valor 2,5 que figuraba aquí estaba falsado
  y hacía fallar R-144, que sí está implementada en el verificador).
- **Interlineado:** Sencillo 1.0, espaciado `0 pt antes / 0 pt después`.
- **Sangrías Institucionales:**
  - Hechos: Izquierda `0.79"` (2.0 cm), Francesa `-0.39"` (-1.0 cm).
  - Resolutivo: Izquierda `0.39"` (1.0 cm), Francesa `-0.39"` (-1.0 cm).
- **Notas al Pie (R-106, R-153):** Formato con *One Dot Leader* (`\u2024`). Tanto la llamada de nota al pie en el cuerpo (`<w:footnoteReference>`) como la referencia en el pie (`<w:footnoteRef/>`) deben tener explícitamente formato de superíndice (`<w:vertAlign w:val="superscript"/>`) y estilo `Refdenotaalpie`. Tamaño de nota al pie: 8 pt (`<w:sz w:val="16"/>`). Pie institucional: `M-CPC-01/03`.
- **Cero Resaltados (R-154):** Queda estrictamente prohibida cualquier etiqueta `<w:highlight>` en todo el documento. Ningún texto puede entregarse con resaltado o sombreado de color.

---

## 6. FIRMA DIGITAL ÚNICA Y VERIFICACIÓN (R-103, R-127)
- **Mandato del instructor (18/09/2026): firma según el proveedor denunciado.**
  **EVELING ROA QUISPE**, cargo `Secretaria Técnica`, firma **todos** los admisorios,
  salvo las denuncias contra **Rímac**, que firma **LUISA ANALÍ SILVA MALPARTIDA**
  con el cargo `Secretaria Técnica Ad Hoc`. **El sufijo `(e)` queda suprimido.**
  Este mandato deroga la firma única del 14/09/2026, que el corpus nunca corroboró:
  494 de 593 plantillas firman Eveling Roa Quispe. Refrendo: se copia del control o
  de la cédula del caso; no se inventa.
- **Isomorfismos Verbatim (R-97 / R-108):**
  - El núcleo fáctico de imputaciones es idéntico entre la considerativa (Sección II) y el resolutivo (`PRIMERO:`, etc.).
  - El requerimiento de información probatorio debe ser idéntico palabra por palabra entre la considerativa (Sección III) y el resolutivo (`QUINTO:`). Se verifica como **observación**: una divergencia no bloquea la entrega, se eleva al instructor.
- **Protocolo de Verificación Previa Obligatorio (R-109):**
  - Todo admisorio debe pasar: `python scripts/verificar_admisorio.py <admisorio.docx>` y obtener `APTO (0 falsadores)` antes de ser entregado.

---

## 7. ORDEN DE TRABAJO Y ECONOMIA DE PASADAS (R-113 A R-115)

**Antes de leer un expediente:**
```
python scripts/extraer_expediente.py <carpeta_del_expediente>
```
Devuelve el numero real de paginas de cada PDF (R-136), cuales tienen capa de texto y
cuales no, y un dossier de fechas, montos, placas, correos y cartas notariales anclado a
la pagina de origen. **No decide que se lee con vision: todas las paginas van a Google
Lens (R-137).** El texto embebido es el contraste de esa lectura.

**El volcado puede corromper acentos y cifras (R-126):** en el Expediente 3054-2026 la
fecha del escrito «17 de agosto de 2026» salió como «1274 de agosto de 2026». Verifica
todo dato crítico (fechas, montos, números de póliza, nombres) contra el PDF con
PyMuPDF antes de escribirlo en el admisorio.

**Para inspeccionar o comparar un .docx, una sola llamada:**
```
python scripts/inspeccionar_docx.py <archivo.docx>              # volcado integro
python scripts/inspeccionar_docx.py <archivo.docx> --resumen    # esqueleto
python scripts/inspeccionar_docx.py <generado.docx> --diff <control.docx>
```
Prohibido inspeccionar parrafo por parrafo con llamadas sucesivas.

**Antes de entregar:**
```
python scripts/verificar_admisorio.py <generado.docx>
```
Se entrega con `APTO`, pegando la salida literal.

---

## 8. PARO, CONTROL APROBADO Y DEMORA (R-117 A R-123)

- **Caso cerrado = paro inmediato (R-122).** Si la carpeta del expediente trae
  `_ESTADO.md` o `_ORDEN_DE_TRABAJO.md` con «CASO CERRADO», **no generes otro `.docx`**:
  reporta y detente. Regenerar trabajo cerrado es la causa medida de la demora.
- **El control aprobado manda sobre la plantilla (R-117 a R-119):** ordinal, fecha de
  emisión, número de imputaciones y el artículo de cada una, y los incisos del
  requerimiento probatorio se copian del control. Sus erratas no se copian (R-121).
  Si el control contradice al expediente, se redacta según el control y se eleva el
  conflicto al instructor; no se resuelve por cuenta propia.
- **Antes de generar, mide Word (R-116, R-123):** `python scripts/estado_word.py <carpeta>`.
  Un `WINWORD.EXE` sin ventana hace esperar la inyección de notas sin límite; el inyector
  ahora aborta con el PID en vez de esperar, y no mata procesos.
- **Prohibido el PDF (mandato del instructor, R-125):** el entregable es el `.docx`. No se
  convierte, imprime ni exporta a PDF. La conversión era el último consumidor de Word por
  COM y una causa medida de cuelgue.
- **Velocidad con calidad:** un admisorio son **cuatro pasos y ≤ 12 llamadas** (F3 a F5 y
  F14 de `docs/PLAN_VELOCIDAD_SIN_COLGARSE.md`). Prohibido releer lo ya leído o abrir las
  593 plantillas a mano: la base se elige por índice en una llamada.
- **La ley de la latencia (R-134, medida):** la sesión del Exp. 3054-2026 duró 1178 s con
  **67 llamadas reales** — **17,6 s por llamada, haga o no trabajo**; los huecos de
  decisión suman 6 s en total. El cómputo útil de un admisorio es ~12 s. Luego
  **T ≈ 17,6 s × N**: la única palanca es bajar N agrupando trabajo por llamada, no
  optimizar CPU. (La versión anterior de esta regla decía 157 llamadas y 7,5 s: contaba
  pasos de la traza en vez de llamadas. Se corrigió el 14/09/2026.)
- **Presupuesto declarado (R-135):** al cerrar un caso se declara **N** (llamadas) y **T**
  (reloj), contando N por `call_id`. Objetivo: N ≤ 12 y T ≤ 4 minutos en un
  expediente corto; los largos escalan con sus páginas.
- **Cwd y scorecard (F8, F9, F13):** todo comando corre desde la raíz del repositorio, con
  el primer paso `python scripts/admisorio.py preparar <carpeta>` en absoluto (el script
  fija la raíz por construcción). Prohibido buscar scripts del repositorio con `-Recurse`
  fuera de él. Antes de entregar, `admisorio.py entregar --caso <n>` debe dar 0
  operaciones evitables en el scorecard.
- **Fecha única de la remesa (R-128):** todos los admisorios llevan
  `Lima, 14 de setiembre de 2026`, sin importar las fechas de las cédulas.
- **Cédulas de la carpeta (R-129, R-138):** las partes procesales son **exactamente** las
  que la cédula notifica, con **una sola vía** cada una; de ella salen también el
  domicilio procesal y el número de resolución. Sus fechas se ignoran (R-128). Que el
  escrito mencione a otra empresa no la convierte en parte: es contexto del relato. No
  hay nada que elevar, la cédula ya lo resolvió. Se copia además el refrendo del control
  o de la cédula.
- **Subsunción, hechos y escrito: los del control (R-130, R-131, R-132).** Cada conducta
  del control conserva su artículo (arts. 56 b), 47 e), 88.1 incluidos); los hechos van en
  narración directa con el alias del encabezado; la fecha del escrito es la del control y
  la contradicción se eleva.

