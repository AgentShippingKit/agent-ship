#!/bin/bash

# AgentShip - One-Command Setup Script
# This script automates the entire setup process for AgentShip

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
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

print_header() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Check if running from correct directory
if [ ! -f "pyproject.toml" ] && [ ! -f "Pipfile" ]; then
    print_error "Please run this script from the ai-ecosystem directory"
    exit 1
fi

print_header "🚀 AgentShip Setup Script"
echo ""

# Step 1: Check prerequisites
print_header "Step 1: Checking Prerequisites"

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.13+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
print_success "Python $PYTHON_VERSION found"

# Check pipenv
if ! command -v pipenv &> /dev/null; then
    print_warning "pipenv not found. Installing pipenv..."
    pip install pipenv
    print_success "pipenv installed"
else
    print_success "pipenv found"
fi

echo ""

# Step 2: Install dependencies
print_header "Step 2: Installing Dependencies"

print_info "Installing Python dependencies (this may take a few minutes)..."
if pipenv install --dev; then
    print_success "Dependencies installed successfully"
else
    print_error "Failed to install dependencies"
    exit 1
fi

echo ""

# Step 3: Setup environment file
print_header "Step 3: Setting Up Environment"

if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        print_info "Creating .env file from env.example..."
        cp env.example .env
        print_success ".env file created"
        print_warning "⚠️  IMPORTANT: Please edit .env and add your API keys:"
        echo "   - At least one LLM API key (OPENAI_API_KEY, GOOGLE_API_KEY, or ANTHROPIC_API_KEY)"
        echo "   - Optional: OPIK_API_KEY for observability"
        echo "   - Optional: SESSION_STORE_URI for database sessions"
    else
        print_error "env.example not found"
        exit 1
    fi
else
    print_warning ".env file already exists, skipping..."
fi

echo ""

# Step 4: Database setup (optional)
print_header "Step 4: Database Setup (Optional)"

read -p "Do you want to set up PostgreSQL for session storage? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "agent_store_deploy/setup_local_postgres.sh" ]; then
        print_info "Setting up PostgreSQL..."
        chmod +x agent_store_deploy/setup_local_postgres.sh
        cd agent_store_deploy
        ./setup_local_postgres.sh
        cd ..
        print_success "PostgreSQL setup completed"
    else
        print_warning "PostgreSQL setup script not found. Skipping database setup."
        print_info "You can set up PostgreSQL manually later or use in-memory sessions."
    fi
else
    print_info "Skipping database setup. You can use in-memory sessions or set up PostgreSQL later."
fi

echo ""

# Step 5: Verify installation
print_header "Step 5: Verifying Installation"

print_info "Running quick verification tests..."

# Check if we can import the main module
if pipenv run python -c "import src.service.main" 2>/dev/null; then
    print_success "Core modules can be imported"
else
    print_warning "Some modules may have import issues (this is normal if API keys are missing)"
fi

echo ""

# Step 6: Summary
print_header "✨ Setup Complete!"

echo ""
print_success "AgentShip is ready to use!"
echo ""
print_info "Next steps:"
echo ""
echo "1. Edit .env file and add your API keys:"
echo "   ${YELLOW}nano .env${NC}  (or use your preferred editor)"
echo ""
echo "2. Start the development server:"
echo "   ${YELLOW}make dev${NC}  or  ${YELLOW}pipenv run uvicorn src.service.main:app --reload --port 7001${NC}"
echo ""
echo "3. Access the API documentation:"
echo "   ${YELLOW}http://localhost:7001/docs${NC}"
echo ""
echo "4. Run tests:"
echo "   ${YELLOW}make test${NC}  or  ${YELLOW}pipenv run pytest${NC}"
echo ""
echo "5. View available commands:"
echo "   ${YELLOW}make help${NC}"
echo ""

print_info "📚 Documentation:"
echo "   - Installation: ${YELLOW}docs/getting-started/installation.md${NC}"
echo "   - API Docs: ${YELLOW}http://localhost:7001/docs${NC} (after starting server)"
echo "   - Full Docs: ${YELLOW}make docs-serve${NC}"
echo ""

print_warning "⚠️  Remember to add your API keys to .env before running the server!"
echo ""

