<#
.SYNOPSIS
    Check status of a specific external task (TASK-004, REQ-003).

.DESCRIPTION
    Polls task status from *.status files and task_registry.json.
    Provides stale detection (5-minute heartbeat timeout per REQ-003).
    Returns JSON output for KI consumption.

.PARAMETER TaskId
    Unique identifier of the task to check.

.PARAMETER RegistryPath
    Path to task_registry.json. Default: AI_COLLABORATION/EXTERNAL_TASKS/task_registry.json

.PARAMETER StaleThresholdMinutes
    Minutes without heartbeat before task is considered STALE. Default: 5 (REQ-003)

.PARAMETER JsonOnly
    Output only JSON, no human-readable summary.

.EXAMPLE
    .\check_task_status.ps1 -TaskId backtest_001
    Returns JSON with task status, progress, duration, stale detection

.EXAMPLE
    .\check_task_status.ps1 -TaskId backtest_001 -JsonOnly
    Returns only JSON output (for KI consumption)

.NOTES
    Part of ISSUE-035: Autonomous External Process Orchestration
    Phase 5: Status Checker & Task Management
    Created: 2025-12-25
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$TaskId,

    [string]$RegistryPath = "AI_COLLABORATION/EXTERNAL_TASKS/task_registry.json",

    [int]$StaleThresholdMinutes = 5,

    [switch]$JsonOnly
)

# Ensure absolute path
if (-not [System.IO.Path]::IsPathRooted($RegistryPath)) {
    $RegistryPath = Join-Path (Get-Location) $RegistryPath
}

function Get-TaskFromRegistry {
    <#
    .SYNOPSIS
        Find task in registry by TaskId
    #>
    param([string]$TaskId, [string]$RegistryPath)

    if (-not (Test-Path $RegistryPath)) {
        return $null
    }

    try {
        $registry = Get-Content $RegistryPath -Raw -Encoding UTF8 | ConvertFrom-Json

        # Search in active_tasks
        foreach ($task in $registry.active_tasks) {
            if ($task.task_id -eq $TaskId) {
                return @{
                    source = "active"
                    task = $task
                }
            }
        }

        # Search in completed_tasks
        foreach ($task in $registry.completed_tasks) {
            if ($task.task_id -eq $TaskId) {
                return @{
                    source = "completed"
                    task = $task
                }
            }
        }

        # Search in failed_tasks
        foreach ($task in $registry.failed_tasks) {
            if ($task.task_id -eq $TaskId) {
                return @{
                    source = "failed"
                    task = $task
                }
            }
        }

        return $null
    }
    catch {
        return $null
    }
}

function Get-StatusFromFile {
    <#
    .SYNOPSIS
        Read status from *.status file
    #>
    param([string]$StatusFilePath)

    if (-not (Test-Path $StatusFilePath)) {
        return $null
    }

    try {
        $content = Get-Content $StatusFilePath -Raw -Encoding UTF8 | ConvertFrom-Json
        return $content
    }
    catch {
        return $null
    }
}

function Test-IsStale {
    <#
    .SYNOPSIS
        Check if task is stale based on heartbeat timeout
    #>
    param(
        [datetime]$LastHeartbeat,
        [int]$ThresholdMinutes
    )

    $now = Get-Date
    $timeSinceHeartbeat = $now - $LastHeartbeat
    return $timeSinceHeartbeat.TotalMinutes -gt $ThresholdMinutes
}

function Get-StatusFilePath {
    <#
    .SYNOPSIS
        Construct status file path from task_id
    #>
    param([string]$TaskId, [string]$BaseDir)

    return Join-Path $BaseDir "$TaskId.status"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

try {
    $baseDir = Split-Path $RegistryPath -Parent
    $result = [ordered]@{
        task_id = $TaskId
        found = $false
        status = "NOT_FOUND"
        source = ""
        progress_percent = 0
        current_phase = ""
        duration_seconds = 0
        started_at = ""
        last_heartbeat = ""
        is_stale = $false
        stale_threshold_minutes = $StaleThresholdMinutes
        exit_code = $null
        error_message = ""
        log_file = ""
        err_file = ""
        status_file = ""
        owner = ""
        command = ""
        pid = $null
        checked_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
    }

    # Step 1: Check registry for task metadata
    $registryTask = Get-TaskFromRegistry -TaskId $TaskId -RegistryPath $RegistryPath
    if ($registryTask) {
        $result.found = $true
        $result.source = "registry_$($registryTask.source)"
        $result.owner = $registryTask.task.owner
        $result.command = $registryTask.task.command
        $result.started_at = $registryTask.task.started_at

        # Get status file path from registry if available
        if ($registryTask.task.status_file) {
            $result.status_file = $registryTask.task.status_file
        }
    }

    # Step 2: Try status file (from registry or constructed path)
    $statusFilePath = if ($result.status_file) {
        $result.status_file
    } else {
        Get-StatusFilePath -TaskId $TaskId -BaseDir $baseDir
    }

    $statusData = Get-StatusFromFile -StatusFilePath $statusFilePath
    if ($statusData) {
        $result.found = $true
        $result.status = $statusData.status
        $result.progress_percent = $statusData.progress_percent
        $result.current_phase = $statusData.current_phase
        $result.duration_seconds = $statusData.duration_seconds
        $result.started_at = $statusData.started_at
        $result.last_heartbeat = $statusData.last_heartbeat
        $result.exit_code = $statusData.exit_code
        $result.error_message = $statusData.error_message
        $result.log_file = $statusData.log_file
        $result.err_file = $statusData.err_file
        $result.status_file = $statusFilePath
        $result.owner = $statusData.started_by
        $result.command = $statusData.command
        $result.pid = $statusData.pid

        # Update source to include status file
        if (-not $result.source) {
            $result.source = "status_file"
        } else {
            $result.source = "$($result.source)+status_file"
        }

        # Step 3: Check for stale (only for RUNNING tasks)
        if ($statusData.status -eq "RUNNING") {
            try {
                $heartbeatTime = [datetime]::ParseExact(
                    $statusData.last_heartbeat,
                    "yyyy-MM-ddTHH:mm:ss",
                    [System.Globalization.CultureInfo]::InvariantCulture
                )
                $result.is_stale = Test-IsStale -LastHeartbeat $heartbeatTime -ThresholdMinutes $StaleThresholdMinutes

                if ($result.is_stale) {
                    $result.status = "STALE"
                }
            }
            catch {
                # If can't parse heartbeat, assume not stale
                $result.is_stale = $false
            }
        }
    }

    # Output JSON
    $jsonOutput = $result | ConvertTo-Json -Depth 3

    if (-not $JsonOnly) {
        # Human-readable summary
        Write-Host ""
        Write-Host "=== Task Status: $TaskId ===" -ForegroundColor Cyan
        Write-Host ""

        if ($result.found) {
            $statusColor = switch ($result.status) {
                "COMPLETED" { "Green" }
                "RUNNING" { "Yellow" }
                "PENDING" { "White" }
                "FAILED" { "Red" }
                "STALE" { "Magenta" }
                default { "Gray" }
            }

            Write-Host "Status:      " -NoNewline
            Write-Host $result.status -ForegroundColor $statusColor

            Write-Host "Progress:    $($result.progress_percent)%"

            if ($result.current_phase) {
                Write-Host "Phase:       $($result.current_phase)"
            }

            Write-Host "Duration:    $($result.duration_seconds) seconds"
            Write-Host "Owner:       $($result.owner)"

            if ($result.is_stale) {
                Write-Host ""
                Write-Host "WARNING: Task is STALE (no heartbeat for >$StaleThresholdMinutes minutes)" -ForegroundColor Magenta
            }

            if ($result.error_message) {
                Write-Host ""
                Write-Host "Error: $($result.error_message)" -ForegroundColor Red
            }

            Write-Host ""
            Write-Host "Log file:    $($result.log_file)"
        }
        else {
            Write-Host "Task not found in registry or status files" -ForegroundColor Red
        }

        Write-Host ""
        Write-Host "=== JSON Output ===" -ForegroundColor Gray
    }

    # Always output JSON (for KI parsing)
    Write-Output $jsonOutput

    # Exit code based on status
    switch ($result.status) {
        "COMPLETED" { exit 0 }
        "RUNNING" { exit 0 }
        "PENDING" { exit 0 }
        "FAILED" { exit 1 }
        "STALE" { exit 2 }
        "NOT_FOUND" { exit 3 }
        default { exit 4 }
    }
}
catch {
    $errorResult = [ordered]@{
        task_id = $TaskId
        found = $false
        status = "ERROR"
        error_message = $_.Exception.Message
        checked_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
    }

    $errorResult | ConvertTo-Json -Depth 2
    exit 1
}
