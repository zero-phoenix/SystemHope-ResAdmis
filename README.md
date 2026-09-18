# SystemHope ResAdmis — CC1

Sistema de apoyo a la redacción de **resoluciones admisorias** de la Comisión de
Protección al Consumidor N° 1 del Indecopi. Un agente redacta; el repositorio le
da las plantillas, las reglas y —sobre todo— las barreras que impiden que un
documento salga con datos que no existen.

> **Norma marco:** Decreto Supremo 006-2026-JUS (TUO de la LPAG).
> **Los datos personales no entran aquí.** Este repositorio es público. Las
> plantillas están anonimizadas y ningún expediente, padrón, mapa de trabajo ni
> admisorio emitido se commitea. Hay una guardia que lo impide y CI la vuelve a
> comprobar.

---

## ⚠️ Antes de nada: el agente trabaja anclado, o no trabaja

```
Antigravity  →  Add Workspace  →  la raíz de este repositorio
```

`AGENTS.md` **solo gobierna si se ha cargado desde aquí**. Antigravity arrancaba
en `_ConfigIA/.resadmi`, una carpeta con una sola subcarpeta, y desde ahí no
existen ni las reglas, ni los scripts, ni las plantillas. Esa raíz equivocada es
la **causa raíz medida** de casi todos sus fallos: no leer las reglas, buscar
scripts con `-Recurse` por todo el disco, irse a proyectos ajenos, gastar 67
llamadas sin producir el triaje.

**Primer comando de toda sesión:**

```bash
python scripts/comprobar_anclaje.py
```

No es un aviso que se pueda olvidar: `admisorio.py preparar` —el paso 1 de todo
flujo— lo llama y **se detiene** si falla (R-152). Un archivo de redirección es
una instrucción, y este sistema tiene medido lo que valen las instrucciones que
dependen de que el agente se acuerde: se le ordenó leer con Lens y la tanda
siguiente entregó con cero toques a imagen.

---

## Qué hay dentro

| | |
|---|---|
| **593 plantillas maestras** (`plantillas_maestras/`) | Admisorios reales **anonimizados**, clasificados en 17 ramas por materia, tipo de denunciado y sujeto |
| **21 herramientas** (`scripts/`) | Triaje, construcción, verificación, auditoría, orquestación, vigilancia, anclaje y filtrado del padrón |
| **60 reglas** (`automatizacion_antigravity/REGLAS_DE_APRENDIZAJE.md`) | Cada una con su **falsador**: la observación concreta que la refutaría |
| **Documentación** (`docs/`) | Índice taxonómico, vías de notificación, casillas habilitadas, contradicciones resueltas, plan de velocidad y manual de supervisión |

## El ciclo de un admisorio

```bash
# 0. Comprobar que estás anclado al repositorio
python scripts/comprobar_anclaje.py

# 1. Preparar el caso: triaje, cédula, dossier anclado y candidatas de plantilla
python scripts/admisorio.py preparar <carpeta-remesa> --caso 3122-2026

# 2. Leer TODAS las páginas con Google Lens (las deja renderizadas en _paginas/)
#    Cero OCR. El volcado de texto es contraste, no fuente.

# 3. Construir, sin abrir Word
python scripts/construir_admisorio.py --mapa mapa.json

# 4. Entregar: verificador + guardia + auditoría de fondo, en una llamada
python scripts/admisorio.py entregar "<ruta>/ADM 3122-2026 R1.docx" --caso 3122
```

El entregable se llama **`ADM <EXPEDIENTE> R<N>.docx`**, donde `N` es el número de
resolución **que fija la cédula** del expediente.

---

## A quién se notifica, y de qué manera

La regla no es «un ordinal por parte»: es **un ordinal por vía**. Dos partes que
comparten vía van juntas en un solo ordinal, con el verbo en plural (93
plantillas). Dos vías distintas, dos ordinales (362). Fundirlas con `; y,` no
ocurre **ni una sola vez en 1 087 párrafos de notificación**.

```
  denunciante persona natural ──► correo electrónico ── 2 días ──► DÉCIMO
  proveedor con casilla ACTIVA ─► Casilla Electrónica ─ 5 días ──► DÉCIMO PRIMERO
  sin canal electrónico ───────► domicilio procesal ── 2 días ──► el último
```

### La Casilla Electrónica tiene tres requisitos (R-151)

Solo procede cuando el padrón de Términos y Condiciones está **ACTIVO**, hay
**número de e-casilla** y hay **teléfono móvil registrado y no vacío**. Si falta
cualquiera de los tres, **la casilla está prohibida**.

Es condición **necesaria, no suficiente**: estar habilitado no obliga a usar la
casilla —eso lo fija la cédula (R-129)—, pero no estarlo la prohíbe.

Medido sobre el padrón del 17/09/2026: de 30 005 registros activos, **13 244
(44 %) no tienen teléfono**. Entre los proveedores de la CC1 **no admiten
casilla** Rímac Seguros y Reaseguros (de baja en el padrón), el Banco de Crédito
del Perú, Banco Ripley, Banco Pichincha (de baja), Financiera Proempresa, Fovipol
y varias AFOCAT y Sub CAFAE.

**Dos fuentes independientes coinciden.** El padrón y el corpus de 593 plantillas
se midieron por separado y dan lo mismo en los tres cruces posibles: Rímac por
correo en 137 de 137, el BCP en 28 de 29, Ripley en 2 de 2. Dos instrumentos
distintos que miden lo mismo es la mejor corroboración que este sistema sabe dar.

```bash
# tras recibir un padrón nuevo
python scripts/filtrar_casillas.py <ReportePersonas....xlsx>
python scripts/filtrar_casillas.py <ReportePersonas....xlsx> --verificar
```

**El padrón no se versiona.** Trae 30 105 registros con DNI, nombres, correos y
teléfonos de consumidores. Solo se publica `docs/casillas_habilitadas.json`: el
veredicto por proveedor, sin una sola persona natural ni un dato de contacto.

---

## Las tres barreras, y qué ve cada una

Ninguna sustituye a las otras. Un documento puede pasar dos y ser inservible.

| Barrera | Comprueba | Lo que **no** ve |
|---|---|---|
| `verificar_admisorio.py` | La forma: firma, ordinales, negritas, espejos, modo verbal, **casilla habilitada** | Que los datos existan |
| `construir_admisorio.py` | Que no sobreviva nada de la plantilla de origen | Un dato que no viene de la plantilla ni de ningún sitio |
| `auditar_admisorio.py` | Que **cada dato exista en el expediente**, y las partes y el ordinal en la cédula | La coherencia jurídica del razonamiento |

La tercera se escribió tarde y, en su primer barrido sobre cuatro admisorios ya
dados por buenos, encontró cuatro fechas sin ancla, un ordinal que contradecía a
su cédula y dos apellidos inventados.

## Reglas que no se negocian

- **Cero OCR. Google Lens en todas las páginas** (R-137), tengan o no capa de
  texto. El texto embebido de un PDF es *contraste*: está medido que pierde tildes
  y corrompe cifras. Si discrepan, manda lo que se ve.
- **Las partes procesales son exactamente las de la cédula** (R-138), con una sola
  vía cada una, y la casilla exige además R-151.
- **Solo se imputa como imputan los modelos** (R-143). El corpus admite **64
  combinaciones**, catalogadas en `docs/catalogo_imputaciones.json`. Si la que
  hace falta no está, se eleva al instructor.
- **El núcleo fáctico se copia verbatim** de la considerativa al resolutivo
  (R-97): 86,5 % exacto por posición en el corpus.
- **Ni Word ni scratch** (R-139). Un `.docx` es un ZIP de XML y se edita en 0,3 s;
  abrir Word cuesta 8,4 s y su proceso huérfano es la causa medida de cuelgue.
- **Prohibido generar PDF.** El entregable es `.docx`.
- **Nada que no conste en el expediente.** Un dato sin ancla se eleva, no se
  rellena.

## Cómo se dirime una discrepancia

```
   0 de 593  ──►  PROHIBICIÓN ABSOLUTA        se corrige
   1 de 593  ──►  cuasi-absoluta: desviación   se corrige
  ≥5 de 593  ──►  NO es prohibición, es gusto  NO se toca
 mandato del instructor ──►  vence al corpus,  y se declara como mandato
```

Una prohibición sin frecuencia detrás es una opinión. Esa escala ya evitó tres
correcciones falsas: la volada de `artículo 20°` (que el propio boilerplate
prescribía y el corpus no usa ni una vez), la cita `los artículos 1 y 2` y el
subrayado del ordinal OCTAVO, que resultó estar en **593 de 593** plantillas.

Las contradicciones que el repositorio tenía consigo mismo están resueltas y
documentadas una por una en **[`docs/CONTRADICCIONES_RESUELTAS.md`](docs/CONTRADICCIONES_RESUELTAS.md)**.

## Supervisión de agentes

Si diriges a un agente redactor, empieza por
**[`docs/SUPERVISION_DE_AGENTES.md`](docs/SUPERVISION_DE_AGENTES.md)**: la
superficie de control, qué medir, cuándo intervenir, y los dos catálogos de fallos
medidos —los del agente y los del supervisor—.

```bash
python scripts/orquestar.py estado              # conversaciones y su estado
python scripts/orquestar.py sanear              # ¿algún workspace apunta aquí?
python scripts/orquestar.py lanzar 2765-2026    # encargo canónico del caso
python scripts/orquestar.py corregir <id> "..." # corrección en caliente
```

## Salud del repositorio

```bash
python scripts/autocomprobacion.py
```

Cuatro comprobaciones, cada una nacida de un fallo real: ninguna expresión regular
con un carácter de retroceso donde debe ir un límite de palabra, ninguna plantilla
con datos personales, todos los módulos compilan, ningún artefacto de trabajo
rastreado. CI las ejecuta en cada push, y además le da al verificador un documento
que **debe** rechazar: una regla que nunca falla no es una regla que se cumple.

## Instalación

```bash
pip install -r requirements.txt
python scripts/instalar_hooks.py     # guardia de datos personales en pre-commit
```

## Licencia

Ver [`LICENSE`](LICENSE). Contribuciones: [`CONTRIBUTING.md`](CONTRIBUTING.md).
