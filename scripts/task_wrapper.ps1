<#
.SYNOPSIS
    Task wrapper for standardized log/heartbeat/status management (REQ-002, TASK-002).

.DESCRIPTION
    Wraps external task execution with:
    - Standardized log format ({task_id}.log, {task_id}.err, {task_id}.status)
    - Heartbeat every 30s for crash detection (REQ-006)
    - JSON status file with 13 fields
    - Log rotation at 100MB
    - Progress parsing from output

.PARAMETER TaskId
    Unique identifier for the task (required).

.PARAMETER Command
    Command to execute (required).

.PARAMETER LogDir
    Directory for log/status files. Default: AI_COLLABORATION/EXTERNAL_TASKS

.PARAMETER Owner
    KI identifier that owns this task. Default: unknown

.PARAMETER MaxLogSizeMB
    Maximum log file size before rotation. Default: 100

.EXAMPLE
    .\task_wrapper.ps1 -TaskId "backtest_001" -Command "python run_backtest.py"

.EXAMPLE
    .\task_wrapper.ps1 -TaskId "test_001" -Command "echo test" -Owner "ki2"

.NOTES
    Part of ISSUE-035: Autonomous External Process Orchestration
    Created: 2025-12-25
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$TaskId,

    [Parameter(Mandatory=$true)]
    [string]$Command,

    [string]$LogDir = "AI_COLLABORATION/EXTERNAL_TASKS",

    [string]$Owner = "unknown",

    [int]$MaxLogSizeMB = 100,

    [string]$ScriptName = "",

    [hashtable]$ScriptParameters = @{}
)

# Constants
$HEARTBEAT_INTERVAL_SECONDS = 30
$MAX_LOG_SIZE_BYTES = $MaxLogSizeMB * 1024 * 1024

# Global variables for cleanup
$script:HeartbeatJob = $null
$script:LogFile = $null
$script:ErrFile = $null
$script:StatusFile = $null
$script:ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Initialize-LogFiles {
    <#
    .SYNOPSIS
        Create log directory and initialize output files.
    #>
    param([string]$TaskId, [string]$LogDir)

    # Ensure absolute path
    if (-not [System.IO.Path]::IsPathRooted($LogDir)) {
        $LogDir = Join-Path (Get-Location) $LogDir
    }

    # Create directory if needed
    if (-not (Test-Path $LogDir)) {
        New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    }

    $script:LogFile = Join-Path $LogDir "$TaskId.log"
    $script:ErrFile = Join-Path $LogDir "$TaskId.err"
    $script:StatusFile = Join-Path $LogDir "$TaskId.status"

    # Initialize files
    "" | Out-File -FilePath $script:LogFile -Encoding UTF8 -Force
    "" | Out-File -FilePath $script:ErrFile -Encoding UTF8 -Force

    return @{
        log_file = $script:LogFile
        err_file = $script:ErrFile
        status_file = $script:StatusFile
    }
}

function Write-Status {
    <#
    .SYNOPSIS
        Write or update JSON status file with 13 required fields.
    #>
    param(
        [string]$TaskId,
        [string]$Command,
        [string]$LogFile,
        [string]$ErrFile,
        [string]$Status,
        [int]$ProgressPercent = 0,
        [string]$CurrentPhase = "",
        [int]$ProcessId = 0,
        [int]$ExitCode = -1,
        [string]$ErrorMessage = "",
        [datetime]$StartedAt,
        [string]$Owner
    )

    $now = Get-Date
    $durationSeconds = 0
    if ($StartedAt) {
        $durationSeconds = [math]::Round(($now - $StartedAt).TotalSeconds, 1)
    }

    $statusObj = [ordered]@{
        task_id = $TaskId
        command = $Command
        log_file = $LogFile
        err_file = $ErrFile
        started_at = if ($StartedAt) { $StartedAt.ToString("yyyy-MM-ddTHH:mm:ss") } else { "" }
        started_by = $Owner
        status = $Status
        progress_percent = $ProgressPercent
        current_phase = $CurrentPhase
        pid = $ProcessId
        last_heartbeat = $now.ToString("yyyy-MM-ddTHH:mm:ss")
        exit_code = $ExitCode
        error_message = $ErrorMessage
        duration_seconds = $durationSeconds
    }

    $statusObj | ConvertTo-Json -Depth 2 | Out-File -FilePath $script:StatusFile -Encoding UTF8 -Force
}

function Start-Heartbeat {
    <#
    .SYNOPSIS
        Start background job that updates last_heartbeat every 30 seconds.
    #>
    param([string]$StatusFile)

    $script:HeartbeatJob = Start-Job -ScriptBlock {
        param($StatusFile, $Interval)

        while ($true) {
            Start-Sleep -Seconds $Interval

            try {
                if (Test-Path $StatusFile) {
                    $content = Get-Content $StatusFile -Raw -Encoding UTF8 | ConvertFrom-Json
                    $content.last_heartbeat = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
                    $content | ConvertTo-Json -Depth 2 | Out-File -FilePath $StatusFile -Encoding UTF8 -Force
                }
            }
            catch {
                # Silently continue if update fails
            }
        }
    } -ArgumentList $StatusFile, $HEARTBEAT_INTERVAL_SECONDS

    return $script:HeartbeatJob
}

function Stop-Heartbeat {
    <#
    .SYNOPSIS
        Stop the heartbeat background job.
    #>
    if ($script:HeartbeatJob) {
        Stop-Job -Job $script:HeartbeatJob -ErrorAction SilentlyContinue
        Remove-Job -Job $script:HeartbeatJob -Force -ErrorAction SilentlyContinue
        $script:HeartbeatJob = $null
    }
}

function Rotate-LogIfNeeded {
    <#
    .SYNOPSIS
        Rotate log file if it exceeds maximum size.
    #>
    param([string]$LogFile, [long]$MaxSizeBytes)

    if (-not (Test-Path $LogFile)) { return }

    $fileInfo = Get-Item $LogFile
    if ($fileInfo.Length -gt $MaxSizeBytes) {
        # Keep last 10% of the file
        $keepBytes = [math]::Floor($MaxSizeBytes * 0.1)
        $content = Get-Content $LogFile -Tail ([math]::Floor($keepBytes / 100))

        $rotationMarker = "[$(Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')] === LOG ROTATED (exceeded $MaxLogSizeMB MB) ==="
        @($rotationMarker) + $content | Out-File -FilePath $LogFile -Encoding UTF8 -Force
    }
}

function Get-ProgressFromOutput {
    <#
    .SYNOPSIS
        Parse progress from command output (X/Y or X% patterns).
    #>
    param([string]$Line)

    # Pattern: X/Y (e.g., "5/10", "Processing 5/10")
    if ($Line -match '(\d+)\s*/\s*(\d+)') {
        $current = [int]$Matches[1]
        $total = [int]$Matches[2]
        if ($total -gt 0) {
            return [math]::Floor(($current / $total) * 100)
        }
    }

    # Pattern: X% (e.g., "50%", "Progress: 50%")
    if ($Line -match '(\d+)\s*%') {
        $percent = [int]$Matches[1]
        if ($percent -ge 0 -and $percent -le 100) {
            return $percent
        }
    }

    return -1  # No progress found
}

function Get-PhaseFromOutput {
    <#
    .SYNOPSIS
        Parse current phase from command output.
    #>
    param([string]$Line)

    # Pattern: [Phase: X] (with colon inside brackets)
    if ($Line -match '\[Phase:\s*([^\]]+)\]') {
        return $Matches[1].Trim()
    }
    # Pattern: [Phase X] (without colon)
    if ($Line -match '\[Phase\s+([^\]]+)\]') {
        return $Matches[1].Trim()
    }
    # Pattern: Phase: X (outside brackets)
    if ($Line -match 'Phase:\s*(\S+)') {
        return $Matches[1].Trim()
    }

    return ""
}

function Update-ExecutionHistory {
    <#
    .SYNOPSIS
        Update execution history for duration learning (REQ-010).
        Silently fails if update script not found or errors occur.
    #>
    param(
        [string]$TaskId,
        [string]$ScriptName,
        [double]$DurationMin,
        [hashtable]$Parameters,
        [int]$ExitCode
    )

    try {
        $updateScript = Join-Path $script:ScriptDir "update_execution_history.ps1"

        if (-not (Test-Path $updateScript)) {
            # Script not found - silent failure
            return
        }

        # Call update script
        $params = @{
            TaskId = $TaskId
            Script = $ScriptName
            DurationMin = $DurationMin
            ExitCode = $ExitCode
        }

        if ($Parameters -and $Parameters.Count -gt 0) {
            $params.Parameters = $Parameters
        }

        & $updateScript @params 2>&1 | Out-Null
    }
    catch {
        # Silent failure - duration learning should not block task completion
    }
}

function Get-ScriptNameFromCommand {
    <#
    .SYNOPSIS
        Extract script name from command for history tracking.
    #>
    param([string]$Command)

    # Pattern: python script.py
    if ($Command -match 'python\s+([^\s]+\.py)') {
        return Split-Path -Leaf $Matches[1]
    }
    # Pattern: .\script.ps1 or script.ps1
    if ($Command -match '\.?\\?([^\s]+\.ps1)') {
        return Split-Path -Leaf $Matches[1]
    }
    # Pattern: powershell ... -File script.ps1
    if ($Command -match '-File\s+([^\s]+)') {
        return Split-Path -Leaf $Matches[1]
    }

    return ""
}

function Invoke-CommandWithLogging {
    <#
    .SYNOPSIS
        Execute command and capture output with logging.
    #>
    param(
        [string]$Command,
        [string]$TaskId,
        [string]$LogFile,
        [string]$ErrFile,
        [string]$Owner,
        [datetime]$StartedAt
    )

    $progressPercent = 0
    $currentPhase = ""
    $processId = 0

    try {
        # Start process
        $pinfo = New-Object System.Diagnostics.ProcessStartInfo
        $pinfo.FileName = "powershell.exe"
        $pinfo.Arguments = "-NoProfile -Command `"$Command`""
        $pinfo.WorkingDirectory = (Get-Location).Path  # BUG-FIX 2025-12-25: Ensure relative paths work
        $pinfo.RedirectStandardOutput = $true
        $pinfo.RedirectStandardError = $true
        $pinfo.UseShellExecute = $false
        $pinfo.CreateNoWindow = $true

        $process = New-Object System.Diagnostics.Process
        $process.StartInfo = $pinfo

        # Event handlers for async output capture
        $stdoutBuilder = New-Object System.Text.StringBuilder
        $stderrBuilder = New-Object System.Text.StringBuilder

        $process.Start() | Out-Null
        $processId = $process.Id

        # Update status with PID
        Write-Status -TaskId $TaskId -Command $Command -LogFile $LogFile -ErrFile $ErrFile `
            -Status "RUNNING" -ProgressPercent $progressPercent -CurrentPhase $currentPhase `
            -ProcessId $processId -StartedAt $StartedAt -Owner $Owner

        # Read output streams
        while (-not $process.HasExited) {
            # Read stdout
            $line = $process.StandardOutput.ReadLine()
            if ($null -ne $line) {
                $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
                "[$timestamp] $line" | Out-File -FilePath $LogFile -Append -Encoding UTF8

                # Parse progress
                $newProgress = Get-ProgressFromOutput -Line $line
                if ($newProgress -ge 0) {
                    $progressPercent = $newProgress
                }

                # Parse phase
                $newPhase = Get-PhaseFromOutput -Line $line
                if ($newPhase) {
                    $currentPhase = $newPhase
                }

                # Update status periodically (every 5 lines or on progress/phase change)
                Write-Status -TaskId $TaskId -Command $Command -LogFile $LogFile -ErrFile $ErrFile `
                    -Status "RUNNING" -ProgressPercent $progressPercent -CurrentPhase $currentPhase `
                    -ProcessId $processId -StartedAt $StartedAt -Owner $Owner

                # Check for log rotation
                Rotate-LogIfNeeded -LogFile $LogFile -MaxSizeBytes $MAX_LOG_SIZE_BYTES
            }

            Start-Sleep -Milliseconds 100
        }

        # Read remaining output
        $remainingStdout = $process.StandardOutput.ReadToEnd()
        $remainingStderr = $process.StandardError.ReadToEnd()

        if ($remainingStdout) {
            $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
            $remainingStdout -split "`n" | ForEach-Object {
                if ($_) { "[$timestamp] $_" | Out-File -FilePath $LogFile -Append -Encoding UTF8 }
            }
        }

        if ($remainingStderr) {
            $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
            $remainingStderr -split "`n" | ForEach-Object {
                if ($_) { "[$timestamp] $_" | Out-File -FilePath $ErrFile -Append -Encoding UTF8 }
            }
        }

        $exitCode = $process.ExitCode
        $process.Close()

        return @{
            exit_code = $exitCode
            progress_percent = $progressPercent
            current_phase = $currentPhase
            pid = $processId
        }
    }
    catch {
        $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        "[$timestamp] ERROR: $($_.Exception.Message)" | Out-File -FilePath $ErrFile -Append -Encoding UTF8

        return @{
            exit_code = 1
            progress_percent = $progressPercent
            current_phase = $currentPhase
            pid = $processId
            error = $_.Exception.Message
        }
    }
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

try {
    $startTime = Get-Date

    # Initialize files
    $files = Initialize-LogFiles -TaskId $TaskId -LogDir $LogDir

    # Write initial PENDING status
    Write-Status -TaskId $TaskId -Command $Command -LogFile $files.log_file -ErrFile $files.err_file `
        -Status "PENDING" -StartedAt $startTime -Owner $Owner

    # Log start
    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    "[$timestamp] Task $TaskId started by $Owner" | Out-File -FilePath $script:LogFile -Append -Encoding UTF8
    "[$timestamp] Command: $Command" | Out-File -FilePath $script:LogFile -Append -Encoding UTF8

    # Update to RUNNING
    Write-Status -TaskId $TaskId -Command $Command -LogFile $files.log_file -ErrFile $files.err_file `
        -Status "RUNNING" -StartedAt $startTime -Owner $Owner

    # Start heartbeat
    $heartbeat = Start-Heartbeat -StatusFile $script:StatusFile

    # Execute command
    $result = Invoke-CommandWithLogging -Command $Command -TaskId $TaskId `
        -LogFile $script:LogFile -ErrFile $script:ErrFile -Owner $Owner -StartedAt $startTime

    # Stop heartbeat
    Stop-Heartbeat

    # Determine final status
    $finalStatus = if ($result.exit_code -eq 0) { "COMPLETED" } else { "FAILED" }
    $errorMessage = if ($result.error) { $result.error } else { "" }

    # Write final status
    Write-Status -TaskId $TaskId -Command $Command -LogFile $files.log_file -ErrFile $files.err_file `
        -Status $finalStatus -ProgressPercent $result.progress_percent -CurrentPhase $result.current_phase `
        -ProcessId $result.pid -ExitCode $result.exit_code -ErrorMessage $errorMessage `
        -StartedAt $startTime -Owner $Owner

    # Log completion
    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    "[$timestamp] Task $TaskId $finalStatus (exit_code: $($result.exit_code))" | Out-File -FilePath $script:LogFile -Append -Encoding UTF8

    # Update execution history for duration learning (REQ-010)
    $endTime = Get-Date
    $durationMin = [math]::Round(($endTime - $startTime).TotalMinutes, 2)

    # Determine script name (use parameter or extract from command)
    $historyScriptName = if ($ScriptName) { $ScriptName } else { Get-ScriptNameFromCommand -Command $Command }

    if ($historyScriptName) {
        "[$timestamp] Updating execution history: $historyScriptName (duration: ${durationMin}min)" | Out-File -FilePath $script:LogFile -Append -Encoding UTF8
        Update-ExecutionHistory `
            -TaskId $TaskId `
            -ScriptName $historyScriptName `
            -DurationMin $durationMin `
            -Parameters $ScriptParameters `
            -ExitCode $result.exit_code
    }

    # Output summary
    Write-Host "Task $TaskId $finalStatus"
    Write-Host "Log: $($script:LogFile)"
    Write-Host "Status: $($script:StatusFile)"

    exit $result.exit_code
}
catch {
    # Ensure heartbeat is stopped
    Stop-Heartbeat

    # Write error status
    if ($script:StatusFile) {
        Write-Status -TaskId $TaskId -Command $Command -LogFile $script:LogFile -ErrFile $script:ErrFile `
            -Status "FAILED" -ExitCode 1 -ErrorMessage $_.Exception.Message `
            -StartedAt $startTime -Owner $Owner
    }

    # Log error
    if ($script:ErrFile) {
        $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        "[$timestamp] FATAL: $($_.Exception.Message)" | Out-File -FilePath $script:ErrFile -Append -Encoding UTF8
    }

    Write-Error "Task $TaskId FAILED: $($_.Exception.Message)"
    exit 1
}
