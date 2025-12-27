<#
.SYNOPSIS
    Autonomous Supervisor Agent - Monitors and fixes V4 Loop issues

.DESCRIPTION
    Runs a Claude agent that:
    1. Reads CLAUDE.md for context
    2. Checks V4 Loop status, external tasks, task registry
    3. Identifies and fixes problems autonomously
    4. Updates status files, fixes scripts, cleans up

.PARAMETER Interval
    Check interval in minutes. Default: 10

.PARAMETER MaxRuns
    Maximum number of supervisor runs. Default: unlimited (0)

.PARAMETER DryRun
    Show what would be done without executing

.EXAMPLE
    .\scripts\supervisor_agent.ps1 -Interval 10

.EXAMPLE
    .\scripts\supervisor_agent.ps1 -Interval 5 -MaxRuns 12  # Run for 1 hour
#>

param(
    [int]$Interval = 10,
    [int]$MaxRuns = 0,
    [switch]$DryRun,
    [string]$Backend = "claude"
)

$ErrorActionPreference = "Stop"
$REPO_ROOT = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $REPO_ROOT

# Supervisor prompt - simplified to avoid CLI parsing issues with dashes
$SUPERVISOR_PROMPT = @"
Du bist der SUPERVISOR AGENT fuer ALLE V4 Autonomous Loops (Alpha UND Beta Team).

DEINE AUFGABEN:
1. Pruefe den aktuellen Status aller laufenden Tasks
2. Erkenne Probleme (stuck tasks, failed tasks, sync issues)
3. Behebe Probleme selbstaendig
4. Aktualisiere Status Dateien und Task Registry

PRUEFE JETZT:
1. Lies AI_COLLABORATION/EXTERNAL_TASKS/task_registry.json
2. Fuer jede aktive Task: Pruefe die .status Datei, ist Heartbeat aktuell?
3. Pruefe ALLE Plan Dateien:
   a) AI_COLLABORATION/PLANS/v4_complete_backlog_plan.yaml (Alpha Team)
   b) AI_COLLABORATION/PLANS/BETA_COMPREHENSIVE_SYSTEM_AUDIT.md (Beta Team, wenn aktiv)
   c) Nutze: ls AI_COLLABORATION/PLANS/*.yaml AI_COLLABORATION/PLANS/*.md
4. Pruefe AI_COLLABORATION/LOOP_STATE/ fuer ALLE laufenden Loops
5. Lies .log und .err Dateien bei Problemen

MULTI LOOP AWARENESS:
Es koennen parallel laufen:
Alpha Team: v4_complete_backlog_plan.yaml (ISSUE Tasks)
Beta Team: BETA_COMPREHENSIVE_SYSTEM_AUDIT.md (Audit Tasks)
Pruefe beide unabhaengig und reporte Status fuer jeden Loop separat.

WICHTIG BEI FAILED TASKS: VERIFIZIERE TATSAECHLICHE OUTPUTS!
Status Dateien koennen veraltet sein. Pruefe immer das Dateisystem:
1. Existiert das Output Verzeichnis? (z.B. best_rules_weak_remined_v1)
2. Zaehle tatsaechliche Output Dateien mit find oder ls
3. Pruefe Timestamps der Dateien (nach Task Start erstellt?)
4. Bei Diskrepanz zwischen Status FAILED und vorhandenen Outputs:
   Der Task war ERFOLGREICH, korrigiere den Status auf COMPLETE

Beispiel Verifikation fuer Mining Tasks:
  ls team_mining_module/best_rules_*/
  find team_mining_module/best_rules_* -name *.json | wc -l
  Wenn Dateien existieren und Timestamp nach Task Start: COMPLETE

BEI PROBLEMEN:
Stuck Task mit altem Heartbeat: Aktualisiere Heartbeat
Failed Task ohne Outputs: Verschiebe zu completed_tasks
Failed Task MIT Outputs: Korrigiere Status zu COMPLETE
Plan Registry Mismatch: Synchronisiere die Dateien

Handle SELBSTAENDIG. Dokumentiere alle Aenderungen.
"@

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logLine = "[$timestamp] [$Level] $Message"
    Write-Host $logLine -ForegroundColor $(
        switch ($Level) {
            "ERROR" { "Red" }
            "WARN"  { "Yellow" }
            "SUCCESS" { "Green" }
            default { "White" }
        }
    )

    # Append to supervisor log
    $logFile = Join-Path $REPO_ROOT "AI_COLLABORATION/LOGS/supervisor_agent.log"
    $logDir = Split-Path -Parent $logFile
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    Add-Content -Path $logFile -Value $logLine -Encoding UTF8
}

function Invoke-SupervisorCheck {
    param([int]$RunNumber)

    Write-Log "=== SUPERVISOR RUN #$RunNumber ===" "INFO"

    # Create temp file for the prompt
    $promptFile = Join-Path $env:TEMP "supervisor_prompt_$RunNumber.txt"
    $SUPERVISOR_PROMPT | Set-Content -Path $promptFile -Encoding UTF8

    # Check which backend to use
    $claudeCmd = Get-Command "claude.cmd" -ErrorAction SilentlyContinue
    $claudeExe = Get-Command "claude" -ErrorAction SilentlyContinue

    if ($claudeCmd) {
        $executable = "claude.cmd"
    } elseif ($claudeExe) {
        $executable = "claude"
    } else {
        Write-Log "Claude CLI not found. Install with: npm install -g @anthropic-ai/claude-code" "ERROR"
        return $false
    }

    if ($DryRun) {
        Write-Log "[DRY RUN] Would execute: $executable with supervisor prompt" "WARN"
        Write-Log "Prompt: $SUPERVISOR_PROMPT" "INFO"
        return $true
    }

    try {
        Write-Log "Starting Claude supervisor agent..." "INFO"

        # Run claude with the simplified supervisor prompt as direct argument
        # The prompt is simplified to avoid CLI parsing issues with dashes
        $result = & $executable -p $SUPERVISOR_PROMPT --dangerously-skip-permissions 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Log "Supervisor check completed successfully" "SUCCESS"

            # Log the agent's response (truncated)
            $responsePreview = if ($result.Length -gt 500) { $result.Substring(0, 500) + "..." } else { $result }
            Write-Log "Agent response: $responsePreview" "INFO"

            return $true
        } else {
            Write-Log "Supervisor check failed with exit code $LASTEXITCODE" "ERROR"
            Write-Log "Output: $result" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Exception during supervisor check: $_" "ERROR"
        return $false
    }
    finally {
        # Cleanup temp file
        if (Test-Path $promptFile) {
            Remove-Item $promptFile -Force -ErrorAction SilentlyContinue
        }
    }
}

# Main loop
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SUPERVISOR AGENT - Autonomous Monitor" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Interval:    $Interval minutes"
Write-Host "Max Runs:    $(if ($MaxRuns -eq 0) { 'Unlimited' } else { $MaxRuns })"
Write-Host "Backend:     $Backend"
Write-Host "Repo Root:   $REPO_ROOT"
Write-Host ""

if ($DryRun) {
    Write-Host "[DRY RUN MODE - No changes will be made]" -ForegroundColor Yellow
    Write-Host ""
}

Write-Log "Supervisor Agent started" "INFO"

$runCount = 0
$successCount = 0
$failCount = 0

while ($true) {
    $runCount++

    # Check if we've reached max runs
    if ($MaxRuns -gt 0 -and $runCount -gt $MaxRuns) {
        Write-Log "Reached maximum runs ($MaxRuns). Stopping." "INFO"
        break
    }

    # Run supervisor check
    $success = Invoke-SupervisorCheck -RunNumber $runCount

    if ($success) {
        $successCount++
    } else {
        $failCount++
    }

    # Status summary
    Write-Host ""
    Write-Host "Run $runCount complete. Success: $successCount, Failed: $failCount" -ForegroundColor Gray
    $nextCheck = (Get-Date).AddMinutes($Interval).ToString('HH:mm:ss')
    Write-Host "Next check in $Interval minutes ($nextCheck)" -ForegroundColor Gray
    Write-Host ""

    # Wait for next interval
    Start-Sleep -Seconds ($Interval * 60)
}

Write-Log "Supervisor Agent stopped. Total runs: $runCount, Success: $successCount, Failed: $failCount" "INFO"
