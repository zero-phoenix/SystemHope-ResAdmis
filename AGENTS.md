# DIRECTRICES MAESTRAS DEL SISTEMA (AGENTS.md)
# SISTEMA DE EMISION DE RESOLUCIONES ADMISORIAS INDECOPI CC1

> **AUTORIDAD:** Indecopi Comisión de Protección al Consumidor  1 (CC1)  
> **NORMA MARCO:** Decreto Supremo 006-2026-JUS  
> **PROTOCOLO VISUAL:** ESTRICTO CERO OCR. Inspección exclusiva mediante Google Lens / Visión Multimodal.  
> **REPOSITORIO:** https://github.com/zero-phoenix/SystemHope-ResAdmis

---

## 1. REGLAS NO NEGOCIABLES (AXIOMAS POPPERIANOS)
1. **PROHIBICIÓN ESTRICTA DE OCR:** Jamás transcribir denuncias con OCR clásico ni extractores que rompan coordenadas o inventen datos. Se analiza la imagen de la denuncia escaneada con Google Lens o modelos de visión directa.
2. **TUO LPAG ACTUALIZADO:** Siempre citar el **Decreto Supremo 006-2026-JUS**. Prohibida cualquier mención al D.S. 004-2019-JUS.
3. **PROHIBICIÓN DE 'INDUCCIÓN A ERROR':** Nunca imputar por el Artículo 3° ni emplear la frase 'inducción a error'. Todas las fallas de información se canalizan por los Artículos 1°, numeral 1, literal b) y 2° del Código de Protección y Defensa del Consumidor.
4. **TIEMPOS VERBALES OBLIGATORIOS:**
   - **En Antecedentes / Hechos:** Pasado indicativo afirmativo ("señaló", "contrató", "solicitó"). PROHIBIDO usar la palabra 'denunciante' en el cuerpo narrativo; usar el nombre de pila o 'el señor / la señora [Apellido]'.
   - **En Imputación de Cargos:** Condicional obligatorio ("habría denegado", "habría omitido", "habría realizado cobros").
5. **INVARIANTES LÉXICAS:**
   - Usar `cónyuge` / `cónyuges` (PROHIBIDO: esposo/a).
   - Usar `luego de` (PROHIBIDO: tras).
   - Usar `esta` / `este` sin tilde diacrítica.
   - Usar `médico` (PROHIBIDO: doctor/a o Dr.).
   - Usar `vehículo con Placa de Rodaje []` (PROHIBIDO: carro, auto).
6. **FORMATO MONETARIO MONOLÍTICO:**
   - `S/ X XXX,XX` o `US$ X XXX,XX` (espacio para miles, coma decimal, nunca punto ni apóstrofe).

---

## 2. LOS TRES PÁRRAFOS RESOLUTIVOS LITERALES DE NOTIFICACIÓN (SIN PARAFRASEAR)
En la sección resolutiva final de todo admisorio, se coloca indefectiblemente el párrafo correspondiente a la vía legal de notificación:

### TIPO 1: VÍA CASILLA ELECTRÓNICA (SINE INDECOPI - 5 DÍAS)
*Para compañías de seguros y bancos afiliados obligatoriamente:*
> *"requerir a [PROVEEDOR(ES)] para que efectúe[n] el acuse de recibo mediante la confirmación de recepción de la notificación remitida por este despacho a su[s] Casilla[s] Electrónica[s], dentro de los cinco (5) primeros días hábiles siguientes a la fecha en que recibe[n] la notificación."*

### TIPO 2: VÍA CORREO ELECTRÓNICO (AUTORIZACIÓN EXPRESA - 2 DÍAS)
*Para consumidores y proveedores con dirección electrónica autorizada:*
> *"requerir a [PARTE(S)] para que, dentro del plazo de dos (2) días hábiles siguientes a la fecha en que reciba[n] la notificación en su[s] bandeja[s] de correo electrónico, efectúe[n] la confirmación de recepción de la notificación remitida por este despacho a su[s] correo[s] electrónico[s], de conformidad con el segundo párrafo del numeral 4 del artículo 20° del Texto Único Ordenado de la Ley del Procedimiento Administrativo General, aprobado mediante Decreto Supremo 006-2026-JUS, bajo apercibimiento de rehacer el acto de notificación y notificarle[s] conforme al numeral 1 del artículo 20° del citado cuerpo normativo."*

### TIPO 3: VÍA DOMICILIO PROCESAL / CÉDULA FÍSICA (2 DÍAS)
*Para denunciantes sin correo, AFOCATs, fondos especiales (CAFAE) o proveedores sin casilla:*
> *"requerir a [PARTE(S)] para que, dentro del plazo de dos (2) días hábiles siguientes a la fecha en que reciba[n] la notificación en su domicilio procesal, efectúe[n] la confirmación de recepción de la notificación remitida por este despacho a su domicilio procesal, de conformidad con el segundo párrafo del numeral 4 del artículo 20° del Texto Único Ordenado de la Ley del Procedimiento Administrativo General, aprobado mediante Decreto Supremo 006-2026-JUS, bajo apercibimiento de rehacer el acto de notificación y notificarle[s] conforme al numeral 1 del artículo 20° del citado cuerpo normativo."*

---

## 3. DOMICILIOS PROCESALES Y VÍAS OFICIALES POR PROVEEDOR
- **Casilla Electrónica (SINE Indecopi):** Pacífico Compañía de Seguros, Mapfre Perú Compañía de Seguros, Interseguro Compañía de Seguros, La Positiva Seguros y Reaseguros, BNP Paribas Cardif, Chubb Perú, Quálitas Compañía de Seguros, Protecta Compañía de Seguros, Crecer Seguros, Banco BBVA Perú, Scotiabank Perú, Interbank, Empresa de Créditos Santander Consumo Perú, Banco Falabella, Banco Ripley, Banco Pichincha, Banco GNB.
- **Correo Electrónico Autorizado / Casilla:** Rímac Seguros y Reaseguros, Banco de Crédito del Perú (BCP).
- **Domicilio Procesal / Cédula Física:** AFOCATs provinciales/regionales, Comités de Administración CAFAE, talleres y personas naturales denunciadas.

---

## 4. TAXONOMÍA Y LOCALIZACIÓN DE PLANTILLAS
El repositorio contiene **605 plantillas Word (.docx) depuradas** en `plantillas_maestras/`:
- `01_seguro_vehicular` (174) | `02_seguro_vida` (134) | `03_seguro_desgravamen` (66)
- `04_seguro_proteccion_tarjetas_y_dinero` (37) | `05_soat_y_afocat` (43) | `06_seguro_hogar_e_inmuebles` (20)
- `07_seguro_sctr` (18) | `08_seguro_salud_eps_oncologico` (12) | `09_seguro_patrimonial_caucion_rc` (10)
- `10_seguro_sepelio` (8) | `11_seguro_accidentes_personales` (7) | `12_seguro_transporte_y_carga` (6)
- `13_seguro_multiple_y_equipos` (4) | `14_seguro_desempleo` (2) | `15_sistema_previsional_afp_onp` (2)
- `16_temas_administrativos_financieros` (4) | `17_seguro_no_especificado` (58)

---

## 5. PARÁMETROS DE ESTILO VISUAL CC1
- **Fuente:** `Arial Narrow` (11 pt cuerpo de texto, 8 pt notas al pie y encabezados).
- **Márgenes A4:** Superior 2.5 cm, Inferior 2.5 cm, Izquierdo 3.0 cm, Derecho 2.5 cm.
- **Interlineado:** Sencillo 1.0, espaciado `0 pt antes / 0 pt después`.
- **Sangrías Institucionales:**
  - Hechos: Izquierda `0.79"` (2.0 cm), Francesa `-0.39"` (-1.0 cm).
  - Resolutivo: Izquierda `0.39"` (1.0 cm), Francesa `-0.39"` (-1.0 cm).
- **Notas al Pie:** Formato con *One Dot Leader* (`\u2024`). Pie institucional: `M-CPC-01/03`.

---

## 6. FIRMA DIGITAL CONDICIONADA Y VERIFICACIÓN (R-103 A R-110)
- **Firma según Denunciado (R-103):**
  - **RÍMAC SEGUROS Y REASEGUROS S.A. (o RÍMAC):** NUNCA firma la titular. Firma obligatoriamente como Secretaria Técnica Ad Hoc: **LUISA ANALÍ SILVA MALPARTIDA**, cargo: `Secretaria Técnica Ad Hoc`, refrendo de calidad: `LSQ/DCQ`.
  - **Demás proveedores:** **EVELING ROA QUISPE**, cargo: `Secretaria Técnica`, refrendo según instructor asignado (ej. `RSV/DCQ`).
- **Isomorfismos Verbatim (R-97 / R-108):**
  - El núcleo fáctico de imputaciones es idéntico entre la considerativa (Sección II) y el resolutivo (`PRIMERO:`, etc.).
  - El requerimiento de información probatorio es idéntico palabra por palabra entre la considerativa (Sección III) y el resolutivo (`QUINTO:`).
- **Protocolo de Verificación Previa Obligatorio (R-109):**
  - Todo admisorio debe pasar: `python scripts/verificar_admisorio.py <admisorio.docx>` y obtener `APTO (0 falsadores)` antes de ser entregado.

