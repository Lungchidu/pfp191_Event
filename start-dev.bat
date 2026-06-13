@echo off
echo === EventRent: khoi dong 2 server ===
echo.

start "Python Backend" cmd /k "cd /d %~dp0LoginandRegister\myapp && pip install -r %~dp0requirements.txt -q && python app.py"
timeout /t 3 /nobreak >nul
start "React Frontend" cmd /k "cd /d %~dp0 && npm start"

echo.
echo Backend Python:  http://localhost:5000
echo Frontend React:  http://localhost:3000  (hoac 3001, 3002 neu port bi chiem)
echo.
echo Luu y: Can chay CA HAI server thi dang nhap/dang ky moi hoat dong.
echo.
pause
