@echo off
echo ========================================
echo Starting Isaac Sim UI Interface...
echo ========================================

:: Activate conda environment
echo Activating conda environment: isaac
call conda activate isaac

:: Set environment variables
set "ISAACSIM_PATH=%~dp0_build\windows-x86_64\release"
set "ISAACSIM_PYTHON_EXE=%ISAACSIM_PATH%\python.bat"

:: Check if Isaac Sim exists
if not exist "%ISAACSIM_PATH%\isaac-sim.bat" (
    echo ERROR: Isaac Sim not found at %ISAACSIM_PATH%
    echo Please make sure Isaac Sim is built first.
    pause
    exit /b 1
)

:: Start Isaac Sim UI
echo Starting Isaac Sim UI...
echo.
echo Note: If you see red error messages during startup, they are mostly
echo non-critical warnings and can be ignored for basic functionality.
echo.
"%ISAACSIM_PATH%\isaac-sim.bat"

echo.
echo Isaac Sim has been closed.
pause
