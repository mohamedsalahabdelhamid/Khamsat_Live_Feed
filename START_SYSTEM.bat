@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo    KHAMSAT DEEP SCANNER PRO - DOCKER
echo ==========================================
echo.

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Desktop is not running.
    echo Please open Docker Desktop first.
    pause
    exit /b
)

echo [1/2] Starting the system (updating code)...
docker-compose up --build -d

echo [2/2] Opening Dashboard...
start http://localhost:8080/frontend/index.html

echo.
echo SUCCESS: System is running.
echo.
timeout /t 5
exit
