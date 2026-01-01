#!/bin/bash

# Script to check for HealthLogue references in the current branch
# Useful for verifying open-source branch doesn't contain HealthLogue content
# Usage: ./scripts/check_healthlogue_refs.sh [branch-name]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BRANCH=${1:-$(git branch --show-current)}

echo -e "${GREEN}Checking for HealthLogue references in branch: ${BRANCH}${NC}"

# Checkout the branch temporarily if needed
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
    echo -e "${YELLOW}Switching to branch: ${BRANCH}${NC}"
    git checkout "$BRANCH" 2>/dev/null || {
        echo -e "${RED}Error: Branch ${BRANCH} not found${NC}"
        exit 1
    }
fi

# Search for HealthLogue references (case-insensitive)
echo -e "${GREEN}Searching for HealthLogue references...${NC}"
REFS=$(grep -r -i "healthlogue" --include="*.py" --include="*.yaml" --include="*.yml" --include="*.json" --include="*.md" --include="*.txt" --exclude-dir=".git" --exclude-dir="__pycache__" --exclude-dir=".pytest_cache" --exclude-dir="site" --exclude-dir="docs_sphinx" . 2>/dev/null | grep -v ".git" || true)

if [ -z "$REFS" ]; then
    echo -e "${GREEN}✓ No HealthLogue references found!${NC}"
    exit 0
else
    echo -e "${RED}✗ Found HealthLogue references:${NC}"
    echo "$REFS" | while IFS= read -r line; do
        echo -e "  ${YELLOW}$line${NC}"
    done
    echo ""
    echo -e "${RED}Please review and remove these references before merging to open-source.${NC}"
    exit 1
fi

