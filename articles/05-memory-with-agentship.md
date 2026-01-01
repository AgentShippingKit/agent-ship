# Memory with AgentShip: Short-Term, Long-Term, RAG, and Mem0

## Why Memory Matters

Without memory, every conversation starts from zero. Users expect agents to remember context, learn from interactions, and recall relevant information.

Memory transforms an agent from a stateless function into an intelligent assistant.

---

## Types of Memory

```
┌─────────────────────────────────────────────────────────────────┐
│                        Agent Memory                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Short-Term     │  │   Long-Term     │  │   Semantic      │  │
│  │  (Sessions)     │  │   (Database)    │  │   (RAG/Mem0)    │  │
│  │                 │  │                 │  │                 │  │
│  │  Current        │  │  User profiles  │  │  Knowledge base │  │
│  │  conversation   │  │  Past sessions  │  │  Documents      │  │
│  │  Active context │  │  Preferences    │  │  Embeddings     │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│         ▲                     ▲                     ▲           │
│         │                     │                     │           │
│    In-Memory /          PostgreSQL            Vector Store      │
│    PostgreSQL                                 (OpenSearch)      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Short-Term Memory (Session Management)

### What It Is
Short-term memory persists within a single conversation session. It allows the agent to maintain context across multiple turns.

### How AgentShip Handles It

AgentShip uses Google ADK's session services with automatic management:

```python
# From src/agents/modules/session_service_factory.py

class SessionServiceFactory:
    @staticmethod
    def create_session_service(agent_name: str):
        session_store_uri = os.getenv('AGENT_SESSION_STORE_URI')
        
        if os.getenv('AGENT_SHORT_TERM_MEMORY') == 'Database':
            # Persistent sessions (PostgreSQL)
            return DatabaseSessionService(session_store_uri), True
        else:
            # Temporary sessions (In-memory)
            return InMemorySessionService(), False
```

### Configuration

```bash
# .env

# For in-memory sessions (development)
# Leave AGENT_SHORT_TERM_MEMORY unset

# For persistent sessions (production)
AGENT_SHORT_TERM_MEMORY=Database
AGENT_SESSION_STORE_URI=postgresql://user:pass@host:5432/db
```

### Session Flow

```
User Request 1                User Request 2
     │                              │
     ▼                              ▼
┌─────────────────────────────────────────────────┐
│                 Session Store                    │
│                                                  │
│  Session: user-123-session-1                    │
│  ┌────────────────────────────────────────────┐ │
│  │ Message 1: "What are my action items?"     │ │
│  │ Response 1: "You have 3 action items..."   │ │
│  │ Message 2: "Mark the first one complete"   │ │
│  │ Response 2: "Done! Marked as complete."    │ │
│  └────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### Usage in Agents

Sessions are managed automatically by `BaseAgent`:

```python
class SessionManager:
    async def ensure_session_exists(self, user_id: str, session_id: str):
        """Create session if it doesn't exist."""
        try:
            await self.session_service.create_session(
                app_name=self.agent_name,
                user_id=user_id,
                session_id=session_id
            )
        except Exception as e:
            if "duplicate key" in str(e).lower():
                pass  # Session already exists, that's fine
            else:
                raise
```

### API Usage

```bash
# First message in session
curl -X POST http://localhost:7001/api/agents/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "health_assistant_agent",
    "query": "What are my action items?",
    "session_id": "session-123",
    "user_id": "user-456"
  }'

# Second message in SAME session (context is maintained)
curl -X POST http://localhost:7001/api/agents/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "health_assistant_agent",
    "query": "Mark the first one as complete",
    "session_id": "session-123",
    "user_id": "user-456"
  }'
```

---

## Long-Term Memory (Database Storage)

### What It Is
Long-term memory persists across sessions. It stores:
- User profiles
- Historical interactions
- Preferences
- Past insights

### Implementation with Tools

AgentShip uses tools to access long-term memory:

```yaml
# In main_agent.yaml
tools:
  - type: function
    id: fetch_conversation_insights_tool
    import: src.agents.tools.conversation_insights_tool.ConversationInsightsTool
    method: run
```

```python
# conversation_insights_tool.py
class ConversationInsightsTool(BaseTool):
    """Fetch conversation insights from database."""
    
    def run(self, user_id: str, limit: int = 10) -> str:
        # Query historical data from PostgreSQL
        insights = db.query("""
            SELECT * FROM conversation_insights 
            WHERE user_id = %s 
            AND created_at > NOW() - INTERVAL '60 days'
            ORDER BY created_at DESC
            LIMIT %s
        """, (user_id, limit))
        
        return json.dumps(insights)
```

### Data Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User Query    │────▶│     Agent       │────▶│   Response      │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
          ┌─────────────────┐       ┌─────────────────┐
          │   Tool Call:    │       │   Tool Call:    │
          │  Fetch History  │       │  Store Result   │
          └────────┬────────┘       └────────┬────────┘
                   │                         │
                   ▼                         ▼
          ┌─────────────────────────────────────────┐
          │              PostgreSQL                  │
          │  ┌───────────────────────────────────┐  │
          │  │  conversations, insights,         │  │
          │  │  action_items, preferences        │  │
          │  └───────────────────────────────────┘  │
          └─────────────────────────────────────────┘
```

---

## RAG (Retrieval-Augmented Generation)

### What It Is
RAG retrieves relevant information from a knowledge base and injects it into the agent's context.

### Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   User Query    │────▶│    Embedder     │
│  "What is my    │     │   (OpenAI)      │
│   diagnosis?"   │     └────────┬────────┘
└─────────────────┘              │
                                 ▼
                    ┌─────────────────────────┐
                    │     Vector Search       │
                    │     (OpenSearch)        │
                    │                         │
                    │  Query embedding        │
                    │       ↓                 │
                    │  Find similar docs      │
                    │       ↓                 │
                    │  Return top K           │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     Retrieved Docs      │
                    │  - Medical report 1     │
                    │  - Previous diagnosis   │
                    │  - Lab results          │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       Agent             │
                    │  (Context = Query +     │
                    │   Retrieved Docs)       │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    Grounded Response    │
                    └─────────────────────────┘
```

### Implementation Pattern

```python
# rag_tool.py
class RAGTool(BaseTool):
    """Retrieval-Augmented Generation tool."""
    
    def __init__(self):
        self.embedder = OpenAIEmbeddings()
        self.vector_store = OpenSearchVectorStore(
            index="medical_documents"
        )
    
    def run(self, query: str, user_id: str, top_k: int = 5) -> str:
        # 1. Embed the query
        query_embedding = self.embedder.embed(query)
        
        # 2. Search vector store
        results = self.vector_store.search(
            embedding=query_embedding,
            filter={"user_id": user_id},
            top_k=top_k
        )
        
        # 3. Format retrieved documents
        context = "\n\n".join([
            f"Document: {r.metadata['title']}\n{r.content}"
            for r in results
        ])
        
        return context
```

### Integrating with AgentShip

```yaml
# main_agent.yaml
tools:
  - type: function
    id: search_medical_history
    import: src.agents.tools.rag_tool.RAGTool
    method: run

instruction_template: |
  You are a health assistant.
  
  When answering questions about user's medical history:
  1. Use search_medical_history tool to retrieve relevant documents
  2. Base your answer ONLY on retrieved documents
  3. If no relevant documents found, say so
  
  Never make up medical information.
```

---

## Mem0: Personal AI Memory

### What It Is
[Mem0](https://github.com/mem0ai/mem0) provides persistent, personalized memory for AI applications. It learns from interactions and maintains a user-specific knowledge graph.

### Key Features
- **Automatic extraction**: Learns facts from conversations
- **Personalization**: Remembers user preferences
- **Graph-based**: Relationships between entities
- **Cross-session**: Persists across all sessions

### Architecture with Mem0

```
┌─────────────────────────────────────────────────────────────────┐
│                        Mem0 Memory Layer                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐│
│  │   User Memory   │   │ Relation Memory │   │  Agent Memory   ││
│  │                 │   │                 │   │                 ││
│  │ - Preferences   │   │ - User→Doctor   │   │ - Learned       ││
│  │ - Facts         │   │ - User→Med      │   │   behaviors     ││
│  │ - History       │   │ - Symptoms      │   │ - Patterns      ││
│  └─────────────────┘   └─────────────────┘   └─────────────────┘│
│                                                                  │
│            ┌────────────────────────────────┐                   │
│            │         Knowledge Graph        │                   │
│            │                                │                   │
│            │  User ──takes── Medication     │                   │
│            │    │                    │      │                   │
│            │    └──has── Condition ──┘      │                   │
│            │            │                   │                   │
│            │      prescribed_by             │                   │
│            │            │                   │                   │
│            │         Doctor                 │                   │
│            └────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

### Integration Pattern

```python
# mem0_tool.py
from mem0 import Memory

class Mem0MemoryTool(BaseTool):
    """Mem0-based memory for personalized AI."""
    
    def __init__(self):
        self.memory = Memory()
    
    def add_memory(self, user_id: str, content: str) -> str:
        """Add a memory from conversation."""
        result = self.memory.add(
            content,
            user_id=user_id,
            metadata={"source": "conversation"}
        )
        return f"Memory added: {result}"
    
    def search_memory(self, user_id: str, query: str) -> str:
        """Search user's memories."""
        results = self.memory.search(
            query,
            user_id=user_id,
            limit=5
        )
        return json.dumps(results)
    
    def get_all_memories(self, user_id: str) -> str:
        """Get all memories for a user."""
        memories = self.memory.get_all(user_id=user_id)
        return json.dumps(memories)
```

### Usage in Agent

```yaml
# main_agent.yaml
tools:
  - type: function
    id: remember
    import: src.agents.tools.mem0_tool.Mem0MemoryTool
    method: add_memory
  
  - type: function
    id: recall
    import: src.agents.tools.mem0_tool.Mem0MemoryTool
    method: search_memory

instruction_template: |
  You are a personalized health assistant with memory.
  
  MEMORY USAGE:
  - Use 'recall' to remember user's preferences, history, facts
  - Use 'remember' to store important information for future
  
  Examples of what to remember:
  - User's health conditions
  - Medication preferences
  - Doctor appointments
  - Personal health goals
  
  Always check memory before asking for information you might already know.
```

---

## Memory Strategy Selection

| Memory Type | Persistence | Scope | Use Case |
|-------------|-------------|-------|----------|
| **Short-Term (In-Memory)** | Session only | Single conversation | Development, testing |
| **Short-Term (Database)** | Until cleared | Single conversation | Production |
| **Long-Term (PostgreSQL)** | Permanent | Cross-session | User history, preferences |
| **RAG (Vector Store)** | Permanent | Knowledge base | Documents, reports |
| **Mem0** | Permanent | Personalized | Learned facts, relationships |

### Decision Tree

```
What do you need to remember?

├── Current conversation only
│   └── Short-Term Memory (Session)
│
├── User's historical data
│   └── Long-Term Memory (Database + Tools)
│
├── Large document collections
│   └── RAG (Vector Store)
│
└── Personal facts and preferences
    └── Mem0 (Personal Memory)
```

---

## Best Practices

### 1. Layer Your Memory
Use multiple memory types together:
- Short-term for conversation
- Long-term for history
- RAG for documents
- Mem0 for personalization

### 2. Clear Memory Boundaries
Define what goes where:
```
Short-term: Current conversation context
Long-term: Explicit user data (health records, action items)
RAG: Reference documents
Mem0: Inferred preferences and facts
```

### 3. Memory Hygiene
- Regularly clean old sessions
- Index vector stores efficiently
- Prune outdated Mem0 memories

### 4. Privacy Considerations
- Encrypt sensitive data
- Implement data retention policies
- Allow users to delete their memories

---

## Summary

AgentShip supports multiple memory strategies:

1. **Short-Term**: Session management (in-memory or PostgreSQL)
2. **Long-Term**: Database tools for historical data
3. **RAG**: Vector search for document retrieval
4. **Mem0**: Personal AI memory for learned facts

Choose based on your use case. Most production applications use a combination.

---

*Next: Observability with AgentShip*

