#!/bin/bash

# AgentShip - Local PostgreSQL Setup Script
# This script sets up a local PostgreSQL database for session storage

set -e  # Exit on any error

echo "🐘 Setting up PostgreSQL for AI Agents Session Store..."

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

# Database configuration - can be overridden by environment variables
DB_NAME="${DB_NAME:-ai_agents_store}"
DB_USER="${DB_USER:-ai_agents_user}"
DB_PASSWORD="${DB_PASSWORD:-ai_agents_password}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

# Display configuration being used
echo ""
print_info "Using the following database configuration:"
echo "  Database Name: $DB_NAME"
echo "  Username: $DB_USER"
echo "  Password: $DB_PASSWORD"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo ""
print_info "To override any of these values, set the corresponding environment variable before running this script."
echo "  Example: DB_NAME=my_custom_db ./setup_local_postgres.sh"
echo ""

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    print_error "PostgreSQL is not installed. Please install it first:"
    echo ""
    echo "On macOS (using Homebrew):"
    echo "  brew install postgresql"
    echo "  brew services start postgresql"
    echo ""
    echo "On Ubuntu/Debian:"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install postgresql postgresql-contrib"
    echo "  sudo systemctl start postgresql"
    echo "  sudo systemctl enable postgresql"
    echo ""
    echo "On CentOS/RHEL:"
    echo "  sudo yum install postgresql-server postgresql-contrib"
    echo "  sudo postgresql-setup initdb"
    echo "  sudo systemctl start postgresql"
    echo "  sudo systemctl enable postgresql"
    exit 1
fi

print_status "PostgreSQL is installed"

# Check if PostgreSQL service is running
if ! pg_isready -q; then
    print_warning "PostgreSQL service is not running. Attempting to start it..."
    
    # Try to start PostgreSQL service
    if command -v brew &> /dev/null; then
        # macOS with Homebrew
        brew services start postgresql
    elif command -v systemctl &> /dev/null; then
        # Linux with systemd
        sudo systemctl start postgresql
    elif command -v service &> /dev/null; then
        # Linux with service command
        sudo service postgresql start
    else
        print_error "Could not start PostgreSQL service automatically. Please start it manually."
        exit 1
    fi
    
    # Wait a moment for the service to start
    sleep 3
    
    # Check again
    if ! pg_isready -q; then
        print_error "PostgreSQL service failed to start. Please start it manually and try again."
        exit 1
    fi
fi

print_status "PostgreSQL service is running"

# Check if we can connect to PostgreSQL
if ! psql -c "SELECT 1;" &> /dev/null; then
    print_warning "Cannot connect to PostgreSQL with default settings. Trying alternative connection methods..."
    
    # Try connecting as current user
    if psql -U "$(whoami)" -c "SELECT 1;" &> /dev/null; then
        print_status "Successfully connected as user: $(whoami)"
        # Set PGPASSWORD to empty for subsequent connections
        export PGPASSWORD=""
    elif psql -U postgres -c "SELECT 1;" &> /dev/null; then
        print_status "Successfully connected as user: postgres"
    else
        # Try to create the default database for current user (common issue on macOS)
        print_info "Attempting to create default database for user: $(whoami)"
        if createdb "$(whoami)" 2>/dev/null; then
            print_status "Created default database for user: $(whoami)"
            if psql -U "$(whoami)" -c "SELECT 1;" &> /dev/null; then
                print_status "Successfully connected as user: $(whoami)"
                export PGPASSWORD=""
            else
                print_error "Still cannot connect after creating default database"
                exit 1
            fi
        else
            print_error "Cannot connect to PostgreSQL. Please check your PostgreSQL installation and permissions."
            print_info "Common solutions:"
            echo "  1. On macOS with Homebrew: brew services restart postgresql"
            echo "  2. Check if PostgreSQL is running: brew services list | grep postgresql"
            echo "  3. Try connecting manually: psql -U $(whoami)"
            echo "  4. Check PostgreSQL logs for errors"
            echo "  5. Create default database: createdb $(whoami)"
            exit 1
        fi
    fi
fi

print_status "Successfully connected to PostgreSQL"

# Determine the correct psql command based on what worked
if psql -U "$(whoami)" -c "SELECT 1;" &> /dev/null; then
    PSQL_CMD="psql -U $(whoami)"
elif psql -U postgres -c "SELECT 1;" &> /dev/null; then
    PSQL_CMD="psql -U postgres"
else
    PSQL_CMD="psql"
fi

print_info "Using psql command: $PSQL_CMD"

# Check if database already exists
if $PSQL_CMD -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    print_warning "Database '$DB_NAME' already exists"
    
    # Check if user already exists
    if $PSQL_CMD -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER';" | grep -q 1; then
        print_warning "User '$DB_USER' already exists"
        print_info "Database and user are already set up. Nothing to do."
    else
        print_info "Creating user '$DB_USER'..."
        $PSQL_CMD -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
        $PSQL_CMD -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
        print_status "User '$DB_USER' created and granted privileges"
    fi
else
    print_info "Creating database '$DB_NAME'..."
    $PSQL_CMD -c "CREATE DATABASE $DB_NAME;"
    print_status "Database '$DB_NAME' created"
    
    print_info "Creating user '$DB_USER'..."
    $PSQL_CMD -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
    $PSQL_CMD -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    print_status "User '$DB_USER' created and granted privileges"
fi

# Test the connection with the new user and database
print_info "Testing connection to the new database..."
if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" &> /dev/null; then
    print_status "Successfully connected to database '$DB_NAME' with user '$DB_USER'"
else
    print_error "Failed to connect to database '$DB_NAME' with user '$DB_USER'"
    print_info "This might be due to PostgreSQL authentication settings."
    print_info "You can test the connection manually with:"
    echo "  PGPASSWORD='$DB_PASSWORD' psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
    exit 1
fi

# Generate the connection URI
SESSION_STORE_URI="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"

print_status "PostgreSQL setup completed successfully!"
echo ""
echo "📊 Database Information:"
echo "  Database Name: $DB_NAME"
echo "  Username: $DB_USER"
echo "  Password: $DB_PASSWORD"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo ""
echo "🔗 Connection URI:"
echo "  $SESSION_STORE_URI"
echo ""

# Check if .env file exists and update it
if [ -f ".env" ]; then
    print_info "Updating .env file with SESSION_STORE_URI..."
    
    # Check if SESSION_STORE_URI already exists in .env
    if grep -q "SESSION_STORE_URI" .env; then
        # Update existing SESSION_STORE_URI
        sed -i.bak "s|SESSION_STORE_URI=.*|SESSION_STORE_URI=$SESSION_STORE_URI|" .env
        print_status "Updated SESSION_STORE_URI in .env file"
    else
        # Add SESSION_STORE_URI to .env
        echo "" >> .env
        echo "# PostgreSQL Session Store" >> .env
        echo "SESSION_STORE_URI=$SESSION_STORE_URI" >> .env
        print_status "Added SESSION_STORE_URI to .env file"
    fi
else
    print_warning ".env file not found. Please add the following to your .env file:"
    echo ""
    echo "SESSION_STORE_URI=$SESSION_STORE_URI"
    echo ""
fi

print_status "Local PostgreSQL setup completed!"
echo ""
echo "🚀 Next steps:"
echo "  1. The database is ready for use with Google ADK DatabaseSessionService"
echo "  2. Update your agent configuration to use DatabaseSessionService"
echo "  3. The SESSION_STORE_URI has been added to your .env file"
echo ""
echo "💡 To connect to the database manually:"
echo "  psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
