---
name: partes-y-notificacion
description: Identificar y nombrar correctamente a denunciantes (varón, mujer, sucesión intestada, herederos, cónyuges, persona jurídica, asociación, varios) y denunciados (uno, dos, tres o más) de un admisorio CC1, y redactar los párrafos de traslado y de notificación por casilla electrónica, correo electrónico o domicilio procesal.
---

# Partes y notificación

## Denunciantes: cómo se nombran (medido en 574 plantillas)
| Clase | Encabezado | HECHOS | Imputaciones y PRIMERO («interpuesta por …») |
|---|---|---|---|
| Varón (321) | `DENUNCIANTE: NOMBRE (SEÑOR APELLIDO)` | «el señor Apellido» | «el señor Nombre Completo» |
| Mujer (199) | `(SEÑORA APELLIDO)` | «la señora Apellido» | «la señora Nombre Completo» |
| Sucesión intestada (34) | `SUCESIÓN INTESTADA DE … (SUCESIÓN)` | «la Sucesión …» | «la Sucesión Intestada de …» |
| Varios, cónyuges o herederos no acreditados como sucesión (14) | una línea y un alias por persona; `DENUNCIANTES` | «el señor X y la señora Y» | ambos nombres completos |
| Persona jurídica o asociación | `RAZÓN SOCIAL (ALIAS)` | el alias | la razón social |

- Con varios denunciantes cambia la concordancia: «denunciaron», «solicitaron», «sus». Cada uno se notifica por su vía.
- En las **imputaciones** (considerativa y resolutivo) la persona va con su **nombre completo**; la tratativa corta («la señora Apellido») es solo de los hechos (R-188).
- Si los herederos **no** acreditaron la sucesión, se nombran como personas, no como «la Sucesión».
- Nunca «denunciante» en HECHOS.

## Denunciados
- El número real es el de **alias entre paréntesis** del bloque DENUNCIADO(S). La cédula del caso fija las partes.
- **1**: encabezado «DENUNCIADO:». Traslado en singular, «presente» y «al denunciado que no lo hubiera presentado». «El proveedor denunciado» es válido.
- **2 o más**: encabezado «DENUNCIADOS:», una línea por proveedor. Traslado en plural, «presenten» y «a los denunciados que no lo hubieran presentado».
  - Cada imputación nombra a su proveedor.
  - La conjunta, solo si la conducta es común: con 2 denunciados, «los proveedores denunciados»; con 3 o más, los dos nombres completos.
  - TERCERO nombra a todos.
  - Un ordinal de requerimiento de información por proveedor.
  - Rótulo del requerimiento en la considerativa: el **alias** del encabezado («Al Banco:»), subrayado solo el rótulo (R-189, R-192).
  - Aseguradora **única** denunciada: en las imputaciones, «la compañía aseguradora». Con dos o más: razón social completa de cada una (R-188).
  - Artículo según la razón social: «al Banco …», «a Rímac …». Ningún ordinal nombra a quien no es parte (R-190).
- Destinatario del traslado: razón social completa, terminada en «S.A.» (o «S.A.A.», «S.A.C.»).

## Traslado (literal)
«correr traslado de la presente resolución a [DENUNCIADO(S)] para que, de conformidad con lo dispuesto por el artículo 26 de la Ley sobre Facultades, Normas y Organización del Indecopi, aprobada por Decreto Legislativo 807, presente[n] sus descargos sobre la imputación de cargos realizada en un plazo no mayor a cinco (5) días hábiles contado a partir del día siguiente de la notificación de la presente resolución, vencido el cual, el Secretario Técnico declarará en rebeldía [al denunciado que no lo hubiera presentado | a los denunciados que no lo hubieran presentado]. Debe precisarse que de conformidad con lo establecido por el artículo 223 del Texto Único Ordenado de la Ley 27444, Ley del Procedimiento Administrativo General, las alegaciones y los hechos relevantes de la reclamación, salvo que hayan sido específicamente negadas en la contestación, se tendrán por aceptadas o merituadas como ciertas.»

## Vía de notificación
- **La cédula manda.** Sin cédula, se **repite la vía con la que ese proveedor se notificó siempre**, según `docs/directorio_proveedores_domicilios.json` y el campo `denunciados.detalle[].via` del índice:
  - **Casilla**: Pacífico, Interseguro, Mapfre, La Positiva (Seguros y Vida), Chubb, Protecta, Quálitas, Cardif, BBVA, Santander Consumo, Falabella, Diners.
  - **Correo**: Rímac, BCP, Scotiabank, Interbank, Ripley.
  - **Domicilio procesal**: AFOCAT, CAFAE, corredores, talleres y personas naturales sin canal.
- La casilla exige padrón ACTIVO, e-casilla y móvil registrado (`docs/casillas_habilitadas.json`). Si falta alguno, no se usa.
- **Un ordinal por vía, no por parte.** Las partes que comparten vía van juntas, con «y a» o «y al» y el verbo en plural («reciban», «efectúen», «notificarles»); con una sola parte, singular («notificarle»). Ninguna vía que el caso no tenga (R-190).

### Casilla electrónica (5 días)
«requerir a [PARTE(S)] para que efectúe[n] el acuse de recibo mediante la confirmación de recepción de la notificación remitida por este despacho a su[s] Casilla[s] Electrónica[s], dentro de los cinco (5) primeros días hábiles siguientes a la fecha en que recibe[n] la notificación.»

### Correo electrónico (2 días)
«requerir a [PARTE(S)] para que, dentro del plazo de dos (2) días hábiles siguientes a la fecha en que reciba[n] la notificación en su[s] bandeja[s] de correo electrónico, efectúe[n] la confirmación de recepción de la notificación remitida por este despacho a su[s] correo[s] electrónico[s], de conformidad con el segundo párrafo del numeral 4 del artículo 20 del Texto Único Ordenado de la Ley del Procedimiento Administrativo General, aprobado mediante Decreto Supremo 006-2026-JUS, bajo apercibimiento de rehacer el acto de notificación y notificarle[s] conforme al numeral 1 del artículo 20 del citado cuerpo normativo.»

### Domicilio procesal (2 días; no pide acuse)
«requerir a [PARTE(S)] para que, dentro del plazo de dos (2) días hábiles siguientes a la fecha en que reciba[n] la notificación en su domicilio procesal, señale[n] un correo electrónico autorizando recibir las notificaciones correspondientes por dicho medio.»

## Nota al pie 1 (primera página)
- La nota del Código va detrás de «Código de Protección y Defensa del Consumidor» en la apertura de HECHOS (R-184).
- **Solo** si la denuncia llegó derivada de otro órgano (MEMORANDUM, Documento de Traslado u Hoja de Traslado/Trámite) y el usuario entregó ese documento, la nota 1 va detrás de la fecha del escrito («Mediante el escrito del …¹») y dice: «Denuncia remitida a esta Comisión mediante [documento] [número] de fecha [fecha de emisión], recibida el [fecha de recepción en CC1].»
- Denuncia **desacumulada** de un expediente previo (caso particular): la forma de las plantillas, p. ej. «Denuncia desacumulada mediante Resolución 0155-2026/CC1-ST de fecha 29 de abril de 2026, recibida el 30 de abril de 2026.» En `_CASO.json`: `traslado.nota` con ese texto literal, más `documento`, `fecha` y `recibida`.
- Siempre «recibida», nunca «recepcionada». Siempre «de 2026», nunca «del 2026». Sin «N°».
- Si la denuncia se presentó directamente en CC1: **ninguna** nota sobre la denuncia. Prohibido «Denuncia presentada el …», «ante la Mesa de Partes …» o cualquier variante (R-167). La primera nota es la del Código.
- Nunca inventes número, fecha de emisión ni fecha de recibido: si el usuario no entregó el documento, no hay nota.

## Notas del traslado (parte resolutiva)
El párrafo «correr traslado …» lleva dos notas al pie: tras «Decreto Legislativo 807» (artículo 26) y tras «Ley 27444, Ley del Procedimiento Administrativo General» (artículo 223, «merituadas»). Ya vienen en todas las plantillas (`docs/notas_traslado.json`): no se borran, no se mueven y no se reescriben (R-173).
