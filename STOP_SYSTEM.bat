@echo off
echo ==========================================
echo    STOPPING KHAMSAT SYSTEM...
echo ==========================================
echo.

docker-compose down

echo.
echo SUCCESS: System stopped.
echo.
timeout /t 3
exit
