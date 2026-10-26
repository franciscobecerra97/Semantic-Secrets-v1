param([switch]$Execute)
. (Join-Path $PSScriptRoot '_common.ps1')
foreach ($auditScope in @('development', 'validation')) {
    $auditRun = Join-Path $auditRoot ('outputs\' + $auditScope + '-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
    $auditArguments = @((Join-Path $auditRoot '02_run_inference.py'), '--models', 'both', '--scope', $auditScope, '--run-dir', $auditRun)
    if ($Execute) { $auditArguments += '--execute' }
    Invoke-AuditPython -Arguments $auditArguments
    if ($Execute) { Invoke-AuditPython -Arguments @((Join-Path $auditRoot '03_validate_outputs.py'), '--run-dir', $auditRun) }
}
