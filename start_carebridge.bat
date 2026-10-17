@echo off
title CareBridge AI
echo ==========================================================
echo    Starting CareBridge AI (Your Medicine, Your Language)
echo ==========================================================
start http://127.0.0.1:5000
python -m backend.app
pause
