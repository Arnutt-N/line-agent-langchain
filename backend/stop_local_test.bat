@echo off
taskkill /F /IM ngrok.exe 2>nul
taskkill /F /IM python.exe 2>nul
echo All processes stopped.
pause
