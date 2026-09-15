# SystemHope ResAdmis — CC1

Sistema de apoyo a la redacción de **resoluciones admisorias** de la Comisión de
Protección al Consumidor N° 1 del Indecopi. Un agente redacta; el repositorio le
da las plantillas, las reglas y —sobre todo— las barreras que impiden que un
documento salga con datos que no existen.

> **Norma marco:** Decreto Supremo 006-2026-JUS (TUO de la LPAG).
> **Los datos personales no entran aquí.** Este repositorio es público. Las
> plantillas están anonimizadas y ningún expediente, mapa de trabajo ni admisorio
> emitido se commitea. Hay una guardia que lo impide y CI la vuelve a comprobar.

## Qué hay dentro

| | |
|---|---|
| **620 plantillas maestras** (`plantillas_maestras/`) | Admisorios reales **anonimizados**, clasificados en 17 ramas por materia, tipo de denunciado y sujeto |
| **18 herramientas** (`scripts/`) | El utillaje completo: triaje, construcción, verificación, auditoría, orquestación y vigilancia |
| **56 reglas** (`automatizacion_antigravity/REGLAS_DE_APRENDIZAJE.md`) | Cada una con su **falsador**: la observación concreta que la refutaría |
| **Documentación** (`docs/`) | Índice taxonómico, directorio de proveedores y vías, plan de velocidad y manual de supervisión |

## El ciclo de un admisorio

```bash
# 1. Preparar el caso: triaje, cédula, dossier anclado y candidatas de plantilla
python scripts/preparar_remesa.py <carpeta-remesa> --caso 3122-2026

# 2. Leer TODAS las páginas con Google Lens (las deja renderizadas en _paginas/)
#    Cero OCR. El volcado de texto es contraste, no fuente.

# 3. Construir, sin abrir Word
python scripts/construir_admisorio.py --mapa mapa.json

# 4. Entregar: verificador + guardia + auditoría de fondo, en una llamada
python scripts/admisorio.py entregar "<ruta>/ADM 3122-2026 R1.docx" --caso 3122
```

El entregable se llama **`ADM <EXPEDIENTE> R<N>.docx`**, donde `N` es el número de
resolución **que fija la cédula** del expediente.

## Las tres barreras, y qué ve cada una

Ninguna sustituye a las otras. Un documento puede pasar dos y ser inservible.

| Barrera | Comprueba | Lo que **no** ve |
|---|---|---|
| `verificar_admisorio.py` | La forma: firma, ordinales, negritas, espejos, modo verbal | Que los datos existan |
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
  vía de notificación cada una.
- **Ni Word ni scratch** (R-139). Un `.docx` es un ZIP de XML y se edita en 0,3 s;
  abrir Word cuesta 8,4 s y su proceso huérfano es la causa medida de cuelgue.
- **Prohibido generar PDF.** El entregable es `.docx`.
- **Nada que no conste en el expediente.** Un dato sin ancla se eleva, no se
  rellena.

## Supervisión de agentes

Si diriges a un agente redactor, empieza por
**[`docs/SUPERVISION_DE_AGENTES.md`](docs/SUPERVISION_DE_AGENTES.md)**: la
superficie de control, qué medir, cuándo intervenir, y los dos catálogos de fallos
medidos —los del agente y los del supervisor—.

```bash
python scripts/orquestar.py estado              # conversaciones y su estado
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
