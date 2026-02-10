# Installation (Local Development)

This guide is for developers who want to run AgentShip locally without Docker.

> **💡 New to AgentShip?** Start with [Docker Setup](../docker-setup.md) - it's much easier!

## Prerequisites

- Python 3.13+
- pipenv (recommended) or pip
- PostgreSQL (optional, for persistent sessions)
- At least one LLM API key (OpenAI, Google, or Anthropic)

## Quick Setup

### Automated Setup (Recommended)

```bash
git clone https://github.com/harshuljain13/ship-ai-agents.git
cd ship-ai-agents/ai/ai-ecosystem
make setup
```

The setup script will:
- ✅ Check prerequisites (Python, pipenv)
- ✅ Install all dependencies
- ✅ Create `.env` file from template
- ✅ Optionally set up PostgreSQL
- ✅ Verify installation

### Manual Setup

If you prefer manual setup:

```bash
# 1. Clone and navigate
git clone https://github.com/harshuljain13/ship-ai-agents.git
cd ship-ai-agents/ai/ai-ecosystem

# 2. Install dependencies
pipenv install --dev

# 3. Configure environment
cp env.example .env
# Edit .env and add your API keys (at least one LLM provider)
```

## Configure Environment

Edit `.env` with your API keys:

```bash
# Required: At least one LLM provider
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional: Database for persistent session management
AGENT_SESSION_STORE_URI=postgresql://user:password@host:port/database

# Optional: Observability
OPIK_API_KEY=your_opik_api_key
OPIK_WORKSPACE=your_workspace
```

See [Configuration Guide](configuration.md) for all environment variables.

## Set Up Database (Optional)

For persistent session storage, set up PostgreSQL:

### Using Setup Script

```bash
cd agent_store_deploy
./setup_local_postgres.sh
cd ..
```

### Manual Setup

```bash
# Install PostgreSQL (macOS)
brew install postgresql
brew services start postgresql

# Create database and user
createdb ai_agents_session_store
psql ai_agents_session_store -c "CREATE USER ai_agents_user WITH PASSWORD 'ai_agents_password';"
psql ai_agents_session_store -c "GRANT ALL PRIVILEGES ON DATABASE ai_agents_session_store TO ai_agents_user;"
```

For production deployment, see the [Deployment Guide](../deployment/overview.md).

## Verify Installation

Start the service:

```bash
make dev
# or: pipenv run uvicorn src.service.main:app --reload --port 7001
```

Access the API documentation:
- **Swagger UI**: http://localhost:7001/swagger
- **ReDoc**: http://localhost:7001/redoc
- **Health Check**: http://localhost:7001/health

## Development Commands

```bash
make help          # Show all available commands
make dev           # Start development server
make test          # Run tests
make test-cov      # Run tests with coverage
make lint          # Run linters
make format        # Format code
make type-check    # Run type checking
```

## Troubleshooting

### Port Already in Use

```bash
# Kill process using port 7001
lsof -ti:7001 | xargs kill -9
```

### Database Connection Failed

- Check if PostgreSQL is running: `brew services list | grep postgresql`
- Verify connection string in `.env`
- Check database exists: `psql -l | grep ai_agents_session_store`

### Import Errors

```bash
# Ensure you're in the virtual environment
pipenv shell

# Reinstall dependencies
pipenv install --dev
```

### API Key Issues

- Verify at least one API key is set in `.env`
- Check key is valid and has sufficient credits
- Test with a simple curl request

## Session Storage

### In-Memory Sessions (Default)

- Sessions stored in memory
- Lost when service restarts
- Good for development and testing

### Database Sessions (Optional)

- Sessions persisted to PostgreSQL
- Survive service restarts
- Set `AGENT_SESSION_STORE_URI` in `.env`

## Next Steps

- Follow the [Quick Start Guide](quickstart.md) to create your first agent
- Read the [Configuration Guide](configuration.md) for advanced settings
- Learn about [Building Agents](../building-agents/overview.md)
