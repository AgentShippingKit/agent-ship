"""Models for the agents."""
from pydantic import BaseModel, Field
from typing import List, Optional, Any

# Base input/output models
class TextInput(BaseModel):
    """Simple text input."""
    text: str

class TextOutput(BaseModel):
    """Simple text output."""
    response: str

class FeatureMap(BaseModel):
    """Feature map for the agent."""
    feature_name: str = Field(description="Feature name")
    feature_value: Any = Field(description="Feature value")

class AgentChatRequest(BaseModel):
    agent_name: str
    user_id: str = None
    session_id: str = None
    sender: str = Field(description="Sender", default="USER")
    query: Any = Field(description="Query")
    features: Optional[List[FeatureMap]] = Field(description="List of features")

class AgentChatResponse(BaseModel):
    agent_name: str
    user_id: str
    session_id: str
    sender: str = Field(description="Sender", default="SYSTEM")
    success: bool
    agent_response: Any