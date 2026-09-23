# PLAN — el workspace de Antigravity

> **Documento de consulta.** Si contradice a `AGENTS.md`, manda `AGENTS.md` (reglas vigentes v3, 23/09/2026).


> La causa raíz de casi todos los fallos del agente, y el plan para dejar de
> parchearla. Escrito el 15/09/2026.

## 1. El hallazgo

Preguntándole a su propia API por los metadatos de una conversación:

```
workspaceFolderAbsoluteUri: file:///c:/Users/D/_ConfigIA/.resadmi
```

`.resadmi` es una carpeta con **una sola subcarpeta**. Desde ahí no existen ni
`AGENTS.md`, ni `scripts/`, ni `plantillas_maestras/`. Comprobado también que
**ningún proyecto de Antigravity apunta al repositorio**: los únicos que hay
apuntan a `.resadmi` y a un proyecto ajeno.

## 2. Por qué explica casi todo

Casi todos los fallos medidos del agente son consecuencias, no causas
independientes:

| Lo que se veía | Lo que era |
|---|---|
| «No lee las reglas» | El `AGENTS.md` que carga al arrancar no es el del repositorio, porque su raíz es otra |
| «Busca scripts con `-Recurse` por todo `C:\Users`» | Busca en su raíz, no los encuentra, y amplía |
| «Se va a otros proyectos» | Desde una carpeta casi vacía, cualquier ruta parece tan buena como otra |
| «Gastó 67 llamadas y 19,6 minutos sin producir el triaje» | Las gastó buscando lo que tenía a un `cd` de distancia |

## 3. Por qué el `AGENTS.md` de redirección **no** es el arreglo

Dejar un archivo en `.resadmi` que dice «el trabajo está en otro sitio» es una
**instrucción**, y este sistema ya tiene medido lo que valen las instrucciones que
dependen de que el agente se acuerde:

- se le ordenó leer con Lens y, en la tanda siguiente, **los tres agentes
  entregaron con cero toques a imagen** (R-137);
- se le dijo el nombre de la rama y **se inventó una que no existe**;
- se le prohibió salir de dos carpetas y **abrió un tercer proyecto**.

Un archivo de redirección solo funciona si el agente lo lee y lo obedece. Eso es
exactamente lo que no se puede dar por hecho.

## 4. La jerarquía de arreglos, de mejor a peor

**Primero: eliminar la posibilidad del error.** Un proyecto de Antigravity cuyo
workspace sea la raíz del repositorio. Entonces el agente arranca donde debe, carga
el `AGENTS.md` correcto y las rutas relativas funcionan. Es **la única solución
real**, y requiere una acción manual, una sola vez:

```
Antigravity → Add Workspace → C:\Users\D\Code\repos\SystemHope-ResAdmis
```

No se puede hacer desde la API: `agentapi` ofrece `new-conversation`,
`send-message` y `get-conversation-metadata`, y ninguno crea proyectos. Se
verificó.

**Segundo: volver el error inofensivo.** Ya está hecho, y por eso el sistema
funciona pese a la causa raíz:

- `admisorio.py` y el resto del utillaje **fijan la raíz por construcción**
  (`Path(__file__).resolve().parent.parent`): da igual desde dónde se invoquen;
- el encargo canónico de `orquestar.py lanzar` lleva **rutas absolutas** y declara
  el Cwd por escrito;
- la orden de trabajo de cada caso trae el triaje, la cédula y las candidatas ya
  resueltas, así que no hay nada que buscar.

**Tercero: detectar y declarar.** `orquestar.py sanear` enumera los workspaces que
Antigravity ha usado, marca los que no son el repositorio y, si no hay ninguno
correcto, lo dice con el remedio exacto en pantalla.

**Cuarto, y el más débil: redirigir.** El `AGENTS.md` de redirección, que `sanear`
escribe **solo** en workspaces relacionados con este trabajo. La primera versión lo
dejó caer en un proyecto ajeno del instructor: ensuciar el trabajo de otro para
proteger el propio no vale, y se corrigió.

## 5. Qué hacer, en orden

1. **Una vez, a mano:** añadir el repositorio como workspace en Antigravity.
2. **Antes de cada remesa:** `python scripts/orquestar.py sanear`. Si dice que
   ningún proyecto apunta al repositorio, el paso 1 no se hizo.
3. **Al lanzar cada caso:** `python scripts/orquestar.py lanzar <expediente>`, que
   usa el encargo canónico con rutas absolutas.
4. **Mientras trabaja:** vigilar con `vigilar_remesa.py`. Un Cwd ajeno o una
   búsqueda recursiva en la traza significa que el paso 1 se deshizo.

## 6. Lo que este plan enseña más allá de Antigravity

Se tardó una remesa entera en mirar el workspace, porque cada síntoma parecía un
fallo con entidad propia y se fue corrigiendo uno por uno: la rama inventada, la
visión que no llegaba, las carpetas ajenas. Ninguna de esas correcciones estaba
mal, pero ninguna tocaba la causa.

Queda como **R-142**: antes de corregir el tercer síntoma del mismo agente, mirar
de dónde arranca. Y el corolario incómodo: **una causa raíz que solo se puede
parchear hay que declararla como tal**, no dejar que el parche pase por solución.
Este documento existe para que el parche no se confunda con el arreglo.
