<#
.SYNOPSIS
    External task launcher with pre-validation (REQ-001, REQ-008).

.DESCRIPTION
    Starts external tasks in a separate PowerShell window with:
    1. Pre-launch dry-run validation (REQ-008)
    2. Resource check before launch (REQ-004)
    3. Task wrapper integration for logging/heartbeat (REQ-002)
    4. Task registry update (REQ-003)

    Workflow:
    1. Check resources (RAM/CPU)
    2. Run dry_run_check.ps1 for validation
    3. If passed, launch task_wrapper.ps1 in new terminal
    4. Update task_registry.json
    5. Return task_id for status tracking

.PARAMETER Command
    Command to execute (required).

.PARAMETER TaskId
    Unique task identifier. Auto-generated if not provided.

.PARAMETER Owner
    KI identifier that owns this task. Default: unknown

.PARAMETER SkipDryRun
    Skip dry-run validation (for known-good scripts).

.PARAMETER SkipResourceCheck
    Skip resource availability check.

.PARAMETER LogDir
    Directory for log files. Default: AI_COLLABORATION/EXTERNAL_TASKS

.EXAMPLE
    .\start_external_task.ps1 -Command "python production_orchestrator.py --mode weekend"

.EXAMPLE
    .\start_external_task.ps1 -Command ".\scripts\MASTER_RECALIBRATION.ps1 -Workers 8" -Owner "ki2"

.NOTES
    Part of ISSUE-035: Autonomous External Process Orchestration
    Created: 2025-12-25
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Command,

    [string]$TaskId = "",

    [string]$Owner = "unknown",

    [switch]$SkipDryRun,

    [switch]$SkipResourceCheck,

    [string]$LogDir = "AI_COLLABORATION/EXTERNAL_TASKS"
)

# ============================================================================
# CONSTANTS
# ============================================================================
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$REPO_ROOT = Split-Path -Parent $SCRIPT_DIR
$MIN_RAM_GB = 8

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

function Get-AbsolutePath {
    param([string]$Path)
    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }
    return Join-Path $REPO_ROOT $Path
}

function New-TaskId {
    <#
    .SYNOPSIS
        Generate unique task ID.
    #>
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $random = Get-Random -Maximum 9999
    return "task_${timestamp}_${random}"
}

function Get-ScriptFromCommand {
    <#
    .SYNOPSIS
        Extract script path from command.
    #>
    param([string]$Command)

    # Pattern: python script.py ... OR .\script.ps1 ... OR script.ps1 ...
    if ($Command -match '^\s*python\s+([^\s]+)') {
        return $Matches[1]
    }
    if ($Command -match '^\s*\.?\\?([^\s]+\.ps1)') {
        return $Matches[1]
    }
    if ($Command -match '^\s*powershell.*-File\s+([^\s]+)') {
        return $Matches[1]
    }

    # Return first word as fallback
    return ($Command -split '\s+')[0]
}

function Test-ResourceAvailability {
    <#
    .SYNOPSIS
        Check if enough RAM is available.
    #>
    param([int]$MinRamGB = 8)

    try {
        $os = Get-CimInstance -ClassName Win32_OperatingSystem
        $freeRamGB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)

        if ($freeRamGB -ge $MinRamGB) {
            return @{
                available = $true
                free_ram_gb = $freeRamGB
                required_gb = $MinRamGB
                message = "Resources OK: ${freeRamGB}GB free (need ${MinRamGB}GB)"
            }
        }
        else {
            return @{
                available = $false
                free_ram_gb = $freeRamGB
                required_gb = $MinRamGB
                message = "Insufficient RAM: ${freeRamGB}GB free, need ${MinRamGB}GB"
            }
        }
    }
    catch {
        return @{
            available = $true
            free_ram_gb = -1
            required_gb = $MinRamGB
            message = "Resource check failed: $($_.Exception.Message) - proceeding anyway"
        }
    }
}

function Get-TaskType {
    <#
    .SYNOPSIS
        Detect task type from command for SCRIPT_CATALOG lookup (REQ-007).
    #>
    param([string]$Command)

    # Common task type patterns
    if ($Command -match 'MASTER_RECALIBRATION') { return "recalibration" }
    if ($Command -match 'production_orchestrator') { return "orchestrator" }
    if ($Command -match 'backtest|run_weekend_backtest') { return "backtest" }
    if ($Command -match 'team_mining|batch_adaptive') { return "mining" }
    if ($Command -match 'hybrid_prediction_engine') { return "prediction" }
    if ($Command -match 'optimized_run_codex|train') { return "training" }
    if ($Command -match '\.ps1') { return "powershell" }
    if ($Command -match 'python') { return "python" }

    return "unknown"
}

function Update-TaskRegistry {
    <#
    .SYNOPSIS
        Add task to central registry with file locking (REQ-003).
    #>
    param(
        [string]$TaskId,
        [string]$Command,
        [string]$Owner,
        [string]$StatusFile,
        [int]$EstimatedRamMb = 0,
        [int]$EstimatedCpuCores = 0
    )

    $registryPath = Get-AbsolutePath -Path "AI_COLLABORATION/EXTERNAL_TASKS/task_registry.json"
    $lockPath = "$registryPath.lock"
    $maxRetries = 10
    $retryDelayMs = 200

    # Acquire file lock (GAP-002 fix)
    for ($i = 0; $i -lt $maxRetries; $i++) {
        if (-not (Test-Path $lockPath)) {
            # Create lock file
            $null = New-Item -ItemType File -Path $lockPath -Force
            break
        }
        # Lock exists - wait and retry
        Start-Sleep -Milliseconds $retryDelayMs
        if ($i -eq ($maxRetries - 1)) {
            Write-Warning "Could not acquire registry lock after $maxRetries attempts - proceeding anyway"
        }
    }

    try {
        # Load or create registry
        if (Test-Path $registryPath) {
            $registry = Get-Content $registryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        }
        else {
            $registry = @{
                version = "1.0"
                created = (Get-Date).ToString("yyyy-MM-dd")
                description = "Central registry for external task tracking (REQ-003)"
                active_tasks = @()
                completed_tasks = @()
                failed_tasks = @()
                system_resources = @{
                    total_ram_mb = $null
                    available_ram_mb = $null
                    reserved_ram_mb = 0
                    cpu_cores = $null
                    reserved_cores = 0
                    min_ram_reserve_mb = 8192
                }
            }
        }

        # Detect task type (GAP-004 fix - REQ-007)
        $taskType = Get-TaskType -Command $Command

        # Create task entry with all fields (GAP-004, GAP-005)
        $taskEntry = @{
            task_id = $TaskId
            command = $Command
            owner = $Owner
            status_file = $StatusFile
            type = $taskType
            started_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
            estimated_ram_mb = $EstimatedRamMb
            estimated_cpu_cores = $EstimatedCpuCores
        }

        # GAP-001 fix: Use active_tasks instead of tasks
        if (-not $registry.PSObject.Properties.Name.Contains("active_tasks")) {
            # Migrate old schema
            if ($registry.PSObject.Properties.Name.Contains("tasks")) {
                $registry | Add-Member -NotePropertyName "active_tasks" -NotePropertyValue $registry.tasks -Force
            }
            else {
                $registry | Add-Member -NotePropertyName "active_tasks" -NotePropertyValue @() -Force
            }
        }

        # Ensure active_tasks is an array
        if ($null -eq $registry.active_tasks) {
            $registry.active_tasks = @()
        }

        # Add new task to active_tasks
        $newActiveTasks = @($registry.active_tasks) + $taskEntry
        $registry.active_tasks = $newActiveTasks

        # Update resource reservations (GAP-005)
        if ($registry.PSObject.Properties.Name.Contains("system_resources")) {
            $registry.system_resources.reserved_ram_mb += $EstimatedRamMb
            $registry.system_resources.reserved_cores += $EstimatedCpuCores
        }

        $registry | ConvertTo-Json -Depth 4 | Out-File -FilePath $registryPath -Encoding UTF8 -Force
    }
    finally {
        # Release lock
        if (Test-Path $lockPath) {
            Remove-Item $lockPath -Force -ErrorAction SilentlyContinue
        }
    }
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

function Get-DurationEstimate {
    <#
    .SYNOPSIS
        Get duration estimate for a script (REQ-010).
    #>
    param(
        [string]$Command,
        [hashtable]$Parameters = @{}
    )

    try {
        $estimateScript = Join-Path $SCRIPT_DIR "estimate_duration.ps1"

        if (-not (Test-Path $estimateScript)) {
            return $null
        }

        $scriptPath = Get-ScriptFromCommand -Command $Command
        $output = & $estimateScript -Script $scriptPath -Parameters $Parameters 2>&1 | Out-String

        if ($output -match '^\s*\{') {
            $estimate = $output | ConvertFrom-Json
            return $estimate
        }
    }
    catch {
        # Silent failure
    }

    return $null
}

try {
    $result = [ordered]@{
        success = $false
        task_id = ""
        command = $Command
        owner = $Owner
        status_file = ""
        message = ""
        validation = @{}
        resources = @{}
        duration_estimate = @{}
    }

    # Generate task ID if not provided
    if (-not $TaskId) {
        $TaskId = New-TaskId
    }
    $result.task_id = $TaskId

    Write-Host "[START] Launching task: $TaskId" -ForegroundColor Cyan
    Write-Host "        Command: $Command"
    Write-Host "        Owner: $Owner"

    # Step 1: Resource check
    if (-not $SkipResourceCheck) {
        Write-Host "`n[1/3] Checking resources..." -ForegroundColor Yellow
        $resourceCheck = Test-ResourceAvailability -MinRamGB $MIN_RAM_GB
        $result.resources = $resourceCheck

        if (-not $resourceCheck.available) {
            $result.message = $resourceCheck.message
            Write-Host "       [FAIL] $($resourceCheck.message)" -ForegroundColor Red
            $result | ConvertTo-Json -Depth 3
            exit 1
        }
        Write-Host "       [OK] $($resourceCheck.message)" -ForegroundColor Green
    }
    else {
        Write-Host "`n[1/3] Resource check skipped" -ForegroundColor Yellow
    }

    # Step 2: Dry-run validation
    if (-not $SkipDryRun) {
        Write-Host "`n[2/3] Running dry-run validation..." -ForegroundColor Yellow

        $scriptPath = Get-ScriptFromCommand -Command $Command
        $dryRunScript = Join-Path $SCRIPT_DIR "dry_run_check.ps1"

        if (Test-Path $dryRunScript) {
            $dryRunResult = & $dryRunScript -ScriptPath $scriptPath 2>&1

            # Parse JSON output
            try {
                $validationJson = $dryRunResult | Where-Object { $_ -match '^\s*\{' } | Out-String
                if ($validationJson) {
                    $validation = $validationJson | ConvertFrom-Json
                    $result.validation = $validation
                }
            }
            catch {
                # Non-JSON output
                $result.validation = @{ raw_output = ($dryRunResult | Out-String) }
            }

            $dryRunExitCode = $LASTEXITCODE

            if ($dryRunExitCode -eq 0) {
                Write-Host "       [OK] Validation passed" -ForegroundColor Green
            }
            elseif ($dryRunExitCode -eq 2) {
                Write-Host "       [WARN] Script not in catalog - syntax check only" -ForegroundColor Yellow
            }
            else {
                $result.message = "Dry-run validation failed"
                Write-Host "       [FAIL] Validation failed" -ForegroundColor Red
                $result | ConvertTo-Json -Depth 3
                exit 1
            }
        }
        else {
            Write-Host "       [WARN] dry_run_check.ps1 not found - skipping" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "`n[2/3] Dry-run validation skipped" -ForegroundColor Yellow
    }

    # Step 2.5: Get duration estimate (REQ-010)
    Write-Host "`n[2.5/3] Getting duration estimate..." -ForegroundColor Yellow
    $durationEstimate = Get-DurationEstimate -Command $Command
    if ($durationEstimate) {
        $result.duration_estimate = $durationEstimate
        Write-Host "       Estimated: $($durationEstimate.estimated_duration_min) min (confidence: $($durationEstimate.confidence), source: $($durationEstimate.source))" -ForegroundColor Cyan
    }
    else {
        Write-Host "       [INFO] No duration estimate available" -ForegroundColor Yellow
    }

    # Step 3: Launch task in external terminal
    Write-Host "`n[3/3] Launching external task..." -ForegroundColor Yellow

    $absLogDir = Get-AbsolutePath -Path $LogDir
    $taskWrapperPath = Join-Path $SCRIPT_DIR "task_wrapper.ps1"
    $statusFile = Join-Path $absLogDir "$TaskId.status"
    $result.status_file = $statusFile

    # Ensure log directory exists
    if (-not (Test-Path $absLogDir)) {
        New-Item -ItemType Directory -Path $absLogDir -Force | Out-Null
    }

    # Build wrapper command
    $wrapperCommand = "& '$taskWrapperPath' -TaskId '$TaskId' -Command '$Command' -LogDir '$absLogDir' -Owner '$Owner'"

    # Launch in new PowerShell window (GAP-003 fix: WindowStyle Normal for visibility per REQ-001)
    # BUG-FIX 2025-12-25: WorkingDirectory MUST be set, otherwise relative paths fail!
    Start-Process powershell.exe -WorkingDirectory $REPO_ROOT -WindowStyle Normal -ArgumentList @(
        "-NoExit",
        "-Command",
        $wrapperCommand
    )

    # Update registry with resource estimates
    Update-TaskRegistry -TaskId $TaskId -Command $Command -Owner $Owner -StatusFile $statusFile -EstimatedRamMb 0 -EstimatedCpuCores 0

    # Success
    $result.success = $true
    $result.message = "Task $TaskId launched successfully"

    Write-Host "       [OK] Task launched in new terminal" -ForegroundColor Green
    Write-Host "`n[RESULT]" -ForegroundColor Cyan
    Write-Host "  Task ID:     $TaskId"
    Write-Host "  Status file: $statusFile"
    Write-Host "  Check with:  .\scripts\check_task_status.ps1 -TaskId $TaskId"

    $result | ConvertTo-Json -Depth 3
    exit 0
}
catch {
    Write-Error "Task launch failed: $($_.Exception.Message)"
    exit 1
}
