# SUPERVISIÓN DE AGENTES REDACTORES

> Escrito el 15/09/2026 a partir de la primera remesa supervisada de punta a punta:
> trece expedientes, un meta orquestador y Antigravity redactando.
> Todo lo que hay aquí está medido. Lo que no pude medir, lo digo.

Este documento no repite las reglas de redacción —esas están en `AGENTS.md` y en
`REGLAS_DE_APRENDIZAJE.md`—. Aquí está **cómo se supervisa a un agente que
redacta**: por dónde se le controla, qué se mide, cuándo se interviene, y el
catálogo de lo que salió mal con su arreglo estructural.

---

## 1. La superficie de control

Antigravity expone una API de agente en su propio *language server*. Con ella se
puede **lanzar un caso y corregir al agente mientras trabaja**, sin tocar su
interfaz. Eso es lo que convirtió un caso de 37 minutos en uno de 5.

```bash
python scripts/orquestar.py estado                    # conversaciones y su estado
python scripts/orquestar.py lanzar 2765-2026          # encargo canónico del caso
python scripts/orquestar.py corregir <conv> "texto"   # corrección en caliente
```

`orquestar.py` descubre solo el puerto gRPC, el token CSRF y el identificador de
proyecto leyendo la línea de comandos del proceso que ya está corriendo. **No hay
que pedirle esos datos a nadie ni apuntarlos.** Si Antigravity está cerrado, lo
dice y para.

Un detalle que costó encontrar y conviene saber: `new-conversation` exige un
`project_id`, y el proyecto que existe **no apunta al repositorio** —el workspace
real era una carpeta casi vacía—. Por eso el encargo canónico lleva siempre rutas
absolutas y fija el Cwd por escrito, en vez de confiar en el directorio del
agente.

## 2. Qué se mide, y por qué esas cuatro cosas

```bash
python scripts/vigilar_remesa.py <conv>:<EXP>:<RES> [...]   # varios casos a la vez
python scripts/auditar_trayectoria.py --caso <n>            # scorecard de cierre
```

| Señal | Qué delata |
|---|---|
| **Llamadas** (por `call_id`) | El reloj lo fija el número de llamadas: **T ≈ 17,6 s × N**. No hay otra palanca |
| **Pasadas de visión** | Cero visión significa que redactó del volcado de texto, que es contraste y no fuente |
| **Relecturas** | El mismo archivo abierto dos veces es contexto que se perdió |
| **Cwd ajeno / recursivas** | Está trabajando desde donde no debe, y todo lo demás se derivará de eso |

**Cuándo intervenir:** en cuanto una señal se desvía, no al final. Las tres
intervenciones que más valieron en la remesa llegaron en los minutos 3, 5 y 6 de
un caso. Una corrección al final no corrige: obliga a rehacer.

**Cómo intervenir:** con un dato anclado, no con una reprimenda. Cuando el agente
se inventó una rama taxonómica, lo que lo corrigió no fue «esa rama no existe»,
sino «la página 1 dice *Seguro de Tarjetas 360 Premium, Póliza 5000068*, la rama
es `04_seguro_proteccion_tarjetas_y_dinero`».

## 3. Las tres barreras de calidad, y qué ve cada una

Ninguna sustituye a las otras. Un documento puede pasar dos y ser inservible.

| Barrera | Comprueba | Lo que NO ve |
|---|---|---|
| `verificar_admisorio.py` | La **forma**: firma, ordinales, negritas, espejos, modo verbal | Que los datos existan |
| `construir_admisorio.py` | Que no sobreviva nada de la **plantilla** de origen | Un dato que no viene de la plantilla ni de ningún sitio |
| `auditar_admisorio.py` | Que cada dato **exista en el expediente**, y las partes y el ordinal en la cédula | La coherencia jurídica del razonamiento |

La tercera nació tarde y encontró, en el primer barrido sobre cuatro admisorios ya
dados por buenos: cuatro fechas sin ancla, un ordinal que contradecía a su cédula y
dos apellidos inventados. Ninguna de esas cosas la veían las otras dos.

## 4. Catálogo de fallos del agente, con su medida y su arreglo

Cada uno se arregló **estructuralmente**: la regla que depende de que el agente se
acuerde no es una regla.

| Fallo | Medida | Arreglo estructural |
|---|---|---|
| Trabajaba desde el workspace equivocado | 36 comandos en una carpeta vacía contra 27 en el repositorio; buscaba scripts propios con `-Recurse` por todo `C:\Users` | `admisorio.py` fija la raíz por construcción; `AGENTS.md` plantado en la carpeta equivocada para redirigir |
| No leía el expediente con Lens | Un caso llegó a 17 llamadas con cero visión; en la segunda tanda **los tres agentes entregaron con cero toques a imagen** | Las páginas llegan ya renderizadas en `_paginas\`, y `entregar` exige `_LECTURA.md` con una línea por página |
| Construía el `.docx` con Word por COM | Cinco `scratch_com*.py` sucesivos peleándose con `DisplayAlerts`; 10 de sus 16 minutos | `construir_admisorio.py` edita el OOXML sin Word; `entregar` declara falsador cualquier `scratch*.py` |
| Reemplazos a ciegas sobre una plantilla | Un admisorio con los hechos de **otro** consumidor y los nombres cambiados | Auditoría de residuos: claves, expediente de origen, aseguradoras ajenas, fechas y cifras heredadas |
| Apellidos quiméricos | «Pablo Santiago **Cornejo** Canal»: mitad plantilla, mitad caso. Certificado APTO | `auditar_admisorio.py` rechaza todo apellido que no sea de una parte ni conste en el expediente |
| Se inventaba la taxonomía | Rama `03_seguro_tarjetas`, inexistente; acabó abriendo plantillas de otra materia | La orden de trabajo propone candidatas **con la evidencia** que las sostiene |
| Dejaba archivos de trabajo en el repositorio | `mapa.json`, `tpl.txt`, `gen_map.py`, cinco `scratch*` | La guardia revisa también `.json`, `.txt`, `.py`; `.gitignore` los nombra; hook instalado |
| Contradecía a la cédula | Un admisorio se declaraba «Resolución 1» con la cédula fijando la 2 | `auditar_admisorio.py` contrasta el ordinal y las partes contra la cédula |

## 5. Catálogo de fallos **del supervisor**

Esto es la mitad del documento por una razón: **más de la mitad de lo que le imputé
al agente era mío**. Un instrumento que miente cuesta más que no tener instrumento,
porque manda a corregir lo que ya estaba bien.

| Instrumento | Cómo mentía | Coste |
|---|---|---|
| `auditar_trayectoria.py` | Contaba *pasos* de la traza, no llamadas; cada llamada aparece en varios | Reporté 157 llamadas donde había **67**, y 70 operaciones evitables donde había **17**. La constante de la ley de latencia estaba inflada 2,3× |
| `construir_admisorio.py` | `<w:t[^>]*>` también casa con `<w:tab>`: el texto del párrafo se llenaba de XML crudo | **14 de 19 fallos eran falsos**. El agente iteró contra un diagnóstico inventado |
| `verificar_admisorio.py` | Los cinco patrones de R-110 tenían un **retroceso (0x08)** donde debía ir un límite de palabra | La regla llevaba declarando `OK` sin comprobar nada, sobre todos los documentos |
| `vigilar.py` | Contaba como búsqueda recursiva el texto del propio encargo | Acusé al agente de una infracción que era mi prompt |
| `auditar_admisorio.py` | Marcaba como inventadas las fechas de publicación de las leyes citadas | 8 de 12 hallazgos eran ruido normativo que ahogaba los reales |
| Mi propio proceder | `git add -A` en un repositorio público | Un `mapa.json` con el nombre completo de dos consumidores entró al historial. El force-push **no lo borró**: GitHub sigue sirviendo el objeto por su SHA |

## 6. Los dos principios que salen de todo esto

**La orden obligatoria se sirve preparada** (R-140). Decirle «lee con Lens» costó 17
llamadas y 6 minutos de agente averiguando *cómo*, leyendo el código de las propias
herramientas. Dejarle los PNG renderizados y la ruta de cada uno en su orden lo
resolvió. Si una regla exige un trabajo, el repositorio entrega ese trabajo hecho o
el comando exacto que lo hace.

**El instrumento se audita como se audita al agente** (R-141). Una métrica que nadie
ha falsado no es una medición: es una creencia con decimales. Toda métrica nueva
nace con su falsador y con una prueba que la vea fallar de verdad.

## 7. Lo que no está resuelto

- **El repositorio es público** y contiene material de expediente en su historial,
  incluido el `mapa.json` que se me coló. Un force-push no lo quita: solo lo quita
  el soporte de GitHub, o deja de importar si el repositorio pasa a privado.
- **El scorecard de trayectoria no distingue casos en paralelo**: toma la
  conversación más reciente, que puede ser la de otro expediente. Por eso la
  constancia de lectura es un artefacto (`_LECTURA.md`) y no una lectura de la
  traza.
- **La fidelidad de `_LECTURA.md` no está garantizada por el sistema**: un agente
  podría escribirla sin haber mirado. Hoy lo cubre la relectura del supervisor, que
  es una garantía humana, no mecánica.
