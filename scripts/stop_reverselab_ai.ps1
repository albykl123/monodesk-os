<#
.SYNOPSIS
    Gracefully Stops Running REVERSELAB AI Workstation Services
#>

Write-Host "Stopping REVERSELAB AI backend (port 8000) and frontend (port 5173)..." -ForegroundColor Yellow

$ports = @(8000, 5173)
$stopped = 0

foreach ($p in $ports) {
    $conns = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue
    foreach ($c in $conns) {
        $pidToKill = $c.OwningProcess
        try {
            $proc = Get-Process -Id $pidToKill -ErrorAction SilentlyContinue
            if ($proc -and ($proc.ProcessName -match "python|node|uvicorn|cmd")) {
                Write-Host "  Stopping $($proc.ProcessName) (PID: $pidToKill) on port $p..." -ForegroundColor Cyan
                Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
                $stopped++
            }
        } catch {}
    }
}

if ($stopped -gt 0) {
    Write-Host "Successfully stopped $stopped REVERSELAB AI service processes." -ForegroundColor Green
} else {
    Write-Host "No active REVERSELAB AI processes were found running on ports 8000 or 5173." -ForegroundColor DarkGray
}
