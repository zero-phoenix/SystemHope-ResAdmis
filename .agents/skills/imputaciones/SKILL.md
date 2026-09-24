---
name: imputaciones
description: Redactar y verificar las imputaciones de cargos (considerativa y resolutivo PRIMERO) de un admisorio CC1 de Indecopi, eligiendo la norma de la tabla del instructor y la forma literal de las plantillas.
---

# Imputaciones de cargos (generado por scripts/analizar_imputaciones.py; no editar a mano)

## Reglas
- Solo normas de `docs/tabla_tipificacion.json`. Nunca art. 3. Art. 24 solo si el proveedor NO está regulado por el sistema financiero; si lo está, numeral 88.1 del art. 88.
- Cláusulas abusivas: SIEMPRE «numeral 49.1 del artículo 49 y al literal x) del artículo 50» (ineficacia absoluta) o «... del artículo 51» (ineficacia relativa).
- Documentos contractuales: a la FIRMA → literal e) del art. 47. DESPUÉS, cuando el consumidor los pide → art. 1, numeral 1, literal b) y art. 2.
- Solicitud de GESTIÓN mal atendida → idoneidad (arts. 18 y 19). Solicitud de INFORMACIÓN o copias → información. Si la misma carta tiene ambas, dos imputaciones separadas.
- Considerativa: «… considera que el hecho denunciado, consistente en que [HECHO en condicional]. Por consiguiente, corresponde calificar el hecho materia de denuncia como una presunta infracción al deber de …, tipificado en … del Código».
- Resolutivo: «Presunta infracción a [NORMA] de la Ley 29571, Código de Protección y Defensa del Consumidor, en tanto [SUJETO] habría(n) [CONDUCTA] [PRODUCTO] [FECHA/CIRCUNSTANCIA].» Una oración, una conducta.
- Sujeto (R-188, instructor 24/09/2026), idéntico en la considerativa y en el resolutivo:
  - aseguradora ÚNICA denunciada: «la compañía aseguradora» (nunca su razón social ni su alias);
  - dos o más denunciados, imputaciones separadas: la **razón social completa** de cada uno (también la aseguradora), nunca el alias;
  - conducta común a todos: «los proveedores denunciados» solo con EXACTAMENTE 2; con 3 o más, los dos nombres completos;
  - «el proveedor denunciado» solo si hay uno;
  - la denunciante o el denunciante: su **nombre completo** («la señora María Pérez Gómez»), nunca la tratativa corta de los hechos.
- Cada calificación termina con la llamada a la nota que transcribe SU norma (`docs/notas_normas.json`): el constructor la pone o la sustituye.
- Mismo orden, misma norma y mismo núcleo fáctico en considerativa y resolutivo. Nunca «y/o», nunca «inducción a error», nunca «N°».

## Por norma (forma canónica medida → úsala; variantes → no)

### art.18|art.19 (1261)
- Considerativa: «presunta infracción al deber de idoneidad, tipificado en …»
- Resolutivo: «Presunta infracción a los artículos 18 y 19 de la Ley 29571, Código de Protección y Defensa del Consumidor, en tanto …»
- Conductas típicas: no habría cumplido con brindar una; habría negado injustificadamente a otorgar; habría negado injustificadamente al denunciante; habría negado injustificadamente a la
- NO: «Presunta infracción de los artículos 18 y 19 de la Ley 29571, Código de Protección y Defensa del Consumidor, e» | «Presunta infracción al deber de idoneidad, tipificada en los artículos 18 y 19 de la Ley 29571, Código de Prot»

### art.1|art.2|lit.b|num.1 (218)
- Considerativa: «presunta infracción al deber de información, tipificado en …»
- Resolutivo: «Presunta infracción al artículo 1, numeral 1, literal b) y al artículo 2 de la Ley 29571, Código de Protección y Defensa del Consumidor, en tanto …»
- Conductas típicas: no habría cumplido con informar oportunamente; no habría cumplido con informar a; no habría cumplido con informar al; no habría cumplido con brindar información
- NO: «Presunta infracción al artículo 1, numeral 1, literal b), y al artículo 2 de la Ley 29571, Código de Protecció» | «Presunta infracción del artículo 1, numeral 1, literal b) y al artículo 2 de la Ley 29571, Código de Protecció»

### art.88|num.88.1 (167)
- Considerativa: «presunta infracción al numeral 88.1 del artículo 88 del Código, tipificado en …»
- Resolutivo: «Presunta infracción al numeral 88.1 del artículo 88 de la Ley 29571, Código de Protección y Defensa del Consumidor, en tanto …»
- Conductas típicas: habría brindado una respuesta inadecuada; no habría cumplido con brindar una; no habría brindado una respuesta adecuada; no habría remitido al denunciante una
- NO: «Presunta infracción al numeral 88.1 del artículo 88 del Código de Protección y Defensa del Consumidor, en tant» | «Presunta infracción al numeral 88.1 del artículo 88, de la Ley 29571, Código de Protección y Defensa del Consu»

### art.47|lit.e (63)
- Considerativa: «presunta infracción al deber de entregar a los usuarios copia de los contratos y demás documentación relacionada con dichos actos jurídicos, tipificado en …»
- Resolutivo: «Presunta infracción al literal e) del artículo 47 de la Ley 29571, Código de Protección y Defensa del Consumidor, en tanto …»
- Conductas típicas: no habría cumplido oportunamente con entregar; no habría cumplido con entregar oportunamente; no habría cumplido con entregar a; no habría cumplido con entregar al
- NO: «Presunta infracción al literal e) del artículo 47 del Código de la Ley 29571, Código de Protección y Defensa d» | «Presunta infracción del literal e) del artículo 47 de la Ley 29571, Código de Protección y Defensa del Consumi»

### art.56|lit.g (35)
- Considerativa: «presunta infracción al deber de protección contra los métodos comerciales coercitivos, tipificado en …»
- Resolutivo: «Presunta infracción al literal g) del artículo 56 de la Ley 29571, Código de Protección y Defensa del Consumidor, en tanto …»
- Conductas típicas: habría condicionado la atención de; habría exigido indebidamente al denunciante; habría requerido indebidamente a la; habría exigido indebidamente a la

### art.56|lit.b (26)
- Considerativa: «presunta infracción al deber de protección contra los métodos comerciales coercitivos, tipificado en …»
- Resolutivo: «Presunta infracción al literal b) del artículo 56 de la Ley 29571, Código de Protección y Defensa del Consumidor, en tanto …»
- Conductas típicas: habría contratado indebidamente a favor; habría atribuido indebidamente al denunciante; habría atribuido indebidamente la Póliza; habrían afiliado a la denunciante
- NO: «Presunta infracción al artículo 56, literal b), de la Ley 29571, Código de Protección y Defensa del Consumidor» | «Presunta infracción al literal b) del artículo 56de la Ley 29571, Código de Protección y Defensa del Consumido»

### art.38 (15)
- Considerativa: «presunta infracción al artículo 38 del Código, tipificado en …»
- Resolutivo: «Presunta infracción al artículo 38 de la Ley 29571, Código de Protección y Defensa del Consumidor, en tanto …»
- Conductas típicas: habría tenido un trato discriminatorio; habría discriminado a la denunciante; habría generado una condición discriminatoria; habría tenido un trato diferenciado
- NO: «Presunta infracción a la prohibición de discriminación, tipificada en el artículo 38 de la Ley 29571, Código d»

### art.56|lit.c (12)
- Considerativa: «presunta infracción al deber de protección contra los métodos comerciales coercitivos, tipificado en …»
- Resolutivo: «Presunta infracción al literal c) del artículo 56 de la Ley 29571, Código de Protección y Defensa del Consumidor, en tanto …»
- Conductas típicas: habría modificado unilateralmente las condiciones; habría modificado unilateralmente y sin; habría hecho disposición de los; habrían modificado unilateralmente la Póliza
- NO: «Presunta infracción al artículo 56, literal c) de la Ley 29571, Código de Protección y Defensa del Consumidor,» | «Presunta infracción al literal c) y d) del artículo 56 de la Ley 29571, Código de Protección y Defensa del Con»

### art.150 (11)
- Considerativa: «presunta infracción al uso del libro de reclamaciones, tipificado en …»
- Resolutivo: «Presunta infracción al artículo 150 de la Ley 29571, Código de Protección y Defensa del Consumidor, en tanto …»
- Conductas típicas: no habría tenido su libro de; no habría contado con un Libro; habría establecido una limitación inadecuada; no habría facilitado el acceso directo
- NO: «Presunta infracción al artículo 150 la Ley 29571, Código de Protección y Defensa del Consumidor, en tanto» | «Presunta infracción al artículo 150 de la Ley 29571, Código de Protección y Defensa del Consumidor, Código de »

### art.49|art.50|lit.*|num.49.1 (4)
- Considerativa: «presunta infracción a la disposición sobre cláusulas abusivas, tipificado en …»
- Resolutivo: «Presunta infracción al numeral 49.1 del artículo 49 y al literal a) del artículo 50 de la Ley 29571, Código de Protección y Defensa del Consumidor, en tanto …»
- Conductas típicas: habría incluido una cláusula abusiva; habría consignado en la Póliza
- NO: «Presunta infracción al numeral 49.1 del artículo 49 y al literal d) del artículo 50 de la Ley 29571, Código de» | «Presunta infracción al numeral 49.1 del artículo 49 y al literal b) del artículo 50 de la Ley 29571, Código de»

### art.61|art.62|lit.a (4)
- Considerativa: «presunta infracción al artículo 61 y el literal a) del artículo 62 del Código, tipificado en …»
- Resolutivo: «Presunta infracción al artículo 61 y al literal a) del artículo 62 de la Ley 29571, Código de Protección y Defensa del Consumidor, en tanto …»
- Conductas típicas: habría autorizado indebidamente que su; habría remitido indebidamente en octubre; habría remitido indebidamente el 5

### art.152 (3)
- Considerativa: «presunta infracción al artículo 152 del Código, tipificado en …»
- Resolutivo: «Presunta infracción al artículo 152 de la Ley 29571, Código de Protección y Defensa del Consumidor, en tanto …»
- Conductas típicas: habría negado en setiembre de; habría negado el acceso al; habría negado injustificadamente a entregar

### art.49|art.51|lit.*|num.49.1 (2)
- Considerativa: «presunta infracción al numeral 49.1 del artículo 49 y al literal a) y literal d) del artículo 51 del Código, tipificado en …»
- Resolutivo: «Presunta infracción al numeral 49.1 del artículo 49 y al literal a) y literal d) del artículo 51 de la Ley 29571, en tanto …»
- Conductas típicas: habría utilizado una cláusula abusiva

### art.58 (2)
- Considerativa: «presunta infracción a la protección contra los métodos comerciales agresivos o engañosos, tipificado en …»
- Resolutivo: «Presunta infracción al artículo 58 de la Ley 29571, Código de Protección y Defensa del Consumidor, en tanto …»
- Conductas típicas: habrían atribuido indebidamente la Póliza; habría atribuido indebidamente la Póliza

### art.56|lit.d (1)
- Considerativa: «presunta infracción al deber de protección contra los métodos comerciales coercitivos, tipificado en …»
- Resolutivo: «Presunta infracción al literal d) del artículo 56 de la Ley 29571, Código de Protección y Defensa del Consumidor, en tanto …»
- Conductas típicas: habría llenado de forma unilateral

### art.56|lit.e (1)
- Considerativa: «presunta infracción al deber de protección contra los métodos comerciales coercitivos, tipificado en …»
- Resolutivo: «Presunta infracción al literal e) del artículo 56 de la Ley 29571, Código de Protección y Defensa del Consumidor, en tanto …»
- Conductas típicas: habría establecido limitaciones injustificadas al

### art.58|lit.b (1)
- Considerativa: «presunta infracción al literal b) del artículo 58 del Código, tipificado en …»
- Resolutivo: «Presunta infracción al artículo 58, literal b), de la Ley 29571, Código de Protección y Defensa del Consumidor, en tanto …»
- Conductas típicas: habría desplegado una práctica comercial

### art.58|lit.b|num.58.1 (1)
- Considerativa: «presunta infracción al deber de información, tipificado en …»
- Resolutivo: «Presunta infracción al literal b) del numeral 58.1 del artículo 58 de la Ley 29571, Código de Protección y Defensa del Consumidor, en tanto …»
- Conductas típicas: habría cambiado la información originalmente

### art.58|lit.c (1)
- Considerativa: «presunta infracción al deber de protección contra [APELLIDO] métodos comerciales coercitivos, tipificado en …»
- Resolutivo: «Presunta infracción al literal c) del artículo 58 de la Ley 29571, Código de Protección y Defensa del Consumidor, en tanto …»
- Conductas típicas: habría realizado una práctica comercial

### art.58|lit.f (1)
- Considerativa: «presunta infracción al artículo 58, literal f) del Código, tipificado en …»
- Resolutivo: «Presunta infracción al artículo 58, literal f) de la Ley 29571, Código de Protección y Defensa del Consumidor, en tanto …»
- Conductas típicas: habría inducido indebidamente a la

Detalle completo, fundamentos y ejemplos: `docs/IMPUTACIONES_ANALITICO.md`.
