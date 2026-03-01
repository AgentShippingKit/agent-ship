#!/bin/bash
set -e

# Create multiple databases
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    -- Create session store database
    CREATE DATABASE agentship_session_store;
    GRANT ALL PRIVILEGES ON DATABASE agentship_session_store TO $POSTGRES_USER;

    -- Create auth database (for MCP OAuth)
    CREATE DATABASE agentship_auth;
    GRANT ALL PRIVILEGES ON DATABASE agentship_auth TO $POSTGRES_USER;

    -- Display created databases
    \l
EOSQL

echo "✅ Databases created: agentship_session_store, agentship_auth"
