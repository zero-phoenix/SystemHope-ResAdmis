# AGENTS.md — Admisorios CC1 Indecopi (seguros). Reglas vigentes v3

Única fuente de reglas. Solo contiene lo **vigente**; el historial está en `CHANGELOG.md`
y `automatizacion_antigravity/REGLAS_DE_APRENDIZAJE.md` (consulta dirigida, no lectura de arranque).
Redactor: **Google Antigravity con el modelo de `config/modelo.json`** (Gemini 3.8 Flash High o superior).

## 0. Arranque
0. **En otra computadora** (el usuario solo pegó el enlace): sigue `ARRANQUE.md`. Instala Python y Git portátiles en `%USERPROFILE%\SystemHope\` y te trae aquí.
   Lee además las skills de `.agents/skills/`: `admisorio-flujo`, `imputaciones` y `partes-y-notificacion`; y `confidencialidad` si el caso la tiene.
1. Trabaja desde la **raíz de este repositorio**. Primer comando: `python scripts/comprobar_anclaje.py`. Si falla, para.
2. Fecha de emisión: `python scripts/config_sistema.py`. Si dice «sin fijar», **pregúntala al instructor** antes de redactar.
3. Si la carpeta del caso trae `_ORDEN_DE_TRABAJO.md`, manda para ese caso. Si trae `_ESTADO.md` con «CASO CERRADO», no generes nada.

## 1. Los cuatro pasos (≤ 12 llamadas en un expediente corto)
1. `python scripts/admisorio.py preparar <carpeta>` — triaje, candidatas de plantilla, **captura completa de cada página** en `_paginas/` y `_LECTURA.md` preparado.
2. **Lectura visual**: abre cada PNG de `_paginas/` y llena su fila de `_LECTURA.md` con lo que ves (tipo de documento, fechas, montos, números, sellos, firmas, resaltados, formato). Cero OCR. El texto embebido solo sirve de contraste; si discrepa, manda la imagen. Copiar el texto embebido no es lectura y `entregar` lo rechaza.
3. `python scripts/construir_admisorio.py --mapa <mapa.json>` sobre la plantilla elegida (sin Word, sin win32com, sin PDF).
4. `python scripts/admisorio.py entregar "<carpeta>/ADM <EXP> R<N>.docx" --recepcion DD/MM/AAAA` — debe decir **ENTREGABLE** y el verificador **APTO**. Pega la salida literal.

Nombre del entregable: `ADM <EXPEDIENTE> R<N>.docx`; `<N>` es el número de resolución que fija la cédula. Nunca PDF.

## 2. Reglas no negociables
1. **Nada que no conste en el expediente.** Dato que no ves en una página, se declara pendiente del instructor.
2. **Imputación cerrada.** Solo por los artículos de `docs/tabla_tipificacion.json` (tabla del instructor) y en la **forma literal de las plantillas**. Prohibido inventar imputaciones o combinar artículos de otro modo.
   - **Nunca el artículo 3** ni la frase «inducción a error».
   - Reclamos: **numeral 88.1 del artículo 88** si el proveedor está regulado por el sistema financiero; **artículo 24** solo si NO lo está.
   - Fallas de información: «el artículo 1, numeral 1, literal b) y al artículo 2 del Código» (forma de los modelos).
   - Documentos contractuales:
     - no entregados **a la firma**: literal e) del artículo 47;
     - pedidos **después** y no entregados: artículo 1, numeral 1, literal b) y artículo 2.
   - **Solicitud de gestión** mal atendida: idoneidad (artículos 18 y 19). **Solicitud de información o de copias**: información. Si la misma carta trae ambas, **dos imputaciones separadas**.
   - Cláusulas abusivas: **siempre** «numeral 49.1 del artículo 49 y al literal x) del artículo 50» (ineficacia absoluta) o «… del artículo 51» (ineficacia relativa).
   - Formas canónicas y lo que no se hace: `docs/IMPUTACIONES_ANALITICO.md`.
   - Si la imputación necesaria no está en la tabla, **se eleva al instructor**.
3. **Uno o varios denunciados** (el número real es el de alias entre paréntesis del encabezado DENUNCIADO(S)):
   - Cada imputación dice **a quién** se atribuye. Una conducta de un solo proveedor lleva el nombre de ese proveedor.
   - **Imputación conjunta** solo si la conducta es común a ambos (p. ej., el banco contratante y la aseguradora emisora del desgravamen que no entregan el contrato).
     - Con **exactamente 2** denunciados: «**los proveedores denunciados** no habrían…».
     - Con **3 o más**: los **nombres completos** de los dos implicados.
   - «El proveedor denunciado» solo existe cuando hay uno.
   - TERCERO nombra a todos los denunciados. Cada denunciado tiene su propio ordinal de requerimiento de información.
4. **Hechos** (sección I):
   - Pasado indicativo.
   - **Nunca «denunciante»** en la narración: se usa la tratativa del encabezado («el señor X», «la señora X», «la Sucesión…»).
   - Abre con «Mediante el escrito del …, … denunció a … por presuntas infracciones a la Ley 29571, Código de Protección y Defensa del Consumidor (en adelante, Código), señalando lo siguiente:» y cierra con el párrafo de medida correctiva.
   - **Imputaciones**: en condicional («habría denegado»).
5. **Nunca «N°», «N», «Nº», «Nro.» ni «°» ante un número, en ningún contexto**: «Ley 29571», «artículo 26», «numeral 1.1 del artículo 51», «Expediente 1234-2026/CC1», «Póliza 2101-1031084», «Documento de Traslado 248-2026-PS2/INDECOPI».
   - Fechas: «de 2025», nunca «del 2025»; el mes, en minúscula.
6. **TUO de la LPAG**: Decreto Supremo 006-2026-JUS. Nunca el 004-2019-JUS.
7. **Enmascarado**: la **póliza nunca** lleva asteriscos. Tarjeta, crédito, cuenta y préstamo: se enmascaran **solo los dígitos del medio** («34\*\*\*83», «100xxxxxx434»).
8. **Léxico**:
   - Obligatorio: cónyuge (no esposo/a); luego de (no tras); esta/este sin tilde; médico (no doctor/Dr.); «vehículo con Placa de Rodaje …» (no carro/auto).
   - Moneda: `S/ 1 234,56` y `US$ 1 234,56`.

## 3. Traslado y descargos (R-155) — literal
`correr traslado de la presente resolución a [DENUNCIADO(S)] para que, de conformidad con lo dispuesto por el artículo 26 de la Ley sobre Facultades, Normas y Organización del Indecopi, aprobada por Decreto Legislativo 807, presente[n] sus descargos sobre la imputación de cargos realizada en un plazo no mayor a cinco (5) días hábiles contado a partir del día siguiente de la notificación de la presente resolución, vencido el cual, el Secretario Técnico declarará en rebeldía [al denunciado que no lo hubiera presentado | a los denunciados que no lo hubieran presentado]. Debe precisarse que de conformidad con lo establecido por el artículo 223 del Texto Único Ordenado de la Ley 27444, Ley del Procedimiento Administrativo General, las alegaciones y los hechos relevantes de la reclamación, salvo que hayan sido específicamente negadas en la contestación, se tendrán por aceptadas o merituadas como ciertas.`

- **1 denunciado**: «presente» y «al denunciado que no lo hubiera presentado».
- **2 o más**: «presenten» y «a los denunciados que no lo hubieran presentado».
- El destinatario es la razón social completa, terminada en «S.A.».

## 4. Notificación — literal, un ordinal por VÍA (no por parte)
- **Casilla Electrónica (5 días)**: «requerir a [PARTE(S)] para que efectúe[n] el acuse de recibo mediante la confirmación de recepción de la notificación remitida por este despacho a su[s] Casilla[s] Electrónica[s], dentro de los cinco (5) primeros días hábiles siguientes a la fecha en que recibe[n] la notificación.»
- **Correo electrónico (2 días)**: «requerir a [PARTE(S)] para que, dentro del plazo de dos (2) días hábiles siguientes a la fecha en que reciba[n] la notificación en su[s] bandeja[s] de correo electrónico, efectúe[n] la confirmación de recepción de la notificación remitida por este despacho a su[s] correo[s] electrónico[s], de conformidad con el segundo párrafo del numeral 4 del artículo 20 del Texto Único Ordenado de la Ley del Procedimiento Administrativo General, aprobado mediante Decreto Supremo 006-2026-JUS, bajo apercibimiento de rehacer el acto de notificación y notificarle[s] conforme al numeral 1 del artículo 20 del citado cuerpo normativo.»
- **Domicilio procesal (2 días)**: «requerir a [PARTE(S)] para que, dentro del plazo de dos (2) días hábiles siguientes a la fecha en que reciba[n] la notificación en su domicilio procesal, señale[n] un correo electrónico autorizando recibir las notificaciones correspondientes por dicho medio.» (No pide acuse.)
- **Las partes y la vía de cada una las fija la cédula del caso.** Si no hay cédula, **se repite la vía con la que ese proveedor ha sido notificado siempre** (`docs/directorio_proveedores_domicilios.json`):
  - Rímac, BCP, Scotiabank, Interbank y Ripley van por **correo**.
  - Pacífico, Interseguro, Mapfre, La Positiva, Chubb, Protecta, Quálitas, Cardif, BBVA, Santander Consumo, Falabella y Diners van por **casilla**.
  - AFOCAT, CAFAE, corredores y personas naturales sin canal van por **domicilio**.
- La casilla exige padrón ACTIVO, número de e-casilla y móvil registrado (`docs/casillas_habilitadas.json`, R-151). Sin eso, está prohibida.
- Dos partes con la misma vía comparten ordinal («y a»/«y al», verbo en plural). Dos vías distintas llevan dos ordinales.

## 5. Nota al pie 1 y plazo
- Si la denuncia llegó derivada de otro órgano, la **nota al pie 1** (primera página) dice: «Denuncia remitida a esta Comisión mediante [MEMORANDUM | Documento de Traslado] [número] de fecha [fecha de emisión], recibida el [fecha de recepción en CC1].»
  Siempre «recibida», nunca «recepcionada». Si se presentó directamente en CC1, no lleva esta nota.
- El **plazo de 20 días hábiles** (desde el día siguiente a la recepción en CC1 o a la presentación) se **calcula** con `python scripts/plazos.py --desde DD/MM/AAAA` y se informa. **No se menciona en la resolución.**

## 6. Firma y fecha (`config/`)
- **Firma** (`config/firmas.json`): EVELING ROA QUISPE, «Secretaria Técnica». Si entre los denunciados está **Rímac**: LUISA ANALÍ SILVA MALPARTIDA, «Secretaria Técnica Ad Hoc». Nunca «(e)». El refrendo se copia del control o de la cédula.
- **Fecha**: «Lima, [fecha de config/remesa.json]», igual para toda la remesa.

## 7. Forma (medida en el corpus)
- Arial Narrow en todo el documento; 11 pt en el cuerpo y 8 pt en las notas.
- Interlineado sencillo, espaciado 0/0, justificado. Sangría izquierda de 1,0 cm y francesa de 1,0 cm (571 de 574 plantillas).
- Márgenes A4: 2,5 cm arriba y abajo, 3,0 cm a izquierda y derecha.
- Notas al pie con llamada en superíndice, estilo `Refdenotaalpie`. Pie `M-CPC-01/03`. Sin resaltados.
- El núcleo fáctico de cada imputación es idéntico en la considerativa y en el resolutivo, **en el mismo orden y con el mismo artículo**.

## 8. Control y consulta
- **El control aprobado manda** en ordinal, fecha, imputaciones y requerimientos; sus erratas no se copian. Si contradice al expediente, se eleva al instructor.
- **No usar** `automatizacion_antigravity/modelos/`, que mezclan varios expedientes.
  - La base es una plantilla del índice, preferentemente **APTA**.
  - La carpeta física de una plantilla no indica cuántos denunciados tiene; el índice (`denunciados.n`) sí.
  - Subtipo **confidencialidad** (23 plantillas): skill `confidencialidad`.
- Para comparar: `python scripts/inspeccionar_docx.py <generado> --diff <control>`.
- **Consulta**: `docs/ANATOMIA_DEL_ADMISORIO.md`, `docs/COMO_NO_SE_REDACTA.md`, `docs/catalogo_imputaciones.json`, `docs/SUPERVISION_DE_AGENTES.md`.
