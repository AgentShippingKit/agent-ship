-- Migration: 001_create_mcp_oauth_tables
-- Description: Create tables for MCP OAuth integration
-- Created: 2026-02-24

-- ============================================
-- User MCP Connections
-- ============================================
CREATE TABLE IF NOT EXISTS mcp_user_connections (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    server_id VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',  -- active | disconnected | expired | error
    config JSONB,  -- Server-specific configuration (e.g., connection strings)
    connected_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_user_server UNIQUE(user_id, server_id)
);

CREATE INDEX idx_mcp_user_connections_user ON mcp_user_connections(user_id, status);
CREATE INDEX idx_mcp_user_connections_server ON mcp_user_connections(server_id);
CREATE INDEX idx_mcp_user_connections_status ON mcp_user_connections(status);

COMMENT ON TABLE mcp_user_connections IS 'Tracks which MCP servers each user has connected';
COMMENT ON COLUMN mcp_user_connections.user_id IS 'User identifier';
COMMENT ON COLUMN mcp_user_connections.server_id IS 'MCP server ID from catalog';
COMMENT ON COLUMN mcp_user_connections.status IS 'Connection status';
COMMENT ON COLUMN mcp_user_connections.config IS 'User-specific configuration (STDIO args, etc.)';


-- ============================================
-- OAuth Tokens (Encrypted)
-- ============================================
CREATE TABLE IF NOT EXISTS mcp_oauth_tokens (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    server_id VARCHAR(100) NOT NULL,
    access_token TEXT NOT NULL,  -- Encrypted with Fernet
    refresh_token TEXT,           -- Encrypted with Fernet
    token_type VARCHAR(50) DEFAULT 'Bearer',
    expires_at TIMESTAMP,
    scope TEXT,  -- Space-separated OAuth scopes
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_user_server_token UNIQUE(user_id, server_id)
);

CREATE INDEX idx_mcp_oauth_tokens_user ON mcp_oauth_tokens(user_id, server_id);
CREATE INDEX idx_mcp_oauth_tokens_expires ON mcp_oauth_tokens(expires_at);

COMMENT ON TABLE mcp_oauth_tokens IS 'Stores encrypted OAuth tokens for SSE MCP servers';
COMMENT ON COLUMN mcp_oauth_tokens.access_token IS 'Encrypted access token (Fernet)';
COMMENT ON COLUMN mcp_oauth_tokens.refresh_token IS 'Encrypted refresh token (Fernet)';
COMMENT ON COLUMN mcp_oauth_tokens.expires_at IS 'Token expiration timestamp';


-- ============================================
-- OAuth Sessions (Temporary for CLI polling)
-- ============================================
CREATE TABLE IF NOT EXISTS mcp_auth_sessions (
    session_id VARCHAR(100) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    server_id VARCHAR(100) NOT NULL,
    state_token VARCHAR(100) NOT NULL,  -- CSRF protection token
    status VARCHAR(50) DEFAULT 'pending',  -- pending | completed | expired | error
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP
);

CREATE INDEX idx_mcp_auth_sessions_user ON mcp_auth_sessions(user_id);
CREATE INDEX idx_mcp_auth_sessions_status ON mcp_auth_sessions(status);
CREATE INDEX idx_mcp_auth_sessions_expires ON mcp_auth_sessions(expires_at);

COMMENT ON TABLE mcp_auth_sessions IS 'Temporary OAuth sessions for CLI polling during OAuth flow';
COMMENT ON COLUMN mcp_auth_sessions.state_token IS 'CSRF protection token for OAuth callback';
COMMENT ON COLUMN mcp_auth_sessions.status IS 'OAuth session status';


-- ============================================
-- Cleanup Function for Expired Sessions
-- ============================================
CREATE OR REPLACE FUNCTION cleanup_expired_mcp_auth_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM mcp_auth_sessions
    WHERE expires_at < NOW()
    AND status IN ('pending', 'expired');

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_expired_mcp_auth_sessions IS 'Delete expired OAuth sessions (run periodically)';


-- ============================================
-- Trigger to Update updated_at
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_mcp_user_connections_updated_at
    BEFORE UPDATE ON mcp_user_connections
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mcp_oauth_tokens_updated_at
    BEFORE UPDATE ON mcp_oauth_tokens
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Initial Data / Validation
-- ============================================
-- Verify tables were created successfully
DO $$
BEGIN
    ASSERT (SELECT COUNT(*) FROM information_schema.tables
            WHERE table_name IN ('mcp_user_connections', 'mcp_oauth_tokens', 'mcp_auth_sessions')) = 3,
           'MCP OAuth tables not created successfully';

    RAISE NOTICE 'MCP OAuth migration completed successfully';
    RAISE NOTICE 'Created tables: mcp_user_connections, mcp_oauth_tokens, mcp_auth_sessions';
END $$;
