param([switch]$Execute, [string]$ImageId = 'cap-v2-064')
. (Join-Path $PSScriptRoot '_common.ps1')
$auditRun = Join-Path $auditRoot ('outputs\one-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
$auditArguments = @((Join-Path $auditRoot '02_run_inference.py'), '--models', 'both', '--scope', 'one', '--image-id', $ImageId, '--run-dir', $auditRun)
if ($Execute) { $auditArguments += '--execute' }
Invoke-AuditPython -Arguments $auditArguments
if ($Execute) { Invoke-AuditPython -Arguments @((Join-Path $auditRoot '03_validate_outputs.py'), '--run-dir', $auditRun) }
