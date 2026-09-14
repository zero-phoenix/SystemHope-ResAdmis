# MEGA PLAN — VELOCIDAD SIN COLGARSE NI PERDER CALIDAD

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
