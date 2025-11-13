# Neon Database Setup Guide

## Environment Variables

In your Netlify Dashboard, go to **Site settings → Environment variables** and add:

- **Variable name:** `NETLIFY_DATABASE_URL`
- **Value:** Your Neon database connection string (from Netlify Dashboard → Database)

The database URL should look like:
```
postgresql://username:password@hostname/database?sslmode=require
```

## Automatic Setup

The database tables will be automatically created on first deployment. The system will:

1. Create `config` table for configuration settings
2. Create `banned_accounts` table for banned player records
3. Create `allowed_accounts` table for whitelisted players

## Fallback Behavior

If the database is not available or not configured, the system will automatically fall back to JSON file storage (temporary on Netlify).

## Database Schema

### config
- `id` (SERIAL PRIMARY KEY)
- `key` (VARCHAR(255) UNIQUE)
- `value` (TEXT)
- `updated_at` (TIMESTAMP)

### banned_accounts
- `id` (SERIAL PRIMARY KEY)
- `player_id` (VARCHAR(255) UNIQUE)
- `player_name` (VARCHAR(255))
- `hwid` (TEXT)
- `ip_address` (VARCHAR(45))
- `reason` (TEXT)
- `ban_duration_hours` (INTEGER)
- `banned_at` (TIMESTAMP)
- `expires_at` (TIMESTAMP)
- `account_data` (JSONB)

### allowed_accounts
- `id` (SERIAL PRIMARY KEY)
- `player_id` (VARCHAR(255) UNIQUE)
- `player_name` (VARCHAR(255))
- `added_at` (TIMESTAMP)
- `added_by` (VARCHAR(255))
- `account_data` (JSONB)

