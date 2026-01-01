#!/bin/bash

# Pre-commit hook to prevent HealthLogue-specific content from being committed to open-source branch
# Install: cp scripts/pre-commit-hook-template.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BRANCH=$(git branch --show-current)

# Only check on open-source branch
if [ "$BRANCH" != "open-source" ]; then
    exit 0
fi

echo -e "${YELLOW}Checking for HealthLogue-specific content...${NC}"

# HealthLogue-specific paths that should not be in open-source
# Note: health_assistant_agent and medical_reports_analysis_agent should be generalized
# as personal_assistant_agent and file_analysis_agent respectively
HEALTHLOGUE_PATTERNS=(
    "medical_conversation_insights_agent"
    "medical_followup_agent"
    "conversation_insights_tool"
    "medical_reports_tool"
    "voice_notes_tool"
    "action_items_tool"
    "action_items_creation_tool"
)

# Check staged files
STAGED_FILES=$(git diff --cached --name-only)

VIOLATIONS=0

for file in $STAGED_FILES; do
    for pattern in "${HEALTHLOGUE_PATTERNS[@]}"; do
        if echo "$file" | grep -qi "$pattern"; then
            echo -e "${RED}✗ HealthLogue-specific file detected: $file${NC}"
            VIOLATIONS=$((VIOLATIONS + 1))
        fi
    done
    
    # Check for HealthLogue references in file content
    if git diff --cached "$file" 2>/dev/null | grep -qi "healthlogue"; then
        echo -e "${RED}✗ HealthLogue reference found in: $file${NC}"
        VIOLATIONS=$((VIOLATIONS + 1))
    fi
done

if [ $VIOLATIONS -gt 0 ]; then
    echo -e "${RED}Commit blocked: Found $VIOLATIONS HealthLogue-specific content(s)${NC}"
    echo -e "${YELLOW}Please remove HealthLogue-specific content before committing to open-source branch.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ No HealthLogue-specific content detected${NC}"
exit 0

