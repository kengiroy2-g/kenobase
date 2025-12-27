# Read KI Inbox from Message Queue
# Usage: .\scripts\read_inbox.ps1 -KI "ki3"

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("ki0", "ki1", "ki2", "ki3", "ki4", "ki5", "ki6", "ki7", "ki8")]
    [string]$KI,

    [switch]$UnreadOnly
)

$ErrorActionPreference = "Stop"

# JSON Sanitization function (fixes invalid escape sequences from KI output)
function Repair-JsonContent {
    param([string]$Content)
    if (-not $Content) { return $Content }
    $Content = $Content -replace '\\!', '!'
    $Content = $Content -replace "\\`'", "'"
    $Content = $Content -replace '\\`', '`'
    $Content = $Content -replace '\\#', '#'
    $Content = $Content -replace '\\\$', '$'
    $Content = $Content -replace '\\\*', '*'
    $Content = $Content -replace '\\\[', '['
    $Content = $Content -replace '\\\]', ']'
    $Content = $Content -replace '\\\(', '('
    $Content = $Content -replace '\\\)', ')'
    $Content = $Content -replace '\\@', '@'
    $Content = $Content -replace '\\%', '%'
    $Content = $Content -replace '\\&', '&'
    $Content = $Content -replace '\\=', '='
    $Content = $Content -replace '\\<', '<'
    $Content = $Content -replace '\\>', '>'
    $Content = $Content -replace '\\~', '~'
    $Content = $Content -replace '\\\^', '^'
    $Content = $Content -replace '\\\|', '|'
    return $Content
}

# Paths
$queueFile = "AI_COLLABORATION/MESSAGE_QUEUE/queue.json"

# Check if queue exists
if (-not (Test-Path $queueFile)) {
    Write-Host "[!] No messages yet (queue.json not found)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Initialize with: echo '{`"messages`": []}' | Set-Content $queueFile"
    exit 0
}

# Load queue
try {
    $rawContent = Get-Content $queueFile -Raw -Encoding UTF8
    $cleanContent = Repair-JsonContent -Content $rawContent
    $queue = $cleanContent | ConvertFrom-Json
} catch {
    Write-Host "[X] Error reading queue.json (corrupt file)" -ForegroundColor Red
    Write-Host "Backup: Copy-Item $queueFile ${queueFile}.backup"
    Write-Host "Reset: echo '{`"messages`": []}' | Set-Content $queueFile"
    exit 1
}

# Filter messages for this KI
$inbox = $queue.messages | Where-Object {
    $_.to -eq $KI -and $_.archived -eq $false
}

if ($UnreadOnly) {
    $inbox = $inbox | Where-Object { $_.read -eq $false }
}

# Display inbox
Write-Host ""
Write-Host "=== Inbox for $KI ===" -ForegroundColor Cyan
Write-Host ("=" * 80)

# Count messages (handle both array and single object)
$messageCount = if ($inbox -is [array]) { $inbox.Count } elseif ($inbox) { 1 } else { 0 }
Write-Host "Total Messages: $messageCount" -ForegroundColor White

if ($UnreadOnly) {
    Write-Host "Filter: Unread only" -ForegroundColor Yellow
}

Write-Host ("=" * 80)
Write-Host ""

if ($messageCount -eq 0) {
    Write-Host "[!] No messages" -ForegroundColor Yellow
    exit 0
}

# Display each message
$counter = 1
foreach ($msg in $inbox) {
    # Status icons
    $readStatus = if ($msg.read) { "[READ]" } else { "[NEW]" }

    $priorityIcon = switch ($msg.priority) {
        "urgent" { "[URGENT]" }
        "high"   { "[HIGH]" }
        default  { "[NORMAL]" }
    }

    # Header
    Write-Host "[$counter] $readStatus $priorityIcon" -NoNewline
    Write-Host " [$($msg.type)]" -ForegroundColor Yellow -NoNewline
    Write-Host " $($msg.subject)" -ForegroundColor White

    # Details
    Write-Host "    From: $($msg.from) | Time: $($msg.timestamp)" -ForegroundColor Gray

    # Body
    Write-Host "    Body: $($msg.body)" -ForegroundColor Gray

    # Handoff file (if exists)
    if ($msg.handoff_file -and $msg.handoff_file -ne "") {
        Write-Host "    Handoff: $($msg.handoff_file)" -ForegroundColor Cyan
    }

    # Message ID
    Write-Host "    ID: $($msg.id)" -ForegroundColor DarkGray

    Write-Host ""
    Write-Host (("-" * 80))
    Write-Host ""

    $counter++
}

# Summary
$unreadCount = ($inbox | Where-Object { $_.read -eq $false }).Count
if ($unreadCount -gt 0) {
    Write-Host "[!] $unreadCount unread message(s)" -ForegroundColor Cyan
    Write-Host "[i] Mark as read: .\scripts\mark_read.ps1 -MessageId MESSAGE_ID" -ForegroundColor Cyan
    Write-Host ""
}
