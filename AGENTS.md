# AGENTS.md — Admisorios CC1 Indecopi (seguros). Reglas vigentes v3.3

Única fuente de reglas vigentes.
Redactor: **Google Antigravity con el modelo de `config/modelo.json`** (Gemini 3.8 Flash High o superior).

## 0. Arranque
0. **En otra computadora** (el usuario solo pegó el enlace): sigue `ARRANQUE.md`.
   Lee además las skills de `.agents/skills/`: `admisorio-flujo`, `imputaciones` y `partes-y-notificacion`; y `confidencialidad` si el caso la tiene.
1. Trabaja desde la **raíz de este repositorio**. Primer comando: `python scripts/comprobar_anclaje.py`. Si falla, para.
2. Fecha de emisión: `python scripts/config_sistema.py`. Si dice «sin fijar», **pregúntala al instructor** antes de redactar.
3. Si la carpeta del caso trae `_ORDEN_DE_TRABAJO.md`, manda para ese caso. Si trae `_ESTADO.md` con «CASO CERRADO», no generes nada.
4. **Haz solo lo que se hace.** Únicos comandos: `comprobar_anclaje`, `config_sistema`, `admisorio.py preparar|previsualizar|entregar`, `similares`, `construir_admisorio`, `inspeccionar_docx`, `plazos`. Prohibido lo demás (`editar_cedulas`, `python -c`, scripts propios, Word, cédulas, borradores). En la carpeta del caso: originales, lo que generan esos comandos y un único `ADM <EXP> R<N>.docx`; `entregar` rechaza el resto.

## 1. Los pasos (≤ 12 llamadas en un expediente corto)
1. `python scripts/admisorio.py preparar <carpeta>` — capturas, `_LECTURA.md`, `_FORMATO.md` y **`_FICHA.md`** (comandos exactos, firmas digitales, proveedores y vías, tipificación). **Ritmo** (~50 s por decisión): sin `-h`, sin leer scripts ni JSON del repositorio, `_hojas/` en una vuelta, `WaitMsBeforeAsync` 120000.
2. **Lectura visual** de `_hojas/` (dos páginas por imagen): una fila por página en `_LECTURA.md`, con «Lo que vi» y «Formato que vi» (medidas en `_FORMATO.md`, cero OCR). Si el texto embebido discrepa, manda la imagen.
2b. **OBLIGATORIO — las 10 plantillas más similares.** `_CASO.json` (`resolucion`, `carpeta_origen`, `traslado`, escritos con fecha, denunciados DEFINITIVOS, conductas y norma) y `python scripts/similares.py <carpeta>`. En `_SIMILARES.md`, el «Por qué» de las 10. La base sale de ellas; citar otra bloquea la entrega.
3. `python scripts/construir_admisorio.py --mapa <mapa.json>` (para corregir un Word dado, ese Word es la plantilla). Claves = **texto de la plantilla**; `"parrafos"` sustituye un párrafo entero por su inicio. El constructor aplica reglas generales y saneamiento. Sin Word, win32com ni PDF.
3b. `python scripts/admisorio.py previsualizar "<docx>" --contra "<plantilla>"` — `_vista/` con cada página junto a la de la plantilla. **Míralas todas en una vuelta** antes de entregar.
4. `python scripts/admisorio.py entregar "<carpeta>/ADM <EXP> R<N>.docx" --recepcion DD/MM/AAAA` — debe decir **ENTREGABLE** y el verificador **APTO**; copia el Word a `carpeta_origen`. Pega la salida literal.

Nombre del entregable: `ADM <EXPEDIENTE> R<N>.docx`; `<N>` es el número de resolución que fija la cédula. Nunca PDF.

## 2. Reglas no negociables
1. **Nada que no conste en el expediente.** Dato que no ves en una página, se declara pendiente del instructor. **Nunca modifiques el repositorio**: si ves un error del sistema, repórtalo; `entregar` comprueba la integridad.
2. **Fechas de los documentos.** Escrito de parte (denuncia, subsanación…) por mesa de partes virtual o presencial: su fecha es la de su **firma digital**, no la que el escrito dice. Resolución, memorándum o documento de traslado de Indecopi: la **fecha de emisión escrita en su texto**, nunca la de la firma digital.
3. **Denunciados definitivos.** Los que resultan tras la resolución de requerimiento y el escrito que la absuelve: la denuncia inicial puede nombrar a uno y la subsanación añadir otro. Todos los escritos se citan con su fecha en la apertura de HECHOS, en PRIMERO y en SEGUNDO («denuncia del …, subsanada mediante escrito del …»).
4. **Imputación cerrada.** Como imputan **las plantillas** un hecho de igual sentido y finalidad, en su forma literal (`docs/tabla_tipificacion.json` es referencial); nunca una ausente de ellas. **Una por solicitud y por cobertura** diferenciada, aunque vayan juntas; sin cobertura precisa, «coberturas» (R-206).
   - **Nunca el artículo 3** ni la frase «inducción a error».
   - Reclamos: **numeral 88.1 del artículo 88** si el proveedor está regulado por el sistema financiero; **artículo 24** solo si NO lo está. **Un reclamo por imputación**: varios reclamos, varias imputaciones.
   - Fallas de información: «el artículo 1, numeral 1, literal b) y al artículo 2 del Código» (forma de los modelos).
   - Documentos contractuales no entregados **a la firma**: literal e) del artículo 47; pedidos **después** y no entregados: artículo 1, numeral 1, literal b) y artículo 2.
   - **Solicitud de gestión** mal atendida: idoneidad (artículos 18 y 19). **Solicitud de información o de copias**: información. Si la misma carta trae ambas, **dos imputaciones separadas**.
   - Cláusulas abusivas: **siempre** «numeral 49.1 del artículo 49 y al literal x) del artículo 50» (ineficacia absoluta) o «… del artículo 51» (ineficacia relativa).
   - Si no hay imputación así en las plantillas, **se eleva al instructor**.
5. **Uno o varios denunciados** (el número real es el de alias entre paréntesis del encabezado DENUNCIADO(S)):
   - Cada imputación dice **a quién** se atribuye, **idéntica** en considerativa y resolutivo (R-97, R-188):
     - la denunciante, con su **nombre completo** o «la denunciante», nunca la tratativa corta ni «la parte denunciante» (R-205);
     - aseguradora **única**: «**la compañía aseguradora**»; nunca «aseguradora» a secas (R-201);
     - dos o más denunciados, imputaciones separadas: **razón social completa** de cada uno, nunca el alias;
     - conducta común a todos: con exactamente 2, «**los proveedores denunciados**»; con 3 o más, los nombres completos de los implicados.
   - «El proveedor denunciado» solo existe cuando hay uno. TERCERO nombra a todos; cada denunciado, su ordinal de requerimiento.
   - Rótulo del requerimiento: el **alias** del encabezado («Al Banco:») (R-189). Ningún ordinal nombra a quien no es parte ni usa una vía que el caso no tiene (R-190).
6. **Hechos** (sección I):
   - Pasado indicativo.
   - **Nunca «denunciante»**. La tratativa («la señora X») solo en apertura y medida correctiva; viñetas con **sujeto tácito** (R-209).
   - Abre con «Mediante el escrito del …, … denunció a … por presuntas infracciones a la Ley 29571, Código de Protección y Defensa del Consumidor (en adelante, Código), señalando lo siguiente:»; cierra con la medida correctiva. Varios denunciantes: «denunciaron», «señalaron».
   - Una viñeta por hecho, cronológica, con fecha; solo lo que sustenta las imputaciones, sin perder el contexto. «Adquirió» el seguro (R-204); sin valorativos («únicamente», R-203).
   - **Imputaciones**: en condicional («habría denegado»). Negativa: «de manera injustificada/indebida», no en -mente (R-208). «Involucraría una presunta afectación…» solo califica **idoneidad**, nunca información ni 88.1.
7. **Nunca «N°», «N», «Nº», «Nro.» ni «°» ante un número**: «Ley 29571», «artículo 26», «Póliza 2101-1031084». Fechas: «de 2025», nunca «del 2025»; mes en minúscula.
8. **TUO de la LPAG**: Decreto Supremo 006-2026-JUS. Nunca el 004-2019-JUS.
9. **Enmascarado**: la **póliza nunca** lleva asteriscos. Tarjeta, crédito, cuenta y préstamo: **solo los dígitos del medio** («34\*\*\*83», «Crédito vehicular 53\*85»; R-176).
10. **Léxico**:
   - Obligatorio: cónyuge (no esposo/a); luego de (no tras); esta/este sin tilde; médico (no doctor/Dr.); «vehículo con Placa de Rodaje …» (no carro/auto).
   - Moneda: `S/ 1 234,56` y `US$ 1 234,56`.

## 3. Traslado y descargos (R-155) — literal
- La fórmula se copia **literal** de la skill `partes-y-notificacion` (artículo 26 del Decreto Legislativo 807; artículo 223 del TUO de la Ley 27444, «merituadas»).
- **1 denunciado**: «presente» y «al denunciado que no lo hubiera presentado». **2 o más**: «presenten» y «a los denunciados que no lo hubieran presentado».
- Destinatario: razón social completa terminada en «S.A.», con su artículo («al Banco …», «a Rímac …»).
- Sus **dos notas al pie** (art. 26 y art. 223) ya están en toda plantilla: no se borran, mueven ni reescriben (R-173).

## 4. Notificación — literal, un ordinal por VÍA (no por parte)
- Párrafos **literales** (skill `partes-y-notificacion`): casilla (5 días), correo (2 días, apercibimiento) y domicilio procesal (2 días, pide señalar correo).
- Partes y vías: las fija la **cédula**; sin cédula, la vía histórica del proveedor (`docs/directorio_proveedores_domicilios.json`). Casilla solo con padrón ACTIVO, e-casilla y móvil (R-151).
- Misma vía, mismo ordinal («y a»/«y al», verbo en plural, «notificarles»); vías distintas, ordinales distintos.

## 5. Nota al pie 1 y plazo
- **Nota del Código**: tras «Código de Protección y Defensa del Consumidor» en la apertura de HECHOS, nunca tras «señalando lo siguiente:» (R-184).
- Denuncia **derivada** (MEMORANDUM, Documento u Hoja de Traslado) **y el usuario entregó el documento**: la nota 1, tras la fecha del escrito («Mediante el escrito del …¹»), dice «Denuncia remitida a esta Comisión mediante [documento] de fecha [emisión], recibida el [recepción en CC1].» Desacumulada: forma de las plantillas. Nunca inventes esos datos.
- Presentada en CC1: **ninguna nota sobre la denuncia**. Declara `traslado` en `_CASO.json` (null o el documento).
- **Plazo de 20 días hábiles**: `python scripts/plazos.py --desde DD/MM/AAAA`; se informa y **no va en la resolución**.

## 6. Firma y fecha (`config/`)
- **Firma** (`config/firmas.json`): EVELING ROA QUISPE, «Secretaria Técnica». Si entre los denunciados está **Rímac**: LUISA ANALÍ SILVA MALPARTIDA, «Secretaria Técnica Ad Hoc». Nunca «(e)». El refrendo se copia del control o de la cédula.
- **Fecha**: «Lima, [fecha de config/remesa.json]», igual para toda la remesa.

## 7. Forma (corpus y revisión del instructor del 24/09/2026)
- Arial Narrow: cuerpo 11 pt, notas e iniciales («LSQ/DCQ») 8 pt. Interlineado sencillo, espaciado 0/0, justificado; sangría izquierda y francesa de 1,0 cm. A4, márgenes 2,5 cm (arriba/abajo) y 3,0 cm (lados). Pie `M-CPC-01/03`. Sin resaltados.
- Negrita: **solo el rótulo de cada ordinal, también en PRIMERO** («**PRIMERO:** admitir…», R-164). Ordinales seguidos, sin saltos.
- Subrayado: solo el rótulo del requerimiento de **cada** denunciado («A La Positiva:», R-207), nunca el párrafo ni frases del resolutivo (R-192). Encabezado «ETIQUETA<tab>:<tab>VALOR».
- Considerativa en una serie continua (R-191); una línea en blanco entre imputaciones, nunca dos (R-194). Si se deja sin efecto una inadmisibilidad, se conservan su apartado y su ordinal.
- **Notas al pie** (R-183 a R-187): toda llamada con su nota y viceversa; **nunca dos llamadas juntas**; competencia tras «en ejercicio de sus facultades»; la nota de la norma imputada solo en la **primera** imputación de ese artículo (R-202); una tabulación tras la llamada y todas las líneas a 1 cm; sin líneas en blanco dentro y una al final; sin dobles espacios; literales completos y con su letra. El constructor lo aplica solo (anclas en `docs/anclas_notas.json`; detalle en la skill `admisorio-flujo`). La transcripción literal de una norma se respeta tal cual.
- **Firma**: cuatro líneas centradas: «Firmado digitalmente por» / FIRMANTE / CARGO / «Comisión de Protección al Consumidor 1» (R-193).
- Núcleo de cada imputación idéntico en considerativa y resolutivo, **mismo orden y mismo artículo**.

## 8. Control y consulta
- **El control aprobado manda** en ordinal, fecha, imputaciones y requerimientos; sus erratas no se copian. Si contradice al expediente, se eleva al instructor.
- **No usar** `automatizacion_antigravity/modelos/` (mezclan expedientes). La base es una plantilla del índice, preferentemente **APTA**; el número de denunciados lo da el índice (`denunciados.n`), no la carpeta. Confidencialidad: skill `confidencialidad`.
