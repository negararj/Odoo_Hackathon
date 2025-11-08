@echo off
echo Restarting Odoo container...
docker-compose restart odoo
echo.
echo Odoo container restarted!
echo Access at: http://localhost:8069
pause

