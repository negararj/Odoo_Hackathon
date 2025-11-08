@echo off
REM ========================================
REM Manual Docker Commands for CSR and Sustainability
REM ========================================
REM
REM 1. Start PostgreSQL Database:
REM    docker run -d --name db -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=12345 -e POSTGRES_DB=postgres -p 5432:5432 postgres:15
REM
REM 2. Create and start Odoo container:
REM    docker run -v "%CD%\custom_devs:/mnt/extra-addons" -p 8069:8069 --name odoo_hackathon --link db:db -t odoo:19 -- -d odoo_hackathon -i base
REM
REM 3. Stop the server:
REM    docker stop odoo_hackathon
REM
REM 4. Start the server:
REM    docker start odoo_hackathon
REM
REM 5. List all running containers:
REM    docker ps
REM
REM 6. View logs:
REM    docker logs -f odoo_hackathon
REM
REM 7. Remove containers (cleanup):
REM    docker stop odoo_hackathon db
REM    docker rm odoo_hackathon db
REM
REM ========================================
echo.
echo Manual Docker Commands Reference
echo ========================================
echo.
echo For easier management, use docker-compose:
echo   - docker-start.bat (recommended)
echo   - docker-stop.bat
echo   - docker-status.bat
echo.
pause

