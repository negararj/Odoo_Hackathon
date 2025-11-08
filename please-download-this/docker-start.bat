@echo off
echo Starting Docker containers for CSR and Sustainability...
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo Starting PostgreSQL database...
docker-compose up -d db

echo Waiting for database to be ready...
timeout /t 5 /nobreak >nul

echo Starting Odoo with CSR and Sustainability module...
docker-compose up -d odoo

echo.
echo ========================================
echo Docker containers started!
echo ========================================
echo.
echo Database: Running on port 5432
echo Odoo: Running on http://localhost:8069
echo.
echo To view logs: docker-compose logs -f odoo
echo To stop: docker-compose down
echo.
timeout /t 3 /nobreak >nul
start http://localhost:8069
pause

