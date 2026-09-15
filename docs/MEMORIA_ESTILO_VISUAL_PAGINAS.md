# MEMORIA PERMANENTE OBLIGATORIA: ESTILO VISUAL Y FORMATO DE PÁGINA (INDECOPI CC1)

> **ESTADO:** NORMA TÉCNICA INSTITUCIONAL PERMANENTE  
> **ORIGEN:** Análisis forense visual multimodal (Google Lens / Visión Multimodal) sobre el corpus de 881 resoluciones PDF de referencia en `000 PLAN PHOENYX`.  
> **ALCANCE:** De cumplimiento estricto y obligatorio para el motor generador, plantillas maestras y cualquier resolución administrativa emitida por el sistema.

---

## 1. Regla Mandatoria de Archivos y Repositorio

- **Archivos para el Repositorio (GitHub):** **ÚNICAMENTE documentos Word (`.docx`)**. Queda terminantemente prohibido subir archivos `.pdf` pesados al repositorio Git para preservar la agilidad del código y la soberanía de las plantillas limpias.
- **Función de los PDFs:** Los 881 archivos PDF del corpus original actúan exclusivamente como **patrón de calibración geométrica y visual** mediante visión multimodal.
- **Inclusión en `.gitignore`:** `*.pdf` debe permanecer ignorado en la raíz de despliegue para evitar fugas de binarios pesados.

---

## 2. Geometría de Página y Dimensiones Físicas (A4)

| Parámetro | Medida en Puntos (pt) | Medida en Centímetros (cm) | Medida en Pulgadas (in) |
| :--- | :--- | :--- | :--- |
| **Tamaño de Papel** | `595.32 pt x 841.92 pt` | `21.00 cm x 29.70 cm` | A4 Standard |
| **Margen Superior** | `70.9 pt` | `2.50 cm` | `0.98 in` |
| **Margen Inferior** | `70.9 pt` | `2.50 cm` | `0.98 in` |
| **Margen Izquierdo** | `85.0 pt` | `3.00 cm` | `1.18 in` |
| **Margen Derecho** | `85.0 pt` | `3.00 cm` | `1.18 in` |  <!-- corregido 15/09/2026: la memoria decia 2,50 cm; el corpus mide 3,00 cm en 113 de 116 secciones. Manda el corpus. -->
| **Distancia Encabezado al borde** | `35.4 pt` | `1.25 cm` | `0.49 in` |
| **Distancia Pie de Página al borde** | `34.0 pt` | `1.20 cm` | `0.47 in` |
| **Ancho Útil de Texto** | `439.4 pt` | `15.50 cm` | `6.10 in` |

---

## 3. Tipografía y Micro-Espaciado

### 3.1. Fuente Institucional Única
- **Tipografía Primaria:** `Arial Narrow` (en todo el documento sin excepciones).
- **Variantes permitidas:** Regular, **Bold** (negrita), *Italic* (cursiva - sólo para locuciones latinas y nombres de expedientes), ***Bold Italic***.
- **Prohibición:** Queda prohibido el uso de Calibri, Times New Roman, Aptos o Arial estándar en el cuerpo de la resolución.

### 3.2. Jerarquía de Tamaños de Fuente
1. **Cuerpo del Documento (Considerandos y Resolutivos):** `11.0 pt`.
2. **Metadatos Iniciales (EXPEDIENTE, PARTES, ETC.):** `11.0 pt`.
3. **Encabezado Institucional (Texto Comisión):** `10.5 pt` o `11.0 pt` (Negrita mayúscula).
4. **Notas al Pie de Página (Footnotes):** `8.0 pt`.
5. **Iniciales de Responsabilidad Legal (ej. `LGP/JCQ`):** `8.0 pt`.
6. **Código Oficial de Formulario (`M-CPC-01/03`):** `8.0 pt`.
7. **Numeración de Página:** `8.0 pt`.

### 3.3. Interlineado y Párrafos
- **Interlineado:** Sencillo (`1.0` / `line_spacing = 1.0`).
- **Espacio anterior (`space_before`):** `0 pt`.
- **Espacio posterior (`space_after`):** `0 pt` (salvo separaciones de bloques temáticos que usan un retorno de carro de 11 pt).
- **Alineación:** Justificada (`WD_ALIGN_PARAGRAPH.JUSTIFY`) para todos los considerandos, hechos, resolutivos y notas al pie.
- **Alineación de Fechado:** Izquierda (`Lima, [día] de [mes] de [año]`).
- **Alineación de Encabezado Derecho:** Derecha (`WD_ALIGN_PARAGRAPH.RIGHT`).

---

## 4. Sangrías Escalonadas CC1 (Indentations)

### 4.1. Bloque de Metadatos (Cabecera de Partes)
- Estructura de dos columnas mediante tabulaciones o sangría francesa:
  - Margen izquierdo: `0 cm`
  - Posición de los dos puntos (`:`): `3.75 cm` (`1.48 in`).
  - Inicio de texto del valor: `4.00 cm` (`1.57 in`).
  - Etiquetas en negrita y mayúsculas:
    ```text
    EXPEDIENTE      :  1196-2026/CC1
    DENUNCIANTE     :  CHRISTIAN REATEGUI VARGAS (SEÑOR REATEGUI)
    DENUNCIADO      :  RÍMAC SEGUROS Y REASEGUROS S.A. (RÍMAC)
    MATERIAS        :  ADMISIÓN A TRÁMITE
                       REQUERIMIENTO DE INFORMACIÓN
    RESOLUCIÓN      :  1
    ```

### 4.2. Títulos de Sección
- `I.    HECHOS`
- `II.   DE LA ADMISIÓN A TRÁMITE DE LA DENUNCIA`
- `III.  REQUERIMIENTO DE INFORMACIÓN`
- `RESUELVE:`
  - Formato: Negrita, mayúsculas, sangría izquierda `0 cm`. Espacio antes de título: 1 línea en blanco.

### 4.3. Considerandos y Narrativa de Hechos
- **Párrafo introductorio:**
  - `1.    Mediante escrito de fecha...`
  - Sangría izquierda: `0.0 cm`, Primera línea: `0.0 cm`, Tabulador tras número: `1.0 cm` (`0.39 in`).
- **Incisos cronológicos de Hechos `(i)`, `(ii)`, `(iii)`...:**
  - Sangría izquierda: `2.00 cm` (`0.79 in`).
  - Sangría francesa (Hanging indent): `-1.00 cm` (`-0.39 in`).
  - Alineación: Justificada.
  - Separación entre incisos: `space_after = 0 pt`.

### 4.4. Parte Resolutiva (`RESUELVE`)
- **Artículos Resolutivos (`PRIMERO:`, `SEGUNDO:`, etc.):**
  - Sangría izquierda: `1.00 cm` (`0.39 in`).
  - Sangría francesa: `-1.00 cm` (`-0.39 in`).
  - La palabra ordinal va en negrita seguida de dos puntos (`PRIMERO: `, `SEGUNDO: `).
- **Sub-incisos de Requerimiento de Información (R-99 / R-108):**
  - Párrafo único consolidado (sin desglosar en múltiples párrafos para no perder compacidad).
  - Números romanos en minúscula entre paréntesis en línea: `(i) ...; (ii) ...; y, (iii) ...`.
  - Máximo 4 incisos por requerimiento. Corresponde verbatim con el considerando de requerimiento de información.

---

## 5. Encabezados, Pies y Elementos OpenXML

### 5.1. Encabezado Oficial
- **Logo Institucional:** Imagen oficial del escudo y logotipo de INDECOPI ubicado a la izquierda (`left: 0`, dentro del margen).
- **Texto Institucional:** Alineado a la derecha:
  ```text
  SECRETARÍA TÉCNICA DE LA
  COMISIÓN DE PROTECCIÓN AL CONSUMIDOR 1
  SEDE CENTRAL
  ```
  Fuente: `Arial Narrow Bold 10.5 pt`, color `#000000`.

### 5.2. Pie de Página Oficial
- **Código de Calidad Institucional:** `M-CPC-01/03` en la esquina inferior izquierda (`8.0 pt`).
- **Numeración de Página:** Campo dinámico de página centrado (`8.0 pt`).
- **Línea Separadora:** Opcional según modelo institucional.

### 5.3. Notas al Pie (Footnotes)
- **Separador:** Línea horizontal de 2 pulgadas a la izquierda.
- **Numeración:** Superíndice correlativo.
- **Tipografía:** `Arial Narrow 8.0 pt`, justificado.
- **Regla Anti-Autoformato Word (One Dot Leader):**
  - Cuando la nota al pie contenga listas numeradas, se utiliza el carácter **One Dot Leader (`\u2024`, U+2024)** en vez del punto regular (`.`) tras el número, para impedir que el motor de Microsoft Word aplique auto-sangrado de listas desconfigurando el margen.

### 5.4. Bloque de Firma Digital (Última Página)

> **La firma NO es una constante.** Depende del proveedor denunciado (regla R-103).
> Codificarla como valor fijo fue la causa raiz del error detectado en el Expediente 2662-2026.

- **Matriz de firma:**

  | Proveedor denunciado | Firmante | Cargo | Iniciales |
  |---|---|---|---|
  | Rímac Seguros y Reaseguros S.A. | `LUISA ANALÍ SILVA MALPARTIDA` | `Secretaria Técnica Ad Hoc` | `LSQ/DCQ` |
  | Cualquier otro proveedor | `EVELING ROA QUISPE` | `Secretaria Técnica` | según especialista instructor |

- **Centrado, cuatro líneas:**
  ```text
  Firmado digitalmente por
  [FIRMANTE según la matriz]
  [CARGO según la matriz]
  Comisión de Protección al Consumidor 1
  ```
- **Iniciales de Control de Calidad:**
  - Alineadas al margen izquierdo, línea inmediatamente posterior al bloque de firma.
  - Toman el valor de la matriz. El valor `LGP/JCQ` que figuraba aquí **no aparece en ningún
    documento de control verificado**; se retira hasta que exista evidencia que lo sustente.
  - Tamaño: `8.0 pt Arial Narrow`.
- **Verificación:** `scripts/verificar_admisorio.py` falsa automáticamente este bloque (prueba R-103).

---

## 6. Checklist de Verificación Visual Automatizada

Antes de entregar cualquier resolución generada:
1. [ ] Papel configurado en A4 (21 x 29.7 cm).
2. [ ] Márgenes exactos: Izq 3.0 cm, Der 2.5 cm, Sup 2.5 cm, Inf 2.5 cm.
3. [ ] 100% tipografía `Arial Narrow` (11 pt cuerpo, 8 pt notas al pie y pies de página).
4. [ ] Encabezado con logo INDECOPI y pie con código `M-CPC-01/03`.
5. [ ] Sangrías escalonadas verificadas: Hechos a `0.79"/-0.39"`, Resolutivo a `0.39"/-0.39"`.
6. [ ] Citas normativas actualizadas al **Decreto Supremo 006-2026-JUS** (publicado el 30 de abril de 2026).
7. [ ] Cero menciones a "inducción a error".
8. [ ] Reglas léxicas estrictas aplicadas (`cónyuge`, `luego de`, `esta` sin tilde, `médico`, `vehículo`).
9. [ ] Moneda institucional: `S/ X XXX,XX` o `US$ X XXX,XX`.
