@echo off
echo === EventRent: khoi dong 2 server ===
echo.
start "Python Backend" cmd /k "cd /d %~dp0LoginandRegister\myapp && pip install -r ..\requirements.txt -q && python app.py"
timeout /t 3 /nobreak >nul
start "React Frontend" cmd /k "cd /d %~dp0 && npm start"
echo.
echo Backend:  http://localhost:5000  (dang nhap)
echo Frontend: http://localhost:3000  (mua sam)
echo.
pause
