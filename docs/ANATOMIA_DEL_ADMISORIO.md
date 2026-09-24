# ANATOMÍA DEL ADMISORIO

> **Documento de consulta.** Si contradice a `AGENTS.md`, manda `AGENTS.md` (reglas vigentes v3.1, 24/09/2026).


> Qué comparten los 630 modelos, qué varía y por qué. Todo medido el 15/09/2026
> sobre el corpus, no deducido de la memoria documentada.

## 0. Primero, una corrección de censo

De las **593 plantillas** del árbol actual, **566 son admisorios**. Las otras 27 son
resoluciones de confidencialidad (esquema `ANTECEDENTES / ANÁLISIS / SE RESUELVE`)
y decretos cortos (`VISTO / CONSIDERANDO / SE HA RESUELTO`). Por eso ninguna
medición de anatomía llega al 100 %: ese techo del ~96 % **no es incumplimiento,
es que el denominador estaba mal**.

## 1. El esqueleto: diez ordinales, siempre en el mismo orden

```
        ┌─────────────────────────── ENCABEZADO ───────────────────────────┐
        │ EXPEDIENTE · DENUNCIANTE · DENUNCIADO · MATERIAS · RESOLUCIÓN N°  │
        └──────────────────────────────────────────────────────────────────┘
                                      │
        ┌─────────── I. HECHOS ───────┴────────────────────────────────────┐
        │  «Mediante el escrito del …, el señor [APELLIDO] denunció a …»   │
        │  (i) fecha + hecho · (ii) fecha + hecho · (iii) …                │
        └──────────────────────────────────────────────────────────────────┘
                                      │
        ┌─────────── II. CONSIDERATIVA ┴───────────────────────────────────┐
        │  «La Secretaría Técnica … considera que el hecho denunciado …»   │
        │  → subsunción + tipificación          ══ ISOMORFISMO VERBATIM ══╗│
        └─────────────────────────────────────────────────────────────────║┘
                                      │                                   ║
        ┌─────────── III. RESOLUTIVA ──┴───────────────────────────────────║┐
        │  PRIMERO   admitir a trámite + imputaciones  ◄═══════════════════╝│
        │  SEGUNDO   tener por ofrecidos los medios probatorios             │
        │  TERCERO   personería, RUC, domicilio procesal y condición MYPE   │
        │  CUARTO    correr traslado al denunciado                          │
        │  QUINTO    requerimiento de información del siniestro             │
        │  SEXTO     sanción hasta 450 UIT (art. 110 del Código)            │
        │  SÉTIMO    costas y gastos (art. 39 del D.L. 807)                 │
        │  OCTAVO    conciliación (art. 29 del D.L. 807)                    │
        │  NOVENO    reserva o medida complementaria                        │
        │  DÉCIMO    acuse de recibo de la notificación                     │
        │  DÉCIMO PRIMERO / DÉCIMO SEGUNDO  →  una por VÍA (R-147)          │
        └──────────────────────────────────────────────────────────────────┘
                                      │
        ┌──────────────────────────────┴───────────────────────────────────┐
        │  Firma: config/firmas.json (Rímac: Ad Hoc; nunca «(e)»)         │
        └──────────────────────────────────────────────────────────────────┘
```

Frecuencia medida de cada ordinal sobre los 603 admisorios:

| Ordinal | Contenido | Presencia | |
|---|---|---:|---|
| PRIMERO | admitir a trámite | 90,0 % | `██████████████████` |
| SEGUNDO | medios probatorios | 91,4 % | `██████████████████` |
| TERCERO | personería y MYPE | 89,6 % | `█████████████████` |
| CUARTO | correr traslado | 88,7 % | `█████████████████` |
| QUINTO | requerir información | 86,6 % | `█████████████████` |
| SEXTO | sanción 450 UIT | 90,9 % | `██████████████████` |
| OCTAVO | conciliación | 72,3 % | `██████████████` |
| DÉCIMO | acuse de recibo | 92,9 % | `██████████████████` |

## 2. Lo que comparten **todos**, más allá de la imputación

| Elemento | Presencia |
|---|---:|
| Sanción hasta 450 UIT (art. 110) | 96,5 % |
| Admisión a trámite | 96,5 % |
| Costas y gastos (art. 39 D.L. 807) | 96,3 % |
| Condición MYPE | 96,2 % |
| Personería ante Registros Públicos | 95,9 % |
| Domicilio procesal (art. 442 C.P.C.) | 95,9 % |
| Conciliación (art. 29 D.L. 807) | 95,7 % |
| Requerimiento de información | 95,7 % |
| Correr traslado | 95,6 % |
| Medios probatorios ofrecidos | 94,1 % |
| Subsunción de la Secretaría Técnica | 94,0 % |

Corregido por el denominador real (603), **todos estos elementos están en
prácticamente el 100 % de los admisorios**. No son opcionales: son el cuerpo del
acto.

## 3. Ortografía forense de los ordinales

El corpus no escribe los ordinales como el diccionario:

| Forma | Veces | Veredicto |
|---|---:|---|
| **SÉTIMO** | **579** | la del corpus |
| SÉPTIMO | 12 | desviación |
| SETIMO | 4 | desviación |
| **DÉCIMO PRIMERO** | **485** | la del corpus |
| **DÉCIMO SEGUNDO** | **152** | la del corpus |
| UNDÉCIMO / DUODÉCIMO | **0** | no existe en el corpus |

## 4. Por qué existen diferencias entre modelos

Las diferencias **no son estilísticas: son estructurales**, y cada una tiene su
causa.

### 4.1 La vía de notificación la fijan las partes, no el redactor

```
  denunciante  ──── persona natural ───────────►  correo electrónico   (2 días)
  denunciado   ──── aseguradora/banco con SINE ─►  Casilla Electrónica (5 días)
  cualquiera   ──── sin canal electrónico ──────►  domicilio procesal  (2 días)
```

Medido por tipo de denunciado:

| Tipo de denunciado | n | combinación dominante |
|---|---:|---|
| 2 o más denunciados varios | 403 | casilla + correo (262) |
| 1 denunciado aseguradora | 89 | casilla + correo (72) |
| 2 denunciados banco y aseguradora | 57 | casilla + correo (42) |
| 1 denunciado banco o financiera | 29 | casilla + correo (16) |

**`casilla + correo` es la norma** porque el reparto típico es una empresa con
Casilla Electrónica y un consumidor con correo. El `domicilio procesal` aparece
solo en el **6,8 %**: son los casos en que una parte carece de canal electrónico.
Por eso un admisorio tiene 10, 11 o 12 ordinales: **uno por parte a notificar**.

### 4.2 Otras diferencias y su causa

| Diferencia | Presencia | Causa |
|---|---:|---|
| Libro de reclamaciones | 7,8 % | Solo cuando la conducta denunciada lo involucra (art. 150) |
| Medida correctiva | 91,9 % | Falta cuando el denunciante no la pidió |
| Bloque de firma digital | 44,3 % → 100 % | La mitad de las plantillas se guardó sin «Firmado digitalmente por»; desde v3.1 es obligatorio (R-193) y el corpus está migrado |
| Apertura «Mediante el escrito» | 79,8 % | El resto abre por subsanación o por traslado de otra comisión |

## 5. Qué se puede parametrizar, y qué no

**Parametrizable** (ya implementado como regla con falsador):

| Regla | Qué fija |
|---|---|
| R-137 | Google Lens en todas las páginas, cero OCR |
| R-138 | Partes y vía, exactamente las de la cédula |
| R-143 | Solo las 64 combinaciones de imputación del corpus |
| R-144 | Fuente, alineación, interlineado y encuadre |
| R-145 | Sub-incisos en romanos minúsculos `(i) (ii)` |
| R-146 | Secuencia de ordinales y su ortografía forense |
| R-155 | Fórmula obligatoria de traslado y descargos con apercibimiento y art. 223 LPAG |

**No parametrizable, y conviene decirlo:** cuál de las 64 imputaciones corresponde
a los hechos de un expediente concreto. Eso es subsunción, es criterio jurídico, y
el sistema solo puede impedir que se invente una que no existe — no puede elegir
por el redactor.
