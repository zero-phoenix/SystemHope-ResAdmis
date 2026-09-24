# SystemHope ResAdmis v3

> **Agente (Google Antigravity): si el usuario te pegó el enlace de este repositorio para redactar un admisorio, NO sigas leyendo aquí. Lee y ejecuta, en orden, [`ARRANQUE.md`](https://github.com/zero-phoenix/SystemHope-ResAdmis/blob/main/ARRANQUE.md) (texto plano: https://raw.githubusercontent.com/zero-phoenix/SystemHope-ResAdmis/main/ARRANQUE.md).**

Sistema para que **Google Antigravity** redacte las resoluciones de **admisión a trámite e
imputación de cargos** de la Comisión de Protección al Consumidor 1 (CC1) de Indecopi en
materia de **seguros**, con un verificador que rechaza lo que no se ajusta a la práctica medida
de la Comisión.

- **Reglas**: [`AGENTS.md`](AGENTS.md) es la única fuente vigente. Tiene menos de 12 000 caracteres, el límite de reglas de Antigravity.
- **Redactor**: Google Antigravity con Gemini 3.8 Flash High o el modelo superior vigente.
- **Cualquier PC**: en una conversación nueva de Antigravity, pega `https://github.com/zero-phoenix/SystemHope-ResAdmis/blob/main/ARRANQUE.md` y adjunta los PDF del expediente. [`ARRANQUE.md`](ARRANQUE.md) instala Python y Git portátiles en `%USERPROFILE%\SystemHope\` (sin administrador) y guía al agente.
- **Skills de Antigravity**: `.agents/skills/` (flujo, imputaciones, partes y notificación, confidencialidad).

## Uso (desde la raíz del repositorio)

```bash
pip install -r requirements.txt
python scripts/comprobar_anclaje.py
python scripts/admisorio.py preparar <carpeta_del_expediente>
#  -> lectura visual de cada página (_paginas/*.png), _LECTURA.md y _FORMATO.md (formato de cada hoja, sin OCR)
python scripts/construir_admisorio.py --mapa <mapa.json>
python scripts/admisorio.py previsualizar "<carpeta>/ADM <EXP> R<N>.docx" --contra <plantilla.docx>
#  -> _vista/: cada página como imagen (ONLYOFFICE, fiel a Word; LibreOffice solo como vista aproximada)
python scripts/admisorio.py entregar "<carpeta>/ADM <EXP> R<N>.docx"
```

Utilidades:
- `scripts/inspeccionar_docx.py <docx> [--diff <control>]` inspecciona o compara documentos.
- `scripts/medir_formato.py <docx|pdf> [--comparar]` mide la huella de formato sin OCR (estructura del archivo).
- `scripts/clasificar_corpus.py` clasifica las plantillas por contenido (denunciantes, denunciados, vías, subtipos, calidad).
- `scripts/prueba_verificador.py` somete al verificador a mutaciones: cada regla debe rechazar su error.
- `scripts/prueba_casos.py` construye los expedientes ficticios de `pruebas/ficticios/` y exige APTO (regresión de extremo a extremo).
- `scripts/migraciones/migrar_v3_1.py [--escribir]` aplica al corpus las reglas generales v3.1 (idempotente).
- `scripts/sanear_admisorio.py <docx>` es el saneamiento final v3.2. `construir_admisorio.py` lo llama solo; se puede correr a mano sobre un Word ya construido.

## Datos de referencia (`docs/`)

| Archivo | Contenido |
|---|---|
| `tabla_tipificacion.json` | Tabla de hechos infractores y tipificación del instructor: **referencial**. Mandan las plantillas: se imputa como ellas imputan un hecho de igual sentido y finalidad (v3.2). |
| `catalogo_imputaciones.json` | Formas literales de imputación del corpus, depuradas contra la tabla. |
| `plantillas_maestras_index.json` | Índice de las **574 plantillas** de `plantillas_maestras/`. |
| `estilo_formato.json` | Perfil de formato medido del corpus (`scripts/medir_formato.py`). |
| `IMPUTACIONES_ANALITICO.md` | Cómo se redacta cada imputación, por qué y qué no hacer (medido). |
| `directorio_proveedores_domicilios.json` | Vía de notificación histórica de cada proveedor. |
| `casillas_habilitadas.json` | Proveedores con casilla electrónica habilitada (R-151). |

## Forma (medida en el corpus)

- Arial Narrow en el 100 % del texto; 11 pt en el cuerpo y 8 pt en las notas.
- Interlineado sencillo en el 94 % de los párrafos; espaciado 0/0; justificado.
- Márgenes de 2,5 cm arriba y abajo y 3,0 cm a los lados.
- Pie `M-CPC-01/03`, notas en superíndice, sin resaltados.

## Plantillas por rama (574)

| Rama | N |
|---|---|
| 01 seguro vehicular | 167 |
| 02 seguro vida | 130 |
| 03 seguro desgravamen | 59 |
| 04 seguro proteccion tarjetas y dinero | 35 |
| 05 soat y afocat | 43 |
| 06 seguro hogar e inmuebles | 19 |
| 07 seguro sctr | 18 |
| 08 seguro salud eps oncologico | 12 |
| 09 seguro patrimonial caucion rc | 8 |
| 10 seguro sepelio | 7 |
| 11 seguro accidentes personales | 7 |
| 12 seguro transporte y carga | 3 |
| 13 seguro multiple y equipos | 4 |
| 14 seguro desempleo | 2 |
| 15 sistema previsional afp onp | 1 |
| 16 temas administrativos financieros | 4 |
| 17 seguro no especificado | 55 |

Por contenido (índice v3): 457 con 1 denunciado, 102 con 2, 15 con 3 o más; 23 con confidencialidad; 336 aptas como base (0 falsadores).

## Novedades v3.4 (24/09/2026)

Revisión del instructor sobre el Exp. 2898-2026 R2. Cada mandato tiene su falsador y su mutación en CI (51 mutaciones).

| Mandato | Regla |
|---|---|
| Viñetas de HECHOS con sujeto tácito; la tratativa («la señora X») solo en la apertura y en la medida correctiva (94 % del corpus) | R-210 |
| Negativa de cobertura «de manera injustificada» o «de manera indebida», nunca «injustificadamente» | R-209 |
| El rótulo del requerimiento de cada denunciado va subrayado; el saneador lo repone | R-208 |

## Novedades v3.3 (24/09/2026)

En la considerativa, toda imputación por el deber de información cierra el hecho con «; involucraría una presunta afectación al derecho de información de los consumidores. Por consiguiente, corresponde calificar el hecho materia de denuncia como una presunta infracción al deber de información, tipificado en el artículo 1, numeral 1, literal b) y al artículo 2 del Código.» Aplicado a 168 plantillas (232 párrafos); el constructor la añade y el verificador la exige (R-207). El resolutivo no cambia.

## Novedades v3.2 (24/09/2026)

Estas son las correcciones definitivas del instructor sobre la remesa de 11 admisorios y sobre el Exp. 3092-2026, rehecho con su expediente. Cada una tiene su falsador en el verificador y su mutación en CI.

| Mandato | Regla |
|---|---|
| Mandan las plantillas: se imputa como ellas imputan un hecho de igual sentido y finalidad; la tabla es referencial | AGENTS §2.4 |
| Una imputación por cada solicitud y por cada cobertura diferenciada, aunque se hayan pedido juntas | R-206 |
| «La denunciante» en las imputaciones, nunca «la parte denunciante» | R-205 |
| «Compañía aseguradora», nunca «aseguradora» a secas | R-201 |
| El seguro «se adquirió», no «contaba con» | R-204 |
| Hechos e imputaciones sin palabras valorativas («únicamente», «totalmente»…) | R-203 |
| La nota de la norma imputada va solo en la primera imputación de ese artículo | R-202 |
| Una línea en blanco entre imputaciones; se conserva la inadmisibilidad dejada sin efecto | AGENTS §7 |

El constructor sanea el documento al terminar (`scripts/sanear_admisorio.py`):
- separa las imputaciones;
- repara las notas del traslado, del Código y de competencia;
- quita la nota sobre la presentación en CC1;
- renumera las notas sin colisiones.

Además, `entregar` ancla la misma fecha escrita en letras o en números, y con «setiembre» o «septiembre».

## Integración continua

- `ci.yml`: autocomprobación, compilación, motor y mutaciones del verificador.
- `admisorio_gate.yml`: guardia de fugas de expediente en cada push.
- `generate_release.yml`: ejecutable y paquete.

## Historial

Ver [`CHANGELOG.md`](CHANGELOG.md). El código de la antigua aplicación de escritorio se conserva en la
rama `archivo-legado`.
