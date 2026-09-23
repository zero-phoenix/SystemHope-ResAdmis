# ARRANQUE — Admisorios CC1 desde cualquier computadora

Eres Google Antigravity y vas a redactar una **resolución de admisión a trámite e imputación
de cargos** de la Comisión de Protección al Consumidor 1 de Indecopi (seguros).
Sigue estos pasos **en orden**, sin saltarte ninguno. Todo corre en PowerShell de Windows,
sin permisos de administrador.

## 0. Modelo
Esta tarea exige **Gemini 3.8 Flash High o un modelo Gemini superior**. Si la conversación usa
otro modelo, dilo al usuario antes de seguir.

## 1. Instalar o actualizar el sistema (una sola llamada)
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/zero-phoenix/SystemHope-ResAdmis/main/arranque/instalar.ps1 | iex"
```
- Deja todo en `%USERPROFILE%\SystemHope\`: `python\` (Python portátil, sin OCR), `git\`,
  `repo\` (reglas, scripts y plantillas) y `casos\`.
- Termina con `LISTO`. Si dice `NO LISTO`, informa al usuario de lo que falta y para.
- Si la red bloquea GitHub, pide al usuario que descargue
  `https://github.com/zero-phoenix/SystemHope-ResAdmis/releases/latest/download/SystemHope-Portable-win64.zip`,
  lo descomprima en `%USERPROFILE%\SystemHope\` y te avise. Después vuelve a ejecutar el paso 1.

Desde aquí, **todo comando** se ejecuta así (define las variables una vez por llamada):
```powershell
$SH="$env:USERPROFILE\SystemHope"; Set-Location "$SH\repo"; & "$SH\python\python.exe" scripts\<script>.py <argumentos>
```

## 2. Leer las reglas (obligatorio, antes de redactar)
Lee **completos**:
1. `%USERPROFILE%\SystemHope\repo\AGENTS.md`: las reglas vigentes. Mandan sobre todo lo demás.
2. El `SKILL.md` de cada carpeta de `%USERPROFILE%\SystemHope\repo\.agents\skills\` que aplique al caso:
   - `admisorio-flujo`: siempre.
   - `imputaciones`: siempre.
   - `partes-y-notificacion`: siempre.
   - `confidencialidad`: solo si el caso la tiene.

No uses reglas de memoria ni de otros proyectos. Si algo no está en estos archivos, **pregunta**.

## 3. Fecha de la remesa
Si el paso 1 mostró `Remesa: SIN FECHA`, **pregunta al usuario la fecha de emisión** y fíjala:
`scripts\config_sistema.py --fecha "25 de setiembre de 2026"`.

## 4. El expediente
1. Crea `%USERPROFILE%\SystemHope\casos\<EXPEDIENTE>\`, por ejemplo `casos\3122-2026\`.
2. Copia allí **todos** los PDF que el usuario adjuntó: denuncia, escritos complementarios o de subsanación, resoluciones previas, programación de audiencia de conciliación, documento de traslado o memorándum, cargo de recepción en CC1 y cédulas.
3. Si no encuentras en disco la ruta de los adjuntos, pide al usuario la carpeta donde están.
4. **Nunca** copies expedientes dentro de `repo\`.

## 5. Redactar con el flujo del repositorio
Sigue el flujo de `AGENTS.md` §1:
1. `admisorio.py preparar <carpeta>`: filtra con `--denunciados`, `--sujeto` y `--subtipo` según el caso.
2. Lectura visual de **cada** captura de `_paginas\`: llena `_LECTURA.md` con lo que ves, **nunca** con el texto seleccionable.
3. `construir_admisorio.py --mapa <mapa.json>`: el mapa va en la carpeta del caso.
4. `admisorio.py entregar "<carpeta>\ADM <EXP> R<N>.docx" --recepcion DD/MM/AAAA`.

Solo está entregado si la salida dice **ENTREGABLE** y el verificador **APTO**. Pega esa salida
literal y la ruta del `.docx`.

## 6. Documento corregido por el usuario
Si el usuario te dice **expresamente** que un admisorio ya está corregido y te da su ruta:
1. Compáralo con tu versión: `inspeccionar_docx.py "<tu versión>" --diff "<corregido>"`.
2. Resume, sección por sección, qué cambió y qué regla lo explica.
3. **No** lo subas a ningún sitio ni lo mezcles con el repositorio: su incorporación como plantilla la hace el instructor con el procedimiento del repositorio.

## Prohibido
- OCR en cualquier forma.
- Generar PDF.
- Abrir Word por COM.
- Inventar datos que no ves en una página.
- Imputar fuera de la tabla del instructor.
- Commitear o publicar expedientes.
