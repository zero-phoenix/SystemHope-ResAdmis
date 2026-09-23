---
name: admisorio-flujo
description: Redactar de principio a fin una resolución de admisión a trámite e imputación de cargos de la Comisión de Protección al Consumidor 1 de Indecopi (seguros) a partir de los PDF de un expediente, con los scripts del repositorio SystemHope-ResAdmis.
---

# Flujo del admisorio CC1

## Objetivo
Un `ADM <EXP> R<N>.docx` que el verificador declare **APTO** y `entregar` declare **ENTREGABLE**, sin un solo dato que no esté en el expediente.

## Instrucciones
1. **Reglas**: lee `AGENTS.md` completo y las skills `imputaciones` y `partes-y-notificacion`. Si el caso trae una solicitud de confidencialidad, lee también `confidencialidad`.
2. **Fecha**: si `scripts/config_sistema.py` dice «sin fijar», pregunta la fecha de emisión al instructor.
3. **Preparar**: `scripts/admisorio.py preparar <carpeta> --denunciados N --sujeto <clase> [--subtipo confidencialidad] [--rama X] [--contiene "frase"]`.
   - `N` es el número real de proveedores denunciados (1, 2, o 3 = 3 o más).
   - Las candidatas marcadas **APTA** (0 falsadores) van primero. Elige una APTA de la misma rama, el mismo número de denunciados y la misma clase de denunciante.
   - La carpeta física de la plantilla **no** indica el número de denunciados; el índice sí.
4. **Leer**: abre **cada** PNG de `_paginas/` (captura de la página completa) y llena su fila de `_LECTURA.md` con lo que ves, incluidos formato, sellos, firmas y resaltados. Cero OCR; el texto seleccionable solo sirve para contrastar.
5. **Las 10 plantillas más similares (obligatorio)**: `_CASO.json` y `scripts/similares.py <carpeta>`; justifica cada una en `_SIMILARES.md` (imputaciones: norma, sujeto, conducta y fecha; hechos; partes). La base sale de esas 10.
6. **Anclar los datos** de cada documento (escrito de parte = fecha de su FIRMA DIGITAL; documento de Indecopi = fecha de emisión del texto):
   - denuncia: fecha y hechos;
   - subsanación o escritos complementarios: fecha;
   - memorándum o documento de traslado: número, fecha de emisión y fecha de recepción en CC1;
   - cédula: partes, vía de cada parte y número de resolución;
   - resolución de programación de audiencia de conciliación: es anterior y no se cita como hecho.
7. **Redactar el mapa** (`mapa.json`, en la carpeta del caso) sobre la plantilla y construir con `scripts/construir_admisorio.py --mapa`.
8. **Entregar**: `scripts/admisorio.py entregar "<docx>" --recepcion DD/MM/AAAA`. Si algo falla, corrige y repite. No entregues sin ENTREGABLE.

## Estructura (orden fijo)
Encabezado:
- EXPEDIENTE
- DENUNCIANTE(S) (ALIAS)
- DENUNCIADO(S) (ALIAS)
- MATERIAS
- RESOLUCIÓN
- «Lima, [fecha]»

Secciones:
- **I. HECHOS**:
  - abre con «Mediante el escrito del …, subsanado mediante escrito del …, [tratativa] denunció a [alias] por presuntas infracciones a la Ley 29571, Código de Protección y Defensa del Consumidor (en adelante, Código), señalando lo siguiente:» (583 de 585 plantillas);
  - sigue con viñetas cronológicas en pasado; casi la mitad empieza con la fecha: «El 16 de agosto de 2024, …»;
  - cierra con «[Tratativa] solicitó, en calidad de medida correctiva, que … cumpla con: (i) …; y, (ii) …. Asimismo, requirió el reembolso de costos y costas del presente procedimiento.» (573 de 585).
- **II. DE LA ADMISIÓN A TRÁMITE**: un párrafo por imputación (skill `imputaciones`) y «En tanto la denuncia reúne los requisitos…, corresponde admitirla a trámite».
- **III. REQUERIMIENTO DE INFORMACIÓN**: lo que se pide a **cada** denunciado.
- **RESOLUCIÓN DE LA SECRETARÍA TÉCNICA**:
  1. PRIMERO: admitir, con las imputaciones en el mismo orden;
  2. SEGUNDO: medios probatorios;
  3. TERCERO: requisitos a **todos** los denunciados;
  4. CUARTO: traslado (fórmula R-155);
  5. QUINTO y siguientes: un requerimiento de información por denunciado;
  6. luego, en este orden: 450 UIT (art. 110); gastos (art. 39 del Decreto Legislativo 807); conciliación (art. 29); desistimiento;
  7. al final, un ordinal de notificación por vía.
- **Firma**: la de `config/firmas.json`.

## Qué NO se pone en HECHOS
- La palabra «denunciante».
- Calificaciones jurídicas o artículos.
- «Habría».
- Adjetivos del consumidor sobre el proveedor como si fueran hechos.
- Pretensiones fuera del párrafo de medida correctiva.
- Datos que no estén en el expediente.

## Formato
- Arial Narrow; 11 pt en el cuerpo y 8 pt en las notas.
- Interlineado sencillo, espaciado 0/0, justificado.
- Sangría izquierda de 1,0 cm y francesa de 1,0 cm.
- Márgenes de 2,5 cm arriba y abajo y 3,0 cm a los lados.
- Notas al pie con llamada en superíndice.
- Pie `M-CPC-01/03`.
- Sin resaltados.
- Fechas «de 2025» (nunca «del 2025»); números sin «N°».

## Restricciones
- Nunca OCR, nunca PDF, nunca Word por COM.
- Nunca copiar datos de la plantilla que no sean del caso (el constructor lo audita).
- Nunca publicar ni commitear el expediente.
