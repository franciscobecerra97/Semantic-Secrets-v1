param([Parameter(Mandatory)][string]$Snapshot, [switch]$Execute, [switch]$NoReasoning)
. (Join-Path $PSScriptRoot '_common.ps1')
$auditRun = Join-Path $auditRoot ('outputs\moondream3-local-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
$auditArguments = @((Join-Path $auditRoot '02_run_inference.py'), '--models', 'moondream3', '--transport', 'local', '--snapshot', $Snapshot, '--scope', 'one', '--run-dir', $auditRun)
if ($NoReasoning) { $auditArguments += '--no-reasoning' } else { $auditArguments += '--reasoning' }
if ($Execute) { $auditArguments += '--execute' }
Invoke-AuditPython -Arguments $auditArguments
if ($Execute) { Invoke-AuditPython -Arguments @((Join-Path $auditRoot '03_validate_outputs.py'), '--run-dir', $auditRun) }
