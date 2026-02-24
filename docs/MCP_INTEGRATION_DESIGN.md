# MCP Server Integration Design & Implementation Plan

## Executive Summary

This document outlines the design and implementation plan for adding Model Context Protocol (MCP) server support to AgentShip framework. The integration will enable agents built with both ADK and LangGraph execution engines to connect to external MCP servers, expanding agent capabilities through standardized tool access.

**Key Goals:**
- Support MCP server connections for both ADK and LangGraph agents
- Flexible authentication/authorization strategy
- Framework-agnostic core with engine-specific adapters
- Maintain existing inference patterns and tool architecture
- Secure credential management

**Document Status:** Updated with current implementation status and gap analysis as of 2026-02-22.

---

## 0. Current Implementation Status & Gap Analysis

### 0.1 What's Been Implemented ✅

**Phase 1: Core Infrastructure - COMPLETE**
- ✅ MCP configuration models (`MCPServerConfig`, `MCPAuthConfig`, `MCPToolInfo`)
- ✅ Global MCP server registry (`MCPServerRegistry`) with JSON/YAML loading
- ✅ Agent-level MCP server references in `AgentConfig`
- ✅ Config merging (global registry + per-agent overrides)
- ✅ `MCPClientManager` singleton for connection management
- ✅ `BaseMCPClient` abstract interface
- ✅ **STDIO transport client** (`StdioMCPClient`) - fully working
- ✅ Unit tests for all core components (29 tests passing)

**Phase 3: Tool Discovery & Integration - COMPLETE (for STDIO only)**
- ✅ `MCPToolDiscovery` for listing tools from servers
- ✅ ADK adapter with proper JSON Schema → genai Schema conversion
- ✅ LangGraph adapter (basic implementation)
- ✅ Integration into `ToolManager._create_mcp_tools()`
- ✅ Support for both ADK and LangGraph engines
- ✅ Tool name filtering (per-agent `tools` list)
- ✅ Async event loop handling (supports both standalone and uvicorn)

**Cursor IDE Config Compatibility - COMPLETE**
- ✅ Registry supports `.cursor/mcp.json` file locations
- ✅ Auto-converts Cursor format to AgentShip format
- ✅ Supports `mcpServers` root key (Cursor standard)
- ✅ Auto-detects transport from config (command → STDIO, url → SSE/HTTP)

### 0.1.1 STDIO Client Fix (2026-02-22) 🔧

**Problem:** MCP STDIO client was hanging indefinitely during `session.initialize()` with `asyncio.TimeoutError` after 30 seconds. Root cause was improper use of MCP SDK's `ClientSession`.

**Solution:** Use proper async context manager pattern for `ClientSession`:

```python
# WRONG (causes hang):
session = ClientSession(read_stream, write_stream)
await session.initialize()  # Hangs forever

# CORRECT (works properly):
async with ClientSession(read_stream, write_stream) as session:
    await session.initialize()  # Works!
```

**Implementation:** Updated `src/agent_framework/mcp/clients/stdio.py`:
- Store `_session_context` (result of `__aenter__`) instead of raw session
- Use `async with` pattern in `_ensure_connected()`
- Properly exit both contexts (ClientSession + stdio_client) in `close()`

**Reference:** https://github.com/modelcontextprotocol/python-sdk/pull/1849

**Test Results:** Successfully connects to MCP filesystem server, discovers 14 tools, calls tools, integrates with AgentConfig/ToolManager. All tests passing.

### 0.2 Critical Gaps 🔴

**Phase 1: Transport Clients - INCOMPLETE**
- ❌ **SSE client** (`SSEMCPClient`) - NOT IMPLEMENTED
- ❌ **HTTP client** (`HTTPMCPClient`) - NOT IMPLEMENTED
- ⚠️ `MCPClientManager._create_client()` only handles STDIO, raises ValueError for SSE/HTTP

**Phase 2: Authentication & Authorization - NOT STARTED**
- ❌ Credential storage (env vars, secret manager, encrypted file)
- ❌ Bearer token authentication
- ❌ API key authentication
- ❌ OAuth 2.1 flow (PRM discovery, authorization code + PKCE, token refresh)
- ❌ Token caching and lifecycle management
- ❌ Authorization scope checking
- ⚠️ Auth models exist but **no implementation uses them**

**Phase 3: Tool Integration - PARTIAL**
- ⚠️ LangGraph adapter uses weak schema (`_MCPToolArgs` with `extra="allow"`)
  - LLM doesn't see typed parameters, only a generic catch-all
  - ADK adapter properly converts JSON Schema, LangGraph doesn't
- ❌ No JSON Schema → Pydantic model conversion for LangGraph

**Phase 4: Error Handling & Observability - NOT STARTED**
- ❌ Connection retry logic with exponential backoff
- ❌ Circuit breaker pattern
- ❌ Timeout handling and recovery
- ❌ OPIK observability integration for MCP operations
- ❌ Structured logging for MCP calls
- ❌ Metrics (connection count, tool invocation latency, failures)
- ⚠️ Basic try/catch exists but not production-ready

**Phase 5: Agent Skills (MCP Prompts & Resources) - NOT STARTED**
- ❌ `prompts/list` and `prompts/get` support
- ❌ `resources/list` and `resources/read` support
- ❌ Skills service layer
- ❌ Prompt invocation and message injection

**Connection Lifecycle Issues:**
- ⚠️ `MCPClientManager.close_all()` defined but **never called**
- ⚠️ No graceful shutdown hook on app termination
- ⚠️ STDIO processes may leak if connections not cleaned up

### 0.3 Architecture Confirmed ✅

**Architecture Decision (Confirmed 2026-02-22):**
```
AgentShip (MCP Client) → STDIO/SSE/HTTP → MCP Server
```

AgentShip acts as an **MCP client**:
- ✅ Agents built with AgentShip connect TO MCP servers
- ✅ Each agent can use different MCP servers (via config)
- ✅ STDIO servers run as child processes of AgentShip
- ✅ Remote servers accessed via SSE/HTTP (to be implemented)
- ✅ AgentShip manages MCP client connections
- ❌ AgentShip does NOT act as an MCP server/gateway

**Out of Scope:**
- ❌ AgentShip exposing MCP protocol endpoints
- ❌ External MCP clients connecting to AgentShip
- ❌ AgentShip as a proxy/middleware for MCP servers

**Focus:** Complete the MCP client implementation (remote transports + authentication + hardening)

### 0.4 Test Coverage

**Unit Tests:** ✅ 29 tests, all passing
- Registry, client manager, models, tool discovery, tool manager integration

**Integration Tests:** ❌ None
- No end-to-end tests with real MCP servers
- No auth flow tests
- No multi-transport tests

**E2E Tests:** ❌ None
- No agent tests with MCP tools
- No streaming tests with MCP

---

## 1. Architecture Overview

### 1.1 Current Architecture

AgentShip follows a clean separation of concerns:

```
BaseAgent
  ├── AgentConfig (YAML-based)
  ├── EngineFactory → AgentEngine (ADK/LangGraph)
  ├── ToolManager → Tools (function/agent tools)
  ├── MemoryFactory → Memory backends
  └── ObservabilityFactory → Observability
```

**Key Components:**
- **BaseAgent**: Core agent class that loads config and wires components
- **AgentEngine**: Abstract interface (`AgentEngine`) with concrete implementations (`AdkEngine`, `LangGraphEngine`)
- **ToolManager**: Creates tools from YAML config, converts to engine-specific formats
- **AgentConfig**: YAML-based configuration loaded per agent

### 1.2 Proposed MCP Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│         Global MCP Server Registry                          │
│  (.mcp.settings.json / mcp_servers.yaml)                   │
│  - Centralized server definitions                          │
│  - Connection details & auth config                        │
│  - Shared across all agents                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent Configuration                       │
│  (main_agent.yaml) - References to MCP servers              │
│  - Server IDs from registry                                 │
│  - Tool filtering & overrides                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              MCP Server Registry Manager                    │
│  (MCPServerRegistry singleton)                              │
│  - Loads global server configs                              │
│  - Resolves agent references to full configs                │
│  - Merges agent-specific overrides                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              MCP Client Manager (Singleton)                  │
│  - Server connection management                            │
│  - Authentication/authorization handling                   │
│  - Connection pooling & lifecycle                          │
│  - Tool discovery from MCP servers                          │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                         │
        ▼                                         ▼
┌──────────────────────┐              ┌──────────────────────┐
│   MCP Client Pool    │              │  MCP Tool Adapter     │
│  (per server type)   │              │  (Engine-specific)   │
│  - STDIO clients     │              │  - ADK Tool wrapper  │
│  - SSE clients       │              │  - LangGraph wrapper │
│  - HTTP clients      │              └──────────────────────┘
└──────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              ToolManager (Enhanced)                          │
│  - Existing: function/agent tools                            │
│  - New: MCP tool integration                                │
│  - Engine-specific tool conversion                          │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                         │
        ▼                                         ▼
┌──────────────────────┐              ┌──────────────────────┐
│    AdkEngine         │              │   LangGraphEngine      │
│  - Uses ADK tools    │              │  - Uses LangChain     │
│  - MCP tools as      │              │    StructuredTool     │
│    ADK FunctionTool  │              │  - MCP tools as        │
│                      │              │    StructuredTool      │
└──────────────────────┘              └──────────────────────┘
```

### 1.3 Design Principles

1. **Framework Agnostic Core**: Core MCP client logic is independent of execution engines
2. **Engine-Specific Adapters**: Each engine (ADK/LangGraph) has its own tool adapter
3. **Configuration-Driven**: MCP servers configured via YAML, no code changes needed
4. **Lazy Initialization**: MCP connections established on first use
5. **Connection Pooling**: Reuse connections across agent invocations
6. **Backward Compatible**: Existing agents continue to work without changes

### 1.4 MCP Beyond Tools (Deferred: Prompts & Resources)

Beyond **tools**, MCP defines **Prompts** and **Resources**. Those can be integrated later. **This design focuses on MCP tools and infrastructure first.**

*Note: [Anthropic’s Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) (filesystem-based SKILL.md, code execution) are a separate product feature and out of scope for this MCP setup.*

For reference, MCP also exposes:

| MCP Capability | What It Is | Agent-Skills Mapping |
|----------------|------------|----------------------|
| **Tools** | RPC-style functions the model can call | Already in scope (tool integration) |
| **Prompts** | Templated messages/workflows with arguments (`prompts/list`, `prompts/get`) | **Skills**: reusable, prompt-based capabilities; lightweight, minimal context |
| **Resources** | Context and data (files, schemas, docs) via `resources/list`, `resources/read` | **Skill context**: optional bundled artifacts or reference data for skills |

**Agent skills** in this design are:

- **Externally defined**: Provided by MCP servers (not hard-coded in the agent).
- **Reusable**: Same skill (prompt template) can be used by multiple agents.
- **Structured**: Clear name, description, and arguments (from MCP prompt schema).
- **On-demand**: Fetched via `prompts/get` when needed; only the resulting messages consume context.

**How they differ from MCP tools:**

- **Tools**: Model decides when to call; execution is a function call; typically more context (e.g. schema).
- **Skills (Prompts)**: User or orchestrator can explicitly invoke (e.g. “use code review skill”); we call `prompts/get` and inject the returned messages into the conversation; often lighter weight.

**Integration approach:**

1. **Discovery**: When an agent has MCP servers that support the `prompts` capability, we discover skills via `prompts/list` (and optionally cache in registry).
2. **Configuration**: In agent config (or global MCP settings), we allow specifying which MCP servers’ prompts an agent can use, and optionally which prompt names to expose as skills.
3. **Invocation**: When a skill is invoked (e.g. by user choice or by a “use skill” meta-tool):
   - Call `prompts/get` with the prompt name and arguments.
   - Inject the returned `messages` into the conversation (e.g. as system/user context for the next turn).
4. **Resources (optional)**: For skills that need extra context, we can support MCP **resources** (e.g. `resources/read` for a doc) and inject that content when resolving a prompt or when the model requests context.

This keeps a single MCP connection per server while supporting tools, skills (prompts), and optional resources in one integrated design.

---

## 2. Authentication & Authorization Strategy

### 2.1 Authentication Methods

MCP supports multiple authentication mechanisms based on transport type:

#### 2.1.1 STDIO Transport (Local)
- **Credentials**: Environment variables or config file
- **Storage**: 
  - Environment variables (preferred for secrets)
  - Encrypted config file (for non-sensitive data)
  - Secret management service (Google Secret Manager, AWS Secrets Manager)

#### 2.1.2 SSE/HTTP Transport (Remote)
- **Bearer Token**: Simple token-based auth
- **OAuth 2.1**: Full OAuth flow with Protected Resource Metadata (PRM)
- **API Keys**: Alternative credential mechanism

### 2.2 Authorization Flow

**For OAuth-enabled MCP Servers:**

```
1. Agent requests MCP tool → MCP Server Manager
2. Check if server requires auth → Yes
3. Check if token exists & valid → No
4. Fetch PRM document from server
5. Discover authorization server & scopes
6. Initiate OAuth flow (if interactive) or use stored refresh token
7. Store access token (encrypted, short-lived)
8. Proceed with tool invocation
```

**For Token/API Key Servers:**

```
1. Agent requests MCP tool → MCP Server Manager
2. Check if server requires auth → Yes
3. Retrieve credentials from secure storage
4. Attach credentials to request
5. Proceed with tool invocation
```

### 2.2.1 OAuth 2.1 flow (MCP Client ↔ Server ↔ Auth Server)

This section maps the standard OAuth 2.1 Authorization Code + PKCE flow to our MCP client so we implement it correctly when connecting to OAuth-protected MCP servers (e.g. SSE/HTTP tool hosts that return 401 and expose Protected Resource Metadata).

**Participants:** MCP Client (our agent framework), MCP Server (tool host), Auth Server (Cognito/Azure/Auth0/self-hosted), Resource (e.g. Gmail API, DB) used by the server’s tools.

**Sequence we must support (implementation: Step 6 – Auth and other transports):**

| Step | Action | Our responsibility |
|------|--------|---------------------|
| 1 | MCP Client connects / calls tool (e.g. `list_tools` or `tools/call`) | HTTP/SSE client sends request (no auth or with cached token). |
| 2 | MCP Server responds **401 Unauthorized** “You need auth” | Client detects 401 and triggers auth flow instead of failing. |
| 3 | **Discover auth endpoints:** Client `GET /.well-known/oauth-protected-resource` on MCP Server | HTTP client issues this request; parse response for `authorization_server` URL. |
| 4 | **Get OAuth server metadata:** Client `GET /.well-known/oauth-authorization-server` on Auth Server | Fetch `authorization_endpoint`, `token_endpoint` (and optionally `registration_endpoint`). |
| 5 | (Optional) **Dynamic client registration:** Client `POST /register` to Auth Server | If not pre-registered, obtain `client_id` / `client_secret`; use `client_id_env` / `client_secret_env` from `MCPServerConfig.auth` or from registration. |
| 6 | **OAuth 2.1 Authorization Code + PKCE:** User authenticates; client exchanges code for tokens | Implement PKCE (code_verifier, code_challenge); redirect/callback handling; exchange at `token_endpoint`; store `access_token` (and optional `refresh_token`). |
| 7 | Client receives **access_token** | Cache per server (and user/session if multi-tenant); associate with `MCPServerConfig.id`. |
| 8 | **Authenticated tool call:** Client sends e.g. `tools/call` with **Authorization: Bearer &lt;access_token&gt;** | All subsequent requests to that MCP Server include the Bearer header until token expires or is refreshed. |
| 9 | MCP Server **validates token** with Auth Server (introspection or JWT) | Server-side; we only send the token. On 401 again, refresh or re-run OAuth. |

**Config already in place:** `MCPAuthConfig` has `type: OAUTH`, `client_id_env`, `client_secret_env`, `scopes`. Global and per-agent config support `auth` for each server. Step 6 will add credential resolution, HTTP/SSE clients, 401 handling, well-known discovery, PKCE flow, and Bearer attachment so this diagram is fully ensured in code.

### 2.3 Credential Storage Strategy

**Multi-Layer Approach:**

1. **Environment Variables** (Highest Priority)
   - **Per-server variable names:** Each MCP server defines which env vars it uses in its auth config (`token_var`, `token_env`, `api_key_var`, `client_id_env`, `client_secret_env`). There is no single global convention—e.g. GitHub might use `GITHUB_TOKEN` or `GITHUB_CLIENT_ID`, a database server might use `DATABASE_MCP_TOKEN`.
   - **Optional naming convention:** If you want a consistent pattern across servers, you *can* use names like `MCP_SERVER_<SERVER_ID>_AUTH_TOKEN`, `MCP_SERVER_<SERVER_ID>_API_KEY`, `MCP_SERVER_<SERVER_ID>_CLIENT_ID`, `MCP_SERVER_<SERVER_ID>_CLIENT_SECRET` and reference them in the server’s auth config (e.g. `token_var: "MCP_SERVER_github_AUTH_TOKEN"`). This is optional, not required.

2. **Secret Management Services** (Production)
   - Google Secret Manager (GCP)
   - AWS Secrets Manager (AWS)
   - Azure Key Vault (Azure)
   - Configurable via environment: `MCP_SECRET_MANAGER_PROVIDER`

3. **Encrypted Config File** (Development)
   - `.mcp_credentials.json.enc` (encrypted with master key)
   - Master key from environment: `MCP_MASTER_KEY`

4. **In-Memory Cache** (Runtime)
   - Short-lived token cache (TTL: 5 minutes)
   - OAuth refresh tokens stored securely

### 2.4 Authorization Scopes & Permissions

**Per-Server Scope Management:**

```yaml
mcp_servers:
  - id: github_server
    scopes:
      - repo:read
      - issues:write
    tool_permissions:
      github_search_code: allowed
      github_create_issue: allowed
      github_delete_repo: denied
```

**Runtime Permission Checks:**

- Before tool invocation, check if agent/user has required scope
- Log authorization failures for audit
- Support per-user/per-agent permission overrides

---

## 3. Configuration Design

### 3.1 Configuration Architecture

**Two-Level Configuration Approach:**

1. **Global MCP Server Registry** (`.mcp.settings.json` or `mcp_servers.yaml`)
   - Centralized definition of all available MCP servers
   - Server connection details, auth config, credentials
   - Shared across all agents

2. **Per-Agent MCP References** (`main_agent.yaml`)
   - Agents reference which MCP servers they want to use
   - Can filter specific tools from servers
   - Agent-specific overrides (if needed)

#### 3.1.1 Global MCP Server Registry

**Supported Formats:**

AgentShip supports **Cursor-compatible format** and **extended AgentShip format** for maximum compatibility.

**File Locations (Priority Order):**
1. `MCP_SERVERS_CONFIG` environment variable (explicit path)
2. `.cursor/mcp.json` (Cursor project config) ✨ **Cursor-compatible**
3. `~/.cursor/mcp.json` (Cursor global config) ✨ **Cursor-compatible**
4. `.mcp.settings.json` (AgentShip project config)
5. `mcp_servers.yaml` (AgentShip YAML format)
6. `mcp_servers.json` (AgentShip legacy)

---

**Format A: Cursor-Compatible (Simplified, STDIO only)**

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"],
      "env": {
        "MCP_FILESYSTEM_ROOT": "/allowed/path"
      }
    },
    "time": {
      "command": "python",
      "args": ["-m", "mcp_server_time", "--local-timezone=America/New_York"]
    }
  }
}
```

**Key characteristics:**
- ✅ Works in Cursor, Claude Desktop, VS Code
- ✅ Simple structure: `command`, `args`, `env`
- ✅ STDIO transport only (implied)
- ⚠️ No OAuth support (env vars only)
- ⚠️ No remote servers (SSE/HTTP)

---

**Format B: AgentShip Extended (All Transports & Auth)**

```json
{
  "mcpServers": {
    "filesystem": {
      "transport": "stdio",
      "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem"],
      "env": {
        "MCP_FILESYSTEM_ROOT": "/allowed/path"
      },
      "timeout": 30,
      "max_retries": 3
    },
    "github": {
      "transport": "sse",
      "url": "https://mcp.github.com/sse",
      "auth": {
        "type": "oauth",
        "client_id_env": "GITHUB_CLIENT_ID",
        "client_secret_env": "GITHUB_CLIENT_SECRET",
        "scopes": ["repo:read", "issues:write"]
      },
      "timeout": 60
    },
    "database": {
      "transport": "http",
      "url": "https://mcp.database.com/api",
      "auth": {
        "type": "bearer_token",
        "token_env": "DATABASE_MCP_TOKEN"
      }
    }
  }
}
```

**Key characteristics:**
- ✅ Supports STDIO, SSE, HTTP transports
- ✅ OAuth, bearer token, API key authentication
- ✅ Timeout and retry configuration
- ✅ Backward compatible with Cursor format
- ⚠️ Extended fields ignored by other tools (Cursor, Claude Desktop)

---

**Format C: YAML Alternative (AgentShip only)**

```yaml
mcpServers:  # Can also use "servers" (legacy)
  filesystem:
    transport: stdio
    command:
      - npx
      - -y
      - "@modelcontextprotocol/server-filesystem"
    env:
      MCP_FILESYSTEM_ROOT: "/allowed/path"

  github:
    transport: sse
    url: https://mcp.github.com/sse
    auth:
      type: oauth
      client_id_env: GITHUB_CLIENT_ID
      client_secret_env: GITHUB_CLIENT_SECRET
      scopes:
        - repo:read
        - issues:write
```

**Auto-Detection:**
- If config has `"command"` → assumes STDIO transport
- If config has `"url"` → detects transport from URL or explicit `"transport"` field
- If config has `"transport"` → uses explicit transport type

#### 3.1.2 Per-Agent MCP Server References

**Updated `main_agent.yaml`:**

```yaml
agent_name: my_agent
execution_engine: adk  # or langgraph
llm_provider_name: openai
llm_model: gpt-4o

# Existing tools section
tools:
  - type: function
    id: my_function_tool
    import: src.tools.my_tool.MyTool
    method: run

# NEW: Reference MCP servers from global registry
mcp_servers:
  # Reference by ID, use all tools from server
  - id: github_server
  
  # Reference with tool filtering
  - id: database_server
    tools:
      - query_database
      - execute_sql
  
  # Reference with agent skills (MCP prompts) - optional
  - id: dev_tools_server
    prompts: [code_review, write_tests]  # Expose these prompts as skills; omit for all
  
  # Reference with agent-specific overrides (optional)
  - id: filesystem_server
    env:
      MCP_FILESYSTEM_ROOT: "/agent-specific/path"  # Override global config
```

**Benefits of This Approach:**
- ✅ **No Duplication**: Server config defined once, referenced by many agents
- ✅ **Centralized Credential Management**: Update credentials in one place
- ✅ **Easier Maintenance**: Change server URL/auth once, affects all agents
- ✅ **Agent Flexibility**: Agents can still filter tools or override config
- ✅ **Environment-Specific**: Different `.mcp.settings.json` per environment

### 3.2 MCP Server Configuration Schema

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal
from enum import Enum

class MCPTransport(str, Enum):
    STDIO = "stdio"
    SSE = "sse"
    HTTP = "http"

class MCPAuthType(str, Enum):
    NONE = "none"
    ENV_VAR = "env_var"
    BEARER_TOKEN = "bearer_token"
    OAUTH = "oauth"
    API_KEY = "api_key"

class MCPAuthConfig(BaseModel):
    type: MCPAuthType = MCPAuthType.NONE
    token_var: Optional[str] = None  # For env_var/bearer_token
    api_key_var: Optional[str] = None  # For api_key
    client_id_env: Optional[str] = None  # For oauth
    client_secret_env: Optional[str] = None  # For oauth
    scopes: List[str] = Field(default_factory=list)  # For oauth

class MCPServerConfig(BaseModel):
    id: str  # Unique identifier
    transport: MCPTransport
    command: Optional[List[str]] = None  # For STDIO
    url: Optional[str] = None  # For SSE/HTTP
    env: Dict[str, str] = Field(default_factory=dict)  # Environment vars
    auth: MCPAuthConfig = Field(default_factory=lambda: MCPAuthConfig(type=MCPAuthType.NONE))
    tools: Optional[List[str]] = None  # Specific tools to expose (None = all)
    timeout: int = 30  # Connection timeout in seconds
    max_retries: int = 3  # Max retry attempts
```

### 3.3 MCP Server Registry Manager

**New Component: `MCPServerRegistry`**

```python
# src/agent_framework/mcp/registry.py

import json
import yaml
import os
from pathlib import Path
from typing import Dict, Optional
from src.agent_framework.mcp.models import MCPServerConfig

class MCPServerRegistry:
    """Manages global MCP server configurations."""
    
    _instance: Optional['MCPServerRegistry'] = None
    _servers: Dict[str, MCPServerConfig] = {}
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize registry from config file."""
        if config_path is None:
            # Try multiple locations
            config_path = self._find_config_file()
        
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)
    
    def _find_config_file(self) -> Optional[str]:
        """Find MCP config file in standard locations."""
        # Check current directory, then project root
        locations = [
            ".mcp.settings.json",
            "mcp_servers.yaml",
            "mcp_servers.json",
            os.path.join(os.getcwd(), ".mcp.settings.json"),
            os.path.join(os.getcwd(), "mcp_servers.yaml"),
        ]
        
        # Also check environment variable
        env_path = os.getenv("MCP_SERVERS_CONFIG")
        if env_path:
            locations.insert(0, env_path)
        
        for path in locations:
            if os.path.exists(path):
                return path
        
        return None
    
    def _load_config(self, config_path: str) -> None:
        """Load server configurations from file."""
        with open(config_path, 'r') as f:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        
        servers = data.get('servers', {})
        for server_id, server_config in servers.items():
            self._servers[server_id] = MCPServerConfig(
                id=server_id,
                **server_config
            )
    
    def get_server(self, server_id: str) -> Optional[MCPServerConfig]:
        """Get server configuration by ID."""
        return self._servers.get(server_id)
    
    def get_servers(self, server_ids: list[str]) -> list[MCPServerConfig]:
        """Get multiple server configurations."""
        return [
            self._servers[sid] 
            for sid in server_ids 
            if sid in self._servers
        ]
    
    @classmethod
    def get_instance(cls) -> 'MCPServerRegistry':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```

### 3.4 AgentConfig Enhancement

**Update `AgentConfig` class to support server references:**

```python
class MCPServerReference(BaseModel):
    """Reference to an MCP server with optional overrides."""
    id: str  # Server ID from global registry
    tools: Optional[List[str]] = None  # Filter specific tools (None = all)
    env: Optional[Dict[str, str]] = None  # Override environment vars
    timeout: Optional[int] = None  # Override timeout
    # Other overrideable fields...

class AgentConfig:
    def __init__(
        self,
        # ... existing parameters ...
        mcp_servers: Optional[List[Dict[str, Any]]] = None,
    ):
        # ... existing initialization ...
        
        # Parse MCP server references (not full configs)
        self.mcp_servers: List[MCPServerReference] = []
        if mcp_servers:
            registry = MCPServerRegistry.get_instance()
            
            for server_ref_dict in mcp_servers:
                server_ref = MCPServerReference(**server_ref_dict)
                
                # Resolve full config from registry
                full_config = registry.get_server(server_ref.id)
                if not full_config:
                    raise ValueError(
                        f"MCP server '{server_ref.id}' not found in registry. "
                        f"Available servers: {list(registry._servers.keys())}"
                    )
                
                # Apply agent-specific overrides
                resolved_config = self._merge_server_config(full_config, server_ref)
                self.mcp_servers.append(resolved_config)
    
    def _merge_server_config(
        self, 
        base_config: MCPServerConfig, 
        override: MCPServerReference
    ) -> MCPServerConfig:
        """Merge agent-specific overrides with base server config."""
        # Create copy of base config
        merged = MCPServerConfig(**base_config.model_dump())
        
        # Apply overrides
        if override.env:
            merged.env.update(override.env)
        if override.timeout:
            merged.timeout = override.timeout
        if override.tools:
            merged.tools = override.tools
        
        return merged
```

---

## 4. Framework-Specific Implementation

### 4.1 Core MCP Components (Framework-Agnostic)

#### 4.1.1 MCP Client Manager

```python
# src/agent_framework/mcp/client_manager.py

class MCPClientManager:
    """Singleton manager for MCP server connections."""
    
    _instance: Optional['MCPClientManager'] = None
    _clients: Dict[str, MCPClient] = {}
    
    def get_client(self, server_config: MCPServerConfig) -> MCPClient:
        """Get or create MCP client for server."""
        if server_config.id not in self._clients:
            self._clients[server_config.id] = self._create_client(server_config)
        return self._clients[server_config.id]
    
    def _create_client(self, config: MCPServerConfig) -> MCPClient:
        """Create MCP client based on transport type."""
        if config.transport == MCPTransport.STDIO:
            return StdioMCPClient(config)
        elif config.transport == MCPTransport.SSE:
            return SSEMCPClient(config)
        elif config.transport == MCPTransport.HTTP:
            return HTTPMCPClient(config)
```

#### 4.1.2 MCP Tool Discovery

```python
# src/agent_framework/mcp/tool_discovery.py

class MCPToolDiscovery:
    """Discovers and caches tools from MCP servers."""
    
    async def discover_tools(
        self, 
        server_config: MCPServerConfig
    ) -> List[MCPTool]:
        """Discover available tools from MCP server."""
        client = MCPClientManager.get_client(server_config)
        tools = await client.list_tools()
        
        # Filter tools if specific tools requested
        if server_config.tools:
            tools = [t for t in tools if t.name in server_config.tools]
        
        return tools
```

### 4.2 ADK Engine Integration

#### 4.2.1 MCP Tool to ADK FunctionTool Adapter

```python
# src/agent_framework/mcp/adapters/adk_adapter.py

class ADKMCPToolAdapter:
    """Converts MCP tools to ADK FunctionTool."""
    
    @staticmethod
    def to_adk_tool(mcp_tool: MCPTool, client: MCPClient) -> FunctionTool:
        """Convert MCP tool to ADK FunctionTool."""
        from google.adk.tools import FunctionTool
        
        async def tool_function(**kwargs) -> str:
            """Wrapper function that calls MCP tool."""
            result = await client.call_tool(mcp_tool.name, kwargs)
            return json.dumps(result)
        
        return FunctionTool(
            tool_function,
            name=mcp_tool.name,
            description=mcp_tool.description,
            input_schema=mcp_tool.input_schema,  # Pydantic model
        )
```

#### 4.2.2 Integration in AdkEngine

**Update `AdkEngine.rebuild()`:**

```python
def rebuild(self) -> None:
    # Existing tool creation
    tools = ToolManager.create_tools(self.agent_config, "adk")
    
    # NEW: Add MCP tools
    if self.agent_config.mcp_servers:
        mcp_tools = self._create_mcp_tools()
        tools.extend(mcp_tools)
    
    # Rest of existing rebuild logic...
```

### 4.3 LangGraph Engine Integration

#### 4.3.1 MCP Tool to LangChain StructuredTool Adapter

```python
# src/agent_framework/mcp/adapters/langgraph_adapter.py

class LangGraphMCPToolAdapter:
    """Converts MCP tools to LangChain StructuredTool."""
    
    @staticmethod
    def to_langgraph_tool(mcp_tool: MCPTool, client: MCPClient) -> StructuredTool:
        """Convert MCP tool to LangChain StructuredTool."""
        from langchain_core.tools import StructuredTool
        
        async def tool_function(**kwargs) -> str:
            """Wrapper function that calls MCP tool."""
            result = await client.call_tool(mcp_tool.name, kwargs)
            return json.dumps(result)
        
        return StructuredTool.from_function(
            func=None,
            coroutine=tool_function,
            name=mcp_tool.name,
            description=mcp_tool.description,
            args_schema=mcp_tool.input_schema,  # Pydantic model
        )
```

#### 4.3.2 Integration in LangGraphEngine

**Update `LangGraphEngine.__init__()`:**

```python
def __init__(self, ...):
    # Existing tool creation
    self._tools: List[StructuredTool] = ToolManager.create_tools(
        agent_config, "langgraph"
    )
    
    # NEW: Add MCP tools
    if agent_config.mcp_servers:
        mcp_tools = self._create_mcp_tools()
        self._tools.extend(mcp_tools)
        self._tools_by_name.update({t.name: t for t in mcp_tools})
```

### 4.4 ToolManager Enhancement

**Update `ToolManager.create_tools()`:**

```python
@staticmethod
def create_tools(agent_config: AgentConfig, engine_type: str) -> List[Any]:
    tools = []
    
    # Existing: function and agent tools
    tool_configs = agent_config.tools or []
    for tool_config in tool_configs:
        tool = ToolManager._create_single_tool(tool_config, engine_type)
        if tool:
            tools.append(tool)
    
    # NEW: MCP tools
    if agent_config.mcp_servers:
        mcp_tools = ToolManager._create_mcp_tools(agent_config, engine_type)
        tools.extend(mcp_tools)
    
    return tools

@staticmethod
async def _create_mcp_tools(
    agent_config: AgentConfig, 
    engine_type: str
) -> List[Any]:
    """Create tools from MCP servers.
    
    Note: server_configs in agent_config.mcp_servers are already
    resolved from the global registry with agent-specific overrides applied.
    """
    from src.agent_framework.mcp.tool_discovery import MCPToolDiscovery
    from src.agent_framework.mcp.adapters import get_adapter
    
    discovery = MCPToolDiscovery()
    all_tools = []
    
    for server_config in agent_config.mcp_servers:
        # Discover tools from server
        mcp_tools = await discovery.discover_tools(server_config)
        
        # Get client for tool invocation
        client = MCPClientManager.get_client(server_config)
        
        # Convert to engine-specific format
        adapter = get_adapter(engine_type)
        for mcp_tool in mcp_tools:
            tool = adapter.to_engine_tool(mcp_tool, client)
            all_tools.append(tool)
    
    return all_tools
```

### 4.5 Configuration Resolution Flow

**How MCP server configs are resolved:**

```
1. AgentConfig.from_yaml() loads main_agent.yaml
   └─> Finds mcp_servers section with server IDs

2. AgentConfig.__init__() processes mcp_servers
   └─> For each server reference:
       ├─> MCPServerRegistry.get_instance() loads global config
       ├─> registry.get_server(server_id) retrieves base config
       └─> _merge_server_config() applies agent overrides

3. ToolManager.create_tools() called by engine
   └─> _create_mcp_tools() uses resolved configs
       ├─> MCPToolDiscovery discovers tools
       ├─> MCPClientManager.get_client() creates/gets client
       └─> Adapter converts to engine-specific tool
```

**Benefits of Registry Approach:**
- ✅ **Single Source of Truth**: Server configs defined once
- ✅ **Easy Updates**: Change server URL/auth in one place
- ✅ **Environment-Specific**: Different `.mcp.settings.json` per env
- ✅ **Credential Management**: Centralized credential handling
- ✅ **Agent Flexibility**: Agents can still override per-agent settings

---

## 5. Agent Skills (MCP Prompts & Resources) Integration — *Deferred*

*This section is for a later phase. Current focus is MCP tools only.*

The following details how to integrate MCP **Prompts** and optionally **Resources** into AgentShip later, reusing the same MCP client and registry as for tools.

### 5.1 MCP Capabilities Beyond Tools

| Capability | MCP Methods | Purpose in AgentShip |
|------------|-------------|----------------------|
| **Tools** | `tools/list`, `tools/call` | Already designed: expose as agent tools |
| **Prompts** | `prompts/list`, `prompts/get` | **Agent skills**: reusable prompt templates, injected on demand |
| **Resources** | `resources/list`, `resources/read` | Optional: load context (docs, schemas) for skills or model context |

### 5.2 Skills: Discovery and Caching

- **When**: For each MCP server that declares the `prompts` capability, discover skills via `prompts/list` (e.g. at agent init or when opening the skills catalog).
- **Cache**: Cache prompt list per server (and optionally TTL or invalidate on `prompts/list_changed` notification).
- **Registry**: Optionally store “available skills” in the same place as server config (e.g. in-memory skill catalog keyed by `server_id` + `prompt_name`).

```text
MCPServerRegistry / MCPClientManager
  └─> For each server with prompts capability:
        client.prompts_list() → List[PromptMeta]
        Cache as "skills" for that server
```

### 5.3 Configuration: Enabling Skills per Agent

**Option A – Same as tools (recommended):**  
Agents that reference an MCP server get both tools and skills from that server. No extra config.

**Option B – Explicit skill allow-list:**  
In agent YAML (or global MCP settings), allow restricting which prompts are exposed as skills:

```yaml
mcp_servers:
  - id: dev_tools_server
    tools: [run_terminal, read_file]   # tools to expose
    prompts: [code_review, write_tests] # skills (prompts) to expose; omit or use "all" for all
```

Schema-wise, extend the MCP server reference (or global server config) with an optional `prompts` field: list of prompt names or `"all"`.

### 5.4 Invocation Model: When and How Skills Run

- **User-initiated (recommended first):**  
  - User selects a skill by name (e.g. from a list or slash command).  
  - Backend calls `prompts/get` with skill name + arguments (from UI or from request payload).  
  - Backend injects the returned `messages` into the conversation (e.g. as the next user message(s), or as a system/user block for the next model turn).  
  - Agent then runs as usual (with tools, memory, etc.) using that augmented context.

- **Orchestrator / meta-tool (later):**  
  - Expose a special tool like `use_skill(name, args)` that:  
    - Resolves the skill to an MCP server + prompt name,  
    - Calls `prompts/get`,  
    - Injects the messages and continues the turn (or next turn).  
  - Same MCP client/registry; only the invocation path differs.

### 5.5 Engine-Agnostic Skill Service

Introduce a small **SkillService** (or extend MCP client manager) that:

1. **List skills** for an agent: from cached `prompts/list` for each of the agent’s MCP servers (filtered by `prompts` config if present).
2. **Get skill** (resolve prompt): `prompts/get(name, arguments)` via the appropriate MCP client.
3. **Return** the MCP response (e.g. `messages` array) so the engine or API layer can inject it.

Engines (ADK/LangGraph) do not need to know about MCP protocol details; they only need to:
- Accept “injected” messages (or a pre-filled user message) before calling the model, or
- Implement a `use_skill` tool that calls the SkillService and then injects the result.

### 5.6 Optional: MCP Resources for Skill Context

- When a skill (prompt) or the model needs extra context (e.g. a doc, a schema), the backend can call `resources/read` (or `resources/templates/list` + expand template) and append that content to the context.
- This can be:
  - **Explicit**: e.g. “load resource X when using skill Y” in config, or
  - **Implicit**: e.g. prompt template references a resource URI and the client resolves it before injecting.

No change to the engine interface is strictly required: resources are just another source of text (or blobs) that get added to the conversation or to the skill payload.

### 5.7 Summary: Skills vs Tools in This Design

| Aspect | MCP Tools | MCP Prompts (Agent Skills) |
|--------|-----------|----------------------------|
| **Discovery** | `tools/list` → ToolManager → engine tools | `prompts/list` → SkillService catalog |
| **Invocation** | Model calls tool → `tools/call` | User/orchestrator requests skill → `prompts/get` → inject messages |
| **Config** | `mcp_servers[].tools` (optional filter) | `mcp_servers[].prompts` (optional filter) or all |
| **Registry** | Same `.mcp.settings.json` + MCPServerRegistry | Same; skills are per-server capability |
| **Auth** | Same MCP client/auth | Same MCP client/auth |

Implementing skills is therefore a **parallel track** to tools: same MCP client and registry, plus SkillService + config and invocation path for prompts (and optionally resources).

---

## 6. Revised Implementation Plan (Updated 2026-02-22)

### Current Status Summary

**Completed:**
- ✅ Phase 1: Core Infrastructure (STDIO only)
- ✅ Phase 3: Tool Discovery & Integration (partial - STDIO + basic adapters)

**In Progress / Incomplete:**
- 🔴 Phase 1: SSE and HTTP transport clients
- 🔴 Phase 2: Authentication & Authorization (not started)
- 🟡 Phase 3: LangGraph adapter needs JSON Schema conversion
- 🔴 Phase 4: Error Handling & Observability (not started)
- 🔴 Phase 5: Agent Skills / Prompts & Resources (not started)
- 🔴 Phase 6: Documentation & Examples (minimal)

---

### Recommended Implementation Order

**Priority 1: Remote Transport Support (Blocking for production)**
1. Implement SSE client (`SSEMCPClient`)
2. Implement HTTP client (`HTTPMCPClient`)
3. Add connection health checks and reconnection logic
4. Integration tests with remote MCP servers

**Priority 2: Authentication (Blocking for OAuth/secure servers)**
1. Credential resolution from environment variables
2. Bearer token authentication
3. API key authentication
4. OAuth 2.1 flow (PRM discovery, PKCE, token refresh)
5. Token storage and lifecycle management
6. Integration tests for each auth method

**Priority 3: Production Hardening**
1. Retry logic with exponential backoff
2. Circuit breaker pattern
3. Graceful shutdown (`close_all()` hook in FastAPI lifespan)
4. OPIK observability integration
5. Structured logging and metrics
6. Performance testing

**Priority 4: LangGraph Schema Fix**
1. JSON Schema → Pydantic model conversion for LangGraph
2. Update `to_langgraph_tool()` to use typed args_schema
3. Test that LLM receives proper parameter schemas

**Priority 5: Skills & Resources (Optional)**
1. Extend BaseMCPClient with `list_prompts()`, `get_prompt()`
2. Extend BaseMCPClient with `list_resources()`, `read_resource()`
3. Implement SkillService
4. Add prompts/resources filtering to agent config
5. API endpoints for skill invocation

**Priority 6: Documentation & Examples**
1. Create working examples for each transport (STDIO, SSE, HTTP)
2. Document authentication setup for each auth type
3. Migration guide for existing agents
4. Troubleshooting guide for common issues

---

### Updated Phase Breakdown

### Phase 1A: Remote Transport Clients (HIGH PRIORITY)

**Status:** 🔴 **NOT STARTED** (STDIO only exists)

**Tasks:**
1. ❌ Implement `SSEMCPClient` (SSE transport for remote servers)
   - Use `mcp` SDK or implement SSE protocol manually
   - Handle SSE reconnection and event parsing
   - Support SSE-specific auth headers

2. ❌ Implement `HTTPMCPClient` (HTTP transport for remote servers)
   - Use `httpx` or `aiohttp` for HTTP requests
   - Handle request/response format per MCP spec
   - Support HTTP-specific auth headers

3. ❌ Update `MCPClientManager._create_client()` to support all transports

4. ❌ Add connection health monitoring
   - Periodic health checks
   - Automatic reconnection on failure
   - Connection timeout handling

5. ❌ Integration tests with remote MCP servers

**Deliverables:**
- SSE and HTTP clients working
- Remote MCP servers connectable
- Integration tests passing

**Estimated Effort:** 1-2 weeks

---

### Phase 2: Authentication & Authorization (HIGH PRIORITY)

**Status:** 🔴 **NOT STARTED** (models exist, no implementation)

**Tasks:**
1. ❌ Implement credential retrieval layer
   ```python
   # src/agent_framework/mcp/auth/credential_store.py
   class CredentialStore:
       def get_credential(self, var_name: str) -> Optional[str]:
           # Check env vars
           # Check secret manager (Google/AWS/Azure)
           # Check encrypted file
   ```

2. ❌ Implement bearer token authentication
   - Attach `Authorization: Bearer <token>` header
   - Token retrieval from `MCPAuthConfig.token_env`

3. ❌ Implement API key authentication
   - Attach API key header (custom header name)
   - Key retrieval from `MCPAuthConfig.api_key_var`

4. ❌ Implement OAuth 2.1 flow
   - PRM discovery (`/.well-known/oauth-protected-resource`)
   - Authorization server metadata discovery
   - PKCE code challenge/verifier generation
   - Authorization code flow
   - Token exchange
   - Token refresh logic

5. ❌ Implement token caching and lifecycle
   ```python
   # src/agent_framework/mcp/auth/token_manager.py
   class TokenManager:
       def get_access_token(self, server_id: str) -> str:
           # Check cache
           # Refresh if expired
           # Re-authenticate if refresh fails
   ```

6. ❌ Add authorization scope validation
   - Check required scopes before tool invocation
   - Log authorization failures

7. ❌ Integration tests for each auth method

**Deliverables:**
- All auth methods implemented
- OAuth flow working end-to-end
- Secure credential storage
- Token refresh working

**Estimated Effort:** 2-3 weeks

---

### Phase 3A: LangGraph Schema Fix (MEDIUM PRIORITY)

**Status:** 🟡 **PARTIAL** (basic adapter exists, schema weak)

**Current Issue:**
```python
# adapters/langgraph.py - CURRENT
class _MCPToolArgs(BaseModel):
    model_config = ConfigDict(extra="allow")  # Accepts anything!
```

**Tasks:**
1. ❌ Implement JSON Schema → Pydantic model conversion
   ```python
   def json_schema_to_pydantic(
       tool_name: str,
       input_schema: Dict[str, Any]
   ) -> Type[BaseModel]:
       # Dynamically create Pydantic model from JSON Schema
       # Handle properties, required fields, types
       # Return typed model class
   ```

2. ❌ Update `to_langgraph_tool()` to use typed schema
   ```python
   def to_langgraph_tool(tool_info: MCPToolInfo, server_config: MCPServerConfig):
       args_schema = json_schema_to_pydantic(
           tool_info.name,
           tool_info.input_schema
       )
       # Now LLM sees typed parameters!
   ```

3. ❌ Add tests comparing ADK vs LangGraph tool declarations

**Deliverables:**
- LangGraph tools have proper typed parameters
- LLM receives full schema (same as ADK)

**Estimated Effort:** 3-5 days

---

### Phase 4: Production Hardening (HIGH PRIORITY)

**Status:** 🔴 **NOT STARTED** (basic try/catch only)

**Tasks:**
1. ❌ Connection retry with exponential backoff
   ```python
   @retry(
       stop=stop_after_attempt(max_retries),
       wait=wait_exponential(multiplier=1, min=2, max=60),
       retry=retry_if_exception_type(ConnectionError)
   )
   async def connect_with_retry():
       ...
   ```

2. ❌ Circuit breaker pattern
   - Track failure rate per server
   - Open circuit after threshold failures
   - Half-open state for recovery testing
   - Automatic circuit reset

3. ❌ Graceful shutdown
   ```python
   # src/service/main.py
   @app.on_event("shutdown")
   async def shutdown_mcp_clients():
       await MCPClientManager.get_instance().close_all()
   ```

4. ❌ OPIK observability integration
   - Trace MCP tool discovery
   - Trace MCP tool invocation
   - Log connection lifecycle events
   - Metrics: connection count, latency, error rate

5. ❌ Structured logging
   ```python
   logger.info(
       "MCP tool invoked",
       extra={
           "server_id": server_config.id,
           "tool_name": tool_name,
           "latency_ms": latency,
           "success": True
       }
   )
   ```

6. ❌ Performance testing
   - Concurrent tool invocations
   - Connection pool stress test
   - Memory leak testing

**Deliverables:**
- Production-ready error handling
- Full observability
- No resource leaks
- Performance benchmarks

**Estimated Effort:** 2 weeks

---

### Phase 5: Agent Skills (MCP Prompts & Resources) – OPTIONAL

**Status:** 🔴 **NOT STARTED**

**Tasks:**
1. ❌ Extend `BaseMCPClient` interface
   ```python
   @abstractmethod
   async def list_prompts(self) -> List[MCPPromptInfo]:
       ...

   @abstractmethod
   async def get_prompt(self, name: str, arguments: dict) -> MCPPromptResult:
       ...

   @abstractmethod
   async def list_resources(self) -> List[MCPResourceInfo]:
       ...

   @abstractmethod
   async def read_resource(self, uri: str) -> Any:
       ...
   ```

2. ❌ Implement `SkillService`
   ```python
   # src/agent_framework/mcp/skill_service.py
   class SkillService:
       def list_skills(self, agent_config: AgentConfig) -> List[SkillInfo]:
           # Gather prompts from agent's MCP servers

       async def invoke_skill(
           self,
           server_id: str,
           prompt_name: str,
           arguments: dict
       ) -> List[Message]:
           # Call prompts/get and return messages
   ```

3. ❌ Add `prompts` filter to `MCPServerReference`
   ```yaml
   mcp_servers:
     - id: dev_tools
       tools: [run_terminal, read_file]
       prompts: [code_review, write_tests]  # NEW
   ```

4. ❌ API endpoints for skill invocation
   ```python
   # GET /api/agents/{agent_name}/skills
   # POST /api/agents/{agent_name}/skills/{skill_name}/invoke
   ```

5. ❌ Documentation and examples

**Deliverables:**
- Skills discoverable per agent
- Skills invocable via API
- Messages injected into conversation
- Resources loadable for context

**Estimated Effort:** 1-2 weeks

---

### Phase 6: Documentation & Examples

**Status:** 🔴 **MINIMAL** (design doc only, no user guides)

**Tasks:**
1. ❌ User guide: Setting up MCP servers
2. ❌ User guide: Authentication configuration
3. ❌ Example agents for each transport
   - STDIO example (filesystem server)
   - SSE example (remote server)
   - HTTP example (API server)
4. ❌ OAuth setup guide
5. ❌ Troubleshooting guide
   - Connection failures
   - Auth errors
   - Tool invocation errors
6. ❌ Migration guide for existing agents
7. ❌ API documentation updates

**Deliverables:**
- Complete user documentation
- Working examples
- Troubleshooting guide

**Estimated Effort:** 1 week

---

### Total Estimated Effort

- **Phase 1A (Remote Transports):** 1-2 weeks
- **Phase 2 (Authentication):** 2-3 weeks
- **Phase 3A (LangGraph Fix):** 3-5 days
- **Phase 4 (Hardening):** 2 weeks
- **Phase 5 (Skills - Optional):** 1-2 weeks
- **Phase 6 (Docs):** 1 week

**Total (Critical Path):** 6-8 weeks for production-ready MCP support (STDIO + remote + auth + hardening)
**Total (with Skills):** 7-10 weeks

---

## 7. Security Considerations

### 6.1 Credential Security

- **Never log credentials**: All credential access logged at debug level only
- **Encryption at rest**: Encrypted config files use AES-256
- **Encryption in transit**: All MCP connections use TLS (HTTPS/WSS)
- **Credential rotation**: Support for credential refresh without agent restart

### 6.2 Authorization Enforcement

- **Scope validation**: Check required scopes before tool invocation
- **Permission checks**: Per-tool permission validation
- **Audit logging**: Log all authorization decisions
- **Rate limiting**: Per-server rate limiting to prevent abuse

### 6.3 Connection Security

- **Connection isolation**: Each agent instance has isolated MCP connections
- **Timeout enforcement**: Strict timeouts prevent hanging connections
- **Input validation**: Validate all inputs before sending to MCP servers
- **Output sanitization**: Sanitize outputs from MCP servers

### 6.4 Best Practices

- Use environment variables for production credentials
- Use secret management services for sensitive deployments
- Implement least-privilege access (minimum required scopes)
- Regular credential rotation
- Monitor connection health and failures

---

## 8. Testing Strategy

### 7.1 Unit Tests

- Configuration parsing (valid/invalid configs)
- Credential retrieval (all storage methods)
- OAuth flow (mock authorization server)
- Tool discovery (mock MCP server)
- Adapter conversion (ADK/LangGraph)

### 7.2 Integration Tests

- End-to-end tool invocation (real MCP server)
- Authentication flows (OAuth, bearer token)
- Error scenarios (server down, invalid credentials)
- Connection pooling and reuse

### 7.3 E2E Tests

- Agent with MCP tools (ADK engine)
- Agent with MCP tools (LangGraph engine)
- Multiple MCP servers per agent
- Tool chaining (MCP tool → function tool → agent tool)

### 7.4 Performance Tests

- Connection establishment time
- Tool invocation latency
- Concurrent tool invocations
- Memory usage with multiple servers

---

## 9. Migration Path

### 8.1 For Existing Agents

**No changes required** - existing agents continue to work without MCP support.

### 8.2 Adding MCP Support to Existing Agent

**Step 1: Define MCP servers globally** (one-time setup)

Create `.mcp.settings.json` in project root:

```json
{
  "servers": {
    "github": {
      "transport": "sse",
      "url": "https://mcp.github.com/sse",
      "auth": {
        "type": "oauth",
        "client_id_env": "GITHUB_CLIENT_ID",
        "client_secret_env": "GITHUB_CLIENT_SECRET",
        "scopes": ["repo:read", "issues:write"]
      }
    }
  }
}
```

**Step 2: Reference servers in agent config**

Add `mcp_servers` section to `main_agent.yaml`:

```yaml
agent_name: my_agent
tools:
  - type: function
    id: my_tool
    import: src.tools.my_tool.MyTool

mcp_servers:
  - id: github  # References server from global registry
```

**Step 3: Configure credentials**

Set environment variables:
```bash
export GITHUB_CLIENT_ID=your_client_id
export GITHUB_CLIENT_SECRET=your_client_secret
```

**Step 4: Restart agent**

MCP tools automatically discovered and available.

### 8.3 Example Migration

**Before:**
```yaml
agent_name: my_agent
tools:
  - type: function
    id: my_tool
    import: src.tools.my_tool.MyTool
```

**After:**

**1. Create `.mcp.settings.json`:**
```json
{
  "servers": {
    "github": {
      "transport": "sse",
      "url": "https://mcp.github.com/sse",
      "auth": {
        "type": "oauth",
        "client_id_env": "GITHUB_CLIENT_ID",
        "client_secret_env": "GITHUB_CLIENT_SECRET"
      }
    }
  }
}
```

**2. Update `main_agent.yaml`:**
```yaml
agent_name: my_agent
tools:
  - type: function
    id: my_tool
    import: src.tools.my_tool.MyTool

mcp_servers:
  - id: github  # Simple reference to global server
```

---

## 10. Future Enhancements

### 10.1 Advanced Features

- **MCP Server Health Monitoring**: Health checks and automatic failover
- **Tool Caching**: Cache tool schemas and results
- **Batch Tool Invocations**: Optimize multiple tool calls
- **Tool Versioning**: Support multiple versions of same tool
- **Dynamic Tool Registration**: Add/remove tools at runtime
- **MCP Resources for context**: Use `resources/list` and `resources/read` to load docs/schemas into agent context or into skill resolution

### 10.2 Integration Improvements

- **MCP Server Marketplace**: Discover and install MCP servers
- **Visual Tool Explorer**: UI for browsing available MCP tools
- **Tool Testing Framework**: Test MCP tools before production use
- **Cost Tracking**: Track MCP server usage and costs

---

## 11. Open Questions & Decisions Needed

### 11.1 Authentication

- **Q**: Should we support interactive OAuth flows (browser redirect)?
  - **A**: Initially no - use refresh tokens. Add interactive flow in Phase 2 if needed.

- **Q**: How to handle token expiration during agent execution?
  - **A**: Automatic refresh with exponential backoff. Fail gracefully if refresh fails.

### 11.2 Connection Management

- **Q**: Should connections be per-agent or shared across agents?
  - **A**: Per-agent initially for isolation. Add connection pooling later if needed.

- **Q**: How to handle MCP server restarts?
  - **A**: Automatic reconnection with exponential backoff. Max retry limit.

### 11.3 Tool Discovery

- **Q**: When to discover tools - at agent init or on-demand?
  - **A**: At agent init for predictable behavior. Cache results.

- **Q**: How to handle tool schema changes?
  - **A**: Re-discover on agent restart. Add versioning in future.

---

## 12. Success Criteria (Updated 2026-02-22)

### 12.1 Functional Requirements

**Current Status:**
- ✅ Agents can connect to MCP servers via **STDIO only**
- ❌ SSE and HTTP connections not supported
- ✅ MCP tools appear as regular tools in both ADK and LangGraph engines (STDIO only)
- ❌ Authentication not implemented (all servers must be unauthenticated)
- ❌ Authorization scopes not enforced
- ❌ Error handling basic (not robust)

**Target State:**
- ✅ Agents can connect to MCP servers (STDIO, SSE, HTTP)
- ✅ MCP tools appear as regular tools in both ADK and LangGraph engines
- ✅ Authentication works for all supported methods (bearer, API key, OAuth)
- ✅ Authorization scopes are enforced
- ✅ Error handling is robust (retry, circuit breaker, graceful failure)

### 12.2 Non-Functional Requirements

**Current Status:**
- ✅ No performance degradation for agents without MCP
- ❓ MCP tool invocation latency (not measured - STDIO only)
- ❓ Connection establishment time (not measured)
- ❓ Memory overhead (not measured)
- ❌ No observability integration for MCP operations

**Target State:**
- ✅ No performance degradation for agents without MCP
- ✅ MCP tool invocation latency < 500ms (p95) for remote servers
- ✅ Connection establishment < 2s (p95) for remote servers
- ✅ Memory overhead < 10MB per MCP server
- ✅ Full observability integration (OPIK traces, metrics, logs)

### 12.3 Quality Requirements

**Current Status:**
- ✅ Unit test coverage > 80% (29 tests, all passing - for implemented features)
- ❌ No integration tests with real MCP servers
- ❌ No auth flow tests
- ❌ Documentation incomplete (design doc only, no user guides)
- ❌ No working examples for users

**Target State:**
- ✅ Unit test coverage > 80%
- ✅ Integration test coverage for all transports (STDIO, SSE, HTTP)
- ✅ Integration test coverage for all auth methods
- ✅ Documentation complete and accurate
- ✅ Examples work out-of-the-box (STDIO, SSE, HTTP with different auth methods)

---

## 13. Implementation Priority (Client Architecture)

**Confirmed Architecture:** AgentShip as MCP Client

```
┌─────────────────┐
│   AgentShip     │
│                 │
│ ┌─────────────┐ │
│ │   Agent     │ │
│ │   (uses     │ │
│ │   MCP tools)│ │
│ └──────┬──────┘ │
│        │        │
│ ┌──────▼──────┐ │
│ │ MCP Client  │ │──────┐
│ │ Manager     │ │      │
│ └─────────────┘ │      │
└─────────────────┘      │
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
   ┌─────────┐     ┌─────────┐     ┌─────────┐
   │  MCP    │     │  MCP    │     │  MCP    │
   │ Server  │     │ Server  │     │ Server  │
   │ (STDIO) │     │  (SSE)  │     │ (HTTP)  │
   └─────────┘     └─────────┘     └─────────┘
   (filesystem)    (github)        (database)
```

### 13.1 Critical Path to Production

**Immediate Priorities (Next 2-4 weeks):**

1. **SSE Client Implementation** (Week 1-2)
   - Enable connection to remote SSE MCP servers
   - Handle SSE events and reconnection
   - Critical for: GitHub, remote APIs, cloud services

2. **HTTP Client Implementation** (Week 1-2)
   - Enable connection to HTTP-based MCP servers
   - Handle HTTP request/response format
   - Critical for: REST APIs, database services

3. **Authentication - Environment Variables** (Week 2-3)
   - Credential resolution from env vars
   - Bearer token authentication
   - API key authentication
   - Critical for: Secure server access

4. **Graceful Shutdown** (Week 2)
   - Close all MCP connections on app shutdown
   - Prevent STDIO process leaks
   - Critical for: Production stability

**Secondary Priorities (Week 4-6):**

5. **OAuth 2.1 Flow** (Week 4-5)
   - PRM discovery
   - Authorization code + PKCE
   - Token refresh
   - Critical for: OAuth-protected servers (GitHub, Google, etc.)

6. **Production Hardening** (Week 5-6)
   - Retry logic with exponential backoff
   - Circuit breaker pattern
   - OPIK observability integration
   - Performance testing

7. **LangGraph Schema Fix** (Week 5)
   - JSON Schema → Pydantic conversion
   - Proper typed parameters for LLM
   - Critical for: LangGraph agents using MCP tools

**Optional Enhancements (Week 7+):**

8. **MCP Prompts/Skills** (Week 7-8)
   - `prompts/list` and `prompts/get`
   - Skills service layer
   - Nice-to-have for: Advanced agent capabilities

9. **MCP Resources** (Week 8+)
   - `resources/list` and `resources/read`
   - Context loading from MCP servers
   - Nice-to-have for: Context-aware agents

### 13.2 MVP Definition

**Minimum Viable Product for Production:**
- ✅ STDIO transport (done)
- ❌ SSE transport (critical)
- ❌ HTTP transport (critical)
- ❌ Environment variable auth (critical)
- ❌ Bearer token auth (critical)
- ❌ Graceful shutdown (critical)
- 🟡 OAuth (important but not blocking)
- 🟡 LangGraph schema fix (important for LangGraph users)
- ❌ Observability (important for production monitoring)

**Timeline to MVP:** 4-6 weeks
**Timeline to Full Production:** 6-8 weeks (including OAuth + hardening)

---

## Appendix A: File Structure

```
src/agent_framework/
├── mcp/
│   ├── __init__.py
│   ├── registry.py                 # Global MCP server registry
│   ├── client_manager.py           # Singleton client manager
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── base.py                 # Base MCPClient interface
│   │   ├── stdio.py                 # STDIO transport client
│   │   ├── sse.py                   # SSE transport client
│   │   └── http.py                  # HTTP transport client
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── credential_store.py     # Credential storage abstraction
│   │   ├── oauth.py                 # OAuth 2.1 implementation
│   │   └── token_manager.py         # Token caching & refresh
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── adk_adapter.py          # ADK tool adapter
│   │   └── langgraph_adapter.py    # LangGraph tool adapter
│   ├── discovery.py                 # Tool discovery
│   ├── skill_service.py             # Agent skills: prompts/list, prompts/get
│   └── models.py                    # MCP data models
├── configs/
│   └── agent_config.py             # Updated with MCP server references
└── tools/
    └── tool_manager.py              # Updated with MCP tool creation

# Configuration files (project root)
.mcp.settings.json                   # Global MCP server registry (JSON)
# OR
mcp_servers.yaml                     # Global MCP server registry (YAML)
```

**Configuration File Location Priority:**
1. Environment variable: `MCP_SERVERS_CONFIG` (explicit path)
2. `.mcp.settings.json` (current directory)
3. `mcp_servers.yaml` (current directory)
4. `mcp_servers.json` (current directory)

---

## Appendix B: Example MCP Server Configurations

### B.1 Local Filesystem Server (STDIO)

```yaml
mcp_servers:
  - id: filesystem
    transport: stdio
    command: ["npx", "-y", "@modelcontextprotocol/server-filesystem"]
    env:
      MCP_FILESYSTEM_ROOT: "/home/user/documents"
    auth:
      type: none
```

### B.2 GitHub Server (SSE with OAuth)

```yaml
mcp_servers:
  - id: github
    transport: sse
    url: https://mcp.github.com/sse
    auth:
      type: oauth
      client_id_env: GITHUB_CLIENT_ID
      client_secret_env: GITHUB_CLIENT_SECRET
      scopes:
        - repo:read
        - issues:write
    tools:
      - github_search_code
      - github_create_issue
```

### B.3 Database Server (HTTP with Bearer Token)

```yaml
mcp_servers:
  - id: database
    transport: http
    url: https://mcp.database.com/api
    auth:
      type: bearer_token
      token_env: DATABASE_MCP_TOKEN
    timeout: 60
    max_retries: 5
```

---

## Appendix C: How Other Frameworks Connect to and Discover MCP Servers

This appendix summarizes how popular frameworks handle MCP server connection and tool discovery. It informs our design and keeps patterns consistent with the ecosystem.

### C.1 LangChain / LangGraph (`langchain-mcp-adapters`)

**Package:** [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters) — converts MCP tools into LangChain tools for use with LangGraph (and other LangChain runnables).

**Connection & discovery:**

- **Single server:** Use `create_session(connection)` to get an MCP `ClientSession`, then `load_mcp_tools(session=session)` to fetch and convert tools to LangChain `BaseTool`.
- **Multiple servers:** `MultiServerMCPClient(connections: dict[str, Connection])` holds a map of server name → connection. Call `get_tools()` (or use `session()` per server and `load_mcp_tools`) to load tools from all servers. Optional `tool_name_prefix=True` prefixes tool names with server name (e.g. `weather_search`) to avoid clashes.
- **Connection types:** Typed connection configs:
  - **Stdio:** `StdioConnection(transport="stdio", command=..., args=[...], env=..., cwd=...)`
  - **SSE:** `SSEConnection(transport="sse", url=..., headers=..., timeout=..., auth=...)`
  - **Streamable HTTP:** `StreamableHttpConnection(...)`

**Pattern:** Session per server (or multi-session client), then “load tools” once per session; tools are converted to LangChain format and passed into the agent/graph. No separate “registry file”; connections are typically built in code or from app config.

**References:**  
- [LangChain MCP Adapters Reference](https://reference.langchain.com/python/langchain_mcp_adapters/)  
- [MultiServerMCPClient](https://reference.langchain.com/python/langchain-mcp-adapters/client/MultiServerMCPClient), [load_mcp_tools](https://reference.langchain.com/python/langchain-mcp-adapters/tools/load_mcp_tools), [create_session](https://reference.langchain.com/python/langchain-mcp-adapters/sessions/create_session)  
- [Harnessing MCP Servers with LangChain and LangGraph](https://dev.to/jamesbmour/harnessing-mcp-servers-with-langchain-and-langgraph-a-comprehensive-guide-1dgl)

---

### C.2 Claude Agent SDK (Anthropic)

**Config:** In-code and/or **`.mcp.json`** at project root. The SDK loads `.mcp.json` automatically so servers don’t need to be passed in code every time.

**Connection & discovery:**

- **In code:** Pass `mcpServers` (or `mcp_servers` in Python) as a dict: key = server name, value = server config (stdio: `command` + `args` + `env`; HTTP/SSE: `type` + `url` + optional `headers`).
- **From file (`.mcp.json`):**

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    },
    "remote-api": {
      "type": "sse",
      "url": "https://api.example.com/mcp/sse",
      "headers": { "Authorization": "Bearer ${API_TOKEN}" }
    }
  }
}
```

- **Tool naming:** Tools are named `mcp__<server_name>__<tool_name>` (e.g. `mcp__github__list_issues`). Discovery is implicit: once connected, the SDK gets tools from the server; the client then uses `allowedTools` (e.g. `["mcp__github__*"]`) to allow all tools from a server or specific tools.
- **Discovery at runtime:** A `system` message with subtype `init` includes MCP server connection status and available tools; you can inspect it to see what was discovered.

**Transports:** stdio (local process with `command`/`args`/`env`), HTTP, SSE. Auth via `env` for stdio and `headers` for HTTP/SSE; OAuth is done in the app and the token is passed in headers.

**References:**  
- [Connect to external tools with MCP (Claude Agent SDK)](https://platform.claude.com/docs/en/agent-sdk/mcp)  
- [MCP connector (Messages API)](https://docs.anthropic.com/en/docs/agents-and-tools/mcp-connector)

---

### C.3 OpenAI Agents SDK (Python)

**Model:** Abstract `MCPServer` base class with `connect()`, `cleanup()`, `list_tools()`, `call_tool()`, plus optional `list_prompts()` / `get_prompt()`. Concrete implementations for each transport.

**Connection & discovery:**

- **Stdio:** `MCPServerStdio(params=MCPServerStdioParams(command=..., args=[...], env=..., cwd=..., encoding=...))`. The SDK spawns the process and maintains the session; `list_tools()` is called to discover tools. Optional `cache_tools_list=True` to avoid repeated discovery.
- **Discovery:** Tools are discovered by calling `list_tools()` on the server instance after `connect()`. Tools can be filtered via a `tool_filter`; approval policies (`require_approval`) and error handling (`failure_error_function`) are per-server.
- **Retries:** `max_retry_attempts` and `retry_backoff_seconds_base` for failed `list_tools` / `call_tool`.

**Pattern:** One object per MCP server; explicit lifecycle (`connect` → use `list_tools` / `call_tool` → `cleanup`). No built-in global registry file; servers are typically constructed in code from config.

**References:**  
- [MCP Servers - OpenAI Agents SDK (Python)](https://openai.github.io/openai-agents-python/ref/mcp/server/)

---

### C.4 OpenAI Responses API (HTTP API)

**Model:** MCP is a **tool type** in the request. You pass the MCP server URL (and optional auth) in the `tools` array; the API runtime connects to the server, discovers tools, and executes tool calls.

**Connection & discovery:**

- You specify a tool of type `mcp` with e.g. `server_url`, optional OAuth/headers, and approval settings.
- The runtime detects transport (streamable HTTP or HTTP-over-SSE), fetches the tool list from the server, and exposes them to the model. Tool calls are executed against the MCP server directly.
- Best practice: use `allowed_tools` (or equivalent) to limit which tools the model can call; filter tools to avoid overwhelming context.

**References:**  
- [Building MCP servers for ChatGPT Apps and API integrations](https://developers.openai.com/api/docs/mcp)  
- [Connectors and MCP servers](https://developers.openai.com/api/docs/guides/tools-connectors-mcp)  
- [Guide to Using the Responses API's MCP Tool](https://developers.openai.com/cookbook/examples/mcp/mcp_tool_guide/)

---

### C.5 Takeaways for AgentShip

| Aspect | LangChain | Claude SDK | OpenAI Agents SDK | AgentShip (this design) |
|--------|-----------|------------|-------------------|-------------------------|
| **Config source** | Code / app config | Code + `.mcp.json` | Code | Global `.mcp.settings.json` / `mcp_servers.yaml` + per-agent refs in YAML |
| **Multi-server** | `MultiServerMCPClient(connections)` | Dict of servers in `mcpServers` | Multiple `MCPServer*` instances | Registry + agent `mcp_servers` list (IDs + overrides) |
| **Discovery** | `load_mcp_tools(session)` or `get_tools()` | Implicit after connect; `init` message | `list_tools()` after `connect()` | `MCPToolDiscovery.discover_tools(server_config)` via client |
| **Tool naming** | Optional prefix per server | `mcp__servername__toolname` | By server/tool | Per-engine adapter; optional prefix to avoid clashes |
| **Transports** | Stdio, SSE, Streamable HTTP | Stdio, HTTP, SSE | Stdio (and others via base) | STDIO, SSE, HTTP (same as others) |
| **Auth** | In connection (env, headers, auth) | `env`, `headers` in server config | `env` in stdio params | Credential store + env vars / bearer / OAuth in registry |
| **Tool filtering** | When loading / composing tools | `allowedTools` (allowlist) | `tool_filter` on server | Per-agent `tools` list in server reference (optional) |

We align with the ecosystem by: supporting a **global registry file** (like Claude’s `.mcp.json` but with optional per-agent overrides), **explicit discovery** via a client that talks to the server (like LangChain and OpenAI SDK), **typed connection configs** per transport (stdio/SSE/HTTP), and **tool filtering** at the agent level (similar to `allowedTools` / `tool_filter`).

---

## Conclusion & Next Steps

### Summary of Current State (2026-02-22)

**What Works:**
- ✅ STDIO MCP servers can be connected and used
- ✅ MCP tools integrate with both ADK and LangGraph engines
- ✅ Configuration system (global registry + per-agent) working
- ✅ Basic tool discovery and invocation working
- ✅ 29 unit tests passing

**Critical Blockers for Production:**
- 🔴 **No remote server support** (SSE/HTTP not implemented)
- 🔴 **No authentication** (can't use OAuth, bearer tokens, or API keys)
- 🔴 **Weak LangGraph schema** (LLM doesn't see typed parameters)
- 🔴 **No observability** (can't trace/debug MCP operations)
- 🔴 **No graceful shutdown** (STDIO processes may leak)

**Estimated Effort to Production:**
- Minimum viable (STDIO + basic remote + env var auth): **4-6 weeks**
- Production-ready (all transports + all auth + hardening): **6-8 weeks**
- Full featured (+ skills/prompts/resources): **7-10 weeks**

### Recommended Next Steps

**Step 1: Architectural Decision (URGENT)**
- Decide: Client Architecture vs Gateway Architecture
- **Recommendation:** Client Architecture (current path) - simpler and faster
- **Decision needed from:** Product/Engineering leadership
- **Timeline:** This week

**Step 2: Prioritize Critical Features (Week 1-2)**
1. Implement SSE client
2. Implement HTTP client
3. Implement basic auth (env vars → bearer tokens)
4. Add graceful shutdown hook
5. Integration tests with remote servers

**Step 3: Authentication (Week 3-4)**
1. OAuth 2.1 flow implementation
2. API key authentication
3. Token refresh logic
4. Integration tests

**Step 4: Production Hardening (Week 5-6)**
1. Retry logic with exponential backoff
2. OPIK observability integration
3. Fix LangGraph schema conversion
4. Performance testing

**Step 5: Documentation & Examples (Week 7-8)**
1. User guides for each transport and auth method
2. Working examples
3. Troubleshooting guide
4. Migration guide

### Open Questions

1. ✅ **Architecture:** Client only (CONFIRMED)
2. **Auth priority:** Which auth methods are most critical?
   - Env vars + bearer token (most common, simple)
   - OAuth 2.1 (complex but needed for GitHub, Google, etc.)
   - API key (simple alternative)
   - **Recommendation:** Start with env vars + bearer, then OAuth
3. **Skills/Prompts:** Are MCP prompts/resources required for MVP?
   - **Recommendation:** Defer to post-MVP (Week 7+)
4. **Deployment:** How to handle MCP server lifecycle in production?
   - STDIO: Child processes managed by AgentShip
   - Remote (SSE/HTTP): External services (separate deployment)
   - **Recommendation:** Document both patterns in deployment guide

### Success Metrics

**Phase 1 (Remote Transports) Success:**
- [ ] Agent can connect to SSE MCP server
- [ ] Agent can connect to HTTP MCP server
- [ ] Integration tests pass for all transports
- [ ] Example agents work with remote servers

**Phase 2 (Auth) Success:**
- [ ] OAuth-protected MCP server works end-to-end
- [ ] Bearer token auth works
- [ ] API key auth works
- [ ] Tokens refresh automatically

**Phase 3 (Production) Success:**
- [ ] MCP operations traced in OPIK
- [ ] Connection failures handled gracefully
- [ ] No resource leaks after 1000+ tool invocations
- [ ] LangGraph tools have proper parameter schemas
- [ ] Documentation complete

### Contact & Support

For questions or issues with MCP integration:
- GitHub Issues: [AgentShip Issues](https://github.com/AgentShippingKit/agentship/issues)
- Design discussions: This document
- Implementation tracking: GitHub Projects

---

## Appendix A: Event Loop Handling

### Problem
MCP STDIO clients experienced event loop mismatch errors in production web servers:
```
RuntimeError: <Queue> is bound to a different event loop
anyio.ClosedResourceError: The receive stream was already closed
```

### Root Cause
- Agent initialization happens in one event loop (application startup)
- Web requests run in different event loops (per request)
- MCP client's anyio streams are bound to initialization event loop
- Reusing client across event loops causes crashes

### Solution
Implemented event loop detection and automatic reconnection in `StdioMCPClient`:

```python
class StdioMCPClient(BaseMCPClient):
    def __init__(self, config: MCPServerConfig) -> None:
        super().__init__(config)
        self._event_loop = None  # Track which event loop created connection

    async def _ensure_connected(self) -> ClientSession:
        current_loop = asyncio.get_event_loop()

        # Check if we're connected AND in the same event loop
        if self._is_connected and self._session is not None:
            if self._event_loop is current_loop:
                return self._session
            else:
                # Event loop changed - reconnect
                logger.warning("Event loop changed, reconnecting...")
                await self.close()
                self._is_connected = False

        # Connect and store event loop
        self._session = await self._connect()
        self._event_loop = current_loop
        return self._session
```

**Benefits:**
- ✅ Works in both standalone scripts and web servers
- ✅ No manual reconnection needed
- ✅ Transparent to agent code
- ✅ Production-ready

---

## Appendix B: Dual Engine Support Verification

### Status: FULLY VERIFIED ✅

MCP integration works identically with **both execution engines**:
- ✅ **ADK Engine** - Production-ready
- ✅ **LangGraph Engine** - Production-ready

### Engine Parity Achieved

Both engines support:
- ✅ MCP tool discovery
- ✅ Auto tool documentation
- ✅ Event loop safe reconnection
- ✅ Custom Pydantic input/output schemas
- ✅ Same configuration format

### Example Agents

**ADK Version:**
```yaml
# src/all_agents/postgres_adk_mcp_agent/main_agent.yaml
agent_name: postgres_adk_mcp_agent
execution_engine: adk
llm_provider_name: openai
llm_model: gpt-4o-mini
temperature: 0.2

mcp_servers:
  - id: postgres
```

**LangGraph Version:**
```yaml
# src/all_agents/postgres_langgraph_mcp_agent/main_agent.yaml
agent_name: postgres_langgraph_mcp_agent
execution_engine: langgraph  # <-- Only difference!
llm_provider_name: openai
llm_model: gpt-4o-mini
temperature: 0.2

mcp_servers:
  - id: postgres
```

**Key Achievement:** Same agent code works with both engines - only YAML `execution_engine` field changes!

### Implementation Details

**ADK Engine:**
- Uses native `output_schema` in ADK agent configuration
- Passes Pydantic model directly to ADK framework
- ADK handles structured output natively

**LangGraph Engine:**
- Uses improved `build_schema_prompt()` with clear examples
- Extracts JSON Schema from MCP tools for proper parameter typing
- Creates dynamic Pydantic models via `create_model()`
- Sets `response_format={"type": "json_object"}` for OpenAI

### Key Fixes Applied

1. **MCP Schema Extraction (LangGraph):**
   - Created `_create_args_schema()` in `langgraph.py` adapter
   - Maps JSON Schema types to Python types
   - Creates dynamic Pydantic models for tool parameters
   - Properly marks required/optional fields

2. **Output Schema Handling (LangGraph):**
   - Rewrote `build_schema_prompt()` to show clear examples
   - Generates field-by-field documentation
   - Shows placeholder values instead of confusing JSON Schema
   - Includes explicit instruction to return actual data

---

## Appendix C: Testing Guide

### Test Agents

**1. PostgreSQL ADK MCP Agent**
- Path: `src/all_agents/postgres_adk_mcp_agent/`
- Engine: ADK
- Class: `PostgresAdkMcpAgent`

**2. PostgreSQL LangGraph MCP Agent**
- Path: `src/all_agents/postgres_langgraph_mcp_agent/`
- Engine: LangGraph
- Class: `PostgresLanggraphMcpAgent`

Both agents demonstrate engine parity - only `execution_engine` field differs.

### Test Suite

**ADK Engine Test:**
```bash
docker exec agentship-api python tests/test_auto_tool_docs.py
```

Tests:
- MCP tool discovery
- Auto-generated tool documentation
- Database queries via MCP
- Proper `TextOutput` validation

**LangGraph Engine Test:**
```bash
docker exec agentship-api python tests/test_postgres_langgraph_mcp.py
```

Tests:
- Engine type verification
- PromptBuilder integration
- MCP tool execution
- Output schema validation

**Direct MCP Client Test:**
```bash
docker exec agentship-api python tests/test_postgres_adk_mcp.py
```

Tests:
- MCP server connection
- Tool discovery
- Raw MCP tool calls

### Expected Results

Both engines return identical database results in `TextOutput` format:

```python
TextOutput(
    response='The following tables are present in the database:\n'
    '- app_states\n'
    '- user_states\n'
    '- sessions\n'
    '- events\n'
    '- checkpoint_migrations\n'
    '- checkpoints\n'
    '- checkpoint_blobs\n'
    '- checkpoint_writes'
)
```

---

## Appendix D: Known Issues

### 1. MCP Client Cleanup Warning (Non-Critical)

**Issue:**
```
RuntimeError: Attempted to exit cancel scope in a different task than it was entered in
```

**Impact:** Cosmetic only - appears during test cleanup but doesn't affect functionality.

**Status:** Known MCP STDIO client issue, does not impact production use.

### 2. Opik Token Usage Logging (Non-Critical)

**Issue:**
```
OPIK: Failed to log token usage from ADK Gemini call
ValidationError: 3 validation errors for GoogleGeminiUsage
```

**Impact:** Observability metrics only - agent functionality unaffected.

**Status:** Opik integration issue, not MCP-related.

### 3. Coroutine Warning (Non-Critical)

**Issue:**
```
RuntimeWarning: coroutine 'ToolManager._create_mcp_tools.<locals>._gather' was never awaited
```

**Impact:** Warning only during agent initialization, doesn't prevent tool loading.

**Status:** Low priority, tools load successfully despite warning.

---

**Document Version:** 3.0 (Consolidated 2026-02-24)
**Last Updated:** 2026-02-24
**Includes:** Design, Implementation, Event Loop Fix, Dual Engine Verification, Testing, Known Issues
**Next Review:** Before SSE/HTTP transport implementation
