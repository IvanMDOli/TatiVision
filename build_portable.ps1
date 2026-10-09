param(
    [string]$OutputDirectory,
    [switch]$RequireFreshOutput
)

$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
$pythonExe = Join-Path $projectRoot "venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = (Get-Command python -ErrorAction Stop).Source
}

$mainFile = Join-Path $projectRoot "main.py"
$stageRoot = Join-Path $projectRoot "build\portable-stage"
$stageApp = Join-Path $stageRoot "TatiVision"
$workPath = Join-Path $projectRoot "build\pyinstaller-work"
$specPath = Join-Path $projectRoot "build\spec"
if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $portableRoot = Join-Path $projectRoot "dist\TatiVision"
} elseif ([System.IO.Path]::IsPathRooted($OutputDirectory)) {
    $portableRoot = $OutputDirectory
} else {
    $portableRoot = Join-Path $projectRoot $OutputDirectory
}
$executableIconFile = Join-Path $projectRoot "assets\icons\executable.ico"
$assetsDirectory = Join-Path $projectRoot "assets"

if ($RequireFreshOutput -and (Test-Path -LiteralPath $portableRoot)) {
    throw "La carpeta de salida ya existe y no se modificará: $portableRoot"
}

if (Test-Path -LiteralPath $stageApp) {
    Remove-Item -LiteralPath $stageApp -Recurse -Force
}

$pyinstallerArguments = @(
    "--noconfirm",
    "--clean",
    "--windowed",
    "--onedir",
    "--name", "TatiVision",
    "--paths", $projectRoot,
    "--distpath", $stageRoot,
    "--workpath", $workPath,
    "--specpath", $specPath
)
if (Test-Path -LiteralPath $executableIconFile) {
    $pyinstallerArguments += @("--icon", $executableIconFile)
}
if (Test-Path -LiteralPath $assetsDirectory) {
    $pyinstallerArguments += @(
        "--add-data",
        "$assetsDirectory;assets"
    )
}

& $pythonExe -m PyInstaller @pyinstallerArguments $mainFile

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller terminó con código $LASTEXITCODE."
}

if (-not (Test-Path $stageApp)) {
    throw "No se encontró el resultado de PyInstaller en $stageApp."
}

New-Item -ItemType Directory -Path $portableRoot -Force | Out-Null
$internalDirectory = Join-Path $portableRoot "_internal"
$executable = Join-Path $portableRoot "TatiVision.exe"
if (Test-Path $internalDirectory) {
    Remove-Item -LiteralPath $internalDirectory -Recurse -Force
}
if (Test-Path $executable) {
    Remove-Item -LiteralPath $executable -Force
}
Copy-Item -Path (Join-Path $stageApp "*") -Destination $portableRoot -Recurse -Force

Write-Host "Portable build ready: $portableRoot"
if (-not $RequireFreshOutput) {
    Write-Host "Existing user settings, catalog, and poster cache in dist were preserved."
}
