# Send Message to KI Message Queue
# Usage: .\scripts\send_message.ps1 -From "ki2" -To "ki3" -Type "HANDOFF" -Subject "Task X" -Body "Details..."

param(
    [Parameter(Mandatory=$true)]
    [string]$From,

    [Parameter(Mandatory=$true)]
    [string]$To,

    [Parameter(Mandatory=$true)]
    [string]$Type,

    [Parameter(Mandatory=$true)]
    [string]$Subject,

    [Parameter(Mandatory=$true)]
    [string]$Body,

    [string]$Priority = "normal",
    [string]$HandoffFile = ""
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
$queueDir = "AI_COLLABORATION/MESSAGE_QUEUE"

# Ensure directory exists
if (-not (Test-Path $queueDir)) {
    New-Item -ItemType Directory -Path $queueDir -Force | Out-Null
}

# Load or initialize queue
if (Test-Path $queueFile) {
    try {
        $rawContent = Get-Content $queueFile -Raw -Encoding UTF8
        $cleanContent = Repair-JsonContent -Content $rawContent
        $queue = $cleanContent | ConvertFrom-Json
    } catch {
        Write-Host "[!] Corrupt queue.json, reinitializing..." -ForegroundColor Yellow
        $queue = @{messages = @()}
    }
} else {
    $queue = @{messages = @()}
}

# Generate message ID
$messageId = "msg_" + (Get-Date -Format "yyyyMMddHHmmss")

# Create new message
$newMessage = [PSCustomObject]@{
    id = $messageId
    timestamp = (Get-Date -Format "o")
    from = $From
    to = $To
    type = $Type
    priority = $Priority
    subject = $Subject
    body = $Body
    handoff_file = $HandoffFile
    action_required = $true
    read = $false
    archived = $false
}

# Add to queue
$queue.messages += $newMessage

# Save queue with UTF8 encoding
$queue | ConvertTo-Json -Depth 10 | Set-Content $queueFile -Encoding UTF8

# Display confirmation
Write-Host ""
Write-Host "[OK] Message sent successfully!" -ForegroundColor Green
Write-Host ("=" * 60)
Write-Host "ID:       $messageId"
Write-Host "From:     $From"
Write-Host "To:       $To"
Write-Host "Type:     $Type"
Write-Host "Priority: $Priority"
Write-Host "Subject:  $Subject"
Write-Host ("=" * 60)
Write-Host ""
Write-Host "[i] Trigger: User sende 'task-ready $To'" -ForegroundColor Cyan
Write-Host ""
