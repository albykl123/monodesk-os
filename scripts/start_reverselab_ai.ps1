<#
.SYNOPSIS
    Single-Click Entrypoint for REVERSELAB AI
.DESCRIPTION
    Invokes the AutoPilot storage discovery and startup engine.
#>

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AutopilotScript = Join-Path $ScriptDir "REVERSELAB-AUTOPILOT.ps1"

if (-not (Test-Path $AutopilotScript)) {
    # Check parent directory
    $AutopilotScript = Join-Path (Split-Path -Parent $ScriptDir) "scripts\REVERSELAB-AUTOPILOT.ps1"
}

if (Test-Path $AutopilotScript) {
    & $AutopilotScript @args
} else {
    Write-Error "Could not locate REVERSELAB-AUTOPILOT.ps1 engine."
    pause
}
