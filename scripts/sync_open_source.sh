#!/bin/bash

# Script to sync open-source branch with main branch while excluding HealthLogue-specific content
# Usage: ./scripts/sync_open_source.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting open-source branch sync...${NC}"

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${YELLOW}Current branch: ${CURRENT_BRANCH}${NC}"

# HealthLogue-specific paths to exclude (agents that can't be generalized)
HEALTHLOGUE_AGENTS=(
    "src/agents/all_agents/medical_conversation_insights_agent"
    "src/agents/all_agents/medical_followup_agent"
)

# Note: health_assistant_agent and medical_reports_analysis_agent will be generalized
# by the generalize_agents_for_opensource.sh script

HEALTHLOGUE_TOOLS=(
    "src/agents/tools/conversation_insights_tool.py"
    "src/agents/tools/medical_reports_tool.py"
    "src/agents/tools/voice_notes_tool.py"
    "src/agents/tools/action_items_tool.py"
    "src/agents/tools/action_items_creation_tool.py"
)

# Step 1: Ensure we're on open-source branch or create sync branch
if [ "$CURRENT_BRANCH" != "open-source" ]; then
    echo -e "${YELLOW}Not on open-source branch. Creating sync branch from open-source...${NC}"
    git fetch origin open-source 2>/dev/null || true
    git checkout open-source 2>/dev/null || git checkout -b open-source
    git pull origin open-source 2>/dev/null || true
fi

# Create a temporary branch for syncing
SYNC_BRANCH="open-source-sync-$(date +%Y%m%d-%H%M%S)"
echo -e "${GREEN}Creating temporary branch: ${SYNC_BRANCH}${NC}"
git checkout -b "$SYNC_BRANCH"

# Step 2: Merge main into sync branch (no commit)
echo -e "${GREEN}Merging main branch...${NC}"
git merge main --no-commit --no-ff || {
    echo -e "${YELLOW}Merge conflicts detected. This is expected.${NC}"
}

# Step 3: Remove HealthLogue-specific agents (that can't be generalized)
echo -e "${GREEN}Removing HealthLogue-specific agents...${NC}"
for agent_path in "${HEALTHLOGUE_AGENTS[@]}"; do
    if [ -e "$agent_path" ] || git ls-files --error-unmatch "$agent_path" > /dev/null 2>&1; then
        echo -e "  Removing: $agent_path"
        git rm -rf "$agent_path" 2>/dev/null || rm -rf "$agent_path"
    fi
done

# Step 3.5: Generalize and rename agents
echo -e "${GREEN}Generalizing agents for open-source...${NC}"
if [ -f "scripts/generalize_agents_for_opensource.sh" ]; then
    ./scripts/generalize_agents_for_opensource.sh
else
    echo -e "${YELLOW}Warning: generalize_agents_for_opensource.sh not found. Skipping agent generalization.${NC}"
fi

# Step 4: Remove HealthLogue-specific tools
echo -e "${GREEN}Removing HealthLogue-specific tools...${NC}"
for tool_path in "${HEALTHLOGUE_TOOLS[@]}"; do
    if [ -e "$tool_path" ] || git ls-files --error-unmatch "$tool_path" > /dev/null 2>&1; then
        echo -e "  Removing: $tool_path"
        git rm "$tool_path" 2>/dev/null || rm -f "$tool_path"
    fi
done

# Step 5: Check for HealthLogue references in code
echo -e "${GREEN}Checking for HealthLogue references in code...${NC}"
HEALTHLOGUE_REFS=$(git diff --cached --name-only | xargs grep -l -i "healthlogue" 2>/dev/null || true)
if [ -n "$HEALTHLOGUE_REFS" ]; then
    echo -e "${YELLOW}Warning: Found HealthLogue references in:${NC}"
    echo "$HEALTHLOGUE_REFS" | while read -r file; do
        echo -e "  ${YELLOW}- $file${NC}"
    done
    echo -e "${YELLOW}Please review and clean these files manually.${NC}"
fi

# Step 6: Clean up tool imports
echo -e "${GREEN}Cleaning up tool imports...${NC}"
TOOLS_INIT="src/agents/tools/__init__.py"
if [ -f "$TOOLS_INIT" ]; then
    echo -e "${YELLOW}Please manually review $TOOLS_INIT to remove HealthLogue-specific tool imports${NC}"
fi

# Step 7: Show status
echo -e "${GREEN}Current status:${NC}"
git status --short

# Step 8: Ask for confirmation before committing
echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Review the changes above carefully!${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""
echo -e "Next steps:"
echo -e "1. Review the changes: ${GREEN}git status${NC}"
echo -e "2. Review specific files: ${GREEN}git diff --cached${NC}"
echo -e "3. Manually clean up Postman files if needed"
echo -e "4. Clean up tool imports in src/agents/tools/__init__.py"
echo -e "5. When ready, commit: ${GREEN}git commit -m 'Sync open-source with main (excluding HealthLogue content)'${NC}"
echo -e "6. Test thoroughly before merging to open-source"
echo ""
read -p "Do you want to commit these changes now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git commit -m "Sync open-source with main (excluding HealthLogue-specific content)"
    echo -e "${GREEN}Changes committed to ${SYNC_BRANCH}${NC}"
    echo -e "${YELLOW}Next: Test the changes, then merge to open-source:${NC}"
    echo -e "  ${GREEN}git checkout open-source${NC}"
    echo -e "  ${GREEN}git merge ${SYNC_BRANCH}${NC}"
else
    echo -e "${YELLOW}Changes staged but not committed. Review and commit manually.${NC}"
fi

echo -e "${GREEN}Sync branch created: ${SYNC_BRANCH}${NC}"

