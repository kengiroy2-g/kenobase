# ============================================================================
# AUTONOMOUS LOOP V4: Plan-Based Execution + Quality Gates (Production)
# ============================================================================
#
# Erweiterung von V2 mit:
#   1. PLAN-BASED: Folgt festem Plan statt ad-hoc Messages
#   2. PHASE WORKFLOW: Architect -> Proxy -> Executor -> Proxy -> Validator -> Proxy
#   3. COMPLETION DETECTION: Automatische Erkennung von Task-Completion
#   4. QUALITY GATES: KI #0 prueft zwischen jeder Phase
#
# Behaelt alle V2 Features:
#   - Budget Management
#   - Per-KI Backend/Model Selection
#   - Lease Management
#   - Garbage Detection
#   - Value Contract Checks
#
# Usage:
#   .\scripts\autonomous_loop_v4.ps1 -Help
#   .\scripts\autonomous_loop_v4.ps1 -Team alpha -PlanFile "AI_COLLABORATION/PLANS/current_plan.yaml"
#
# ============================================================================

param(
    # === V4 NEW PARAMETERS ===
    [string]$PlanFile = "AI_COLLABORATION/PLANS/current_plan.yaml",
    [ValidateSet("alpha", "beta")]
    [string]$Team = "alpha",
    [int]$CompletionCheckInterval = 60,    # Sekunden zwischen Completion-Checks
    [int]$MaxPhaseTimeMinutes = 120,       # Max Zeit pro Phase (erhoeht auf 120 min 2025-12-25)
    [int]$MaxProxyTimeMinutes = 30,        # Max Zeit fuer Proxy-Checks (erhoeht 2025-12-25)
    [switch]$SkipProxy,                    # Proxy-Checks ueberspringen (schneller, weniger sicher)

    # === V4 EFFICIENCY PARAMETERS (Token Hygiene) ===
    [switch]$EnableLightContext,          # Use lightweight context (~1K tokens vs ~10K)
    [string]$LightContextPath = "AI_COLLABORATION/PLANS/loop_context.md",
    [int]$MaxPromptChars = 60000,
    [int]$SoftPromptChars = 45000,
    [int]$MaxPrevContextChars = 2500,
    [int]$MaxNotesChars = 2000,
    [bool]$EnableHandoffValidation = $false,  # Disabled for long-run stability
    [int]$MaxInvalidHandoffRetries = 3,
    [string[]]$HandoffPlaceholderPatterns = @(
        "<command>",
        "<output path>",
        "\.\.\.",
        "\bTBD\b",
        "\bTODO\b",
        'python\s+-c\s+"\.{3}"',
        "python\s+-c\s+'\.{3}'"
    ),
    [int]$WorkingSetMaxFiles = 8,

    # === V4 WORKING SET GUARD (Deterministic Token Control) ===
    [switch]$EnableWorkingSetGuard = $true,
    [int]$GuardMaxReadBytesProxy = 200000,
    [int]$GuardMaxReadBytesExecutor = 800000,
    [int]$MaxWorkingSetRequestRounds = 3,
    [int]$MaxWorkingSetRequestFiles = 6,
    [string[]]$GuardHardBlockPatterns = @("current_status", "knowledgebase", "CLAUDE.md"),
    [string[]]$GuardHardBlockPaths = @("AI_COLLABORATION/MESSAGE_QUEUE", "AI_COLLABORATION/LOCKS"),
    [switch]$EnableAutoCompact = $true,
    [string]$MemoryDir = "AI_COLLABORATION/MEMORY",
    [string]$ArtifactsDir = "AI_COLLABORATION/ARTIFACTS",
    [bool]$EnableMetrics = $true,
    [string]$MetricsPath = "AI_COLLABORATION/METRICS/loop_v4_metrics.jsonl",
    [string]$MetricsSummaryPath = "AI_COLLABORATION/METRICS/loop_v4_summary.json",

    # === V2 PARAMETERS (alle beibehalten) ===
    [int]$CheckIntervalSeconds = 10,
    [int]$MaxConcurrent = 1,
    [int]$MaxRetries = 3,
    [int]$LeaseMinutes = 45,
    [int]$MaxRunMinutes = 0,  # 0 = unlimited for long-run
    [int]$OutboxGraceSeconds = 30,
    [int]$RequeueStaleClaimsMinutes = 30,
    [int]$IdleExitMinutes = 0,
    [int[]]$SwitchBackendOnExitCodes = @(-1, 1),
    [int]$SwitchBackendExitCooldownMinutes = 10,
    [int]$SwitchBackendRequeueDelaySeconds = 10,
    [switch]$DryRun,
    [int]$MaxIterations = 0,  # 0 = unlimited for long-run
    [switch]$Verbose,
    [switch]$AllowMultiInstance,
    [bool]$EnableProxy = $true,
    [ValidateSet("claude", "codex")]
    [string]$DefaultBackend = "claude",
    [string]$KiBackends = "ki0=claude,ki1=claude,ki2=claude,ki3=claude",
    [string]$ClaudePath = "claude.cmd",
    [string]$ClaudeModel = "opus",
    [int]$ClaudeMaxTurns = 0,
    [string]$KiModels = "",
    [string]$CodexPath = "codex",
    [string]$CodexModel = "gpt-5.1-codex-max",
    # Backward compatible knob used in project docs as "low|medium|high" for reasoning effort.
    # NOTE: This is NOT the same as Codex CLI `--profile` (which refers to config.toml profiles).
    [string]$CodexProfile = "high",
    [ValidateSet("low", "medium", "high")]
    [string]$CodexReasoningEffort = "medium",
    [ValidateSet("full", "limited", "readonly")]
    [string]$CodexAgentMode = "full",
    [switch]$NoFallback,
    [ValidateSet("off", "report", "enforce")]
    [string]$BudgetMode = "report",
    [string]$BudgetPath = "AI_COLLABORATION/MESSAGE_QUEUE/usage_budget.json",
    [int]$BudgetWindowHours = 5,
    [int]$CodexBudgetLimit = 150,
    [int]$ClaudeBudgetLimit = 300,
    [double]$BudgetWarnPercent = 0.65,
    [double]$BudgetSoftPercent = 0.95,
    [double]$BudgetHardPercent = 0.98,
    [int]$BudgetDeferMinutes = 15,
    [bool]$BudgetPauseOnHard = $true,
    [ValidateRange(0,100)]
    [int]$InitialSessionUsedPercent = 0,
    [ValidateRange(0,100)]
    [int]$InitialWeeklyUsedPercent = 0,
    [ValidateRange(0.1,10)]
    [double]$EstimatedPercentPerTask = 1.0,
    [ValidateRange(1,100)]
    [double]$RecoveryPercentPerHour = 20.0,
    [string]$RunRegistryPath = "AI_COLLABORATION/LOGS/run_registry.jsonl",
    [int]$HealthCheckIntervalMinutes = 10,
    [string]$LoopStatePath = "AI_COLLABORATION/MESSAGE_QUEUE/loop_state.json",
    [bool]$EnableGarbageDetection = $true,
    [bool]$EnableValueContractCheck = $true,
    [switch]$Help
)

$ErrorActionPreference = "Stop"
$script:ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$script:ProjectRoot = Split-Path -Parent $script:ScriptRoot
$script:VerboseEnabled = [bool]$Verbose

# Error Handling Variables
$script:MaxPhaseRetries = 3
$script:PhaseRetryCount = 0

# ============================================================================
# HELP
# ============================================================================

function Show-Help {
    Write-Host ""
    Write-Host "AUTONOMOUS LOOP V4 - Plan-Based Execution + Quality Gates (Production)" -ForegroundColor Cyan
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "V4 FEATURES:" -ForegroundColor Yellow
    Write-Host "  - Plan-Based Execution (folgt YAML-Plan)"
    Write-Host "  - Phase Workflow: Architect -> Proxy -> Executor -> Proxy -> Validator"
    Write-Host "  - Automatic Completion Detection (alle 60s)"
    Write-Host "  - KI #0 Quality Gates zwischen Phasen"
    Write-Host ""
    Write-Host "V4 PARAMETERS:" -ForegroundColor Yellow
    Write-Host "  -PlanFile                 Plan-YAML Pfad (default: AI_COLLABORATION/PLANS/current_plan.yaml)"
    Write-Host "  -Team                     alpha (KI 1-3) oder beta (KI 5-7)"
    Write-Host "  -CompletionCheckInterval  Sekunden zwischen Completion-Checks (default: 60)"
    Write-Host "  -MaxPhaseTimeMinutes      Max Zeit pro Phase (default: 30)"
    Write-Host "  -MaxProxyTimeMinutes      Max Zeit fuer Proxy-Checks (default: 30)"
    Write-Host "  -SkipProxy                Proxy-Checks ueberspringen"
    Write-Host ""
    Write-Host "TOKEN OPTIMIZATION:" -ForegroundColor Yellow
    Write-Host "  -EnableLightContext       88% Token-Reduktion (~1K statt ~10K Tokens)"
    Write-Host "                            Generiert leichten Context aus Plan + CLAUDE.md"
    Write-Host "                            KIs behalten vollen Zugriff via Read/Grep/Glob"
    Write-Host "  -LightContextPath         Pfad fuer generierten Context (default: AI_COLLABORATION/PLANS/loop_context.md)"
    Write-Host ""
    Write-Host "WORKFLOW:" -ForegroundColor Yellow
    Write-Host "  1. ARCHITECT (KI #1/5)  - Erstellt Implementierungsplan"
    Write-Host "  2. PROXY (KI #0)        - Prueft Plan-Qualitaet"
    Write-Host "  3. EXECUTOR (KI #2/6)   - Fuehrt Plan aus"
    Write-Host "  4. PROXY (KI #0)        - Prueft Implementation"
    Write-Host "  5. VALIDATOR (KI #3/7)  - Validiert Ergebnis"
    Write-Host "  6. PROXY (KI #0)        - Finale Freigabe"
    Write-Host ""
    Write-Host "BEISPIELE:" -ForegroundColor Yellow
    Write-Host "  # Standard-Start mit Alpha-Team:"
    Write-Host "  .\scripts\autonomous_loop_v4.ps1 -Team alpha"
    Write-Host ""
    Write-Host "  # Beta-Team, ohne Proxy (schneller):"
    Write-Host "  .\scripts\autonomous_loop_v4.ps1 -Team beta -SkipProxy"
    Write-Host ""
    Write-Host "  # Custom Plan:"
    Write-Host "  .\scripts\autonomous_loop_v4.ps1 -PlanFile 'AI_COLLABORATION/PLANS/adr020_plan.yaml'"
    Write-Host ""
    Write-Host "  # Mit Token-Optimierung (88% weniger Tokens):"
    Write-Host "  .\scripts\autonomous_loop_v4.ps1 -EnableLightContext"
    Write-Host ""
    Write-Host "PLAN FORMAT (YAML):" -ForegroundColor Yellow
    Write-Host @"
  plan:
    name: "My Plan"
  tasks:
    - id: task_001
      name: "Task Description"
      priority: P1
      status: PENDING
      current_phase: null
"@
    Write-Host ""
    exit 0
}

if ($Help) { Show-Help }

# ============================================================================
# LOGGING
# ============================================================================

$script:LogFile = Join-Path $script:ProjectRoot "AI_COLLABORATION/LOGS/loop_v4.log"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "ERROR"   { "Red" }
        "WARNING" { "Yellow" }
        "SUCCESS" { "Green" }
        "DEBUG"   { "DarkGray" }
        default   { "White" }
    }

    if ($Level -ne "DEBUG" -or $script:VerboseEnabled) {
        Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
    }

    $logDir = Split-Path $script:LogFile -Parent
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
    Add-Content -Path $script:LogFile -Value "[$timestamp] [$Level] $Message" -ErrorAction SilentlyContinue
}

# ============================================================================
# BACKEND SWITCHING + RATE LIMIT COOLDOWNS (ported from V2)
# ============================================================================

$script:BackendStatusPath = Join-Path $script:ProjectRoot "AI_COLLABORATION/MESSAGE_QUEUE/backend_status_v4.json"
$script:BackendStatus = $null
$script:ProcessMeta = @{}
$script:WorkingSetRequestCounts = @{}
$script:InvalidHandoffCounts = @{}

function Initialize-BackendStatus {
    if ($script:BackendStatus) { return }

    $dir = Split-Path $script:BackendStatusPath -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }

    if (-not (Test-Path $script:BackendStatusPath)) {
        $script:BackendStatus = @{
            codex  = @{ limited = $false; limited_until = $null; reason = $null; last_limited_at = $null }
            claude = @{ limited = $false; limited_until = $null; reason = $null; last_limited_at = $null }
        }
        Save-BackendStatus
        return
    }

    try {
        $raw = Get-Content $script:BackendStatusPath -Raw -ErrorAction SilentlyContinue
        $data = if ($raw) { $raw | ConvertFrom-Json -ErrorAction Stop } else { $null }
        if ($data) {
            $script:BackendStatus = @{
                codex  = @{ limited = [bool]$data.codex.limited; limited_until = $data.codex.limited_until; reason = $data.codex.reason; last_limited_at = $data.codex.last_limited_at }
                claude = @{ limited = [bool]$data.claude.limited; limited_until = $data.claude.limited_until; reason = $data.claude.reason; last_limited_at = $data.claude.last_limited_at }
            }
        } else {
            $script:BackendStatus = @{
                codex  = @{ limited = $false; limited_until = $null; reason = $null; last_limited_at = $null }
                claude = @{ limited = $false; limited_until = $null; reason = $null; last_limited_at = $null }
            }
        }
    } catch {
        $script:BackendStatus = @{
            codex  = @{ limited = $false; limited_until = $null; reason = $null; last_limited_at = $null }
            claude = @{ limited = $false; limited_until = $null; reason = $null; last_limited_at = $null }
        }
    }
}

function Save-BackendStatus {
    if (-not $script:BackendStatus) { return }
    $dir = Split-Path $script:BackendStatusPath -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    try {
        $script:BackendStatus | ConvertTo-Json -Depth 6 | Set-Content -Path $script:BackendStatusPath -Encoding UTF8
    } catch { }
}

function Get-BackendLimitedUntil {
    param([ValidateSet("claude", "codex")] [string]$Backend)
    Initialize-BackendStatus
    $entry = $script:BackendStatus[$Backend]
    if (-not $entry -or $entry.limited -ne $true -or -not $entry.limited_until) { return $null }
    try { return [datetime]$entry.limited_until } catch { return $null }
}

function Test-BackendAvailable {
    param([ValidateSet("claude", "codex")] [string]$Backend)
    Initialize-BackendStatus

    $until = Get-BackendLimitedUntil -Backend $Backend
    if (-not $until) { return $true }

    if ($until -le (Get-Date)) {
        $script:BackendStatus[$Backend].limited = $false
        $script:BackendStatus[$Backend].limited_until = $null
        $script:BackendStatus[$Backend].reason = $null
        Save-BackendStatus
        Write-Log "Auto-cleared expired backend cooldown for $Backend" "INFO"
        return $true
    }

    return $false
}

function Set-BackendLimited {
    param(
        [ValidateSet("claude", "codex")] [string]$Backend,
        [datetime]$Until,
        [string]$Reason
    )

    if (-not $Until) { return }
    Initialize-BackendStatus

    $script:BackendStatus[$Backend].limited = $true
    $script:BackendStatus[$Backend].limited_until = $Until.ToString("o")
    $script:BackendStatus[$Backend].reason = $Reason
    $script:BackendStatus[$Backend].last_limited_at = (Get-Date -Format "o")
    Save-BackendStatus

    Write-Log "Backend LIMITED: $Backend until $($Until.ToString('yyyy-MM-dd HH:mm:ss')) ($Reason)" "WARNING"
}

function Get-FilePreview {
    param([string]$Path, [int]$MaxChars = 6000)

    if (-not $Path -or -not (Test-Path $Path)) { return "" }
    try {
        $text = Get-Content $Path -Raw -ErrorAction SilentlyContinue
        if (-not $text) { return "" }
        $text = $text.TrimEnd()
        if ($text.Length -le $MaxChars) { return $text }

        $half = [Math]::Floor($MaxChars / 2)
        $head = $text.Substring(0, $half)
        $tail = $text.Substring($text.Length - $half)
        return ($head + "`n... (truncated) ...`n" + $tail)
    } catch {
        return ""
    }
}

# ============================================================================
# CLI PATH RESOLUTION
# ============================================================================

function Resolve-ClaudePath {
    param([string]$Candidate)

    if ($Candidate) {
        try {
            if (Test-Path $Candidate) { return (Resolve-Path $Candidate).Path }
        } catch { }

        try {
            $cmd = Get-Command $Candidate -ErrorAction SilentlyContinue
            if ($cmd) { return $cmd.Source }
        } catch { }
    }

    $fallbacks = @("claude.exe", "claude.cmd", "claude")
    foreach ($name in $fallbacks) {
        try {
            $cmd = Get-Command $name -ErrorAction SilentlyContinue
            if ($cmd) { return $cmd.Source }
        } catch { }
    }

    if ($env:USERPROFILE) {
        $local = Join-Path $env:USERPROFILE ".local\\bin\\claude.exe"
        if (Test-Path $local) { return $local }
    }

    return $null
}

function Estimate-Tokens {
    param([int]$Chars)
    if ($Chars -le 0) { return 0 }
    return [int][Math]::Ceiling($Chars / 4.0)
}

function Initialize-Metrics {
    param([string]$PlanName)

    if (-not $EnableMetrics) { return }

    $ts = Get-Date -Format "yyyyMMdd_HHmmss"
    $script:RunId = "loop_v4_${ts}_$PID"
    $script:MetricsPath = Join-Path $script:ProjectRoot $MetricsPath
    $script:MetricsSummaryPath = Join-Path $script:ProjectRoot $MetricsSummaryPath
    Ensure-Dir -Path (Split-Path $script:MetricsPath -Parent)

    $script:MetricsSummary = @{
        run_id = $script:RunId
        plan_file = $PlanFile
        plan_name = $PlanName
        team = $Team
        start_time = (Get-Date -Format "o")
        default_backend = $DefaultBackend
        backend_map = $script:KiBackendMap
        codex_model = $CodexModel
        claude_path = $ClaudePath
        phases_started = 0
        phases_completed = 0
        phases_blocked = 0
        phases_approved = 0
        phases_failed = 0
        rate_limit_events = 0
        backend_switches = 0
        auto_compact_events = 0
        prompt_chars_total = 0
        prompt_tokens_est_total = 0
        output_chars_total = 0
        output_tokens_est_total = 0
        files_changed_total = 0
        summary_items_total = 0
        duration_sec_total = 0
    }

    Write-MetricsEvent -Event "RUN_START" -Data @{
        plan_name = $PlanName
        plan_file = $PlanFile
        team = $Team
        backend_map = $script:KiBackendMap
        codex_model = $CodexModel
        claude_path = $ClaudePath
    }
    Write-MetricsSummary
}

function Write-MetricsSummary {
    if (-not $EnableMetrics -or -not $script:MetricsSummaryPath) { return }
    try {
        ($script:MetricsSummary | ConvertTo-Json -Depth 6) | Set-Content $script:MetricsSummaryPath -Encoding UTF8
    } catch { }
}

function Write-MetricsEvent {
    param([string]$Event, [hashtable]$Data)

    if (-not $EnableMetrics -or -not $script:MetricsPath -or -not $script:RunId) { return }

    $payload = @{
        timestamp = (Get-Date -Format "o")
        run_id = $script:RunId
        event = $Event
    }

    if ($Data) {
        foreach ($k in $Data.Keys) {
            $payload[$k] = $Data[$k]
        }
    }

    try {
        $json = $payload | ConvertTo-Json -Depth 6 -Compress
        Add-Content -Path $script:MetricsPath -Value $json
    } catch { }
}

function Get-QualitySignals {
    param([string]$Content)

    $summaryCount = 0
    $filesCount = 0
    $status = ""

    if ($Content) {
        $fm = Get-HandoffFrontmatter -Content $Content
        if ($fm) {
            $status = $fm.status
            if ($fm.summary) { $summaryCount = $fm.summary.Count }
            if ($fm.files_changed) { $filesCount = $fm.files_changed.Count }
        }

        if ($summaryCount -eq 0) {
            $summaryCount = (Get-MarkdownSummaryBullets -Content $Content).Count
        }
    }

    $outputChars = if ($Content) { $Content.Length } else { 0 }
    return @{
        status = $status
        summary_items = $summaryCount
        files_changed = $filesCount
        output_chars = $outputChars
        output_tokens_est = (Estimate-Tokens -Chars $outputChars)
    }
}

function Record-PhaseStart {
    param(
        [string]$TaskId,
        [string]$TaskName,
        [string]$Phase,
        [string]$KI,
        [string]$Backend,
        [int]$PromptChars,
        [int]$PromptCharsRaw,
        [int]$PromptTokensEst,
        [bool]$AutoCompactUsed,
        [int]$RetryCount
    )

    if (-not $EnableMetrics) { return }

    $script:CurrentPhaseMetrics = @{
        task_id = $TaskId
        task_name = $TaskName
        phase = $Phase
        ki = $KI
        backend = $Backend
        prompt_chars = $PromptChars
        prompt_chars_raw = $PromptCharsRaw
        prompt_tokens_est = $PromptTokensEst
        auto_compact_used = $AutoCompactUsed
        retry_count = $RetryCount
        phase_start = (Get-Date -Format "o")
    }

    $script:MetricsSummary.phases_started++
    $script:MetricsSummary.prompt_chars_total += $PromptChars
    $script:MetricsSummary.prompt_tokens_est_total += $PromptTokensEst
    if ($AutoCompactUsed) { $script:MetricsSummary.auto_compact_events++ }

    Write-MetricsEvent -Event "PHASE_START" -Data $script:CurrentPhaseMetrics
    Write-MetricsSummary
}

function Record-PhaseComplete {
    param(
        [hashtable]$Completion,
        [datetime]$PhaseStartTime,
        [hashtable]$PhaseMetrics
    )

    if (-not $EnableMetrics -or -not $Completion) { return }

    if (-not $PhaseMetrics) {
        $PhaseMetrics = @{
            task_id = $Completion.task_id
            phase = ""
            ki = ""
            backend = ""
            prompt_chars = 0
            prompt_tokens_est = 0
            auto_compact_used = $false
        }
    }

    if (-not $Completion.task_id) { $Completion.task_id = $PhaseMetrics.task_id }

    $durationSec = 0
    if ($PhaseStartTime -and $PhaseStartTime -ne [datetime]::MinValue) {
        $durationSec = [int]([math]::Round(((Get-Date) - $PhaseStartTime).TotalSeconds))
    }

    $quality = Get-QualitySignals -Content $Completion.content
    $status = $Completion.status
    $data = @{
        task_id = $Completion.task_id
        phase = $PhaseMetrics.phase
        ki = $PhaseMetrics.ki
        backend = $PhaseMetrics.backend
        status = $status
        duration_sec = $durationSec
        prompt_chars = $PhaseMetrics.prompt_chars
        prompt_tokens_est = $PhaseMetrics.prompt_tokens_est
        output_chars = $quality.output_chars
        output_tokens_est = $quality.output_tokens_est
        files_changed_count = $quality.files_changed
        summary_items_count = $quality.summary_items
        auto_compact_used = $PhaseMetrics.auto_compact_used
    }

    Write-MetricsEvent -Event "PHASE_COMPLETE" -Data $data

    $script:MetricsSummary.phases_completed++
    if ($status -eq "APPROVED") { $script:MetricsSummary.phases_approved++ }
    elseif ($status -eq "BLOCKED" -or $status -eq "REJECTED") { $script:MetricsSummary.phases_blocked++ }
    $script:MetricsSummary.output_chars_total += $quality.output_chars
    $script:MetricsSummary.output_tokens_est_total += $quality.output_tokens_est
    $script:MetricsSummary.files_changed_total += $quality.files_changed
    $script:MetricsSummary.summary_items_total += $quality.summary_items
    $script:MetricsSummary.duration_sec_total += $durationSec

    Write-MetricsSummary
}

function Get-NextResetAtLocalTime {
    param([int]$Hour, [int]$Minute = 0)
    $now = Get-Date
    $candidate = Get-Date -Year $now.Year -Month $now.Month -Day $now.Day -Hour $Hour -Minute $Minute -Second 0
    if ($candidate -le $now) { $candidate = $candidate.AddDays(1) }
    return $candidate.AddMinutes(2) # buffer
}

function Parse-RateLimitUntil {
    param([ValidateSet("claude", "codex")] [string]$Backend, [string]$Text)

    $now = Get-Date
    if (-not $Text) { return $now.AddMinutes([int]$SwitchBackendExitCooldownMinutes) }

    # "Retry after 120s"
    if ($Text -match '(?i)retry[- ]after\s+(\d+)\s*s') {
        return $now.AddSeconds([int]$Matches[1] + 5)
    }

    # "Resets at 02:00"
    if ($Text -match '(?i)resets?\s+(?:at\s+)?(\d{1,2}):(\d{2})') {
        return Get-NextResetAtLocalTime -Hour ([int]$Matches[1]) -Minute ([int]$Matches[2])
    }

    return $now.AddMinutes([int]$SwitchBackendExitCooldownMinutes)
}

function Detect-RateLimitInfo {
    param(
        [ValidateSet("claude", "codex")] [string]$Backend,
        [string]$StdoutPath,
        [string]$StderrPath
    )

    $stdout = Get-FilePreview -Path $StdoutPath -MaxChars 6000
    $stderr = Get-FilePreview -Path $StderrPath -MaxChars 6000
    $combined = (($stderr + "`n" + $stdout).Trim())
    if (-not $combined) { return @{ is_rate_limit = $false } }

    $hay = $combined.ToLowerInvariant()
    $isRateLimit =
        ($hay -match 'rate limit') -or
        ($hay -match 'limit reached') -or
        ($hay -match 'hit your limit') -or
        ($hay -match "you've hit your limit") -or
        ($hay -match 'too many requests') -or
        ($hay -match '\b429\b') -or
        ($hay -match 'quota') -or
        ($hay -match 'resets \d') -or
        ($hay -match 'try again later')

    if (-not $isRateLimit) { return @{ is_rate_limit = $false } }

    $until = Parse-RateLimitUntil -Backend $Backend -Text $combined
    $reason = if ($combined.Length -gt 200) { $combined.Substring(0, 200) } else { $combined }
    $reason = $reason.Replace("`r", " ").Replace("`n", " ").Trim()

    return @{ is_rate_limit = $true; until = $until; reason = $reason }
}

function Resolve-BackendForKI {
    param([string]$KI)

    $preferred = Get-KiBackend -Ki $KI
    $order = if ($NoFallback) { @($preferred) } else { @($preferred, $(if ($preferred -eq "codex") { "claude" } else { "codex" })) }

    $bestUntil = $null
    $deny = @()

    foreach ($b in $order) {
        if (Test-BackendAvailable -Backend $b) {
            return [PSCustomObject]@{ allow = $true; backend = $b; defer_until = $null; deny_reasons = @() }
        }
        $until = Get-BackendLimitedUntil -Backend $b
        if ($until) {
            if (-not $bestUntil -or $until -lt $bestUntil) { $bestUntil = $until }
            $deny += ("limited:{0}" -f $b)
        } else {
            $deny += ("unavailable:{0}" -f $b)
        }
    }

    if (-not $bestUntil) { $bestUntil = (Get-Date).AddMinutes([int]$SwitchBackendExitCooldownMinutes) }
    return [PSCustomObject]@{ allow = $false; backend = $null; defer_until = $bestUntil; deny_reasons = @($deny) }
}

# ============================================================================
# V4 EFFICIENCY HELPERS (Token Hygiene)
# ============================================================================

function Ensure-Dir {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Normalize-YamlScalar {
    param([string]$Value)

    if ($null -eq $Value) { return "" }

    $v = $Value.Trim()

    # Strip inline comments (best-effort) if not quoted
    if (-not ($v.StartsWith('"') -or $v.StartsWith("'"))) {
        $hash = $v.IndexOf('#')
        if ($hash -ge 0) {
            $v = $v.Substring(0, $hash).Trim()
        }
    }

    # Strip surrounding quotes
    if (($v.StartsWith('"') -and $v.EndsWith('"')) -or ($v.StartsWith("'") -and $v.EndsWith("'"))) {
        if ($v.Length -ge 2) { $v = $v.Substring(1, $v.Length - 2) }
    }

    return $v.Trim()
}

function Sanitize-FileNameComponent {
    param([string]$Value)

    $v = Normalize-YamlScalar -Value $Value
    if (-not $v) { return "" }

    $invalid = [System.IO.Path]::GetInvalidFileNameChars() + [System.IO.Path]::GetInvalidPathChars()
    $pattern = '[' + ([regex]::Escape(($invalid -join ''))) + ']'
    $v = [regex]::Replace($v, $pattern, '_')

    # Extra hardening against accidental quoting/backticks
    $v = $v.Replace('`', '_').Replace('"', '_').Replace("'", '_')

    # Collapse repeats and trim
    $v = [regex]::Replace($v, '_{2,}', '_').Trim('_', ' ')

    # Keep filenames reasonable
    if ($v.Length -gt 120) { $v = $v.Substring(0, 120) }

    return $v
}

function Get-HandoffFrontmatter {
    param([string]$Content)

    if (-not $Content) { return $null }

    $c = $Content
    # Strip UTF-8 BOM if present
    if ($c.Length -gt 0 -and [int]$c[0] -eq 0xFEFF) { $c = $c.Substring(1) }

    $m = [regex]::Match($c, "(?s)^\s*---\s*(.*?)\s*---")
    if (-not $m.Success) {
        # Some handoffs accidentally start with whitespace/newlines; be tolerant.
        $m = [regex]::Match($c, "(?s)\A.*?\n\s*---\s*(.*?)\s*---")
    }
    if (-not $m.Success) { return $null }

    $yaml = $m.Groups[1].Value

    # Minimalparser: summary/files/status/task_id (regex-basiert)
    $status = if ($yaml -match "(?m)^status:\s*(\S+)") { $Matches[1] } else { "" }
    $taskId = if ($yaml -match "(?m)^task_id:\s*(\S+)") { $Matches[1] } else { "" }

    $summary = @()
    if ($yaml -match "(?s)summary:\s*(.*?)(?=\n\w+:|$)") {
        $summaryBlock = $Matches[1]
        foreach ($m in [regex]::Matches($summaryBlock, "(?m)^\s*-\s*[`"']?(.*?)[`"']?\s*$")) {
            $summary += $m.Groups[1].Value.Trim()
        }
    }

    $filesChanged = @()
    if ($yaml -match "(?s)files_changed:\s*(.*?)(?=\n\w+:|$)") {
        $filesBlock = $Matches[1]
        foreach ($m in [regex]::Matches($filesBlock, "(?m)^\s*-\s*[`"']?(.*?)[`"']?\s*$")) {
            $filesChanged += $m.Groups[1].Value.Trim()
        }
    }

    return @{
        status = $status
        task_id = $taskId
        raw = $yaml
        summary = $summary
        files_changed = $filesChanged
    }
}

function Get-HandoffMeta {
    param([string]$Content)

    $meta = @{
        status = ""
        task = ""
        phase = ""
        role = ""
    }

    if (-not $Content) { return $meta }

    if ($Content -match "(?m)^status:\s*(\S+)") { $meta.status = $Matches[1] }
    if ($Content -match "(?m)^task:\s*(\S+)") { $meta.task = $Matches[1] }
    elseif ($Content -match "(?m)^task_id:\s*(\S+)") { $meta.task = $Matches[1] }
    if ($Content -match "(?m)^phase:\s*(\S+)") { $meta.phase = $Matches[1] }
    if ($Content -match "(?m)^role:\s*(\S+)") { $meta.role = $Matches[1] }

    return $meta
}

function Get-SectionBlock {
    param(
        [string]$Content,
        [string]$Heading
    )

    if (-not $Content -or -not $Heading) { return "" }
    $escaped = [regex]::Escape($Heading)
    $pattern = "(?ms)^\s*$escaped\s*\r?\n(.*?)(?=^\s*#|\z)"
    $m = [regex]::Match($Content, $pattern)
    if ($m.Success) {
        return $m.Groups[1].Value.Trim()
    }
    return ""
}

function Test-HandoffQuality {
    param(
        [string]$Content,
        [string]$TaskId,
        [string]$Phase
    )

    $reasons = New-Object System.Collections.Generic.List[string]
    if (-not $Content) {
        $reasons.Add("empty_content")
        return @{ ok = $false; reasons = $reasons }
    }

    $firstNonEmpty = ($Content -split "\r?\n" | Where-Object { $_.Trim().Length -gt 0 } | Select-Object -First 1)
    if (-not $firstNonEmpty -or $firstNonEmpty.Trim() -ne "---") {
        $reasons.Add("missing_yaml_frontmatter")
    }

    $fm = Get-HandoffFrontmatter -Content $Content
    if (-not $fm -or -not $fm.status) {
        $reasons.Add("missing_yaml_status")
    }

    $meta = Get-HandoffMeta -Content $Content
    if (-not $meta.task) { $reasons.Add("missing_task_id") }
    if (-not $meta.role) { $reasons.Add("missing_role") }
    if (-not $meta.phase) {
        $reasons.Add("missing_phase")
    } elseif ($Phase -and ($meta.phase -ne $Phase)) {
        $reasons.Add("phase_mismatch")
    }

    if ($Content -notmatch "(?m)^# Rule Confirmation") { $reasons.Add("missing_rule_confirmation") }
    if ($Content -notmatch "(?m)^- Rule 6 ") { $reasons.Add("missing_rule_6") }

    $reproBlock = Get-SectionBlock -Content $Content -Heading "## Repro Commands"
    if (-not $reproBlock) {
        $reasons.Add("missing_repro_section")
    } else {
        $hasUnverified = $reproBlock -match "(?i)\bUNVERIFIED\b"
        $hasOutputMap = $reproBlock -match "(?m)->\s*\S"
        $hasCommandLine = $reproBlock -match "(?im)^\s*[-*]?\s*(\.\./|\.\\|[A-Za-z]:\\|python\s|pwsh\s|powershell\s|rg\s|Get-Content|Get-ChildItem|cat\s|type\s)"
        $hasCodeFence = $reproBlock -match '(?s)```'
        if (-not $hasUnverified -and -not ($hasOutputMap -or $hasCommandLine -or $hasCodeFence)) {
            $reasons.Add("missing_repro_command")
        }

        foreach ($pattern in $HandoffPlaceholderPatterns) {
            if ($reproBlock -match $pattern) {
                $reasons.Add("placeholder_repro")
                break
            }
        }
    }

    return @{ ok = ($reasons.Count -eq 0); reasons = $reasons }
}

function Get-MarkdownSummaryBullets {
    param([string]$Content)

    if (-not $Content) { return @() }

    # Try common patterns: "## Summary" / "### Summary" blocks with bullet lists.
    $m = [regex]::Match($Content, "(?s)^\s*#+\s*Summary.*?\n(.*?)(?=\n\s*#+\s|\z)")
    if (-not $m.Success) { return @() }

    $block = $m.Groups[1].Value
    $bullets = @()
    foreach ($line in ($block -split "\r?\n")) {
        $t = $line.Trim()
        if ($t -match "^\-\s+(.+)$") {
            $bullets += $Matches[1].Trim()
            if ($bullets.Count -ge 8) { break }
        }
    }
    return $bullets
}

function Compact-TaskNotesFile {
    param([string]$TaskId, [int]$KeepEntries = 3)

    $p = Get-TaskNotesPath -TaskId $TaskId
    if (-not (Test-Path $p)) { return }

    $c = Get-Content $p -Raw -ErrorAction SilentlyContinue
    if (-not $c) { return }

    if ($c.Length -le ([int]$MaxNotesChars * 2)) { return }

    $matches = [regex]::Matches($c, "(?m)^## \[")
    if ($matches.Count -le $KeepEntries) { return }

    $startIndex = $matches[$matches.Count - $KeepEntries].Index
    $trimmed = $c.Substring($startIndex).TrimStart()

    # Ensure we still respect MaxNotesChars (best-effort)
    if ($trimmed.Length -gt $MaxNotesChars) {
        $trimmed = $trimmed.Substring($trimmed.Length - $MaxNotesChars)
        $m2 = [regex]::Match($trimmed, "(?m)^## \[")
        if ($m2.Success -and $m2.Index -gt 0) { $trimmed = $trimmed.Substring($m2.Index) }
    }

    Set-Content -Path $p -Value $trimmed -Encoding UTF8
}

function Get-PreviousContext {
    param([hashtable]$Completion)

    if (-not $Completion -or -not $Completion.found) {
        return @{ text=""; ref="" }
    }

    $fullPath = Join-Path $script:HandoffsDir $Completion.file
    $content = $Completion.content

    $fm = Get-HandoffFrontmatter -Content $content

    $summaryText = ""
    if ($fm -and $fm.summary.Count -gt 0) {
        # nimm die ersten 8 bullets und begrenze chars
        $s = ($fm.summary | Select-Object -First 8) -join "`n- "
        $summaryText = "- " + $s
    } else {
        # fallback: harter trim
        $summaryText = ($content.Substring(0, [Math]::Min($content.Length, $MaxPrevContextChars)))
    }

    if ($summaryText.Length -gt $MaxPrevContextChars) {
        $summaryText = $summaryText.Substring(0, $MaxPrevContextChars) + " ... (gekürzt)"
    }

    return @{
        text = $summaryText
        ref  = $fullPath
    }
}

function Get-TaskNotesPath {
    param([string]$TaskId)
    $dir = Join-Path $script:ProjectRoot $MemoryDir
    Ensure-Dir $dir
    $safeId = Sanitize-FileNameComponent -Value $TaskId
    if (-not $safeId) { $safeId = "unknown_task" }
    return Join-Path $dir ("TASK_{0}_NOTES.md" -f $safeId)
}

function Get-TaskNotesExcerpt {
    param([string]$TaskId)
    $p = Get-TaskNotesPath -TaskId $TaskId
    if (-not (Test-Path $p)) { return "" }
    $c = Get-Content $p -Raw -ErrorAction SilentlyContinue
    if (-not $c) { return "" }

    # Prefer returning whole recent entries (avoid cutting inside YAML/frontmatter).
    $matches = [regex]::Matches($c, "(?m)^## \[")
    if ($matches.Count -gt 0) {
        $keep = 3
        $idx = $matches.Count - $keep
        if ($idx -lt 0) { $idx = 0 }
        $startIndex = $matches[$idx].Index
        $excerpt = $c.Substring($startIndex).TrimStart()
        if ($excerpt.Length -gt $MaxNotesChars) {
            $excerpt = $excerpt.Substring($excerpt.Length - $MaxNotesChars)
            $m2 = [regex]::Match($excerpt, "(?m)^## \[")
            if ($m2.Success -and $m2.Index -gt 0) { $excerpt = $excerpt.Substring($m2.Index) }
        }
        return $excerpt
    }

    if ($c.Length -gt $MaxNotesChars) { return $c.Substring($c.Length - $MaxNotesChars) }
    return $c
}

function Update-TaskNotesFromHandoff {
    param(
        [string]$TaskId,
        [string]$Phase,
        [string]$KI,
        [string]$HandoffContent,
        [string]$HandoffFile
    )

    $notesPath = Get-TaskNotesPath -TaskId $TaskId
    $fm = Get-HandoffFrontmatter -Content $HandoffContent
    $mdSummary = @()
    if (-not $fm -or $fm.summary.Count -eq 0) {
        $mdSummary = Get-MarkdownSummaryBullets -Content $HandoffContent
    }

    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $block = @()
    $block += "## [$ts] $TaskId - $Phase ($KI)"
    if ($fm -and $fm.summary.Count -gt 0) {
        $block += ""
        $block += "### Summary"
        $block += ($fm.summary | Select-Object -First 8 | ForEach-Object { "- $_" })
    } elseif ($mdSummary.Count -gt 0) {
        $block += ""
        $block += "### Summary"
        $block += ($mdSummary | Select-Object -First 8 | ForEach-Object { "- $_" })
    } else {
        $block += ""
        $block += "### Summary (fallback)"
        $snippet = $HandoffContent
        if ($snippet.Length -gt 280) { $snippet = $snippet.Substring(0, 280) + " ..." }
        $snippet = $snippet.Replace("`r", " ").Replace("`n", " ").Trim()
        $block += ("- " + $snippet)
    }
    $block += ""
    $block += "### Handoff"
    $block += "- File: $HandoffFile"
    $block += ""

    Add-Content -Path $notesPath -Value ($block -join "`n") -Encoding UTF8
    Compact-TaskNotesFile -TaskId $TaskId -KeepEntries 3
}

function Add-TaskNotesMessage {
    param(
        [string]$TaskId,
        [string]$Phase,
        [string]$KI,
        [string]$Message,
        [string]$HandoffFile = ""
    )

    $notesPath = Get-TaskNotesPath -TaskId $TaskId
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $block = @()
    $block += "## [$ts] $TaskId - $Phase ($KI)"
    $block += ""
    $block += "### Validation Error"
    $block += ("- " + $Message)
    if ($HandoffFile) { $block += "- File: $HandoffFile" }
    $block += ""

    Add-Content -Path $notesPath -Value ($block -join "`n") -Encoding UTF8
    Compact-TaskNotesFile -TaskId $TaskId -KeepEntries 3
}

function Reset-InvalidHandoffCount {
    param([string]$TaskId, [string]$Phase)
    $key = "$TaskId|$Phase"
    if ($script:InvalidHandoffCounts.ContainsKey($key)) {
        $script:InvalidHandoffCounts.Remove($key)
    }
}

function Register-InvalidHandoff {
    param(
        [string]$TaskId,
        [string]$Phase,
        [string]$KI,
        [string]$HandoffFile,
        [string[]]$Reasons
    )

    $key = "$TaskId|$Phase"
    $count = 0
    if ($script:InvalidHandoffCounts.ContainsKey($key)) {
        $count = [int]$script:InvalidHandoffCounts[$key]
    }
    $count++
    $script:InvalidHandoffCounts[$key] = $count

    $reasonText = if ($Reasons -and $Reasons.Count -gt 0) { $Reasons -join ", " } else { "unknown" }
    Write-Log "Invalid handoff for $TaskId/$Phase (attempt $count/$MaxInvalidHandoffRetries): $reasonText" "WARNING"
    Add-TaskNotesMessage -TaskId $TaskId -Phase $Phase -KI $KI `
        -Message ("Invalid handoff: {0} (attempt {1}/{2})" -f $reasonText, $count, $MaxInvalidHandoffRetries) `
        -HandoffFile $HandoffFile

    Write-MetricsEvent -Event "HANDOFF_INVALID" -Data @{
        task_id = $TaskId
        phase = $Phase
        ki = $KI
        reasons = $Reasons
        attempt = $count
        max_attempts = $MaxInvalidHandoffRetries
    }

    return @{
        count = $count
        exceeded = ($count -ge $MaxInvalidHandoffRetries)
        reason = $reasonText
    }
}

function Get-WorkingSetPath {
    param([string]$TaskId)
    $dir = Join-Path $script:ProjectRoot $MemoryDir
    Ensure-Dir $dir
    $safeId = Sanitize-FileNameComponent -Value $TaskId
    if (-not $safeId) { $safeId = "unknown_task" }
    return Join-Path $dir ("TASK_{0}_WORKING_SET.json" -f $safeId)
}

function Update-WorkingSetFromHandoff {
    param([string]$TaskId, [string]$HandoffContent)

    $path = Get-WorkingSetPath -TaskId $TaskId
    $set = @()
    if (Test-Path $path) {
        try {
            $json = Get-Content $path -Raw
            if ($json) {
                $set = ($json | ConvertFrom-Json)
                if (-not $set) { $set = @() }
            }
        } catch {
            $set = @()
        }
    }

    $files = @()
    $fm = Get-HandoffFrontmatter -Content $HandoffContent
    if ($fm -and $fm.files_changed.Count -gt 0) {
        $files = $fm.files_changed
    } elseif ($HandoffContent -match "(?s)files_changed:\s*(.*?)(?=\n\w+:|$)") {
        $block = $Matches[1]
        foreach ($m in [regex]::Matches($block, "(?m)^\s*-\s*[`"']?(.*?)[`"']?\s*$")) {
            $files += $m.Groups[1].Value.Trim()
        }
    }

    
    # Also allow explicit requests for additional files (when Read() is gated to Working Set)
    $req = Get-WorkingSetRequestsFromContent -Content $HandoffContent
    foreach ($r in $req) {
        if ($r -and ($set -notcontains $r)) { $set += $r }
    }

foreach ($f in $files) {
        if ($f -and ($set -notcontains $f)) { $set += $f }
    }

    # cap
    if ($set.Count -gt $WorkingSetMaxFiles) {
        $set = $set | Select-Object -Last $WorkingSetMaxFiles
    }

    ($set | ConvertTo-Json -Depth 3) | Set-Content $path -Encoding UTF8
}

function Get-WorkingSetList {
    param([string]$TaskId)
    $path = Get-WorkingSetPath -TaskId $TaskId
    if (-not (Test-Path $path)) { return @() }
    try {
        $json = Get-Content $path -Raw
        if ($json) {
            $result = ($json | ConvertFrom-Json)
            if ($result) { return $result }
        }
        return @()
    } catch {
        return @()
    }
}

function Get-WorkingSetRequestsFromContent {
    param([string]$Content)

    if (-not $Content) { return @() }

    $req = @()

    # YAML Frontmatter key (optional): working_set_request:
    $fm = Get-HandoffFrontmatter -Content $Content
    if ($fm -and ($fm.PSObject.Properties.Name -contains "working_set_request") -and $fm.working_set_request) {
        try {
            foreach ($p in $fm.working_set_request) {
                $v = [string]$p
                if ($v) { $req += $v.Trim() }
            }
        } catch { }
    }

    # Markdown heading style: "WORKING_SET_REQUEST:" or "## WORKING_SET_REQUEST"
    if ($Content -match "(?ms)^\s*(?:##\s*)?WORKING_SET_REQUEST\s*:?\s*\n(.*?)(?=\n\s*(?:##\s*|\w[\w\- ]{1,40}\s*:)\s*|\z)") {
        $block = $Matches[1]
        foreach ($m in [regex]::Matches($block, '(?m)^\s*[-*]\s+["'']?(.*?)["'']?\s*$')) {
            $v = $m.Groups[1].Value.Trim()
            if ($v) { $req += $v }
        }
    }

    # normalize + cap
    $req = $req | Where-Object { $_ -and $_.Trim().Length -gt 0 } | ForEach-Object { $_.Trim() } | Select-Object -Unique
    if ($req.Count -gt $MaxWorkingSetRequestFiles) { $req = $req | Select-Object -First $MaxWorkingSetRequestFiles }
    return $req
}

function Ensure-ClaudeWorkingSetGuardInstalled {
    if (-not $EnableWorkingSetGuard) { return }

    $claudeDir = Join-Path $script:ProjectRoot ".claude"
    $hooksDir  = Join-Path $claudeDir "hooks"
    Ensure-Dir -Path $claudeDir
    Ensure-Dir -Path $hooksDir

    $hookScript = Join-Path $hooksDir "autoloop_guard.ps1"
    $settingsPath = Join-Path $claudeDir "settings.local.json"

    # Write/refresh hook script (idempotent)
    $hookBody = @'
param()

$ErrorActionPreference = "Stop"

function To-LowerPath([string]$p) {
  if (-not $p) { return "" }
  try { return ($p -replace "\\\\","/").ToLowerInvariant() } catch { return ($p -replace "\\\\","/").ToLower() }
}

function Is-Under([string]$path, [string]$root) {
  if (-not $path -or -not $root) { return $false }
  $p = To-LowerPath $path
  $r = To-LowerPath $root
  if (-not $r.EndsWith("/")) { $r = $r + "/" }
  return ($p -eq $r.TrimEnd("/")) -or $p.StartsWith($r)
}

# Read hook input
$raw = ""
try { $raw = [Console]::In.ReadToEnd() } catch { $raw = "" }
if (-not $raw) { exit 0 }

$data = $null
try { $data = $raw | ConvertFrom-Json -ErrorAction Stop } catch { exit 0 }

$tool = [string]$data.tool_name
$input = $data.tool_input

$projectRoot = $env:CLAUDE_PROJECT_DIR
if (-not $projectRoot) { $projectRoot = $env:ALOOP_PROJECT_ROOT }
if (-not $projectRoot) { $projectRoot = (Get-Location).Path }

$phase = $env:ALOOP_PHASE
$strict = ($env:ALOOP_GUARD_STRICT -eq "1")
$maxBytes = 0
try { $maxBytes = [int]$env:ALOOP_GUARD_MAX_READ_BYTES } catch { $maxBytes = 0 }

# Block patterns/paths (hard)
$patterns = @()
if ($env:ALOOP_GUARD_BLOCK_PATTERNS) { $patterns = $env:ALOOP_GUARD_BLOCK_PATTERNS.Split(";") | Where-Object { $_ } }

$blockPaths = @()
if ($env:ALOOP_GUARD_BLOCK_PATHS) { $blockPaths = $env:ALOOP_GUARD_BLOCK_PATHS.Split(";") | Where-Object { $_ } }

# Always-allowed roots (small, local loop artifacts)
$alwaysRoots = @(
  ".claude",
  "AI_COLLABORATION/MEMORY",
  "AI_COLLABORATION/PLANS",
  "AI_COLLABORATION/HANDOFFS",
  "AI_COLLABORATION/ARTIFACTS"
)

# Load working set list (relative paths)
$wsFile = $env:ALOOP_WORKING_SET_FILE
$ws = @()
if ($wsFile -and (Test-Path $wsFile)) {
  try {
    $wsRaw = Get-Content $wsFile -Raw
    if ($wsRaw) { $ws = ($wsRaw | ConvertFrom-Json) }
  } catch { $ws = @() }
}
$wsAbs = @()
foreach ($p in $ws) {
  $v = [string]$p
  if (-not $v) { continue }
  $v = $v.Trim()
  if (-not $v) { continue }
  if ([System.IO.Path]::IsPathRooted($v)) {
    $wsAbs += (Resolve-Path $v -ErrorAction SilentlyContinue).Path
  } else {
    $wsAbs += (Join-Path $projectRoot $v)
  }
}

function Block([string]$msg) {
  if (-not $msg) { $msg = "Blocked by autoloop guard." }
  Write-Error $msg
  exit 2
}

# Helper: decide if a file is allowed to READ in strict mode
function Is-AllowedRead([string]$filePath) {
  if (-not $filePath) { return $true }

  $abs = $filePath
  if (-not [System.IO.Path]::IsPathRooted($abs)) { $abs = Join-Path $projectRoot $abs }

  # allow always roots
  foreach ($r in $alwaysRoots) {
    $rr = Join-Path $projectRoot $r
    if (Is-Under $abs $rr) { return $true }
  }

  # allow working set entries
  foreach ($w in $wsAbs) {
    if ($w -and (To-LowerPath $abs) -eq (To-LowerPath $w)) { return $true }
  }

  return $false
}

# Handle tool types
if ($tool -in @("Read","Edit","Write")) {
  $fp = ""
  try { $fp = [string]$input.file_path } catch { $fp = "" }
  if (-not $fp) { exit 0 }

  # hard block paths
  foreach ($bp in $blockPaths) {
    if (-not $bp) { continue }
    $bpa = Join-Path $projectRoot $bp
    if (Is-Under (Join-Path $projectRoot $fp) $bpa) { Block "Pfad gesperrt: $fp (Policy: no MESSAGE_QUEUE/LOCKS)" }
  }

  # hard block patterns
  foreach ($pat in $patterns) {
    if (-not $pat) { continue }
    if ((To-LowerPath $fp) -like "*$((To-LowerPath $pat))*") { Block "Datei gesperrt (Monolith): $fp. Nutze Digest/Excerpt oder WORKING_SET_REQUEST." }
  }

  # strict reads: only working set + alwaysRoots
  if ($strict -and $tool -eq "Read") {
    if (-not (Is-AllowedRead $fp)) {
      Block "Read() ausserhalb WORKING SET geblockt: $fp. Nutze zuerst Grep/Glob, dann WORKING_SET_REQUEST im Handoff."
    }
  }

  # size guard for Read
  if ($tool -eq "Read" -and $maxBytes -gt 0) {
    try {
      $abs = $fp
      if (-not [System.IO.Path]::IsPathRooted($abs)) { $abs = Join-Path $projectRoot $abs }
      if (Test-Path $abs) {
        $len = (Get-Item $abs).Length
        if ($len -gt $maxBytes) {
          Block "Read() Datei zu gross ($len bytes > $maxBytes): $fp. Nutze Grep/Excerpt oder Digest."
        }
      }
    } catch { }
  }

  exit 0
}

# Bash: block obvious reads of monoliths and forbidden paths in strict phases
if ($tool -eq "Bash") {
  $cmd = ""
  try { $cmd = [string]$input.command } catch { $cmd = "" }
  if (-not $cmd) { exit 0 }

  $cmdL = $cmd.ToLowerInvariant()

  foreach ($pat in $patterns) {
    if (-not $pat) { continue }
    if ($cmdL -like "*$($pat.ToLowerInvariant())*") {
      Block "Bash command references blocked monolith pattern ('$pat'). Bitte nutze Digest/Excerpt oder WORKING_SET_REQUEST."
    }
  }

  # In strict mode, block content-dumping commands unless obviously within alwaysRoots/working set
  if ($strict) {
    if ($cmdL -match "\b(cat|type|get-content|more|less|head|tail)\b") {
      Block "Bash content-dump commands sind in dieser Phase geblockt. Nutze Read() nur im WORKING SET oder stelle WORKING_SET_REQUEST."
    }
  }

  exit 0
}

exit 0
'@

    $hookBody | Set-Content -Path $hookScript -Encoding UTF8

    # Merge settings.local.json (do not clobber)
    $settings = @{}
    if (Test-Path $settingsPath) {
        try { $settings = (Get-Content $settingsPath -Raw | ConvertFrom-Json) } catch { $settings = @{} }
    }

    if (-not $settings.hooks) { $settings | Add-Member -MemberType NoteProperty -Name hooks -Value (@{}) -Force }
    if (-not $settings.hooks.PreToolUse) { $settings.hooks | Add-Member -MemberType NoteProperty -Name PreToolUse -Value (@()) -Force }

    $cmd = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File .claude/hooks/autoloop_guard.ps1"
    $existing = $false
    foreach ($entry in $settings.hooks.PreToolUse) {
        try {
            if ($entry.matcher -eq "Read|Edit|Write|Bash") {
                foreach ($h in $entry.hooks) {
                    if ($h.type -eq "command" -and $h.command -eq $cmd) { $existing = $true }
                }
            }
        } catch { }
    }

    if (-not $existing) {
        $newEntry = [pscustomobject]@{
            matcher = "Read|Edit|Write|Bash"
            hooks = @(
                [pscustomobject]@{
                    type = "command"
                    command = $cmd
                }
            )
        }
        $settings.hooks.PreToolUse += $newEntry
    }

    ($settings | ConvertTo-Json -Depth 10) | Set-Content -Path $settingsPath -Encoding UTF8
}



function Test-NeedsCompact {
    param([string]$Prompt)
    if (-not $EnableAutoCompact) { return $false }
    # V4 EFFICIENCY: Trigger at 75% (SoftPromptChars) instead of 100% (MaxPromptChars)
    # This gives better control over what gets retained
    return ($Prompt.Length -gt $SoftPromptChars)
}

# ============================================================================
# ROLE MAPPING
# ============================================================================

$script:RoleMapping = @{
    "alpha" = @{
        "ARCHITECT" = "ki1"
        "EXECUTOR"  = "ki2"
        "VALIDATOR" = "ki3"
        "PROXY"     = "ki0"
    }
    "beta" = @{
        "ARCHITECT" = "ki5"
        "EXECUTOR"  = "ki6"
        "VALIDATOR" = "ki7"
        "PROXY"     = "ki0"
    }
}

$script:Roles = $script:RoleMapping[$Team]

# ============================================================================
# PHASE STATE MACHINE
# ============================================================================

$script:PhaseFlow = @{
    "ARCHITECT"     = @{ next_success = "PROXY_PLAN";  next_fail = $null;       ki_role = "ARCHITECT"; max_time = $MaxPhaseTimeMinutes }
    "PROXY_PLAN"    = @{ next_success = "EXECUTOR";    next_fail = "ARCHITECT"; ki_role = "PROXY";     max_time = $MaxProxyTimeMinutes }
    "EXECUTOR"      = @{ next_success = "PROXY_IMPL";  next_fail = $null;       ki_role = "EXECUTOR";  max_time = $MaxPhaseTimeMinutes }
    "PROXY_IMPL"    = @{ next_success = "VALIDATOR";   next_fail = "EXECUTOR";  ki_role = "PROXY";     max_time = $MaxProxyTimeMinutes }
    "VALIDATOR"     = @{ next_success = "PROXY_FINAL"; next_fail = $null;       ki_role = "VALIDATOR"; max_time = $MaxPhaseTimeMinutes }
    "PROXY_FINAL"   = @{ next_success = "DONE";        next_fail = "EXECUTOR";  ki_role = "PROXY";     max_time = $MaxProxyTimeMinutes }
    # EXTERNAL_TASK: Wartet auf externe Prozesse (Backtests, Mining) - 10h Timeout
    "EXTERNAL_TASK" = @{ next_success = "VALIDATOR";   next_fail = $null;       ki_role = "EXTERNAL";  max_time = 600 }
}

function Get-KI-For-Phase {
    param([string]$Phase)
    $flow = $script:PhaseFlow[$Phase]
    if (-not $flow) { return $null }
    return $script:Roles[$flow.ki_role]
}

function Get-Next-Phase {
    param([string]$CurrentPhase, [string]$Result)
    $flow = $script:PhaseFlow[$CurrentPhase]
    if (-not $flow) { return $null }

    # Skip Proxy phases if -SkipProxy is set
    if ($SkipProxy -and $flow.ki_role -eq "PROXY") {
        return $flow.next_success
    }

    switch -Regex ($Result) {
        "COMPLETE|APPROVED|TASK_COMPLETE" { return $flow.next_success }
        "REJECTED|TASK_REJECTED"          { return $flow.next_fail }
        "BLOCKED"                         { return "BLOCKED" }
        "ESCALATE|ESCALATION"             { return "ESCALATE" }
        default                           { return $null }
    }
}

# ============================================================================
# ESCALATION MANAGEMENT
# ============================================================================

$script:EscalationsDir = Join-Path $script:ProjectRoot "AI_COLLABORATION/ESCALATIONS"

function Write-Escalation {
    param(
        [string]$TaskId,
        [string]$TaskName,
        [string]$Phase,
        [string]$EscalatedBy,
        [string]$Reason,
        [string]$HandoffContent
    )

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $filename = "escalation_${TaskId}_${timestamp}.md"
    $filepath = Join-Path $script:EscalationsDir $filename

    # Extract escalation details from handoff if available
    $problem = "User-Entscheidung erforderlich"
    $options = ""
    $recommendation = ""

    if ($HandoffContent -match "(?s)PROBLEM[:\s]+(.+?)(?=OPTION|EMPFEHLUNG|---|\z)") {
        $problem = $Matches[1].Trim()
    }
    if ($HandoffContent -match "(?s)(Option\s+[ABC].+?)(?=EMPFEHLUNG|---|\z)") {
        $options = $Matches[1].Trim()
    }
    if ($HandoffContent -match "(?s)EMPFEHLUNG[:\s]+(.+?)(?=---|\z)") {
        $recommendation = $Matches[1].Trim()
    }

    $content = @"
---
status: PENDING
task_id: "$TaskId"
task_name: "$TaskName"
escalated_by: "$EscalatedBy"
escalated_at: "$(Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')"
phase: "$Phase"
priority: "HIGH"
category: "ARCHITECTURE"
resolution: null
resolved_at: null
resolved_by: null
---

# Escalation: $TaskName

## Problem

$problem

## Kontext

- **Task:** $TaskId
- **Phase:** $Phase
- **Escalated by:** $EscalatedBy
- **Reason:** $Reason

## Optionen

$options

## Empfehlung

$recommendation

---

## User Resolution (bitte ausfuellen)

``````yaml
resolution: PROCEED  # oder ABORT oder MODIFY
chosen_option: "A"   # oder "B" oder "C"
notes: "..."         # Optional: zusaetzliche Anweisungen
``````

Nach dem Ausfuellen: Datei speichern. Loop erkennt Resolution automatisch.
"@

    Set-Content -Path $filepath -Value $content -Encoding UTF8
    Write-Log "Escalation geschrieben: $filename" "WARNING"
    return $filepath
}

function Check-EscalationResolved {
    param([string]$TaskId)

    $pattern = "escalation_${TaskId}_*.md"
    $files = Get-ChildItem -Path $script:EscalationsDir -Filter $pattern -ErrorAction SilentlyContinue |
             Sort-Object LastWriteTime -Descending

    if (-not $files -or $files.Count -eq 0) { return $null }

    $latestFile = $files[0]
    $content = Get-Content -Path $latestFile.FullName -Raw -Encoding UTF8

    # Check if resolved
    if ($content -match "status:\s*RESOLVED") {
        # Extract resolution
        $resolution = @{ status = "RESOLVED"; action = "PROCEED"; notes = "" }

        if ($content -match "resolution:\s*(PROCEED|ABORT|MODIFY)") {
            $resolution.action = $Matches[1]
        }
        if ($content -match "chosen_option:\s*[`"']?([ABC])[`"']?") {
            $resolution.option = $Matches[1]
        }
        if ($content -match "notes:\s*[`"']?(.+?)[`"']?\s*$") {
            $resolution.notes = $Matches[1]
        }

        Write-Log "Escalation resolved: $($latestFile.Name) -> $($resolution.action)" "SUCCESS"
        return $resolution
    }

    # Check for manual resolution marker
    if ($content -match "resolution:\s*(PROCEED|ABORT|MODIFY)") {
        # User filled in resolution but forgot to change status - auto-detect
        $resolution = @{ status = "RESOLVED"; action = $Matches[1]; notes = "" }

        # Update file to mark as resolved
        $content = $content -replace "status:\s*PENDING", "status: RESOLVED"
        $content = $content -replace "resolved_at:\s*null", "resolved_at: `"$(Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')`""
        $content = $content -replace "resolved_by:\s*null", "resolved_by: `"user`""
        Set-Content -Path $latestFile.FullName -Value $content -Encoding UTF8

        Write-Log "Escalation auto-resolved: $($latestFile.Name) -> $($resolution.action)" "SUCCESS"
        return $resolution
    }

    return $null
}

# ============================================================================
# EXTERNAL TASK MANAGEMENT (Phase 6 - V4 Loop Integration)
# ============================================================================
# Enables polling of external tasks (backtests, training) and notification to owner KI

$script:ExternalTasksDir = Join-Path $script:ProjectRoot "AI_COLLABORATION/EXTERNAL_TASKS"
$script:ExternalTasksRegistry = Join-Path $script:ExternalTasksDir "task_registry.json"
$script:ExternalTasksPollingInterval = 60  # seconds between polls

function Poll-ExternalTasks {
    <#
    .SYNOPSIS
        Poll task_registry.json for COMPLETED/FAILED tasks and create notifications.
        Called every 60s in main loop (after Check-EscalationResolved).
    #>

    if (-not (Test-Path $script:ExternalTasksRegistry)) {
        return @()  # No registry yet, nothing to poll
    }

    try {
        $registry = Get-Content $script:ExternalTasksRegistry -Raw -Encoding UTF8 | ConvertFrom-Json
    }
    catch {
        Write-Log "Failed to read external task registry: $_" "WARNING"
        return @()
    }

    $notifications = @()

    # Check each active task for completion
    $tasksToMove = @()
    foreach ($task in $registry.active_tasks) {
        if (-not $task.status_file -or -not (Test-Path $task.status_file)) {
            continue
        }

        try {
            $statusData = Get-Content $task.status_file -Raw -Encoding UTF8 | ConvertFrom-Json
        }
        catch {
            continue
        }

        if ($statusData.status -eq "COMPLETED" -or $statusData.status -eq "FAILED") {
            # Task is done - create notification handoff
            $notification = @{
                task_id = $task.task_id
                owner = $task.owner
                status = $statusData.status
                exit_code = $statusData.exit_code
                output_dir = $statusData.output_dir
                duration_seconds = $statusData.duration_seconds
                log_file = $statusData.log_file
                err_file = $statusData.err_file
                completed_at = $statusData.completed_at
            }

            # Create handoff notification for owner KI
            $handoffPath = Write-ExternalTaskNotification -Notification $notification
            if ($handoffPath) {
                $notifications += $notification
                $tasksToMove += @{
                    task = $task
                    status = $statusData.status
                    statusData = $statusData
                }
                Write-Log "External task completed: $($task.task_id) -> $($statusData.status) (notifying $($task.owner))" "SUCCESS"
            }
        }
    }

    # Move completed tasks to completed_tasks or failed_tasks
    foreach ($move in $tasksToMove) {
        Move-TaskInRegistry -TaskId $move.task.task_id -NewStatus $move.status -StatusData $move.statusData
    }

    return $notifications
}

function Move-TaskInRegistry {
    <#
    .SYNOPSIS
        Atomically move task from active_tasks to completed_tasks or failed_tasks.
        Uses file-lock pattern for safety.
    #>
    param(
        [string]$TaskId,
        [ValidateSet("COMPLETED", "FAILED")]
        [string]$NewStatus,
        [object]$StatusData
    )

    if (-not (Test-Path $script:ExternalTasksRegistry)) {
        return
    }

    $lockFile = "$($script:ExternalTasksRegistry).lock"
    $maxRetries = 5
    $retryDelay = 200  # ms

    for ($i = 0; $i -lt $maxRetries; $i++) {
        try {
            # Simple lock: create exclusive file
            $lockStream = [System.IO.File]::Open($lockFile, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)

            try {
                $registry = Get-Content $script:ExternalTasksRegistry -Raw -Encoding UTF8 | ConvertFrom-Json

                # Find and remove from active_tasks
                $taskToMove = $null
                $newActiveTasks = @()
                foreach ($task in $registry.active_tasks) {
                    if ($task.task_id -eq $TaskId) {
                        $taskToMove = $task
                    } else {
                        $newActiveTasks += $task
                    }
                }

                if ($taskToMove) {
                    # Add completion metadata
                    $taskToMove | Add-Member -NotePropertyName "completed_at" -NotePropertyValue $StatusData.completed_at -Force
                    $taskToMove | Add-Member -NotePropertyName "exit_code" -NotePropertyValue $StatusData.exit_code -Force
                    $taskToMove | Add-Member -NotePropertyName "duration_seconds" -NotePropertyValue $StatusData.duration_seconds -Force
                    $taskToMove | Add-Member -NotePropertyName "output_dir" -NotePropertyValue $StatusData.output_dir -Force

                    # Move to appropriate list
                    $registry.active_tasks = $newActiveTasks
                    if ($NewStatus -eq "COMPLETED") {
                        if (-not $registry.completed_tasks) { $registry.completed_tasks = @() }
                        $registry.completed_tasks += $taskToMove
                    } else {
                        if (-not $registry.failed_tasks) { $registry.failed_tasks = @() }
                        $registry.failed_tasks += $taskToMove
                    }

                    # Save registry
                    $registry | ConvertTo-Json -Depth 10 | Set-Content -Path $script:ExternalTasksRegistry -Encoding UTF8
                    Write-Log "Moved task $TaskId to $NewStatus in registry" "DEBUG"
                }
            }
            finally {
                $lockStream.Close()
                Remove-Item $lockFile -Force -ErrorAction SilentlyContinue
            }
            return
        }
        catch [System.IO.IOException] {
            # Lock file exists, wait and retry
            Start-Sleep -Milliseconds $retryDelay
        }
        catch {
            Write-Log "Error moving task in registry: $_" "WARNING"
            Remove-Item $lockFile -Force -ErrorAction SilentlyContinue
            return
        }
    }

    Write-Log "Failed to acquire lock for registry update (task: $TaskId)" "WARNING"
}

function Write-ExternalTaskNotification {
    <#
    .SYNOPSIS
        Create handoff notification file for owner KI when external task completes.
        Format: external_task_{task_id}_{status}_{timestamp}.md
    #>
    param([hashtable]$Notification)

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $status = $Notification.status.ToLower()
    $filename = "external_task_$($Notification.task_id)_${status}_${timestamp}.md"
    $filepath = Join-Path $script:HandoffsDir $filename

    $statusEmoji = if ($Notification.status -eq "COMPLETED") { "SUCCESS" } else { "FAILED" }
    $durationMin = [math]::Round($Notification.duration_seconds / 60, 1)

    # Build next steps based on status
    $nextSteps = if ($Notification.status -eq "COMPLETED") {
        "1. Review output in output_dir`n2. Continue with dependent tasks`n3. Update task status in plan if needed"
    } else {
        "1. Check error file for failure reason`n2. Decide: Retry, Abort, or Escalate`n3. If retrying, use start_external_task.ps1 again"
    }

    $content = @"
---
type: EXTERNAL_TASK_$($Notification.status)
task_id: "$($Notification.task_id)"
owner: "$($Notification.owner)"
status: "$($Notification.status)"
exit_code: $($Notification.exit_code)
duration_minutes: $durationMin
completed_at: "$($Notification.completed_at)"
---

# External Task $statusEmoji`: $($Notification.task_id)

**Owner:** $($Notification.owner)
**Status:** $($Notification.status)
**Exit Code:** $($Notification.exit_code)
**Duration:** $durationMin minutes

## Output Location
- **Output Dir:** ``$($Notification.output_dir)``
- **Log File:** ``$($Notification.log_file)``
- **Error File:** ``$($Notification.err_file)``

## Next Steps
$nextSteps
"@

    try {
        if (-not (Test-Path $script:HandoffsDir)) {
            New-Item -ItemType Directory -Path $script:HandoffsDir -Force | Out-Null
        }
        Set-Content -Path $filepath -Value $content -Encoding UTF8
        return $filepath
    }
    catch {
        Write-Log "Failed to write external task notification: $_" "WARNING"
        return $null
    }
}

# ============================================================================
# PLAN MANAGEMENT
# ============================================================================

$script:PlansDir = Join-Path $script:ProjectRoot "AI_COLLABORATION/PLANS"
$script:HandoffsDir = Join-Path $script:ProjectRoot "AI_COLLABORATION/HANDOFFS"

function Load-Plan {
    param([string]$Path)

    $fullPath = if ([System.IO.Path]::IsPathRooted($Path)) { $Path } else { Join-Path $script:ProjectRoot $Path }

    if (-not (Test-Path $fullPath)) {
        Write-Log "Plan-Datei nicht gefunden: $fullPath" "ERROR"
        return $null
    }

    $content = Get-Content $fullPath -Raw -Encoding UTF8
    $plan = @{ name = ""; tasks = @() }

    # Parse tasks (simple YAML parser)
    $lines = $content -split "`n"
    $currentTask = $null
    $inPlan = $false

    foreach ($line in $lines) {
        if ($line -match '^\s*plan:\s*$') {
            $inPlan = $true
            continue
        }
        if ($line -match '^\s*tasks:\s*$') {
            $inPlan = $false
            continue
        }

        if ($inPlan -and $line -match '^\s*name:\s*(.+?)\s*$') {
            $plan.name = (Normalize-YamlScalar -Value $Matches[1])
            continue
        }

        if ($line -match '^\s*-\s*id:\s*(.+?)\s*$') {
            if ($currentTask) { $plan.tasks += $currentTask }
            $rawId = (Normalize-YamlScalar -Value $Matches[1])
            $safeId = (Sanitize-FileNameComponent -Value $rawId)
            if (-not $safeId) { $safeId = "unknown_task" }
            $currentTask = @{
                id = $safeId
                id_raw = $rawId
                name = ""
                priority = "P2"
                status = "PENDING"
                current_phase = $null
            }
        }
        elseif ($currentTask) {
            if ($line -match '^\s*name:\s*(.+?)\s*$') { $currentTask.name = (Normalize-YamlScalar -Value $Matches[1]) }
            elseif ($line -match '^\s*priority:\s*(.+?)\s*$') { $currentTask.priority = (Normalize-YamlScalar -Value $Matches[1]) }
            elseif ($line -match '^\s*status:\s*(.+?)\s*$') { $currentTask.status = (Normalize-YamlScalar -Value $Matches[1]) }
            elseif ($line -match '^\s*current_phase:\s*(.+?)\s*$') {
                $phase = (Normalize-YamlScalar -Value $Matches[1])
                $currentTask.current_phase = if ($phase -eq "null" -or -not $phase) { $null } else { $phase }
            }
        }
    }
    if ($currentTask) { $plan.tasks += $currentTask }

    return $plan
}

function Get-Latest-HandoffInfo {
    param(
        [string]$KI,
        [string]$TaskId = "",
        [string]$Phase = ""
    )

    $today = Get-Date -Format "yyyyMMdd"

    # V3: Task-/Phase-specific pattern
    if ($TaskId -and $Phase) {
        $pattern = "${KI}_${TaskId}_${Phase}_*.md"
    } elseif ($TaskId) {
        $pattern = "${KI}_${TaskId}_*.md"
    } else {
        $pattern = "${KI}_${today}*.md"
    }

    $latest = Get-ChildItem -Path $script:HandoffsDir -Filter $pattern -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if (-not $latest) { return @{ found = $false } }

    $content = Get-Content $latest.FullName -Raw -ErrorAction SilentlyContinue
    if (-not $content) { return @{ found = $false; reason = "empty_handoff" } }

    return @{
        found = $true
        file = $latest.Name
        content = $content
    }
}

function Save-Plan {
    param($Plan, [string]$Path)

    $fullPath = if ([System.IO.Path]::IsPathRooted($Path)) { $Path } else { Join-Path $script:ProjectRoot $Path }

    $yaml = @"
# Autonomous Loop V4 Plan
# Updated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

plan:
  name: "$($Plan.name)"

tasks:
"@

    foreach ($task in $Plan.tasks) {
        $phase = if ($task.current_phase) { $task.current_phase } else { "null" }
        $yaml += @"

  - id: $($task.id)
    name: "$($task.name)"
    priority: $($task.priority)
    status: $($task.status)
    current_phase: $phase
"@

        # Preserve task description (V3 plans often carry the real scope/constraints here).
        try {
            $taskDesc = ""
            if ($task -and ($task.PSObject.Properties.Name -contains "description")) {
                $taskDesc = [string]$task.description
            }
            if ($taskDesc) {
                $taskDesc = ($taskDesc -replace "`r", "").TrimEnd()
                $indented = ($taskDesc -split "`n" | ForEach-Object { "      " + $_ }) -join "`n"
                $yaml += @"
    description: |
$indented
"@
            }
        } catch { }
    }

    $planDir = Split-Path $fullPath -Parent
    if (-not (Test-Path $planDir)) { New-Item -ItemType Directory -Path $planDir -Force | Out-Null }

    $yaml | Set-Content $fullPath -Encoding UTF8
    Write-Log "Plan gespeichert: $fullPath" "DEBUG"
}

# ============================================================================
# PER-KI BACKEND SELECTION (from V2)
# ============================================================================

$script:KiBackendMap = @{}
$script:KiModelMap = @{}

function Initialize-KiBackends {
    if ($KiBackends) {
        Write-Log "Parsing KiBackends: $KiBackends" "INFO"
        $pairs = $KiBackends -split ','
        foreach ($pair in $pairs) {
            $parts = $pair.Trim() -split '='
            if ($parts.Count -eq 2) {
                $ki = $parts[0].Trim().ToLower()
                $backend = $parts[1].Trim().ToLower()
                if ($backend -in @("claude", "codex")) {
                    $script:KiBackendMap[$ki] = $backend
                    Write-Log "  $ki -> $backend" "DEBUG"
                }
            }
        }
    }
}

function Get-KiBackend {
    param([string]$Ki)
    $kiLower = $Ki.ToLower()
    if ($script:KiBackendMap.ContainsKey($kiLower)) { return $script:KiBackendMap[$kiLower] }
    return $DefaultBackend
}

function Get-Previous-Phase {
    param([string]$CurrentPhase)

    # Phase workflow: ARCHITECT -> PROXY_PLAN -> EXECUTOR -> PROXY_IMPL -> VALIDATOR -> PROXY_FINAL -> DONE
    $phaseMap = @{
        "PROXY_PLAN" = "ARCHITECT"
        "EXECUTOR" = "PROXY_PLAN"
        "PROXY_IMPL" = "EXECUTOR"
        "VALIDATOR" = "PROXY_IMPL"
        "PROXY_FINAL" = "VALIDATOR"
        "DONE" = "PROXY_FINAL"
    }

    if ($phaseMap.ContainsKey($CurrentPhase)) {
        return $phaseMap[$CurrentPhase]
    }
    return ""
}

# ============================================================================
# KI DISPATCH
# ============================================================================

function Get-Phase-Prompt {
    param($Task, [string]$Phase, $PreviousOutput)

    # V4 EFFICIENCY: Extract NOTES + Working Set
    $notes = Get-TaskNotesExcerpt -TaskId $Task.id
    $ws = Get-WorkingSetList -TaskId $Task.id
    $wsText = if ($ws.Count -gt 0) { ($ws | ForEach-Object { "- $_" }) -join "`n" } else { "- (leer)" }
    $safeTaskId = Sanitize-FileNameComponent -Value $Task.id
    if (-not $safeTaskId) { $safeTaskId = "unknown_task" }

    # Plan excerpt: keep prompts grounded without triggering repo-wide scans.
    $desc = ""
    try {
        if ($Task -and ($Task.PSObject.Properties.Name -contains "description")) {
            $desc = [string]$Task.description
        }
    } catch { $desc = "" }
    if ($null -eq $desc) { $desc = "" }
    $desc = $desc.Trim()
    if ($desc.Length -gt 1400) { $desc = $desc.Substring(0, 1400) + "`n... (gekürzt)" }

    # PreviousOutput is now a hashtable {text, ref} from Get-PreviousContext
    $prevText = if ($PreviousOutput -is [hashtable]) { $PreviousOutput.text } else { $PreviousOutput }
    $prevRef = if ($PreviousOutput -is [hashtable]) { $PreviousOutput.ref } else { "" }

    $baseContext = @"
AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: $($Task.name)
TASK-ID: $($Task.id)
PRIORITY: $($Task.priority)
PHASE: $Phase

TASK DESCRIPTION (Plan excerpt, kurz):
$desc

TASK NOTES (kurz, autoritativ):
$notes

MANDATORY WORKFLOW (do first, every task incl docs):
1) Context-sync: read `AI_COLLABORATION/SYSTEM_STATUS.json` + relevant ADR/Docs; run `git status --porcelain`.
2) Data claims must cite artifact path + filter + N + repro command (no placeholders).
3) Zero != missing: if unclear, mark UNVERIFIED.
4) Line refs must be verified via: `nl -ba <file> | sed -n 'a,bp'`.
5) Deliverable must include: changes + summary + repro commands + CURRENT_STATUS update.
6) No assumptions: verify from current repo snapshot.

RULE CONFIRMATION REQUIRED:
- Include "Rule Confirmation" block in output (CONFIRMED/UNVERIFIED).
- State granularity + semantics + target metric before analysis.

WORKING SET (nur relevante Dateien):
$wsText

WORKING SET POLICY (enforced in ARCHITECT/PROXY/VALIDATOR):
- Read() ausserhalb WORKING SET kann technisch geblockt sein.
- Wenn du eine Datei ausserhalb brauchst: nutze Grep/Glob, dann fordere sie im Handoff an:

WORKING_SET_REQUEST:
- relative/path/to/file1
- relative/path/to/file2
(max $MaxWorkingSetRequestFiles)


WORKDIR:
- Du bist bereits im Repo-Root: $($script:ProjectRoot)
- Vermeide `Set-Location`/`cd` auf `\\?\\`-Pfade (Windows long-path Prefix kann Tools verwirren)

"@

    switch ($Phase) {
        "ARCHITECT" {
            $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
            $ki = $script:Roles.ARCHITECT
            return $baseContext + @"
ROLLE: ARCHITECT
AUFGABE: Erstelle detaillierten Implementierungsplan.

EFFIZIENZ-REGELN (wie normal CLI):
- Kein Repo-weiter Scan (kein rekursives Listing, kein breitflächiges Grep).
- Arbeite primär mit WORKING SET + TASK NOTES; wenn leer: max 2 gezielte Datei-Finder-Queries, dann stoppen und fehlende Pfade anfordern.
- Keine Status-/Messaging-Dateien lesen/schreiben (queue/CURRENT_STATUS) ausser explizit verlangt.
- Keine langen Tool-Outputs im Handoff; grosse Logs nach AI_COLLABORATION/ARTIFACTS/ auslagern und verlinken.

SCHRITTE:
1. Analysiere Anforderungen
2. Identifiziere betroffene Dateien
3. Erstelle Schritt-fuer-Schritt Checkliste
4. Definiere Acceptance Criteria

TOKEN HYGIENE:
- Output muss direkt das Handoff-Markdown sein (keine Diffs, keine Zusatztexte).
- Schreibe Handoff mit YAML Frontmatter (---\nstatus: COMPLETE\n...\n---)
- Max 8 summary bullets
- Keine langen Logs/Diffs im Body (nur Pfade)

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: COMPLETE
task: $safeTaskId
role: ARCHITECT
phase: ARCHITECT
files_changed: []
summary:
  - <max 8 bullets>
---
# Rule Confirmation
- Rule 1 (SYSTEM_STATUS + ADR/Docs + git status): CONFIRMED/UNVERIFIED
- Rule 2 (granularity stated): <global|per-market|per-league|per-team>
- Rule 3 (semantics defined): <fields/keys>
- Rule 4 (target metric): <accuracy|calibration|bet-selection>
- Rule 5 (helper-only boundaries): CONFIRMED/UNVERIFIED
- Rule 6 (reproducibility): <command + output path> or UNVERIFIED (no placeholders)

## Task Setup
- Granularity: <global|per-market|per-league|per-team>
- Semantics: <key fields/definitions>
- Target metric: <accuracy|calibration|bet-selection>

## Repro Commands
- <command> -> <output path> or UNVERIFIED

# Implementierungsplan

WICHTIG: Erstelle Handoff-Datei wenn fertig:
- Datei: AI_COLLABORATION/HANDOFFS/${ki}_${safeTaskId}_ARCHITECT_${timestamp}.md
- YAML mit status: COMPLETE
- YAML mit files_changed: [...]
"@
        }
        "PROXY_PLAN" {
            $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
            return $baseContext + @"
ROLLE: PROXY (User-Stellvertreter mit Projekt-Kontext)
AUFGABE: Pruefe den Plan vom ARCHITECT - NICHT nur mechanisch, sondern konzeptionell.

PFLICHTLEKTUERE (vor Review lesen):
1. AI_COLLABORATION/KI_PROFILES/ki0_proxy.md - Dein vollstaendiges Profil mit Known Bugs
2. AI_COLLABORATION/SYSTEM_STATUS.json - Aktueller Projektstatus
3. CLAUDE.md - Projektkontext (bei Architektur-Fragen)

EFFIZIENZ-REGELN:
- Arbeite mit VORHERIGER OUTPUT + TASK NOTES + Profil-Wissen
- Maximal 3-4 gezielte Reads (Profil, Status, relevante Dateien)
- Keine breiten Repo-Scans

VORHERIGER OUTPUT (kurz, no logs):
$prevText

FULL HANDOFF (nur bei Bedarf oeffnen):
$prevRef

PRUEFKRITERIEN (4 Dimensionen):
1. MECHANISCH: Plan vollstaendig? Schritte klar? Acceptance Criteria messbar?
2. ARCHITEKTUR: Passt zu ADRs? Keine Widersprueche?
3. INTEGRATION: Werden alle betroffenen Dateien genannt? (siehe Known Integration Points im Profil)
4. KONZEPTIONELL: Globale Werte wo spezifische noetig? Known Bugs vermieden?

RED FLAGS (sofort REJECTED):
- Globale Thresholds in team-spezifischem System (BUG-001)
- Feature ohne Orchestrator-Integration (BUG-003)
- Cross-File Aenderung ohne alle Dateien (Known Integration Points)

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: APPROVED
task: $safeTaskId
role: PROXY
phase: PROXY_PLAN
reviewed_handoff: "<nur filename oder leer>"
summary:
  - <max 8 bullets>
---
# Rule Confirmation
- Rule 1 (SYSTEM_STATUS + ADR/Docs + git status): CONFIRMED/UNVERIFIED
- Rule 2 (granularity stated): <global|per-market|per-league|per-team>
- Rule 3 (semantics defined): <fields/keys>
- Rule 4 (target metric): <accuracy|calibration|bet-selection>
- Rule 5 (helper-only boundaries): CONFIRMED/UNVERIFIED
- Rule 6 (reproducibility): <command + output path> or UNVERIFIED (no placeholders)

## Task Setup
- Granularity: <global|per-market|per-league|per-team>
- Semantics: <key fields/definitions>
- Target metric: <accuracy|calibration|bet-selection>

## Repro Commands
- <command> -> <output path> or UNVERIFIED

# Proxy Review

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki0_${safeTaskId}_PROXY_PLAN_${timestamp}.md
- YAML Frontmatter mit status:
  - APPROVED: Plan ist gut, weiter zu Executor
  - REJECTED: Bug gefunden, zurueck zu Architect
  - ESCALATE: User-Entscheidung noetig (Architektur-Frage, Design-Wahl)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung (max 8 bullets)
"@
        }
        "EXECUTOR" {
            $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
            $ki = $script:Roles.EXECUTOR
            return $baseContext + @"
ROLLE: EXECUTOR
AUFGABE: Fuehre den genehmigten Plan aus.

EFFIZIENZ-REGELN:
- Starte mit WORKING SET; vermeide Repo-weite Scans. Wenn du suchen musst: 1 gezieltes Grep pro Subtask, nicht breit.
- Schreibe nur kurze, entscheidungsrelevante Logs; grosse Logs nach AI_COLLABORATION/ARTIFACTS/ auslagern und verlinken.
- Aktualisiere Status ausschliesslich ueber den Handoff (keine CURRENT_STATUS edits im Body).
- Aendere niemals AI_COLLABORATION/MESSAGE_QUEUE/* oder AI_COLLABORATION/RESULTS/CURRENT_STATUS.md (nur Handoff-Ausgabe).
- Vermeide das Ausgeben von Diffs (diff --git, Patch-Blöcke). In der Antwort nur Summary + Pfade.

PLAN (kurz):
$prevText

FULL PLAN (nur bei Bedarf):
$prevRef

REGELN:
1. Folge Checkliste exakt
2. Keine eigenen Interpretationen
3. Dokumentiere jeden Schritt
4. WICHTIG: Fuege files_changed: [...] im YAML hinzu

TOKEN HYGIENE:
- Final Output muss direkt das Handoff-Markdown sein (keine Diffs, keine Zusatztexte).
- Keine langen Command-Outputs im Handoff
- Bei Fehlern: nur Command + 20 Zeilen excerpt
- Lange Logs: speichere in AI_COLLABORATION/ARTIFACTS/ und referenziere nur Pfad

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: COMPLETE
task: $safeTaskId
role: EXECUTOR
phase: EXECUTOR
files_changed: []
summary:
  - <max 8 bullets>
---
# Rule Confirmation
- Rule 1 (SYSTEM_STATUS + ADR/Docs + git status): CONFIRMED/UNVERIFIED
- Rule 2 (granularity stated): <global|per-market|per-league|per-team>
- Rule 3 (semantics defined): <fields/keys>
- Rule 4 (target metric): <accuracy|calibration|bet-selection>
- Rule 5 (helper-only boundaries): CONFIRMED/UNVERIFIED
- Rule 6 (reproducibility): <command + output path> or UNVERIFIED (no placeholders)

## Task Setup
- Granularity: <global|per-market|per-league|per-team>
- Semantics: <key fields/definitions>
- Target metric: <accuracy|calibration|bet-selection>

## Repro Commands
- <command> -> <output path> or UNVERIFIED

# Umsetzung

WICHTIG: Erstelle Handoff-Datei wenn fertig:
- Datei: AI_COLLABORATION/HANDOFFS/${ki}_${safeTaskId}_EXECUTOR_${timestamp}.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
"@
        }
        "PROXY_IMPL" {
            $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
            return $baseContext + @"
ROLLE: PROXY (User-Stellvertreter mit Projekt-Kontext)
AUFGABE: Pruefe die Implementation - NICHT nur mechanisch, sondern auf Architektur-Konsistenz.

PFLICHTLEKTUERE (vor Review):
1. AI_COLLABORATION/KI_PROFILES/ki0_proxy.md - Known Bugs & Integration Points
2. AI_COLLABORATION/SYSTEM_STATUS.json - Bei Architektur-Fragen

EFFIZIENZ-REGELN:
- Arbeite mit VORHERIGER OUTPUT + WORKING SET + Profil-Wissen
- Maximal 3-4 gezielte Reads
- Minimaler Sanity-Check (python -m py_compile, JSON-Validierung)

VORHERIGER OUTPUT (kurz):
$prevText

FULL HANDOFF:
$prevRef

PRUEFKRITERIEN (4 Dimensionen):
1. MECHANISCH: Alle Schritte ausgefuehrt? Syntax OK? Acceptance Criteria erfuellt?
2. ARCHITEKTUR: Implementation passt zu ADRs? Keine Widersprueche eingefuehrt?
3. INTEGRATION: ALLE betroffenen Dateien geaendert? (siehe Known Integration Points)
   - hybrid_prediction_engine.py geaendert? -> production_orchestrator.py pruefen!
   - Config geaendert? -> Code der Config liest pruefen!
   - Threshold geaendert? -> Ist er global oder spezifisch?
4. KNOWN BUGS: Keiner der 10 Known Bugs reproduziert? (BUG-001 bis BUG-010)

RED FLAGS (sofort REJECTED):
- Aenderung in Datei A ohne korrespondierende Aenderung in Datei B
- Globale Werte wo spezifische noetig (BUG-001)
- Feature implementiert aber nicht im Orchestrator eingebunden (BUG-003)
- Config-Pfad im Code stimmt nicht mit YAML-Struktur (BUG-002)

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: APPROVED
task: $safeTaskId
role: PROXY
phase: PROXY_IMPL
reviewed_handoff: "<nur filename oder leer>"
summary:
  - <max 8 bullets>
---
# Rule Confirmation
- Rule 1 (SYSTEM_STATUS + ADR/Docs + git status): CONFIRMED/UNVERIFIED
- Rule 2 (granularity stated): <global|per-market|per-league|per-team>
- Rule 3 (semantics defined): <fields/keys>
- Rule 4 (target metric): <accuracy|calibration|bet-selection>
- Rule 5 (helper-only boundaries): CONFIRMED/UNVERIFIED
- Rule 6 (reproducibility): <command + output path> or UNVERIFIED (no placeholders)

## Task Setup
- Granularity: <global|per-market|per-league|per-team>
- Semantics: <key fields/definitions>
- Target metric: <accuracy|calibration|bet-selection>

## Repro Commands
- <command> -> <output path> or UNVERIFIED

# Proxy Review (Implementation)

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki0_${safeTaskId}_PROXY_IMPL_${timestamp}.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
"@
        }
        "VALIDATOR" {
            $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
            $ki = $script:Roles.VALIDATOR
            return $baseContext + @"
ROLLE: VALIDATOR
AUFGABE: Validiere die Implementation.

EFFIZIENZ-REGELN:
- Tests nur zielgerichtet (klein starten). Keine riesigen Logs in die Antwort; speichere nach AI_COLLABORATION/ARTIFACTS/ und verlinke.
- Vermeide Repo-weite Scans; nutze WORKING SET + gezielte Reads.

VORHERIGER OUTPUT (kurz):
$prevText

FULL HANDOFF:
$prevRef

VALIDIERUNG:
1. Fuehre minimale Tests aus (zielgerichtet)
2. Pruefe Code-Qualitaet
3. Verifiziere Acceptance Criteria

TOKEN HYGIENE:
- Bei Test FAIL: nur Command + kurze Fehlermeldung (max 20 Zeilen)
- Mehr Log noetig? Speichere in AI_COLLABORATION/ARTIFACTS/ und referenziere Pfad

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: APPROVED
task: $safeTaskId
role: VALIDATOR
phase: VALIDATOR
validated_handoff: "<nur filename oder leer>"
summary:
  - <max 8 bullets>
---
# Rule Confirmation
- Rule 1 (SYSTEM_STATUS + ADR/Docs + git status): CONFIRMED/UNVERIFIED
- Rule 2 (granularity stated): <global|per-market|per-league|per-team>
- Rule 3 (semantics defined): <fields/keys>
- Rule 4 (target metric): <accuracy|calibration|bet-selection>
- Rule 5 (helper-only boundaries): CONFIRMED/UNVERIFIED
- Rule 6 (reproducibility): <command + output path> or UNVERIFIED (no placeholders)

## Task Setup
- Granularity: <global|per-market|per-league|per-team>
- Semantics: <key fields/definitions>
- Target metric: <accuracy|calibration|bet-selection>

## Repro Commands
- <command> -> <output path> or UNVERIFIED

# Validation

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/${ki}_${safeTaskId}_VALIDATOR_${timestamp}.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
"@
        }
        "PROXY_FINAL" {
            $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
            return $baseContext + @"
ROLLE: PROXY (User-Stellvertreter - Finale Freigabe)
AUFGABE: Finale Freigabe mit Projekt-Perspektive.

PFLICHTLEKTUERE (kurz):
1. AI_COLLABORATION/KI_PROFILES/ki0_proxy.md - Falls Zweifel an Integration

EFFIZIENZ-REGELN:
- Nutze VALIDATOR OUTPUT + dein Wissen aus vorherigen Proxy-Phasen
- Keine weiteren Tests, nur finale Entscheidung

VALIDATOR OUTPUT (kurz):
$prevText

FULL VALIDATOR HANDOFF:
$prevRef

FINALE PRUEFUNG:
1. Hat Validator alle kritischen Aspekte geprueft?
2. Wuerde der USER diese Aenderung akzeptieren?
3. Gibt es offene Architektur-Fragen die der User entscheiden sollte?

ESKALATION an User wenn:
- Architektur-Entscheidung noetig die nicht in ADRs dokumentiert ist
- Unsicherheit ueber globale vs spezifische Werte
- Potenzielle Breaking Changes

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: COMPLETE
task: $safeTaskId
role: PROXY
phase: PROXY_FINAL
summary:
  - <max 8 bullets>
---
# Rule Confirmation
- Rule 1 (SYSTEM_STATUS + ADR/Docs + git status): CONFIRMED/UNVERIFIED
- Rule 2 (granularity stated): <global|per-market|per-league|per-team>
- Rule 3 (semantics defined): <fields/keys>
- Rule 4 (target metric): <accuracy|calibration|bet-selection>
- Rule 5 (helper-only boundaries): CONFIRMED/UNVERIFIED
- Rule 6 (reproducibility): <command + output path> or UNVERIFIED (no placeholders)

## Task Setup
- Granularity: <global|per-market|per-league|per-team>
- Semantics: <key fields/definitions>
- Target metric: <accuracy|calibration|bet-selection>

## Repro Commands
- <command> -> <output path> or UNVERIFIED

# Proxy Final Review

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki0_${safeTaskId}_PROXY_FINAL_${timestamp}.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
"@
        }
    }
    return $baseContext
}

function Get-ExpectedHandoffOutputPath {
    param([string]$PromptText)

    if (-not $PromptText) { return $null }

    # Extract the handoff target path from the prompt so runners can persist the final message.
    # Example line: "- Datei: AI_COLLABORATION/HANDOFFS/ki2_task_EXECUTOR_yyyymmdd_hhmmss.md"
    $m = [regex]::Match(
        $PromptText,
        "(?m)^- Datei:\s*(AI_COLLABORATION/HANDOFFS/[A-Za-z0-9_.-]+\.md)\s*$"
    )
    if (-not $m.Success) { return $null }

    $rel = $m.Groups[1].Value.Trim()
    if (-not $rel) { return $null }

    return (Join-Path $script:ProjectRoot $rel)
}

function Start-KI-Process {
    param(
        [string]$KI,
        [string]$Prompt,
        [string]$TaskId = "",
        [string]$Phase = "",
        [ValidateSet("claude", "codex")]
        [string]$Backend = ""
    )

    $backend = if ($Backend) { $Backend } else { Get-KiBackend -Ki $KI }

    # V4 EFFICIENCY: Phase-specific turn limits and tool restrictions
    $maxTurns = $ClaudeMaxTurns  # default
    $skipPermissions = $true
    $allowedTools = ""

    switch ($Phase) {
        # Claude Code tool names (prefer search tools before broad Read()).
        "PROXY_PLAN"  { $maxTurns = $ClaudeMaxTurns; $allowedTools = "Read,Glob,Grep,Bash" }
        "PROXY_IMPL"  { $maxTurns = $ClaudeMaxTurns; $allowedTools = "Read,Glob,Grep,Bash" }
        "PROXY_FINAL" { $maxTurns = $ClaudeMaxTurns; $allowedTools = "Read,Glob,Grep,Bash" }
        "ARCHITECT"   { $maxTurns = $ClaudeMaxTurns; $allowedTools = "Read,Glob,Grep,Bash" }
        "EXECUTOR"    { $maxTurns = $ClaudeMaxTurns; $allowedTools = "Read,Edit,Write,Bash" }
        "VALIDATOR"   { $maxTurns = $ClaudeMaxTurns; $allowedTools = "Read,Glob,Grep,Bash" }
    }

    # V4: --max-turns nur wenn > 0 (0 = unlimited)
    $maxTurnsFlag = if ($maxTurns -gt 0) { "--max-turns $maxTurns" } else { "" }

    # === WORKING SET GUARD CONTEXT (passed to Claude Code hooks) ===
    $wsFile = ""
    if ($EnableWorkingSetGuard -and $TaskId) {
        $wsFile = Get-WorkingSetPath -TaskId $TaskId
        if (-not (Test-Path $wsFile)) { "[]" | Set-Content -Path $wsFile -Encoding UTF8 }
    }

    $strictGuard = "0"
    if ($EnableWorkingSetGuard) {
        if ($Phase -in @("PROXY_PLAN","PROXY_IMPL","PROXY_FINAL","ARCHITECT","VALIDATOR")) { $strictGuard = "1" }
    }

    $guardMaxBytes = if ($strictGuard -eq "1") { $GuardMaxReadBytesProxy } else { $GuardMaxReadBytesExecutor }
    $guardPatterns = ($GuardHardBlockPatterns -join ";")
    $guardPaths = ($GuardHardBlockPaths -join ";")


    $toolHint = if ($allowedTools) { $allowedTools } else { "(default)" }
    if ($backend -eq "claude") {
        Write-Log "Starting $KI ($Phase) with claude backend (allowed-tools: $toolHint)..." "INFO"
    } else {
        Write-Log "Starting $KI ($Phase) with codex backend (tool-hint: $toolHint)..." "INFO"
    }

    if ($DryRun) {
        Write-Log "[DRY-RUN] Would start $KI" "DEBUG"
        return $null
    }

    # Save prompt to a runtime artifact file (avoids command line length limit)
    # NOTE: Do NOT write into AI_COLLABORATION/TEMP because those files are tracked in git.
    $runtimeDir = Join-Path $script:ProjectRoot "AI_COLLABORATION/ARTIFACTS/v4_runtime"
    Ensure-Dir -Path $runtimeDir

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $safePhase = Sanitize-FileNameComponent -Value $Phase
    $promptFile = Join-Path $runtimeDir "prompt_${KI}_${safePhase}_${timestamp}.md"
    $promptDir = Split-Path $promptFile -Parent
    if (-not (Test-Path $promptDir)) { New-Item -ItemType Directory -Path $promptDir -Force | Out-Null }
    $Prompt | Set-Content $promptFile -Encoding UTF8

    try {
        # Use a wrapper script to pipe prompt to claude/codex (avoids Windows command line length limit)
        $wrapperScript = Join-Path $runtimeDir "run_${KI}_${safePhase}_${timestamp}.ps1"

        # Persist the model's final message to the expected handoff file to avoid "completion wait" thrash.
        $handoffOut = Get-ExpectedHandoffOutputPath -PromptText $Prompt
        if ($handoffOut) {
            Ensure-Dir -Path (Split-Path $handoffOut -Parent)
        }

        if ($backend -eq "claude") {
            # Prefer `--tools` (available tool set) to reduce accidental tool usage; only works with --print.
            $toolsFlag = if ($allowedTools) { "--tools $allowedTools" } else { "" }
            $permissionsFlag = if ($skipPermissions) { "--dangerously-skip-permissions" } else { "" }

            if ($handoffOut) {
                # Windows PowerShell 5.1 Tee-Object has no -Encoding; write UTF-8 explicitly.
                $wrapperContent = @"
Set-Location '$($script:ProjectRoot)'
$env:ALOOP_PROJECT_ROOT = '$($script:ProjectRoot)'
$env:ALOOP_TASK_ID = '$TaskId'
$env:ALOOP_PHASE = '$Phase'
$env:ALOOP_WORKING_SET_FILE = '$wsFile'
$env:ALOOP_GUARD_STRICT = '$strictGuard'
$env:ALOOP_GUARD_MAX_READ_BYTES = '$guardMaxBytes'
$env:ALOOP_GUARD_BLOCK_PATTERNS = '$guardPatterns'
$env:ALOOP_GUARD_BLOCK_PATHS = '$guardPaths'
`$out = Get-Content '$promptFile' | & '$ClaudePath' --print --model $ClaudeModel $maxTurnsFlag $permissionsFlag $toolsFlag $($script:SystemPromptFlag)
`$out | Set-Content -Path '$handoffOut' -Encoding UTF8
`$out
exit $LASTEXITCODE
"@
            } else {
                $wrapperContent = @"
Set-Location '$($script:ProjectRoot)'
$env:ALOOP_PROJECT_ROOT = '$($script:ProjectRoot)'
$env:ALOOP_TASK_ID = '$TaskId'
$env:ALOOP_PHASE = '$Phase'
$env:ALOOP_WORKING_SET_FILE = '$wsFile'
$env:ALOOP_GUARD_STRICT = '$strictGuard'
$env:ALOOP_GUARD_MAX_READ_BYTES = '$guardMaxBytes'
$env:ALOOP_GUARD_BLOCK_PATTERNS = '$guardPatterns'
$env:ALOOP_GUARD_BLOCK_PATHS = '$guardPaths'
Get-Content '$promptFile' | & '$ClaudePath' --print --model $ClaudeModel $maxTurnsFlag $permissionsFlag $toolsFlag $($script:SystemPromptFlag)
exit $LASTEXITCODE
"@
            }
        }
        else {
            # Codex CLI: use non-interactive mode so piping the prompt via stdin works.
            # Interactive `codex` requires a TTY and will fail with: "stdin is not a terminal".
            $agentModeFlag = switch ($CodexAgentMode) {
                "full"     { "--dangerously-bypass-approvals-and-sandbox" }
                "limited"  { "--full-auto" }
                "readonly" { "--sandbox read-only" }
                default    { "" }
            }

            # Map project "CodexProfile" (low|medium|high) to Codex CLI config override.
            # If user provided a non-standard value, treat it as a real Codex config profile name.
            $profileLower = ($(if ($null -eq $CodexProfile) { "" } else { "$CodexProfile" })).ToLower()
            $effort = if ($profileLower -in @("low", "medium", "high")) { $profileLower } else { $CodexReasoningEffort }
            $configProfileFlag = if ($profileLower -and ($profileLower -notin @("low", "medium", "high"))) { "--profile $CodexProfile" } else { "" }
            $effortFlag = if ($effort) { "-c model_reasoning_effort=`"$effort`"" } else { "" }
            $handoffFlag = if ($handoffOut) { "-o `"$handoffOut`"" } else { "" }

            $wrapperContent = @"
Set-Location '$($script:ProjectRoot)'
Get-Content '$promptFile' -Raw | & '$CodexPath' exec --model $CodexModel $effortFlag $configProfileFlag $agentModeFlag $handoffFlag -C '$($script:ProjectRoot)' -
exit $LASTEXITCODE
"@
        }

        $wrapperContent | Set-Content $wrapperScript -Encoding UTF8

        $runLogsDir = Join-Path $script:ProjectRoot "AI_COLLABORATION/LOGS/v4_runs"
        Ensure-Dir -Path $runLogsDir
        $stdoutPath = Join-Path $runLogsDir "run_${KI}_${safePhase}_${timestamp}_${backend}.stdout.txt"
        $stderrPath = Join-Path $runLogsDir "run_${KI}_${safePhase}_${timestamp}_${backend}.stderr.txt"

        $process = Start-Process -FilePath "powershell.exe" `
            -ArgumentList "-ExecutionPolicy", "Bypass", "-File", $wrapperScript `
            -WorkingDirectory $script:ProjectRoot `
            -RedirectStandardOutput $stdoutPath `
            -RedirectStandardError $stderrPath `
            -PassThru -NoNewWindow

        $script:ProcessMeta[$process.Id] = @{
            ki = $KI
            phase = $Phase
            backend = $backend
            prompt = $promptFile
            wrapper = $wrapperScript
            stdout = $stdoutPath
            stderr = $stderrPath
            started_at = (Get-Date -Format "o")
        }

        Write-Log "$KI started (PID: $($process.Id), Backend: $backend)" "SUCCESS"
        return $process
    }
    catch {
        Write-Log "Failed to start $KI : $_" "ERROR"
        return $null
    }
}

# ============================================================================
# COMPLETION DETECTION
# ============================================================================

function Detect-Completion {
    param(
        [string]$KI,
        [string]$TaskId,
        [DateTime]$PhaseStartTime = [DateTime]::MinValue,
        [string]$Phase = ""
    )

    $today = Get-Date -Format "yyyyMMdd"

    # V4 EFFICIENCY: Task-/Phase-specific patterns
    if ($TaskId -and $Phase) {
        # Exact: ki<N>_<taskId>_<phase>_*.md
        $pattern1 = "${KI}_${TaskId}_${Phase}_*.md"
        $pattern2 = "${KI}_${TaskId}_${Phase}_*.md"
    } elseif ($TaskId) {
        # Task-specific: ki<N>_<taskId>_*.md
        $pattern1 = "${KI}_${TaskId}_*.md"
        $pattern2 = "${KI}_${TaskId}_*.md"
    } else {
        # Legacy fallback: date-based
        $pattern1 = "${KI}_${today}*.md"
        $pattern2 = "${KI}_*.md"
    }

    $handoffs = @()
    $handoffs += Get-ChildItem -Path $script:HandoffsDir -Filter $pattern1 -ErrorAction SilentlyContinue
    if ($pattern2 -ne $pattern1) {
        $handoffs += Get-ChildItem -Path $script:HandoffsDir -Filter $pattern2 -ErrorAction SilentlyContinue
    }

    # Filter by timestamp and deduplicate
    $handoffs = $handoffs |
        Where-Object { $_.LastWriteTime -gt $PhaseStartTime } |
        Sort-Object FullName -Unique |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 5

    if ($PhaseStartTime -ne [DateTime]::MinValue -and $handoffs.Count -eq 0) {
        # No files after phase start - this is expected, KI still working
        return @{ found = $false; reason = "no_files_after_phase_start" }
    }

    foreach ($file in $handoffs) {
        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        if (-not $content) { continue }

        # Check for status markers (flexible pattern - looks for keywords anywhere in Status line)
        if ($content -match "(?i)\*?\*?Status:?\*?\*?\s*[^\n]*(COMPLETE|APPROVED|REJECTED|BLOCKED|DESIGN.COMPLETE)") {
            $status = $Matches[1]
            # Normalize status
            if ($status -match "DESIGN") { $status = "COMPLETE" }
            Write-Log "Completion detected in $($file.Name): $status" "SUCCESS"
            return @{
                found = $true
                status = $status
                file = $file.Name
                content = $content
            }
        }
    }

    return @{ found = $false }
}

function Get-Latest-Handoff {
    param(
        [string]$KI,
        [string]$TaskId = "",
        [string]$Phase = ""
    )

    $today = Get-Date -Format "yyyyMMdd"

    # V4 EFFICIENCY: Task-/Phase-specific pattern
    if ($TaskId -and $Phase) {
        # Exact: ki<N>_<taskId>_<phase>_<timestamp>.md
        $pattern = "${KI}_${TaskId}_${Phase}_*.md"
    } elseif ($TaskId) {
        # Task-specific: ki<N>_<taskId>_*.md
        $pattern = "${KI}_${TaskId}_*.md"
    } else {
        # Legacy fallback: ki<N>_<date>*.md
        $pattern = "${KI}_${today}*.md"
    }

    $latest = Get-ChildItem -Path $script:HandoffsDir -Filter $pattern -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if ($latest) {
        return Get-Content $latest.FullName -Raw -ErrorAction SilentlyContinue
    }
    return ""
}

# ============================================================================
# MAIN LOOP
# ============================================================================

function Start-PlanBasedLoop {
    Write-Log "=============================================" "INFO"
    Write-Log "AUTONOMOUS LOOP V4 - Plan-Based Execution (Production)" "INFO"
    Write-Log "=============================================" "INFO"
    Write-Log "Team: $Team" "INFO"
    Write-Log "Plan: $PlanFile" "INFO"
    Write-Log "Backend: $DefaultBackend" "INFO"
    Write-Log "Completion Check: ${CompletionCheckInterval}s" "INFO"
    Write-Log "Skip Proxy: $SkipProxy" "INFO"
    Write-Log "Roles: ARCHITECT=$($script:Roles.ARCHITECT), EXECUTOR=$($script:Roles.EXECUTOR), VALIDATOR=$($script:Roles.VALIDATOR), PROXY=$($script:Roles.PROXY)" "INFO"
    Write-Log "=============================================" "INFO"

    # === SUPERVISOR INTEGRATION: Save PID for external monitoring ===
    $script:LoopPidFile = Join-Path $script:ProjectRoot "AI_COLLABORATION/LOOP_STATE/v4_loop.pid"
    $loopStateDir = Split-Path $script:LoopPidFile -Parent
    if (-not (Test-Path $loopStateDir)) { New-Item -ItemType Directory -Path $loopStateDir -Force | Out-Null }
    $PID | Set-Content -Path $script:LoopPidFile -Force
    Write-Log "Loop PID saved: $PID -> $($script:LoopPidFile)" "INFO"

    # Initialize
    Initialize-KiBackends

    $needsClaude = ($DefaultBackend -eq "claude") -or ($KiBackends -match '(?i)claude')
    if ($needsClaude) {
        $resolvedClaude = Resolve-ClaudePath -Candidate $ClaudePath
        if (-not $resolvedClaude) {
            Write-Log "Claude CLI not found. Set -ClaudePath to the full path (e.g., C:\\Users\\<user>\\.local\\bin\\claude.exe) and retry." "ERROR"
            throw "Claude CLI not found"
        }
        if ($resolvedClaude -ne $ClaudePath) {
            $ClaudePath = $resolvedClaude
            Write-Log "Claude CLI resolved to: $ClaudePath" "INFO"
        }
    }

    # Load plan
    $plan = Load-Plan -Path $PlanFile

    if (-not $plan -or $plan.tasks.Count -eq 0) {
        Write-Log "Kein gueltiger Plan gefunden! Erstelle Beispiel-Plan..." "WARNING"
        Create-SamplePlan
        $plan = Load-Plan -Path $PlanFile
    }

    Write-Log "Plan geladen: $($plan.name) mit $($plan.tasks.Count) Tasks" "INFO"

    # Generate lightweight context if enabled (88% token reduction)
    $script:SystemPromptFlag = ""
    if ($EnableLightContext) {
        Write-Log "Generating lightweight context (EnableLightContext=true)..." "INFO"
        $contextScript = Join-Path $script:ProjectRoot "scripts/generate_loop_context.py"
        $claudeMd = Join-Path $script:ProjectRoot "CLAUDE.md"
        $contextOut = Join-Path $script:ProjectRoot $LightContextPath

        if (Test-Path $contextScript) {
            try {
                # Windows: Try py launcher first, then python3, then python
                $pythonCmd = $null
                foreach ($cmd in @("py", "python3", "python")) {
                    $cmdPath = Get-Command $cmd -ErrorAction SilentlyContinue
                    if ($cmdPath -and $cmdPath.Source -notmatch "WindowsApps") {
                        $pythonCmd = $cmd
                        break
                    }
                }
                if (-not $pythonCmd) { $pythonCmd = "py" }  # Fallback to py launcher
                $result = & $pythonCmd $contextScript --plan $PlanFile --claude-md $claudeMd --output $contextOut 2>&1
                if ($LASTEXITCODE -eq 0 -and (Test-Path $contextOut)) {
                    $script:SystemPromptFlag = "--system-prompt `"$contextOut`""
                    $contextSize = (Get-Item $contextOut).Length
                    Write-Log "Light context generated: $contextOut ($contextSize bytes, ~$([math]::Round($contextSize/4)) tokens)" "SUCCESS"
                } else {
                    Write-Log "Light context generation failed, using full CLAUDE.md: $result" "WARNING"
                }
            } catch {
                Write-Log "Light context generation error: $_" "WARNING"
            }
        } else {
            Write-Log "Context generator not found: $contextScript - using full CLAUDE.md" "WARNING"
        }
    } else {
        Write-Log "Using full CLAUDE.md context (EnableLightContext=false)" "INFO"
    }

    Initialize-Metrics -PlanName $plan.name

    # DryRun: Show plan summary and exit
    if ($DryRun) {
        Write-Log "" "INFO"
        Write-Log "=============================================" "INFO"
        Write-Log "[DRY-RUN] PLAN SUMMARY" "DEBUG"
        Write-Log "=============================================" "INFO"
        foreach ($task in $plan.tasks) {
            Write-Log "  Task: $($task.name) | Status: $($task.status) | Priority: $($task.priority)" "DEBUG"
        }
        Write-Log "" "INFO"
        Write-Log "Phase Workflow:" "DEBUG"
        Write-Log "  ARCHITECT ($($script:Roles.ARCHITECT)) -> PROXY_PLAN ($($script:Roles.PROXY)) -> EXECUTOR ($($script:Roles.EXECUTOR)) -> PROXY_IMPL ($($script:Roles.PROXY)) -> VALIDATOR ($($script:Roles.VALIDATOR)) -> PROXY_FINAL ($($script:Roles.PROXY)) -> DONE" "DEBUG"
        Write-Log "" "INFO"
        Write-Log "[DRY-RUN] Exit - Kein Start im DryRun Modus" "SUCCESS"
        return
    }

    Initialize-BackendStatus

    # Single-instance guard: prevents accidentally running multiple V4 loops (which multiplies token usage).
    $lockPath = Join-Path $script:ProjectRoot "AI_COLLABORATION/MESSAGE_QUEUE/loop_v4.lock.json"
    if (-not $AllowMultiInstance) {
        try {
            if (Test-Path $lockPath) {
                $raw = Get-Content $lockPath -Raw -ErrorAction SilentlyContinue
                $lock = if ($raw) { $raw | ConvertFrom-Json -ErrorAction SilentlyContinue } else { $null }
                $pid = $null
                try { $pid = [int]$lock.pid } catch { $pid = $null }
                if ($pid) {
                    $p = Get-Process -Id $pid -ErrorAction SilentlyContinue
                    if ($p) {
                        Write-Log "Another autonomous_loop_v4 instance is already running (PID=$pid). Use -AllowMultiInstance to override." "ERROR"
                        return
                    }
                }
            }

            Ensure-Dir -Path (Split-Path $lockPath -Parent)
            @{ pid = $PID; started_at = (Get-Date -Format "o"); plan = $PlanFile } | ConvertTo-Json -Depth 3 |
                Set-Content -Path $lockPath -Encoding UTF8
        } catch { }
    }

    $currentProcess = $null
    $phaseStartTime = $null
    $lastKI = $null
    $lastCompletion = $null
    $script:CurrentPhaseMetrics = $null
    $iteration = 0

    try {
        while ($true) {
            $iteration++
            if ($MaxIterations -gt 0 -and $iteration -gt $MaxIterations) {
                Write-Log "MaxIterations erreicht ($MaxIterations). Stoppe Loop (Plan bleibt erhalten)." "WARNING"
                break
            }

            # Check for resolved escalations first
            $escalatedTasks = $plan.tasks | Where-Object { $_.status -eq "ESCALATE" }
            foreach ($escTask in $escalatedTasks) {
                $resolution = Check-EscalationResolved -TaskId $escTask.id
                if ($resolution) {
                    if ($resolution.action -eq "PROCEED") {
                        Write-Log "Escalation resolved (PROCEED): $($escTask.name)" "SUCCESS"
                        $escTask.status = "IN_PROGRESS"
                        # Phase bleibt wie sie war
                        Save-Plan -Plan $plan -Path $PlanFile
                    }
                    elseif ($resolution.action -eq "ABORT") {
                        Write-Log "Escalation resolved (ABORT): $($escTask.name)" "WARNING"
                        $escTask.status = "BLOCKED"
                        $escTask.current_phase = $null
                        Save-Plan -Plan $plan -Path $PlanFile
                    }
                    elseif ($resolution.action -eq "MODIFY") {
                        Write-Log "Escalation resolved (MODIFY): $($escTask.name) - Notes: $($resolution.notes)" "INFO"
                        # User hat Anweisungen gegeben, zurueck zu ARCHITECT
                        $escTask.status = "IN_PROGRESS"
                        $escTask.current_phase = "ARCHITECT"
                        Save-Plan -Plan $plan -Path $PlanFile
                    }
                }
            }

            # Poll external tasks for completion (every iteration, ~60s interval via CheckIntervalSeconds)
            # This enables Task-Owner model: KI starts task, continues working, gets notified on completion
            $externalNotifications = Poll-ExternalTasks
            if ($externalNotifications.Count -gt 0) {
                Write-Log "External task notifications created: $($externalNotifications.Count)" "INFO"
            }

            # Find current task (skip EXTERNAL_TASK - they run in background)
            $currentTask = $plan.tasks | Where-Object {
                $_.status -eq "IN_PROGRESS" -and $_.current_phase -ne "EXTERNAL_TASK"
            } | Select-Object -First 1

            # Check EXTERNAL_TASK tasks in background (parallel processing)
            $externalTasks = $plan.tasks | Where-Object {
                $_.status -eq "IN_PROGRESS" -and $_.current_phase -eq "EXTERNAL_TASK"
            }
            foreach ($extTask in $externalTasks) {
                # Poll external task status
                if (Test-Path $script:ExternalTasksRegistry) {
                    try {
                        $registry = Get-Content $script:ExternalTasksRegistry -Raw -Encoding UTF8 | ConvertFrom-Json
                        foreach ($regTask in $registry.active_tasks) {
                            if ($regTask.task_id -match $extTask.id -or $extTask.id -match $regTask.task_id) {
                                if ($regTask.status_file -and (Test-Path $regTask.status_file)) {
                                    $statusData = Get-Content $regTask.status_file -Raw -Encoding UTF8 | ConvertFrom-Json
                                    if ($statusData.status -eq "COMPLETED") {
                                        Write-Log "EXTERNAL_TASK completed: $($extTask.id) -> advancing to VALIDATOR" "SUCCESS"
                                        $extTask.current_phase = "VALIDATOR"
                                        Save-Plan -Plan $plan -Path $PlanFile
                                    }
                                    elseif ($statusData.status -eq "FAILED") {
                                        Write-Log "EXTERNAL_TASK failed: $($extTask.id) -> BLOCKED" "ERROR"
                                        $extTask.status = "BLOCKED"
                                        $extTask.current_phase = $null
                                        Save-Plan -Plan $plan -Path $PlanFile
                                    }
                                }
                                break
                            }
                        }
                        # Also check completed_tasks
                        foreach ($regTask in $registry.completed_tasks) {
                            if ($regTask.task_id -match $extTask.id -or $extTask.id -match $regTask.task_id) {
                                if ($extTask.current_phase -eq "EXTERNAL_TASK") {
                                    Write-Log "EXTERNAL_TASK already completed: $($extTask.id) -> advancing to VALIDATOR" "SUCCESS"
                                    $extTask.current_phase = "VALIDATOR"
                                    Save-Plan -Plan $plan -Path $PlanFile
                                }
                                break
                            }
                        }
                    }
                    catch {
                        Write-Log "Error checking external task $($extTask.id): $_" "WARNING"
                    }
                }
            }

            if (-not $currentTask) {
                # Start next pending task (skip ESCALATE - waiting for user)
                $currentTask = $plan.tasks | Where-Object { $_.status -eq "PENDING" } | Select-Object -First 1

                if (-not $currentTask) {
                    # Check if all done or if there are escalated/external tasks waiting
                    $escalatedCount = ($plan.tasks | Where-Object { $_.status -eq "ESCALATE" }).Count
                    $externalWaitingCount = ($plan.tasks | Where-Object {
                        $_.status -eq "IN_PROGRESS" -and $_.current_phase -eq "EXTERNAL_TASK"
                    }).Count

                    if ($externalWaitingCount -gt 0) {
                        Write-Log "Keine weiteren Tasks - $externalWaitingCount EXTERNAL_TASK(s) laufen im Hintergrund" "INFO"
                        Start-Sleep -Seconds 60  # Warte und pruefe erneut
                        continue
                    }
                    if ($escalatedCount -gt 0) {
                        Write-Log "Keine weiteren Tasks - $escalatedCount Task(s) warten auf User-Entscheidung" "WARNING"
                        Write-Log "Escalation-Dateien pruefen: AI_COLLABORATION/ESCALATIONS/" "INFO"
                        Start-Sleep -Seconds 30  # Warte und pruefe erneut
                        continue
                    }
                    Write-Log "=============================================" "SUCCESS"
                    Write-Log "ALLE TASKS COMPLETE!" "SUCCESS"
                    Write-Log "=============================================" "SUCCESS"
                    break
                }

                $currentTask.status = "IN_PROGRESS"
                $currentTask.current_phase = "ARCHITECT"
                Save-Plan -Plan $plan -Path $PlanFile
                Write-Log "Starte Task: $($currentTask.name)" "INFO"
                $lastCompletion = $null
            }

            $phase = $currentTask.current_phase

        # Skip proxy if requested
        if ($SkipProxy -and $phase -match "PROXY") {
            $phase = Get-Next-Phase -CurrentPhase $phase -Result "APPROVED"
            $currentTask.current_phase = $phase
            Save-Plan -Plan $plan -Path $PlanFile
            Write-Log "Proxy uebersprungen, weiter mit: $phase" "DEBUG"
            continue
        }

        # Handle DONE phase - task is complete
        if ($phase -eq "DONE") {
            Write-Log "Task COMPLETE: $($currentTask.name)" "SUCCESS"
            $currentTask.status = "COMPLETE"
            $currentTask.current_phase = $null
            Save-Plan -Plan $plan -Path $PlanFile
            $currentProcess = $null
            $phaseStartTime = $null
            $lastCompletion = $null
            continue
        }

        $ki = Get-KI-For-Phase -Phase $phase

        # === EXTERNAL_TASK SPECIAL HANDLING ===
        # When phase is EXTERNAL_TASK, poll external task status instead of launching KI
        if ($phase -eq "EXTERNAL_TASK") {
            Write-Log "Phase: EXTERNAL_TASK - Polling external task status..." "INFO"

            # Find matching external task by task_id
            $externalTaskId = $currentTask.id -replace "_.*$", ""  # Extract base task id
            $externalCompleted = $false
            $externalStatus = $null

            # Poll external task registry
            if (Test-Path $script:ExternalTasksRegistry) {
                try {
                    $registry = Get-Content $script:ExternalTasksRegistry -Raw -Encoding UTF8 | ConvertFrom-Json

                    # Check active_tasks for matching task
                    foreach ($extTask in $registry.active_tasks) {
                        if ($extTask.task_id -match $currentTask.id -or $currentTask.id -match $extTask.task_id) {
                            # Check status file
                            if ($extTask.status_file -and (Test-Path $extTask.status_file)) {
                                $statusData = Get-Content $extTask.status_file -Raw -Encoding UTF8 | ConvertFrom-Json
                                if ($statusData.status -eq "COMPLETED") {
                                    $externalCompleted = $true
                                    $externalStatus = "COMPLETED"
                                    Write-Log "External task COMPLETED: $($extTask.task_id)" "SUCCESS"
                                }
                                elseif ($statusData.status -eq "FAILED") {
                                    $externalCompleted = $true
                                    $externalStatus = "FAILED"
                                    Write-Log "External task FAILED: $($extTask.task_id)" "ERROR"
                                }
                                else {
                                    Write-Log "External task still running: $($extTask.task_id) (status: $($statusData.status), progress: $($statusData.progress_percent)%)" "DEBUG"
                                }
                            }
                            break
                        }
                    }

                    # Also check completed_tasks
                    if (-not $externalCompleted) {
                        foreach ($extTask in $registry.completed_tasks) {
                            if ($extTask.task_id -match $currentTask.id -or $currentTask.id -match $extTask.task_id) {
                                $externalCompleted = $true
                                $externalStatus = "COMPLETED"
                                Write-Log "External task already completed: $($extTask.task_id)" "SUCCESS"
                                break
                            }
                        }
                    }
                }
                catch {
                    Write-Log "Error polling external tasks: $_" "WARNING"
                }
            }

            if ($externalCompleted) {
                # Move to next phase (VALIDATOR)
                $nextPhase = $script:PhaseFlow["EXTERNAL_TASK"].next_success
                Write-Log "External task done -> moving to $nextPhase" "INFO"
                $currentTask.current_phase = $nextPhase
                Save-Plan -Plan $plan -Path $PlanFile
            }
            else {
                # Still waiting - sleep and continue
                Write-Log "Waiting ${CompletionCheckInterval}s for external task..." "DEBUG"
                Start-Sleep -Seconds $CompletionCheckInterval
            }
            continue
        }
        # === END EXTERNAL_TASK HANDLING ===

        Write-Log "Phase: $phase (KI: $ki)" "INFO"

        # If the previous process ended, first check if it still produced a completion handoff.
        # This avoids losing successful runs that exited with non-zero codes (e.g. Windows/piped stdin quirks).
        if ($currentProcess -and $currentProcess.HasExited) {
            if ($phaseStartTime) {
                $completionEarly = Detect-Completion -KI $ki -TaskId $currentTask.id -PhaseStartTime $phaseStartTime -Phase $phase
                if ($completionEarly.found) {
                    Write-Log "Phase ${phase} - $($completionEarly.status)" "SUCCESS"
                    $lastCompletion = $completionEarly
                    $completionEarly.task_id = $currentTask.id

                    $handoffPath = Join-Path $script:HandoffsDir $completionEarly.file
                    if ($EnableHandoffValidation) {
                        $validation = Test-HandoffQuality -Content $completionEarly.content -TaskId $currentTask.id -Phase $phase
                        if (-not $validation.ok) {
                            $invalid = Register-InvalidHandoff -TaskId $currentTask.id -Phase $phase -KI $ki `
                                -HandoffFile $handoffPath -Reasons $validation.reasons
                            if ($invalid.exceeded) {
                                Write-Log "Max invalid handoffs reached for $($currentTask.id)/$phase; task BLOCKED." "ERROR"
                                $currentTask.status = "BLOCKED"
                                $currentTask.current_phase = $null
                                Save-Plan -Plan $plan -Path $PlanFile
                            }
                            $currentProcess = $null
                            $phaseStartTime = $null
                            $lastCompletion = $null
                            $script:CurrentPhaseMetrics = $null
                            continue
                        }
                        Reset-InvalidHandoffCount -TaskId $currentTask.id -Phase $phase
                    }

                    Update-TaskNotesFromHandoff -TaskId $currentTask.id -Phase $phase -KI $ki `
                        -HandoffContent $completionEarly.content -HandoffFile $handoffPath
                    Update-WorkingSetFromHandoff -TaskId $currentTask.id -HandoffContent $completionEarly.content
                    $wsReq = Get-WorkingSetRequestsFromContent -Content $completionEarly.content
                    if ($EnableWorkingSetGuard -and $wsReq.Count -gt 0) {
                        $wsKey = "$($currentTask.id)|$phase"
                        $prev = 0
                        if ($script:WorkingSetRequestCounts.ContainsKey($wsKey)) { $prev = [int]$script:WorkingSetRequestCounts[$wsKey] }
                        $now = $prev + 1
                        $script:WorkingSetRequestCounts[$wsKey] = $now

                        if ($now -le $MaxWorkingSetRequestRounds) {
                            Write-Log "WORKING_SET_REQUEST detected. Expanded working set and rerunning phase $phase (round $now)." "INFO"
                            # Phase stays the same
                            $currentProcess = $null
                            $phaseStartTime = $null
                            continue
                        } else {
                            Write-Log "WORKING_SET_REQUEST rounds exceeded ($MaxWorkingSetRequestRounds). Continuing normal phase flow." "WARN"
                        }
                    }

                    $nextPhase = Get-Next-Phase -CurrentPhase $phase -Result $completionEarly.status

                    if ($nextPhase -eq "DONE") {
                        Write-Log "Task COMPLETE: $($currentTask.name)" "SUCCESS"
                        $currentTask.status = "COMPLETE"
                        $currentTask.current_phase = $null
                    }
                    elseif ($nextPhase -eq "BLOCKED") {
                        Write-Log "Task BLOCKED: $($currentTask.name)" "WARNING"
                        $currentTask.status = "BLOCKED"
                        $currentTask.current_phase = $null
                    }
                    elseif ($nextPhase -eq "ESCALATE") {
                        Write-Log "Task ESCALATE: $($currentTask.name) - User-Entscheidung erforderlich" "WARNING"
                        $currentTask.status = "ESCALATE"
                        # Phase bleibt erhalten fuer Resume nach User-Decision
                        Write-Escalation -TaskId $currentTask.id -TaskName $currentTask.name `
                            -Phase $phase -EscalatedBy $ki -Reason "User-Entscheidung erforderlich" `
                            -HandoffContent $completionEarly.content
                    }
                    elseif ($nextPhase) {
                        Write-Log "Naechste Phase: $nextPhase" "INFO"
                        $currentTask.current_phase = $nextPhase
                    }
                    else {
                        Write-Log "Phase $phase wird wiederholt..." "WARNING"
                    }

                    Save-Plan -Plan $plan -Path $PlanFile
                    $currentProcess = $null
                    $phaseStartSnapshot = $phaseStartTime
                    $phaseStartTime = $null
                    if ($script:CurrentPhaseMetrics) {
                        Record-PhaseComplete -Completion $completionEarly -PhaseStartTime $phaseStartSnapshot -PhaseMetrics $script:CurrentPhaseMetrics
                        $script:CurrentPhaseMetrics = $null
                    }
                    continue
                }
            }

            $exitCode = $currentProcess.ExitCode
            $meta = $null
            if ($script:ProcessMeta.ContainsKey($currentProcess.Id)) { $meta = $script:ProcessMeta[$currentProcess.Id] }
            $backendUsed = $(if ($meta -and $meta.backend) { $meta.backend } else { Get-KiBackend -Ki $ki })

            try {
                $rate = Detect-RateLimitInfo -Backend $backendUsed -StdoutPath $(if ($meta) { $meta.stdout } else { "" }) -StderrPath $(if ($meta) { $meta.stderr } else { "" })
                    if ($rate.is_rate_limit) {
                        Set-BackendLimited -Backend $backendUsed -Until $rate.until -Reason $rate.reason
                        if ($EnableMetrics -and $script:MetricsSummary) {
                            $script:MetricsSummary.rate_limit_events++
                            Write-MetricsSummary
                        }
                        Write-MetricsEvent -Event "RATE_LIMIT" -Data @{
                            task_id = $currentTask.id
                            phase = $phase
                            ki = $ki
                            backend = $backendUsed
                            until = $rate.until.ToString("o")
                            reason = $rate.reason
                        }
                        Write-Log "Rate-limit detected for $backendUsed; requeue phase $phase after backoff." "WARNING"
                        Start-Sleep -Seconds ([int]$SwitchBackendRequeueDelaySeconds)
                        $currentProcess = $null
                        $phaseStartTime = $null
                        continue
                }
            } catch { }

            if ($null -ne $exitCode -and $exitCode -ne 0) {
                $shouldSwitch = $false
                try {
                    if (-not $NoFallback -and [int]$exitCode -eq -1) {
                        $shouldSwitch = $true
                        Write-Log "Exit -1 detected (CLI crash/rate-limit) -> switching backend" "WARNING"
                    } elseif (-not $NoFallback -and $SwitchBackendOnExitCodes -and ($SwitchBackendOnExitCodes -contains [int]$exitCode)) {
                        $shouldSwitch = $true
                    }
                } catch { }

                if ($shouldSwitch) {
                    $cooldownUntil = (Get-Date).AddMinutes([int]$SwitchBackendExitCooldownMinutes)
                    Set-BackendLimited -Backend $backendUsed -Until $cooldownUntil -Reason ("exit_code:{0}" -f $exitCode)
                    if ($EnableMetrics -and $script:MetricsSummary) {
                        $script:MetricsSummary.backend_switches++
                        Write-MetricsSummary
                    }
                    Write-MetricsEvent -Event "BACKEND_SWITCH" -Data @{
                        task_id = $currentTask.id
                        phase = $phase
                        ki = $ki
                        backend = $backendUsed
                        exit_code = [int]$exitCode
                        cooldown_until = $cooldownUntil.ToString("o")
                    }
                    Write-Log "Backend switch triggered (exit=$exitCode). Requeue phase $phase after delay." "WARNING"
                    Start-Sleep -Seconds ([int]$SwitchBackendRequeueDelaySeconds)
                    $currentProcess = $null
                    $phaseStartTime = $null
                    continue
                }
            }
        }

        # Start KI if not running
        if (-not $currentProcess -or $currentProcess.HasExited) {
            # Check if previous process crashed (non-zero exit code, not null/empty)
            $exitCode = $currentProcess.ExitCode
            if ($currentProcess -and $currentProcess.HasExited -and $null -ne $exitCode -and $exitCode -ne 0) {
                $script:PhaseRetryCount++
                Write-Log "KI $ki crashed (ExitCode: $exitCode), Retry $script:PhaseRetryCount/$script:MaxPhaseRetries" "WARNING"

                if ($script:PhaseRetryCount -ge $script:MaxPhaseRetries) {
                    Write-Log "Max retries erreicht fuer Phase $phase - Task wird BLOCKED" "ERROR"
                    $currentTask.status = "BLOCKED"
                    $currentTask.current_phase = $null
                    Save-Plan -Plan $plan -Path $PlanFile
                    $currentProcess = $null
                    $script:PhaseRetryCount = 0
                    continue
                }
            }
            else {
                # New phase, reset retry count
                $script:PhaseRetryCount = 0
            }

            # V4 EFFICIENCY: Use Get-PreviousContext for short summaries
            $prevPhase = if ($lastKI) { Get-Previous-Phase -CurrentPhase $phase } else { "" }
            $prevCompletion = if ($lastCompletion -and $lastCompletion.found) {
                # Efficiency Fix: reuse last completion (no re-read).
                $lastCompletion
            } elseif ($lastKI) {
                # Fallback: locate latest handoff file (e.g., after loop restart).
                Get-Latest-HandoffInfo -KI $lastKI -TaskId $currentTask.id -Phase $prevPhase
            } else {
                @{ found = $false }
            }

            $previousCtx = Get-PreviousContext -Completion $prevCompletion
            $prompt = Get-Phase-Prompt -Task $currentTask -Phase $phase -PreviousOutput $previousCtx
            $promptCharsRaw = $prompt.Length
            $autoCompactUsed = $false

            # V4 EFFICIENCY: Auto-Compact if prompt too large
            if (Test-NeedsCompact -Prompt $prompt) {
                Write-Log "AUTO-COMPACT: Prompt > MaxPromptChars. Using NOTES-only context." "WARNING"
                # Rebuild prompt with empty previous output
                $autoCompactUsed = $true
                $previousCtx = @{text="(auto-compact: previous output suppressed)"; ref=""}
                $prompt = Get-Phase-Prompt -Task $currentTask -Phase $phase -PreviousOutput $previousCtx
            }

            $resolved = Resolve-BackendForKI -KI $ki
            if (-not $resolved.allow) {
                $until = $resolved.defer_until
                $seconds = 60
                if ($until) {
                    $delta = ($until - (Get-Date)).TotalSeconds
                    if ($delta -gt 0) { $seconds = [Math]::Max(10, [int][Math]::Ceiling($delta)) }
                }

                # Do not stop when both backends are limited; keep waiting until the next window.
                $sleepChunk = [Math]::Min($seconds, 600)
                $untilText = if ($until) { $until.ToString('yyyy-MM-dd HH:mm:ss') } else { "<unknown>" }
                Write-Log "All backends limited for $ki (deny=$($resolved.deny_reasons -join ',')); sleeping ${sleepChunk}s (until $untilText)" "WARNING"
                Write-MetricsEvent -Event "BACKEND_DEFER" -Data @{
                    task_id = $currentTask.id
                    phase = $phase
                    ki = $ki
                    deny_reasons = $resolved.deny_reasons
                    sleep_seconds = $sleepChunk
                    defer_until = $untilText
                }
                Start-Sleep -Seconds $sleepChunk

                # Waiting for quota windows should not consume MaxIterations (otherwise long rate-limits stop the loop).
                if ($MaxIterations -gt 0 -and $iteration -gt 0) { $iteration-- }
                continue
            }

            # Capture phase start time BEFORE launching the subprocess to avoid a race where
            # a fast model run writes the handoff file before we set $phaseStartTime.
            $phaseStartTime = Get-Date
            $currentProcess = Start-KI-Process -KI $ki -Prompt $prompt -TaskId $currentTask.id -Phase $phase -Backend $resolved.backend

            if (-not $currentProcess) {
                $phaseStartTime = $null
                Write-Log "Failed to start KI $ki - retrying next iteration" "ERROR"
                Write-MetricsEvent -Event "PHASE_START_FAILED" -Data @{
                    task_id = $currentTask.id
                    phase = $phase
                    ki = $ki
                    backend = $resolved.backend
                }
                Start-Sleep -Seconds 5
                continue
            }

            $promptChars = $prompt.Length
            $promptTokensEst = Estimate-Tokens -Chars $promptChars
            if ($autoCompactUsed) {
                Write-MetricsEvent -Event "AUTO_COMPACT" -Data @{
                    task_id = $currentTask.id
                    phase = $phase
                    ki = $ki
                    prompt_chars_raw = $promptCharsRaw
                    prompt_chars = $promptChars
                }
            }
            Record-PhaseStart -TaskId $currentTask.id -TaskName $currentTask.name -Phase $phase -KI $ki `
                -Backend $resolved.backend -PromptChars $promptChars -PromptCharsRaw $promptCharsRaw `
                -PromptTokensEst $promptTokensEst -AutoCompactUsed $autoCompactUsed -RetryCount $script:PhaseRetryCount

            $lastKI = $ki
        }

        # Wait for completion check
        Write-Log "Warte ${CompletionCheckInterval}s auf Completion..." "DEBUG"
        Start-Sleep -Seconds $CompletionCheckInterval

        # Check for completion (only files created AFTER phase start)
        $completion = Detect-Completion -KI $ki -TaskId $currentTask.id -PhaseStartTime $phaseStartTime -Phase $phase

        if ($completion.found) {
            Write-Log "Phase ${phase} - $($completion.status)" "SUCCESS"
            $lastCompletion = $completion
            $completion.task_id = $currentTask.id

            # V4 EFFICIENCY: Update Notes + Working Set from Handoff
            $handoffPath = Join-Path $script:HandoffsDir $completion.file
            if ($EnableHandoffValidation) {
                $validation = Test-HandoffQuality -Content $completion.content -TaskId $currentTask.id -Phase $phase
                if (-not $validation.ok) {
                    $invalid = Register-InvalidHandoff -TaskId $currentTask.id -Phase $phase -KI $ki `
                        -HandoffFile $handoffPath -Reasons $validation.reasons
                    if ($invalid.exceeded) {
                        Write-Log "Max invalid handoffs reached for $($currentTask.id)/$phase; task BLOCKED." "ERROR"
                        $currentTask.status = "BLOCKED"
                        $currentTask.current_phase = $null
                        Save-Plan -Plan $plan -Path $PlanFile
                    }
                    $currentProcess = $null
                    $phaseStartTime = $null
                    $lastCompletion = $null
                    $script:CurrentPhaseMetrics = $null
                    continue
                }
                Reset-InvalidHandoffCount -TaskId $currentTask.id -Phase $phase
            }

            Update-TaskNotesFromHandoff -TaskId $currentTask.id -Phase $phase -KI $ki `
                -HandoffContent $completion.content -HandoffFile $handoffPath
            Update-WorkingSetFromHandoff -TaskId $currentTask.id -HandoffContent $completion.content

            $nextPhase = Get-Next-Phase -CurrentPhase $phase -Result $completion.status

            if ($nextPhase -eq "DONE") {
                Write-Log "Task COMPLETE: $($currentTask.name)" "SUCCESS"
                $currentTask.status = "COMPLETE"
                $currentTask.current_phase = $null
            }
            elseif ($nextPhase -eq "BLOCKED") {
                Write-Log "Task BLOCKED: $($currentTask.name)" "WARNING"
                $currentTask.status = "BLOCKED"
                $currentTask.current_phase = $null
            }
            elseif ($nextPhase -eq "ESCALATE") {
                Write-Log "Task ESCALATE: $($currentTask.name) - User-Entscheidung erforderlich" "WARNING"
                $currentTask.status = "ESCALATE"
                # Phase bleibt erhalten fuer Resume nach User-Decision
                Write-Escalation -TaskId $currentTask.id -TaskName $currentTask.name `
                    -Phase $phase -EscalatedBy $ki -Reason "User-Entscheidung erforderlich" `
                    -HandoffContent $completion.content
            }
            elseif ($nextPhase) {
                Write-Log "Naechste Phase: $nextPhase" "INFO"
                $currentTask.current_phase = $nextPhase
            }
            else {
                # Retry same phase
                Write-Log "Phase $phase wird wiederholt..." "WARNING"
            }

            Save-Plan -Plan $plan -Path $PlanFile
            $currentProcess = $null
            $phaseStartSnapshot = $phaseStartTime
            $phaseStartTime = $null  # Reset for next phase
            if ($script:CurrentPhaseMetrics) {
                Record-PhaseComplete -Completion $completion -PhaseStartTime $phaseStartSnapshot -PhaseMetrics $script:CurrentPhaseMetrics
                $script:CurrentPhaseMetrics = $null
            }
        }
        else {
            # Check timeout
            if ($phaseStartTime) {
                $elapsed = (Get-Date) - $phaseStartTime
                $maxTime = $script:PhaseFlow[$phase].max_time
                if ($elapsed.TotalMinutes -gt $maxTime) {
                    Write-Log "Phase $phase Timeout nach $maxTime Minuten!" "WARNING"
                    Write-MetricsEvent -Event "PHASE_TIMEOUT" -Data @{
                        task_id = $currentTask.id
                        phase = $phase
                        ki = $ki
                        max_time_minutes = $maxTime
                    }
                    if ($currentProcess -and -not $currentProcess.HasExited) {
                        $currentProcess.Kill()
                        Write-Log "Prozess beendet" "WARNING"
                    }
                    $currentProcess = $null
                }
            }
        }
    }
    } finally {
        # === SUPERVISOR INTEGRATION: Remove PID file on exit ===
        if ($script:LoopPidFile -and (Test-Path $script:LoopPidFile)) {
            Remove-Item $script:LoopPidFile -Force -ErrorAction SilentlyContinue
            Write-Log "Loop PID file removed: $($script:LoopPidFile)" "INFO"
        }

        if ($EnableMetrics -and $script:MetricsSummary) {
            $planName = ""
            try { if ($plan -and $plan.name) { $planName = $plan.name } } catch { $planName = "" }
            $script:MetricsSummary.end_time = (Get-Date -Format "o")
            $script:MetricsSummary.duration_sec_total = [int]([math]::Round(((Get-Date) - [datetime]$script:MetricsSummary.start_time).TotalSeconds))
            Write-MetricsEvent -Event "RUN_END" -Data @{
                plan_file = $PlanFile
                plan_name = $planName
                duration_sec = $script:MetricsSummary.duration_sec_total
            }
            Write-MetricsSummary
        }
        # best-effort lock cleanup
        if (-not $AllowMultiInstance) {
            try {
                if (Test-Path $lockPath) { Remove-Item -Force $lockPath -ErrorAction SilentlyContinue }
            } catch { }
        }
    }
}

function Create-SamplePlan {
    $samplePlan = @"
# Autonomous Loop V4 - Sample Plan
# Created: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

plan:
  name: "ADR-020 Remaining Tasks"

tasks:
  - id: task_004
    name: "NEW_ML O1.5/O2.5 State-Awareness"
    priority: P2
    status: PENDING
    current_phase: null

  - id: task_005
    name: "ADR-015 Cross-Market Divergenz Detection"
    priority: P2
    status: PENDING
    current_phase: null

  - id: task_006
    name: "ADR-017 Ecosystem Phase-Detection"
    priority: P3
    status: PENDING
    current_phase: null
"@

    $planPath = Join-Path $script:ProjectRoot $PlanFile
    $planDir = Split-Path $planPath -Parent
    if (-not (Test-Path $planDir)) { New-Item -ItemType Directory -Path $planDir -Force | Out-Null }
    $samplePlan | Set-Content $planPath -Encoding UTF8
    Write-Log "Sample Plan erstellt: $planPath" "INFO"
}

# ============================================================================
# ENTRY POINT
# ============================================================================

try {
    Start-PlanBasedLoop
}
catch {
    Write-Log "FATAL ERROR: $_" "ERROR"
    Write-Log $_.ScriptStackTrace "ERROR"
    exit 1
}
