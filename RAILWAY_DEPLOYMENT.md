# Railway Deployment Guide for Odoo 16

## The Problem
Odoo 17+ has a security restriction that prevents using 'postgres' as the database user. Since Railway's PostgreSQL service uses 'postgres' as the default user, this causes deployment failures.

## The Solution
We use **Odoo 16** which doesn't have this restriction.

## Deployment Steps

### 1. Ensure you're using the correct Dockerfile

Railway should use either:
- `Dockerfile` (already updated to use Odoo 16)
- `Dockerfile.railway` (Railway-specific version)

### 2. Set Railway Build Configuration

In your Railway project settings, set:
```json
{
  "build": {
    "dockerfilePath": "./Dockerfile.railway"
  }
}
```

Or rename `Dockerfile.railway` to `Dockerfile` if you want to use the default.

### 3. Add PostgreSQL to Railway

1. In Railway dashboard, click "+ New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically set these environment variables:
   - `PGHOST`
   - `PGPORT`
   - `PGUSER`
   - `PGPASSWORD`
   - `PGDATABASE`

### 4. Deploy the Application

1. Push your changes to GitHub
2. Railway will automatically deploy
3. The application will be available on port 8080

### 5. First Time Setup

When you first access Odoo:
1. It will create the database automatically
2. Set your admin email and password
3. Install the construction modules from `/mnt/extra-addons/`

## Environment Variables

Railway automatically provides:
- `PORT` - The port your app should listen on (usually 8080)
- `PGHOST` - PostgreSQL host
- `PGPORT` - PostgreSQL port (5432)
- `PGUSER` - PostgreSQL user (postgres)
- `PGPASSWORD` - PostgreSQL password
- `PGDATABASE` - PostgreSQL database name (railway)

## Testing Locally

Use docker-compose for local testing:
```bash
docker-compose up
```

Access at: http://localhost:8069

## Troubleshooting

### "Using the database user 'postgres' is a security risk"
- **Solution**: Make sure you're using Odoo 16, not Odoo 17+
- Check your Dockerfile starts with `FROM odoo:16`

### Container keeps restarting
- Check Railway logs for the specific error
- Ensure PostgreSQL service is added and running
- Verify environment variables are set

### Can't connect to database
- Ensure PostgreSQL service is in the same Railway project
- Check that the service is named correctly
- Verify network connectivity between services

## Files Structure

```
/
├── Dockerfile.railway     # Railway-specific Dockerfile (Odoo 16)
├── railway-entrypoint.sh  # Railway startup script
├── docker-compose.yml     # Local testing
├── addons/               # Your custom Odoo modules
│   ├── construction_project/
│   ├── construction_materials/
│   └── construction_smeta_task_integration/
└── railway.json          # Railway configuration
```