@echo off
echo Prometheus Prime v2.2 Setup
echo ===========================

echo Setting up Python backend...
cd core
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
cd ..

echo Setting up React frontend...
cd ui
npm install
cd ..

echo Setup complete!
echo.
echo To start:
echo 1. Backend: cd core && venv\Scripts\activate && python app.py
echo 2. Frontend: cd ui && npm start
echo 3. Visit: http://localhost:3000
pause
