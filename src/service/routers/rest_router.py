from fastapi import APIRouter
from src.service.routers.agent_conversation_router import router as agent_conversation_router

router = APIRouter(prefix="/api")

# Include routers in order of specificity (most specific first)
router.include_router(agent_conversation_router, prefix="/agents", tags=["agents"])

# Add other API endpoints here as needed
