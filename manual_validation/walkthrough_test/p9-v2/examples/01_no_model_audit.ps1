# Inspect, reparse historical answers, and exercise the scorer. No model inference.
. (Join-Path $PSScriptRoot '_common.ps1')
Invoke-AuditPython -Arguments @((Join-Path $auditRoot '00_walkthrough.py'))
Invoke-AuditPython -Arguments @((Join-Path $auditRoot '01_inspect_dataset.py'), '--gallery', '--recreate')
Invoke-AuditPython -Arguments @((Join-Path $auditRoot '04_replay_history.py'))
Invoke-AuditPython -Arguments @((Join-Path $auditRoot '05_teaching_examples.py'))
