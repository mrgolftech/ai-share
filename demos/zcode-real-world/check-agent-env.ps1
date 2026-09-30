$ErrorActionPreference = "Continue"

$checks = @(
    @{ Name = "git"; Commands = @("git"); Args = @("--version"); Required = $true },
    @{ Name = "python"; Commands = @("python", "py"); Args = @("--version"); Required = $true },
    @{ Name = "node"; Commands = @("node"); Args = @("--version"); Required = $true },
    @{ Name = "npm"; Commands = @("npm"); Args = @("--version"); Required = $true },
    @{ Name = "curl"; Commands = @("curl.exe", "curl"); Args = @("--version"); Required = $true },
    @{ Name = "ssh"; Commands = @("ssh"); Args = @("-V"); Required = $false },
    @{ Name = "docker"; Commands = @("docker"); Args = @("--version"); Required = $false }
)

$failed = 0

Write-Host "=== Agent Environment Preflight ==="
Write-Host "PATH=$env:PATH"
Write-Host ""

foreach ($check in $checks) {
    $found = $null
    foreach ($candidate in $check.Commands) {
        $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($cmd) {
            $found = $candidate
            break
        }
    }

    if (-not $found) {
        $level = if ($check.Required) { "FAIL" } else { "OPTIONAL" }
        Write-Host "[$level] $($check.Name): not found"
        if ($check.Required) { $failed++ }
        continue
    }

    try {
        $output = & $found @($check.Args) 2>&1 | Select-Object -First 1
        Write-Host "[OK] $($check.Name): $output"
    }
    catch {
        Write-Host "[FAIL] $($check.Name): $($_.Exception.Message)"
        if ($check.Required) { $failed++ }
    }
}

Write-Host ""
Write-Host "=== Python Package Tool ==="
$pythonCmd = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } elseif (Get-Command py -ErrorAction SilentlyContinue) { "py" } else { $null }
if ($pythonCmd) {
    try {
        $pip = & $pythonCmd -m pip --version 2>&1 | Select-Object -First 1
        Write-Host "[OK] pip: $pip"
    } catch {
        Write-Host "[FAIL] pip unavailable"
        $failed++
    }
}

Write-Host ""
Write-Host "=== Git Identity ==="
try { Write-Host "user.name : $(git config --get user.name)" } catch {}
try { Write-Host "user.email: $(git config --get user.email)" } catch {}

Write-Host ""
Write-Host "=== Package Sources ==="
try { Write-Host "npm registry: $(npm config get registry)" } catch {}
if ($pythonCmd) {
    try { & $pythonCmd -m pip config list } catch {}
}

Write-Host ""
if ($failed -gt 0) {
    Write-Host "Preflight FAILED: $failed required capability/capabilities missing."
    exit 1
}

Write-Host "Preflight PASSED."
exit 0
