"""Translation agent using Google ADK for multi-language text translation."""

from typing import List
from pydantic import BaseModel, Field
from src.all_agents.base_agent import BaseAgent


class TranslationInput(BaseModel):
    """Input for translation generation."""
    text: str = Field(description="The text to translate.")
    from_language: str = Field(description="The language of the text to translate from.")
    to_language: str = Field(description="The language of the text to translate to.")


class TranslationOutput(BaseModel):
    """Output for translation generation."""
    translated_text: str = Field(description="The translated text.")


class TranslationAgent(BaseAgent):
    """Agent for generating translation."""

    def __init__(self):
        """Initialize the translation agent."""
        # Config auto-loads from main_agent.yaml, chat() is implemented by base class
        super().__init__(
            _caller_file=__file__,
            input_schema=TranslationInput,
            output_schema=TranslationOutput
        )
    
    # No need to override chat() - base class handles it!
    # No need to override _create_tools() or _create_sub_agents() - defaults to empty list


if __name__ == "__main__":
    import asyncio
    import hashlib
    from src.service.models.base_models import AgentChatRequest
    
    async def main():
        agent = TranslationAgent()
        
        # Generate a deterministic session ID
        user_id = "123"
        session_id = hashlib.md5(f"{user_id}".encode()).hexdigest()[:8]
        print(f"Generated session ID: {session_id}")
        
        query = {"text": "Hello, how are you?", "from_language": "en", "to_language": "es"}

        # Create proper input using the schema
        request = AgentChatRequest(
            agent_name=agent._get_agent_name(),
            user_id=user_id,
            session_id=session_id,
            query=query,
            features=[]
        )
        
        result = await agent.chat(request=request)
        print(f"Result: {result}")
    
    asyncio.run(main())