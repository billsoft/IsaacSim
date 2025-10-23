@echo off
REM Set Packman Download Retry Configuration
REM This script sets environment variables for packman download retry behavior

echo Setting Packman retry configuration...

REM Set download retry count to 1000
set PACKMAN_DOWNLOAD_RETRY_COUNT=1000
echo PACKMAN_DOWNLOAD_RETRY_COUNT=%PACKMAN_DOWNLOAD_RETRY_COUNT%

REM Set download retry delay to 600 seconds (10 minutes)
set PACKMAN_DOWNLOAD_RETRY_DELAY=600
echo PACKMAN_DOWNLOAD_RETRY_DELAY=%PACKMAN_DOWNLOAD_RETRY_DELAY%

echo.
echo Packman retry configuration has been set for this session.
echo To make these settings permanent, add them to your system environment variables.
echo.
echo Current settings:
echo - Retry count: %PACKMAN_DOWNLOAD_RETRY_COUNT% times
echo - Retry delay: %PACKMAN_DOWNLOAD_RETRY_DELAY% seconds (10 minutes)
echo.