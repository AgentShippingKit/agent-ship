#!/bin/bash
# Test memory optimizations in Docker with 512MB limit (matching Heroku eco dyno)

set -e

echo "🧪 Testing memory optimizations in Docker..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Build and start test container
echo -e "${YELLOW}📦 Building and starting test container with 512MB memory limit...${NC}"
docker compose -f docker-compose.test.yml up -d --build

# Wait for container to be healthy
echo -e "${YELLOW}⏳ Waiting for container to be healthy...${NC}"
timeout=60
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker inspect agentship-test --format='{{.State.Health.Status}}' 2>/dev/null | grep -q "healthy"; then
        echo -e "${GREEN}✅ Container is healthy!${NC}"
        break
    fi
    sleep 2
    elapsed=$((elapsed + 2))
    echo -n "."
done

if [ $elapsed -ge $timeout ]; then
    echo -e "\n${RED}❌ Container failed to become healthy within ${timeout}s${NC}"
    docker compose -f docker-compose.test.yml logs agentship-test
    docker compose -f docker-compose.test.yml down
    exit 1
fi

echo ""
echo -e "${YELLOW}📊 Checking memory usage...${NC}"

# Get memory stats
MEMORY_STATS=$(docker stats agentship-test --no-stream --format "{{.MemUsage}}" 2>/dev/null || echo "N/A")
MEMORY_PERCENT=$(docker stats agentship-test --no-stream --format "{{.MemPerc}}" 2>/dev/null || echo "N/A")

echo "Memory Usage: $MEMORY_STATS"
echo "Memory Percent: $MEMORY_PERCENT"

# Test health endpoint
echo ""
echo -e "${YELLOW}🔍 Testing /health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:7001/health || echo "FAILED")

if echo "$HEALTH_RESPONSE" | grep -q "running"; then
    echo -e "${GREEN}✅ Health endpoint working!${NC}"
    echo "Response: $HEALTH_RESPONSE"
    
    # Extract memory info if available
    if echo "$HEALTH_RESPONSE" | grep -q "memory_mb"; then
        MEMORY_MB=$(echo "$HEALTH_RESPONSE" | grep -o '"memory_mb":[0-9.]*' | cut -d: -f2)
        WITHIN_LIMIT=$(echo "$HEALTH_RESPONSE" | grep -o '"within_limit":[a-z]*' | cut -d: -f2)
        
        echo ""
        echo "📈 Memory Stats from API:"
        echo "  Memory: ${MEMORY_MB}MB"
        echo "  Within Limit (512MB): $WITHIN_LIMIT"
        
        if [ "$WITHIN_LIMIT" = "true" ]; then
            echo -e "${GREEN}✅ Memory is within 512MB limit!${NC}"
        else
            echo -e "${RED}⚠️  Memory exceeds 512MB limit${NC}"
        fi
    fi
else
    echo -e "${RED}❌ Health endpoint failed!${NC}"
    echo "Response: $HEALTH_RESPONSE"
fi

# Check if container is still running (not OOM killed)
echo ""
echo -e "${YELLOW}🔍 Checking if container is still running...${NC}"
if docker ps | grep -q agentship-test; then
    echo -e "${GREEN}✅ Container is still running (no OOM kill)${NC}"
else
    echo -e "${RED}❌ Container was killed (likely OOM)${NC}"
    docker compose -f docker-compose.test.yml logs agentship-test | tail -20
fi

# Run unit tests in container
echo ""
echo -e "${YELLOW}🧪 Running unit tests in container...${NC}"
docker exec agentship-test pytest tests/unit/test_memory_optimizations.py -v || {
    echo -e "${RED}❌ Unit tests failed${NC}"
}

echo ""
echo -e "${YELLOW}📋 Container logs (last 20 lines):${NC}"
docker compose -f docker-compose.test.yml logs --tail=20 agentship-test

echo ""
echo -e "${YELLOW}🧹 Cleaning up...${NC}"
docker compose -f docker-compose.test.yml down

echo ""
echo -e "${GREEN}✅ Memory optimization tests complete!${NC}"

