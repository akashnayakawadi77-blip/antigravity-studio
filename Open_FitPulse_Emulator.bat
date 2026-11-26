@echo off
title FitPulse AI - Phone Emulator
echo ======================================================
echo    Launching Android Phone Window on Your Desktop
echo ======================================================
echo.
start "" "%LOCALAPPDATA%\Android\Sdk\emulator\emulator.exe" -avd medium_phone
echo Phone window launched!
timeout /t 5
