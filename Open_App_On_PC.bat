@echo off
title FitPulse AI - Desktop Controller
echo ======================================================
echo    FITPULSE AI - Personal Gym Trainer & AI Coach
echo ======================================================
echo.
echo Launching live interactive Android screen mirroring...
start "" "C:\Users\Admin\AppData\AndroidCLI\android.exe" device hub --device=emulator-5554
echo.
echo The mobile screen is now active on your desktop!
echo You can use your mouse to tap, scroll, and log workouts.
echo.
pause
