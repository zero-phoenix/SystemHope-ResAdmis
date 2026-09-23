# MEGA PLAN — VELOCIDAD SIN COLGARSE NI PERDER CALIDAD

> **Documento de consulta.** Si contradice a `AGENTS.md`, manda `AGENTS.md` (reglas vigentes v3, 23/09/2026).


> Encargo del instructor, 14/09/2026, al abrir el tercer caso de prueba (3054-2026).
> Aplica a Antigravity y a cualquier agente que redacte un admisorio.

## 0. Restricciones duras

1. **PROHIBIDO GENERAR PDF.** En adelante el sistema produce **solo Word (`.docx`)**. La
   conversion a PDF era el ultimo consumidor de Word por COM y una de las causas medidas
   de cuelgue (el expediente 2723-2026 no pudo cerrarla por un Word huerfano).
2. **La calidad no se negocia por velocidad.** Nada de este plan vale si el generado deja
   de pasar `python scripts/verificar_admisorio.py` con `APTO (0 falsadores)` o deja de
   resistir `inspeccionar_docx.py --diff <control>` donde hay control.

## 1. Linea base medida (no estimada)

| Etapa | Coste real | Fuente |
|---|---:|---|
| Triaje de expediente (18 paginas) | **1,1 s** | R-113 |
| Inspeccion integra de un `.docx` | **0,5 s** | R-114 |
| Abrir las 630 plantillas maestras | **1,69 s** | R-115 |
| Inyeccion de notas en Word (abrir + formatear + guardar + cerrar) | **8,4 s** | medida 14/09/2026, `ADM 2723-2026 R2 - LSQok` |
| **Total de computo de un admisorio** | **~12 s** | suma de lo anterior |

**Conclusion:** la maquina no es el problema. Un admisorio tarda minutos u horas por el
**bucle del agente** (llamadas sucesivas, releer lo ya leido) y por **cuelgues**
(procesos huerfanos, regeneracion de trabajo cerrado). El plan ataca eso, no el CPU.

## 2. Las cuatro causas de cuelgue, con evidencia

| # | Causa | Evidencia medida | Estado |
|---|---|---|---|
| C1 | `WINWORD.EXE` huerfano con el `.docx` abierto y bloqueo `~$` | 14/09 03:41: un Word sin ventana vivo desde las 02:30, mas `~$S_02_2662...` en la carpeta del expediente en curso (R-116) | **Acotado** (R-123: falla rapido con el PID) |
| C2 | Regeneracion de un caso ya cerrado | Expediente 2723-2026 cerrado 03:27; a las 03:33 ya habia un `RES_02` regenerado (R-122) | **Cerrado** (R-122: caso cerrado = paro) |
| C3 | Superficie de instrucciones de arranque | 149 KB con R-103 repetida en 8 archivos (R-116) | **Acotado** (`AGENTS.md` es la unica lectura de arranque) |
| C4 | Conversion a PDF por COM | El expediente 2723-2026 quedo sin PDF por un Word huerfano | **Eliminado** (prohibicion de PDF) |

## 3. Frentes de trabajo

### F1 — Word acotado y sin huerfanos (causa C1)
- **Hecho:** pre-flight que aborta con el PID si hay `WINWORD.EXE` sin ventana (R-123), y
  `_limpiar_bloqueo` retira el `~$` antes de abrir.
- **Siguiente (presupuesto de tiempo):** si `procesar_notas` supera **60 s** de pared,
  abortar y reportar en vez de esperar. Un Word atascado deja de costar una tarde.
- **Metrica:** 0 `WINWORD.EXE` vivos al terminar una generacion.
- **Falsador:** dos admisorios seguidos dejan un Word sin ventana, o una generacion pasa
  de 60 s en la etapa de inyeccion.

### F2 — Cero PDF (causa C4, mandato del instructor)
- El entregable es el `.docx`. No se convierte, no se imprime, no se exporta.
- **Metrica:** 0 archivos `.pdf` producidos por el sistema en `casos_de_prueba/` y en las
  carpetas de expediente del escritorio.
- **Falsador:** un `.pdf` generado por el pipeline de admisorios.

### F3 — El bucle del agente: un admisorio son cinco llamadas (causa principal)
- Los cinco pasos de R-115 se ejecutan en **una sola pasada**, con salida compacta y sin
  releer nada que ya este en contexto.
- Prohibido: inspeccionar parrafo por parrafo, abrir plantillas a mano, repetir el triaje
  del expediente, repetir lecturas de un archivo ya leido.
- **Metrica:** numero de llamadas al shell por admisorio. Objetivo **≤ 12**.
- **Falsador:** un admisorio que consuma mas de 25 llamadas, o que lea dos veces el mismo
  archivo para averiguar cosas distintas.

### F4 — Eleccion determinista de plantilla (sin leer 630)
- La plantilla base se elige por consulta contra `docs/plantillas_maestras_index.json`
  (existe) y `docs/INDICE_TAXONOMICO_PLANTILLAS_MAESTRAS.md`, no abriendo el arbol.
- **Metrica:** eleccion en **1 llamada** y **≤ 2 s**, con la ruta impresa.
- **Falsador:** mas de una llamada para elegir plantilla, o una plantilla elegida cuyo
  patron no coincida en las cinco dimensiones (materia, submateria, numero y tipo de
  denunciados, genero, ordinal).

### F5 — Superficie de arranque minima
- La lectura de arranque es **solo `AGENTS.md`** (≤ 15 KB). `REGLAS_DE_APRENDIZAJE.md` y
  `MATRIZ_MAESTRA` son consulta dirigida: se busca **una** regla, no se leen enteros.
- Toda regla nueva se escribe en **un** lugar y se espeja; se prohibe repetirla en mas de
  dos archivos.
- **Metrica:** KB de arranque y numero de copias por regla.
- **Falsador:** una regla presente en tres o mas archivos.

### F6 — Paro y no-regeneracion (causa C2)
- `_ESTADO.md` o `_ORDEN_DE_TRABAJO.md` con «CASO CERRADO» ⇒ el agente reporta y se
  detiene (R-122). La guardia de puerta ya bloquea commits con material de expediente.
- **Metrica:** 0 `.docx` nuevos en una carpeta marcada CERRADA.
- **Falsador:** un `.docx` nuevo despues de la marca de cierre.

### F7 — Solo si F1 no basta: notas al pie sin Word
- Inyectar las notas en el OOXML directamente (sin COM). Es la unica forma de eliminar
  Word del flujo. **No se emprende todavia:** con la espera acotada, los 8,4 s de Word no
  justifican el riesgo.

## 4. Regla de oro

> Un admisorio completo se juega en **cinco pasos y doce llamadas**, con un presupuesto de
> computo de **~12 s** y un presupuesto de pared que no depende del CPU del agente.

## 5. Criterio de aceptacion global

Un caso se considera resuelto a la velocidad objetivo cuando, partiendo de un expediente
con capa de texto:

1. `verificar_admisorio.py` dice `APTO (0 falsadores)`;
2. no se genero ningun PDF;
3. no queda ningun `WINWORD.EXE` vivo;
4. el total de llamadas al shell es ≤ 12;
5. el `.docx` quedo fuera del repositorio (dato personal) y el caso quedo documentado.

Cualquier incumplimiento se reporta con la misma claridad que el exito (Ley 2).

## 6. Supervision del tercer caso de prueba (3054-2026)

Puntos de control que el supervisor mide, en orden:

1. **Triaje:** las paginas sin capa de texto, enumeradas; vision solo sobre esas.
2. **Datos anclados:** cada fecha, monto y placa del generado existe en el expediente.
3. **Plantilla:** la elegida coincide en las cinco dimensiones y existe.
4. **Control:** si hay documento de control, `inspeccionar_docx.py --diff`; las
   divergencias se juzgan una por una, no se presuponen errores (R-117 a R-121).
5. **Estructura:** firma segun proveedor (R-103), ordinales (R-104), parrafos vacios
   (R-105), anclas (R-106), membrete (R-107), espejos (R-108), modo verbal (R-110).
6. **Entrega:** `verificar_admisorio.py` con salida literal `APTO` y `guardia_admisorio.py`
   sin fuga. Sin PDF.

---

## 7. Autopsia medida de la trayectoria (Expediente 3054-2026, 14/09/2026)

Fuente: `python scripts/auditar_trayectoria.py --caso 3054`, que lee la base de
conversaciones del agente en solo lectura. No es una impresion: es el conteo de lo que
hizo, paso por paso.

> **CIFRAS CORREGIDAS EL 14/09/2026** (contadas por `call_id`, no por pasos de la traza;
> ver el aviso de la seccion 10). Las magnitudes bajan ~2,3x. El diagnostico no cambia:
> el Cwd equivocado, las relecturas y la espera activa siguen ahi y siguen siendo
> evitables.

| Metrica | Medido | Objetivo |
|---|---:|---:|
| Llamadas reales | **67** | **<= 12** |
| Vision sobre paginas (entonces desaconsejada; hoy obligatoria, R-137) | 10 | n/a |
| Relecturas del mismo archivo | **5** | **0** |
| Busquedas recursivas de `C:\Users` | **1** | **0** |
| Espera activa (polls de mas) | **1** | **0** |
| **Desperdicio evitable** | **17 operaciones** (~300 s) | **0** |

Desglose de donde se va el trabajo (censo de herramientas): `run_command` 25,
`manage_task` 21, `view_file` 19, `write_to_file` 2.

### El hallazgo que ordena todos los demas: el Cwd equivocado

36 comandos corrieron en `C:\Users\D\_ConfigIA\.resadmi` (carpeta practicamente vacia) y
27 en el repositorio. Desde el Cwd equivocado no existen ni `plantillas_maestras` ni
`verificar_admisorio.py`, y el agente reacciono asi:

1. **Renderizo paginas a PNG y las miro con vision.** Entonces se conto como
   desperdicio; **hoy ya no lo es**: R-137 obliga a leer todas las paginas con Google
   Lens. Lo que si fue desperdicio es haberlo hecho **sin el triaje previo**, sin saber
   cuantas paginas habia ni cuales carecian de capa de texto.
2. **Releyo su propio volcado de texto en tramos crecientes desde el offset 0**
   (0-180, 0-360, 0-540, 0-746...), 8 veces el mismo archivo.
3. **Buscó `verificar_admisorio.py` recorriendo todo `C:\Users\D` con `-Recurse`**, el
   peor comando disponible: un script del propio repositorio buscado a ciegas en todo el
   perfil de usuario.
4. **Espera activa**: 28 `manage_task` para consultar el estado de tareas asincronicas
   que ya tenia resueltas.

Ninguna de estas operaciones produce una linea del admisorio. Todas nacen de no haber
ejecutado el primer paso de R-115.

## 8. Frentes nuevos (F8 a F13)

- **F8 — Punto de entrada unico y absoluto.** El primer comando del caso es siempre
  `python scripts/extraer_expediente.py <carpeta>` **desde la raiz del repositorio**, con
  rutas absolutas. Su salida (paginas con texto / sin texto, dossier anclado) es la unica
  fuente para decidir vision.
  - *Metrica:* 1 llamada, y el numero real de paginas conocido antes de leer nada.
  - *Falsador:* empezar a leer sin haber hecho el triaje, o desconocer cuantas paginas
    tiene el expediente. **Ya no es falsador mirar una pagina con capa de texto: R-137
    obliga a mirarlas todas.**

- **F9 — Contrato de Cwd.** Todo comando corre con Cwd = raiz del repositorio. Prohibido
  operar desde otro directorio o buscar archivos del repositorio fuera de el.
  - *Metrica:* 0 comandos con Cwd ajeno al repositorio.
  - *Falsador:* un `Cwd` distinto de la raiz, o un `-Recurse` sobre `C:\Users`.

- **F10 — Lectura unica.** Un archivo se lee **una** vez, entero o en el tramo que haga
  falta; prohibido releerlo con offsets crecientes desde 0.
  - *Metrica:* 0 relecturas.
  - *Falsador:* el mismo archivo abierto dos veces en la misma tarea.

- **F11 — Sin espera activa.** Las tareas asincronicas se esperan con el resultado, no se
  consultan en bucle. Prohibido mas de un `manage_task` por tarea.
  - *Metrica:* 0 polls de mas.
  - *Falsador:* dos consultas de estado para la misma tarea.

- **F12 — Aislamiento por caso.** Una conversacion por expediente, abierta con el
  `_ORDEN_DE_TRABAJO.md` del caso y cerrada al entregar. La conversacion auditada acumula
  **1526 pasos** y su `brain` conserva el plan del caso anterior: asi se contamina un
  admisorio con otro.
  - *Metrica:* 1 caso por conversacion; 0 datos de un expediente en otro.
  - *Falsador:* dos numeros de expediente distintos en la misma conversacion.

- **F13 — Scorecard obligatorio antes de entregar.** `python scripts/auditar_trayectoria.py
  --caso <n>` debe mostrar 0 en las columnas de desperdicio (relecturas, recursivas,
  espera activa). La columna de vision dejo de ser desperdicio con R-137. Se entrega junto con la
  salida de `verificar_admisorio.py`.

## 9. Instrumento de supervision

`scripts/auditar_trayectoria.py` (solo lectura) reconstruye la secuencia real del agente
desde su base de conversaciones y cuenta vision, relecturas, Cwd ajeno, busquedas
recursivas y espera activa. Da un veredicto por regla y un total de desperdicio. Es el
mismo instrumento que se usara para supervisar la cola de admisorios uno por uno.

---

## 10. La ley de la latencia: el tiempo lo fija el numero de llamadas

Las secciones 7-9 contaban **cuantas** operaciones sobraban. Faltaba lo que **cuesta**
cada una. Se midio el reloj paso a paso sobre la misma traza (las marcas de tiempo de
cada paso, no una estimacion):

> **CIFRAS CORREGIDAS EL 14/09/2026.** Esta seccion decia 157 llamadas y 7,5 s por
> llamada. Era un defecto **del instrumento**: `auditar_trayectoria.py` contaba *pasos*
> de la traza, y una misma llamada aparece en varios (invocacion, resultado, eco).
> Contado por identificador de llamada, la sesion fueron **67 llamadas** y **17**
> operaciones evitables, no 157 y 70. El auditor ya cuenta por `call_id`. La forma de la
> ley no cambia; cambia la constante, y con ella el presupuesto.

| Magnitud medida | Valor |
|---|---:|
| Ventana de reloj de la sesion (Exp. 3054-2026) | **1178 s (19,6 min)** |
| Llamadas reales en esa ventana (por `call_id`) | **67** |
| **Coste medio por llamada** | **17,6 s** |
| Huecos de decision entre pasos (el agente "pensando") | **6 s en total** |
| Computo util de un admisorio completo | **~12 s** |

Dos conclusiones, y la segunda es la unica que importa:

1. **La latencia no esta en pensar.** Los huecos entre pasos suman 6 s en 19,6 minutos.
   Casi todo el reloj esta **dentro** de las llamadas.
2. **El coste por llamada es fijo y no depende del trabajo.** Un `manage_task` que solo
   consulta un estado ya conocido cuesta lo mismo que un paso que genera documento.
   Luego:

   > **T ≈ 17,6 s × N**, donde N es el numero de llamadas reales (por `call_id`).

   Con esa ley, las **17 operaciones evitables** del caso 3054 valen **~300 s (5 min)**:
   una cuarta parte de la sesion se fue en trabajo que no produjo una linea del
   admisorio. Y el presupuesto queda fijado: **12 llamadas × 17,6 s ≈ 3,5 min** de reloj
   mas el computo. Un expediente corto debe cerrarse **por debajo de 4 minutos**; uno
   largo escala con sus paginas, porque leerlas todas con Lens (R-137) es coste
   irreducible.

**Corolario operativo:** optimizar el computo es inutil (ya son 12 s de 1178). La unica
palanca es **agrupar trabajo por llamada**. Todo frente nuevo se justifica por cuantas
llamadas elimina, no por cuanto CPU ahorra.

## 11. F14 y F15 — los frentes que salen de la ley

- **F14 — Punto de entrada unico: `scripts/admisorio.py`.** Dos ordenes, una llamada
  cada una:
  - `preparar <carpeta>` = paro por caso cerrado (R-122) + deteccion de Word huerfano
    (R-123) + triaje con dossier anclado + presupuesto de vision + candidatas de
    plantilla del indice, con filtro por texto. **Sustituye a seis llamadas.**
    *Medido:* 4,3 s con filtro de texto sobre las 605 plantillas; 0,3 s cuando el caso
    esta cerrado y corta de inmediato.
  - `entregar <docx>` = `verificar_admisorio` + `guardia_admisorio` + control de PDF +
    control de Word vivo + scorecard de trayectoria (`--caso`). **Sustituye a cuatro
    llamadas.** *Medido:* 0,6 s.
  - El script fija el Cwd en la raiz del repositorio por construccion (F9): desde el no
    se puede repetir la busqueda recursiva de un script propio sobre `C:\Users`.
  - *Metrica:* un admisorio de expediente con capa de texto se juega en **2 llamadas de
    herramienta mas la redaccion**.
  - *Falsador:* un caso que necesite llamar por separado a `extraer_expediente.py`,
    `verificar_admisorio.py` o `guardia_admisorio.py`.

- **F15 — Presupuesto de reloj, no solo de llamadas.** Cada caso se cierra declarando
  `N` llamadas (contadas por `call_id`) y `T` de reloj. Objetivo: **N ≤ 12** y
  **T ≤ 4 min** en un expediente corto, desde el triaje hasta el veredicto
  `ENTREGABLE`. Un expediente largo escala con su numero de paginas.
  - *Falsador:* un caso entregado sin declarar N y T, o que supere su presupuesto sin
    que la causa quede identificada (numero de paginas, control ausente, contradiccion
    elevada).

### Correccion de un dato que se habia dado por bueno

El cierre del caso 3054 afirmaba que `TPL_1190_2026_...` era **la unica** plantilla cuyo
texto contiene el nucleo de *derecho de arrepentimiento*. Medido con
`admisorio.py preparar --contiene "derecho de arrepentimiento"`: son **dos de 605**
(tambien `TPL_2603_2025_SEGURO_VIDA_MATERIA_GENERAL_ASEGURATIVA_ASEGURADORA_VARON_R1`).
Se corrige aqui porque una afirmacion de unicidad sin el comando que la reproduce es
exactamente lo que este plan le exige al agente no hacer.
