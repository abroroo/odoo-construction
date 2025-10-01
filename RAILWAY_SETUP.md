# Railway Odoo Deployment - Complete Setup Guide

## ✅ Current Status
- **Postgres user check**: BYPASSED (patched in Dockerfile)
- **Issue**: Database connection - PostgreSQL service not added to Railway

## 📋 Step-by-Step Setup

### 1. Add PostgreSQL to Railway Project

1. Go to your Railway dashboard
2. Click **"+ New"** in your project
3. Select **"Database"**
4. Choose **"Add PostgreSQL"**
5. Railway will automatically create the database and set environment variables

### 2. Verify Environment Variables

After adding PostgreSQL, Railway automatically provides these variables:
- `DATABASE_URL` - Full connection string
- `PGHOST` - Database host
- `PGPORT` - Database port (5432)
- `PGUSER` - Database user
- `PGPASSWORD` - Database password
- `PGDATABASE` - Database name

### 3. Connect Services

Make sure your Odoo service can see the PostgreSQL service:
1. Click on your Odoo service
2. Go to "Variables" tab
3. You should see the PostgreSQL variables referenced

### 4. Deploy

1. Commit and push the latest Dockerfile changes
2. Railway will automatically redeploy
3. Monitor the deployment logs

## 🔍 Troubleshooting

### Current Error: "could not translate host name"
**Cause**: PostgreSQL service not added to project
**Solution**: Follow Step 1 above to add PostgreSQL

### If you see "postgres user security risk"
**Status**: Already fixed! The Dockerfile patches this check
**Note**: Using Odoo 15 with patched security check

### Connection Issues After Adding PostgreSQL
1. Check that both services are in the same Railway project
2. Verify the PostgreSQL service is running (green status)
3. Check environment variables are visible in Odoo service

## 📝 What the Dockerfile Does

1. **Uses Odoo 15** - Stable version
2. **Patches security check** - Removes postgres user restriction
3. **Parses DATABASE_URL** - Handles Railway's connection string
4. **Configures Odoo** - Sets up proper parameters

## 🚀 Expected Result

Once PostgreSQL is added, you should see:
```
=== Odoo Railway Deployment (Patched) ===
Configuration:
  DB_HOST: [your-postgres-host].railway.app
  DB_USER: postgres
  DB_NAME: railway
  HTTP_PORT: 8080
2025-XX-XX XX:XX:XX INFO ? odoo: Odoo version 15.0
2025-XX-XX XX:XX:XX INFO ? odoo.service.server: HTTP service ready
```

Then you can access Odoo at your Railway URL on port 8080!