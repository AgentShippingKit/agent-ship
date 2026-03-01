# MCP OAuth Database Migrations

This directory contains SQL migrations for MCP OAuth integration.

## Migrations

### 001_create_mcp_oauth_tables.sql
Creates the core tables for MCP OAuth:
- `mcp_user_connections` - Tracks user's connected MCP servers
- `mcp_oauth_tokens` - Stores encrypted OAuth tokens
- `mcp_auth_sessions` - Temporary sessions for CLI OAuth flow

## Running Migrations

### Manual Execution

```bash
# Using psql
psql -U your_user -d your_database -f src/agent_framework/mcp/migrations/001_create_mcp_oauth_tables.sql

# Or using docker-compose
docker-compose exec postgres psql -U agentship -d agentship_session_store -f /path/to/migration.sql
```

### From Python

```python
from src.agent_framework.mcp.migrations.migration_runner import run_migrations

run_migrations()
```

## Migration Files

Migration files are named with a numeric prefix for ordering:
- `001_*.sql` - Initial schema
- `002_*.sql` - Subsequent changes
- etc.

## Schema

### mcp_user_connections
Tracks which MCP servers each user has connected.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| user_id | VARCHAR(255) | User identifier |
| server_id | VARCHAR(100) | MCP server ID from catalog |
| status | VARCHAR(50) | Connection status (active, disconnected, expired, error) |
| config | JSONB | User-specific configuration |
| connected_at | TIMESTAMP | When user connected |
| last_used_at | TIMESTAMP | Last tool usage |
| updated_at | TIMESTAMP | Last update |

### mcp_oauth_tokens
Stores encrypted OAuth access and refresh tokens for SSE servers.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| user_id | VARCHAR(255) | User identifier |
| server_id | VARCHAR(100) | MCP server ID |
| access_token | TEXT | Encrypted access token (Fernet) |
| refresh_token | TEXT | Encrypted refresh token (Fernet) |
| token_type | VARCHAR(50) | Token type (usually "Bearer") |
| expires_at | TIMESTAMP | Token expiration |
| scope | TEXT | OAuth scopes (space-separated) |
| created_at | TIMESTAMP | Token creation time |
| updated_at | TIMESTAMP | Last token refresh |

### mcp_auth_sessions
Temporary OAuth sessions for CLI polling during the OAuth flow.

| Column | Type | Description |
|--------|------|-------------|
| session_id | VARCHAR(100) | Primary key, unique session ID |
| user_id | VARCHAR(255) | User identifier |
| server_id | VARCHAR(100) | MCP server ID |
| state_token | VARCHAR(100) | CSRF protection token |
| status | VARCHAR(50) | Session status (pending, completed, expired, error) |
| error_message | TEXT | Error details if failed |
| created_at | TIMESTAMP | Session creation |
| expires_at | TIMESTAMP | Session expiration (typically 5 minutes) |
| completed_at | TIMESTAMP | When OAuth completed |

## Maintenance

### Cleanup Expired Sessions

Run periodically (e.g., via cron or scheduled task):

```sql
SELECT cleanup_expired_mcp_auth_sessions();
```

This removes expired OAuth sessions to prevent table bloat.

## Security Notes

- **Token Encryption**: All OAuth tokens are encrypted using Fernet symmetric encryption
- **Encryption Key**: Store `MCP_TOKEN_ENCRYPTION_KEY` environment variable securely
- **CSRF Protection**: OAuth flows use state tokens to prevent CSRF attacks
- **Expiration**: Auth sessions expire after 5 minutes, tokens tracked with expires_at
