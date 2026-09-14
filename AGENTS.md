# DIRECTRICES MAESTRAS DEL SISTEMA (AGENTS.md)
# SISTEMA DE EMISION DE RESOLUCIONES ADMISORIAS INDECOPI CC1

> **AUTORIDAD:** Indecopi Comisión de Protección al Consumidor  1 (CC1)  
> **NORMA MARCO:** Decreto Supremo 006-2026-JUS  
> **PROTOCOLO DE LECTURA:** cero OCR óptico. Primero `scripts/extraer_expediente.py`: las páginas con capa de texto se leen literales (no es OCR, es el texto embebido); Google Lens / Visión Multimodal **solo** en las páginas que el triaje marque sin texto.  
> **PROTOCOLO DE ENTREGA:** `scripts/verificar_admisorio.py` debe decir `APTO`. Sin esa salida, el admisorio no está entregado.  
> **REPOSITORIO:** https://github.com/zero-phoenix/SystemHope-ResAdmis

---

## LECTURA DE ARRANQUE: SOLO ESTE ARCHIVO

Para redactar un admisorio **basta con este archivo**. `REGLAS_DE_APRENDIZAJE.md` (79 KB) y
`MATRIZ_MAESTRA_PHOENYX_POPPERIANA.md` (45 KB) son corpus de **consulta dirigida**: se abren
para buscar una regla concreta, no se leen enteros antes de empezar.

**Los cinco pasos, en orden:**

1. `python scripts/extraer_expediente.py <carpeta>` — triaje y dossier anclado.
2. Vision multimodal **solo** en las paginas que el triaje liste sin capa de texto.
3. Redaccion sobre la plantilla que corresponda al patron del caso.
4. `python scripts/inspeccionar_docx.py <generado> --diff <control>` — si hay control.
5. `python scripts/verificar_admisorio.py <generado>` — se entrega con `APTO`, pegando la
   salida literal. Sin eso, el admisorio no esta entregado.

**Si la carpeta del expediente trae un `_ORDEN_DE_TRABAJO.md`, ese archivo manda sobre este
para ese caso concreto:** significa que el triaje, la eleccion de plantilla y el anclaje de
datos ya estan hechos y no hay que rehacerlos.

---

## 1. REGLAS NO NEGOCIABLES (AXIOMAS POPPERIANOS)
1. **PROHIBICIÓN ESTRICTA DE OCR:** Jamás transcribir denuncias con OCR clásico ni extractores que rompan coordenadas o inventen datos. Se analiza la imagen de la denuncia escaneada con Google Lens o modelos de visión directa.
2. **TUO LPAG ACTUALIZADO:** Siempre citar el **Decreto Supremo 006-2026-JUS**. Prohibida cualquier mención al D.S. 004-2019-JUS.
3. **PROHIBICIÓN DE 'INDUCCIÓN A ERROR':** Nunca imputar por el Artículo 3° ni emplear la frase 'inducción a error'. Todas las fallas de información se canalizan por los Artículos 1°, numeral 1, literal b) y 2° del Código de Protección y Defensa del Consumidor.
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
> *"requerir a [PARTE(S)] para que, dentro del plazo de dos (2) días hábiles siguientes a la fecha en que reciba[n] la notificación en su[s] bandeja[s] de correo electrónico, efectúe[n] la confirmación de recepción de la notificación remitida por este despacho a su[s] correo[s] electrónico[s], de conformidad con el segundo párrafo del numeral 4 del artículo 20° del Texto Único Ordenado de la Ley del Procedimiento Administrativo General, aprobado mediante Decreto Supremo 006-2026-JUS, bajo apercibimiento de rehacer el acto de notificación y notificarle[s] conforme al numeral 1 del artículo 20° del citado cuerpo normativo."*

### TIPO 3: VÍA DOMICILIO PROCESAL / CÉDULA FÍSICA (2 DÍAS)
*Para denunciantes sin correo, AFOCATs, fondos especiales (CAFAE) o proveedores sin casilla:*
> *"requerir a [PARTE(S)] para que, dentro del plazo de dos (2) días hábiles siguientes a la fecha en que reciba[n] la notificación en su domicilio procesal, efectúe[n] la confirmación de recepción de la notificación remitida por este despacho a su domicilio procesal, de conformidad con el segundo párrafo del numeral 4 del artículo 20° del Texto Único Ordenado de la Ley del Procedimiento Administrativo General, aprobado mediante Decreto Supremo 006-2026-JUS, bajo apercibimiento de rehacer el acto de notificación y notificarle[s] conforme al numeral 1 del artículo 20° del citado cuerpo normativo."*

---

## 3. DOMICILIOS PROCESALES Y VÍAS OFICIALES POR PROVEEDOR
- **Casilla Electrónica (SINE Indecopi):** Pacífico Compañía de Seguros, Mapfre Perú Compañía de Seguros, Interseguro Compañía de Seguros, La Positiva Seguros y Reaseguros, BNP Paribas Cardif, Chubb Perú, Quálitas Compañía de Seguros, Protecta Compañía de Seguros, Crecer Seguros, Vivir Seguros Compañía de Seguros de Vida, Banco BBVA Perú, Scotiabank Perú, Interbank, Empresa de Créditos Santander Consumo Perú, Banco Falabella, Banco Ripley, Banco Pichincha, Banco GNB.
- **La cédula de notificación de la carpeta manda sobre esta lista (R-129):** de ella se
  toman las partes y el domicilio procesal; la vía que indique es la que se usa.
- **Correo Electrónico Autorizado / Casilla:** Rímac Seguros y Reaseguros, Banco de Crédito del Perú (BCP).
- **Domicilio Procesal / Cédula Física:** AFOCATs provinciales/regionales, Comités de Administración CAFAE, talleres y personas naturales denunciadas.

---

## 4. TAXONOMÍA Y LOCALIZACIÓN DE PLANTILLAS
El repositorio contiene **605 plantillas Word (.docx) depuradas** en `plantillas_maestras/`:
- `01_seguro_vehicular` (174) | `02_seguro_vida` (134) | `03_seguro_desgravamen` (66)
- `04_seguro_proteccion_tarjetas_y_dinero` (37) | `05_soat_y_afocat` (43) | `06_seguro_hogar_e_inmuebles` (20)
- `07_seguro_sctr` (18) | `08_seguro_salud_eps_oncologico` (12) | `09_seguro_patrimonial_caucion_rc` (10)
- `10_seguro_sepelio` (8) | `11_seguro_accidentes_personales` (7) | `12_seguro_transporte_y_carga` (6)
- `13_seguro_multiple_y_equipos` (4) | `14_seguro_desempleo` (2) | `15_sistema_previsional_afp_onp` (2)
- `16_temas_administrativos_financieros` (4) | `17_seguro_no_especificado` (58)

---

## 5. PARÁMETROS DE ESTILO VISUAL CC1
- **Fuente:** `Arial Narrow` (11 pt cuerpo de texto, 8 pt notas al pie y encabezados).
- **Márgenes A4:** Superior 2.5 cm, Inferior 2.5 cm, Izquierdo 3.0 cm, Derecho 2.5 cm.
- **Interlineado:** Sencillo 1.0, espaciado `0 pt antes / 0 pt después`.
- **Sangrías Institucionales:**
  - Hechos: Izquierda `0.79"` (2.0 cm), Francesa `-0.39"` (-1.0 cm).
  - Resolutivo: Izquierda `0.39"` (1.0 cm), Francesa `-0.39"` (-1.0 cm).
- **Notas al Pie:** Formato con *One Dot Leader* (`\u2024`). Pie institucional: `M-CPC-01/03`.

---

## 6. FIRMA DIGITAL ÚNICA Y VERIFICACIÓN (R-103, R-127)
- **Mandato del instructor (14/09/2026): firma única.** Todos los admisorios firman
  **LUISA ANALÍ SILVA MALPARTIDA**, cargo `Secretaria Técnica (e)`. **Nunca** EVELING ROA
  QUISPE. **Nunca** designación `Ad Hoc`. Refrendo: se copia del control o de la cédula
  del caso (observados: `LSQ/DCQ`, `LSQ/JCQ`); no se inventa.
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
Devuelve que paginas tienen capa de texto (se leen literales) y cuales requieren vision
multimodal (solo esas). Incluye un dossier de fechas, montos, placas, correos y cartas
notariales anclado a la pagina de origen.

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
- **Velocidad con calidad:** un admisorio son **cinco pasos y ≤ 12 llamadas** (F3 a F5 de
  `docs/PLAN_VELOCIDAD_SIN_COLGARSE.md`). Prohibido releer lo ya leído o abrir las 630
  plantillas a mano: la base se elige por índice en una llamada.
- **Cwd y scorecard (F8, F9, F13):** todo comando corre desde la raíz del repositorio, con
  el primer paso `python scripts/extraer_expediente.py <carpeta>` en absoluto. Prohibido
  buscar scripts del repositorio con `-Recurse` fuera de él. Antes de entregar,
  `python scripts/auditar_trayectoria.py --caso <n>` debe dar 0 operaciones evitables.
- **Fecha única de la remesa (R-128):** todos los admisorios llevan
  `Lima, 14 de setiembre de 2026`, sin importar las fechas de las cédulas.
- **Cédulas de la carpeta (R-129):** de ellas se toman las partes procesales y el
  domicilio procesal; sus fechas se ignoran; la vía de notificación es la que la cédula
  indique. Se copia además el refrendo del control o de la cédula.
- **Subsunción, hechos y escrito: los del control (R-130, R-131, R-132).** Cada conducta
  del control conserva su artículo (arts. 56 b), 47 e), 88.1 incluidos); los hechos van en
  narración directa con el alias del encabezado; la fecha del escrito es la del control y
  la contradicción se eleva.

