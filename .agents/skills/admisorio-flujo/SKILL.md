---
name: admisorio-flujo
description: Redactar de principio a fin una resolución de admisión a trámite e imputación de cargos de la Comisión de Protección al Consumidor 1 de Indecopi (seguros) a partir de los PDF de un expediente, con los scripts del repositorio SystemHope-ResAdmis.
---

# Flujo del admisorio CC1

## Objetivo
Un `ADM <EXP> R<N>.docx` que el verificador declare **APTO** y `entregar` declare **ENTREGABLE**, sin un solo dato que no esté en el expediente.

## Instrucciones
1. **Reglas**: lee `AGENTS.md` completo y las skills `imputaciones` y `partes-y-notificacion`. Si el caso trae una solicitud de confidencialidad, lee también `confidencialidad`.
2. **Fecha**: si `scripts/config_sistema.py` dice «sin fijar», pregunta la fecha de emisión al instructor.
3. **Preparar**: `scripts/admisorio.py preparar <carpeta> --denunciados N --sujeto <clase> [--subtipo confidencialidad] [--rama X] [--contiene "frase"]`.
   - `N` es el número real de proveedores denunciados (1, 2, o 3 = 3 o más).
   - Las candidatas marcadas **APTA** (0 falsadores) van primero. Elige una APTA de la misma rama, el mismo número de denunciados y la misma clase de denunciante.
   - La carpeta física de la plantilla **no** indica el número de denunciados; el índice sí.
4. **Leer**: abre **cada** PNG de `_paginas/` (captura de la página completa) y llena su fila de `_LECTURA.md`: «Lo que vi» (contenido, sellos, firmas, resaltados) y «Formato que vi» (letra, negritas, subrayados, alineación, encabezado, pie). Las medidas exactas de formato de cada página están en `_FORMATO.md` (estructura del PDF; cero OCR). El texto seleccionable solo sirve para contrastar.
5. **Las 10 plantillas más similares (obligatorio)**: `_CASO.json` y `scripts/similares.py <carpeta>`; justifica cada una en `_SIMILARES.md` (imputaciones: norma, sujeto, conducta y fecha; hechos; partes). La base sale de esas 10.
6. **Anclar los datos** de cada documento (escrito de parte = fecha de su FIRMA DIGITAL; documento de Indecopi = fecha de emisión del texto):
   - denuncia: fecha y hechos;
   - subsanación o escritos complementarios: fecha;
   - memorándum o documento de traslado: número, fecha de emisión y fecha de recepción en CC1;
   - cédula: partes, vía de cada parte y número de resolución;
   - resolución de programación de audiencia de conciliación: es anterior y no se cita como hecho.
7. **Redactar el mapa** (`mapa.json`, en la carpeta del caso) sobre la plantilla y construir con `scripts/construir_admisorio.py --mapa`. Las claves son texto de la **plantilla**. El constructor aplica solo las reglas generales v3.1: quita notas huérfanas y renumera, lleva cada nota canónica a su ancla, pone a cada calificación la nota de SU norma, deja una tabulación tras cada llamada, quita dobles espacios y líneas en blanco de más, deja en negrita solo el rótulo de cada ordinal, quita el subrayado fuera del rótulo del requerimiento, fija la firma según `config/firmas.json` con «Firmado digitalmente por». Lo que imprime en «NORMALIZACION v3.1» es informativo.
7b. **Ver**: `scripts/admisorio.py previsualizar "<docx>" --contra "<plantilla>"` y mira **todas** las imágenes de `_vista/` en una vuelta (cada página junto a la de la plantilla).
8. **Entregar**: `scripts/admisorio.py entregar "<docx>" --recepcion DD/MM/AAAA`. Si algo falla, corrige y repite. No entregues sin ENTREGABLE.

## Estructura (orden fijo)
Encabezado:
- EXPEDIENTE
- DENUNCIANTE(S) (ALIAS)
- DENUNCIADO(S) (ALIAS)
- MATERIAS
- RESOLUCIÓN
- «Lima, [fecha]»

Secciones:
- **I. HECHOS**:
  - abre con «Mediante el escrito del …, subsanado mediante escrito del …, [tratativa] denunció a [alias] por presuntas infracciones a la Ley 29571, Código de Protección y Defensa del Consumidor (en adelante, Código), señalando lo siguiente:» (583 de 585 plantillas);
  - sigue con viñetas cronológicas en pasado; casi la mitad empieza con la fecha: «El 16 de agosto de 2024, …»;
  - cierra con «[Tratativa] solicitó, en calidad de medida correctiva, que … cumpla con: (i) …; y, (ii) …. Asimismo, requirió el reembolso de costos y costas del presente procedimiento.» (573 de 585).
- **II. DE LA ADMISIÓN A TRÁMITE**: un párrafo por imputación (skill `imputaciones`) y «En tanto la denuncia reúne los requisitos…, corresponde admitirla a trámite».
- **III. REQUERIMIENTO DE INFORMACIÓN**: lo que se pide a **cada** denunciado.
- **RESOLUCIÓN DE LA SECRETARÍA TÉCNICA**:
  1. PRIMERO: admitir, con las imputaciones en el mismo orden;
  2. SEGUNDO: medios probatorios;
  3. TERCERO: requisitos a **todos** los denunciados;
  4. CUARTO: traslado (fórmula R-155);
  5. QUINTO y siguientes: un requerimiento de información por denunciado;
  6. luego, en este orden: 450 UIT (art. 110); gastos (art. 39 del Decreto Legislativo 807); conciliación (art. 29); desistimiento;
  7. al final, un ordinal de notificación por vía.
- **Firma**: la de `config/firmas.json`.

## Qué NO se pone en HECHOS
- La palabra «denunciante».
- Calificaciones jurídicas o artículos.
- «Habría».
- Adjetivos del consumidor sobre el proveedor como si fueran hechos.
- Pretensiones fuera del párrafo de medida correctiva.
- Datos que no estén en el expediente.

## Formato
- Arial Narrow; 11 pt en el cuerpo y 8 pt en las notas.
- Negrita solo en el rótulo de cada ordinal, **también PRIMERO**; subrayado solo en el rótulo del requerimiento.
- Notas: una tabulación tras la llamada; sin líneas en blanco dentro; nunca dos llamadas juntas; la del Código tras «Consumidor»; la de competencia tras «en ejercicio de sus facultades»; cada calificación con la nota de su norma.
- Firma de cuatro líneas: «Firmado digitalmente por» / firmante / cargo / Comisión.
- Una sola numeración en la considerativa; nunca dos líneas en blanco seguidas.
- Interlineado sencillo, espaciado 0/0, justificado.
- Sangría izquierda de 1,0 cm y francesa de 1,0 cm.
- Márgenes de 2,5 cm arriba y abajo y 3,0 cm a los lados.
- Notas al pie con llamada en superíndice.
- Pie `M-CPC-01/03`.
- Sin resaltados.
- Fechas «de 2025» (nunca «del 2025»); números sin «N°».

## Restricciones
- Nunca OCR, nunca PDF, nunca Word por COM.
- Nunca copiar datos de la plantilla que no sean del caso (el constructor lo audita).
- Nunca publicar ni commitear el expediente.

## Ritmo (medido: cada decisión del modelo cuesta 45-70 s)
- Todo lo necesario está en `_FICHA.md`: comandos exactos con rutas absolutas, fechas de firma digital, proveedores (casilla y vía) y tabla de tipificación. **No** uses `-h`, **no** abras scripts ni JSON del repositorio, **no** hagas grep sobre el repositorio.
- Lectura visual con `_hojas/` (dos páginas por imagen): ábrelas todas en una sola vuelta y escribe `_LECTURA.md` una sola vez.
- `run_command` con `WaitMsBeforeAsync` 120000: los scripts terminan en segundos; nada de consultar tareas en bucle.
- Escribe `_CASO.json`, `_SIMILARES.md` y `mapa.json` completos de una vez; relee solo si un script lo pide.
- Objetivo: ≤ 25 decisiones por expediente.

## Añadir párrafos (imputaciones o hechos de más)
`mapa.json` admite `"insertar_despues": {"fragmento del párrafo ancla": [{"texto": "...", "nota": "numeral 88.1 del artículo 88"}]}`. Clona el párrafo ancla (sangría, numeración y formato) y lo coloca detrás; `nota` añade la nota normativa del corpus (normas en `docs/notas_normas.json`: «artículos 18 y 19», «artículo 1, numeral 1, literal b) y al artículo 2», «literal e) del artículo 47», «numeral 88.1 del artículo 88», …). Úsalo en la considerativa y en PRIMERO. Nunca inspecciones el XML ni el código para esto.

## Corregir un Word que entrega el instructor
Ese Word es la `plantilla` del `mapa.json`: `reemplazos` para el texto e `insertar_despues` para párrafos nuevos. Se conservan su numeración y sus notas. Nunca lo reescribas con ElementTree, python-docx ni `python -c` (Exp. 2835-2026: Word corrupto y numeración duplicada). El verificador rechaza numerales pegados («9.La», R-179) o duplicados («1. 1.», R-180).

## Revisión del Exp. 2889-2026 (v3.4, 24/09/2026)
- **Reclamos (R-208)**: toda imputación por el numeral 88.1 del artículo 88 (o el artículo 24) cierra el hecho, en la considerativa, con «; involucraría una presunta afectación a su derecho de recibir respuestas adecuadas a los reclamos formulados. Por consiguiente, corresponde calificar …». Nunca la frase de «expectativas». El resolutivo no la lleva. Las 109 plantillas con reclamos ya la traen (167 párrafos).
- **Traslado (R-209)**: «correr traslado de la denuncia del …[, subsanada mediante escrito del …] a …», con la cita del PRIMERO. Las 574 plantillas ya lo traen; el constructor sincroniza la cita con el PRIMERO del caso.
- **Modificación unilateral (R-210)**: subir la prima o cambiar las condiciones sin consentimiento expreso (aunque se hubiera informado que se mantendrían) es el «literal c) del artículo 56» (nunca «numeral 56.1»: R-143) («deber de protección contra los métodos comerciales coercitivos»), no idoneidad; sin «expectativas»; su nota, la de `docs/notas_normas.json`.
- Migraciones: `scripts/migraciones/afectacion_derecho_reclamos.py` y `traslado_denuncia.py` (idempotentes, solo el texto).

## Deber de información en la considerativa (v3.3, R-207)
Toda imputación por el artículo 1, numeral 1, literal b) y el artículo 2 cierra el hecho, en la considerativa, así:
«…consistente en que [SUJETO] no habría [HECHO, con fecha]; involucraría una presunta afectación al derecho de información de los consumidores. Por consiguiente, corresponde calificar el hecho materia de denuncia como una presunta infracción al deber de información, tipificado en el artículo 1, numeral 1, literal b) y al artículo 2 del Código.»
- Las 168 plantillas que imputan información ya la traen (232 párrafos, `scripts/migraciones/afectacion_derecho_informacion.py`).
- Si un `"parrafos"` del mapa la omite, el constructor la añade al sanear; el verificador rechaza la imputación que no la tenga.
- El resolutivo («Presunta infracción al artículo 1, numeral 1, literal b) y al artículo 2 de la Ley 29571, … en tanto …») **no** la lleva.

## Revisión del instructor del 24/09/2026 (v3.2)
Remesa de 11 admisorios corregidos y el Exp. 3092-2026 rehecho sobre su expediente. Lo que se generalizó:
- **El constructor sanea solo** (`scripts/sanear_admisorio.py`, lo llama al terminar):
  - añade una línea en blanco entre imputaciones contiguas, incluidas las de `insertar_despues`;
  - une los tramos del párrafo del traslado para que sus dos notas se anclen, y quita las notas sobrantes;
  - restituye la nota del Código y la de competencia si se pierden al reanclarse;
  - deja la nota de la norma imputada **solo en la primera imputación** de ese artículo (R-202);
  - renumera las notas sin colisiones.
- **Imputaciones** (skill `imputaciones`): mandan las plantillas por **sentido y finalidad**; la tabla es referencial. **Una por solicitud y por cobertura** (R-206). «La denunciante» (R-205), «compañía aseguradora» (R-201).
- **Hechos**: «adquirió» el seguro (R-204); nada valorativo como «únicamente» (R-203); solo lo que sustenta las imputaciones, sin perder el contexto.
- **Inadmisibilidad dejada sin efecto**: si el Word o el expediente la traen, se conservan el apartado «DE LA INADMISIBILIDAD» y el ordinal que la deja sin efecto.
- **Nota sobre la presentación de la denuncia en CC1** (prohibida, R-167): el constructor la quita y renumera.
- **Vista**: `previsualizar` usa ONLYOFFICE Document Builder si está instalado; si es LibreOffice, rotula «VISTA APROXIMADA».
- **Anclaje de fechas**: `entregar` reconoce la misma fecha escrita «10 de setiembre de 2026», «10 de septiembre de 2026» o «10/09/2026». `pdftotext` extrae en UTF-8; antes se perdían las tildes («falleci�»).
