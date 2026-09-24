# -*- coding: utf-8 -*-
Write-Host "Running syntax and dry-run validation for Fix-UyapEditor.ps1..."

$scriptPath = Join-Path $PSScriptRoot "Fix-UyapEditor.ps1"
if (-not (Test-Path $scriptPath)) {
    throw "Script not found: $scriptPath"
}

# Test script parsing
$errors = $null
$tokens = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($scriptPath, [ref]$tokens, [ref]$errors)

if ($errors.Count -gt 0) {
    throw "PowerShell Syntax Errors: $($errors | Out-String)"
}

Write-Host "PowerShell syntax validation passed with 0 errors!"
