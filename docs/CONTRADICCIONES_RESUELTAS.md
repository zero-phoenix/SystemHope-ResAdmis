# CONTRADICCIONES RESUELTAS

> **Documento de consulta.** Si contradice a `AGENTS.md`, manda `AGENTS.md` (reglas vigentes v3.1, 24/09/2026).


> Un repositorio que se contradice a sí mismo le da al agente **permiso escrito**
> para incumplir sus reglas vigentes: siempre hay una frase que respalda lo que
> hizo. Por eso se retiraron `.cursorrules`, `.windsurfrules` y `CLAUDE.md` en
> septiembre, y por eso este documento existe.
>
> Cada entrada dice qué decía cada lado, **qué cifra lo dirime** y dónde quedó
> arreglado. Resuelto el 18/09/2026; ampliado el 24/09/2026 (v3.1).

## El árbitro

```
   0 de 593  ──►  PROHIBICIÓN ABSOLUTA        se corrige
   1 de 593  ──►  cuasi-absoluta: desviación   se corrige
  ≥5 de 593  ──►  NO es prohibición, es gusto  NO se toca
 mandato del instructor ──►  vence al corpus,  y se declara como mandato
```

---

## 1. El censo de plantillas: 620 contra 605 contra 630

| Decía | Dónde |
|---|---|
| 620 | `README.md` |
| 605 | `AGENTS.md` §4 y §8 |
| 630 | `RESUMEN_EJECUTIVO.md`, `docs/ANATOMIA_DEL_ADMISORIO.md` |

**El árbol tiene 593 `.docx`.** Contados, no recordados. Las tres cifras eran
anteriores a la depuración y ninguna se actualizó. Corregidas las cuatro.

## 2. El margen derecho: 2,5 contra 3,0 cm

`R-144` mide **3,0 cm en 113 de 116 secciones** y el verificador lo exige. Pero
`AGENTS.md` §5 —que es **la lectura de arranque**— y el checklist de
`MEMORIA_ESTILO_VISUAL_PAGINAS.md` §6 conservaban el 2,5 falsado.

Un admisorio hecho siguiendo la lectura de arranque **fallaba el verificador**.
Los seis documentos de la remesa de septiembre que tenían el margen corto salían
de ahí. Corregido en los dos sitios.

## 3. `RESUELVE:` no existe

`MEMORIA_ESTILO_VISUAL_PAGINAS.md` §4.2 lo daba como título de la parte
resolutiva. Medición: **0 de 593**. El corpus escribe
`RESOLUCIÓN DE LA SECRETARÍA TÉCNICA` en **591 de 593**. Corregido.

## 4. La volada de `artículo 20°`

`AGENTS.md` §2 ordenaba copiar los tres párrafos de notificación «SIN
PARAFRASEAR», y esos párrafos escribían `artículo 20°`. `PHOENYX-06` prohibía la
volada. Ninguna de las dos marcada como derogada.

Medición: de **1 166 ocurrencias** de «artículo 20» en el corpus, **ninguna**
lleva la volada. El mandato literal estaba mal escrito. Corregido en AGENTS.md; y
se estuvo a punto de «corregir» doce admisorios hacia el error.

## 5. `los artículos 1 y 2`

Para el deber de información, `AGENTS.md` §1.3 escribía «Artículos 1°, numeral 1,
literal b) y 2°». Medición de la forma literal en las imputaciones:

| Forma | Veces |
|---|---:|
| `artículo 1, numeral 1, literal b) y al artículo 2` | **192** |
| `los artículos 1 y 2` | **0** |

Y en el cierre de la considerativa, `tipificado en el artículo 1, numeral 1,
literal b) y al artículo 2 del Código`: **230**. Corregido.

## 6. La vía por domicilio procesal pedía un acuse que nadie pide

`AGENTS.md` §2 TIPO 3 pedía «efectúe la confirmación de recepción … a su
domicilio procesal». Medición sobre los 43 párrafos por domicilio procesal del
corpus:

| Fórmula | Veces |
|---|---:|
| `señale un correo electrónico autorizando recibir las notificaciones…` | **37** |
| acuse de recibo | 6, tres de ellos malformados |

Los modelos `MODELO_1_DDO.docx` y `MODELO_2_DDOS.docx` confirman la primera.
**La vía 3 no pide acuse: pide que se designe un correo.** Corregido.

## 7. El modo verbal en los hechos: contradicción triple

| Decía | Dónde |
|---|---|
| «terminantemente prohibido usar *habría* en HECHOS» | R-87 y la matriz |
| «se enuncia **siempre** bajo atribución o en potencial» | R-110 |
| «el control narra en **indicativo directo** con el alias» | R-131 |
| «pasado indicativo afirmativo» | AGENTS.md §1.4 |

Tres órdenes incompatibles sobre el mismo párrafo, y R-124 lo declaraba sin
resolver. Lo dirime R-148: **el 60 % del corpus narra en indicativo directo con
el alias**, y el documento de control sí usa el condicional.

**R-87 queda derogada.** Conviven las dos formas. Lo único prohibido es el
indicativo asertivo que atribuya al proveedor un hecho no probado.

## 8. El artículo 24: prescrito y prohibido a la vez

La tabla de 44 infracciones de la matriz prescribía «*Presunta infracción al
numeral 88.1 del artículo 88 [o Art. 24 si no es financiero]*». Y R-56 lo
prohíbe en términos absolutos.

Comprobado: **`art.24` no existe en `docs/catalogo_imputaciones.json`**, luego
R-143 lo rechaza siempre. La tabla prescribía una imputación que el verificador
bloquea. Corregida la fila: si el proveedor no es financiero, **se eleva**.

## 9. `remitir`: prescrito y prohibido

La matriz lo daba como verbo válido del requerimiento; R-149 lo prohíbe. Medición:
`presentar` **591**, `remitir` **4**. Es residuo, no alternativa. Corregido.

## 10. El tope de «6 páginas justas»

La matriz lo daba como estándar. No tiene **ni una cifra detrás**, y el esqueleto
obligatorio —de PRIMERO a DÉCIMO más un ordinal de acuse por parte, con todas sus
notas legales— nunca se midió contra ese tope. Bajo R-148, una prohibición sin
frecuencia es una opinión. Retirado.

## 11. La firma: tres versiones simultáneas

| Decía | Dónde |
|---|---|
| Firma única de Analí con `(e)`, nunca Ad Hoc | R-127 y el verificador |
| Rímac → Ad Hoc; el resto → Eveling | R-103 en la matriz y la memoria §5.4 |
| «ninguno firma Eveling Roa Quispe» | R-127 |

Lo último es **falso**: el corpus lo desmiente con **494 de 593**. El propio §94
de las reglas ya lo había confesado.

**Mandato del instructor (18/09/2026), que es el que ahora manda:** Eveling Roa
Quispe firma todos los admisorios, salvo las denuncias contra **Rímac**, que
firma Luisa Analí Silva Malpartida como **Secretaria Técnica Ad Hoc**. **El
sufijo `(e)` queda suprimido.** Corregido en el verificador, en AGENTS.md y en la
memoria de estilo.

**El refrendo deja de estar cableado** en la memoria: se copia del control o de
la cédula. Inventarlo es exactamente lo que el sistema prohíbe.

## 12. `UNDÉCIMO` y `DUODÉCIMO` dentro del propio verificador

R-146 mide **0 apariciones** en el corpus y el verificador los rechaza… pero su
lista global `ORDINALES` los incluía. Incoherencia del instrumento, que R-141
obliga a auditar como se audita al agente. Retirados de la lista.

## 13. La errata que enseñaba a escribir mal

`COMO_NO_SE_REDACTA.md` §1 daba como forma correcta `luego de el rechazo`. La
contracción se hace: **`luego del rechazo`**. Una regla que enseña una errata
propaga la errata. Corregida.

## 14. Las vías de notificación no dependían de nada medible

El directorio clasificaba a Rímac y al BCP como «Correo Electrónico / Casilla,
según apersonamiento previo», y metía a Banco Pichincha, Banco Ripley y
Scotiabank en la lista de Casilla.

Dos fuentes independientes lo desmienten:

| Proveedor | Corpus | Padrón de TyC |
|---|---|---|
| Rímac | correo **137 de 137** | **de baja en el padrón** |
| Banco de Crédito del Perú | correo **28 de 29** | sin teléfono móvil |
| Banco Ripley | correo **2 de 2** | sin teléfono móvil |
| Banco Pichincha | domicilio | **de baja en el padrón** |
| Scotiabank | correo **7 de 7** | no figura en el padrón |

No había ambigüedad que resolver: la ambigüedad **no describía la práctica**.
Corregido en AGENTS.md §3, en el directorio, en el motor y en
`docs/casillas_habilitadas.json`, que ahora es la lista viva.

## 15. El motor llevaba su propia copia de la doctrina

`src/systemhope_engine.py` embebía el texto de las vías con las listas viejas.
Es exactamente el problema por el que se borraron `.cursorrules` y
`.windsurfrules`: **doctrina duplicada que envejece por separado**. Actualizada y
apuntada a `docs/casillas_habilitadas.json`.

---

## Lo que NO se tocó, por medición

Tres «defectos» que parecían evidentes y resultaron ser la casa:

| Candidato | Medición | Veredicto |
|---|---:|---|
| El subrayado del ordinal OCTAVO | **593 de 593** | ~~no es defecto~~ **derogado el 24/09/2026**: el instructor ordenó quitar el subrayado de la conciliación; solo el rótulo del requerimiento va subrayado (R-192, migrado en las 574) |
| `indebidamente` en los hechos | 149 de 593 (25 %) | uso corriente |
| `carro` / `auto` | 11 de 593 | infrecuente, no prohibido |

Medir antes de corregir evitó tres correcciones falsas. Es el mismo hábito que la
escala de arriba: **una prohibición sin frecuencia detrás es una opinión.**

---

## v3.1 (24/09/2026): revisión página por página del instructor

Mandatos del instructor que vencen al corpus (se declaran como mandato, según el árbitro de arriba). Cada uno tiene su falsador y el corpus está migrado (`scripts/migraciones/migrar_v3_1.py`).

| Tema | Antes (corpus o regla) | Ahora (mandato) | Falsador |
|---|---|---|---|
| Negrita de PRIMERO | Párrafo entero (541 de 574, R-164 del 23/09) | Solo el rótulo, como los demás ordinales | R-164 |
| Nota del Código | Tras «señalando lo siguiente:» (547 de 549) | Tras «Código de Protección y Defensa del Consumidor» | R-184 |
| Nota del traslado | Tras «señalando lo siguiente:», junto a la del Código | Tras la fecha del escrito, para seguir siendo la nota 1 (AGENTS §5) | R-184, R-167 |
| Nota de competencia | Pegada a la de la norma (62 plantillas) | Tras «en ejercicio de sus facultades» | R-184, R-185 |
| Llamada y texto de la nota | Espacio tras la llamada (7 268 notas): primera línea corrida | Una tabulación: todas las líneas a 1 cm | R-187 |
| Literales h. e i. del 115.1 | Sin letra (544 plantillas) | Con su letra, como a. a g. | R-187 |
| Subrayado en la conciliación | «no es defecto» (593 de 593) | Solo el rótulo del requerimiento | R-192 |
| «Firmado digitalmente por» | 250 de 574 | Siempre | R-193 |
| Sujeto de la imputación con aseguradora | «la compañía aseguradora» con cualquier número de denunciados | Solo si es la única denunciada; con dos o más, razón social completa | R-188 |
| Denunciante en la imputación | Tratativa corta («la señora Pérez») | Nombre completo, idéntico en considerativa y resolutivo | R-188, R-97 |
| Rótulo del requerimiento | Razón social o alias | Alias del encabezado | R-189 |
| Transcripción literal de una norma («éste») | — | Se respeta tal cual; el léxico de AGENTS §2.10 rige la redacción propia | — |
| Vista del documento | LibreOffice | ONLYOFFICE (fiel a Word); LibreOffice solo como vista aproximada rotulada | — |

Retirados del árbol el mismo día, por datos personales y por ser borradores: `automatizacion_antigravity/temp_*` y `automatizacion_antigravity/casos/`. Siguen en el historial de git hasta que el instructor decida purgarlo.
