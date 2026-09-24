# ÍNDICE TAXONÓMICO MAESTRO DE PLANTILLAS WORD (INDECOPI CC1)

> **Documento de consulta.** Si contradice a `AGENTS.md`, manda `AGENTS.md` (reglas vigentes v3.1, 24/09/2026).


> **ESTADO:** CATÁLOGO DE PRODUCCIÓN PARA GENERACIÓN AUTOMÁTICA  
> **TOTAL DE PLANTILLAS DEPURADAS:** 578 archivos `.docx` (23/09/2026: fuera 13 duplicados exactos y 2 documentos que no eran admisorios). El conteo vivo está en `docs/plantillas_maestras_index.json`; los subtotales de abajo son históricos.  
> **NORMATIVA LPAG APLICADA:** Decreto Supremo 006-2026-JUS (Vigente al 13 de setiembre de 2026)  
> **DEPURACIÓN ORTOGRÁFICA:** Sanitización completa de mojibake y reglas léxicas popperianas aplicadas.

---

## 1. Distribución por Ramas de Seguro

| Código y Rama | Cantidad | % Total |
| :--- | :--- | :--- |
| `01_seguro_vehicular` | **174** | 28.8% |
| `02_seguro_vida` | **134** | 22.1% |
| `03_seguro_desgravamen` | **66** | 10.9% |
| `04_seguro_proteccion_tarjetas_y_dinero` | **37** | 6.1% |
| `05_soat_y_afocat` | **43** | 7.1% |
| `06_seguro_hogar_e_inmuebles` | **20** | 3.3% |
| `07_seguro_sctr` | **18** | 3.0% |
| `08_seguro_salud_eps_oncologico` | **12** | 2.0% |
| `09_seguro_patrimonial_caucion_rc` | **10** | 1.7% |
| `10_seguro_sepelio` | **8** | 1.3% |
| `11_seguro_accidentes_personales` | **7** | 1.2% |
| `12_seguro_transporte_y_carga` | **6** | 1.0% |
| `13_seguro_multiple_y_equipos` | **4** | 0.7% |
| `14_seguro_desempleo` | **2** | 0.3% |
| `15_sistema_previsional_afp_onp` | **2** | 0.3% |
| `16_temas_administrativos_financieros` | **4** | 0.7% |
| `17_seguro_no_especificado` | **58** | 9.6% |

---

## 2. Distribución por Materia / Servicio Denunciado

| Materia Denunciada | Cantidad |
| :--- | :--- |
| `negativa_cobertura` | **282** |
| `materia_general_asegurativa` | **157** |
| `anulacion_indebida` | **33** |
| `falta_atencion_o_demora_reclamo` | **28** |
| `liquidacion_o_pago_menor` | **26** |
| `falta_renovacion_poliza` | **15** |
| `cobro_indebido_primas` | **14** |
| `falta_evaluacion_invalidez` | **11** |
| `contratacion_no_consentida` | **10** |
| `discriminacion` | **9** |
| `clausula_abusiva` | **8** |
| `modificacion_unilateral` | **6** |
| `falta_entrega_poliza` | **5** |
| `deficiente_gestion_siniestro` | **1** |

---

## 3. Distribución por Configuración de Proveedores

| Tipo de Proveedor | Cantidad |
| :--- | :--- |
| `2_o_mas_ddos_varios` | **420** |
| `1_ddo_aseguradora` | **93** |
| `2_ddos_banco_y_aseguradora` | **61** |
| `1_ddo_banco_o_financiera` | **30** |
| `1_ddo_corredor` | **1** |

---

## 4. Distribución por Sujeto Denunciante

| Sujeto Denunciante | Cantidad |
| :--- | :--- |
| `varon` | **348** |
| `mujer` | **217** |
| `sucesion_intestada` | **35** |
| `varios` | **5** |

---

## 5. Guía de Selección Rápida de Plantillas para Admisorios

Para generar una nueva resolución admisoria a partir de una denuncia escaneada con Visión Multimodal:

1. **Identificar la rama de seguro:** Desgravamen (`03`), Tarjetas (`04`), Vehicular (`01`), Vida (`02`), etc.
2. **Identificar la materia principal:** Negativa de cobertura (`negativa_cobertura`), anulación indebida (`anulacion_indebida`), falta de póliza (`falta_entrega_poliza`), etc.
3. **Identificar proveedores denunciados:** Si solo denuncia a la aseguradora (`1_ddo_aseguradora`), o banco y aseguradora (`2_ddos_banco_y_aseguradora`).
4. **Identificar sujeto:** Varón (`varon`), mujer (`mujer`), o sucesión intestada (`sucesion_intestada`).
5. **Cargar la plantilla `.docx` correspondiente de `plantillas_maestras/`**, la cual ya cuenta con:

   - Citas al **Decreto Supremo 006-2026-JUS**.
   - Cero imputaciones a inducción a error.
   - Formato institucional de página, fuentes Arial Narrow, sangrías escalonadas y notas al pie con One Dot Leader.
