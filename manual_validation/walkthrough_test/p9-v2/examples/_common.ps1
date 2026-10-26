$ErrorActionPreference = 'Stop'
$auditRoot = Split-Path -Parent $PSScriptRoot
$projectRoot = Split-Path -Parent (Split-Path -Parent $auditRoot)
$auditPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $auditPython)) {
    throw "Project Python environment is missing: $auditPython"
}
function Invoke-AuditPython {
    param([Parameter(Mandatory)][string[]]$Arguments)
    & $auditPython @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Audit command failed with exit code $LASTEXITCODE" }
}
