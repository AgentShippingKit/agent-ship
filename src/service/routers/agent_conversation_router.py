import asyncio

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from sse_starlette.sse import EventSourceResponse
from src.agent_framework.registry import get_agent_instance
import json
import logging
from src.service.models.base_models import FeatureMap, AgentChatRequest, AgentChatResponse


logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/chat")
async def chat(request: AgentChatRequest) -> AgentChatResponse:
    """
    Generic chat endpoint that routes to the requested agent using the registry.
    
    This is a non-streaming endpoint that returns the complete response after processing.
    For streaming responses, use /chat/stream instead.
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


@router.post("/chat/stream")
async def chat_stream(request: AgentChatRequest):
    """
    Streaming chat endpoint using Server-Sent Events (SSE).
    
    This endpoint streams events as they happen, including:
    - session: Session info (sent first)
    - thinking: Agent is processing
    - tool_call: Agent is calling a tool (shows function name + args)
    - tool_result: Tool returned a result
    - content: Agent's text response (may be sent in chunks)
    - done: Stream complete
    - error: An error occurred
    
    Uses traditional streaming (runner.run()) which works with all Gemini models.
    For bidirectional streaming with interruptions (requires Gemini 2.0/2.5), 
    use WebSocket endpoint (future implementation).
    
    Example client usage:
    ```javascript
    const eventSource = new EventSource('/api/agents/chat/stream', {
      method: 'POST',
      body: JSON.stringify({agent_name: '...', query: '...'})
    });
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log(data.type, data);
    };
    ```
    """
    logger.info(f"🚀 Stream request received for agent: {request.agent_name}")
    
    async def event_generator():
        stream_completed = False
        try:
            logger.info(f"📡 Starting stream for session: {request.session_id}")
            
            # Send session info first
            yield {
                "event": "session",
                "data": json.dumps({
                    "session_id": request.session_id,
                    "user_id": request.user_id,
                    "agent_name": request.agent_name
                })
            }
            
            # Get agent instance from registry (singleton)
            agent = get_agent_instance(request.agent_name)
            logger.info(f"🤖 Got agent instance, starting chat_stream...")
            
            # Stream real events from the agent
            try:
                async for event in agent.chat_stream(request):
                    event_type = event.get("type", "message")
                    
                    # Log content events
                    if event_type == "content":
                        content_text = event.get("text", "") or event.get("content", "")
                        logger.debug(
                            f"📨 Yielding content event: type={event_type}, "
                            f"text_length={len(str(content_text))}"
                        )
                    else:
                        logger.debug(f"📨 Yielding event: {event_type}")
                    
                    # Track completion
                    if event_type == "done":
                        stream_completed = True
                    
                    # Format as SSE event
                    yield {
                        "event": event_type,
                        "data": json.dumps(event)
                    }
                
                stream_completed = True
                
            except (GeneratorExit, asyncio.CancelledError):
                logger.info("Client disconnected, stream cancelled for %s", request.agent_name)
                stream_completed = True
                return
            except Exception as stream_error:
                logger.exception("Error during agent chat_stream")
                yield {
                    "event": "error",
                    "data": json.dumps({
                        "type": "error",
                        "message": str(stream_error)
                    })
                }

        except KeyError as e:
            logger.error(f"Agent not found: {e}")
            yield {
                "event": "error",
                "data": json.dumps({
                    "type": "error",
                    "message": f"Agent not found: {str(e)}"
                })
            }
        except Exception as e:
            logger.exception("Streaming chat failed")
            yield {
                "event": "error",
                "data": json.dumps({
                    "type": "error",
                    "message": str(e)
                })
            }
        finally:
            # Always yield a done event to properly close the stream
            if not stream_completed:
                yield {
                    "event": "done",
                    "data": json.dumps({"type": "done"})
                }
    
    return EventSourceResponse(event_generator())

