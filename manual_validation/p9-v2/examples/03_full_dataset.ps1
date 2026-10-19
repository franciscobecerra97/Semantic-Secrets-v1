param([switch]$Execute, [switch]$RepeatValidation)
. (Join-Path $PSScriptRoot '_common.ps1')
$auditRun = Join-Path $auditRoot ('outputs\all-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
$auditArguments = @((Join-Path $auditRoot '02_run_inference.py'), '--models', 'both', '--scope', 'all', '--run-dir', $auditRun)
if ($RepeatValidation) { $auditArguments += '--repeat-validation' }
if ($Execute) { $auditArguments += '--execute' }
Invoke-AuditPython -Arguments $auditArguments
if ($Execute) {
    foreach ($auditScope in @('all', 'development', 'validation')) {
        Invoke-AuditPython -Arguments @((Join-Path $auditRoot '03_validate_outputs.py'), '--run-dir', $auditRun, '--scope', $auditScope)
    }
}
