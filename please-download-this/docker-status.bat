@echo off
echo ========================================
echo Docker Container Status
echo ========================================
echo.
docker ps
echo.
echo ========================================
echo Expected:
echo - db (PostgreSQL) container running
echo - odoo container running
echo ========================================
pause

