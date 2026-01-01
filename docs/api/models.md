# Models API Reference

## Base Models

### `AgentChatRequest`

Request model for agent chat interactions.

```python
class AgentChatRequest(BaseModel):
    agent_name: str
    user_id: str
    session_id: str
    query: Union[str, dict]
    features: List[str] = []
```

### `AgentChatResponse`

Response model for agent chat interactions.

```python
class AgentChatResponse(BaseModel):
    success: bool
    agent_name: str
    agent_response: BaseModel
    error: Optional[str] = None
```

### `TextInput`

Default input schema for text-based agents.

```python
class TextInput(BaseModel):
    text: str
```

### `TextOutput`

Default output schema for text-based agents.

```python
class TextOutput(BaseModel):
    text: str
```

### `FeatureMap`

Feature mapping for agent capabilities.

```python
class FeatureMap(BaseModel):
    feature_name: str
    enabled: bool
```

### `Artifact`

Artifact model for file and data handling.

```python
class Artifact(BaseModel):
    type: str
    content: str
    metadata: Optional[dict] = None
```
