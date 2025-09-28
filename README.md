# Odoo Construction System

A Docker-based Odoo 17 development environment for construction management system.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git

## Quick Start

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd odoo-construction-system
   ```

2. Start the services:
   ```bash
   docker-compose up -d
   ```

3. Wait for services to be ready (this may take a few minutes on first run)

4. Access Odoo:
   - URL: http://localhost:8069
   - Admin login: admin
   - Master password: admin123

## Project Structure

```
odoo-construction-system/
├── docker-compose.yml      # Docker services configuration
├── config/
│   └── odoo.conf          # Odoo server configuration
├── addons/                # Custom Odoo modules directory
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Configuration

### Odoo Configuration
The main Odoo configuration is in `config/odoo.conf`:
- Admin password: `admin123`
- Demo data: Disabled
- Custom addons path: `/mnt/extra-addons`
- Database connection configured for PostgreSQL

### Database Configuration
- Host: `db` (internal Docker network)
- Port: `5432`
- Database: `postgres`
- User: `odoo`
- Password: `odoo_password`

## Development

### Adding Custom Modules
1. Place your custom modules in the `addons/` directory
2. Restart the Odoo container:
   ```bash
   docker-compose restart odoo
   ```
3. Update the app list in Odoo interface or use:
   ```bash
   docker-compose exec odoo odoo -u all -d <database_name>
   ```

### Accessing Containers
- Odoo container: `docker-compose exec odoo bash`
- PostgreSQL container: `docker-compose exec db psql -U odoo -d postgres`

### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f odoo
docker-compose logs -f db
```

## Common Commands

### Start services
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### Update Odoo modules
```bash
docker-compose exec odoo odoo -u module_name -d database_name
```

### Install new modules
```bash
docker-compose exec odoo odoo -i module_name -d database_name
```

### Backup database
```bash
docker-compose exec db pg_dump -U odoo postgres > backup.sql
```

### Restore database
```bash
docker-compose exec -T db psql -U odoo postgres < backup.sql
```

## Data Persistence

The following Docker volumes are used for data persistence:
- `postgres_data`: PostgreSQL database files
- `odoo_data`: Odoo filestore and sessions
- `odoo_logs`: Odoo log files

## Ports

- **8069**: Odoo web interface
- **5432**: PostgreSQL database (exposed for external tools)

## Environment Variables

Key environment variables in `docker-compose.yml`:
- `POSTGRES_DB`: Database name
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `HOST`: Database host for Odoo
- `USER`: Database user for Odoo
- `PASSWORD`: Database password for Odoo

## Security Notes

⚠️ **Important**: This configuration is intended for development use only.

For production deployment:
1. Change all default passwords
2. Remove database port exposure
3. Configure SSL/TLS
4. Set up proper backup procedures
5. Review security settings in `odoo.conf`

## Troubleshooting

### Services won't start
Check if ports are already in use:
```bash
lsof -i :8069
lsof -i :5432
```

### Database connection issues
1. Ensure PostgreSQL container is healthy:
   ```bash
   docker-compose ps
   ```
2. Check database logs:
   ```bash
   docker-compose logs db
   ```

### Odoo won't start
1. Check Odoo logs:
   ```bash
   docker-compose logs odoo
   ```
2. Verify configuration file:
   ```bash
   cat config/odoo.conf
   ```

### Permission issues with custom addons
```bash
sudo chown -R $(id -u):$(id -g) addons/
```

## Support

For issues related to:
- Odoo: https://www.odoo.com/documentation/17.0/
- Docker: https://docs.docker.com/
- PostgreSQL: https://www.postgresql.org/docs/

## License

This project is licensed under the MIT License.# odoo-construction
