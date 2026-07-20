# MATRIZ DE APRENDIZAJE Y REGLAS DE REDACCIÓN (ANTIGRAVITY)
*Documento autogenerado para consolidar las instrucciones de "Lo que se debe hacer" (DOs) vs "Lo que NO se debe hacer" (DONTs) en la elaboración de resoluciones admisorias.*

## ✅ LO QUE SE DEBE HACER (DOs)

1. **Tipificación estricta de Falta de Información:** Cuando se detecte una falta de información (ej. no entrega de constancia MTC, falta de respuesta a reconsideraciones), la imputación DEBE referirse exacta y literalmente a: `"artículo 1, numeral 1, literal b) y al artículo 2 del Código"`.
2. **Unificación de Sujetos Procesales (Notificaciones):** Si dos o más sujetos (ej. denunciante y denunciado) van a ser notificados por la **misma vía** (ej. correo electrónico), se debe unificar el mandato en un **único párrafo** resolutivo utilizando conjugaciones en plural (ej. `reciban`, `efectúen`, `notificarles`).
3. **Fidelidad a las Plantillas de Notificación:**
   - **Correo Electrónico:** Plazo de dos (2) días hábiles para confirmar recepción. Citar el "artículo 20" (sin símbolo de grado °).
   - **Casilla Electrónica:** Plazo de cinco (5) días hábiles para confirmar acuse de recibo. 
   - **Domicilio Físico / Procesal:** Plazo de dos (2) días hábiles para señalar un correo electrónico autorizando recibir notificaciones por dicho medio.
4. **Respeto a la Estructura Documental:** Mantener el formato íntegro del documento base (fuente Arial Narrow, tamaño 11, alineación justificada, sin resaltados residuales verdes, márgenes y viñetas romanas alineadas).
5. **Control de Redundancia:** Aplicar revisión de coherencia y congruencia evitando repetir palabras de transición como "Asimismo" en párrafos consecutivos de imputación.

## ❌ LO QUE NO SE DEBE HACER (DONTs)

1. **PROHIBIDO IMPUTAR EL ARTÍCULO 24:** Bajo ninguna circunstancia se debe imputar infracciones al artículo 24 del Código.
2. **PROHIBIDO IMPUTAR INDUCCIÓN AL ERROR:** Nunca se debe tipificar una conducta como "inducción al error". Siempre canalizar los problemas informativos a través del Artículo 1, numeral 1, literal b) y Artículo 2.
3. **NO VULNERAR EL PRINCIPIO NON BIS IN IDEM:** Está terminantemente prohibido imputar dos infracciones distintas por un mismo hecho (por ejemplo, la falta de entrega de un contrato o póliza corresponde solo al artículo 47 y NO a Idoneidad - artículos 18 y 19).
4. **NO INVENTAR VÍAS DE NOTIFICACIÓN:** Se debe analizar rigurosamente la cédula de notificación. Si la empresa (ej. Rímac) tiene consignado un correo electrónico en la cédula, no se le debe imponer una plantilla de Casilla Electrónica.
5. **NO MODIFICAR TEXTOS TABULARES:** Respetar los cuadros iniciales sin aplicar sombreados o alteraciones indebidas.
6. **NO SOBRETIPIFICAR LA FALTA DE INFORMACIÓN EN SEGUROS:** Si la denuncia alega que se rechazó la cobertura usando una cláusula de exclusión ambigua o poco precisa (ej. estado de ebriedad como sujeto pasivo), el hecho se subsume enteramente como una presunta infracción al deber de **Idoneidad** (Artículos 18° y 19°) por negativa injustificada de cobertura. No se debe tipificar doblemente como "falta de información".

## 📝 REGLAS ESTRICTAS DE ESTRUCTURA Y FORMATO (WORD)

1. **Uso Obligatorio de Plantillas Base:** NUNCA se debe generar un documento Word desde cero. Para conservar las imágenes del encabezado (Logo Indecopi a la izquierda, Firma digital a la derecha) y los formatos nativos, se debe abrir un modelo existente (ej. `MODELO xxxx exp. ADM...docx`), vaciar su contenido corporal (manteniendo Headers y Footers intactos) y luego inyectar el nuevo texto.
2. **Encabezado en Cuerpo (Header-Body):** La frase `"SECRETARIA TÉCNICA DE LA COMISIÓN DE PROTECCIÓN AL CONSUMIDOR 1 SEDE CENTRAL"` debe ir alineada a la derecha, en cursiva y negrita en la parte superior del documento (después del Header con imágenes).
3. **Cuerpo de Metadatos (Sin Tablas):** Los datos iniciales (`EXPEDIENTE :`, `DENUNCIANTE :`, etc.) NO deben construirse como una tabla de Word. Deben usar sangría francesa (Hanging Indent de -1.48 pulgadas) y tabulación para alinear el valor a la derecha. El campo va en texto normal y el valor **en negrita**.
4. **Títulos Principales:** Numerados en romanos, alineados a la izquierda y en negrita. Deben usar sangría francesa (Hanging indent).
5. **Espaciado y Párrafos (¡MUY IMPORTANTE!):** El documento es de interlineado simple (`1.0`) y `SpaceBefore`/`SpaceAfter` en 0 puntos. **¡CRÍTICO! NO SE DEBEN INSERTAR PÁRRAFOS EN BLANCO ENTRE ELEMENTOS DE UNA MISMA LISTA NI DEBAJO DE LOS TÍTULOS DE SECCIÓN.** Solo se inserta una línea en blanco (un párrafo vacío) para separar grandes bloques procesales (ej. antes de pasar a un numeral romano nuevo, o para separar los puntos resolutivos PRIMERO, SEGUNDO, etc.). Dentro de la narración de los HECHOS, las viñetas (i), (ii), (iii) van totalmente pegadas sin saltos de línea entre sí, al igual que los subtítulos como 'Contra el Banco:'. Esto es esencial para que la estructura visual no se infle desproporcionadamente.
6. **Citas y Notas al Pie (¡EL SECRETO DE LAS 6 PÁGINAS!):** Siempre que se invoque una norma, debe insertarse una nota al pie real de Microsoft Word (Footnote). La inyección técnica debe ser perfecta. La fuente de las notas al pie es estrictamente **Arial tamaño 8.0**, alineación **Justificada**. Un tamaño mayor (ej. 10.0) inflará el documento de 6 a 7 o más páginas, lo cual es inaceptable. Para aplicar formato de negrita a secciones específicas del texto de la nota al pie (ej. Títulos de normas), se debe procesar el texto e inyectarlo fraccionado usando la API de Microsoft Word (ej. modificando `Font.Bold = True` al Range de la nota) para que la jerarquía visual de la norma sea idéntica al original.
7. **Pie de Página (Footer):** Todas las páginas del documento llevan el código `"M-CPC-01/03"`.
8. **Fuentes Generales:** El cuerpo del documento usa estrictamente **Arial tamaño 11** (NUNCA Arial Narrow), alineación **Justificada**.
9. **Nomenclatura del Archivo:** El nombre del archivo Word final SIEMPRE debe comenzar con el prefijo "ADM " seguido del número de expediente (ej. `ADM 0955-2026.docx`).
10. **Ruta de Guardado (¡Estricto!):** Todas las versiones de las resoluciones admisorias deben guardarse EXCLUSIVAMENTE en la ruta `D:\BETTER CALL DAVID\ResAdmi\productos (resoluciones) elaborada por google antigravity`. NUNCA deben guardarse dentro de la subcarpeta `cedulas de notificacion de los productos (resoluciones)`.
11. **Tipificación de Falta de Entrega de Estados de Cuenta (Bancos):** Cuando se impute a una entidad financiera la omisión de remitir un estado de cuenta solicitado, la imputación correcta DEBE hacer referencia al **artículo 152° de la Ley N° 26702** (Ley General del Sistema Financiero y del Sistema de Seguros y Orgánica de la Superintendencia de Banca y Seguros), concordante con los **artículos 18° y 19°** del Código (Idoneidad). NUNCA usar el artículo 24.
