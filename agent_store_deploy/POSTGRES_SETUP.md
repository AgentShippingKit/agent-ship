# PostgreSQL Session Store Setup

This document explains how to set up PostgreSQL for the AI Agents session store, replacing the default InMemorySessionService with DatabaseSessionService.

## Overview

The AI Agents platform now supports PostgreSQL for persistent session storage. This provides better scalability and persistence compared to the in-memory session service.

## Files Created/Modified

- `setup_local_postgres.sh` - Local PostgreSQL setup script
- `verify_db_setup.py` - Database verification script
- `env.example` - Updated with SESSION_STORE_URI
- `requirements.txt` - Added psycopg2-binary dependency
- `pyproject.toml` - Added psycopg2-binary dependency
- `service_cloud_deploy/heroku/deploy_heroku.sh` - Updated to include PostgreSQL addon

## Local Setup

### 1. Install PostgreSQL

**macOS (using Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**CentOS/RHEL:**
```bash
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Run the Setup Script

```bash
# Basic setup with default configuration
./setup_local_postgres.sh

# Or with custom configuration
DB_NAME=my_custom_db DB_USER=my_user DB_PASSWORD=my_password ./setup_local_postgres.sh
```

The script will:
- Check if PostgreSQL is installed and running
- Create the database and user (if they don't exist)
- Set up proper permissions
- Update your `.env` file with the SESSION_STORE_URI

### 3. Verify the Setup

```bash
python verify_db_setup.py
```

This script will:
- Test database connectivity
- Verify user permissions
- Test table creation capabilities
- Ensure the database is ready for Google ADK

## Heroku Setup

### 1. Deploy with PostgreSQL

The Heroku deployment script has been updated to automatically:
- Add a PostgreSQL addon (hobby-dev tier)
- Set the SESSION_STORE_URI environment variable
- Configure the database connection

```bash
./service_cloud_deploy/heroku/deploy_heroku.sh
```

### 2. Manual Heroku Setup (if needed)

If you need to set up PostgreSQL manually on Heroku:

```bash
# Add PostgreSQL addon
heroku addons:create postgresql:hobby-dev --app your-app-name

# Add on info
$ sleep 20 && heroku addons:info ai-agents-session-store --app ai-agents-alpha

# Get the database URL
heroku config:get DATABASE_URL --app your-app-name

# Set SESSION_STORE_URI (same as DATABASE_URL)
heroku config:set SESSION_STORE_URI="your-database-url" --app your-app-name
```

## Configuration

### Environment Variables

The following environment variables control the database configuration:

- `SESSION_STORE_URI` - PostgreSQL connection URI (required)
- `DB_NAME` - Database name (default: ai_agents_session_store)
- `DB_USER` - Database username (default: ai_agents_user)
- `DB_PASSWORD` - Database password (default: ai_agents_password)
- `DB_HOST` - Database host (default: localhost)
- `DB_PORT` - Database port (default: 5432)

### Connection URI Format

```
postgresql://username:password@host:port/database_name
```

Example:
```
postgresql://ai_agents_user:ai_agents_password@localhost:5432/ai_agents_session_store
```

## Usage in Code

Once the database is set up, you can use it with Google ADK:

```python
from google.adk.sessions import DatabaseSessionService
import os

# Get the session store URI from environment
session_store_uri = os.getenv('SESSION_STORE_URI')

# Create the database session service
session_service = DatabaseSessionService(session_store_uri)

# Use it in your runner
runner = Runner(
    agent=agent,
    app_name=agent_name,
    session_service=session_service,
)
```

## Troubleshooting

### Common Issues

1. **PostgreSQL not running**
   - Start the PostgreSQL service
   - Check if the port is available

2. **Permission denied**
   - Ensure the database user has CREATE privileges
   - Check if the database exists

3. **Connection refused**
   - Verify the host and port
   - Check firewall settings
   - Ensure PostgreSQL is accepting connections

4. **Database not found**
   - Run the setup script again
   - Check if the database name is correct

### Verification Steps

1. Run `python verify_db_setup.py` to check connectivity
2. Check the `.env` file for SESSION_STORE_URI
3. Test the connection manually:
   ```bash
   psql "postgresql://ai_agents_user:ai_agents_password@localhost:5432/ai_agents_session_store"
   ```

## Security Notes

- Change default passwords in production
- Use environment variables for sensitive data
- Consider using SSL connections for production
- Regularly backup your database

## Next Steps

After setting up the database:

1. Update your agent configuration to use DatabaseSessionService
2. Test the session persistence
3. Monitor database performance
4. Set up regular backups

## Support

If you encounter issues:

1. Check the logs: `heroku logs --tail --app your-app-name`
2. Verify the database setup: `python verify_db_setup.py`
3. Check the environment variables: `heroku config --app your-app-name`
