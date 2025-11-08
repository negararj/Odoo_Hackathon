# Docker Setup for CSR and Sustainability

## Quick Start (Recommended)

1. **Start Docker Desktop** (make sure it's running)

2. **Start the application:**
   ```bash
   docker-start.bat
   ```
   This will:
   - Start PostgreSQL database
   - Start Odoo with your custom module
   - Open browser to http://localhost:8069

3. **Access the application:**
   - Open http://localhost:8069 in your browser
   - Create database: `odoo_hackathon`
   - Install "CSR and Sustainability" module from Apps menu

## Available Commands

### Using Docker Compose (Recommended)
- `docker-start.bat` - Start all containers
- `docker-stop.bat` - Stop all containers
- `docker-restart.bat` - Restart Odoo container
- `docker-status.bat` - Check container status
- `docker-logs.bat` - View Odoo logs
- `docker-install-module.bat` - Install/update module

### Manual Docker Commands

**1. Start PostgreSQL Database:**
```bash
docker run -d --name db -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=12345 -e POSTGRES_DB=postgres -p 5432:5432 postgres:15
```

**2. Start Odoo Container:**
```bash
docker run -v "%CD%\custom_devs:/mnt/extra-addons" -p 8069:8069 --name odoo_hackathon --link db:db -t odoo:19 -- -d odoo_hackathon -i base
```

**3. Stop the server:**
```bash
docker stop odoo_hackathon
```

**4. Start the server:**
```bash
docker start odoo_hackathon
```

**5. List all running containers:**
```bash
docker ps
```
Should show:
- `db` (PostgreSQL)
- `odoo_hackathon` (Odoo)

## Database Configuration

- **Host:** localhost (or `db` from within Docker network)
- **Port:** 5432
- **User:** odoo
- **Password:** 12345
- **Database:** odoo_hackathon

## Troubleshooting

**Check if containers are running:**
```bash
docker ps
```

**View logs:**
```bash
docker logs odoo_hackathon
docker logs db
```

**Restart containers:**
```bash
docker restart odoo_hackathon
docker restart db
```

**Clean up (remove all containers):**
```bash
docker-compose down -v
```

## Module Installation

After starting Odoo:
1. Go to http://localhost:8069
2. Create database: `odoo_hackathon`
3. Login with admin credentials
4. Go to **Apps** menu
5. Remove "Apps" filter
6. Search for "CSR and Sustainability"
7. Click **Install**

## Access Your Application

After installation, you'll see:
- **CSR & Sustainability** menu in the main menu
  - **Projects** - Manage sustainability projects
  - **Tasks** - Manage sustainability tasks  
  - **Employees** - View employee sustainability metrics

