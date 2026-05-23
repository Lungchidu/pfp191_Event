@echo off
cd /d "%~dp0"
echo ========================================
echo   EventRent - Build for publish
echo ========================================
echo.

call "%ProgramFiles%\nodejs\npm.cmd" run build
if errorlevel 1 (
  echo BUILD FAILED.
  pause
  exit /b 1
)

copy /Y build\index.html build\404.html >nul

echo.
echo BUILD OK - folder: %cd%\build
echo.
echo --- Cach publish nhanh nhat (Netlify Drop) ---
echo 1. Mo: https://app.netlify.com/drop
echo 2. Keo tha folder "build" vao trang web
echo 3. Nhan link *.netlify.app (xong trong 1 phut)
echo.
echo --- Hoac GitHub Pages ---
echo 1. Push code len GitHub
echo 2. Settings ^> Pages ^> Source: GitHub Actions
echo 3. Doi workflow "Publish to GitHub Pages" chay xong
echo.
pause
