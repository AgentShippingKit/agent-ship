# 🚀 Ship AI Agents: Production-Ready Framework

A complete cookie-cutter template for building, deploying, and operating AI agents using Google ADK. **Fork → Deploy → Ship in minutes.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Google ADK](https://img.shields.io/badge/Google-ADK-blue)](https://google.github.io/adk-docs/)

## ✨ What You Get Out of the Box

### 🤖 **Multi-Agent Patterns**
- **Orchestrator Pattern**: Coordinate multiple sub-agents (trip planner with flight, hotel, summary agents)
- **Single Agent Pattern**: Standalone agents (translation)
- **Tool Pattern**: Database agents with comprehensive tooling
- **YAML + Python Configs**: Easy customization and deployment

### ⚡ **Production-Ready Backend**
- **FastAPI**: REST APIs with streaming, WebSocket support
- **Google ADK Framework**: Multi-LLM provider support (Gemini, OpenAI, Claude)
- **Security Guardrails**: PII protection, input/output processing
- **Observability**: Native Opik integration for tracing and metrics

### 🎨 **API-First Design**
- **REST APIs**: Comprehensive HTTP endpoints
- **WebSocket Support**: Real-time communication ready
- **Streaming APIs**: Large response handling
- **OpenAPI Documentation**: Auto-generated API docs

### 🧠 **Memory Management**
- **Short-term**: PostgreSQL for session management
- **Long-term**: OpenSearch for RAG capabilities
- **File Storage**: S3 integration for document handling
- **Agent Caching**: DiceDB for high-performance agent state and session caching

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/ship-ai-agents.git
cd ship-ai-agents

# Install dependencies
pipenv install

# Set up environment variables
cp env.example .env
# Edit .env with your API keys (see Environment Variables section)
```

### 2. Database Setup
```bash
# Set up PostgreSQL (see Database Setup guide)
cd agent_store_deploy
./setup_local_postgres.sh  # For local development
# OR
./setup_heroku_postgres.sh # For production
```

### 3. Start Development
```bash
# Start the FastAPI backend
pipenv run uvicorn src.service.main:app --reload --port 7001
```

### 4. Deploy to Production
```bash
# Deploy to Heroku (see Heroku Deployment guide)
cd service_cloud_deploy/heroku
./deploy_heroku.sh
```

### 4. Access Your Application
- **API Documentation**: http://localhost:7001/docs
- **Health Check**: http://localhost:7001/health
- **Agents Chat**: http://localhost:7001/api/agents/chat

## 📋 Environment Variables

Create a `.env` file with the following variables:

```bash
# Required: At least one LLM provider
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Database (set automatically by deployment scripts)
SESSION_STORE_URI=postgresql://user:password@host:port/database

# Optional
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## 🏗️ Architecture Overview

![AI Agents Architecture](AgenticAI.jpg)

Our platform provides a complete AI agent ecosystem with:

#### ✨ Features
- **FastAPI Layer**: HTTP/chat, SSE/chat-streaming, WebSocket support with guardrails, observability, and PII security
- **AI Backend**: Google ADK framework (only) with multiple LLM provider integration like Google Gemini, OpenAI Chatgpt, Claude etc.
- **Memory Management**: Short/long-term memory with Postgres, RAG with Opensearch, and caching with DiceDB and flat file interaction with S3.
- **Observability**: Native Opik integration for tracing and metric
- **Operations**: Prompt versioning, evals, and evals tracing via Opik SDK integration
- **Tools & MCP**: Comprehensive tool registry and Model Control Plane for agent capabilities

## 🤖 Pre-Built Agents

### Trip Planner Agent
- **Purpose**: Complete trip planning with flight and hotel coordination
- **Features**: Orchestrates flight, hotel, and summary agents
- **Use Case**: Travel applications, booking platforms

### Translation Agent
- **Purpose**: Multi-language text translation
- **Features**: Language detection, context preservation
- **Use Case**: International applications, content localization

### Database Agent
- **Purpose**: Natural language database queries
- **Features**: Schema exploration, data analysis, statistics
- **Use Case**: Business intelligence, data exploration tools

### Flight & Hotel Agents
- **Purpose**: Specialized travel planning
- **Features**: Route optimization, accommodation recommendations
- **Use Case**: Travel booking, itinerary planning

## 🛠️ Customization

### Adding New Agents
1. Create agent directory in `src/agents/all_agents/`
2. Add YAML configuration file
3. Implement agent logic in Python
4. Register in agent registry

### Example Agent Structure
```
src/agents/all_agents/your_agent/
├── main_agent.py          # Agent implementation
├── main_agent.yaml        # Configuration
└── __init__.py           # Module initialization
```

### Environment Configuration
```yaml
# main_agent.yaml
agent_name: your_agent
llm_provider_name: openai
llm_model: gpt-4o
temperature: 0.4
description: Your agent description
instruction_template: |
  Your agent instructions here...
```

## 🚀 Deployment

### Heroku (Backend)
```bash
# Deploy to Heroku
./service_cloud_deploy/heroku/deploy_heroku.sh
```


## 📊 Observability & Monitoring

### Opik Integration
- **Tracing**: Request/response tracking
- **Metrics**: Performance monitoring
- **Evals**: Agent evaluation and testing
- **Logging**: Structured logging with context

### Health Checks
- **Service Health**: `/health` endpoint
- **Database Health**: Connection monitoring
- **Agent Health**: Individual agent status

## 🔒 Security Features

### Input/Output Processing
- **PII Detection**: Automatic sensitive data identification
- **Content Filtering**: Inappropriate content detection
- **Rate Limiting**: API abuse prevention
- **Authentication**: JWT-based security

### Data Protection
- **Encryption**: Data at rest and in transit
- **Access Control**: Role-based permissions
- **Audit Logging**: Complete activity tracking

## 🗺️ Roadmap

### ✅ **Phase 1: Foundation (Completed)**
- [x] **Multi-LLM Provider Support**: Google Gemini, OpenAI, Claude integration
- [x] **Agent Patterns**: Orchestrator, single-agent, tool-based patterns
- [x] **PostgreSQL Integration**: Short-term memory and session management
- [x] **FastAPI Chat Interface**: REST APIs with comprehensive endpoints
- [x] **Opik Observability**: Agent and tool monitoring, tracing, metrics
- [x] **Security Guardrails**: PII protection, input/output processing
- [x] **Postman Testing**: Complete API testing suite
- [x] **Heroku Deployment**: Production-ready deployment scripts

### 🚧 **Phase 2: Enhanced Capabilities (In Progress)**
- [ ] **Long-term Memory**: OpenSearch integration for RAG capabilities
- [ ] **Agent Caching**: DiceDB integration for high-performance agent caching and session management
- [ ] **Multi-modal Support**: Image, audio, and video processing capabilities for agents
- [ ] **WebSocket APIs**: Real-time communication support
- [ ] **Streaming APIs**: FastAPI streaming for large responses
- [ ] **Prompt Management**: Opik-based prompt versioning and management
- [ ] **Enhanced PII Security**: Advanced data protection mechanisms
- [ ] **React Frontend**: Modern web interface with Vite + TypeScript

### 🌐 **Phase 3: Multi-Cloud Deployment (Planned)**
- [ ] **AWS Deployment**: ECS, Lambda, RDS integration
- [ ] **Google Cloud**: Cloud Run, Cloud SQL, Vertex AI integration
- [ ] **Azure Deployment**: Container Instances, Azure SQL, Azure AI
- [ ] **Kubernetes Support**: Helm charts and K8s manifests
- [ ] **CI/CD Pipelines**: GitHub Actions, GitLab CI, Jenkins

### 🔮 **Phase 4: Advanced Features (Future)**
- [ ] **Multi-Agent Orchestration**: Complex workflow management
- [ ] **Agent Marketplace**: Community agent sharing
- [ ] **Visual Agent Builder**: No-code agent creation
- [ ] **Enterprise Features**: SSO, RBAC, audit logs
- [ ] **Mobile SDKs**: iOS and Android agent integration

## 📚 Documentation

### Setup Guides
- **[Local Development](LOCAL_DEVELOPMENT.md)** - Complete local setup
- **[Heroku Deployment](service_cloud_deploy/heroku/README.md)** - Production deployment
- **[Database Setup](agent_store_deploy/README.md)** - PostgreSQL configuration
- **[API Testing](postman/README.md)** - Postman collection guide

### API Documentation
- **Swagger UI**: `/docs` endpoint
- **ReDoc**: `/redoc` endpoint
- **OpenAPI Spec**: Available at `/openapi.json`

## 🧪 Testing

### Postman Collection
Complete API testing suite with:
- Health checks
- Agent testing scenarios
- Error handling tests
- Performance tests

### Agent Testing
```bash
# Test trip planner agent
curl -X POST "http://localhost:7001/api/agents/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "trip_planner_agent",
    "user_id": "test-user",
    "session_id": "test-session",
    "query": {
      "source": "New York",
      "destination": "Paris"
    }
  }'
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### MIT License Summary
- ✅ **Commercial Use**: Use in commercial projects
- ✅ **Modification**: Modify and distribute
- ✅ **Distribution**: Share and redistribute
- ✅ **Private Use**: Use in private projects
- ❌ **Liability**: No warranty provided
- ❌ **Warranty**: No warranty provided

## 🙏 Acknowledgments

- **Google ADK** for the agent framework
- **FastAPI** for the web framework
- **Opik** for observability
- **Heroku** for deployment
- **PostgreSQL** for data persistence
- **[MichaelisTrofficus](https://github.com/MichaelisTrofficus)** for inspiration
- **[iusztinpaul](https://github.com/iusztinpaul)** for inspiration

**Built with ❤️ for the AI community**

*Ready to build your next AI agent product? Fork this repository and start building!*