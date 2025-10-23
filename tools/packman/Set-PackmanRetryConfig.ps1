# Set Packman Download Retry Configuration
# This script sets environment variables for packman download retry behavior

param(
    [int]$RetryCount = 1000,
    [int]$RetryDelayMinutes = 10,
    [switch]$Permanent
)

$RetryDelaySeconds = $RetryDelayMinutes * 60

Write-Host "Setting Packman retry configuration..." -ForegroundColor Green

if ($Permanent) {
    # Set permanent environment variables (requires admin rights)
    try {
        [Environment]::SetEnvironmentVariable("PACKMAN_DOWNLOAD_RETRY_COUNT", $RetryCount, "User")
        [Environment]::SetEnvironmentVariable("PACKMAN_DOWNLOAD_RETRY_DELAY", $RetryDelaySeconds, "User")
        Write-Host "Environment variables set permanently for current user." -ForegroundColor Green
    }
    catch {
        Write-Warning "Failed to set permanent environment variables: $($_.Exception.Message)"
        Write-Host "Setting for current session only..." -ForegroundColor Yellow
        $env:PACKMAN_DOWNLOAD_RETRY_COUNT = $RetryCount
        $env:PACKMAN_DOWNLOAD_RETRY_DELAY = $RetryDelaySeconds
    }
}
else {
    # Set for current session only
    $env:PACKMAN_DOWNLOAD_RETRY_COUNT = $RetryCount
    $env:PACKMAN_DOWNLOAD_RETRY_DELAY = $RetryDelaySeconds
    Write-Host "Environment variables set for current session only." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Current Packman retry configuration:" -ForegroundColor Cyan
Write-Host "- Retry count: $RetryCount times" -ForegroundColor White
Write-Host "- Retry delay: $RetryDelayMinutes minutes ($RetryDelaySeconds seconds)" -ForegroundColor White
Write-Host ""

if (-not $Permanent) {
    Write-Host "To make these settings permanent, run:" -ForegroundColor Yellow
    Write-Host "  .\Set-PackmanRetryConfig.ps1 -Permanent" -ForegroundColor White
}