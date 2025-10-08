#!/bin/bash

# Ship AI Agents - Heroku Deployment Script

set -e  # Exit on any error

echo "🚀 Deploying Ship AI Agents to Heroku..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    print_error "Heroku CLI is not installed. Please install it first:"
    echo "   https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

##############################################
# .env presence and validation
##############################################

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    if [ -f "env.example" ]; then
        cp env.example .env
        print_status ".env file created from env.example"
        print_warning "Please edit .env with your actual values before deploying"
    else
        print_error "env.example file not found. Please create a .env file manually."
        exit 1
    fi
fi

# Helper to get a value from .env (ignores comments and surrounding quotes)
get_env_value() {
  local key="$1"
  # shellcheck disable=SC2002
  cat .env \
    | grep -E -v '^\s*#' \
    | grep -E "^${key}=" \
    | head -n1 \
    | cut -d'=' -f2- \
    | sed 's/^"//; s/"$//; s/^\'"'"'//; s/\'"'"'$//'
}

# Validate presence of critical variables for AI agents
# Check for at least one API key
API_KEYS=(
  OPENAI_API_KEY
  ANTHROPIC_API_KEY
  GOOGLE_API_KEY
)

HAS_API_KEY=false
for VAR in "${API_KEYS[@]}"; do
  VAL=$(get_env_value "$VAR")
  if [ -n "$VAL" ]; then
    HAS_API_KEY=true
    break
  fi
done

if [ "$HAS_API_KEY" = false ]; then
  print_error "No API keys found in .env file!"
  echo ""
  echo "You need at least one API key for the AI agents to work:"
  echo "  OPENAI_API_KEY=your-openai-key"
  echo "  ANTHROPIC_API_KEY=your-claude-key"
  echo "  GOOGLE_API_KEY=your-google-key"
  echo ""
  echo "Optional variables:"
  echo "  TEMPERATURE=0.7"
  echo "  LOG_LEVEL=INFO"
  echo "  ENVIRONMENT=production"
  exit 1
fi

# Check for other required variables
REQUIRED_VARS=(
  LOG_LEVEL
  ENVIRONMENT
)

MISSING=()
for VAR in "${REQUIRED_VARS[@]}"; do
  VAL=$(get_env_value "$VAR")
  if [ -z "$VAL" ]; then
    MISSING+=("$VAR")
  fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
  print_warning "The following environment variables are missing, but deployment will continue:"
  for VAR in "${MISSING[@]}"; do
    echo "  - $VAR"
  done
  echo ""
  print_status "Setting default values for missing variables..."
  if [[ " ${MISSING[@]} " =~ " LOG_LEVEL " ]]; then
    echo "LOG_LEVEL=INFO" >> .env
  fi
  if [[ " ${MISSING[@]} " =~ " ENVIRONMENT " ]]; then
    echo "ENVIRONMENT=production" >> .env
  fi
fi

# Check if git repository is initialized
if [ ! -d ".git" ]; then
    print_status "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit for Heroku deployment"
fi

# Get app name - use ai-agents-alpha
APP_NAME="ai-agents-alpha"
print_status "Using Heroku app: $APP_NAME"

# Check if the app exists and we have access to it
if heroku apps:info --app "$APP_NAME" &> /dev/null; then
    print_status "App $APP_NAME exists and is accessible"
else
    print_warning "App $APP_NAME does not exist. Creating it..."
    if heroku apps:create "$APP_NAME" --region us; then
        print_status "Successfully created app $APP_NAME"
    else
        print_error "Failed to create app $APP_NAME"
        print_status "Available apps:"
        heroku apps
        exit 1
    fi
fi

# Set up git remote for ai-agents-alpha
if git remote get-url heroku &> /dev/null; then
    print_status "Updating existing heroku remote to point to $APP_NAME"
    git remote set-url heroku "https://git.heroku.com/$APP_NAME.git"
else
    print_status "Adding heroku remote for $APP_NAME"
    git remote add heroku "https://git.heroku.com/$APP_NAME.git"
fi

# Set buildpacks
print_status "Setting up buildpacks..."
heroku buildpacks:set heroku/python --app "$APP_NAME" || print_warning "Buildpack already set or failed to set"

# Note: PostgreSQL storage setup is handled separately
# Run ./agent_store_deploy/setup_heroku_postgres.sh to set up PostgreSQL storage

# Clear build cache to ensure fresh install
print_status "Clearing build cache..."
heroku builds:cache:purge --app "$APP_NAME" || print_warning "Cache purge failed or not needed"

# Check if environment variables are set
print_status "Checking environment variables..."

# Read from .env file and set in Heroku (all keys)
if [ -f ".env" ]; then
    print_status "Setting environment variables from .env file..."
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        if [[ ! $key =~ ^# ]] && [[ -n $key ]] && [[ -n $value ]]; then
            # Remove quotes from value
            clean_value=$(echo "$value" | sed 's/^"//;s/"$//;s/^'"'"'//;s/'"'"'$//')
            echo "Setting $key..."
            if heroku config:set "$key=$clean_value" --app "$APP_NAME"; then
                print_status "Successfully set $key"
            else
                print_warning "Failed to set $key (this might be expected for some variables)"
            fi
        fi
    done < .env
fi

# Set SESSION_STORE_URI from PostgreSQL addon
print_status "Setting SESSION_STORE_URI from PostgreSQL addon..."
if heroku addons:info postgresql --app "$APP_NAME" &> /dev/null; then
    # Get the DATABASE_URL from the PostgreSQL addon
    DATABASE_URL=$(heroku config:get DATABASE_URL --app "$APP_NAME")
    if [ -n "$DATABASE_URL" ]; then
        # Set SESSION_STORE_URI to the same value as DATABASE_URL
        if heroku config:set SESSION_STORE_URI="$DATABASE_URL" --app "$APP_NAME"; then
            print_status "SESSION_STORE_URI set from PostgreSQL addon"
        else
            print_warning "Failed to set SESSION_STORE_URI"
        fi
    else
        print_warning "DATABASE_URL not found. PostgreSQL addon may not be ready yet."
    fi
else
    print_warning "PostgreSQL addon not found. SESSION_STORE_URI will not be set automatically."
fi

# Deploy to Heroku
print_status "Deploying to Heroku..."
git add .
git commit -m "Deploy AI Agents to Heroku - $(date)" || true
git push heroku main

# Wait for deployment to complete
print_status "Waiting for deployment to complete..."
sleep 10

# Check if app is running
print_status "Checking application status..."
if heroku ps --app $APP_NAME | grep -q "up"; then
    print_status "Application is running!"
else
    print_error "Application failed to start. Check logs:"
    heroku logs --tail --app $APP_NAME
    exit 1
fi

# Health check
print_status "Performing health check..."
HEALTH_URL="https://$APP_NAME.herokuapp.com/health"
if curl -f -s $HEALTH_URL > /dev/null; then
    print_status "Health check passed!"
else
    print_warning "Health check failed. Application might still be starting up."
fi

# Show app info
print_status "Deployment completed successfully!"
echo ""
echo "🌐 Application URL: https://$APP_NAME.herokuapp.com"
echo "📊 Dashboard: https://dashboard.heroku.com/apps/$APP_NAME"
echo "📋 Logs: heroku logs --tail --app $APP_NAME"
echo "🔧 Config: heroku config --app $APP_NAME"
echo ""
echo "📚 API Documentation: https://$APP_NAME.herokuapp.com/docs"
echo "🏥 Health Check: https://$APP_NAME.herokuapp.com/health"
echo "🤖 Agents Chat: https://$APP_NAME.herokuapp.com/api/agents/chat"

# Open the app
read -p "Would you like to open the application in your browser? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    heroku open --app $APP_NAME
fi

print_status "Deployment script completed!"
