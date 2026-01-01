# Agent Tests

This directory contains unit tests for each agent in the framework.

## Test Coverage

Each agent has a dedicated test file that verifies:

1. **Initialization**: Agent can be instantiated correctly
2. **Input Schema**: Agent correctly handles input transformation from `AgentChatRequest`
3. **Output Schema**: Agent correctly parses and validates output
4. **Chat Method**: Agent's `chat()` method works end-to-end with mocked LLM calls

## Tested Agents

- ✅ **TranslationAgent** (`test_translation_agent.py`)
  - Tests translation input/output schemas
  - Tests translation with mocked LLM response

- ✅ **DatabaseAgent** (`test_database_agent.py`)
  - Tests database query handling
  - Verifies tools are configured
  - Tests with mocked LLM response

- ✅ **TripPlannerAgent** (`test_trip_planner_agent.py`)
  - Tests trip planning input/output schemas
  - Verifies sub-agent tools are configured
  - Tests orchestration with mocked LLM response

- ✅ **HealthAssistantAgent** (`test_health_assistant_agent.py`)
  - Tests health assistant input/output schemas
  - Verifies conversation insights tool is configured
  - Tests with mocked LLM response

- ✅ **MedicalConversationInsightsAgent** (`test_medical_conversation_insights_agent.py`)
  - Tests conversation insights input/output schemas
  - Tests feature-based configuration (summary_length, key_findings, action_items)
  - Tests with mocked LLM response

- ✅ **MedicalFollowupAgent** (`test_medical_followup_agent.py`)
  - Tests followup questions input/output schemas
  - Tests feature-based configuration (max_followups)
  - Tests with mocked LLM response

- ✅ **MedicalReportsAnalysisAgent** (`test_medical_reports_analysis_agent.py`)
  - Tests medical report analysis input/output schemas
  - Tests artifact handling
  - Verifies Azure artifact tool is configured
  - Tests with mocked LLM response

## Running Tests

Run all agent tests:
```bash
pipenv run pytest tests/unit/agents/all_agents/
```

Run a specific agent test:
```bash
pipenv run pytest tests/unit/agents/all_agents/test_translation_agent.py
```

Run with verbose output:
```bash
pipenv run pytest tests/unit/agents/all_agents/ -v
```

## Mocking

All tests use mocked LLM calls via the `mock_runner` fixture in `tests/conftest.py`. This ensures:
- Tests run without API keys
- Tests are fast and deterministic
- Tests don't make real API calls

The mocking strategy:
- Mocks the Google ADK `Runner.run()` method
- Returns fake JSON responses that match each agent's output schema
- Allows testing the full agent flow without external dependencies
