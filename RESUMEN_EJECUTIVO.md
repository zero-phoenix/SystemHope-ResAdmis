# Resumen ejecutivo — estado del sistema

> Actualizado el 15/09/2026, tras la primera remesa supervisada de punta a punta y
> la depuración del repositorio. Todo lo que se afirma aquí está medido; lo que no
> se pudo medir se declara como tal.

## Qué es esto

Un sistema de apoyo a la redacción de resoluciones admisorias de la CC1 del
Indecopi. Un agente redacta; el repositorio aporta las plantillas, las reglas y las
barreras que impiden que salga un documento con datos que no existen.

## Lo que cambió en esta versión

### 1. Depuración: de 1.481 archivos publicados a 725

Se retiró del repositorio —**sin borrar nada del disco del instructor**— todo lo
que era expediente real, sedimento o contradicción:

| Retirado | Por qué |
|---|---|
| `ADMI + CONFI/`, `Modelos al 30-06-26/` | Expedientes y modelos reales, incluida una carpeta llamada `CONFI` |
| `productos (resoluciones)...`, `casos/`, `casos_de_prueba/` | Admisorios emitidos con datos de consumidores |
| Un `.xlsx` de personas, 31 `.db`, 20 `.pyc`, `build/`, `dist/`, `temp_docx/` | Sedimento |
| 47 scripts sueltos en la raíz (`test_xml8.py`, `test_del7.py`, …) | Exploración de un solo uso |
| 16 scripts de `scripts/` con rutas de otra máquina | Análisis puntual ya consumido en `docs/` |
| `.cursorrules`, `.windsurfrules`, `CLAUDE.md` | **Contradicción**: predicaban «visión solo en páginas sin capa de texto», doctrina que R-137 derogó |

### 2. Las 630 plantillas llevaban el nombre de un consumidor real

Medido sobre una muestra de 40: **39 identificaban a una persona**. Ampliado a
todas: **630 de 630**, con 6.869 sustituciones aplicadas.

Anonimizar no las degrada, las **mejora**: un modelo que dice «el señor Espinoza»
invita al reemplazo a ciegas —de ahí salieron apellidos quimera como «Pablo
Santiago Cornejo Canal»—; uno que dice «el señor [APELLIDO]» obliga a rellenar
desde la cédula, que es la fuente correcta. Se conservan pólizas, fechas, montos y
artículos: una plantilla sin sus hechos no sirve de plantilla.

### 3. Tres barreras de calidad, no una

| Barrera | Qué ve | Qué no ve |
|---|---|---|
| `verificar_admisorio.py` | La forma | Que los datos existan |
| `construir_admisorio.py` | Residuo de la plantilla de origen | Un dato que no viene de ningún sitio |
| `auditar_admisorio.py` | **Que cada dato exista en el expediente** | La coherencia jurídica |

La tercera, en su primer barrido sobre cuatro admisorios ya dados por buenos,
encontró cuatro fechas sin ancla, un ordinal que contradecía a su cédula y dos
apellidos inventados.

### 4. El sistema se comprueba a sí mismo

`scripts/autocomprobacion.py`, que CI ejecuta en cada push. Cuatro pruebas, cada
una nacida de un fallo real:

- ninguna expresión regular con un carácter de retroceso donde debe ir un límite de
  palabra —pasó **tres veces**, y la peor dejó R-110 declarando `OK` sin comprobar
  nada sobre todos los documentos—;
- ninguna plantilla con datos personales;
- todos los módulos compilan —se compila, no se importa: importar los ejecuta, y
  una prueba que modifica el repositorio que comprueba no es una prueba—;
- ningún artefacto de trabajo rastreado.

CI le da además al verificador un documento que **debe** rechazar. Una regla que
nunca falla no es una regla que se cumple: es una regla que no se está ejecutando.

## Lo que sigue sin resolver

1. **El historial público.** El repositorio lleva meses abierto y su historial
   contiene los expedientes que hoy se retiran. Retirarlos del árbol no los quita
   del historial; eso solo lo hace el soporte de GitHub, o deja de importar si el
   repositorio pasa a privado. **Es una decisión del instructor.**
2. **Ningún proyecto de Antigravity apunta al repositorio.** Es la causa raíz
   medida de casi todos los fallos del agente. `scripts/orquestar.py sanear` lo
   diagnostica y acota el daño, pero el arreglo real es una acción manual, una sola
   vez: *Antigravity → Add Workspace → la raíz del repositorio*.
3. **La constancia de lectura (`_LECTURA.md`) no está garantizada por el sistema.**
   Un agente podría escribirla sin haber mirado. Hoy lo cubre la relectura del
   supervisor, que es una garantía humana y no mecánica.

## Cifras

| | |
|---|---:|
| Plantillas maestras anonimizadas | 620 |
| Ramas taxonómicas | 17 |
| Herramientas en `scripts/` | 19 |
| Reglas con falsador | 58 |
| Archivos publicados | 725 (antes 1.481) |
