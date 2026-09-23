# SystemHope ResAdmis - instalador portatil (Windows, sin administrador).
#
# Deja en %USERPROFILE%\SystemHope\ :
#   python\  Python embebido con sus dependencias (sin OCR)
#   git\     MinGit portatil
#   repo\    el repositorio (reglas, scripts, plantillas)
#   casos\   las carpetas de los expedientes (nunca se tocan al actualizar)
#
# Si ya esta instalado, solo actualiza cuando hay una version nueva, y conserva
# repo\config\remesa.json (fecha de la remesa en curso).
#
# Uso (lo ejecuta Antigravity; tambien a mano):
#   powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/zero-phoenix/SystemHope-ResAdmis/main/arranque/instalar.ps1 | iex"

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}

$Base    = Join-Path $env:USERPROFILE 'SystemHope'
$Release = 'https://github.com/zero-phoenix/SystemHope-ResAdmis/releases/latest/download'
$Zip     = 'SystemHope-Portable-win64.zip'
New-Item -ItemType Directory -Force -Path $Base, (Join-Path $Base 'casos') | Out-Null

function Leer-Texto($url) { (Invoke-WebRequest -Uri $url -UseBasicParsing).Content.ToString().Trim() }

$remota = $null
try { $remota = Leer-Texto "$Release/VERSION.txt" } catch {
    Write-Host "SIN RED hacia GitHub: $($_.Exception.Message)"
}
$verLocal = Join-Path $Base 'VERSION.txt'
$local = if (Test-Path $verLocal) { (Get-Content $verLocal -Raw).Trim() } else { $null }

# --- Diagnostico previo (mandato del instructor, 23/09/2026) -----------------
# Antes de hacer nada, el agente sabe si en ESTA computadora ya se elaboraron
# admisorios, si el sistema esta instalado y si su version esta al dia frente a
# la publicada en GitHub.
$casos = @(Get-ChildItem (Join-Path $Base 'casos') -Directory -ErrorAction SilentlyContinue)
$conAdm = @($casos | Where-Object { Get-ChildItem $_.FullName -Filter 'ADM *.docx' -ErrorAction SilentlyContinue })
$ultimo = $conAdm | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$pyPrevio = Join-Path $Base 'python\python.exe'
$integ = 'no aplica'
if ($local -and (Test-Path $pyPrevio)) {
    Push-Location (Join-Path $Base 'repo')
    $salidaInteg = & $pyPrevio 'scripts\integridad.py' 2>&1 | Out-String
    $integ = if ($LASTEXITCODE -eq 0) { 'OK' } else { 'MODIFICADO (se reinstala)' }
    Pop-Location
}
Write-Host '=== DIAGNOSTICO PREVIO ==='
Write-Host ("Instalacion previa en esta PC : {0}" -f $(if ($local) { "si ($Base)" } else { 'no (primera vez)' }))
Write-Host ("Version local / GitHub        : {0} / {1}" -f $(if ($local) { $local } else { '-' }), $(if ($remota) { $remota } else { 'sin red' }))
Write-Host ("Estado                        : {0}" -f $(if (-not $remota) { 'no se pudo comparar (sin red)' } elseif ($remota -eq $local) { 'AL DIA' } elseif ($local) { 'DESACTUALIZADA: se actualiza ahora' } else { 'se instala ahora' }))
Write-Host ("Integridad del sistema local  : {0}" -f $integ)
Write-Host ("Admisorios previos en la PC   : {0} caso(s){1}" -f $conAdm.Count, $(if ($ultimo) { " - ultimo: $($ultimo.Name) ($($ultimo.LastWriteTime.ToString('dd/MM/yyyy HH:mm')))" } else { '' }))
Write-Host '=========================='
if ($integ -like 'MODIFICADO*') { $local = 'modificado' }

if ($remota -and $remota -ne $local) {
    Write-Host "Instalando SystemHope $remota (antes: $(if ($local) { $local } else { 'nada' }))..."
    $tmp = Join-Path $env:TEMP ("shp_" + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Force -Path $tmp | Out-Null
    $zipLocal = Join-Path $tmp $Zip
    Invoke-WebRequest -Uri "$Release/$Zip" -OutFile $zipLocal -UseBasicParsing
    $esperado = (Leer-Texto "$Release/SHA256.txt").Split(' ')[0].ToLower()
    $real = (Get-FileHash $zipLocal -Algorithm SHA256).Hash.ToLower()
    if ($esperado -ne $real) { throw "SHA256 no coincide: el paquete no es el publicado. No se instala." }
    $remesa = Join-Path $Base 'repo\config\remesa.json'
    $remesaGuardada = if (Test-Path $remesa) { Get-Content $remesa -Raw } else { $null }
    Expand-Archive -Path $zipLocal -DestinationPath (Join-Path $tmp 'x') -Force
    foreach ($d in 'python', 'git', 'repo') {
        $destino = Join-Path $Base $d
        if (Test-Path $destino) { Remove-Item -Recurse -Force $destino }
        Move-Item (Join-Path $tmp "x\$d") $destino
    }
    if ($remesaGuardada) { Set-Content -Path $remesa -Value $remesaGuardada -Encoding UTF8 }
    Set-Content -Path $verLocal -Value $remota -Encoding ASCII
    Remove-Item -Recurse -Force $tmp
} elseif (-not $local) {
    throw "No hay instalacion previa y no se pudo descargar. Descarga a mano $Release/$Zip, descomprimelo en $Base y vuelve a ejecutar."
} else {
    Write-Host "SystemHope $local ya esta al dia."
}

$py = Join-Path $Base 'python\python.exe'
Set-Location (Join-Path $Base 'repo')
& $py 'scripts\comprobar_entorno.py'
Write-Host ""
Write-Host "PYTHON = $py"
Write-Host "REPO   = $(Join-Path $Base 'repo')"
Write-Host "CASOS  = $(Join-Path $Base 'casos')"
