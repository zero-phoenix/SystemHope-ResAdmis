
> ⚠️ **NO ES LECTURA DE ARRANQUE.** Este archivo es el corpus de consulta dirigida.
> Para trabajar un admisorio basta con `AGENTS.md`, que es corto y manda. Aqui se viene a
> buscar **una** regla concreta cuando hace falta, no a leerlo entero antes de empezar.
> Leerlo completo en cada arranque es la razon de que el segundo admisorio tardara mas que
> el primero: la superficie de instrucciones crecio a 149 KB con R-103 repetida en 8 archivos.



# MATRIZ DE APRENDIZAJE Y REGLAS DE REDACCIÓN (ANTIGRAVITY)
Documento autogenerado para consolidar las instrucciones de "Lo que se debe hacer" (DOs) vs "Lo que NO se debe hacer" (DONTs) en la elaboración de resoluciones admisorias.

✅ LO QUE SE DEBE HACER (DOs)
Tipificación estricta de Falta de Información: Cuando se detecte una falta de información (ej. no entrega de constancia MTC, falta de respuesta a reconsideraciones), la imputación DEBE referirse exacta y literalmente a: "artículo 1, numeral 1, literal b) y al artículo 2 del Código".
Unificación de Sujetos Procesales (Notificaciones): Si dos o más sujetos (ej. denunciante y denunciado) van a ser notificados por la misma vía (ej. correo electrónico), se debe unificar el mandato en un único párrafo resolutivo utilizando conjugaciones en plural (ej. reciban, efectúen, notificarles).
Fidelidad a las Plantillas de Notificación:
Correo Electrónico: Plazo de dos (2) días hábiles para confirmar recepción. Citar el "artículo 20" (sin símbolo de grado °).
Casilla Electrónica: Plazo de cinco (5) días hábiles para confirmar acuse de recibo.
Domicilio Físico / Procesal: Plazo de dos (2) días hábiles para señalar un correo electrónico autorizando recibir notificaciones por dicho medio.
Respeto a la Estructura Documental: Mantener el formato íntegro del documento base (fuente Arial Narrow, tamaño 11, alineación justificada, sin resaltados residuales verdes, márgenes y viñetas romanas alineadas).
Control de Redundancia: Aplicar revisión de coherencia y congruencia evitando repetir palabras de transición como "Asimismo" en párrafos consecutivos de imputación.

❌ LO QUE NO SE DEBE HACER (DONTs)
PROHIBIDO IMPUTAR EL ARTÍCULO 24: Bajo ninguna circunstancia se debe imputar infracciones al artículo 24 del Código.
PROHIBIDO IMPUTAR INDUCCIÓN AL ERROR: Nunca se debe tipificar una conducta como "inducción al error". Siempre canalizar los problemas informativos a través del Artículo 1, numeral 1, literal b) y Artículo 2.
NO VULNERAR EL PRINCIPIO NON BIS IN IDEM: Está terminantemente prohibido imputar dos infracciones distintas por un mismo hecho (por ejemplo, la falta de entrega de un contrato o póliza corresponde solo al artículo 47 y NO a Idoneidad - artículos 18 y 19).
NO INVENTAR VÍAS DE NOTIFICACIÓN: Se debe analizar rigurosamente la cédula de notificación. Si la empresa (ej. Rímac) tiene consignado un correo electrónico en la cédula, no se le debe imponer una plantilla de Casilla Electrónica.
NO MODIFICAR TEXTOS TABULARES: Respetar los cuadros iniciales sin aplicar sombreados o alteraciones indebidas.
NO SOBRETIPIFICAR LA FALTA DE INFORMACIÓN EN SEGUROS: Si la denuncia alega que se rechazó la cobertura usando una cláusula de exclusión ambigua o poco precisa (ej. estado de ebriedad como sujeto pasivo), el hecho se subsume enteramente como una presunta infracción al deber de Idoneidad (Artículos 18° y 19°) por negativa injustificada de cobertura. No se debe tipificar doblemente como "falta de información".

📝 REGLAS ESTRICTAS DE ESTRUCTURA Y FORMATO (WORD)
Uso Obligatorio de Plantillas Base: NUNCA se debe generar un documento Word desde cero. Para conservar las imágenes del encabezado (Logo Indecopi a la izquierda, Firma digital a la derecha) y los formatos nativos, se debe abrir un modelo existente (ej. MODELO xxxx exp. ADM...docx), vaciar su contenido corporal (manteniendo Headers y Footers intactos) y luego inyectar el nuevo texto.
Cuerpo de Metadatos (Sin Tablas): Los datos iniciales (EXPEDIENTE :, DENUNCIANTE :, etc.) NO deben construirse como una tabla de Word. Deben usar sangría francesa (Hanging Indent de -1.48 pulgadas) y tabulación para alinear el valor a la derecha. Tanto la etiqueta del campo (ej. EXPEDIENTE) como el valor deben ir OBLIGATORIAMENTE en negrita.
Títulos Principales: Numerados en romanos, alineados a la izquierda y en negrita. Deben usar sangría francesa (Hanging indent).
Espaciado y Párrafos (¡MUY IMPORTANTE!): El documento es de interlineado simple (1.0) y SpaceBefore/SpaceAfter en 0 puntos. ¡CRÍTICO! NO SE DEBEN INSERTAR PÁRRAFOS EN BLANCO ENTRE ELEMENTOS DE UNA MISMA LISTA NI DEBAJO DE LOS TÍTULOS DE SECCIÓN. Solo se inserta una línea en blanco (un párrafo vacío) para separar grandes bloques procesales (ej. antes de pasar a un numeral romano nuevo, o para separar los puntos resolutivos PRIMERO, SEGUNDO, etc.). Dentro de la narración de los HECHOS, las viñetas (i), (ii), (iii) van totalmente pegadas sin saltos de línea entre sí, al igual que los subtítulos como 'Contra el Banco:'. Esto es esencial para que la estructura visual no se inflé desproporcionadamente.
Citas y Notas al Pie (¡EL SECRETO DE LAS 6 PÁGINAS!): Siempre que se invoque una norma, debe insertarse una nota al pie real de Microsoft Word (Footnote). La inyección técnica debe ser perfecta. La fuente de las notas al pie es estrictamente Arial tamaño 8.0, alineación Justificada. Un tamaño mayor (ej. 10.0) inflará el documento de 6 a 7 o más páginas, lo cual es inaceptable. Para aplicar formato de negrita a secciones específicas del texto de la nota al pie (ej. Títulos de normas), se debe procesar el texto e inyectarlo fraccionado usando la API de Microsoft Word (ej. modificando Font.Bold = True al Range de la nota) para que la jerarquía visual de la norma sea idéntica al original.
Pie de Página (Footer): Todas las páginas del documento llevan el código "M-CPC-01/03".
Fuentes Generales: El cuerpo del documento y la metadata usan estrictamente Arial Narrow tamaño 11, alineación Justificada (NUNCA usar Arial regular, ya que expande innecesariamente el ancho de las letras y aumenta el número de páginas).
Fechas: Siempre en minúsculas para los meses (ej. "31 de marzo de 2026").
Alineación de Texto: Estrictamente "Justificar" para todo el cuerpo. Fechas y firma van alineadas según corresponda.
Tipificación de Falta de Entrega de Estados de Cuenta (Bancos): Cuando se impute a una entidad financiera la omisión de remitir un estado de cuenta solicitado, la imputación correcta DEBE hacer referencia al artículo 152° de la Ley N° 26702, Ley General del Sistema Financiero y del Sistema de Seguros y Orgánica de la Superintendencia de Banca y Seguros, concordante con los artículos 18° y 19° del Código.
Redacción de HECHOS (Orden Cronológico): La sección de HECHOS NUNCA debe ser una mera copia del petitorio dividida por denunciados (evitar subtítulos como "Contra la Aseguradora:" o "Contra el Banco:"). Los hechos DEBEN redactarse como una narración cronológica unificada mediante viñetas correlativas (i), (ii), (iii), etc., entrelazando las acciones del consumidor frente a ambos proveedores en orden de tiempo.
Manejo de Declinatorias de Competencia (Nota al Pie): Cuando el expediente llega por una Declinatoria de Competencia de un Órgano Resolutivo Sumarísimo (OPS), el Documento de Traslado NO debe ocupar un párrafo principal en los Hechos ni en la Admisión. Se debe colocar elegantemente como una Nota al Pie anclada al primer párrafo de los Hechos (junto a la mención de la denuncia), con la fórmula: "Denuncia remitida a esta Comisión mediante DOCUMENTO DE TRASLADO N° [Número] de fecha [Fecha], recepcionada el [Fecha de recepción]."
Abreviaturas en Metadatos: En la sección de DENUNCIADOS, utilizar abreviaturas cortas y precisas entre paréntesis. Ej: PACÍFICO COMPAÑÍA DE SEGUROS Y REASEGUROS S.A. (PACÍFICO) y BANCO DE CRÉDITO DEL PERÚ S.A. (BANCO). No usar (LA ASEGURADORA) o (EL BANCO) si la plantilla/imagen indica lo contrario.
Numeración de Resolución: En la tabla de metadatos inicial, el número de resolución puede variar. Si la denuncia proviene de una declinatoria (que ya fue una Resolución 1 del OPS), o si se indica en el modelo, usar RESOLUCIÓN : 2.
Uso de Notas al Pie (Dispositivos Legales): La primera vez que se cite un dispositivo legal (ej. "Código de Protección y Defensa del Consumidor", "Ley General del Sistema Financiero") debe insertarse su nombre corto o sigla (ej. "en adelante, Código") y agregar de inmediato una Nota al Pie que contenga la sumilla de publicación y/o el texto íntegro del artículo aplicable, copiando el formato institucional.
Manejo del Encabezado Institucional: El bloque superior derecho que indica "SECRETARÍA TÉCNICA DE LA COMISIÓN..." NO debe insertarse manualmente en el cuerpo del documento. Este texto ya forma parte del Header (Encabezado) de la plantilla institucional de Indecopi. Tocarlo o reescribirlo duplica el membrete y desalinea el formato.
Alineación de Metadata (Cuadro Resumen Inicial): No usar espacios ni múltiples 	 sin formato. Para lograr la alineación idéntica a la plantilla, la metadata (EXPEDIENTE, DENUNCIANTE, etc.) debe usar sangría izquierda (left indent) de 1.48" y sangría de primera línea (first line indent) de -1.48", estableciendo dos tabulaciones precisas: una a 1.18" (para los dos puntos :) y otra a 1.48" (para el inicio del texto de la variable). Así las líneas envueltas (wrapped text) caen perfectamente alineadas bajo la primera letra de la variable.
Sangría Colgante (Hanging Indent) en Viñetas y Numerales: Para garantizar que el texto de un inciso (ej. "i)", "1.") comience exacto y el texto envuelto (segunda línea en adelante) se alinee a la perfección con la primera palabra, debe asignarse un tab_stop explícito en la misma posición que el left_indent. De lo contrario, la primera línea saltará a una tabulación por defecto distinta a la del texto envuelto, rompiendo la estructura de bloque de Indecopi.
Redacción Técnica de la PARTE RESOLUTIVA (PRIMERO): En el primer resolutivo de la admisión (PRIMERO), el párrafo introductorio SOLO debe indicar de manera general "en atención a lo siguiente:". Luego, CADA viñeta (i), (ii)... DEBE empezar invocando textualmente: "Presunta infracción a [NORMA], en tanto [PROVEEDOR] habría [HECHO]". Por ejemplo: "Presunta infracción a los artículos 18° y 19° de la Ley N° 29571... en tanto el Banco habría efectuado cobros no autorizados". NO hacer un resumen, sino citar "Presunta infracción a..." explícitamente.
Redacción Técnica de REQUERIMIENTOS (SEXTO y SÉTIMO): Los requerimientos de información específicos a los denunciados (ej. "presentar contrato", "remitir grabaciones") NO deben redactarse de corrido en un solo bloque de texto continuo. Deben desglosarse forzosamente en viñetas (i), (ii), (iii)... con sangría colgante, igual que la sección de Hechos, para facilitar su lectura y control.
Redacción de Medidas Correctivas y Costas/Costos: Las medidas correctivas NO deben redactarse de corrido. Deben desglosarse en incisos romanos (i), (ii), (iii)... dentro del párrafo. Al final del bloque, se debe añadir SIEMPRE la mención expresa a costas y costos. **El sentido de la mención no es fijo: se toma del petitorio del escrito de denuncia.** Si el denunciante los solicitó: "Asimismo, solicitó el reembolso de los costos y costas del presente procedimiento."; si no lo hizo: "Asimismo, no requirió de manera expresa el reembolso de costos y costas del presente procedimiento.". Fijar una de las dos formas como plantilla hace que el motor afirme un petitorio que el expediente puede contradecir.
Estructura PARTE CONSIDERATIVA - ADMISIÓN A TRÁMITE: ¡CRÍTICO! A diferencia de los Hechos o Requerimientos, las imputaciones de la Admisión a Trámite NUNCA deben redactarse como una lista con viñetas bajo un solo numeral introductorio. CADA IMPUTACIÓN debe constituir un párrafo principal numerado independientemente (ej. numeral 3, 4, 5, 6, etc.). Todos esos párrafos deben usar la fórmula: "Asimismo, la Secretaría Técnica..., considera que el hecho denunciado, consistente en que [PROVEEDOR] [ACCIÓN] ; involucraría una presunta afectación a sus expectativas...".
Notas al Pie Mixtas (Facultades de la Secretaría): La primera nota al pie de la sección "De la Admisión a Trámite" que sustente el "ejercicio de sus facultades", DEBE incluir obligatoriamente dos normas conjuntas: Primero, el Artículo 105° del Código (Ley N° 29571) y, segundo, el Artículo 27° de la Ley de Organización y Funciones del Indecopi (Ley N° 1033), copiando estrictamente la jurisprudencia de las plantillas.
Tipificación de Afiliación sin Autorización (Métodos Coercitivos): Cuando un proveedor atribuye indebidamente la contratación de una póliza o servicio sin autorización expresa, la imputación NO DEBE tipificarse genéricamente como Idoneidad (Artículos 18° y 19°). Corresponde su tipificación estricta como presunta infracción al deber de protección contra los métodos comerciales coercitivos, tipificado en el literal b) del artículo 56° del Código.
Tipificación de Envío de Información a Correo Erróneo (Deber de Información): Cuando el proveedor remite información de un servicio a un correo electrónico que no corresponde al denunciante, la conducta NO DEBE tipificarse como Idoneidad. Corresponde su tipificación estricta como presunta infracción al deber de información, tipificado en el artículo 1°, numeral 1, literal b) y al artículo 2° del Código.
Conectores Lógicos en Admisión a Trámite: Al enumerar los distintos hechos denunciados en párrafos numerados consecutivos (ej. numerales 3, 4, 5, 6...), NO SE DEBE repetir monótonamente el conector "Asimismo". Se debe variar sistemáticamente la transición inicial usando conectores correlativos como "Además,", "Adicionalmente,", "Así también," y "Asimismo," para mantener la fluidez y calidad técnica de la resolución.
Boilerplate de Idoneidad Exclusivo: La frase "involucraría una presunta afectación a sus expectativas, quien no habría encontrado una correspondencia entre lo que esperaba recibir de parte del proveedor y lo que realmente recibió" es EXCLUSIVA para imputaciones de Idoneidad (Arts. 18° y 19°). Para infracciones al Deber de Información (Arts. 1° y 2°) o Métodos Coercitivos (Art. 56°), esta frase DEBE omitirse obligatoriamente, pasando directamente del hecho narrado a la conclusión: "Por consiguiente, corresponde calificar el hecho...".
Requerimientos Específicos en Sección III: Los requerimientos específicos de información a los proveedores no solo van en la parte resolutiva, sino que deben detallarse expresamente en la parte considerativa, dentro de la Sección III. REQUERIMIENTO DE INFORMACIÓN, desglosados por proveedor (ej. A Pacífico: subrayado, seguido de los incisos requeridos).
Unificación del PRIMERO Resolutivo: El punto PRIMERO de la Resolución de la Secretaría Técnica (donde se admite a trámite) debe unificar a TODOS los proveedores denunciados en un solo párrafo introductorio (ej. "admitir a trámite... contra [Proveedor 1] y [Proveedor 2], por lo siguiente:"), listando a continuación todas las imputaciones de ambos proveedores en viñetas correlativas, identificando al responsable en el texto de cada una ("en tanto la aseguradora...", "en tanto el banco...").
Tipificación de Solicitud Histórica de Documentos: Si el consumidor solicita documentos históricos (ej. un estado de cuenta de hace años) y el proveedor no los remite, se tipifica como infracción al Deber de Información (Art. 1°, numeral 1, literal b y Art. 2°), NO como Idoneidad ni como la obligación sectorial de remisión periódica mensual.
Formato Estricto de Viñetas Resolutivas: En la sección RESOLUCIÓN (punto PRIMERO), las viñetas de las imputaciones admitidas NO deben empezar simplemente con la norma abreviada ("A los artículos..."). Deben empezar obligatoriamente con la frase formal y la norma legal completa: "Presunta infracción a [norma] de la Ley N° 29571, Código de Protección y Defensa del Consumidor, en tanto [Nombre Completo del Proveedor]...".
Orden Lógico de Viñetas Resolutivas: En el punto PRIMERO, las imputaciones deben agruparse por NORMA INFRINGIDA, no cronológicamente. Primero todas las imputaciones por Idoneidad (Arts. 18° y 19°), luego Métodos Coercitivos (Art. 56°), y finalmente Deber de Información (Arts. 1° y 2°).
Precisión Resolutiva en SEGUNDO y CUARTO: El punto SEGUNDO (medios probatorios) debe mencionar las fechas exactas del escrito de denuncia y su subsanación. El punto CUARTO (traslado) se rige obligatoria y exclusivamente por la fórmula literal canónica R-155 (traslado de la presente resolución con apercibimiento de rebeldía y cita al artículo 223° del TUO de la LPAG, quedando derogadas las fórmulas históricas anteriores).
El Filtro MYPE (Inclusión Obligatoria): NUNCA se debe eliminar la viñeta que requiere la acreditación de micro/pequeña empresa (MYPE) en el requerimiento general (TERCERO), sin importar si los denunciados son manifiestamente grandes corporaciones (Bancos, Aseguradoras). Es un requerimiento de inclusión obligatoria y universal por estricto rigor procedimental ("en caso califique...").
Reiteración de Requerimientos Específicos: Los requerimientos específicos detallados para cada proveedor en la Sección III NO se resumen con una referencia cruzada en la parte resolutiva (PROHIBIDO usar "cumpla con lo requerido en el numeral 11"). En los numerales respectivos de la Resolución (ej. QUINTO y SEXTO), se DEBEN volver a transcribir literalmente todas las viñetas del requerimiento para cada proveedor.
Formato de Notas al Pie (Alineación y Espaciado): Las notas al pie deben tener una alineación de sangría francesa (Hanging Indent) perfecta. El número de la nota debe estar alineado al margen izquierdo (LeftIndent=1cm, FirstLineIndent=-1cm), seguido de una tabulación explícita (	) antes del texto. Todas las líneas del párrafo de la nota deben alinearse exactamente a 1 cm. Además, debe existir un espacio en blanco (SpaceAfter = 10pt) entre cada nota al pie para separar visualmente las referencias.
Alineación Multi-línea en Notas al Pie (Anti-Stretching / Soft Returns): Para evitar que los párrafos internos pierdan la sangría francesa, se DEBEN usar saltos de línea manuales (). SIN EMBARGO, como la nota al pie está justificada, un salto manual estirará horriblemente las palabras de esa línea. Para evitar este estiramiento (Error de Justificación), OBLIGATORIAMENTE se debe insertar una tabulación antes del salto de línea (	). El tabulador absorbe el espacio sobrante y mantiene las palabras juntas sin alterar el bloque visual.
Actualización Normativa LPAG: En el cuerpo del texto y en las notas al pie, la referencia al TUO de la Ley del Procedimiento Administrativo General (LPAG) debe estar actualizada al año del expediente (2026): Decreto Supremo N° 006-2026-JUS, publicado el 30 de abril de 2026. (Reemplaza a la versión derogada 004-2019-JUS).

39. NUNCA EXTRAPOLAR SANGRIAS DE NUMERACIONES A TODO EL DOCUMENTO
Contexto
Al automatizar los modelos, es tentador aplicar un único valor de sangría (left_indent y hanging_indent) a todos los sub-numerales (por ejemplo, los incisos (i), (ii), (iii)) independientemente de en qué parte del documento se encuentren.
El Error (Extrapolación de estilo)
En resoluciones de Indecopi, la sangría de los incisos varía dependiendo de la sección lógica:
En la sección HECHOS: Los incisos (i), (ii), etc., están anidados bajo un número (ej: 1. Mediante la denuncia...). Por lo tanto, tienen mayor sangría. (Típicamente: left_indent = 2 cm, hanging_indent = 1 cm. La viñeta comienza a 1 cm del margen y el texto a 2 cm).
En la sección RESOLUCIÓN (PRIMERO, TERCERO, etc.): Los incisos (i), (ii) NO están anidados bajo un numeral arábigo, sino directamente bajo la palabra "PRIMERO:" o "TERCERO:". Por lo tanto, tienen menor sangría. (Típicamente: left_indent = 1 cm, hanging_indent = 1 cm. La viñeta comienza a 0 cm del margen y el texto a 1 cm).
La Regla Definitiva
Analiza el contexto estructural: Al aplicar estilos de viñetas, distingue siempre si estás en el bloque de HECHOS o en los bloques resolutivos (PRIMERO, TERCERO).
HECHOS: Aplica left_indent = Inches(0.79) (2cm) y first_line_indent = Inches(-0.39) (-1cm).
RESOLUCIÓN (PRIMERO, SEGUNDO, TERCERO...): Aplica left_indent = Inches(0.39) (1cm) y first_line_indent = Inches(-0.39) (-1cm).
Verificación Visual: En la sección resolutiva, la viñeta (i) o (v) debe quedar alineada casi al ras del margen izquierdo (0 cm), justo debajo de la palabra "PRIMERO:" o "TERCERO:".

36. SIEMPRE EXIGIR LA ACREDITACIÓN MYPE A TODOS LOS PROVEEDORES
Contexto
En el requerimiento de información al denunciado (usualmente en el TERCERO), existe un inciso que pide al proveedor presentar documentos que acrediten su condición de micro o pequeña empresa.
La Regla Definitiva
NUNCA elimines este inciso, sin importar cuán grande sea la empresa denunciada (por ejemplo, Bancos, Aseguradoras, Telecomunicaciones).
A todos los proveedores denunciados se les debe requerir esta información formalmente para que la Comisión pueda meritar la documentación conforme al artículo 110° del Código.

40. EXCEPCIÓN DE SUCESIÓN INTESTADA EN CASOS DE SOAT
Contexto
Cuando se trata de seguros SOAT por fallecimiento, la ley ya establece quiénes son los beneficiarios directos.
La Regla Definitiva
En denuncias sobre cobertura de SOAT por fallecimiento, NO es necesario que la Sucesión Intestada sea la denunciante. El beneficiario (por ejemplo, los padres) se presenta a título personal como denunciante.
Cuando en otros casos sí corresponda usar una sucesión, siempre debe denominarse formalmente como 'Sucesión Intestada', quedando estrictamente prohibido usar el término abreviado 'la Sucesión'.

41. NO CORTAR NOTAS AL PIE A LA MITAD DE UNA ORACIÓN
La Regla Definitiva
Al aplicar la regla del salto de línea (\t\x0b) en notas al pie, nunca debes usarlo para cortar arbitrariamente una oración (por ejemplo, después de una coma). El texto de un solo párrafo debe fluir y hacer word wrap naturalmente. Solo usa el salto forzado para separar bloques de texto o artículos distintos dentro de una misma nota al pie.

42. TAMAÑO DE INICIALES AL FINAL DEL DOCUMENTO
La Regla Definitiva
Las iniciales del proyectista y revisor (ejemplo: LGP/JCQ) ubicadas al final de la resolución, siempre deben ir en tamaño 8, no en tamaño 11.

43. REDACCIÓN DE HECHOS: OBJETIVA, TÉCNICA Y COMO ESPEJO DE LA DENUNCIA
Contexto
La sección de HECHOS no es un resumen libre ni una interpretación deductiva de los anexos. Debe reflejar técnica y objetivamente lo que el denunciante plasmó en su escrito de denuncia.
La Regla Definitiva
Tono frío y objetivo: NUNCA usar adverbios o adjetivos emocionales (ej. 'lamentablemente falleció'). Limitarse a los hechos concretos: 'ocasionó el fallecimiento'.
Precisión documental: Extraer del escrito de denuncia y mencionar explícitamente los números de pólizas, contratos, y los medios probatorios exactos con los que el denunciante acredita su dicho (ej. 'hecho documentado mediante el acta de defunción y el atestado policial correspondientes').
Espejo del escrito: Si el escrito de denuncia detalla los documentos exactos que presentó al proveedor en su reclamo previo, lístalos tal cual (ej. 'entregando el acta de defunción, el atestado policial y la documentación adicional exigida').
No inventar ni anticipar defensas: En la narración de hechos, relata el rechazo del proveedor tal como lo sufre el denunciante ('denegó el reconocimiento y pago de la cobertura solicitados'). No extraigas proactivamente los argumentos técnicos del proveedor desde sus cartas de rechazo (ej. 'alegando que no era ocupante sino que iba en moto') a menos que el denunciante base su relato expresamente en rebatir eso. Cíñete al escrito de denuncia.
Formalidad en montos: Escribir los conceptos formalmente (ej. 'cuatro (4) Unidades Impositivas Tributarias' en lugar de '4 UIT').

44. FORMATO DE PÁRRAFO ÚNICO PARA IMPUTACIÓN ÚNICA
Contexto
Cuando se admite a trámite por un solo hecho infractor, no se deben usar listas ni incisos (i).
La Regla Definitiva
Si hay una sola presunta infracción, el artículo PRIMERO de la Resolución de la Secretaría Técnica debe redactarse de corrido en un solo párrafo. Ejemplo:
PRIMERO: admitir a trámite la denuncia del [fecha] interpuesta por [Denunciante] contra [Denunciado], por presunta infracción a los artículos 18° y 19°..., en tanto [hecho infractor].

45. REDACCIÓN DEL HECHO INFRACTOR (ESPECIFICIDAD Y NO REDUNDANCIA)
Contexto
La imputación debe ser precisa, elegante y evitar repeticiones innecesarias en el mismo párrafo.
La Regla Definitiva
Evitar redundancia: Si ya se mencionó el nombre completo del denunciado al inicio del párrafo (ej. La Positiva Seguros y Reaseguros S.A.A.), referirse a él a continuación de forma genérica (ej. 'la compañía aseguradora', 'el banco') en lugar de repetir su nombre legal.
Especificidad Extrema: Detallar exactamente el producto, número de póliza/contrato y los conceptos reclamados. No basta con 'cobertura del SOAT'; debe ser 'la cobertura de fallecimiento y gastos de sepelio de la Póliza 140733548 del Seguro Obligatorio de Accidente de Tránsito'.
Neutralidad: Usar lenguaje condicional neutro ('se habría negado a otorgar') y evitar pre-calificar la conducta ('habría denegado de manera injustificada').

46. TRATAMIENTO DE REPRESENTANTES DE PERSONAS NATURALES
Contexto
Es común confundir al representante legal con el titular de los derechos (denunciante).
La Regla Definitiva
Si el denunciante es una Persona Natural pero presenta su escrito a través de un representante, NUNCA se menciona al representante en el texto de la resolución (ni en Hechos, ni en Análisis, ni en el Resolutivo). Todos los actos se atribuyen directamente al denunciante titular. Solo se menciona explícitamente a un representante cuando el denunciante es una Persona Jurídica.

47. REQUERIMIENTOS DE INFORMACIÓN ESPECÍFICOS Y ESTRATÉGICOS (NO GENÉRICOS)
Contexto
La sección de Requerimiento de Información (tanto en el numeral de la parte considerativa como en el artículo resolutivo respectivo, usualmente QUINTO) tiene como fin acopiar las pruebas exactas para resolver el caso. Fórmulas genéricas como 'presentar un informe detallado' son insuficientes y evidencian falta de análisis.
La Regla Definitiva
Al requerir información al proveedor denunciado, la redacción debe ser quirúrgica y apuntar a los hechos controvertidos:
Evitar redundancia del nombre: Referirse al denunciado como 'el proveedor denunciado' (si el nombre ya es obvio por el contexto).
Exigir el contrato base: Requerir siempre el documento que sustenta la relación de consumo de manera específica (ej. 'presentar una copia completa, legible y debidamente suscrita de la Póliza 140733548 del Seguro Obligatorio de Accidente de Tránsito').
Exigir la prueba de descargo del hecho infractor: Requerir los medios probatorios que justifiquen su accionar (ej. 'presentar los medios probatorios que acrediten que la negativa de otorgamiento de cobertura fue justificada').
Cláusula obligatoria de comunicaciones: SIEMPRE incluir como último inciso: 'presentar todas las comunicaciones cursadas con la parte denunciante en virtud de los hechos materia de denuncia'.
Especificidad en grabaciones: Si el denunciante alega en su escrito que hubo una contratación telefónica, entrevista poligráfica por videollamada, u otro contacto grabado, el requerimiento de comunicaciones debe exigir expresamente el archivo de audio/video de dicha comunicación.

48. REFERENCIA AL DENUNCIADO: COMPAÑÍA ASEGURADORA VS PROVEEDOR DENUNCIADO
Contexto
Para evitar redundancias en la redacción y mantener un nivel técnico superior, es necesario utilizar pronombres o sustantivos genéricos que identifiquen claramente la naturaleza del infractor.
La Regla Definitiva
Cuando el denunciado es una empresa de seguros (ej. La Positiva, Pacífico Seguros, Mapfre, Rimac), el término genérico a utilizar a lo largo de todo el documento (para no repetir su nombre legal) será estrictamente 'la compañía aseguradora'. Solo cuando la empresa pertenezca a otro rubro (colegios, tiendas, aerolíneas, etc.) se utilizará el término general 'el proveedor denunciado'.

49. REDACCIÓN TÉCNICA Y ESTRUCTURACIÓN LÓGICA DE HECHOS Y PETITORIO
Esta regla rige el estilo de redacción microscópico y la formulación técnica de la resolución:
Evitar Marcas Comerciales (Aplicativos): Para mantener la formalidad técnica, se deben omitir los nombres comerciales de los aplicativos en la medida de lo posible. Por ejemplo, en lugar de decir 'ZOOM', usar 'plataforma virtual de videoconferencia'.
Definición Rigurosa de Términos: Queda estrictamente prohibido usar fórmulas perezosas como 'la referida póliza' o 'el citado contrato' en los párrafos subsiguientes o en las medidas correctivas. Se debe definir el término anticipadamente usando '(en adelante, Seguro de Vida)' o similar, y emplear EXCLUSIVAMENTE ese término definido en el resto de la resolución.
Secuencia Cronológica Completa: No se debe omitir ningún hito relevante narrado en la denuncia. Si el denunciante señala que acudió a una audiencia de conciliación previa en Indecopi (ej. SBC) y no hubo acuerdo, esto debe redactarse como un inciso independiente (usualmente el último de los hechos).
Verbos Rectores en Medidas Correctivas: Al redactar lo solicitado como medida correctiva, después de la frase 'cumpla con', se deben usar verbos en infinitivo para cada acción exigida. Ej: 'cumpla con realizar la resolución total... y, consecuentemente, otorgar la devolución...'.
Precisión Jurídica: Se debe depurar el lenguaje del consumidor hacia términos jurídicos exactos. Por ejemplo, si el denunciante pide la 'cancelación' de un contrato por un incumplimiento, el término correcto a usar es 'resolución'. Asimismo, los aportes son 'aportes del pago de primas' y se solicita el 'reembolso de costos y costas'.

50. REGLA SUPREMA: IMPUTACIÓN ÚNICA POR HECHO (MÉTODOS ENGAÑOSOS VS IDONEIDAD)
Esta regla es inviolable y corrige un error grave de tipificación:
Prohibición de Doble Imputación: NUNCA se deben imputar dos presuntas infracciones distintas (ej. falta de idoneidad y falta de deber de información) sobre un mismo y único hecho denunciado.
Tipificación Específica para Contrataciones Engañosas: Cuando el hecho consista en que el proveedor, al momento de la contratación, ofreció verbalmente o promocionó un servicio con ciertas condiciones favorables (ej. sin plazo mínimo, sin penalidades) pero el contrato real difiere de ello imponiendo obligaciones no pactadas, la tipificación correcta y ÚNICA es:
'presunta infracción al deber de protección contra los métodos comerciales agresivos o engañosos, tipificado en literal b) del artículo 58 del Código'.
Ortografía y Tildación: Cuidar escrupulosamente las tildes obligatorias en nombres propios, términos jurídicos y palabras esdrújulas (ej. Pacífico, Código, artículo, compañía, póliza, etc.).

51. PRECISIÓN ESTRICTA AL INVOCAR EL ARTÍCULO 58 DEL CÓDIGO (NO CONFUNDIR CON ART. 56)
Contexto
Es un error gravísimo confundir el contenido de los literales del artículo 56 (Métodos coercitivos) con el artículo 58 (Métodos agresivos o engañosos) del Código, ya que ambos tienen un literal b).
La Regla Definitiva
Cuando se impute 'presunta infracción al deber de protección contra los métodos comerciales agresivos o engañosos, tipificado en literal b) del artículo 58 del Código' por modificar lo ofrecido inicialmente, el contenido de la nota al pie debe ser ESTRICTAMENTE el siguiente:
Artículo: Artículo 58.- Definición y alcances
Texto literal b): 'El cambio de la información originalmente proporcionada al consumidor al momento de celebrarse la contratación, sin el consentimiento expreso e informado del consumidor.'
Queda ESTRICTAMENTE PROHIBIDO citar como literal b) del Art. 58 el texto 'Obligar al consumidor a asumir prestaciones que no ha pactado...', ya que ese texto pertenece al literal b) del Artículo 56 (Métodos coercitivos).
Se debe mantener las tildes precisas (Código, Capítulo, Definición) y usar exactamente la estructura de la sumilla 'LEY 29571, CÓDIGO DE PROTECCIÓN Y DEFENSA DEL CONSUMIDOR, publicado el 2 de setiembre de 2010 y modificado por Decreto Legislativo N° 1308'.

52. REQUERIMIENTO DE INFORMACIÓN: FORMATO DE PÁRRAFO ÚNICO, VERBOS EN INFINITIVO Y HECHOS FÁCTICOS SIN MENCIÓN A DEBERES
Contexto
El apartado de requerimiento de información debe ser lo más técnico posible, enfocado estrictamente en la evidencia física o documental relacionada al hecho denunciado, sin calificar legalmente el pedido mediante la mención a 'deberes'.
La Regla Definitiva
Un solo denunciado: Cuando solo hay una empresa denunciada, NO se debe separar en una nueva línea con subrayado (ej. 'A Pacífico: (i)...'). Debe continuarse en el mismo párrafo de forma fluida: '...cumpla con lo siguiente: (i) presentar...'.
Verbos en infinitivo: Todos los requerimientos probatorios deben empezar con verbos en infinitivo (ej. presentar, exhibir), NUNCA en subjuntivo (ej. presente, exhiba).
Prohibición de mencionar deberes normativos: NUNCA se debe solicitar información mencionando los deberes normativos (ej. 'medios probatorios que acrediten haber cumplido con su deber de información').
Requerimiento estrictamente fáctico: El pedido debe atarse únicamente al hecho controvertido. Por ejemplo, en vez de mencionar el deber, solicitar 'medios probatorios que acrediten que no cambió la información originalmente proporcionada al consumidor al momento de celebrarse la contratación de la Póliza...'.
Extracción de la imagen: Deben usarse los requerimientos idénticos a los señalados en la plantilla del usuario para el caso análogo, sin inventar pedidos de audios/videos si no están en su plantilla específica para este tipo de escenarios de pólizas.

53. FORMATO COMPACTO DE LOS REQUERIMIENTOS EN LA PARTE RESOLUTIVA (SIN LÍNEAS EN BLANCO)
Contexto
Los incisos listados en el requerimiento (ej. TERCERO) no deben estar separados por saltos de línea (párrafos en blanco). Deben ir uno debajo del otro de manera compacta para reflejar el formato estricto y limpio del modelo.
La Regla Definitiva
Sin separaciones excesivas: Nunca insertar líneas en blanco entre los numerales (i), (ii), (iii), (iv) y (v) en el apartado donde se listan los requerimientos al proveedor denunciado.
El enlace final 'y,': En caso de haber cinco incisos (hasta el v que es MYPE), el enlace 'y,' se coloca en el inciso (iii) previo a solicitar el domicilio procesal (iv). Ej: '(iii) consignar el Número de Registro Único de Contribuyentes (RUC); y,'
Tildes estrictas en el proveedor: Asegurarse SIEMPRE de colocar las tildes en los nombres de las empresas dentro de la resolutiva, ej. 'Pacífico Compañía...'.

54. ESTRUCTURA Y FORMATO ESTRICTO PARA ADMISORIOS DE LA COMISIÓN (CC1) VERSUS ORPS (PS1)
Contexto
Se cometió un error grave al redactar un admisorio de la Comisión de Protección al Consumidor 1 (CC1) utilizando la estructura de un Órgano Resolutivo de Procedimientos Sumarísimos (ORPS), y se omitieron las abreviaturas en el encabezado y los pies de página obligatorios.
La Regla Definitiva
Identificación de la Autoridad: SIEMPRE guiarse por la Resolución 1 (el requerimiento previo) para determinar si el caso es CC1 o PS1. Nunca confiarse ciegamente en el cargo de ingreso, ya que puede tener errores de derivación.
Encabezado CC1: Debe decir SECRETARÍA TÉCNICA DE LA / COMISIÓN DE PROTECCIÓN AL CONSUMIDOR 1 / SEDE CENTRAL alineado a la derecha.
Bloque de Datos (CC1): Las abreviaturas de las partes se definen en el mismo encabezado entre paréntesis. Ej: DENUNCIANTE : EFRAÍN CORONEL QUISPE (SEÑOR CORONEL). DENUNCIADO : LA POSITIVA SEGUROS Y REASEGUROS S.A.A. (LA POSITIVA). La materia debe ser ADMISIÓN A TRÁMITE / REQUERIMIENTO DE INFORMACIÓN.
Estructura del Cuerpo (CC1): NO usar VISTOS ni CONSIDERANDO. Se debe estructurar con números romanos y arábigos: I. HECHOS, 1. Mediante la denuncia... señalando lo siguiente:, (i)... (ii)..., 2. El señor X solicitó..., II. DE LA ADMISIÓN A TRÁMITE DE LA DENUNCIA, 3. La Secretaría Técnica... considera que el hecho...
Pies de Página Obligatorios en la primera página (CC1):
Pie 1 (Denuncia): Denuncia remitida a esta Comisión mediante DOCUMENTO DE TRASLADO N°... (extraer de la Res 1).
Pie 2 (Código): Publicado el 2 de setiembre del 2010 en el Diario Oficial El Peruano, vigente desde el 2 de octubre del 2010 y modificado por Decreto Legislativo 1308.
Pie 3 (Facultades de la Secretaría Técnica): LEY N° 29571, CÓDIGO DE PROTECCIÓN Y DEFENSA DEL CONSUMIDOR, publicado el 2 de setiembre de 2010 y modificado por Decreto Legislativo N° 1308. Artículo 105.- Autoridad competente.

55. REGLA SUPREMA DE ARQUITECTURA DE CÓDIGO Y FORMATO ESTRICTO (SPACING Y FUENTES)
Contexto
Al cambiar de librería a win32com para soportar pies de página complejos, se abandonó la arquitectura modular de funciones (ej. add_paragraph, add_run) que garantizaba el control absoluto del espaciado (SpaceAfter=0, LineSpacing=1.0) y tipografía, resultando en un documento visualmente deformado por los estilos por defecto de Word.
La Regla Definitiva
Nunca abandonar la arquitectura modular de control de formato: Toda generación de documentos, independientemente de la librería usada (python-docx o win32com), DEBE usar funciones encapsuladas que fuercen estrictamente SpaceBefore=0, SpaceAfter=0 (0 puntos) y LineSpacing=1.0 (Sencillo) para cada párrafo.
Identidad Visual Intacta: El no forzar estos parámetros hace que Word aplique sus estilos por defecto (ej. 8pt de espacio posterior), destruyendo el formato compacto y técnico requerido.
Aplicación Universal: Esta regla subsume y protege a todas las reglas anteriores (como la Regla 53 de no dejar líneas en blanco), ya que asegura que a nivel de metadatos del párrafo no existan espacios fantasma.

55. MEMORIA TOTAL: FORMATO ESTRICTO CC1, ARIAL NARROW Y BOILERPLATE COMPLETO
Contexto
Se olvidaron reglas críticas de formato previamente aprendidas, como el uso de la fuente Arial Narrow, tamaños específicos, sangrías jerárquicas y la inserción del 'boilerplate' (textos estándar) completo de la CC1.
La Regla Definitiva
Tipografía Inquebrantable: TODO el documento debe usar Arial Narrow 11, excepto las notas al pie que usan Arial Narrow 8, y las iniciales finales (ej. LGP/JCQ) que también usan Arial Narrow 8.
Nesting Escalonado (Sangrías):
Los romanos (I., II.) van al margen (0 cm).
Los numerales (1., 2.) van al margen (0 cm), el texto a 1 cm.
Los incisos (i), (ii) dentro de HECHOS van a 1 cm, el texto a 2 cm.
Los incisos en la parte RESOLUTIVA van alineados con el margen (0 cm), el texto a 1 cm.
Soft Returns Inteligentes en Notas al Pie: Cuando una nota al pie tenga múltiples párrafos o líneas, NUNCA usar un Enter normal (\n) porque rompe la nota, ni un Soft Return solo (\x0b) porque causa estiramiento justificado. Se debe usar Tabulador + Soft Return (\t\x0b) para mantener el formato bloque impecable.
Boilerplate Completo CC1: Todo admisorio de la CC1 debe contener íntegramente las secciones estándar: III. REQUERIMIENTO DE INFORMACIÓN (parte considerativa) y IV. RESOLUCIÓN DE LA SECRETARÍA TÉCNICA (parte resolutiva). La resolución debe incluir desde el PRIMERO hasta el DÉCIMO PRIMERO (traslado, requerimiento MYPE, información sobre multas, atenuantes, conciliación, desistimiento, y casillas electrónicas), junto con todas sus respectivas notas al pie legales (Artículos 18, 19, 110, 114, 115, 116, 112 del Código, y 24, 29 del DL 807).

56. REGLA SUPREMA DEFINITIVA: APLICACIÓN OBLIGATORIA E INQUEBRANTABLE DEL CORPUS COMPLETO
Contexto
Esta regla consolida y sella todas las instrucciones previas. Su propósito es garantizar que bajo ninguna circunstancia se omita o relaje el cumplimiento de las normativas de formato, estructura y tipificación de la matriz.
La Regla Definitiva
Para TODA resolución de admisorio que se elabore en adelante, el asistente DEBE aplicar SIEMPRE, de manera sistemática y sin omitir un solo detalle, la integridad de los DOs, DONTs y reglas estructurales descritos en este documento. Esto incluye expresamente:
Respetar la Tipificación estricta (Art. 1 y 2 para Info, Art. 18 y 19 para Idoneidad, Art. 58.b para Métodos Engañosos).
Unificar sujetos procesales y plazos de notificación (2 días correo/físico, 5 días casilla).
Respetar la prohibición absoluta de imputar el Art. 24, Inducción al error, y la doble imputación (Non bis in idem).
Usar estrictamente las plantillas base y el formato visual: Arial Narrow 11 (cuerpo), Arial Narrow 8 (notas al pie), interlineado sencillo, sin párrafos en blanco entre listas, y el Boilerplate completo (CC1 o PS1 según corresponda).
Mantener las sangrías escalonadas exactas (0cm, 1cm, 2cm) dependiendo si es la sección de HECHOS o la RESOLUTIVA, y usar \t\x0b para notas al pie multilínea.
Narrar los hechos de forma objetiva, cronológica, reflejando el petitorio sin adjetivaciones, y redactar requerimientos fácticos en infinitivo sin invocar "deberes" en la sección probatoria. Cualquier desviación u omisión de los puntos listados a lo largo de este documento constituirá un error crítico.

57. REGLA SUPREMA DE NOMENCLATURA SOAT Y OTORGAMIENTO
Contexto
El usuario exige estricta precisión técnica para casos de SOAT.
La Regla Definitiva
Cuando se trate de SOAT, usar "(en adelante, SOAT)" de inmediato en los Hechos. Además, nunca usar la frase "pagar la cobertura" aislada, sino "otorgar la cobertura de fallecimiento y gastos de sepelio del SOAT".

58. REQUERIMIENTOS IN-LINE PARA UN SOLO PROVEEDOR (SECCIÓN III Y RESOLUTIVO QUINTO)
Contexto
Para ahorrar espacio y mantener la estructura limpia, cuando solo se requiere información a un denunciado.
La Regla Definitiva
NO usar listas verticales numeradas con (i), (ii), (iii) que generen nuevos párrafos. Se deben agrupar todos los requerimientos en un solo párrafo continuo de manera 'in-line', separados por punto y coma. Ejemplo: "...cumpla con lo siguiente: (i) presentar una copia...; (ii) presentar los medios...; y, (iii) presentar todas las comunicaciones...".

59. RESOLUTIVO "PRIMERO" EN PÁRRAFO ÚNICO (CERO VIÑETAS)
Contexto
Cuando solo se está imputando una presunta infracción a un proveedor.
La Regla Definitiva
El punto PRIMERO NUNCA debe contener un bloque introductorio seguido de viñetas. Debe redactarse fluidamente de corrido. Ejemplo: "PRIMERO: admitir a trámite la denuncia del [fecha] interpuesta por [Denunciante] contra [Denunciado], por presunta infracción a los artículos [x], en tanto la compañía aseguradora se habría negado a otorgar..."

60. CONTROL DE FORMATO NATIVO (ELIMINACIÓN DE RESALTADOS)
Contexto
En las plantillas Word maestras a veces existen textos o viñetas resaltados en verde (como marcadores de posición) que ensucian el documento final.
La Regla Definitiva
El script `insert_footnotes.py` o el procesador final DEBE aplicar `document.Content.HighlightColorIndex = 0` a todo el documento para erradicar cualquier resaltado residual simulando un "Ctrl+E" -> "Sin Color".

61. INSERCIÓN CORRECTA DE NOTAS AL PIE VÍA WIN32COM
Contexto
Las notas al pie aparecían vacías (sin texto) porque se pasaba un argumento nombrado (`Text=...`) que el puente COM ignora o malinterpreta.
La Regla Definitiva
Para agregar notas al pie por COM se deben pasar los argumentos de forma posicional estricta. Ejemplo correcto: `document.Footnotes.Add(rng, "", str(note))` en lugar de usar `Text=...`.

62. PROHIBICIÓN ABSOLUTA DE MARKDOWN Y SALTOS DE PÁRRAFO DUROS EN NOTAS AL PIE
Contexto
En las notas al pie, usar asteriscos (`**`) para negritas resultaba en la impresión literal de los asteriscos, arruinando la objetividad del documento. Asimismo, los saltos de línea con `\n` rompían el estilo "Footnote Text" nativo de Word en las líneas subsecuentes (volviéndose letra grande o desfasada).
La Regla Definitiva
JAMÁS usar asteriscos u otro markdown en las cadenas de texto del JSON destinadas a MS Word. Adicionalmente, si una nota al pie requiere varias líneas, se debe utilizar EXCLUSIVAMENTE el salto de línea suave (`\u000b` o `\x0b`) en vez de `\n` para evitar que Word cree nuevos párrafos y destruya la tipografía Arial Narrow tamaño 8.

63. FORZADO DE ESTILO TIPOGRÁFICO EN NOTAS AL PIE
Contexto
Word 365 y la inserción COM (`Footnotes.Add`) a menudo insertan texto con fuentes predeterminadas como "Aptos 10", destrozando la uniformidad con el estilo original de "Arial Narrow 8 Justificado".
La Regla Definitiva
Es OBLIGATORIO que `insert_footnotes.py` itere sobre todas las notas al pie del documento final (`document.Footnotes`) y fuerce explícitamente la fuente (`Arial Narrow`), el tamaño (`8`) y la alineación justificada (`Alignment = 3`), sin confiar ciegamente en el estilo heredado de la plantilla.

64. MODIFICACIÓN A LA REGLA 62: NO USAR SALTOS SUAVES EN TEXTO JUSTIFICADO
Contexto
Se había intentado usar `\x0b` (soft line break) en las notas al pie para mantener el estilo original. Sin embargo, dado que los pies de página están JUSTIFICADOS, un salto de línea suave provoca que Word estire las palabras de forma grotesca para abarcar todo el ancho del párrafo (espacios gigantes entre palabras).
La Regla Definitiva
En el JSON, las notas al pie de múltiples párrafos DEBEN utilizar saltos de párrafo reales (`\n`). Para evitar la pérdida del formato, la aplicación obligatoria de la Regla 63 (bucle COM forzando `Arial Narrow 8` a todo `document.Footnotes`) es suficiente para mantener el formato en todos los sub-párrafos sin causar estiramientos indeseados.

65. RESPETAR LOS PÁRRAFOS Y NOTAS RESIDENTES DE LA PLANTILLA
Contexto
Se inyectó el párrafo "En tanto la denuncia reúne..." y su correspondiente nota al pie en el JSON, ignorando que la plantilla ya traía ese párrafo de base. Esto causó duplicidad del párrafo y de la nota (Nota 5 inyectada vs Nota 6 residente).
La Regla Definitiva
Antes de rellenar `imputaciones_analisis`, se debe constatar qué párrafos de conclusión ("En tanto la denuncia...") ya habitan la plantilla. La automatización NO DEBE inyectar párrafos redundantes que ya existan en la estructura base del Word.

66. USO OBLIGATORIO DE `\r` PARA SALTOS DE PÁRRAFO DUROS EN WIN32COM
Contexto
En MS Word (vía `win32com`), inyectar un string con `\n` en un objeto Text lo interpreta internamente como un salto de línea suave (Soft Line Break / `Shift+Enter`). En párrafos justificados, esto estira grotescamente la línea final de cada falso párrafo.
La Regla Definitiva
Antes de inyectar textos multilínea vía COM (especialmente en `insert_footnotes.py`), se DEBE reemplazar todo `\n` por `\r` (`str(note).replace("\n", "\r")`). En MS Word, `\r` es el verdadero y único salto de párrafo duro, garantizando que el texto justificado no se estire.

67. MANEJO DE LISTAS COMPUESTAS EN RESOLUTIVOS (CLONACIÓN Y PURGA)
Contexto
El resolutivo `TERCERO` de la plantilla contenía una lista dummy `(i) presentar documentos...`. Inyectar todos los requerimientos como un bloque de texto gigante dentro del párrafo principal `TERCERO:` destruía la indentación nativa y generaba estiramientos, además de dejar viva la basura (el ítem `(i)` original) en el documento final.
La Regla Definitiva
Cuando un resolutivo (ej. `TERCERO`) contenga listas separadas por `\n`:
1. El motor debe inyectar únicamente la línea base ("TERCERO: requerir...") en el párrafo ancla.
2. Debe guardar el resto de ítems en memoria.
3. Debe esperar a toparse con el primer ítem dummy de la plantilla (ej. el párrafo que empieza por `(i)`).
4. Usará ese primer ítem dummy para clonar su estilo perfecto por cada ítem en memoria, inyectándolos uno por uno.
5. Finalmente, el motor debe **eliminar/purgar** todos los ítems residuales de la plantilla que empiecen por un enumerador romano para no dejar duplicados sucios al final de la resolución.

66. USO OBLIGATORIO DE `\r` PARA SALTOS DE PÁRRAFO DUROS EN WIN32COM
Contexto
En MS Word (vía `win32com`), inyectar un string con `\n` en un objeto Text lo interpreta internamente como un salto de línea suave (Soft Line Break / `Shift+Enter`). En párrafos justificados, esto estira grotescamente la línea final de cada falso párrafo.
La Regla Definitiva
Antes de inyectar textos multilínea vía COM (especialmente en `insert_footnotes.py`), se DEBE reemplazar todo `\n` por `\r` (`str(note).replace("\n", "\r")`). En MS Word, `\r` es el verdadero y único salto de párrafo duro, garantizando que el texto justificado no se estire.

67. MANEJO DE LISTAS COMPUESTAS EN RESOLUTIVOS (CLONACIÓN Y PURGA)
Contexto
El resolutivo `TERCERO` de la plantilla contenía una lista dummy `(i) presentar documentos...`. Inyectar todos los requerimientos como un bloque de texto gigante dentro del párrafo principal `TERCERO:` destruía la indentación nativa y generaba estiramientos, además de dejar viva la basura (el ítem `(i)` original) en el documento final.
La Regla Definitiva
Cuando un resolutivo (ej. `TERCERO`) contenga listas separadas por `\n`:
1. El motor debe inyectar únicamente la línea base ("TERCERO: requerir...") en el párrafo ancla.
2. Debe guardar el resto de ítems en memoria.
3. Debe esperar a toparse con el primer ítem dummy de la plantilla (ej. el párrafo que empieza por `(i)`).
4. Usará ese primer ítem dummy para clonar su estilo perfecto por cada ítem en memoria, inyectándolos uno por uno.
5. Finalmente, el motor debe **eliminar/purgar** todos los ítems residuales de la plantilla que empiecen por un enumerador romano para no dejar duplicados sucios al final de la resolución.

68. FORMATO ESTRICTO EN NOTAS AL PIE Y LEYES
Contexto:
El estilo técnico exige que las notas al pie tengan sangría francesa (Hanging Indent) perfectamente alineada, y que los títulos de leyes y artículos se resalten en negrita de forma automática.
La Regla Definitiva:
1. En `insert_footnotes.py`, toda nota al pie debe recibir `p.Format.LeftIndent = 567` y `p.Format.FirstLineIndent = -567` (para lograr el bloque de 1cm con sangría francesa), además de `Alignment = 3` (justificado).
2. Todo párrafo dentro de una nota al pie que inicie con "LEY " o "Artículo " DEBE ponerse automáticamente en negrita (`p.Range.Font.Bold = True`).
3. Esto garantiza que las referencias legales destaquen armónicamente dentro del texto de tamaño 8pt.

69. TAMAÑO PROTEGIDO PARA INICIALES (LGP/JCQ)
Contexto:
El proceso global de formateo en `build.py` iteraba sobre cada run aplicando 11pt, lo cual destruía las iniciales finales del revisor/proyectista (que deben ser 8pt).
La Regla Definitiva:
En la función que limpia o formatea los runs globales (ej. `clean_run`), se DEBE detectar si el texto corresponde al formato de iniciales usando Regex (`^[A-Z]{2,4}/[A-Z]{2,4}$`). Si hace match, se debe blindar forzando `run.font.size = Pt(8)`. NUNCA sobreescribir el tamaño de las iniciales a 11pt.

70. EL SECRETO DEL HANGING INDENT EN WORD (SANGRÍA FRANCESA)
Contexto:
Al aplicar sangría francesa (LeftIndent = 1cm, FirstLineIndent = -1cm) en notas al pie usando `win32com`, se generaba un vacío (gap) enorme al final de la página y el texto desaparecía.
La Regla Definitiva:
En MS Word, para que un texto respete la sangría francesa (Hanging Indent) sin romperse visualmente ni causar saltos de página erráticos, **TODO PÁRRAFO DEBE INICIAR CON UN CARÁCTER TABULADOR (`\t`) DESPUÉS DEL NÚMERO DE REFERENCIA**.
En `insert_footnotes.py`, el texto a insertar debe procesarse así:
`safe_note = "\t" + str(note).replace("\n", "\r\t")`
Esto asegura que la primera línea (después del superíndice) tenga un Tab, y que cada salto de línea (párrafo nuevo dentro de la nota) también inicie con un Tab. NUNCA se debe aplicar FirstLineIndent negativo sin inyectar caracteres Tab.

71. META-ANÁLISIS DE ROBUSTEZ DEL MOTOR DE COMPILACIÓN
Contexto:
Para evitar la fragilidad del código en iteraciones futuras, se establece la filosofía de desarrollo del motor `build.py` y dependencias.
La Regla Definitiva:
a) Mutaciones en `python-docx`: Siempre clonar usando `copy.deepcopy` en el XML (`_element`) y re-envolver, pero con cuidado de limpiar tags específicos (`w:shd`, `w:highlight`) a nivel XML puro (`OxmlElement`).
b) Límites de `python-docx`: Nunca intentar procesar Notas al Pie, Macros o campos complejos con `python-docx`. Delegar siempre a `win32com` en un script secundario.
c) Intervención de estilos con `win32com`: Al inyectar texto vía COM, Word asume estilos por defecto (Normal). TODO texto inyectado debe ser formateado explícitamente (Fuente, Tamaño, Alineación, Sangrías) mediante el objeto `Range.Format`.

72. METRÍCAS DE DISTANCIA EN VBA (POINTS VS TWIPS)
Contexto:
El documento generado colapsó catastróficamente (pasó de 7 páginas a 159 páginas). La causa fue haber inyectado el valor `567` en `p.Format.LeftIndent` vía la API `win32com` de Word.
La Regla Definitiva:
En el XML interno de Word (`python-docx`), las distancias se miden en **twips** (donde 1 cm = 567 twips). SIN EMBARGO, en la API COM (`win32com` / VBA), las distancias se miden en **puntos (points)**. 
- 1 pulgada = 72 puntos.
- 1 centímetro = 28.35 puntos.
Al pasar `567` a VBA, Word interpretó 567 puntos (casi 20 centímetros), empujando todo el texto fuera del margen de la hoja, reduciendo el ancho de columna a cero y generando 159 páginas de texto desbordado.
NUNCA utilices valores twips (ej. 567) en la API `win32com`. Para lograr un centímetro de sangría francesa vía COM, la instrucción correcta es ineludiblemente:
`p.Format.LeftIndent = 28.35`
`p.Format.FirstLineIndent = -28.35`

73. FORMATO EXPLÍCITO Y LIMPIEZA DE TABS EN NOTAS AL PIE
Contexto:
El texto inyectado en las notas al pie generaba doble-tabulaciones y espacios residuales, arruinando la sangría francesa. Además, la herencia de negritas ("Bold") no funcionaba si la palabra clave (ej. "Artículo") no estaba exactamente al principio del párrafo debido a estos espacios/tabs fantasmas, o si el documento arrastraba estilos invisibles.
La Regla Definitiva:
NUNCA confíes en heredar estilos de la plantilla vía código.
1. Al inyectar el texto base del JSON, se deben eliminar todos los espacios y tabs manuales al inicio de cada línea usando `line.lstrip(" \t")`, para luego concatenar con un ÚNICO `\t` maestro y saltos de párrafo `\r`.
2. Al formatear los párrafos resultantes vía COM (`win32com`), TODO texto inyectado en la etapa final debe ser **formateado explícitamente**. Se debe declarar `p.Range.Font.Bold = False` para limpiar la herencia de estilos antes de aplicar la lógica de negritas.
3. La evaluación para aplicar `Bold = True` a leyes debe evaluar todo el párrafo y no estar restringida a las primeras palabras de un string no higienizado.

74. MAYÚSCULAS EN PARTES RESOLUTIVAS
Contexto:
En la redacción de las partes resolutivas (ej. PRIMERO, SEGUNDO, CUARTO, etc.), el nombre de las partes (denunciante y denunciado) se inyectaba enteramente en mayúsculas (ej. "LA POSITIVA SEGUROS Y REASEGUROS S.A.A. (LA POSITIVA)"), lo cual es incorrecto para el texto narrativo.
La Regla Definitiva:
NUNCA utilices mayúsculas sostenidas para los nombres de las partes dentro del texto de los puntos resolutivos. Solo se deben usar mayúsculas para la letra inicial de los nombres propios o siglas, aplicando "Title Case" o formato de título (ej. "La Positiva Seguros y Reaseguros S.A.A." y no "LA POSITIVA SEGUROS Y REASEGUROS S.A.A."). Las mayúsculas sostenidas solo se permiten estrictamente en el bloque de metadatos iniciales (encabezado del documento).

75. REGLAS GRAMATICALES ESTRICTAS: MAYÚSCULA INICIAL Y CERO A LA IZQUIERDA
Contexto:
Se observaron errores de redacción donde las oraciones o incisos comenzaban en minúscula y las fechas utilizaban ceros a la izquierda para números de un dígito (ej. "06 de julio").
La Regla Definitiva:
- Mayúscula inicial obligatoria: Toda oración, incluso si forma parte de un inciso listado como `(i)`, `(ii)`, `(iii)`, etc., DEBE comenzar siempre con letra mayúscula (ej. "(v) La compañía aseguradora..." y no "(v) la compañía aseguradora...").
- Prohibición del cero a la izquierda en números de un dígito: Al escribir fechas o números menores a 10, NUNCA se debe colocar un cero a la izquierda (ej. debe escribirse "6 de julio de 2023" y está estrictamente prohibido usar "06 de julio de 2023").

74. MAYÚSCULAS EN PARTES RESOLUTIVAS
Contexto:
En la redacción de las partes resolutivas (ej. PRIMERO, SEGUNDO, CUARTO, etc.), el nombre de las partes (denunciante y denunciado) se inyectaba enteramente en mayúsculas (ej. "LA POSITIVA SEGUROS Y REASEGUROS S.A.A. (LA POSITIVA)"), lo cual es incorrecto para el texto narrativo.
La Regla Definitiva:
NUNCA utilices mayúsculas sostenidas para los nombres de las partes dentro del texto de los puntos resolutivos. Solo se deben usar mayúsculas para la letra inicial de los nombres propios o siglas, aplicando "Title Case" o formato de título (ej. "La Positiva Seguros y Reaseguros S.A.A." y no "LA POSITIVA SEGUROS Y REASEGUROS S.A.A."). Las mayúsculas sostenidas solo se permiten estrictamente en el bloque de metadatos iniciales (encabezado del documento).

- R-84: **Protección ortográfica estricta:** Al transcribir textos, en especial referencias legales, NUNCA omitas tildes ni alteres la escritura correcta. Específicamente, nunca escribas 'Artculo' u omitas la 'í'. Siempre debe decir 'Artículo'.

## 76. MASTER PHOENYX: REGLAS POPPERIANAS DE REDACCIÓN Y TIPIFICACIÓN (R-85 A R-95)

- R-85: **PROHIBICIÓN CATEGÓRICA DE 'INDUCCIÓN A ERROR':** Bajo ninguna circunstancia se imputará la figura de 'inducción al error' ni el Artículo 3 del Código. Cualquier defecto, falta o inexactitud en la información comercial se canaliza exclusivamente por el **Artículo 1°, numeral 1, literal b) y Artículo 2° del Código**.
- R-86: **HECHOS SIN LA PALABRA 'DENUNCIANTE' NI SU NOMBRE:** Dado que la narración de los hechos es antecedida obligatoriamente por la frase *"el/la denunciante señaló lo siguiente:"*, queda estrictamente prohibido usar la palabra 'denunciante' o el nombre propio dentro de los párrafos de hechos. Se emplean directamente verbos afirmativos en tercera persona (ej. *"presentó"*, nunca *"se presentó"*).
- R-87: **PROHIBICIÓN DE CONDICIONALES EN HECHOS ('HABRÍA'):** **[DEROGADA el 18/09/2026 — la medición la falsó]** ~~En la sección de HECHOS está terminantemente prohibido usar 'habría' o 'habrían'~~. **El documento de control sí lo usa** (R-110) y **el 60 % del corpus narra en indicativo directo con el alias** (R-148). Conviven las dos formas: atribución al denunciante y narración directa. Lo único prohibido es el indicativo asertivo que atribuya al proveedor un hecho no probado. Los hechos reflejan la versión del denunciante y se narran en tiempo pasado afirmativo (ej. *"presentó la solicitud"*, *"denegó la cobertura"*). El condicional 'habría' es de uso exclusivo para las imputaciones de la Secretaría Técnica.
- R-88: **INICIO ESTRICTO DE PÁRRAFO CON FECHA:** Todo párrafo de hechos debe iniciar con la fecha precedida del artículo 'El' (ej. *"El 14 de agosto de 2024,"*). Colocar directamente el número del día y año (sin palabras superfluas como 'día' o 'año'). Si no hay fecha para un hecho previo crucial (como suscripción de contrato), iniciar como: *"Con anterioridad a [fecha del párrafo posterior],"*.
- R-89: **FORMATO DE MONEDA MONOLÍTICO:** En montos en soles (`S/`) o dólares (`US$`), está prohibido el uso de punto `.` en cualquier posición y prohibida la coma `,` en números enteros. Solo se permite coma para decimales y espacio para separar miles (ejemplo exacto: `S/ 2 618,00` o `US$ 1 500,00`).
- R-90: **PROHIBICIONES LÉXICAS Y REEMPLAZOS OBLIGATORIOS:**
  - Prohibido 'esposo/esposa/esposos': usar exclusivamente `cónyuge` o `cónyuges`.
  - Prohibido 'tras': usar exclusivamente `luego de`.
  - Prohibido tildar 'esta': nunca escribir `ésta`, `éstas`, `éste` o `éstos`.
  - Prohibido 'Dr.' o 'doctor': en profesionales de salud usar siempre `médico`.
  - Prohibido 'carro' o 'auto': referirse siempre como `vehículo` (o `vehículo con Placa de Rodaje [número]`).
- R-91: **NOMENCLATURA DE PÓLIZAS:** La primera mención de una póliza con número debe seguir la fórmula: `Seguro [tipo] – Póliza [número] (en adelante, “Seguro [tipo]”)`, y en adelante omitir el número y la palabra póliza.
- R-92: **SUCESIÓN INTESTADA Y CAUSANTE:** Cuando la parte denunciante sea una Sucesión Intestada, a la persona fallecida se la llamará obligatoriamente `la/el causante de la Sucesión Intestada`.
- R-93: **ESTRUCTURA DE IMPUTACIONES RESOLUTIVAS (PRIMERO):** Cada imputación debe ser de **una sola oración**, sin palabras en negrita, invocando la fórmula: `(i) Presunta infracción a... de la Ley 29571... en tanto [Nombre Proveedor] habría/no habría [conducta concreta]...` individualizando fechas exactas y pólizas.
- R-94: **REQUERIMIENTOS EN PÁRRAFO ÚNICO (MÁXIMO 4 ÍTEMS):** La parte considerativa y resolutiva de requerimientos se condensa en un solo párrafo con máximo cuatro (4) viñetas `(i)`, `(ii)`... en infinitivo, guardando simetría estricta con la infracción principal controvertida.
- R-95: **MANDATO CERO-OCR (VISIÓN MULTIMODAL EXCLUSIVA):** En escritos escaneados o manuscritos, queda prohibido el uso de OCR tradicional. El procesamiento se ejecuta exclusivamente con Visión Multimodal / Google Lens para garantizar cero alucinaciones en fechas, números y montos.
  - **AMPLIADA POR R-137 (14/09/2026):** ya no rige solo para escaneados o manuscritos.
    **Todas** las páginas se leen con Google Lens, tengan o no capa de texto.

## 77. MASTER PHOENYX: INVARIANTES POPPERIANAS DE IDENTIDAD PROCESAL, NOTIFICACIÓN COMPARTIDA Y SIMETRÍA CONSIDERATIVA-RESOLUTIVA (R-96 A R-102)

- R-96: **DENOMINACION DE PARTES POR ZONA DEL DOCUMENTO (REESCRITA — v2):**
  - *Estado epistemico:* la version 1 de esta regla (prohibicion absoluta de `el denunciante`
    y uso exclusivo del alias en todo el documento) **fue falsada** por el documento de control
    el documento de control corregido por el instructor el 14/09/2026, que usa
    `el denunciante` en la considerativa y la razon social completa en la resolutiva. Se sustituye
    por una regla por zonas. Corroboracion: n=1 documento de control; **pendiente de contraste
    contra el corpus completo** (ver R-109).
  - **Zona 1 — Encabezado (`EXPEDIENTE`/`DENUNCIANTE`/`DENUNCIADO`):** nombre completo en
    mayusculas y alias entre parentesis: `DENUNCIANTE: [NOMBRE COMPLETO EN MAYUSCULAS] (SEÑOR [PRIMER APELLIDO])`,
    `DENUNCIADO: RIMAC SEGUROS Y REASEGUROS S.A. (RIMAC)`. Todo el bloque en negrita (R-104).
  - **Zona 2 — Numeral 1 de Hechos:** `el señor [Nombre Completo]` y razon social completa con
    definicion del alias. A partir de aqui rige el alias.
  - **Zona 3 — Incisos de Hechos:** `el señor [Primer Apellido]` y alias del proveedor (`Rimac`).
    Se admite `el denunciante` como sujeto anaforico. Prohibido `la denunciada` para el proveedor.
  - **Zona 4 — Nucleo factico de la imputacion (considerativa Seccion II y articulos PRIMERO/SEGUNDO):**
    el proveedor se designa por su **categoria** (`la compañia aseguradora`, `el banco`) y el
    consumidor como `el denunciante`. Prohibido el alias corto en esta zona, porque el texto debe
    resistir la lectura aislada del articulo resolutivo.
  - **Zona 5 — Articulos resolutivos de mandato (TERCERO en adelante):** **razon social completa**,
    nunca el alias. `requerir a Rimac Seguros y Reaseguros S.A.`, no `requerir a Rimac`.
  - **Sucesion Intestada:** `la Sucesion Intestada de [Causante]`; a la persona fallecida,
    `la/el causante de la Sucesion Intestada`. Prohibido 'el difunto', 'el occiso', 'el finado',
    'el fallecido'.
  - *Falsador:* un admisorio que use el alias corto dentro de un articulo resolutivo de mandato,
    o la razon social completa dentro de un inciso de hechos, refuta la regla o el documento.
- R-97: **TEOREMA DE SIMETRÍA Y CONGRUENCIA TEXTUAL (CONSIDERATIVA VS RESOLUTIVA):**
  - El núcleo fáctico de la imputación debe ser **idéntico palabra por palabra** entre la Sección II (De la Admisión a Trámite) y los artículos de imputación en la Sección RESUELVE (`PRIMERO:`, `SEGUNDO:`).
  - En Considerativa (Sección II): `...considera que el hecho denunciado, consistente en que [NÚCLEO FÁCTICO], involucraría una presunta afectación a sus expectativas... Por consiguiente, corresponde calificar el hecho... como una presunta infracción al [NORMA].`
  - En Resolutiva (`PRIMERO:` / `SEGUNDO:`): `Presunta infracción a los artículos [NORMA] de la Ley 29571... en tanto [PROVEEDOR] [NÚCLEO FÁCTICO].`
  - La alteración de una sola palabra rompe la congruencia procesal exigida por el artículo 10° del TUO de la LPAG y vicia de nulidad el acto administrativo.
- R-98: **REGLA DE DOMICILIO COMPARTIDO Y NOTIFICACIÓN CONJUNTA EN PÁRRAFO ÚNICO:**
  - Cuando dos o más partes procesales compartan el mismo domicilio físico, casilla electrónica o correo electrónico (v. gr., denunciante y denunciado notificados por correo, co-denunciantes con domicilio/correo común, o dos entidades del mismo grupo financiero con Casilla Electrónica), **se les debe agrupar obligatoriamente en un único artículo resolutivo consolidado**, en estricta aplicación del principio de economía y celeridad procesal.
  - Se redacta en plural concordado: `requerir a [Parte 1] y a [Parte 2] para que, dentro del plazo de dos (2) días hábiles siguientes a la fecha en que reciban la notificación en sus bandejas de correo electrónico, efectúen la confirmación de recepción... de conformidad con el segundo párrafo del numeral 4 del artículo 20 del Texto Único Ordenado de la Ley del Procedimiento Administrativo General, aprobado mediante Decreto Supremo 006-2026-JUS, bajo apercibimiento de rehacer el acto de notificación y notificarles conforme al numeral 1 del artículo 20 del citado cuerpo normativo.`
- R-99: **DUALIDAD DE REQUERIMIENTOS AL PROVEEDOR EN LA PARTE RESOLUTIVA:**
  - Todo admisorio debe articular dos tipos de requerimiento al proveedor:
    1. *Requerimiento Administrativo-Estructural (Artículo TERCERO):* Plazo improrrogable de 5 días hábiles para acreditar inscripción en Registros Públicos, vigencia de poder de representante legal, número de RUC, fijación de domicilio procesal y acreditación de condición MYPE (Art. 110 del Código).
    2. *Requerimiento Probatorio Específico de la Controversia (Artículo CUARTO o SEXTO):* Redactado en **párrafo único con sub-incisos en numeracion romana minuscula en linea `(i)`, `(ii)`, `(iii)`, `(iv)`**, verbo en infinitivo, separados por `;` y con `y,` antes del ultimo (**corregido**: la version 1 exigia letras `(a)-(d)`, notacion que **no aparece** en el documento de control ni en los modelos institucionales revisados) exigiendo póliza matriz, certificado, grabaciones de voz, estado de cuenta y cartas de respuesta al reclamo.
- R-100: **ANCLAJE Y FÓRMULA DE TRASLADO DE OTRO ÓRGANO (NOTA AL PIE PÁGINA 1):**
  - En casos donde la denuncia proceda de otro órgano resolutivo (ORPS 1, ORPS 2, CC2, sedes regionales u oficinas desconcentradas), se inserta un superíndice de nota al pie sobre la palabra `denuncia` o `escrito` en el numeral 1 de Hechos: `Mediante la denuncia¹ del [fecha]...`
  - La nota al pie número 1 debe contener obligatoriamente la fórmula: `Denuncia remitida a esta Comisión mediante [TIPO_DOC] [NÚMERO] de fecha [FECHA_EMISIÓN], [recibida/recepcionada] el [FECHA_RECEPCIÓN].`
- R-101: **INFORMACIÓN OBLIGATORIA SOBRE GRADUACIÓN DE SANCIONES Y ATENUANTES (ARTS. 110 Y 112):**
  - Debe incorporarse un artículo resolutivo específico que informe a las partes sobre la escala sancionadora (hasta 450 UIT) y la consideración del allanamiento o reconocimiento de pretensiones como circunstancia atenuante.
- R-102: **FACULTAD DE CONCILIACIÓN PREVIA Y APERCIBIMIENTO DE INASISTENCIA (ART. 29 D.LEG. 807):**
  - Debe incorporarse un artículo resolutivo que informe a las partes su derecho a solicitar audiencia de conciliación antes de la resolución final, con apercibimiento expreso de tener por no realizada la audiencia y levantar acta de inasistencia si el representante no cuenta con poder especial con firma legalizada ante Notario Público.

## 78. MASTER PHOENYX: INVARIANTES DERIVADAS DEL DOCUMENTO DE CONTROL ADM 2662-2026 R3 (R-103 A R-110)

> Origen: comparacion milimetrica, parrafo por parrafo y a nivel OOXML, entre la version generada
> por el motor (`RES_02_2662-2026_CC1_ADMISORIO.docx`) y la version corregida por el instructor
> (`ADM 2662-2026 R3 RIMAC - LSQok.docx`), el 14/09/2026. Cada regla se enuncia junto con su
> **falsador**: el hecho observable que la refutaria. Ninguna regla se da por corroborada sin haber
> corrido `scripts/verificar_admisorio.py` sobre el documento.

- R-103: **FIRMA VARIABLE SEGUN EL PROVEEDOR DENUNCIADO (MANDATO DEL INSTRUCTOR, NO INDUCCION):**
  - **Mandato vigente desde el 14/09/2026:** cuando el proveedor denunciado es
    **Rimac Seguros y Reaseguros S.A.**, la resolucion **no** la firma la Secretaria Tecnica titular.
    Firma: `Firmado digitalmente por / LUISA ANALI SILVA MALPARTIDA / Secretaria Tecnica Ad Hoc /
    Comision de Proteccion al Consumidor 1`, con iniciales de control `LSQ/DCQ`.
  - En los demas casos firma la Secretaria Tecnica titular (`EVELING ROA QUISPE`, `Secretaria Tecnica`).
  - **Advertencia epistemica — el corpus NO corrobora este mandato.** Medicion reproducible sobre
    `plantillas_maestras/` (n=630) el 14/09/2026:

    | Plantillas con Rimac como denunciado | 143 |
    |---|---|
    | firmadas Ad Hoc | **3** (04–05/08/2026) |
    | firmadas por la titular | **140** (15/04/2025 – 21/08/2026) |

    La hipotesis de rescate temporal ("rige desde agosto de 2026") tambien queda **falsada**: hay
    plantillas con Rimac firmadas por la titular el 07, 12 y 21 de agosto de 2026, posteriores a las
    tres ad hoc. El criterio real **no es** la sola presencia de Rimac como denunciado.
  - **Por tanto esta regla se aplica por mandato de autoridad, no por induccion del corpus.** Queda
    abierta la pregunta al instructor: cual es el hecho que dispara la designacion ad hoc
    (¿abstencion de la titular por conflicto de interes, art. 99 del TUO de la LPAG? ¿designacion por
    resolucion de la Comision para expedientes determinados? ¿materia o sede?). Hasta que se responda,
    el motor aplica el mandato literal y **no** reescribe retroactivamente las 140 plantillas.
  - *Causa raiz del error del caso de control:* `docs/MEMORIA_ESTILO_VISUAL_PAGINAS.md` codificaba
    la firma como valor fijo `EVELING ROA QUISPE`. El motor cumplio el repositorio; **el repositorio
    estaba mal**. Corregido con una matriz de firma en esa misma seccion.
  - *Falsador:* un admisorio contra Rimac emitido despues del 14/09/2026 firmado por la titular.

- R-104: **INTEGRIDAD TIPOGRAFICA DEL ENCABEZADO Y DE LOS ORDINALES:**
  - Las cuatro lineas del encabezado (`EXPEDIENTE`, `DENUNCIANTE`, `DENUNCIADO`, `MATERIAS`,
    `RESOLUCION`) van integramente en **negrita**.
  - **Todos** los rotulos ordinales de la parte resolutiva (`PRIMERO:` a `DECIMO:`) van en negrita,
    sin excepcion. Una resolucion con los cinco primeros en redonda y los cinco ultimos en negrita
    delata que el generador escribio los articulos por dos caminos distintos.
  - *Falsador:* un solo rotulo ordinal sin `<w:b/>` en su run.

- R-105: **PROHIBICION DE PARRAFOS NUMERADOS VACIOS Y DE SECCION ANUNCIADA SIN CONTENIDO:**
  - Ningun parrafo con `numPr` activo puede quedar sin texto: Word le pinta igual su numero o viñeta
    y la resolucion sale con incisos huerfanos.
  - Ninguna seccion puede anunciar contenido que luego no formula. `cumpla con lo siguiente:` seguido
    de nada es un vicio de motivacion, no un defecto estetico.
  - *Falsador:* `numPr` presente y `w:t` vacio; o un `lo siguiente:` sin `(i)` posterior.

- R-106: **ANCLAS DE NOTA AL PIE OBLIGATORIAS:**
  - Toda nota definida en `footnotes.xml` con texto debe tener su `footnoteReference` en el cuerpo.
    Las notas de la tipificacion (articulos 18 y 19 del Codigo) y la del articulo 20 del TUO de la
    LPAG en el articulo de confirmacion de recepcion son obligatorias.
  - *Falsador:* una nota con contenido y sin ancla, o un ancla sin nota.

- R-107: **MEMBRETE Y PIE INSTITUCIONAL (REESCRITA — v2):**
  - *Estado epistemico:* la version 1 exigia **seis** referencias de encabezado/pie en el `sectPr`.
    **Falsada** el 14/09/2026 por un documento de control valido que declara solo **dos**. El numero
    de referencias depende del modelo del que se parte y no es invariante.
  - Lo invariante es el **contenido**: el encabezado lleva el membrete de tres lineas
    (`SECRETARIA TECNICA DE LA` / `COMISION DE PROTECCION AL CONSUMIDOR 1` / `SEDE CENTRAL`) y el pie
    lleva el codigo de calidad `M-CPC-01/03`.
  - El campo dinamico de numero de pagina **no se exige**: esta presente en 2 de los 3 controles.
  - *Falsador:* ausencia de cualquiera de las tres lineas del membrete o del codigo `M-CPC-01/03`.

- R-108: **SEGUNDO ISOMORFISMO: REQUERIMIENTO DE INFORMACION (CONSIDERATIVA) <-> ARTICULO RESOLUTIVO:**
  - El parrafo `REQUERIMIENTO DE INFORMACION` de la considerativa y el articulo resolutivo que lo
    ordena (`QUINTO` en el documento de control) contienen **la misma lista de incisos, palabra por
    palabra**. Solo cambia el sujeto: la considerativa nombra al proveedor por su categoria
    (`la compañia aseguradora`), el articulo resolutivo usa `el proveedor denunciado`.
  - Este isomorfismo es independiente del de R-97 y **no estaba registrado**: R-99 describia la
    dualidad de requerimientos sin advertir que el probatorio tambien se escribe dos veces.
  - *Grado de corroboracion:* 2 de 3 controles lo cumplen verbatim. El tercero omite en la
    resolutiva una clausula que si figura en la considerativa y sigue siendo valido. Por eso esta
    regla se verifica como **observacion, no como falsador**: una divergencia no bloquea la entrega,
    se eleva al instructor para que decida.
  - *Falsador:* un inciso presente en una zona y ausente en la otra.

- R-109: **PROTOCOLO DE FALSACION PREVIO A LA ENTREGA (OBLIGATORIO):**
  - Ningun admisorio se entrega ni se declara terminado sin haber corrido:
    `python scripts/verificar_admisorio.py <archivo.docx>` y obtenido `APTO`.
  - El resultado se reporta al instructor **con su salida literal**, incluidos los fallos. Un informe
    de entrega sin la salida del verificador es un informe no verificado.
  - Toda regla de este archivo que no tenga prueba automatizada debe declararse como tal al reportar.
  - *Falsador:* una entrega declarada conforme cuyo `verificar_admisorio.py` devuelve `NO APTO`.

- R-110: **MODO VERBAL Y ATRIBUCION EN LOS INCISOS DE HECHOS:**
  - La conducta del proveedor se enuncia **siempre** bajo atribucion al denunciante
    (`Indico que...`, `Señalo que...`, `Preciso que...`, `Manifesto que...`) o en modo potencial
    (`habria retenido`, `habria reconocido`). Nunca en indicativo asertivo.
  - **Correccion de un error propagado:** el analisis entregado al instructor el 13/09/2026 afirmaba
    que el condicional `habria` estaba **prohibido** en los hechos. Es **falso**: el documento de
    control lo usa (`Rimac habria intentado llegar a un acuerdo`, `el conductor asegurado habria
    reconocido su responsabilidad`). Ademas, esa supuesta prohibicion nunca fue escrita en este
    archivo: se enuncio en conversacion y no existia como regla. **Lo no commiteado no existe.**
  - Los hechos referidos al propio denunciante (`El 9 de mayo de 2023, notifico la Carta Notarial...`)
    si van en indicativo: el sujeto es el, no el proveedor.
  - *Falsador:* un inciso de hechos donde el proveedor sea sujeto de un verbo en indicativo pasado
    sin verbo de atribucion en el mismo inciso.

## 79. MASTER PHOENYX: PROTOCOLO DE TRABAJO Y ECONOMIA DE PASADAS (R-113 A R-115)

> Origen: medicion del 14/09/2026 sobre el Expediente 2723-2026. El tiempo de un
> admisorio no se va en generar el Word: se va en mirar lo que ya se puede leer y en
> preguntarle al documento una cosa por llamada.

- R-113: **TRIAJE ANTES DE VISION. LA VISION ES PARA LO ESCANEADO, NO PARA TODO:**
  - Antes de abrir un expediente se ejecuta `python scripts/extraer_expediente.py <carpeta>`.
  - **DEROGADO EN SU CRITERIO DE AHORRO POR R-137 (14/09/2026).** Lo que sigue se
    conserva como registro de lo que se creyo y por que dejo de valer: se sostenia que
    las paginas con capa de texto no necesitaban vision porque «el caracter esta
    escrito, no interpretado». La medicion posterior lo refuto: el volcado pierde
    tildes y corrompe caracteres (R-126), y la capa de texto no muestra sellos, firmas
    ni anexos manuscritos. Hoy **todas** las paginas van a Google Lens y el volcado
    queda como contraste.
  - *Lo que si conserva su valor:* el triaje sigue siendo el primer paso, porque da el
    numero real de paginas (R-136) y el dossier anclado. Cuesta **1,1 s**.
  - El script devuelve ademas un dossier con cada fecha, monto, placa, correo y carta notarial
    **anclados a la pagina de la que salieron**, que es lo que hace verificable la cita (R-112).
  - *Falsador:* una pasada de vision sobre una pagina que el triaje marco como 'con texto'.

- R-114: **INTROSPECCION EN UNA SOLA LLAMADA:**
  - Queda prohibido inspeccionar un `.docx` parrafo por parrafo con llamadas sucesivas
    ('lee el parrafo 75', 'ahora sus runs', 'ahora sus notas'). Todo eso sale junto con
    `python scripts/inspeccionar_docx.py <archivo.docx>` en **0,5 s**: texto, negritas,
    subrayados, estilo, numeracion, anclas y notas, encabezados, pies y `sectPr`.
  - Para comparar contra un documento de control: `--diff <control.docx>`, que imprime
    **solo lo que difiere**. `--resumen` da el esqueleto de la resolucion.
  - *Falsador:* dos o mas lecturas consecutivas del mismo documento para averiguar cosas
    distintas del mismo parrafo.

- R-115: **ORDEN DE TRABAJO DE UN ADMISORIO (CINCO PASOS, EN ESTE ORDEN):**
  1. `extraer_expediente.py <carpeta>` — triaje y dossier anclado.
  2. Vision multimodal **solo** sobre las paginas que el triaje listo como sin texto.
  3. Redaccion sobre la plantilla que corresponda al patron del caso.
  4. `inspeccionar_docx.py <generado> --diff <control>` — si hay control disponible.
  5. `verificar_admisorio.py <generado>` — se entrega con `APTO`, pegando la salida literal (R-109).
  - Saltarse el paso 1 es lo que convierte un admisorio de minutos en un admisorio de horas.
  - *Lo que NO hay que optimizar:* abrir las 630 plantillas maestras cuesta **1,69 s** medidos.
    No es el cuello de botella y no necesita indice, cache ni base de datos. Optimizar ahi es
    trabajo inventado.

- R-116: **WORD HUERFANO Y SUPERFICIE DE INSTRUCCIONES: LAS DOS CAUSAS DE QUE UN ADMISORIO SE ATASQUE:**
  - *Word huerfano.* `footnote_injector` abre Word por COM. Si el proceso que lo lanzo muere entre
    `Documents.Open` y `word.Quit()`, queda un WINWORD.EXE **sin ventana** con el documento abierto
    y el bloqueo `~$nombre.docx` en la carpeta. El siguiente intento espera indefinidamente.
    Diagnostico: `python scripts/estado_word.py <carpeta>`. El script **informa y no mata**: cerrar
    un Word que puede tener trabajo sin guardar es decision de la persona.
    *Medicion del 14/09/2026:* un WINWORD.EXE sin ventana llevaba 50 minutos vivo con 5,7 s de CPU,
    y un bloqueo `~$` de un expediente anterior seguia en la carpeta del expediente en curso.
  - *Superficie de instrucciones.* Lo que el agente lee antes de empezar llego a **149 KB**, con
    R-103 repetida en **8** archivos y R-108 en **7**. Crecer el corpus de reglas hace el trabajo
    mas lento sin hacerlo mejor. Por eso `REGLAS_DE_APRENDIZAJE.md` y
    `MATRIZ_MAESTRA_PHOENYX_POPPERIANA.md` quedan marcados como **consulta dirigida**: se abren
    para buscar una regla, no se leen enteros al arrancar. La lectura de arranque es `AGENTS.md`.
  - *Falsador:* un admisorio que tarde mas que el anterior sin que el expediente sea mayor.

## 80. MASTER PHOENYX: LO QUE ENSEÑA EL CONTROL APROBADO (R-117 A R-123)

> Origen: diff del 14/09/2026 entre el entregable generado del Expediente 2723-2026 y el
> control aprobado de la CC1 (`ADM 2723-2026 R2 - LSQok.docx`). El generado pasaba
> `verificar_admisorio.py` con `APTO (0 falsadores)` y aun asi divergia del control en
> cuatro puntos que el verificador no mira. Leccion: el verificador falsa lo formalizable;
> el control aprobado falsa el contenido. Ninguno sustituye al otro.

- R-117: **EL NUMERO DE IMPUTACIONES Y EL ARTICULO DE CADA UNA SE COPIAN DEL CONTROL:**
  - *Medicion:* el control imputa **seis** conductas (arts. 18 y 19 en tres hechos; art. 1,
    numeral 1, literal b) y art. 2; **art. 150**; **art. 88, numeral 88.1**). El generado
    imputo **cinco**: refundio el libro de reclamaciones (150) y la falta de respuesta al
    reclamo (88.1) dentro de 18 y 19.
  - Prohibido colapsar dos conductas en un solo articulo para calzar la plantilla base. Si
    la rama de la plantilla no trae el articulo, se inserta desde el donante verificado.
  - *Falsador:* una imputacion del control que en el generado aparezca ausente o subsumida
    en otro articulo.

- R-118: **ORDINAL Y FECHA DE EMISION: LOS DEL CONTROL. LA CONTRADICCION SE ELEVA:**
  - *Medicion:* control RESOLUCION **2** y «Lima, 28 de agosto de 2026»; generado
    RESOLUCION **3** y 14/09/2026, inferidos del escrito de subsanacion.
  - Se redacta con el ordinal y la fecha del control, y el conflicto se lista como punto
    abierto para el instructor. No se resuelve por cuenta propia.
  - *Falsador:* un ordinal o una fecha de emision distintos del control sin constancia de
    elevacion.

- R-119: **REQUERIMIENTO PROBATORIO: LOS INCISOS DEL CONTROL, NI UNO MAS NI UNO MENOS:**
  - *Medicion:* el inciso (i) del control incluye «asi como el cargo de remision de la
    poliza»; el generado lo omitio y anadio incisos propios (Certificado del SOAT, informe
    de auditoria medica, constancia de remision al Instituto Nacional de Rehabilitacion).
  - *Falsador:* un inciso del control ausente del generado, o un inciso anadido que no
    figure en el control ni en el escrito, sin elevacion.

- R-120: **HECHOS: CADA ACTO CON SU FECHA, SIN FUSIONAR:**
  - *Medicion:* el control separa «El 9 de junio del 2026, realizo el envio de la
    solicitud» y «El 11 de junio del 2026, presento la solicitud»; el generado fundio los
    dos actos en un solo inciso con la segunda fecha.
  - *Falsador:* dos incisos de hecho del control reducidos a uno en el generado.

- R-121: **EL CONTROL TAMBIEN FALLA: NO SE COPIAN SUS ERRATAS:**
  - *Medicion:* el control trae «del del Seguro», «articulo 150° 29571» (sin «de la Ley»)
    y «esta debera» con tilde diacritica. Las invariantes del §1 de `AGENTS.md` siguen
    mandando: el control se copia en estructura, no en errata.
  - *Punto abierto medido, no silenciado:* «9 de junio» y «24 de junio» del control tienen
    **0** ocurrencias en el texto extraido de los tres PDF del expediente.
  - *Falsador:* una errata del control reproducida en el generado, o una fecha del control
    ausente del expediente incorporada sin elevacion.

- R-122: **CASO CERRADO = PARO INMEDIATO (ANTIDOTO CONTRA LA DEMORA POR REGENERACION):**
  - Si la carpeta del expediente trae `_ESTADO.md` o `_ORDEN_DE_TRABAJO.md` con «CASO
    CERRADO», el agente **no produce un `.docx` nuevo**: reporta y se detiene.
  - *Medicion:* el Expediente 2723-2026 quedo cerrado a las 03:27 (RES_03) y a las 03:33 ya
    existia un RES_02 regenerado con ordinal y contenido divergentes, pese a que la orden
    decia «NO EJECUTAR ESTA ORDEN». La demora no vino de generar el Word: vino de rehacer
    trabajo cerrado.
  - *Falsador:* un `.docx` nuevo en una carpeta marcada CERRADA despues de la marca.

- R-123: **LA ESPERA DE WORD ES ACOTADA: FALLA RAPIDO, NO ESPERA:**
  - `footnote_injector.procesar_notas` consulta antes de `DispatchEx` si hay
    `WINWORD.EXE` sin ventana; si lo hay, aborta con el PID y el comando exacto para
    cerrarlo, en vez de esperar sin limite. Sigue sin matar procesos: informa.
  - *Medicion del 14/09/2026, 03:41:* seis procesos de Antigravity consumiendo **1,3 s y
    2,4 s de CPU en 3 s** (trabajando en ese momento) y un `WINWORD.EXE` huerfano vivo
    desde las 02:30 con el bloqueo `~$S_02_2662-2026_CC1_ADMISORIO.docx` en la carpeta del
    expediente en curso. Ambos se detuvieron y el bloqueo se retiro.
  - *Falsador:* una generacion que pase mas de un minuto sin producir salida nueva ni error.

### 80.1 / R-124. Contradiccion declarada, no resuelta: R-110 contra el control 2723

- R-110 exige que las conductas del proveedor se redacten **mediante atribucion al
  denunciante** («Senalo que...», «Preciso que...», «Manifesto que...») o en potencial.
  Su falsador es un inciso con verbo asertivo directo atribuido al denunciado.
- El control 2723, en cambio, narra **en tercera persona directa y sin atribucion**:
  «El 24 de marzo del 2025, sufrio un accidente...», «El 9 de junio del 2026, realizo el
  envio...», «El 24 de junio del 2026, la compania aseguradora despacho una comunicacion
  notarial...». Bajo el falsador de R-110, ese control no la cumple.
- El generado, por su parte, mezcla los dos estilos: hechos en directo («El 24 de marzo
  de 2025, sufrio...») y hechos con atribucion («Senalo que el 11 de junio...»,
  «Manifesto que el 27 de junio...»).
- **No se resuelve aqui.** Se eleva al instructor: o R-110 acota su dominio (p. ej. solo
  cuando el hecho consta unicamente en la declaracion del denunciante), o el estilo del
  control 2723 es el que manda y R-110 se reescribe. Una regla que hay que reinterpretar
  caso por caso dejo de ser regla.

- R-125: **PROHIBIDO EL PDF: EL ENTREGABLE ES WORD (MANDATO DEL INSTRUCTOR, 14/09/2026):**
  - El sistema no convierte, imprime ni exporta a PDF en ningun punto del flujo. La
    conversion era el ultimo consumidor de Word por COM y una de las causas medidas de
    cuelgue: el Expediente 2723-2026 no pudo cerrarla porque un Word huerfano retenia los
    bloqueos.
  - *Falsador:* un `.pdf` producido por el pipeline de admisorios.
  - Plan completo y presupuestos: `docs/PLAN_VELOCIDAD_SIN_COLGARSE.md` (F2; linea base de
    ~12 s de computo total y las cuatro causas de cuelgue con su evidencia).

- R-126: **VERIFICACION CRUZADA DEL VOLCADO: EL EXTRACTOR CORROMPE EL TEXTO:**
  - *Medicion del 14/09/2026 (Expediente 3054-2026):* `_texto_expediente.txt` escribio el
    caracter de reemplazo en cada acento («MART?N» por «MARTIN» con tilde) y convirtio la
    fecha del escrito «17 de agosto de 2026» en **«1274 de agosto de 2026»**. PyMuPDF
    sobre el mismo PDF devuelve los acentos y el «17» correctos: el PDF esta bien y el
    defecto es del extractor (`pypdf`/`pdftotext -layout`).
  - Mientras el extractor no se reemplace, **todo dato critico** —fechas, montos, numeros
    de solicitud o poliza, nombres y numeros de carta— se verifica contra el PDF con
    PyMuPDF antes de entrar al admisorio. Un «1274» en la fecha del escrito es un
    admisorio mal emitido.
  - *Falsador:* un dato del generado que no coincida con la extraccion de PyMuPDF del
    mismo PDF, o una fecha del volcado incorporada sin verificacion cruzada.

## 81. MANDATO DEL INSTRUCTOR DEL 14/09/2026 Y LECCIONES DEL CONTROL 3054 (R-127 A R-132)

> Origen: encargo de la remesa de 13 admisorios y diff entre el generado del Expediente
> 3054-2026 y el control aprobado `ADM 3054-2026 R1 - LSQok.docx`. El mandato del
> instructor manda sobre el control en firma y fecha; el control manda sobre la plantilla
> en imputaciones, escrito y via de notificacion.

- R-127: **FIRMA UNICA (MANDATO): TODOS FIRMAN ANALI, SECRETARIA TECNICA (e):**
  - Todos los admisorios firman **LUISA ANALI SILVA MALPARTIDA** con el cargo
    `Secretaria Técnica (e)`. **Ninguno** firma EVELING ROA QUISPE. **Ninguno** usa la
    designacion `Ad Hoc`. Esta regla **sustituye a R-103**.
  - *Falsador:* una firma distinta de Anali, el cargo sin `(e)`, o la aparicion de
    `Ad Hoc` o de `EVELING ROA QUISPE` en el documento.

- R-128: **FECHA UNICA DE LA REMESA (MANDATO): 14 DE SETIEMBRE DE 2026:**
  - Todos los admisorios de esta remesa llevan `Lima, 14 de setiembre de 2026`, sin
    importar las fechas que traigan las cedulas de notificacion.
  - *Falsador:* cualquier otra fecha de emision.

- R-129: **LAS CEDULAS DE NOTIFICACION DE LA CARPETA MANDAN EN PARTES Y DOMICILIO:**
  - Cada carpeta de expediente trae sus cedulas. De ellas se toman las **partes
    procesales** y el **domicilio procesal** (son correctos). Sus **fechas se ignoran**
    (R-128). La **via** de notificacion se toma de la cedula: si dice Casilla
    Electronica, se usa el parrafo TIPO 1 (cinco dias); si dice correo, TIPO 2; si dice
    domicilio, TIPO 3.
  - *Falsador:* notificar por una via distinta de la que senala la cedula, o consignar
    un domicilio procesal distinto del de la cedula.

- R-130: **SUBSUNCION POR CONDUCTA, TAL COMO LA Fija EL CONTROL (LECCION 3054):**
  - El control 3054 imputa **seis** conductas, cada una con su articulo: arts. 18 y 19
    (denegatoria del 14/07); arts. 18 y 19 (denegatoria del 5/08); **literal b) del
    articulo 56** (metodos comerciales coercitivos: remitir la poliza pese a la
    solicitud); art. 1, numeral 1, literal b) y art. 2 (omision de informar el
    arrepentimiento); **literal e) del articulo 47** (no entregar el resumen de
    cobertura); **numeral 88.1 del articulo 88** (atencion deficiente del reclamo).
  - Prohibido refundir dos conductas en un articulo, o imputar la lista larga del
    escrito en lugar de la subsuncion depurada del control.
  - *Falsador:* una conducta del control ausente o subsumida en otro articulo.

- R-131: **HECHOS EN NARRACION DIRECTA CON EL ALIAS (LECCION 3054):**
  - El control narra los actos del proveedor en indicativo directo y con el alias del
    encabezado: «Vivir Seguros remitio por correo electronico la Poliza...». No usa
    «senalo que el proveedor...». El detector automatico de R-110 solo vigila los alias
    de su lista (Rimac, Pacifico, el Banco, la compania aseguradora, la aseguradora, el
    proveedor); usar el alias del encabezado es la forma correcta y ademas verificable.
  - *Falsador:* un inciso de hechos con «la compania aseguradora» o «la aseguradora»
    como sujeto de un verbo en indicativo, en lugar del alias.

- R-132: **FECHA DEL ESCRITO DE DENUNCIA: LA DEL CONTROL. LA CONTRADICCION SE ELEVA:**
  - *Medicion:* el control 3054 consigna «escrito del 24 de agosto de 2026»; la firma
    del PDF (pagina 21, leida con PyMuPDF) dice «Lima, 17 de agosto de 2026». Se redacta
    con la fecha del control y el conflicto se eleva al instructor.
  - *Falsador:* una fecha de escrito distinta de la del control sin constancia de
    elevacion.

- R-133: **PROHIBIDO EL PDF (RECORDATORIO) Y EL `.docx` FUERA DEL REPOSITORIO:**
  - El entregable es el `.docx`; no se genera PDF (R-125). El `.docx` del expediente no
    se commitea: el repositorio es publico y contiene datos personales
    (`guardia_admisorio.py` lo bloquea).

## 82. LA LEY DE LA LATENCIA Y EL PUNTO DE ENTRADA UNICO (R-134 A R-135)

> Origen: medicion del reloj paso a paso sobre la traza real del Expediente 3054-2026
> (14/09/2026), leyendo las marcas de tiempo de cada paso de la base de conversaciones
> del agente. No es una estimacion: es el reloj.

- R-134: **CADA LLAMADA CUESTA ~17,6 s, HAGA O NO TRABAJO. EL PUNTO DE ENTRADA ES UNICO:**
  - **CIFRA CORREGIDA EL 14/09/2026.** La primera version de esta regla decia 7,5 s por
    llamada sobre 157 llamadas. Estaba mal **por un defecto del instrumento, no del
    agente**: `auditar_trayectoria.py` contaba *pasos* de la traza, y una misma llamada
    aparece en varios (la invocacion, el resultado, a veces un eco). Contado por
    identificador de llamada, la sesion del Exp. 3054 fueron **67 llamadas**, no 157, y
    **17 operaciones evitables**, no 70. El auditor ya cuenta por `call_id`.
  - *Medicion corregida:* 1178 s de ventana / **67 llamadas** = **17,6 s por llamada**.
    Los huecos de decision entre pasos suman **6 s en toda la sesion**: el reloj esta
    dentro de las llamadas, no en pensar. El computo util de un admisorio completo es
    **~12 s**. Luego **T ≈ 17,6 s × N**.
  - *Lo que no cambia:* la forma de la ley y su consecuencia. El tiempo lo fija el
    numero de llamadas y la unica palanca es agrupar trabajo por llamada. Lo que cambia
    es la constante, y con ella el presupuesto: **12 llamadas ≈ 3,5 minutos**, no 90 s.
  - *Leccion sobre el propio supervisor:* una metrica que nadie ha falsado no es una
    medicion, es una creencia con decimales. El instrumento se audita como se audita al
    agente.
  - *Mandato:* el caso se abre con `python scripts/admisorio.py preparar <carpeta>` y se
    cierra con `python scripts/admisorio.py entregar <docx> --caso <n>`. La primera
    sustituye a seis llamadas; la segunda, a cuatro. Llamar a `extraer_expediente.py`,
    `verificar_admisorio.py` o `guardia_admisorio.py` por separado esta permitido para
    depurar, pero **cuenta como desperdicio** en el scorecard.
  - *Falsador:* un caso que gaste una llamada en algo que `admisorio.py` ya agrupa, o una
    propuesta de optimizacion justificada en CPU y no en numero de llamadas.

- R-135: **AL CERRAR UN CASO SE DECLARAN N (LLAMADAS) Y T (RELOJ):**
  - Objetivo: **N ≤ 12** y **T ≤ 4 minutos** desde el triaje hasta `ENTREGABLE` en un
    expediente corto. El limite sale de la constante corregida de R-134 (17,6 s × 12 ≈
    3,5 min) mas el computo. Un expediente largo escala con sus paginas: la lectura con
    Lens de todas las paginas (R-137) es parte del coste y no se recorta.
  - **N se cuenta por identificador de llamada**, no por pasos de la traza.
  - *Falsador:* un caso entregado sin declarar N y T, o que supere su presupuesto sin
    causa identificada (numero de paginas, control ausente, contradiccion elevada).

## 83. EL TRIAJE CUENTA PAGINAS, NO TEXTO (R-136)

- R-136: **UN PDF SIN TEXTO NO ES UN PDF SIN PAGINAS:**
  - *Medicion (14/09/2026, remesa de 13 expedientes):* `extraer_expediente.py`
    descartaba **todos** los tramos vacios que devuelve `pdftotext`, no solo el
    form-feed final. Un PDF integramente escaneado no devuelve texto, luego se quedaba
    en **cero paginas** y el triaje lo declaraba resuelto. Asi, `DENUNCIA F.PDF.pdf`
    (Exp. 2893-2026), que tiene **14 paginas escaneadas**, figuraba como 0 paginas y
    **0 pasadas de vision**: el escrito de denuncia entero era invisible para el agente.
  - *Efecto medido en la remesa:* el triaje pasaba de **116 paginas y 0 visiones** a
    **175 paginas y 59 visiones** una vez corregido. Cinco expedientes (2785, 2794,
    2893, 2894, 2899) tienen documentos escaneados.
  - *Mandato:* el numero de paginas lo fija la estructura del PDF (PyMuPDF), no su
    texto. Las paginas sin texto se rellenan vacias para que el triaje las mande a
    vision.
  - *Falsador:* un PDF cuyo conteo de paginas del triaje no coincida con el de PyMuPDF,
    o un expediente con paginas escaneadas que el triaje reporte con 0 visiones.
  - *Por que importa mas que la velocidad:* este defecto no hacia lento al agente, lo
    hacia **redactar sin fuente**. Un escrito invisible es la via mas corta a inventar.

## 84. LECTURA VISUAL UNIVERSAL Y PARTES DE LA CEDULA (R-137 A R-138)

> Mandato del instructor del 14/09/2026, al entregar la remesa de 13 expedientes.
> **R-137 amplia el alcance de R-95 y deroga la excepcion de los PDF nativos.**

- R-137: **CERO OCR. GOOGLE LENS EN TODAS LAS PAGINAS, SIEMPRE:**
  - **Todas** las paginas de **todos** los PDF del expediente se leen con la vision
    **Google Lens de Antigravity**: escaneadas y no escaneadas, con capa de texto y
    sin ella. No hay excepcion por «PDF nativo».
  - **Prohibido el OCR** en cualquier forma: ni tesseract, ni el OCR de un lector de
    PDF, ni ningun motor de reconocimiento optico de terceros. La unica lectura de
    imagen autorizada es Google Lens.
  - El texto embebido que extrae `extraer_expediente.py` **no sustituye** esa lectura:
    es **contraste**. Esta medido que el volcado pierde tildes y corrompe caracteres
    («1274 de agosto» por «17 de agosto de 2026»; «MART?N» por «MARTIN») — R-126.
    **Ante discrepancia entre el volcado y lo que ve Lens, manda Lens.**
  - *Por que, y no es capricho:* la capa de texto de un PDF es lo que el generador
    dijo que puso, no necesariamente lo que la pagina muestra; y la unica forma de
    detectar sellos, firmas, anexos manuscritos, tachaduras y numeros de foja es
    mirar la pagina. Una lectura que no se puede contrastar con la imagen no es
    verificable.
  - *Alcance sobre la eficiencia:* la velocidad **no se busca recortando lectura**.
    Se busca no releyendo, no repitiendo el triaje, no consultando tareas en bucle y
    agrupando comandos (R-134). Leer menos paginas nunca es una optimizacion valida.
  - *Falsador:* una pagina del expediente que no fue leida con Google Lens; el uso de
    cualquier motor OCR; o un dato del admisorio tomado del volcado de texto que
    contradiga lo que muestra la imagen.

- R-138: **LAS PARTES PROCESALES SON, EXACTAMENTE, LAS DE LA CEDULA:**
  - La cedula de notificacion de la carpeta **fija** quienes son las partes, su
    denominacion y su **unica** via de notificacion. No se anade ninguna parte que la
    cedula no notifique, ni se omite ninguna que si notifique.
  - Que el escrito de denuncia **mencione** a otra empresa (el banco donde se pago la
    prima, el corredor que intermedio, la entidad que financio) **no la convierte en
    parte**. Es contexto del relato, no sujeto del procedimiento.
  - Esto **cierra** el asunto: no se eleva, no se consulta, no se «resuelve contra el
    petitorio». La cedula ya lo resolvio.
  - *Falsador:* un admisorio con una parte que la cedula no notifica, una parte de la
    cedula ausente del admisorio, o una parte notificada por dos vias.

## 85. COMO SE CONSTRUYE EL DOCUMENTO (R-139)

> Origen: supervision en vivo del Expediente 3122-2026, 14/09/2026.

- R-139: **NI WORD NI SCRATCH: SE CONSTRUYE CON `construir_admisorio.py`:**
  - *Medicion:* el agente intento construir el admisorio con `win32com` y escribio
    **cinco** scratch sucesivos (`scratch.py`, `scratch_com.py`, `_com2`, `_com3`,
    `_com4`) anadiendo `DisplayAlerts = False` y `try/except` en cada intento. **Diez de
    sus dieciseis minutos** se fueron ahi y el resultado quedo **NO APTO** (R-97 y R-103).
  - **Prohibido `win32com` para construir el admisorio.** Un `.docx` es un ZIP de XML:
    se edita en ~0,3 s sin abrir Word. Word cuesta 8,4 s por apertura y su proceso
    huerfano es la causa medida de que un caso cueste una tarde (R-116, R-123).
  - **Prohibido dejar scratch en la raiz del repositorio.** `admisorio.py entregar` lo
    declara falsador.
  - **El peligro real no es la lentitud, es el residuo.** Sustituir «Pacifico» por
    «Interseguro» deja intacto *todo lo que el redactor no penso en listar*: fechas,
    polizas, apellidos y hechos del caso de origen se quedan dentro con aspecto de dato
    verdadero. Es la forma mas silenciosa de inventar que tiene este sistema. Por eso
    `construir_admisorio.py` **se niega a dar por bueno** el documento si encuentra
    residuo: una clave del mapa sin aplicar o aun presente, el numero de expediente de
    la plantilla, una aseguradora que no es parte del caso, o un marcador `[FALTA: ...]`.
  - *Dos errores medidos de aquel mapa, como muestra de lo que el control atrapa:*
    reemplazar «correo electronico» en todas sus apariciones rompia el parrafo de
    notificacion del denunciante, que **si** se notifica por correo; y el refrendo
    «LSM/JCQ» -> «LSM» era inventado.
  - *Falsador:* un admisorio construido con Word, un `scratch*.py` en la raiz, o un
    documento entregado con la auditoria de residuos en falla.

## 86. COMO SE SUPERVISA (R-140 A R-141)

> Origen: primera remesa supervisada de punta a punta, 14-15/09/2026, trece
> expedientes. El detalle esta en `docs/SUPERVISION_DE_AGENTES.md`.

- R-140: **LA ORDEN OBLIGATORIA SE SIRVE PREPARADA, NO SE ENUNCIA:**
  - *Medicion:* decirle al agente «lee todas las paginas con Google Lens» no basto.
    Se paso **17 llamadas y 6 minutos** averiguando **como** hacerlo, llegando a
    leer el codigo de las propias herramientas del repositorio. Solo lo hizo tras
    una segunda orden que incluia el comando exacto. Cuando el triaje empezo a
    dejar las paginas ya renderizadas en `_paginas/` y la orden de trabajo a listar
    la ruta de cada imagen, el problema desaparecio: 175 paginas de trece
    expedientes renderizadas en **66,6 s** y una sola llamada.
  - *Mandato:* si una regla exige un trabajo, el repositorio entrega ese trabajo
    **hecho** o el **comando exacto** que lo hace. Una regla que obliga al agente a
    inventarse el procedimiento se paga en llamadas y se incumple a la primera.
  - *Corolario para quien escriba reglas nuevas:* antes de anadir una obligacion,
    pregunta que artefacto la vuelve trivial. Si no hay ninguno, la obligacion aun
    no esta lista.
  - *Falsador:* una regla obligatoria cuyo cumplimiento exija al agente descubrir el
    metodo, o un caso en el que se gasten llamadas averiguando **como** cumplir en
    vez de cumpliendo.

- R-141: **EL INSTRUMENTO SE AUDITA COMO SE AUDITA AL AGENTE:**
  - *Medicion, y es incomoda:* mas de la mitad de lo que se le imputo al agente en
    la primera remesa era defecto del supervisor. `auditar_trayectoria.py` contaba
    pasos en vez de llamadas (157 donde habia **67**); `construir_admisorio.py`
    declaraba inexistentes **14 de 19** reemplazos por un `<w:t[^>]*>` que capturaba
    `<w:tab>`; `verificar_admisorio.py` tenia los cinco patrones de R-110 con un
    caracter de retroceso y **llevaba sin comprobar nada**; el vigilante contaba
    como busqueda recursiva el texto del propio encargo.
  - *Mandato:* **toda metrica nueva nace con su falsador y con una prueba que la vea
    fallar de verdad.** Una regla que nunca falla no es una regla que se cumple: es
    una regla que no se esta ejecutando. Un diagnostico que miente cuesta mas que no
    tener diagnostico, porque manda a corregir lo que ya estaba bien.
  - *Procedimiento:* antes de acusar al agente de incumplir, reproduce el hallazgo a
    mano sobre el artefacto. Si el instrumento y la lectura directa discrepan, el
    sospechoso es el instrumento.
  - *Falsador:* una comprobacion que jamas haya dado FALLA sobre ningun documento, o
    un hallazgo automatico que no se haya contrastado contra la fuente antes de
    exigir la correccion.

- R-142: **ANTES DE CORREGIR EL TERCER SINTOMA, MIRA DE DONDE ARRANCA EL AGENTE:**
  - *Medicion:* el workspace de Antigravity era `C:/Users/D/_ConfigIA/.resadmi`, una
    carpeta con una sola subcarpeta, y **ningun proyecto suyo apuntaba al
    repositorio**. Casi todos sus fallos eran consecuencias de eso: no cargaba el
    `AGENTS.md` correcto porque su raiz era otra; buscaba los scripts con `-Recurse`
    por todo el perfil porque no estaban donde miraba; se iba a otros proyectos
    porque desde una carpeta vacia cualquier ruta parece igual de buena. Se tardo
    una remesa entera en mirarlo, corrigiendo sintomas de uno en uno.
  - *Mandato:* al tercer fallo del mismo agente, se comprueba su punto de partida
    antes de escribir otra correccion. `python scripts/orquestar.py sanear` lo
    dice.
  - *Corolario incomodo:* **una causa raiz que solo se puede parchear se declara
    como tal.** El `AGENTS.md` de redireccion que se dejo en el workspace
    equivocado es un parche, no el arreglo, y depende de que el agente lo lea y lo
    obedezca --que es justo lo que no se puede dar por hecho--. El arreglo es una
    accion manual, una vez: anadir el repositorio como workspace. Esta escrito en
    `docs/PLAN_WORKSPACE_ANTIGRAVITY.md` para que el parche no se confunda con la
    solucion.
  - *Falsador:* tres correcciones consecutivas al mismo agente sin haber
    comprobado su workspace, o un parche presentado como arreglo de causa raiz.

## 87. SOLO SE IMPUTA COMO IMPUTAN LOS MODELOS (R-143)

> Mandato del instructor, 15/09/2026.

- R-143: **PROHIBIDA TODA IMPUTACION QUE NO EXISTA EN EL CORPUS:**
  - No se inventan combinaciones de articulos, ni se mezclan imputaciones
    distintas en una sola, ni se imputa por una norma que ninguna resolucion del
    corpus haya usado para ese tipo de conducta.
  - *Por que no es una preferencia de estilo:* la imputacion fija el **objeto del
    procedimiento**. De ella dependen los descargos, la carga de la prueba y el
    marco sancionador. Una combinacion inventada --aunque cada articulo suelto sea
    correcto-- formula un cargo que la Comision nunca ha hecho, y obliga al
    administrado a defenderse de algo que en la practica no existe.
  - *Medicion:* `catalogar_imputaciones.py` extrajo de las 630 plantillas
    **64 combinaciones de normas** y **212 enunciados** distintos. El catalogo vive
    en `docs/catalogo_imputaciones.json` con la frecuencia de cada una y las
    plantillas donde aparece. La mas usada, con diferencia, es `art.18|art.19` --el
    deber de idoneidad-- con 1.430 apariciones en la considerativa y 1.243 en la
    resolutiva.
  - *Comprobacion:* la prueba R-143 de `verificar_admisorio.py` extrae las normas
    de cada enunciado `Presunta infraccion...` del documento --en la considerativa
    y en la resolutiva, que se escriben distinto-- y rechaza la que no figure en el
    catalogo. Verificado: acepta `art.18|art.19`, y rechaza tanto
    `art.18|art.19|art.77` como `art.18|art.19|art.88|num.88.1`, que es exactamente
    el error medido en el control 2723-2026 (refundir el 88.1 dentro de 18 y 19 en
    lugar de imputarlo aparte).
  - *Como se amplia el catalogo:* no se amplia a mano. Entra una resolucion nueva
    al corpus y se vuelve a ejecutar `catalogar_imputaciones.py --guardar`. Si una
    combinacion hace falta y el corpus no la tiene, **se eleva al instructor**: eso
    es una decision de criterio, no de redaccion.
  - *Falsador:* un admisorio con una combinacion de normas ausente del catalogo, o
    un catalogo modificado a mano en vez de regenerado desde el corpus.

## 88. FORMA MEDIDA: FUENTE, ALINEACION, ESPACIADO Y ENCUADRE (R-144)

> Mandato del instructor, 15/09/2026. Los valores salen de **medir 120 plantillas**,
> no de la memoria documentada. Donde las dos discrepan, manda el corpus.

- R-144: **LA FORMA NO SE ELIGE, SE HEREDA DEL CORPUS:**
  - **Fuente `Arial Narrow`**: 59.337 de 59.370 runs con fuente declarada. Solo se
    tolera `Segoe UI Symbol` para simbolos.
  - **Alineacion justificada o centrada, nunca a la izquierda ni a la derecha**:
    10.412 parrafos justificados, 421 centrados, **cero** alineados a la izquierda.
    El desalineamiento es el falsador mas visible que existe: un parrafo a la
    izquierda dentro de un cuerpo justificado se ve desde el otro lado de la sala y
    delata que el documento se manipulo fuera del flujo.
  - **Interlineado sencillo (`240`)**: el `276` aparece en el 1 % y es desviacion.
  - **Encuadre `3,0 / 3,0 / 2,5 / 2,5 cm`** (izq/der/sup/inf). *Correccion medida:*
    `MEMORIA_ESTILO_VISUAL_PAGINAS.md` afirmaba un margen derecho de **2,50 cm**;
    el corpus mide **3,00 cm** en 113 de 116 secciones. La memoria estaba mal.
  - *Calibracion:* de 40 plantillas del corpus tomadas al azar, **37 pasan** y las
    3 que fallan son desviaciones reales (dos con runs en `Arial`, una con
    interlineado 276). La regla caza anomalias, no ruido.
  - *Falsador:* un run en fuente ajena, un parrafo alineado a izquierda o derecha,
    un interlineado distinto de 240 o unos margenes distintos de los medidos.

- R-145: **LOS SUB-INCISOS DEL REQUERIMIENTO VAN EN ROMANOS MINUSCULOS:**
  - *Medicion sobre 150 plantillas:* **72 requerimientos usan `(i) (ii) (iii)`** y
    **uno solo** usa `(a) (b)`. No hay empate que discutir.
  - *Cierra una contradiccion abierta desde el primer analisis:* R-99 enunciaba
    «sub-incisos (a), (b), (c), (d)» mientras el ejemplo canonico que ella misma
    adjuntaba usaba `(i)` y `(ii)`. Se resolvio midiendo, que es como habia que
    resolverlo: **gana `(i) (ii)`**.
  - *Falsador:* un requerimiento con incisos en letras.

## 89. ESQUELETO Y ORTOGRAFIA FORENSE DE LOS ORDINALES (R-146)

> Medido sobre los **603 admisorios reales** del corpus. Correccion de censo: de
> las 630 plantillas, 27 son resoluciones de confidencialidad o decretos cortos.
> Por eso ninguna medicion de anatomia llegaba al 100 %: el techo del 96 % no era
> incumplimiento, era el denominador mal puesto.

- R-146: **LA RESOLUTIVA SIGUE LA SECUENCIA DEL CORPUS Y ESCRIBE COMO EL CORPUS:**
  - Secuencia medida: PRIMERO admitir a tramite (90,0 %) · SEGUNDO medios
    probatorios (91,4 %) · TERCERO personeria y MYPE (89,6 %) · CUARTO correr
    traslado (88,7 %) · QUINTO requerimiento de informacion (86,6 %) · SEXTO
    sancion hasta 450 UIT (90,9 %) · SETIMO costas y gastos · OCTAVO conciliacion
    (72,3 %) · NOVENO reserva o medida complementaria · DECIMO acuse de recibo
    (92,9 %). A partir del DECIMO, **un ordinal por parte a notificar**.
  - **Ortografia forense:** el corpus escribe `SETIMO` (579 veces) y no `SEPTIMO`
    (12); compone `DECIMO PRIMERO` (485) y `DECIMO SEGUNDO` (152), y **nunca** usa
    `UNDECIMO` ni `DUODECIMO` --cero apariciones--.
  - *Calibracion:* 57 de 57 admisorios del corpus pasan. Y la regla **no es vacia**:
    rechaza `SEPTIMO`, rechaza `UNDECIMO` y rechaza una resolutiva desordenada.
    Comprobado en negativo antes de darla por buena, que es lo que no se hizo con
    R-110 (R-141).
  - *Un falso positivo que costo encontrar:* buscar los ordinales en el texto
    corrido hacia saltar la regla con la palabra «tercero» de la prosa --7 de 57
    plantillas--. Solo cuentan los ordinales que **encabezan** un parrafo.
  - *Falsador:* un ordinal fuera de secuencia, o escrito en una forma que el corpus
    no usa.

## 90. POR QUE DIFIEREN LOS MODELOS (R-147)

- R-147: **LAS DIFERENCIAS ENTRE ADMISORIOS SON ESTRUCTURALES, NO DE ESTILO:**
  - **La via de notificacion la fijan las partes**, no el redactor: persona natural
    -> correo (2 dias); aseguradora o banco con Casilla -> Casilla Electronica (5
    dias); parte sin canal electronico -> domicilio procesal. Medido: `casilla +
    correo` es la combinacion dominante en **todos** los tipos de denunciado,
    porque el reparto tipico es una empresa con casilla y un consumidor con correo.
    El domicilio procesal aparece en el **6,8 %**.
  - **El numero de ordinales no es libre:** hay uno de acuse de recibo por cada
    parte a notificar. De ahi que un admisorio tenga 10, 11 o 12.
  - Otras diferencias con su causa medida: libro de reclamaciones **7,8 %** (solo
    si la conducta lo involucra, art. 150); medida correctiva **91,9 %** (falta
    cuando el denunciante no la pidio); apertura «Mediante el escrito» **79,8 %**
    (el resto abre por subsanacion o por traslado de otra comision).
  - *Consecuencia practica:* ante una diferencia entre el modelo y el caso, la
    pregunta no es «que estilo prefiero» sino **que hecho estructural la causa**.
    Si no hay ninguno, la diferencia es un error.
  - *Falsador:* una via de notificacion que no corresponda a la que la cedula fija
    para esa parte, o un numero de ordinales de acuse distinto del numero de partes.

El mapa visual completo esta en `docs/ANATOMIA_DEL_ADMISORIO.md`.

## 91. LO QUE EL CORPUS NO HACE (R-148)

> Prohibiciones derivadas **por ausencia**, medidas sobre los 593 admisorios que
> quedan tras retirar las 27 plantillas que no eran admisorios. El detalle visual,
> apartado por apartado, esta en `docs/COMO_NO_SE_REDACTA.md`.

- R-148: **UNA PROHIBICION SIN FRECUENCIA DETRAS ES UNA OPINION:**
  - **Absolutas (0 de 593):** `tras` (se escribe «luego de»), `esposo/esposa` (se
    escribe «conyuge»), «induccion a error» (se canaliza por arts. 1.1.b y 2) y el
    `D.S. 004-2019-JUS` (rige el 006-2026-JUS, presente en el 97,3 %).
  - **Cuasi-absolutas (1 de 593, 0,17 %):** `doctor` (se escribe «medico»),
    `difunto`/`occiso`/`finado` (se escribe «el causante»), `carro`/`auto` (se
    escribe «vehiculo con Placa de Rodaje»), y el monto con punto de miles.
  - **CORRECCION DE UNA REGLA MAL ENUNCIADA:** estaba escrito que en los hechos se
    prohibian los calificativos «indebidamente», «arbitrariamente» y «vulnerando
    la ley». El corpus lo desmiente: **«indebidamente» aparece en 149 de 593
    admisorios (25,1 %)**. Prohibirlo haria fallar a uno de cada cuatro documentos
    reales de la Comision. Cuando una regla hace fallar al corpus, esta mal la
    regla, no el corpus. «arbitraria» (2,4 %) y «vulnerando/incumpliendo» (1,5 %)
    son infrecuentes, no prohibidos.
  - **SEGUNDA CORRECCION:** tampoco es cierto que todo hecho deba ir bajo
    atribucion al denunciante. Las formulas de estilo indirecto --«indico que»
    (25,6 %), «senalo que» (12,3 %), «preciso que» (2,4 %), «manifesto que»
    (2,0 %)-- suman ~40 %. **El 60 % narra en indicativo directo con el alias.**
    Conviven las dos formas, y R-110 solo debe perseguir el indicativo **sin**
    ninguna de las dos marcas.
  - *Calibracion:* 0 de 60 plantillas del corpus incumplen R-148, y la regla
    rechaza «tras», «esposa», «induccion a error» y «el difunto». Probada en los
    dos sentidos (R-141).
  - *Falsador:* un termino de los niveles absoluto o cuasi-absoluto dentro de un
    admisorio; o una prohibicion nueva anadida a este archivo sin la frecuencia
    medida que la sostenga.

## 92. FORMAS CANONICAS POR APARTADO (R-149)

- R-149: **CADA APARTADO TIENE SU FORMULA, MEDIDA:**
  - **Hechos, apertura:** «Mediante el escrito del [fecha], el senor [APELLIDO]
    denuncio a [PROVEEDOR]...» --**78,2 %**--. Las variantes abren por subsanacion
    o por traslado de otra comision.
  - **Imputacion, modo verbal:** condicional `habria` en **591 de 593 (99,7 %)**.
    El indicativo prejuzga el fondo antes de los descargos: es el error mas grave
    del apartado y el unico que el modo verbal delata por si solo.
  - **Requerimiento, verbo:** `presentar` --«presentar copia de...» esta en el
    **99,7 %**--. `remitir` (4 de 593) e `informar sobre si` (7 de 593) son
    residuos, no formas alternativas. Sub-incisos `(i) (ii)`, nunca letras (R-145).
  - *Falsador:* un requerimiento que ordene «remitir» en vez de «presentar», o una
    imputacion en indicativo.

## 93. IMAGENES: PROCEDENCIA SELLADA Y LECTURA CON LENS (R-150)

> Mandato del instructor, 15/09/2026, al cerrar el riesgo residual de las capturas.

- R-150: **NINGUNA IMAGEN ENTRA SIN SELLO, Y TODA IMAGEN SE MIRA CON LENS:**
  - *El agujero:* ninguna guardia de texto mira dentro de una imagen. Entraron
    1.042 capturas al repositorio; iban tachadas en origen, pero nada impedia que
    alguien anadiera despues una captura a mano, sin tachar, y **nada la habria
    detenido**. Un PNG de un admisorio lleva exactamente los mismos datos que el
    `.docx`; lo unico que cambia es que ningun `grep` los ve.
  - *Cierre por procedencia:* `capturar_referencias.py` sella cada PNG que genera
    con su origen en un chunk de texto del propio archivo. `guardia_admisorio.py`
    bloquea toda imagen sin ese sello. Verificado en los dos sentidos: la sellada
    pasa, la anadida a mano se bloquea.
  - *El sello no sustituye a mirar.* Prueba que la imagen paso por el tachado
    automatico, no que el tachado sea correcto --el apellido «de Pastor» sobrevivio
    a una version del patron--. Por eso **toda imagen que entre al repositorio se
    revisa con Google Lens antes de publicarse**, tenga o no capa de texto detras,
    sea escaneo o sea render: R-137 no distingue, y aqui tampoco.
  - **Cero OCR, sin excepcion.** Ni para comprobar un tachado, ni para leer una
    captura, ni para verificar una firma. La unica lectura de imagen autorizada es
    Google Lens.
  - *Falsador:* una imagen rastreada sin sello de procedencia, o una captura
    publicada sin constancia de haberse mirado.

## 94. EN ESPERA, DECLARADO (no implementar hasta que el instructor decida)

- **Firma y refrendo de los casos de Rimac.** El instructor mando que los
  admisorios contra Rimac los firme LUISA ANALI SILVA MALPARTIDA como **Secretaria
  Tecnica Ad Hoc**, y que bajo esa firma --y bajo la de Eveling-- vaya `LSQ/DCQ` a
  tamano 8 como maximo.
  - *Lo medido, y por eso queda en espera:* en los 593 admisorios del corpus,
    «Ad Hoc» aparece **0 veces** y `LSQ/DCQ` aparece **0 veces**. Lo que si existe
    es `LSM/JCQ` (292), `LGP/JCQ` (234) y `LSM/LCG` (24). El tamano 8 pt si lo
    confirma el corpus: 1.291 apariciones contra 90 a 9 pt.
  - *La duda concreta, pendiente de respuesta:* si `LSQ/DCQ` sustituye a `LSM/JCQ`
    en **todos** los admisorios o solo en los de Rimac con firma Ad Hoc.
  - Cuando se resuelva, se implementa como **mandato que vence al corpus**, igual
    que la fecha unica de la remesa, y se deja declarado que no es un patron
    extraido sino una orden. No se implementa antes: una regla de firma a medias
    es peor que ninguna.
  - *Nota para el que lea esto mas tarde:* R-127 afirmaba que «ninguno firma
    EVELING ROA QUISPE». Es falso para el corpus --lo hacen **494 de 593**-- y solo
    era cierto para los admisorios que generamos nosotros. La regla estaba mal
    enunciada y se corrige aqui.


---

## R-151 — LA CASILLA ELECTRONICA TIENE TRES REQUISITOS

**Mandato del instructor, 18/09/2026.**

Solo procede notificar a Casilla Electronica cuando el registro en el padron de
aceptacion de Terminos y Condiciones cumple **los tres**:

1. estado **ACTIVA** (no de baja),
2. **numero de e-casilla**,
3. **telefono movil registrado y no vacio**.

Si falta cualquiera, la casilla esta **prohibida**: la parte se notifica por
correo electronico o por domicilio procesal, segun la cedula.

**Condicion necesaria, no suficiente.** Estar habilitado no obliga a usar la
casilla —la via la fija la cedula (R-129)—, pero no estarlo la prohibe.

**Medicion (padron del 17/09/2026, 30 104 registros):** 13 244 registros activos
(44 %) no tienen telefono movil. Entre los proveedores de la CC1 **no admiten
casilla**: Rimac Seguros y Reaseguros (de baja), Banco de Credito del Peru,
Banco Ripley, Banco Pichincha (de baja), Financiera Proempresa, Fovipol, Caja
Arequipa (de baja), Caja Ica, tres AFOCAT y dos Sub CAFAE.

**Corroboracion independiente.** El padron y el corpus de 593 plantillas son dos
fuentes distintas y coinciden en las tres que se pueden cruzar: Rimac por correo
137 de 137, BCP 28 de 29, Ripley 2 de 2. Dos instrumentos independientes que
miden lo mismo es la mejor corroboracion que este sistema puede dar.

**Fuente publicada:** `docs/casillas_habilitadas.json`, generado por
`scripts/filtrar_casillas.py`. El padron **no se versiona**: trae datos
personales de consumidores y el repositorio es publico.

*Falsador:* un admisorio que notifique a Casilla Electronica a un proveedor que
`docs/casillas_habilitadas.json` marca como no habilitado. Lo comprueba
`prueba_r151_casilla_habilitada` en `scripts/verificar_admisorio.py`, y se
verifico en los dos sentidos: caza los originales de los expedientes 2939 y 3057
—que notificaban a Rimac por casilla— y deja pasar los doce corregidos.

---

## R-152 — EL AGENTE TRABAJA ANCLADO AL REPOSITORIO O NO TRABAJA

**18/09/2026.** Consecuencia operativa de R-142.

`AGENTS.md` solo gobierna si se ha cargado desde la raiz de este repositorio.
Antigravity arrancaba en `_ConfigIA/.resadmi`, y desde ahi no existen ni las
reglas, ni los scripts, ni las plantillas.

La version anterior confiaba en un archivo de redireccion. Eso es una
**instruccion**, y este sistema tiene medido lo que valen las instrucciones que
dependen de que el agente se acuerde: se le ordeno leer con Lens y la tanda
siguiente entrego con cero toques a imagen.

Ahora es una **puerta**: `scripts/comprobar_anclaje.py` verifica la raiz y el
directorio de trabajo, y `admisorio.py preparar` —el paso 1 de todo flujo— la
llama y **se detiene** si falla. Hay ademas punteros en `.antigravity/` y
`.agent/` que no repiten ni una regla: solo dicen donde estan y que hay que
pararse.

*Falsador:* un admisorio producido por un flujo que arranco fuera del
repositorio sin que la puerta lo detuviera.

---

## R-153 — CALIBRACION DE NOTAS AL PIE: SUPERINDICE EXPLICITO Y ESTILO REFDENOTAALPIE

**21/09/2026.** Mandato estricto de forma, diseño y encuadre visual.

En la renderización tipográfica de Microsoft Word y visores de documentos, una llamada de nota al pie (`<w:footnoteReference>`) o su referencia dentro del cuerpo de notas (`<w:footnoteRef/>`) puede descender a la línea base y mostrarse al tamaño regular del texto (p. ej., `Código)2,` en lugar de `Código)²,`) si el run no declara explícitamente la elevación vertical.

**Invariante técnica XML:**
1. En `word/document.xml`: todo run `<w:r>` que contenga `<w:footnoteReference>` debe contener en su `<w:rPr>`:
   - `<w:rStyle w:val="Refdenotaalpie"/>`
   - `<w:vertAlign w:val="superscript"/>`
2. En `word/footnotes.xml`: todo run `<w:r>` que contenga `<w:footnoteRef/>` debe contener en su `<w:rPr>`:
   - `<w:rStyle w:val="Refdenotaalpie"/>`
   - `<w:vertAlign w:val="superscript"/>`
   - `<w:sz w:val="16"/>` (equivalente a 8 pt)
3. En `word/styles.xml`: los estilos de carácter `Refdenotaalpie` y `FootnoteReference` deben tener definido `<w:vertAlign w:val="superscript"/>`.

*Falsador:* cualquier documento en el cual una llamada de nota al pie o número de nota al pie carezca de `<w:vertAlign w:val="superscript"/>`. Lo comprueba y refuta `prueba_r153_superindice_notas` en `scripts/verificar_admisorio.py`.

---

## R-154 — PROHIBICION TOTAL DE RESALTADOS DE COLOR

**21/09/2026.** Mandato estricto de acabado institucional y diseño profesional.

Queda estrictamente prohibida la presencia de etiquetas `<w:highlight>` en cualquier archivo XML del paquete `.docx` (`document.xml`, `footnotes.xml`, `header*.xml`, `footer*.xml`, `styles.xml`, etc.). Ningún texto, variable o número de folio puede entregarse con sombreado o resaltado amarillo, verde o de cualquier color.

El normalizador popperiano `scripts/normalizar_plantillas_popperianas.py` purgó 848 etiquetas de resaltado en las 596 plantillas del repositorio, eliminando de raíz la herencia de marcas residuales de edición.

*Falsador:* la detección de al menos una etiqueta `<w:highlight>` en cualquier parte XML del `.docx`. Lo comprueba y refuta `prueba_r154_cero_resaltados` en `scripts/verificar_admisorio.py`.

---

## R-155 — FORMULA OBLIGATORIA DE TRASLADO DE RESOLUCION Y DESCARGOS (DEROGACION DE FORMULAS HISTORICAS A Y B)

**21/09/2026.** Mandato imperativo del instructor.

Quedan formalmente derogadas e invalidadas todas las fórmulas históricas de traslado:
1. **Fórmula A (derogada):** fórmula estándar que rezaba `"...correr traslado de la denuncia interpuesta el [FECHA], a [DENUNCIADO], para que... presente [o presenten] sus descargos en un plazo no mayor de cinco (5) días hábiles contados desde la notificación."`
2. **Fórmula B (derogada):** fórmula con cita desfasada o errónea al artículo 233 / numeral 233.1 de la LPAG.

**Regla de Oro R-155:** El artículo resolutivo de traslado (habitualmente `CUARTO:` o `QUINTO:`) **NUNCA debe quedar vacío**, y debe redactarse **literal e invariablemente** con arreglo a las siguientes dos fórmulas oficiales:

### A. Para un solo denunciado (Singular):
> `CUARTO: correr traslado de la presente resolución a [DENUNCIADO] para que, de conformidad con lo dispuesto por el artículo 26° de la Ley sobre Facultades, Normas y Organización del Indecopi, aprobado por Decreto Legislativo N° 8079, presente sus descargos sobre la imputación de cargos realizada en un plazo no mayor a cinco (5) días hábiles contado a partir del día siguiente de la notificación de la presente resolución, vencido el cual, el Secretario Técnico declarará en rebeldía a los denunciados que no lo hubieran presentado. Debe precisarse que de conformidad con lo establecido por el artículo 223° del Texto Único Ordenado de la Ley N° 27444, Ley del Procedimiento Administrativo General, las alegaciones y los hechos relevantes de la reclamación, salvo que hayan sido específicamente negadas en la contestación, se tendrán por aceptadas o meritadas como ciertas.`

### B. Para dos o más denunciados (Plural):
> `[CUARTO o QUINTO]: correr traslado de la presente resolución a [DENUNCIADO 1] y [DENUNCIADO 2] para que, de conformidad con lo dispuesto por el artículo 26° de la Ley sobre Facultades, Normas y Organización del Indecopi, aprobado por Decreto Legislativo N° 8079, presenten sus descargos sobre la imputación de cargos realizada en un plazo no mayor a cinco (5) días hábiles contado a partir del día siguiente de la notificación de la presente resolución, vencido el cual, el Secretario Técnico declarará en rebeldía a los denunciados que no lo hubieran presentado. Debe precisarse que de conformidad con lo establecido por el artículo 223° del Texto Único Ordenado de la Ley N° 27444, Ley del Procedimiento Administrativo General, las alegaciones y los hechos relevantes de la reclamación, salvo que hayan sido específicamente negadas en la contestación, se tendrán por aceptadas o meritadas como ciertas.`

**Exigencias de Formato Institucional:**
- Rótulo ordinal en negrita (`CUARTO:` o `QUINTO:`).
- Cuerpo del párrafo sin negrita.
- Tipografía `Arial Narrow` 10 pt.
- Interlineado sencillo (línea 240).
- Alineación justificada (`both`).
- Sangría resolutiva institucional (`left="567"`, `hanging="567"`).

*Falsador:* cualquier documento que:
1. Omita el artículo resolutivo de traslado.
2. Contenga la fórmula derogada de cómputo `"contados desde la notificación"` o cita al `"numeral 233.1"` / `"artículo 233"`.
3. Altere la redacción literal de los descargos, el apercibimiento de rebeldía por el Secretario Técnico, o la cita legal al artículo 223° del TUO de la LPAG (Ley 27444).
Lo comprueba y refuta `prueba_r155_formula_traslado` en `scripts/verificar_admisorio.py`.

