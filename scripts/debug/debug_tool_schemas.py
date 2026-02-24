"""Debug script to verify tool schemas are properly converted and sent to LLM."""

import asyncio
import json
import sys
import os

sys.path.insert(0, "src")


async def debug_tool_schemas():
    """Check what tool schemas are actually being sent to the LLM."""
    from src.agent_framework.configs.agent_config import AgentConfig
    from src.agent_framework.configs.llm.llm_provider_config import LLMProviderName, LLMModel
    from src.agent_framework.tools.tool_manager import ToolManager
    from src.agent_framework.mcp.registry import MCPServerRegistry

    print("\n" + "=" * 80)
    print("Tool Schema Debug - Verifying ADK receives correct MCP tool schemas")
    print("=" * 80 + "\n")

    # Reset registry
    MCPServerRegistry.reset_instance()

    # Create agent config
    config = AgentConfig(
        llm_provider_name=LLMProviderName.OPENAI,
        llm_model=LLMModel.GPT_4O_MINI,
        agent_name="postgres_mcp_agent",
        mcp_servers=[{"id": "postgres"}]
    )

    print(f"Agent: {config.agent_name}")
    print(f"MCP servers: {[s.id for s in config.mcp_servers]}\n")

    # Create tools
    print("Creating ADK tools from MCP...")
    adk_tools = ToolManager.create_tools(config, "adk")
    print(f"✓ Created {len(adk_tools)} ADK tools\n")

    print("=" * 80)
    print("Tool Declarations (what ADK sends to the LLM)")
    print("=" * 80 + "\n")

    for tool in adk_tools:
        print(f"Tool: {tool.name}")
        print(f"Description: {tool.description}")

        # Get the function declaration that ADK sends to the LLM
        try:
            declaration = tool._get_declaration()
            if declaration:
                print(f"Function Declaration:")
                print(f"  Name: {declaration.name}")
                print(f"  Description: {declaration.description}")

                if declaration.parameters:
                    print(f"  Parameters Type: {declaration.parameters.type}")
                    print(f"  Properties:")
                    if hasattr(declaration.parameters, 'properties'):
                        for prop_name, prop_schema in declaration.parameters.properties.items():
                            print(f"    - {prop_name}:")
                            print(f"        type: {prop_schema.type}")
                            if hasattr(prop_schema, 'description') and prop_schema.description:
                                print(f"        description: {prop_schema.description}")

                    if hasattr(declaration.parameters, 'required'):
                        print(f"  Required: {declaration.parameters.required}")
                else:
                    print(f"  Parameters: None")
            else:
                print(f"  No declaration available")
        except Exception as e:
            print(f"  Error getting declaration: {e}")
            import traceback
            traceback.print_exc()

        print("\n" + "-" * 80 + "\n")

    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print("\nIf you see proper parameter names above (like 'sql', 'table'),")
    print("then ADK IS getting the correct schema.")
    print("\nIf parameters are missing or wrong, then we have a schema conversion bug.")


if __name__ == "__main__":
    try:
        asyncio.run(debug_tool_schemas())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
