@echo off
echo Testing LINE Agent System...
echo ============================

echo.
echo [1] Testing Backend Health...
curl -s http://localhost:8000/health
echo.

echo.
echo [2] Testing API Endpoints...
echo - Root: 
curl -s http://localhost:8000/
echo.
echo.
echo - Users API:
curl -s http://localhost:8000/api/users
echo.
echo.
echo - Dashboard API:
curl -s http://localhost:8000/api/dashboard
echo.
echo.
echo ============================
echo If you see JSON responses above, the backend is working!
pause