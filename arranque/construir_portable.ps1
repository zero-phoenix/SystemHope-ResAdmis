# Construye dist/SystemHope-Portable-win64.zip (Python 3.12 embebido + dependencias
# sin OCR + MinGit + repositorio sin capturas) y lo PRUEBA con su propio Python.
# Lo usan ci.yml (prueba en cada PR) y generate_release.yml (publica).
#
# Uso: pwsh -File arranque/construir_portable.ps1 -Version v3.0.N
param([string]$Version = 'dev')

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$pv = '3.12.10'
Remove-Item -Recurse -Force portable -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force portable/python, portable/git, dist | Out-Null

Invoke-WebRequest "https://www.python.org/ftp/python/$pv/python-$pv-embed-amd64.zip" -OutFile py.zip
Expand-Archive py.zip portable/python -Force
$pth = Get-ChildItem portable/python -Filter 'python3*._pth' | Select-Object -First 1
Add-Content $pth.FullName 'Lib\site-packages'
Add-Content $pth.FullName 'import site'
python -m pip install --quiet --only-binary=:all: --platform win_amd64 --python-version 3.12 --implementation cp --target portable/python/Lib/site-packages -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'pip no pudo instalar las dependencias' }

$cab = @{}
if ($env:GH_TOKEN) { $cab.Authorization = "Bearer $env:GH_TOKEN" }
$rel = Invoke-RestMethod https://api.github.com/repos/git-for-windows/git/releases/latest -Headers $cab
$mg = $rel.assets | Where-Object { $_.name -match '^MinGit-[\d.]+-64-bit\.zip$' } | Select-Object -First 1
Invoke-WebRequest $mg.browser_download_url -OutFile mingit.zip
Expand-Archive mingit.zip portable/git -Force

git archive --format=zip -o repo.zip HEAD -- . ':!docs/capturas_referenciales'
Expand-Archive repo.zip portable/repo -Force
Set-Content portable/VERSION.txt $Version
Push-Location portable/repo
../python/python.exe scripts/integridad.py --generar
Pop-Location

Push-Location portable/repo
try {
    ../python/python.exe scripts/comprobar_entorno.py
    if ($LASTEXITCODE -ne 0) { throw 'el entorno portatil no quedo LISTO' }
    ../python/python.exe scripts/prueba_verificador.py
    if ($LASTEXITCODE -ne 0) { throw 'el verificador portatil no distingue' }
    ../git/cmd/git.exe --version
    if ($LASTEXITCODE -ne 0) { throw 'MinGit no arranca' }
} finally { Pop-Location }

Compress-Archive -Path portable/python, portable/git, portable/repo, portable/VERSION.txt -DestinationPath dist/SystemHope-Portable-win64.zip -Force
$h = (Get-FileHash dist/SystemHope-Portable-win64.zip -Algorithm SHA256).Hash.ToLower()
Set-Content dist/SHA256.txt "$h  SystemHope-Portable-win64.zip"
Set-Content dist/VERSION.txt $Version
$mb = [math]::Round((Get-Item dist/SystemHope-Portable-win64.zip).Length / 1MB, 1)
Write-Host "Paquete portatil $Version listo: $mb MB, sha256 $h"
