"""Debug script to see what tool schemas are actually sent to OpenAI."""

import asyncio
import json
import sys
import os

sys.path.insert(0, "src")

# Monkey patch LiteLLM to log API calls
original_acompletion = None


def setup_litellm_logging():
    """Patch LiteLLM to log what's sent to OpenAI."""
    import litellm
    global original_acompletion

    original_acompletion = litellm.acompletion

    async def logged_acompletion(*args, **kwargs):
        """Wrapper that logs the API call."""
        print("\n" + "=" * 80)
        print("LiteLLM API Call to OpenAI")
        print("=" * 80)
        print(f"\nModel: {kwargs.get('model', 'N/A')}")

        # Log tools/functions
        if 'tools' in kwargs:
            print(f"\n✓ TOOLS FOUND: {len(kwargs['tools'])} tools")
            for i, tool in enumerate(kwargs['tools']):
                print(f"\nTool {i+1}: {tool.get('function', {}).get('name', 'N/A')}")
                func = tool.get('function', {})
                print(f"  Description: {func.get('description', 'N/A')}")
                params = func.get('parameters', {})
                if params:
                    print(f"  Parameters:")
                    print(f"    Type: {params.get('type', 'N/A')}")
                    props = params.get('properties', {})
                    if props:
                        print(f"    Properties:")
                        for prop_name, prop_def in props.items():
                            print(f"      - {prop_name}: {prop_def.get('type', 'N/A')}")
                    required = params.get('required', [])
                    if required:
                        print(f"    Required: {required}")
                else:
                    print(f"  Parameters: NONE")
        else:
            print("\n✗ NO TOOLS in API call")

        if 'functions' in kwargs:
            print(f"\n✓ FUNCTIONS FOUND: {len(kwargs['functions'])} functions")

        print("\n" + "=" * 80 + "\n")

        # Call original
        return await original_acompletion(*args, **kwargs)

    litellm.acompletion = logged_acompletion


async def test_tool_schemas():
    """Test if tool schemas are sent to OpenAI."""

    # Set up logging BEFORE importing agent
    setup_litellm_logging()

    from src.all_agents.postgres_mcp_agent.main_agent import PostgresMcpAgent
    from src.service.models.base_models import TextInput

    print("\n🔍 Creating PostgreSQL MCP agent...")
    agent = PostgresMcpAgent()

    print("🔍 Sending request to agent...")
    print("   This will trigger an LLM call with tools")
    print("   Watch for the API call log above\n")

    # Simple request that should use a tool
    from src.service.models.base_models import AgentChatRequest

    request = AgentChatRequest(
        agent_name="postgres_mcp_agent",
        query="List all tables in the database",  # It's 'query' not 'message'
        session_id="debug_session_123"
    )

    result = await agent.chat(request)

    print("\n✓ Agent response received")
    print(f"Response: {result.response}\n")


if __name__ == "__main__":
    try:
        asyncio.run(test_tool_schemas())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
