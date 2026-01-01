#!/bin/bash

# AgentShip - True One-Command Setup
# Handles everything: Docker check, .env creation, API key prompt, container startup

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_header() { echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n${CYAN}$1${NC}\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; }

print_header "🐳 AgentShip - One-Command Setup"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    print_warning "Docker not found. Install from: https://www.docker.com/products/docker-desktop"
    exit 1
fi
print_success "Docker found"

if ! docker compose version &> /dev/null 2>&1 && ! docker-compose version &> /dev/null 2>&1; then
    print_warning "Docker Compose not available"
    exit 1
fi
print_success "Docker Compose available"

# Create/update .env
if [ ! -f ".env" ]; then
    print_info "Creating .env file..."
    cp env.example .env
    
    # Update database URI for Docker
    sed -i.bak 's|SESSION_STORE_URI=.*|AGENT_SESSION_STORE_URI=postgresql://ai_agents_user:ai_agents_password@postgres:5432/ai_agents_store|' .env 2>/dev/null || \
    sed -i '' 's|SESSION_STORE_URI=.*|AGENT_SESSION_STORE_URI=postgresql://ai_agents_user:ai_agents_password@postgres:5432/ai_agents_store|' .env
    
    # Prompt for API key
    echo ""
    print_info "You need at least one LLM API key to use agents."
    echo ""
    read -p "Enter your OpenAI API key (or press Enter to skip): " OPENAI_KEY
    if [ ! -z "$OPENAI_KEY" ]; then
        sed -i.bak "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=$OPENAI_KEY|" .env 2>/dev/null || \
        sed -i '' "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=$OPENAI_KEY|" .env
        print_success "OpenAI API key added"
else
        read -p "Enter your Google API key (or press Enter to skip): " GOOGLE_KEY
        if [ ! -z "$GOOGLE_KEY" ]; then
            sed -i.bak "s|GOOGLE_API_KEY=.*|GOOGLE_API_KEY=$GOOGLE_KEY|" .env 2>/dev/null || \
            sed -i '' "s|GOOGLE_API_KEY=.*|GOOGLE_API_KEY=$GOOGLE_KEY|" .env
            print_success "Google API key added"
        else
            read -p "Enter your Anthropic API key (or press Enter to skip): " ANTHROPIC_KEY
            if [ ! -z "$ANTHROPIC_KEY" ]; then
                sed -i.bak "s|ANTHROPIC_API_KEY=.*|ANTHROPIC_API_KEY=$ANTHROPIC_KEY|" .env 2>/dev/null || \
                sed -i '' "s|ANTHROPIC_API_KEY=.*|ANTHROPIC_API_KEY=$ANTHROPIC_KEY|" .env
                print_success "Anthropic API key added"
            else
                print_warning "No API key provided. You can add one later in .env file"
            fi
        fi
    fi
else
    print_info ".env file exists"
    # Update database URI if needed
    if grep -q "SESSION_STORE_URI=postgresql://.*localhost" .env; then
        sed -i.bak 's|SESSION_STORE_URI=.*localhost|AGENT_SESSION_STORE_URI=postgresql://ai_agents_user:ai_agents_password@postgres:5432/ai_agents_store|' .env 2>/dev/null || \
        sed -i '' 's|SESSION_STORE_URI=.*localhost|AGENT_SESSION_STORE_URI=postgresql://ai_agents_user:ai_agents_password@postgres:5432/ai_agents_store|' .env
    fi
fi

# Determine compose command
    COMPOSE_CMD="docker compose"
if ! docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
fi

# Build and start
echo ""
print_header "🚀 Starting AgentShip"
echo ""
print_info "Building containers (first time may take a few minutes)..."
$COMPOSE_CMD up --build -d

# Wait for health check
echo ""
print_info "Waiting for services to start..."
sleep 10

MAX_WAIT=90
WAIT_COUNT=0
while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    if curl -f http://localhost:7001/health &> /dev/null 2>&1; then
        echo ""
        print_success "✨ AgentShip is ready!"
        echo ""
        echo "📚 Documentation:"
        echo -e "   API Docs (Swagger): ${CYAN}http://localhost:7001/swagger${NC}"
        echo -e "   Framework Docs:     ${CYAN}http://localhost:7001/docs${NC}"
        echo -e "   Debug UI:           ${CYAN}http://localhost:7001/debug-ui${NC}"
        echo ""
        exit 0
    fi
    echo -n "."
    sleep 3
    WAIT_COUNT=$((WAIT_COUNT + 3))
done

echo ""
print_warning "Service is starting (may take a bit longer)"
echo -e "Check status: ${CYAN}make docker-logs${NC}"
echo -e "API Docs: ${CYAN}http://localhost:7001/swagger${NC}"
echo -e "Framework Docs: ${CYAN}http://localhost:7001/docs${NC}"
echo -e "Debug UI: ${CYAN}http://localhost:7001/debug-ui${NC}"
