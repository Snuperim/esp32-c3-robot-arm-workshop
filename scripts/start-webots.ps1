param(
    [ValidateSet("pause", "realtime", "fast")]
    [string]$Mode = "realtime"
)

$ErrorActionPreference = "Stop"

$webotsExecutable = "C:\Program Files\Webots\msys64\mingw64\bin\webots.exe"
$projectRoot = Split-Path -Parent $PSScriptRoot
$worldFile = Join-Path $projectRoot "webots\worlds\robot_arm.wbt"

if (-not (Test-Path -LiteralPath $webotsExecutable)) {
    throw "Webots was not found at: $webotsExecutable"
}

if (-not (Test-Path -LiteralPath $worldFile)) {
    throw "Robot arm world was not found at: $worldFile"
}

# Ignore a broken inherited value such as the literal "angle or software".
# This changes only this launcher process and the Webots process it starts.
Remove-Item Env:QT_OPENGL -ErrorAction SilentlyContinue

& $webotsExecutable "--mode=$Mode" $worldFile

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
