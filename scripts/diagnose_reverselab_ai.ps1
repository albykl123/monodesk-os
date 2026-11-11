<#
.SYNOPSIS
    REVERSELAB AI — Comprehensive System & Drive Diagnostics Doctor
#>

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  REVERSELAB AI — SYSTEM & STORAGE DIAGNOSTICS DOCTOR" -ForegroundColor White
Write-Host "================================================================================" -ForegroundColor Cyan

# 1. Host Hardware
Write-Host "`n[1] HOST HARDWARE DIAGNOSTICS:" -ForegroundColor Yellow
$cs = Get-CimInstance Win32_ComputerSystem
$proc = Get-CimInstance Win32_Processor
$gpu = Get-CimInstance Win32_VideoController | Select-Object -First 1

Write-Host "  Model:       $($cs.Manufacturer) $($cs.Model)"
Write-Host "  Processor:   $($proc.Name) ($($proc.NumberOfCores) Cores / $($proc.NumberOfLogicalProcessors) Threads)"
Write-Host "  Graphics:    $($gpu.Name) (Driver Version: $($gpu.DriverVersion))"
Write-Host "  Total RAM:   $([math]::Round($cs.TotalPhysicalMemory / 1GB, 1)) GB"

# 2. Storage Subsystem
Write-Host "`n[2] STORAGE SUBSYSTEM & CONNECTED DRIVES:" -ForegroundColor Yellow
$drives = [System.IO.DriveInfo]::GetDrives()
foreach ($d in $drives) {
    if ($d.IsReady) {
        $freeGB = [math]::Round($d.AvailableFreeSpace / 1GB, 1)
        $totalGB = [math]::Round($d.TotalSize / 1GB, 1)
        $usedPct = [math]::Round((($totalGB - $freeGB) / $totalGB) * 100, 1)
        Write-Host "  Drive $($d.Name) [$($d.VolumeLabel)] Type: $($d.DriveType) | Free: $freeGB GB / $totalGB GB ($usedPct% used)" -ForegroundColor Green
    } else {
        Write-Host "  Drive $($d.Name) [Not Ready / Disconnected]" -ForegroundColor DarkGray
    }
}

# 3. Environment Dependencies
Write-Host "`n[3] RUNTIME ENVIRONMENT & DEPENDENCIES:" -ForegroundColor Yellow
$py = Get-Command "python" -ErrorAction SilentlyContinue
if ($py) {
    $pyV = & $py.Source --version
    Write-Host "  Python:      $pyV ($($py.Source))" -ForegroundColor Green
} else {
    Write-Host "  Python:      NOT FOUND ON PATH" -ForegroundColor Red
}

$node = Get-Command "node" -ErrorAction SilentlyContinue
if ($node) {
    $nodeV = & $node.Source --version
    Write-Host "  Node.js:     $nodeV ($($node.Source))" -ForegroundColor Green
} else {
    Write-Host "  Node.js:     NOT FOUND ON PATH" -ForegroundColor Red
}

$npm = Get-Command "npm" -ErrorAction SilentlyContinue
if ($npm) {
    $npmV = & $npm.Source --version
    Write-Host "  npm:         $npmV ($($npm.Source))" -ForegroundColor Green
} else {
    Write-Host "  npm:         NOT FOUND ON PATH" -ForegroundColor Red
}

$git = Get-Command "git" -ErrorAction SilentlyContinue
if ($git) {
    $gitV = & $git.Source --version
    Write-Host "  Git:         $gitV ($($git.Source))" -ForegroundColor Green
} else {
    Write-Host "  Git:         NOT FOUND ON PATH" -ForegroundColor Red
}

# 4. Port Status
Write-Host "`n[4] WORKSTATION PORT STATUS:" -ForegroundColor Yellow
$p8000 = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
$p5173 = Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue

if ($p8000) {
    Write-Host "  Port 8000 (Backend):  OCCUPIED by PID $($p8000.OwningProcess)" -ForegroundColor Green
} else {
    Write-Host "  Port 8000 (Backend):  Available (Offline)" -ForegroundColor DarkGray
}

if ($p5173) {
    Write-Host "  Port 5173 (Frontend): OCCUPIED by PID $($p5173.OwningProcess)" -ForegroundColor Green
} else {
    Write-Host "  Port 5173 (Frontend): Available (Offline)" -ForegroundColor DarkGray
}

# 5. Project Location Search
Write-Host "`n[5] PROJECT LOCATION SCAN:" -ForegroundColor Yellow
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Autopilot = Join-Path $ScriptDir "REVERSELAB-AUTOPILOT.ps1"
if (Test-Path $Autopilot) {
    & $Autopilot -DiagnosticOnly
}
Write-Host "`nDiagnostics Complete." -ForegroundColor Cyan
