from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from src.agents.registry import get_agent_instance
import logging
from src.models.base_models import FeatureMap, AgentChatRequest, AgentChatResponse


logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/chat")
async def chat(request: AgentChatRequest) -> AgentChatResponse:
    """
    Generic chat endpoint that routes to the requested agent using the registry.
    """
    try:
        logger.info(f"Chatting with agent: {request.agent_name}")

        # Get agent instance from registry (singleton)
        agent = get_agent_instance(request.agent_name)

        # Delegate chat to the agent implementation
        result = await agent.chat(request)
        logger.info(f"Result from agent chat: {result}")

        return result
            
    except KeyError as e:
        logger.error(f"Agent not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Agent chat failed")
        raise HTTPException(status_code=500, detail=str(e))

