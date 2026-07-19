@echo off
REM Script para hacer push automático a GitHub
REM Versión 1.0.2 - Resoluciones desde modelos base INDECOPI

cd /d D:\BETTER CALL DAVID\ResAdmi

echo [1] Agregando cambios a git...
git add .

echo [2] Creando commit...
git commit -m "feat: generar resoluciones desde modelos base INDECOPI (v1.0.2)

- Usar modelos base en lugar de generar desde cero
- Preserva imagenes del encabezado y colores
- Script: generar_955_desde_modelo.py
- Validador: validar_docx.py
- Guia actualizada: GENERAR_RESOLUCIONES_WORD.md
- Tamanio correcto: 125+ KB con imagenes

Expediente 0955-2026/CC1:
- Denunciante: Eufemia Estefa Martinez Moreno de Romero
- Denunciado: Interseguro Compania de Seguros S.A.
- Resolucion: 1
- Fecha: Lima, 20 de abril de 2026

Validacion: ZIP OOXML con 25 archivos internos (imagenes incluidas)"

echo [3] Haciendo push a GitHub...
git push origin main

echo [4] Mostrando últimos commits...
git log --oneline -3

echo.
echo [OK] Push completado exitosamente
echo [GitHub] Cambios disponibles en: https://github.com/davidchaveznge-wq/ResAdmi

pause
