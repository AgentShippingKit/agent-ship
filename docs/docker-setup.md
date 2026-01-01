# Docker Setup

**The easiest way to get started** - one command and everything is set up!

## Why Docker?

- ✅ **No Python installation needed** - Everything runs in containers
- ✅ **No pipenv setup** - Dependencies are pre-installed
- ✅ **PostgreSQL included** - Database runs automatically
- ✅ **Consistent environment** - Works the same on all machines
- ✅ **One command setup** - `make docker-setup` and you're done!

## Prerequisites

- **Docker Desktop** (macOS/Windows) or **Docker Engine** (Linux)
  - Download: https://www.docker.com/products/docker-desktop
- **Git** (to clone the repository)

That's it! No Python, pipenv, or PostgreSQL installation needed.

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/harshuljain13/ship-ai-agents.git
cd ship-ai-agents/ai/ai-ecosystem
make docker-setup
```

The script will:
1. Check Docker installation
2. Create `.env` file from template
3. Configure database connection for Docker
4. Build Docker images
5. Start all services (API + PostgreSQL)
6. Wait for services to be ready

### 2. Add API Keys

Edit `.env` and add at least one LLM API key:

```bash
nano .env
# or use your preferred editor
```

Add your keys:
```env
OPENAI_API_KEY=your-actual-key-here
# or
GOOGLE_API_KEY=your-actual-key-here
# or
ANTHROPIC_API_KEY=your-actual-key-here
```

### 3. Restart if Needed

If you added keys after starting:

```bash
make docker-down
make docker-up
```

### 4. Access the API

Open in your browser:
- **API Docs**: http://localhost:7001/docs
- **ReDoc**: http://localhost:7001/redoc
- **Health Check**: http://localhost:7001/health

## Docker Commands

### Using Make (Recommended)

```bash
make docker-setup   # One-command setup
make docker-up      # Start containers
make docker-down    # Stop containers
make docker-logs    # View logs (follow mode)
make docker-build   # Rebuild images
```

### Using Docker Compose Directly

```bash
docker compose up -d          # Start in background
docker compose down           # Stop containers
docker compose logs -f        # View logs
docker compose ps             # View status
docker compose restart        # Restart services
docker compose build          # Rebuild images
```

## Container Details

### Services

1. **agentship** (API Service)
   - Port: `7001`
   - Health check: `/health`
   - Auto-restart: Yes
   - Hot-reload: Source code is mounted for development

2. **postgres** (Database)
   - Port: `5432` (exposed for local access)
   - Database: `ai_agents_store`
   - User: `ai_agents_user`
   - Password: `ai_agents_password`
   - Data persistence: Volume `postgres_data`

### Environment Variables

The `.env` file is automatically loaded. Key variables:

```env
# Required: At least one LLM provider
OPENAI_API_KEY=your-key
GOOGLE_API_KEY=your-key
ANTHROPIC_API_KEY=your-key

# Database (automatically configured for Docker)
AGENT_SESSION_STORE_URI=postgresql://ai_agents_user:ai_agents_password@postgres:5432/ai_agents_store
```

**Note:** The database connection string uses `postgres` as the hostname (Docker service name), not `localhost`.

## Troubleshooting

### Containers won't start

```bash
# Check logs
make docker-logs

# Check status
docker compose ps

# Rebuild from scratch
make docker-down
make docker-build
make docker-up
```

### Port already in use

If port 7001 or 5432 is already in use, change ports in `docker-compose.yml`:

```yaml
ports:
  - "7002:7001"  # Use 7002 instead
```

### Clean slate

To start completely fresh:

```bash
# Stop and remove everything
make docker-down
docker volume rm agentship_postgres_data  # Remove database data
docker system prune -f                     # Clean up

# Start again
make docker-setup
```

## Next Steps

- Follow the [Quick Start Guide](getting-started/quickstart.md) to create your first agent
- Read the [Installation Guide](getting-started/installation.md) for local development
- Check out [Deployment Guide](deployment/overview.md) for production

