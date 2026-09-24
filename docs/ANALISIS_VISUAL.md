# ANÁLISIS VISUAL DEL CORPUS

> **Documento de consulta.** Si contradice a `AGENTS.md`, manda `AGENTS.md` (reglas vigentes v3.1, 24/09/2026).


> 1.042 capturas referenciales en `docs/capturas_referenciales/`, una por celda de
> **rama × materia × tipo de denunciado × sujeto** (205 celdas, hasta 3 documentos
> y 3 páginas por celda). Leídas con visión directa, **cero OCR**.

## 0. Cómo se hicieron, y por qué se pueden publicar

Las fuentes son admisorios reales. Una imagen **no la filtra ninguna guardia de
texto**, así que publicar capturas sin tocar habría sido la peor fuga del sistema.

Por eso cada PNG **nace tachado**: PyMuPDF da la caja de cada palabra, los datos
personales se localizan por coordenadas y se pintan en negro **antes** de guardar.
No existe una versión intermedia limpia en el disco.

Se tacha: nombres (incluidos los compuestos con partícula, «X **de Pastor**»), DNI,
RUC, correos, teléfonos, números de póliza y cuentas de 7 o más dígitos. En la
plantilla esos números se conservan porque hacen falta para redactar; **en una
captura no hacen falta para nada**, y cruzados con la aseguradora y la fecha
señalan a una persona.

Dos garantías, y las dos son de fallo cerrado:

1. **Página sin capa de texto → no se captura.** Sin texto no hay coordenadas, y
   sin coordenadas no se puede garantizar el tachado.
2. **Dato detectado pero no localizable → no se captura la página entera.**
   Publicar una captura a medias es peor que no tenerla.

De 1.071 intentos, **26 se descartaron** por una de esas dos razones.

## 1. La fuente tiene que ser el PDF, nunca el `.docx`

Al comparar los dos renders de un mismo expediente:

| | `.docx` convertido | **PDF original** |
|---|---|---|
| Logo Indecopi | ✗ desaparece | ✓ |
| Membrete de la Secretaría Técnica | ✗ desaparece | ✓ |
| Tipografía | ✗ serif genérica | ✓ Arial Narrow |
| Encabezado en columna con `:` alineado | ✗ se reflowea | ✓ |
| Sangría francesa de los sub-incisos | ✗ se pierde | ✓ |
| Pie `M-CPC-01/03` | ✗ desaparece | ✓ |

MuPDF **reflowea** el `.docx`: conserva el texto y pierde la maqueta. Para medir
tipografía sirve el OOXML (R-144, que da los valores exactos); para **ver** el
documento, solo sirve el PDF.

## 2. Lo que solo se ve mirando

Elementos que ninguna medición de texto había revelado:

```
 ┌──────────────────────────────────────────────────────────────┐
 │ [logo Indecopi]              SECRETARIA TÉCNICA DE LA        │  ← cursiva,
 │                        COMISIÓN DE PROTECCIÓN AL CONSUMIDOR 1│    alineado
 │                                              SEDE CENTRAL    │    a la derecha
 │                                                              │
 │ EXPEDIENTE    :  1196-2026/CC1                               │  ← etiquetas y
 │ DENUNCIANTE   :  ███████████                                 │    valores en
 │ DENUNCIADO    :  RÍMAC SEGUROS Y REASEGUROS S.A. (RÍMAC)     │    negrita, con
 │ MATERIAS      :  ADMISIÓN A TRÁMITE                          │    los `:` en
 │                  REQUERIMIENTO DE INFORMACIÓN                │    columna
 │ RESOLUCIÓN    :  1                                           │
 │                                                              │
 │ Lima, 5 de mayo de 2026                                      │  ← sin negrita
 │                                                              │
 │ I.   HECHOS                                                  │  ← romano + tab
 │                                                              │
 │ 1.   Mediante el escrito del …, el señor ███ denunció a …    │  ← numeración
 │                                                              │
 │      (i)   El 20 de diciembre de 2019, inició sus labores…   │  ← sangría
 │      (ii)  El 19 de julio de 2024, solicitó a Rímac…         │    francesa
 │ ─────────────────────                                        │
 │ ¹ Publicado el 2 de setiembre del 2010 en el Diario Oficial… │  ← nota al pie
 │ M-CPC-01/03                          1                       │  ← pie + página
 └──────────────────────────────────────────────────────────────┘
```

| Hallazgo visual | Consecuencia |
|---|---|
| Membrete en **cursiva**, tres líneas, alineado a la derecha | Es el único uso sistemático de cursiva del documento |
| Las etiquetas del encabezado y sus valores van en **negrita** | La negrita no es decorativa: marca encabezado y ordinales |
| Los `:` del encabezado forman **columna** | Es tabulación, no espacios |
| `I. HECHOS` lleva **romano mayúsculo** y tabulador | Las secciones se numeran; los artículos no |
| Los sub-incisos `(i)` cuelgan con **sangría francesa** | Coincide con R-145 medido en texto |
| **Nota al pie 1** siempre es la publicación del Código | Invariante que el texto no delataba como posicional |
| Pie `M-CPC-01/03` y número de página centrado | Identificador de formulario institucional |

## 3. Cómo usar las capturas

```
docs/capturas_referenciales/
  01_seguro_vehicular/
    negativa_cobertura__1_ddo_aseguradora__varon/
      TPL_xxxx_..._p01.png   ← encabezado y apertura de hechos
      TPL_xxxx_..._p02.png   ← hechos y considerativa
      TPL_xxxx_..._p03.png   ← resolutiva y firma
```

Antes de redactar un caso, **se mira la celda que le corresponde**. Una captura de
la misma rama, materia, tipo de denunciado y sujeto enseña en un vistazo lo que
ninguna regla escrita transmite: cuánto ocupa cada bloque, dónde caen los saltos,
cómo se ve una resolutiva de tres partes frente a una de dos.

## 4. El riesgo residual, ya cerrado

Lo era: `guardia_admisorio.py` leía texto y un PNG le pasaba por delante sin que lo
mirara. **Cerrado el 15/09/2026 (R-150)**: cada captura se sella con su procedencia
en un chunk del propio PNG, y la guardia bloquea toda imagen sin sello. Verificado
en los dos sentidos — la sellada pasa, una añadida a mano se bloquea.

El sello prueba que la imagen pasó por el tachado automático, **no que el tachado
sea correcto**: el apellido «de Pastor» sobrevivió a una versión del patrón. Por eso
toda imagen se revisa además **con Google Lens**, sea escaneo o sea render, tenga o
no capa de texto detrás. Cero OCR, sin excepción.

Se descubrió además, con las capturas ya generadas, que los patrones de DNI, RUC y
teléfono **llevaban rotos desde el principio**: un carácter de retroceso donde
debía ir un límite de palabra (el mismo defecto que R-141 persigue, y la cuarta vez
que aparece en este repositorio). Lo cazó `autocomprobacion.py`, que existe
exactamente para eso. Las 1.042 capturas se regeneraron con los patrones vivos.
