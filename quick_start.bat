@echo off
title Isaac Sim Quick Start

:: Activate conda and start Isaac Sim
call conda activate isaac
"%~dp0_build\windows-x86_64\release\isaac-sim.bat"
