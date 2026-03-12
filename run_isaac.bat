@echo off
call conda activate isaac
cd /d "%~dp0_build\windows-x86_64\release"
isaac-sim.bat
