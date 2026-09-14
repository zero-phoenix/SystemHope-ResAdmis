# Claude Code Instructions - SystemHope ResAdmis CC1

Este repositorio contiene el sistema automatizado de resoluciones admisorias de Indecopi CC1.

## Comandos Principales
- Ver catálogo y estado: `python -m src.systemhope_engine info`
- Buscar plantillas: `python -m src.systemhope_engine templates --rama 03_seguro_desgravamen --materia negativa_cobertura`
- Consultar vías de notificación: `python -m src.systemhope_engine notifications`
- Auditar documento: `python -m src.systemhope_engine validate <archivo.docx>`
- Exportar memoria completa a IDE: `python -m src.systemhope_engine dump-memory`

## Reglas Críticas
- **Cero OCR:** Siempre analizar capturas con Google Lens / Vision.
- **LPAG 2026:** D.S. N° 006-2026-JUS.
- **Cero Inducción a Error:** Arts. 1.1.b y 2 de Ley 29571.
- **Notificaciones Finales:** 3 fórmulas literales estrictas (Casilla 5 días, Correo 2 días con apercibimiento, Domicilio Procesal 2 días con apercibimiento).
- **Formato:** Arial Narrow 11 pt, notas 8 pt, sangrías CC1, pie institucional M-CPC-01/03.
