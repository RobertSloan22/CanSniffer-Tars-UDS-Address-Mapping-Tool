#Requires -Version 5.1
<#
Creates .venv in repo root and installs requirements.txt.
Requires Python on PATH as `python`, or Windows `py` launcher.
#>

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

Set-Location $RepoRoot

function Find-Python {
    foreach ($exe in @('python', 'python3')) {
        $c = Get-Command $exe -ErrorAction SilentlyContinue
        if ($c) { return $c.Source }
    }
    foreach ($launcher in @('py', 'py.exe')) {
        $c = Get-Command $launcher -ErrorAction SilentlyContinue
        if ($c) {
            Write-Host 'Using launcher: py -3 ...'
            return 'py_launcher'
        }
    }
    return $null
}

$venv = Join-Path $RepoRoot '.venv'

$Py = Find-Python
if (-not $Py) {
    Write-Error @'
Python not found. Install Python 3.11+ from https://www.python.org/downloads/windows/
(or App Store/Microsoft Store build) with "Add to PATH".
See docs/PYTHON_OPTIONAL_WINDOWS.md
'@
}

$pip = Join-Path $venv 'Scripts\pip.exe'
$venvPython = Join-Path $venv 'Scripts\python.exe'

# Treat a venv as valid only if pip.exe exists; an interrupted `python -m venv`
# can leave python.exe behind without pip, and the bare-directory check would
# then incorrectly skip recreation on subsequent runs.
if ((Test-Path $venv) -and -not (Test-Path $pip)) {
    Write-Host "Removing incomplete venv at $venv (missing pip.exe)"
    Remove-Item -Recurse -Force $venv
}

if (-not (Test-Path $venv)) {
    if ($Py -eq 'py_launcher') {
        py -3 -m venv $venv
        if (-not $?) { py -m venv $venv }
    } else {
        & $Py -m venv $venv
    }
}

if (-not (Test-Path $pip)) {
    # venv ships with ensurepip; bootstrap pip manually if it's still missing.
    Write-Host "pip.exe still missing; running ensurepip"
    & $venvPython -m ensurepip --upgrade
}

if (-not (Test-Path $pip)) {
    Write-Error "Failed to install pip into $venv. Delete .venv\ and rerun this script."
}

$requirements = Join-Path $RepoRoot 'requirements.txt'

& $pip install --upgrade pip
& $pip install -r $requirements

Write-Host "Done. Activate: .\\.venv\\Scripts\\Activate.ps1"
