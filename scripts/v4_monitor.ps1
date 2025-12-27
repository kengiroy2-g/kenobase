# V4 MONITOR: Live Status Dashboard
# Usage: .\scripts\v4_monitor.ps1 -Watch

param(
    [string]$PlanFile = "AI_COLLABORATION/PLANS/v4_production_issues_longrun.yaml",
    [string]$LogFile = "AI_COLLABORATION/LOGS/loop_v4.log",
    [string]$MetricsFile = "AI_COLLABORATION/METRICS/loop_v4_metrics.jsonl",
    [string]$HandoffsDir = "AI_COLLABORATION/HANDOFFS",
    [string]$LockFile = "AI_COLLABORATION/MESSAGE_QUEUE/loop_v4.lock.json",
    [switch]$Watch,
    [int]$Interval = 5
)

function Get-LoopStatus {
    $status = @{ Running = $false; Reason = "No Activity"; LogAge = 999 }

    if (Test-Path $LockFile) {
        $lock = Get-Content $LockFile -Raw | ConvertFrom-Json -ErrorAction SilentlyContinue
        if ($lock -and $lock.pid) {
            $status.LockPid = $lock.pid
            $status.StartedAt = $lock.started_at
        }
    }

    if (Test-Path $LogFile) {
        $lastWrite = (Get-Item $LogFile).LastWriteTime
        $age = ((Get-Date) - $lastWrite).TotalSeconds
        $status.LogAge = [math]::Round($age)
        if ($age -lt 120) {
            $status.Running = $true
            $status.Reason = "Active"
        }
    }

    return $status
}

function Get-CurrentTask {
    if (-not (Test-Path $PlanFile)) { return $null }
    $content = Get-Content $PlanFile -Raw
    if ($content -match "(?s)- id: (\S+)\s+name: `"([^`"]+)`".*?status: IN_PROGRESS.*?current_phase: (\S+)") {
        return @{ Id = $Matches[1]; Name = $Matches[2]; Phase = $Matches[3] }
    }
    return $null
}

function Get-TaskProgress {
    if (-not (Test-Path $PlanFile)) { return $null }
    $content = Get-Content $PlanFile -Raw
    $total = ([regex]::Matches($content, "- id:")).Count
    $complete = ([regex]::Matches($content, "status: COMPLETE")).Count
    $inProgress = ([regex]::Matches($content, "status: IN_PROGRESS")).Count
    $escalate = ([regex]::Matches($content, "status: ESCALATE")).Count
    $blocked = ([regex]::Matches($content, "status: BLOCKED")).Count
    $pending = $total - $complete - $inProgress - $escalate - $blocked
    $pct = if ($total -gt 0) { [math]::Round(($complete / $total) * 100) } else { 0 }
    return @{ Total = $total; Complete = $complete; InProgress = $inProgress; Pending = $pending; Escalate = $escalate; Blocked = $blocked; Percent = $pct }
}

function Get-PendingEscalations {
    $escalationsDir = "AI_COLLABORATION/ESCALATIONS"
    if (-not (Test-Path $escalationsDir)) { return @() }

    $pending = @()
    $files = Get-ChildItem $escalationsDir -Filter "escalation_*.md" -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        if ($content -match "status:\s*PENDING") {
            $taskId = ""
            $taskName = ""
            $priority = "HIGH"
            $escalatedAt = ""

            if ($content -match 'task_id:\s*"([^"]+)"') { $taskId = $Matches[1] }
            if ($content -match 'task_name:\s*"([^"]+)"') { $taskName = $Matches[1] }
            if ($content -match 'priority:\s*"([^"]+)"') { $priority = $Matches[1] }
            if ($content -match 'escalated_at:\s*"([^"]+)"') { $escalatedAt = $Matches[1] }

            $pending += @{
                File = $file.Name
                TaskId = $taskId
                TaskName = $taskName
                Priority = $priority
                EscalatedAt = $escalatedAt
            }
        }
    }
    return $pending
}

function Get-CurrentKiAction {
    $handoffs = Get-ChildItem $HandoffsDir -Filter "*.md" -ErrorAction SilentlyContinue |
                Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($handoffs) {
        $age = [math]::Round(((Get-Date) - $handoffs.LastWriteTime).TotalSeconds)
        $size = $handoffs.Length
        if ($handoffs.Name -match "^(ki\d)_.*?_(\w+)_\d+\.md$") {
            return @{ Ki = $Matches[1].ToUpper(); Phase = $Matches[2]; Age = $age; Size = $size }
        }
    }
    return $null
}

function Get-TokenUsage {
    if (-not (Test-Path $MetricsFile)) { return $null }
    $metrics = Get-Content $MetricsFile -ErrorAction SilentlyContinue |
               ForEach-Object { $_ | ConvertFrom-Json -ErrorAction SilentlyContinue }
    if (-not $metrics) { return $null }

    $latestRun = ($metrics | Select-Object -Last 1).run_id
    $runMetrics = $metrics | Where-Object { $_.run_id -eq $latestRun }

    $totalPrompt = 0; $totalOutput = 0; $phaseCount = 0; $totalDuration = 0
    foreach ($m in $runMetrics) {
        if ($m.prompt_tokens_est) { $totalPrompt += $m.prompt_tokens_est }
        if ($m.output_tokens_est) { $totalOutput += $m.output_tokens_est }
        if ($m.event -eq "PHASE_COMPLETE") {
            $phaseCount++
            if ($m.duration_sec) { $totalDuration += $m.duration_sec }
        }
    }

    $inputCost = ($totalPrompt / 1000000) * 15
    $outputCost = ($totalOutput / 1000000) * 75

    return @{
        PromptTokens = $totalPrompt
        OutputTokens = $totalOutput
        TotalTokens = $totalPrompt + $totalOutput
        PhaseCount = $phaseCount
        TotalDuration = $totalDuration
        EstCost = $inputCost + $outputCost
    }
}

function Get-RecentActivity {
    if (-not (Test-Path $LogFile)) { return @() }
    $lines = Get-Content $LogFile -Tail 30 -ErrorAction SilentlyContinue
    $activity = @()
    foreach ($line in $lines) {
        if ($line -match "\[(SUCCESS|WARNING|ERROR)\]") {
            $activity += $line
        }
    }
    return $activity | Select-Object -Last 6
}

function Show-V4Status {
    Clear-Host
    $ts = Get-Date -Format "HH:mm:ss"

    Write-Host ""
    Write-Host "  ================================================================" -ForegroundColor Cyan
    Write-Host "       V4 AUTONOMOUS LOOP MONITOR  [$ts]" -ForegroundColor Cyan
    Write-Host "  ================================================================" -ForegroundColor Cyan
    Write-Host ""

    # LOOP STATUS
    $status = Get-LoopStatus
    Write-Host "  [LOOP STATUS]" -ForegroundColor Yellow
    if ($status.Running) {
        Write-Host "    Status: " -NoNewline
        Write-Host "RUNNING" -ForegroundColor Green
        if ($status.StartedAt) {
            $runtime = ((Get-Date) - [DateTime]$status.StartedAt)
            Write-Host "    Runtime: $([math]::Floor($runtime.TotalMinutes)) min"
        }
        Write-Host "    Last Activity: $($status.LogAge) sec ago"
    } else {
        Write-Host "    Status: " -NoNewline
        Write-Host "NOT RUNNING" -ForegroundColor Red
    }
    Write-Host ""

    # CURRENT TASK
    $task = Get-CurrentTask
    $kiAction = Get-CurrentKiAction
    Write-Host "  [CURRENT WORK]" -ForegroundColor Yellow
    if ($task) {
        Write-Host "    Task:  $($task.Id)" -ForegroundColor Cyan
        Write-Host "    Name:  $($task.Name)"
        Write-Host "    Phase: " -NoNewline
        switch ($task.Phase) {
            "ARCHITECT" { Write-Host $task.Phase -ForegroundColor Blue }
            "EXECUTOR"  { Write-Host $task.Phase -ForegroundColor Green }
            "VALIDATOR" { Write-Host $task.Phase -ForegroundColor Magenta }
            default     { Write-Host $task.Phase -ForegroundColor Cyan }
        }
    }
    if ($kiAction) {
        $ageStr = "$($kiAction.Age) sec ago"
        $sizeStr = "$($kiAction.Size) bytes"
        Write-Host "    Active: $($kiAction.Ki) doing $($kiAction.Phase) ($ageStr, $sizeStr)" -ForegroundColor DarkGray
    }
    Write-Host ""

    # PROGRESS
    $progress = Get-TaskProgress
    if ($progress) {
        Write-Host "  [PROGRESS]" -ForegroundColor Yellow
        $barWidth = 40
        $filled = [math]::Round(($progress.Percent / 100) * $barWidth)
        $empty = $barWidth - $filled
        $bar = ("=" * $filled) + ("-" * $empty)
        Write-Host "    [$bar] $($progress.Percent)%" -ForegroundColor Green
        Write-Host -NoNewline "    Done: "
        Write-Host -NoNewline "$($progress.Complete)" -ForegroundColor Green
        Write-Host -NoNewline " | Active: "
        Write-Host -NoNewline "$($progress.InProgress)" -ForegroundColor Cyan
        Write-Host -NoNewline " | Pending: "
        Write-Host -NoNewline "$($progress.Pending)" -ForegroundColor Gray
        if ($progress.Escalate -gt 0) {
            Write-Host -NoNewline " | "
            Write-Host -NoNewline "ESCALATE: $($progress.Escalate)" -ForegroundColor Yellow -BackgroundColor DarkRed
        }
        if ($progress.Blocked -gt 0) {
            Write-Host -NoNewline " | Blocked: "
            Write-Host -NoNewline "$($progress.Blocked)" -ForegroundColor Red
        }
        Write-Host ""
        Write-Host ""
    }

    # PENDING ESCALATIONS
    $escalations = Get-PendingEscalations
    if ($escalations.Count -gt 0) {
        Write-Host "  [USER INPUT REQUIRED]" -ForegroundColor Red -BackgroundColor Yellow
        foreach ($esc in $escalations) {
            Write-Host "    Task: " -NoNewline
            Write-Host "$($esc.TaskId)" -ForegroundColor Yellow -NoNewline
            Write-Host " - $($esc.TaskName)"
            Write-Host "    File: " -NoNewline
            Write-Host "AI_COLLABORATION/ESCALATIONS/$($esc.File)" -ForegroundColor Cyan
            Write-Host "    Action: Edit file, set resolution: PROCEED|ABORT|MODIFY, save" -ForegroundColor DarkGray
            Write-Host ""
        }
    }

    # TOKEN USAGE
    $tokens = Get-TokenUsage
    if ($tokens) {
        Write-Host "  [TOKEN USAGE]" -ForegroundColor Yellow
        $promptK = "{0:N1}K" -f ($tokens.PromptTokens / 1000)
        $outputK = "{0:N1}K" -f ($tokens.OutputTokens / 1000)
        $totalK = "{0:N1}K" -f ($tokens.TotalTokens / 1000)
        $costStr = "{0:N3}" -f $tokens.EstCost
        $durMin = "{0:N1}" -f ($tokens.TotalDuration / 60)

        Write-Host "    Prompt: " -NoNewline
        Write-Host $promptK -ForegroundColor Cyan -NoNewline
        Write-Host " | Output: " -NoNewline
        Write-Host $outputK -ForegroundColor Yellow -NoNewline
        Write-Host " | Total: " -NoNewline
        Write-Host $totalK -ForegroundColor Green

        Write-Host "    Phases: $($tokens.PhaseCount) | Duration: $durMin min | Est. Cost: " -NoNewline
        Write-Host "`$$costStr" -ForegroundColor Magenta
        Write-Host ""
    }

    # RECENT ACTIVITY
    $activity = Get-RecentActivity
    if ($activity) {
        Write-Host "  [RECENT ACTIVITY]" -ForegroundColor Yellow
        foreach ($line in $activity) {
            $short = if ($line.Length -gt 75) { $line.Substring(0, 72) + "..." } else { $line }
            if ($line -match "\[SUCCESS\]") {
                Write-Host "    $short" -ForegroundColor Green
            } elseif ($line -match "\[WARNING\]") {
                Write-Host "    $short" -ForegroundColor Yellow
            } elseif ($line -match "\[ERROR\]") {
                Write-Host "    $short" -ForegroundColor Red
            } else {
                Write-Host "    $short" -ForegroundColor Gray
            }
        }
        Write-Host ""
    }

    # Footer
    Write-Host "  ----------------------------------------------------------------" -ForegroundColor DarkGray
    if ($Watch) {
        Write-Host "  Refreshing every $Interval sec | Ctrl+C to stop" -ForegroundColor DarkGray
    } else {
        Write-Host "  Run with -Watch for live updates" -ForegroundColor DarkGray
    }
    Write-Host ""
}

# Main
if ($Watch) {
    while ($true) {
        Show-V4Status
        Start-Sleep -Seconds $Interval
    }
} else {
    Show-V4Status
}
