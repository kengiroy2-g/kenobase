<#
.SYNOPSIS
    Resource monitor for autonomous KI task orchestration (REQ-004).

.DESCRIPTION
    Checks RAM and CPU availability before launching external tasks.
    Enforces 8GB RAM reserve and 75% CPU limit.
    Outputs JSON for KI consumption.

.PARAMETER RequestRamMB
    Optional. RAM required for planned task in MB.
    If provided, checks if task can be launched.

.PARAMETER RequestCpuPercent
    Optional. CPU percentage required for planned task.
    If provided, checks if task can be launched.

.EXAMPLE
    .\check_resources.ps1
    # Returns current system resources as JSON

.EXAMPLE
    .\check_resources.ps1 -RequestRamMB 4096 -RequestCpuPercent 50
    # Checks if a task needing 4GB RAM and 50% CPU can be launched

.NOTES
    Part of ISSUE-035: Autonomous External Process Orchestration
    Created: 2025-12-25
#>

param(
    [int]$RequestRamMB = 0,
    [int]$RequestCpuPercent = 0
)

# Constants
$RAM_RESERVE_MB = 8192  # 8GB reserve
$CPU_LIMIT_PERCENT = 75 # Max 75% CPU usage

function Get-RamInfo {
    <#
    .SYNOPSIS
        Get RAM information using CIM cmdlets.
    #>
    try {
        $os = Get-CimInstance -ClassName Win32_OperatingSystem
        $totalMB = [math]::Round($os.TotalVisibleMemorySize / 1024)
        $freeMB = [math]::Round($os.FreePhysicalMemory / 1024)

        return @{
            total_mb = $totalMB
            available_mb = $freeMB
            used_mb = $totalMB - $freeMB
            used_percent = [math]::Round(($totalMB - $freeMB) / $totalMB * 100, 1)
        }
    }
    catch {
        Write-Warning "Failed to get RAM info: $_"
        return @{
            total_mb = 0
            available_mb = 0
            used_mb = 0
            used_percent = 0
            error = $_.Exception.Message
        }
    }
}

function Get-CpuInfo {
    <#
    .SYNOPSIS
        Get CPU information using CIM cmdlets.
    #>
    try {
        $cpu = Get-CimInstance -ClassName Win32_Processor
        $cores = ($cpu | Measure-Object -Property NumberOfCores -Sum).Sum
        $logicalProcessors = ($cpu | Measure-Object -Property NumberOfLogicalProcessors -Sum).Sum

        # Get current CPU load percentage
        $loadPercent = ($cpu | Measure-Object -Property LoadPercentage -Average).Average
        if ($null -eq $loadPercent) { $loadPercent = 0 }

        return @{
            cores = $cores
            logical_processors = $logicalProcessors
            load_percent = [math]::Round($loadPercent, 1)
        }
    }
    catch {
        Write-Warning "Failed to get CPU info: $_"
        return @{
            cores = 0
            logical_processors = 0
            load_percent = 0
            error = $_.Exception.Message
        }
    }
}

function Test-ResourceAvailability {
    <#
    .SYNOPSIS
        Check if resources are available for a new task.

    .PARAMETER RamInfo
        RAM information hashtable from Get-RamInfo.

    .PARAMETER CpuInfo
        CPU information hashtable from Get-CpuInfo.

    .PARAMETER RequestRamMB
        RAM required for the task in MB.

    .PARAMETER RequestCpuPercent
        CPU percentage required for the task.
    #>
    param(
        [hashtable]$RamInfo,
        [hashtable]$CpuInfo,
        [int]$RequestRamMB,
        [int]$RequestCpuPercent
    )

    $warnings = @()
    $canLaunch = $true

    # Calculate available RAM after reserve
    $availableAfterReserve = $RamInfo.available_mb - $RAM_RESERVE_MB
    if ($availableAfterReserve -lt 0) { $availableAfterReserve = 0 }

    # Calculate available CPU headroom
    $cpuHeadroom = $CPU_LIMIT_PERCENT - $CpuInfo.load_percent
    if ($cpuHeadroom -lt 0) { $cpuHeadroom = 0 }

    # Check RAM reserve
    if ($RamInfo.available_mb -lt $RAM_RESERVE_MB) {
        $warnings += "LOW_RAM: Available $($RamInfo.available_mb)MB < $($RAM_RESERVE_MB)MB reserve"
        $canLaunch = $false
    }

    # Check CPU limit
    if ($CpuInfo.load_percent -gt $CPU_LIMIT_PERCENT) {
        $warnings += "HIGH_CPU: Load $($CpuInfo.load_percent)% > $($CPU_LIMIT_PERCENT)% limit"
        $canLaunch = $false
    }

    # Check if request can be fulfilled
    $requestFeasible = $true
    if ($RequestRamMB -gt 0) {
        if ($RequestRamMB -gt $availableAfterReserve) {
            $warnings += "REQUEST_RAM_EXCEEDS: Need $($RequestRamMB)MB but only $($availableAfterReserve)MB available after reserve"
            $requestFeasible = $false
        }
    }

    if ($RequestCpuPercent -gt 0) {
        if ($RequestCpuPercent -gt $cpuHeadroom) {
            $warnings += "REQUEST_CPU_EXCEEDS: Need $($RequestCpuPercent)% but only $($cpuHeadroom)% headroom"
            $requestFeasible = $false
        }
    }

    return @{
        can_launch = $canLaunch
        request_feasible = $requestFeasible
        available_ram_after_reserve_mb = $availableAfterReserve
        cpu_headroom_percent = [math]::Round($cpuHeadroom, 1)
        warnings = $warnings
    }
}

# Main execution
try {
    $ramInfo = Get-RamInfo
    $cpuInfo = Get-CpuInfo
    $availability = Test-ResourceAvailability -RamInfo $ramInfo -CpuInfo $cpuInfo -RequestRamMB $RequestRamMB -RequestCpuPercent $RequestCpuPercent

    $result = @{
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        system = @{
            ram = $ramInfo
            cpu = $cpuInfo
        }
        limits = @{
            ram_reserve_mb = $RAM_RESERVE_MB
            cpu_limit_percent = $CPU_LIMIT_PERCENT
        }
        availability = @{
            can_launch_task = $availability.can_launch
            available_ram_after_reserve_mb = $availability.available_ram_after_reserve_mb
            cpu_headroom_percent = $availability.cpu_headroom_percent
        }
        request = @{
            ram_mb = $RequestRamMB
            cpu_percent = $RequestCpuPercent
            feasible = $availability.request_feasible
        }
        warnings = $availability.warnings
    }

    # Output as JSON
    $result | ConvertTo-Json -Depth 4

    # Exit code: 0 = can launch, 1 = cannot launch
    if (-not $availability.can_launch) {
        exit 1
    }
    if ($RequestRamMB -gt 0 -or $RequestCpuPercent -gt 0) {
        if (-not $availability.request_feasible) {
            exit 2
        }
    }
    exit 0
}
catch {
    $errorResult = @{
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        error = $_.Exception.Message
        can_launch_task = $false
    }
    $errorResult | ConvertTo-Json -Depth 2
    exit 1
}
