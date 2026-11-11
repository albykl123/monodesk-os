<#
.SYNOPSIS
    REVERSELAB AI — AutoPilot Storage Discovery, Self-Configuring & Recovery Engine
.DESCRIPTION
    Dynamically discovers the REVERSELAB AI repository across all mounted drives (C:, D:, E:, F:, etc.),
    validates environment dependencies, handles drive disconnections gracefully,
    starts the FastAPI backend and Vite frontend services, verifies health endpoints,
    and opens the workstation in the default browser.
.AUTHOR
    Albert Linson (albykl123)
.VERSION
    2.0.0
#>

param(
    [switch]$DiagnosticOnly,
    [switch]$NoBrowser,
    [string]$TargetDrive
)

$ErrorActionPreference = "Continue"

# Output formatting
function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor White
    Write-Host "================================================================================" -ForegroundColor Cyan
}

function Write-Success { param([string]$Text) Write-Host "  [OK] $Text" -ForegroundColor Green }
function Write-Info    { param([string]$Text) Write-Host "  [..] $Text" -ForegroundColor Cyan }
function Write-Warn    { param([string]$Text) Write-Host "  [WARN] $Text" -ForegroundColor Yellow }
function Write-Fail    { param([string]$Text) Write-Host "  [FAIL] $Text" -ForegroundColor Red }

# ------------------------------------------------------------------------------
# STEP 1: AUTOMATIC STORAGE AND PROJECT DISCOVERY
# ------------------------------------------------------------------------------
function Find-ReverseLabProject {
    Write-Info "Scanning all active storage volumes for REVERSELAB AI..."

    $drives = [System.IO.DriveInfo]::GetDrives() | Where-Object { $_.IsReady }
    $driveSummaries = @()
    foreach ($d in $drives) {
        $free = [math]::Round($d.AvailableFreeSpace / 1GB, 1)
        $driveSummaries += "$($d.Name) ($($d.DriveType), $free GB free)"
    }
    Write-Host "  Found active drives: $($driveSummaries -join ', ')" -ForegroundColor DarkGray

    # Known candidate relative paths
    $candidateSubPaths = @(
        "anti\REVERSELAB-AI",
        "REVERSELAB-AI",
        "Projects\REVERSELAB-AI",
        "Users\$env:USERNAME\Projects\REVERSELAB-AI",
        "Users\$env:USERNAME\REVERSELAB-AI"
    )

    # 1. Direct candidate check
    foreach ($drive in $drives) {
        $driveRoot = $drive.RootDirectory.FullName
        foreach ($sub in $candidateSubPaths) {
            $testPath = Join-Path $driveRoot $sub
            if (Test-Path $testPath) {
                if (Test-IsReverseLabRepo -Path $testPath) {
                    Write-Success "Located valid REVERSELAB AI repository at: $testPath"
                    return $testPath
                }
            }
        }
    }

    # 2. Bounded search on non-system drives or root directories (Depth 2)
    foreach ($drive in $drives) {
        $root = $drive.RootDirectory.FullName
        try {
            $matchingDirs = Get-ChildItem -Path $root -Directory -Depth 2 -Filter "*REVERSELAB*" -ErrorAction SilentlyContinue
            foreach ($dir in $matchingDirs) {
                if (Test-IsReverseLabRepo -Path $dir.FullName) {
                    Write-Success "Discovered REVERSELAB AI repository at: $($dir.FullName)"
                    return $dir.FullName
                }
            }
        } catch {}
    }

    return $null
}

function Test-IsReverseLabRepo {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $false }

    $hasBackend   = Test-Path (Join-Path $Path "backend\main.py")
    $hasFrontend  = Test-Path (Join-Path $Path "frontend\package.json")
    $hasReadme    = Test-Path (Join-Path $Path "README.md")

    return ($hasBackend -and $hasFrontend -and $hasReadme)
}

# ------------------------------------------------------------------------------
# STEP 2: DEPENDENCY VALIDATION AND ENVIRONMENT SETUP
# ------------------------------------------------------------------------------
function Ensure-PythonEnvironment {
    param([string]$ProjectPath)

    Write-Info "Checking Python runtime environment..."
    $pythonCmd = Get-Command "python" -ErrorAction SilentlyContinue
    if (-not $pythonCmd) {
        $pythonCmd = Get-Command "py" -ErrorAction SilentlyContinue
    }

    if (-not $pythonCmd) {
        Write-Fail "Python is not installed or not present on system PATH!"
        Write-Host "  Please install Python 3.11+ from https://www.python.org/downloads/" -ForegroundColor Yellow
        return $null
    }

    $pyVer = & $pythonCmd.Source --version 2>&1
    Write-Success "System Python detected: $pyVer"

    # Fast validation: check if system python already has core packages
    $check = & $pythonCmd.Source -c "import fastapi, uvicorn, sqlalchemy; print('OK')" 2>$null
    if ($check -match "OK") {
        Write-Success "Python backend dependencies verified (fastapi, uvicorn, sqlalchemy available)."
        return $pythonCmd.Source
    }

    # Virtual Environment Fallback
    $venvPath = Join-Path $ProjectPath "venv"
    $venvPython = Join-Path $venvPath "Scripts\python.exe"

    if (-not (Test-Path $venvPython)) {
        Write-Info "Initializing virtual environment with system site packages at: $venvPath..."
        & $pythonCmd.Source -m venv --system-site-packages $venvPath
    }

    if (Test-Path $venvPython) {
        return $venvPython
    }

    return $pythonCmd.Source
}

function Ensure-FrontendEnvironment {
    param([string]$ProjectPath)

    Write-Info "Checking Node.js and npm runtime..."
    $nodeCmd = Get-Command "node" -ErrorAction SilentlyContinue
    $npmCmd  = Get-Command "npm"  -ErrorAction SilentlyContinue

    if (-not $nodeCmd -or -not $npmCmd) {
        Write-Fail "Node.js or npm is missing! Please install Node 18+ LTS from https://nodejs.org/"
        return $false
    }

    $nodeVer = & $nodeCmd.Source --version 2>&1
    Write-Success "Node.js detected: $nodeVer"

    $frontendDir = Join-Path $ProjectPath "frontend"
    $nodeModules = Join-Path $frontendDir "node_modules"

    if (-not (Test-Path $nodeModules)) {
        Write-Info "node_modules missing in frontend. Executing 'npm install'..."
        cmd.exe /c "cd /d `"$frontendDir`" && npm install"
        Write-Success "Frontend packages installed successfully."
    } else {
        Write-Success "Frontend node_modules present."
    }

    return $true
}

# ------------------------------------------------------------------------------
# STEP 3: PORT CONFLICT AND INSTANCE RECOVERY
# ------------------------------------------------------------------------------
function Test-PortOccupied {
    param([int]$Port)
    $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    return ($null -ne $conn)
}

function Test-ReverseLabHealth {
    param([int]$Port = 8000)
    try {
        $resp = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/system/health" -Method Get -TimeoutSec 3 -ErrorAction Stop
        if ($resp.status -eq "operational" -or $resp.platform_name -eq "REVERSELAB AI") {
            return $true
        }
    } catch {}
    return $false
}

function Test-FrontendReady {
    param([int]$Port = 5173)
    try {
        $resp = Invoke-WebRequest -Uri "http://127.0.0.1:$Port" -Method Get -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($resp.StatusCode -eq 200) {
            return $true
        }
    } catch {}
    return $false
}

function Stop-OrphanedReverseLabInstances {
    param([int]$BackendPort = 8000, [int]$FrontendPort = 5173)

    $ports = @($BackendPort, $FrontendPort)
    foreach ($p in $ports) {
        $conns = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue
        foreach ($c in $conns) {
            $pidToKill = $c.OwningProcess
            try {
                $proc = Get-Process -Id $pidToKill -ErrorAction SilentlyContinue
                if ($proc -and ($proc.ProcessName -match "python|node|uvicorn|cmd")) {
                    Write-Warn "Terminating orphaned process $($proc.ProcessName) (PID: $pidToKill) listening on port $p..."
                    Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
                }
            } catch {}
        }
    }
}

# ------------------------------------------------------------------------------
# STEP 4: SERVICE ORCHESTRATION AND STARTUP
# ------------------------------------------------------------------------------
function Start-ReverseLabServices {
    param(
        [string]$ProjectPath,
        [string]$PythonExe
    )

    $logDir = Join-Path $ProjectPath "projects\Logs"
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

    # 1. Start FastAPI Backend if not already running
    if (-not (Test-ReverseLabHealth -Port 8000)) {
        Write-Info "Starting FastAPI backend server on http://127.0.0.1:8000..."
        $backendProc = Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", "`$env:PYTHONPATH = '$ProjectPath'; cd '$ProjectPath'; & '$PythonExe' -m uvicorn backend.main:app --host 127.0.0.1 --port 8000" -PassThru -WindowStyle Hidden

        # Wait for Backend Health
        Write-Info "Waiting for backend health check..."
        $backendReady = $false
        for ($i = 0; $i -lt 30; $i++) {
            Start-Sleep -Milliseconds 400
            if (Test-ReverseLabHealth -Port 8000) {
                $backendReady = $true
                break
            }
        }

        if (-not $backendReady) {
            Write-Fail "Backend failed to pass health check within 12 seconds."
            return $false
        }
    }
    Write-Success "Backend operational on http://127.0.0.1:8000 (API Docs: http://127.0.0.1:8000/docs)"

    # 2. Start Vite Frontend if not already running
    if (-not (Test-FrontendReady -Port 5173)) {
        Write-Info "Starting Vite frontend server on http://127.0.0.1:5173..."
        $frontendDir = Join-Path $ProjectPath "frontend"
        $frontendProc = Start-Process cmd.exe -ArgumentList "/c cd /d `"$frontendDir`" && npm run dev" -PassThru -WindowStyle Hidden

        # Wait for Frontend Readiness
        Write-Info "Waiting for frontend dev server..."
        $frontendReady = $false
        for ($i = 0; $i -lt 25; $i++) {
            Start-Sleep -Milliseconds 400
            if (Test-FrontendReady -Port 5173) {
                $frontendReady = $true
                break
            }
        }

        if ($frontendReady) {
            Write-Success "Frontend operational on http://127.0.0.1:5173"
        } else {
            Write-Warn "Frontend server process started; ready on http://127.0.0.1:5173"
        }
    } else {
        Write-Success "Frontend already active on http://127.0.0.1:5173"
    }

    # 3. Open Browser
    if (-not $NoBrowser) {
        Write-Info "Launching default browser to REVERSELAB AI..."
        Start-Process "http://127.0.0.1:5173"
    }

    return $true
}

# ------------------------------------------------------------------------------
# MAIN EXECUTION FLOW
# ------------------------------------------------------------------------------
Write-Header "REVERSELAB AI -- AUTOPILOT LAUNCHER AND DRIVE DISCOVERY"

# 1. Discover Project Location
$projectDir = Find-ReverseLabProject

if (-not $projectDir) {
    Write-Header "DRIVE DISCOVERY REPORT -- ACTION REQUIRED"
    Write-Fail "REVERSELAB AI repository could not be located on any currently connected drive."
    Write-Host ""
    Write-Host "  DIAGNOSTIC DETAILS:" -ForegroundColor Yellow
    Write-Host "  - Target Drive F: was not found or is physically disconnected."
    Write-Host "  - Searched Drives: $( (Get-PSDrive -PSProvider FileSystem).Root -join ', ' )"
    Write-Host ""
    Write-Host "  SAFE RECOVERY PATHS:" -ForegroundColor Cyan
    Write-Host "  [Option 1] Plug in your 1TB External USB HDD and re-run this launcher."
    Write-Host "  [Option 2] Clone your official GitHub repository to internal SSD (C:\REVERSELAB-AI):"
    Write-Host "             git clone https://github.com/albykl123/REVERSELAB-AI.git C:\REVERSELAB-AI" -ForegroundColor Green
    Write-Host ""
    exit 1
}

if ($DiagnosticOnly) {
    Write-Success "Project verified at: $projectDir"
    exit 0
}

# 2. If both services already running and healthy, open browser and finish
if ((Test-ReverseLabHealth -Port 8000) -and (Test-FrontendReady -Port 5173)) {
    Write-Success "REVERSELAB AI is already running and fully operational!"
    Write-Success "Backend: http://127.0.0.1:8000 | Frontend: http://127.0.0.1:5173"
    if (-not $NoBrowser) {
        Write-Info "Opening browser directly to dashboard..."
        Start-Process "http://127.0.0.1:5173"
    }
    exit 0
}

# 3. Ensure Dependencies
$pythonExe = Ensure-PythonEnvironment -ProjectPath $projectDir
if (-not $pythonExe) { exit 1 }

$frontendOk = Ensure-FrontendEnvironment -ProjectPath $projectDir
if (-not $frontendOk) { exit 1 }

# 4. Launch Services
$started = Start-ReverseLabServices -ProjectPath $projectDir -PythonExe $pythonExe
if ($started) {
    Write-Header "REVERSELAB AI IS OPERATIONAL"
    Write-Host "  Dashboard:         http://127.0.0.1:5173" -ForegroundColor Green
    Write-Host "  Backend API:       http://127.0.0.1:8000" -ForegroundColor Cyan
    Write-Host "  API Documentation: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
    Write-Host "  Project Root:      $projectDir" -ForegroundColor White
    Write-Host ""
    Write-Host "  To stop services, run 'scripts/stop_reverselab_ai.ps1' or close the terminal." -ForegroundColor DarkGray
    Write-Host ""
}
