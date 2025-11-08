@echo off
echo Installing CSR and Sustainability module...
echo.
docker-compose exec odoo odoo -d odoo_hackathon -u csr_sustainability --stop-after-init
echo.
echo Module installation complete!
pause

