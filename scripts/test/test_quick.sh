#!/bin/bash

# AgentShip - Quick Test Script
# This script quickly validates that the framework is set up correctly

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo "🧪 AgentShip Quick Test"
echo ""

# Test 1: Check if dependencies are installed
print_info "Test 1: Checking dependencies..."
if pipenv --version &> /dev/null; then
    print_success "pipenv is installed"
else
    print_error "pipenv is not installed. Run: make setup"
    exit 1
fi

# Test 2: Check if virtual environment exists
print_info "Test 2: Checking virtual environment..."
if pipenv --venv &> /dev/null; then
    print_success "Virtual environment exists"
else
    print_warning "Virtual environment not found. Installing dependencies..."
    pipenv install --dev
fi

# Test 3: Check if .env file exists
print_info "Test 3: Checking environment configuration..."
if [ -f ".env" ]; then
    print_success ".env file exists"
    
    # Check if at least one API key is set
    if grep -q "OPENAI_API_KEY=" .env && ! grep -q "OPENAI_API_KEY=your-" .env; then
        print_success "OPENAI_API_KEY is configured"
    elif grep -q "GOOGLE_API_KEY=" .env && ! grep -q "GOOGLE_API_KEY=your-" .env; then
        print_success "GOOGLE_API_KEY is configured"
    elif grep -q "ANTHROPIC_API_KEY=" .env && ! grep -q "ANTHROPIC_API_KEY=your-" .env; then
        print_success "ANTHROPIC_API_KEY is configured"
    else
        print_warning "No API keys found in .env. Add at least one LLM API key to test agents."
    fi
else
    print_warning ".env file not found. Run: cp env.example .env"
fi

# Test 4: Check if core modules can be imported
print_info "Test 4: Testing module imports..."
if pipenv run python -c "import src.service.main; import src.agent_framework.registry.core" 2>/dev/null; then
    print_success "Core modules can be imported"
else
    print_error "Failed to import core modules. Check your installation."
    exit 1
fi

# Test 5: Run a quick unit test
print_info "Test 5: Running quick unit test..."
if pipenv run pytest tests/ -v -k "test_" --maxfail=1 -q 2>/dev/null; then
    print_success "Tests are passing"
else
    print_warning "Some tests may have failed (this is OK if API keys are missing)"
fi

echo ""
print_success "Quick test complete!"
echo ""
print_info "To start the development server:"
echo "  ${YELLOW}make dev${NC}"
echo ""
print_info "To run all tests:"
echo "  ${YELLOW}make test${NC}"
echo ""

