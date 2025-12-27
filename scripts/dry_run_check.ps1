<#
.SYNOPSIS
    Dry-run validation before external task execution (REQ-008).

.DESCRIPTION
    Validates scripts before external execution using:
    1. SCRIPT_CATALOG.json lookup for dry_run_supported flag
    2. Native dry-run execution if supported
    3. Fallback to syntax validation (py_compile or PS Parser)

    Exit codes:
    - 0: Validation passed
    - 1: Validation failed (syntax error or dry-run failure)
    - 2: Script not found in catalog (no validation possible)

.PARAMETER ScriptPath
    Path to the script to validate (required).

.PARAMETER CatalogPath
    Path to SCRIPT_CATALOG.json. Default: AI_COLLABORATION/SCRIPT_CATALOG.json

.PARAMETER SkipCatalog
    Skip catalog lookup and use syntax fallback only.

.EXAMPLE
    .\dry_run_check.ps1 -ScriptPath "scripts/MASTER_RECALIBRATION.ps1"

.EXAMPLE
    .\dry_run_check.ps1 -ScriptPath "hybrid_prediction_engine.py" -SkipCatalog

.NOTES
    Part of ISSUE-035: Autonomous External Process Orchestration
    Implements REQ-008: Dry-Run validation
    Created: 2025-12-25
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ScriptPath,

    [string]$CatalogPath = "AI_COLLABORATION/SCRIPT_CATALOG.json",

    [switch]$SkipCatalog
)

# ============================================================================
# CONSTANTS
# ============================================================================
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$REPO_ROOT = Split-Path -Parent $SCRIPT_DIR

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

function Get-AbsolutePath {
    <#
    .SYNOPSIS
        Convert relative path to absolute path.
    #>
    param([string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }
    return Join-Path $REPO_ROOT $Path
}

function Get-ScriptFromCatalog {
    <#
    .SYNOPSIS
        Look up script in SCRIPT_CATALOG.json.
    #>
    param([string]$ScriptPath, [string]$CatalogPath)

    $absPath = Get-AbsolutePath -Path $CatalogPath

    if (-not (Test-Path $absPath)) {
        Write-Warning "Catalog not found: $absPath"
        return $null
    }

    try {
        $catalog = Get-Content $absPath -Raw -Encoding UTF8 | ConvertFrom-Json

        # Normalize script path for comparison
        $normalizedPath = $ScriptPath -replace '\\', '/'

        foreach ($script in $catalog.scripts) {
            $scriptPathNorm = $script.path -replace '\\', '/'
            if ($scriptPathNorm -eq $normalizedPath -or
                $scriptPathNorm -like "*$normalizedPath" -or
                $normalizedPath -like "*$scriptPathNorm") {
                return $script
            }
        }

        return $null
    }
    catch {
        Write-Warning "Failed to parse catalog: $($_.Exception.Message)"
        return $null
    }
}

function Test-PythonSyntax {
    <#
    .SYNOPSIS
        Validate Python file syntax using py_compile.
    #>
    param([string]$FilePath)

    $absPath = Get-AbsolutePath -Path $FilePath

    if (-not (Test-Path $absPath)) {
        return @{
            success = $false
            message = "File not found: $absPath"
        }
    }

    try {
        $result = & python -m py_compile $absPath 2>&1
        $exitCode = $LASTEXITCODE

        if ($exitCode -eq 0) {
            return @{
                success = $true
                message = "Python syntax OK: $FilePath"
            }
        }
        else {
            return @{
                success = $false
                message = "Python syntax error: $result"
            }
        }
    }
    catch {
        return @{
            success = $false
            message = "py_compile failed: $($_.Exception.Message)"
        }
    }
}

function Test-PowerShellSyntax {
    <#
    .SYNOPSIS
        Validate PowerShell file syntax using Parser.
    #>
    param([string]$FilePath)

    $absPath = Get-AbsolutePath -Path $FilePath

    if (-not (Test-Path $absPath)) {
        return @{
            success = $false
            message = "File not found: $absPath"
        }
    }

    try {
        $errors = $null
        $tokens = $null
        $ast = [System.Management.Automation.Language.Parser]::ParseFile(
            $absPath,
            [ref]$tokens,
            [ref]$errors
        )

        if ($errors.Count -eq 0) {
            return @{
                success = $true
                message = "PowerShell syntax OK: $FilePath"
            }
        }
        else {
            $errorDetails = $errors | ForEach-Object { $_.Message } | Select-Object -First 3
            return @{
                success = $false
                message = "PowerShell syntax errors: $($errorDetails -join '; ')"
            }
        }
    }
    catch {
        return @{
            success = $false
            message = "Parser failed: $($_.Exception.Message)"
        }
    }
}

function Invoke-NativeDryRun {
    <#
    .SYNOPSIS
        Execute script's native dry-run command.
    #>
    param([string]$ScriptPath, [string]$DryRunFlag)

    $absPath = Get-AbsolutePath -Path $ScriptPath

    if (-not (Test-Path $absPath)) {
        return @{
            success = $false
            message = "Script not found: $absPath"
        }
    }

    try {
        $ext = [System.IO.Path]::GetExtension($absPath).ToLower()

        if ($ext -eq ".py") {
            $result = & python $absPath $DryRunFlag 2>&1
        }
        elseif ($ext -eq ".ps1") {
            $result = & powershell -NoProfile -File $absPath $DryRunFlag 2>&1
        }
        else {
            return @{
                success = $false
                message = "Unsupported script type: $ext"
            }
        }

        $exitCode = $LASTEXITCODE

        if ($exitCode -eq 0) {
            return @{
                success = $true
                message = "Dry-run passed: $ScriptPath $DryRunFlag"
            }
        }
        else {
            $errorOutput = $result | Where-Object { $_ -match 'error|exception|fail' } | Select-Object -First 3
            return @{
                success = $false
                message = "Dry-run failed (exit $exitCode): $($errorOutput -join '; ')"
            }
        }
    }
    catch {
        return @{
            success = $false
            message = "Dry-run execution failed: $($_.Exception.Message)"
        }
    }
}

function Get-ScriptType {
    <#
    .SYNOPSIS
        Determine script type from extension.
    #>
    param([string]$ScriptPath)

    $ext = [System.IO.Path]::GetExtension($ScriptPath).ToLower()

    switch ($ext) {
        ".py"  { return "python" }
        ".ps1" { return "powershell" }
        default { return "unknown" }
    }
}

# ============================================================================
# MAIN VALIDATION LOGIC
# ============================================================================

function Invoke-DryRunValidation {
    param([string]$ScriptPath, [string]$CatalogPath, [bool]$SkipCatalog)

    $result = [ordered]@{
        script_path = $ScriptPath
        script_type = Get-ScriptType -ScriptPath $ScriptPath
        validation_method = ""
        passed = $false
        message = ""
        catalog_entry = $null
        timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
    }

    # Step 1: Check if script file exists
    $absScriptPath = Get-AbsolutePath -Path $ScriptPath
    if (-not (Test-Path $absScriptPath)) {
        $result.validation_method = "file_check"
        $result.passed = $false
        $result.message = "Script file not found: $absScriptPath"
        return $result
    }

    # Step 2: Catalog lookup (unless skipped)
    $catalogEntry = $null
    if (-not $SkipCatalog) {
        $catalogEntry = Get-ScriptFromCatalog -ScriptPath $ScriptPath -CatalogPath $CatalogPath
        $result.catalog_entry = $catalogEntry
    }

    # Step 3: Choose validation method
    if ($catalogEntry -and $catalogEntry.dry_run_supported -eq $true) {
        # Use native dry-run
        $result.validation_method = "native_dry_run"
        $dryRunFlag = $catalogEntry.dry_run_flag

        if (-not $dryRunFlag) {
            $dryRunFlag = "--dry-run"  # Default flag
        }

        $validationResult = Invoke-NativeDryRun -ScriptPath $ScriptPath -DryRunFlag $dryRunFlag
        $result.passed = $validationResult.success
        $result.message = $validationResult.message
    }
    else {
        # Fallback to syntax validation
        $result.validation_method = "syntax_check"

        switch ($result.script_type) {
            "python" {
                $validationResult = Test-PythonSyntax -FilePath $ScriptPath
                $result.passed = $validationResult.success
                $result.message = $validationResult.message
            }
            "powershell" {
                $validationResult = Test-PowerShellSyntax -FilePath $ScriptPath
                $result.passed = $validationResult.success
                $result.message = $validationResult.message
            }
            default {
                $result.passed = $false
                $result.message = "Unsupported script type: $($result.script_type)"
            }
        }
    }

    return $result
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

try {
    # Run validation
    $validationResult = Invoke-DryRunValidation -ScriptPath $ScriptPath -CatalogPath $CatalogPath -SkipCatalog $SkipCatalog

    # Output JSON result
    $validationResult | ConvertTo-Json -Depth 3

    # Determine exit code
    if ($validationResult.passed) {
        Write-Host "`n[PASS] $($validationResult.message)" -ForegroundColor Green
        exit 0
    }
    else {
        Write-Host "`n[FAIL] $($validationResult.message)" -ForegroundColor Red

        # Exit 2 if catalog not found, else 1
        if ($validationResult.catalog_entry -eq $null -and -not $SkipCatalog) {
            exit 2
        }
        exit 1
    }
}
catch {
    Write-Error "Validation error: $($_.Exception.Message)"
    exit 1
}
