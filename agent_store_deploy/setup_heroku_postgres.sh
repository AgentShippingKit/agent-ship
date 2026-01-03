#!/bin/bash

# AgentShip - Heroku PostgreSQL Storage Setup Script
# This script sets up PostgreSQL storage for AI Agents on Heroku

set -e  # Exit on any error

echo "🐘 Setting up PostgreSQL Storage for AI Agents on Heroku..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Default app name - can be overridden
APP_NAME="${APP_NAME:-ai-agents-alpha}"
POSTGRES_PLAN="${POSTGRES_PLAN:-essential-0}"
SESSION_STORE_NAME="${SESSION_STORE_NAME:-}"

# Display configuration being used
echo ""
print_info "Using the following Heroku configuration:"
echo "  App Name: $APP_NAME"
echo "  PostgreSQL Plan: $POSTGRES_PLAN"
if [ -n "$SESSION_STORE_NAME" ]; then
    echo "  Session Store Name: $SESSION_STORE_NAME"
else
    echo "  Session Store Name: (auto-generated)"
fi
echo ""
print_info "To override these values, set the environment variables before running this script."
echo "  Example: APP_NAME=my-app POSTGRES_PLAN=standard-0 ./setup_heroku_postgres.sh"
echo ""

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    print_error "Heroku CLI is not installed. Please install it first:"
    echo "   https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

print_status "Heroku CLI is installed"

# Check if we're logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
    print_error "Not logged in to Heroku. Please log in first:"
    echo "   heroku login"
    exit 1
fi

print_status "Logged in to Heroku as: $(heroku auth:whoami)"

# Check if the app exists and we have access to it
if heroku apps:info --app "$APP_NAME" &> /dev/null; then
    print_status "App $APP_NAME exists and is accessible"
else
    print_warning "App $APP_NAME does not exist. Creating it..."
    if heroku apps:create "$APP_NAME" --region us; then
        print_status "Successfully created app $APP_NAME"
    else
        print_error "Failed to create app $APP_NAME"
        print_info "Available apps:"
        heroku apps
        exit 1
    fi
fi

# Add PostgreSQL addon with specific database name
print_status "Setting up PostgreSQL addon..."
if heroku addons:info heroku-postgresql --app "$APP_NAME" &> /dev/null; then
    print_status "PostgreSQL addon already exists"
    
    # Get current plan
    CURRENT_PLAN=$(heroku addons:info heroku-postgresql --app "$APP_NAME" | grep "Plan:" | awk '{print $2}')
    print_info "Current PostgreSQL plan: $CURRENT_PLAN"
    
    if [ "$CURRENT_PLAN" != "$POSTGRES_PLAN" ]; then
        print_warning "Current plan ($CURRENT_PLAN) differs from requested plan ($POSTGRES_PLAN)"
        print_info "To upgrade/downgrade, you may need to do it manually:"
        echo "   heroku addons:upgrade heroku-postgresql:$POSTGRES_PLAN --app $APP_NAME"
    fi
else
    print_info "Adding PostgreSQL addon ($POSTGRES_PLAN tier)..."
    if [ -n "$SESSION_STORE_NAME" ]; then
        # Use custom session store name if provided
        if heroku addons:create heroku-postgresql:$POSTGRES_PLAN --app "$APP_NAME" --name "$SESSION_STORE_NAME"; then
            print_status "PostgreSQL addon added successfully with name: $SESSION_STORE_NAME"
        else
            print_error "Failed to add PostgreSQL addon with name '$SESSION_STORE_NAME'. The name might already be taken."
            print_info "Try leaving SESSION_STORE_NAME empty for auto-generated name, or choose a unique name."
            exit 1
        fi
    else
        # Let Heroku auto-generate the name
        if heroku addons:create heroku-postgresql:$POSTGRES_PLAN --app "$APP_NAME"; then
            print_status "PostgreSQL addon added successfully"
        else
            print_error "Failed to add PostgreSQL addon. You may need to add it manually:"
            echo "   heroku addons:create heroku-postgresql:$POSTGRES_PLAN --app $APP_NAME"
            exit 1
        fi
    fi
    
    # Wait for the addon to be ready
    print_info "Waiting for PostgreSQL addon to be ready..."
    heroku pg:wait --app "$APP_NAME" || sleep 30
fi

# Get the DATABASE_URL from the PostgreSQL addon
print_status "Getting DATABASE_URL from PostgreSQL addon..."
DATABASE_URL=$(heroku config:get DATABASE_URL --app "$APP_NAME")

if [ -n "$DATABASE_URL" ]; then
    print_status "DATABASE_URL retrieved successfully"
    print_info "Database URL: ${DATABASE_URL:0:50}..."
    
    # The database is already created with the correct name by Heroku
    print_status "Using the database created by Heroku Postgres addon..."
    
    # Extract connection details from DATABASE_URL
    # Format: postgres://user:password@host:port/database
    DB_HOST=$(echo "$DATABASE_URL" | sed 's/.*@\([^:]*\):.*/\1/')
    DB_PORT=$(echo "$DATABASE_URL" | sed 's/.*:\([0-9]*\)\/.*/\1/')
    DB_USER=$(echo "$DATABASE_URL" | sed 's/postgres:\/\/\([^:]*\):.*/\1/')
    DB_PASSWORD=$(echo "$DATABASE_URL" | sed 's/postgres:\/\/[^:]*:\([^@]*\)@.*/\1/')
    DB_NAME=$(echo "$DATABASE_URL" | sed 's/.*\/\([^?]*\).*/\1/')
    
    print_info "Database name: $DB_NAME"
    
    # Use the DATABASE_URL as AGENT_SESSION_STORE_URI
    AGENT_SESSION_STORE_URI="$DATABASE_URL"
    
    print_status "Setting AGENT_SESSION_STORE_URI..."
    if heroku config:set AGENT_SESSION_STORE_URI="$AGENT_SESSION_STORE_URI" --app "$APP_NAME"; then
        print_status "AGENT_SESSION_STORE_URI set successfully"
    else
        print_error "Failed to set AGENT_SESSION_STORE_URI"
        exit 1
    fi
else
    print_error "DATABASE_URL not found. PostgreSQL addon may not be ready yet."
    print_info "Please wait a few minutes and try again, or check the addon status:"
    echo "   heroku addons:info heroku-postgresql --app $APP_NAME"
    exit 1
fi

# Verify the setup
print_status "Verifying PostgreSQL setup..."
if heroku config:get AGENT_SESSION_STORE_URI --app "$APP_NAME" &> /dev/null; then
    AGENT_SESSION_STORE_URI=$(heroku config:get AGENT_SESSION_STORE_URI --app "$APP_NAME")
    print_status "AGENT_SESSION_STORE_URI is set: ${AGENT_SESSION_STORE_URI:0:50}..."
else
    print_error "AGENT_SESSION_STORE_URI is not set"
    exit 1
fi

# Test database connectivity (if psycopg2 is available)
print_info "Testing database connectivity..."
if command -v python3 &> /dev/null; then
    # Create a temporary test script
    cat > /tmp/test_db_connection.py << 'EOF'
import os
import sys
try:
    import psycopg2
    from urllib.parse import urlparse
    
    session_store_uri = os.getenv('AGENT_SESSION_STORE_URI')
    if not session_store_uri:
        print("❌ AGENT_SESSION_STORE_URI not set")
        sys.exit(1)
    
    # Parse the URI
    parsed_uri = urlparse(session_store_uri)
    
    # Test connection
    conn = psycopg2.connect(session_store_uri)
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    print(f"✅ Successfully connected to PostgreSQL: {version}")
    sys.exit(0)
    
except ImportError:
    print("⚠️  psycopg2 not available, skipping connectivity test")
    sys.exit(0)
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)
EOF
    
    # Run the test with the AGENT_SESSION_STORE_URI
    if AGENT_SESSION_STORE_URI="$AGENT_SESSION_STORE_URI" python3 /tmp/test_db_connection.py; then
        print_status "Database connectivity test passed"
    else
        print_warning "Database connectivity test failed, but setup may still be valid"
    fi
    
    # Clean up
    rm -f /tmp/test_db_connection.py
else
    print_warning "Python3 not available, skipping connectivity test"
fi

# Show final configuration
print_status "PostgreSQL storage setup completed successfully!"
echo ""
echo "📊 Configuration Summary:"
echo "  App Name: $APP_NAME"
echo "  PostgreSQL Plan: $POSTGRES_PLAN"
echo "  AGENT_SESSION_STORE_URI: ${AGENT_SESSION_STORE_URI:0:50}..."
echo ""
echo "🔧 Useful Commands:"
echo "  View config: heroku config --app $APP_NAME"
echo "  View addons: heroku addons --app $APP_NAME"
echo "  View logs: heroku logs --tail --app $APP_NAME"
echo "  Connect to DB: heroku pg:psql --app $APP_NAME"
echo ""
echo "🚀 Next Steps:"
echo "  1. Your PostgreSQL storage is ready for AI Agents"
echo "  2. Update your agent configuration to use DatabaseSessionService"
echo "  3. Deploy your application to use the new storage"
echo ""
echo "💡 To use this storage in your code:"
echo "  from google.adk.sessions import DatabaseSessionService"
echo "  import os"
echo "  session_service = DatabaseSessionService(os.getenv('AGENT_SESSION_STORE_URI'))"
