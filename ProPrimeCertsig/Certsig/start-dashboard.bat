@echo off
REM Start the Certsig dashboard server and open it in the default browser
cd /d "%~dp0"
start "Certsig Dashboard" http://localhost:3000
start "Node Server" cmd /c "node server.js"
