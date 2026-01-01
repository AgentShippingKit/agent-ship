#!/bin/bash

# Script to generalize and rename agents for open-source branch
# This should be run after merging main into a sync branch, before committing

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Generalizing agents for open-source...${NC}"

BASE_DIR="src/agents/all_agents"

# 1. Rename medical_reports_analysis_agent to file_analysis_agent
if [ -d "${BASE_DIR}/medical_reports_analysis_agent" ]; then
    echo -e "${GREEN}Renaming medical_reports_analysis_agent to file_analysis_agent...${NC}"
    
    # Create new directory
    mkdir -p "${BASE_DIR}/file_analysis_agent"
    
    # Copy and generalize main_agent.py
    if [ -f "${BASE_DIR}/medical_reports_analysis_agent/main_agent.py" ]; then
        sed -e 's/MedicalReportsAnalysisInput/FileAnalysisInput/g' \
            -e 's/MedicalReportsAnalysisOutput/FileAnalysisOutput/g' \
            -e 's/MedicalReportsAnalysisAgent/FileAnalysisAgent/g' \
            -e 's/medical reports analysis/file analysis/g' \
            -e 's/medical report/file/g' \
            -e 's/medical_report_path/file_path/g' \
            -e 's/medical reports/file documents/g' \
            "${BASE_DIR}/medical_reports_analysis_agent/main_agent.py" > \
            "${BASE_DIR}/file_analysis_agent/main_agent.py"
    fi
    
    # Copy and generalize main_agent.yaml
    if [ -f "${BASE_DIR}/medical_reports_analysis_agent/main_agent.yaml" ]; then
        sed -e 's/medical_reports_analysis_agent/file_analysis_agent/g' \
            -e 's/MedicalReportsAnalysisInput/FileAnalysisInput/g' \
            -e 's/MedicalReportsAnalysisOutput/FileAnalysisOutput/g' \
            -e 's/medical reports analysis/file analysis/g' \
            -e 's/medical report/file document/g' \
            -e 's/medical_report_path/file_path/g' \
            -e 's/tags: \[medical, reports, analysis\]/tags: [file, analysis, document]/g' \
            -e 's/specialized in analyzing medical reports/specialized in analyzing files and documents/g' \
            "${BASE_DIR}/medical_reports_analysis_agent/main_agent.yaml" > \
            "${BASE_DIR}/file_analysis_agent/main_agent.yaml"
    fi
    
    # Copy __init__.py if it exists
    if [ -f "${BASE_DIR}/medical_reports_analysis_agent/__init__.py" ]; then
        cp "${BASE_DIR}/medical_reports_analysis_agent/__init__.py" \
           "${BASE_DIR}/file_analysis_agent/__init__.py"
    fi
    
    # Remove old directory from git
    git rm -rf "${BASE_DIR}/medical_reports_analysis_agent" 2>/dev/null || rm -rf "${BASE_DIR}/medical_reports_analysis_agent"
    
    # Add new directory
    git add "${BASE_DIR}/file_analysis_agent"
    
    echo -e "${GREEN}✓ Renamed medical_reports_analysis_agent to file_analysis_agent${NC}"
fi

# 2. Rename health_assistant_agent to personal_assistant_agent (simplified version)
if [ -d "${BASE_DIR}/health_assistant_agent" ]; then
    echo -e "${GREEN}Creating simplified personal_assistant_agent from health_assistant_agent...${NC}"
    
    # Create new directory
    mkdir -p "${BASE_DIR}/personal_assistant_agent"
    
    # Create simplified main_agent.py (without HealthLogue-specific sub-agent imports)
    cat > "${BASE_DIR}/personal_assistant_agent/main_agent.py" << 'PYEOF'
"""Personal assistant agent - a general-purpose assistant for answering questions and helping with tasks."""

from typing import List
from pydantic import BaseModel, Field
from src.agents.all_agents.base_agent import BaseAgent
from src.models.base_models import AgentChatRequest
from google.adk.tools import FunctionTool, AgentTool


class PersonalAssistantInput(BaseModel):
    """Input for answering questions and helping with tasks."""
    message: str = Field(description="The message to answer.")
    session_id: str = Field(description="The session id to answer the question.")
    user_id: str = Field(description="The user id to answer the question.")


class PersonalAssistantOutput(BaseModel):
    """Output for answering questions and helping with tasks."""
    answer: str = Field(description="The answer to the question.")
    session_id: str = Field(description="The session id to answer the question.")
    user_id: str = Field(description="The user id to answer the question.")


class PersonalAssistantAgent(BaseAgent):
    """Agent for answering questions and helping with various tasks."""

    def __init__(self):
        """Initialize the personal assistant agent."""
        # Config auto-loads, chat() is implemented by base class
        super().__init__(
            _caller_file=__file__,
            input_schema=PersonalAssistantInput,
            output_schema=PersonalAssistantOutput
        )

    def _create_input_from_request(self, request: AgentChatRequest) -> BaseModel:
        """Create input schema from request with message, session_id, and user_id."""
        return PersonalAssistantInput(
            message=request.query if isinstance(request.query, str) else str(request.query),
            session_id=request.session_id,
            user_id=request.user_id,
        )

    # Tools are configured via YAML (`tools` section in main_agent.yaml).
    # Add your custom tools in the YAML configuration.
PYEOF
    
    # Create simplified main_agent.yaml (remove HealthLogue-specific tools/sub-agents)
    if [ -f "${BASE_DIR}/health_assistant_agent/main_agent.yaml" ]; then
        # Create a simplified version without HealthLogue-specific tools
        cat > "${BASE_DIR}/personal_assistant_agent/main_agent.yaml" << 'EOF'
agent_name: personal_assistant_agent
tags: [assistant, personal, general]
llm_provider_name: openai
llm_model: gpt-4o
temperature: 0.4
description: A general-purpose personal assistant that can answer questions and help with various tasks.
instruction_template: >
  You are an expert personal assistant. You are responsible for answering questions and helping users with various tasks.
  
  You will receive input in the following format:
  - message: The message to answer.
  - session_id: The session id to answer the question.
  - user_id: The user id to answer the question.

  CRITERIA FOR ANSWERING QUESTIONS:
  - focus on providing the most relevant answer to the question
  - the answer should be in a friendly and engaging tone but not too informal.
  - the answer should be in a concise and to the point manner.
  - the answer should be in a grammatically correct manner.
  - the answer should be in a way that is easy to understand and not too technical but sometimes it can be technical if the question is technical.
  
  Your output should be in the following format. Try to keep a balance between detailed and concise. In case you feel like using markdown, feel free to do so:
  PersonalAssistantOutput model:
  - answer: str

tools:
  # Add your custom tools here
  # Example:
  # - type: function
  #   id: custom_tool
  #   import: src.agents.tools.custom_tool.CustomTool
  #   method: run
EOF
    fi
    
    # Copy __init__.py if it exists
    if [ -f "${BASE_DIR}/health_assistant_agent/__init__.py" ]; then
        echo "# Personal Assistant Agent" > "${BASE_DIR}/personal_assistant_agent/__init__.py"
    fi
    
    # Note: We're NOT removing health_assistant_agent - it stays on main branch
    # We're just creating a simplified generic version for open-source
    
    # Add new directory
    git add "${BASE_DIR}/personal_assistant_agent"
    
    echo -e "${GREEN}✓ Created simplified personal_assistant_agent${NC}"
    echo -e "${YELLOW}Note: health_assistant_agent remains on main branch with HealthLogue-specific features${NC}"
fi

# 3. Update test files if they exist
if [ -f "tests/unit/agents/all_agents/test_medical_reports_analysis_agent.py" ]; then
    echo -e "${GREEN}Updating test file for file_analysis_agent...${NC}"
    mkdir -p "tests/unit/agents/all_agents"
    
    sed -e 's/test_medical_reports_analysis_agent/test_file_analysis_agent/g' \
        -e 's/MedicalReportsAnalysisAgent/FileAnalysisAgent/g' \
        -e 's/MedicalReportsAnalysisInput/FileAnalysisInput/g' \
        -e 's/MedicalReportsAnalysisOutput/FileAnalysisOutput/g' \
        -e 's/medical_reports_analysis_agent/file_analysis_agent/g' \
        -e 's/medical_reports_analysis_agent\.main_agent/file_analysis_agent.main_agent/g' \
        "tests/unit/agents/all_agents/test_medical_reports_analysis_agent.py" > \
        "tests/unit/agents/all_agents/test_file_analysis_agent.py"
    
    git rm "tests/unit/agents/all_agents/test_medical_reports_analysis_agent.py" 2>/dev/null || true
    git add "tests/unit/agents/all_agents/test_file_analysis_agent.py"
fi

echo -e "${GREEN}✓ Agent generalization complete!${NC}"
echo -e "${YELLOW}Please review the changes before committing.${NC}"

