# Resumen ejecutivo — SystemHope ResAdmis v3 (23/09/2026)

**Qué es:** el sistema con el que Google Antigravity (Gemini 3.8 Flash High o superior) redacta las resoluciones de admisión a trámite e imputación de cargos de la CC1 de Indecopi (seguros), y el verificador que decide si una resolución es entregable.

**Parte 1 del plan v3 (aplicada):**
- **Fórmula de traslado R-155 corregida** según la ley en todo el corpus: «aprobada por Decreto Legislativo 807», «merituadas», sin «N°» ni volada. Antes, el verificador exigía el error.
- **Singular y plural por el número real de denunciados**: 388 plantillas tenían el número equivocado (369 de un solo denunciado en plural) y 5 tenían el destinatario del traslado corrompido.
- **Imputación cerrada**: solo por la tabla de tipificación del instructor (`docs/tabla_tipificacion.json`). Nunca el art. 3; el art. 24 solo ante un proveedor no regulado.
- **Firma vigente en todas las plantillas** (427 bloques normalizados). La fecha de emisión, la firma y el modelo se leen de `config/`.
- **Nuevas reglas con falsador**: números de normas sin «N°» (R-156), sin «denunciante» en los hechos (R-157), enmascarado (R-158), nota al pie del traslado a CC1 (R-159) y fecha de la remesa (R-160). El plazo de 20 días hábiles se calcula con `scripts/plazos.py`.
- **Lectura visual verificable**: `preparar` captura cada página completa y prepara `_LECTURA.md`; `entregar` rechaza filas vacías o copiadas del texto embebido.
- **Limpieza**: 578 plantillas (fuera 13 duplicados y 2 documentos que no eran admisorios). AGENTS.md cabe en el límite de Antigravity. El código muerto pasó a la rama `archivo-legado`.

**Pendiente:**
- **Parte 2** (esfuerzo medio): clasificación por contenido, medición de formato y uso desde cualquier PC con Python y Git portátiles.
- **Parte 3** (esfuerzo alto): anonimización y purga del historial, modelos canónicos de 1 y de 2 o más denunciados, HECHOS e imputaciones, y supervisión A/B de Antigravity.
