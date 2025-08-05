@echo off
echo Installing dependencies...
pip install -r requirements_api_server.txt

echo.
echo Starting API Relay Server...
python api_server_advanced.py