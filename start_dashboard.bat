@echo off
echo Starting Prometheus Prime Dashboard Server...
echo.
echo Backend Server (Flask) starting on port 5000...
start /B venv311\Scripts\python.exe core\app.py

echo.
echo Frontend Server starting on port 8080...
cd ui
start /B ..\venv311\Scripts\python.exe -m http.server 8080

echo.
echo Dashboard will be available at:
echo http://localhost:8080/dashboard.html
echo.
echo Backend API available at:
echo http://localhost:5000/api/health
echo.
echo Press any key to open dashboard...
pause
start http://localhost:8080/dashboard.html
