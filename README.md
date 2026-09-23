# SystemHope ResAdmis v3

Sistema para que **Google Antigravity** redacte las resoluciones de **admisión a trámite e
imputación de cargos** de la Comisión de Protección al Consumidor 1 (CC1) de Indecopi en
materia de **seguros**, con un verificador que rechaza lo que no se ajusta a la práctica medida
de la Comisión.

- **Reglas**: [`AGENTS.md`](AGENTS.md) es la única fuente vigente. Tiene menos de 12 000 caracteres, el límite de reglas de Antigravity.
- **Redactor**: Google Antigravity con el modelo de [`config/modelo.json`](config/modelo.json) (Gemini 3.8 Flash High o superior).
- **Estado**: la parte 1 del plan v3 está aplicada. El uso desde cualquier PC con Python y Git portátiles llega en la parte 2.

## Uso (desde la raíz del repositorio)

```bash
pip install -r requirements.txt
python scripts/comprobar_anclaje.py
python scripts/config_sistema.py --fecha "25 de setiembre de 2026"   # fecha de la remesa
python scripts/admisorio.py preparar <carpeta_del_expediente>
#  -> lectura visual de cada página (_paginas/*.png) y _LECTURA.md
python scripts/construir_admisorio.py --mapa <mapa.json>
python scripts/admisorio.py entregar "<carpeta>/ADM <EXP> R<N>.docx" --recepcion DD/MM/AAAA
```

Utilidades:
- `scripts/plazos.py --desde DD/MM/AAAA` calcula el plazo de 20 días hábiles con los feriados del Perú. Se informa, no va en la resolución.
- `scripts/inspeccionar_docx.py <docx> [--diff <control>]` inspecciona o compara documentos.
- `scripts/prueba_verificador.py` somete al verificador a mutaciones: cada regla debe rechazar su error.

## Configuración única (`config/`)

| Archivo | Qué fija |
|---|---|
| `remesa.json` | Fecha de emisión de toda la remesa. Si está vacía, el agente la pregunta. |
| `firmas.json` | Firma según el denunciado: Eveling Roa Quispe, Secretaria Técnica; si hay Rímac, Luisa Analí Silva Malpartida, Secretaria Técnica Ad Hoc. |
| `modelo.json` | Modelo redactor exigido. |
| `feriados_peru.json` | Días no laborables adicionales. Los feriados nacionales se calculan solos. |

## Datos de referencia (`docs/`)

| Archivo | Contenido |
|---|---|
| `tabla_tipificacion.json` | Tabla de hechos infractores y tipificación del instructor: lista **cerrada** de artículos imputables. |
| `catalogo_imputaciones.json` | Formas literales de imputación del corpus, depuradas contra la tabla. |
| `plantillas_maestras_index.json` | Índice de las **578 plantillas** de `plantillas_maestras/`. |
| `directorio_proveedores_domicilios.json` | Vía de notificación histórica de cada proveedor. |
| `casillas_habilitadas.json` | Proveedores con casilla electrónica habilitada (R-151). |

## Forma (medida en el corpus)

- Arial Narrow en el 100 % del texto; 11 pt en el cuerpo y 8 pt en las notas.
- Interlineado sencillo en el 94 % de los párrafos; espaciado 0/0; justificado.
- Márgenes de 2,5 cm arriba y abajo y 3,0 cm a los lados.
- Pie `M-CPC-01/03`, notas en superíndice, sin resaltados.

## Plantillas por rama (578)

| Rama | N | Rama | N |
|---|---|---|---|
| 01 vehicular | 168 | 10 sepelio | 7 |
| 02 vida | 131 | 11 accidentes personales | 7 |
| 03 desgravamen | 59 | 12 transporte y carga | 3 |
| 04 protección de tarjetas y dinero | 35 | 13 múltiple y equipos | 4 |
| 05 SOAT y AFOCAT | 43 | 14 desempleo | 2 |
| 06 hogar e inmuebles | 20 | 15 sistema previsional | 1 |
| 07 SCTR | 18 | 16 temas administrativos financieros | 4 |
| 08 salud, EPS y oncológico | 12 | 17 no especificado | 56 |
| 09 patrimonial, caución y RC | 8 | | |

## Integración continua

- `ci.yml`: autocomprobación, compilación, motor y mutaciones del verificador.
- `admisorio_gate.yml`: guardia de fugas de expediente en cada push.
- `generate_release.yml`: ejecutable y paquete.

## Historial

Ver [`CHANGELOG.md`](CHANGELOG.md). El código de la antigua aplicación de escritorio se conserva en la
rama `archivo-legado`.
