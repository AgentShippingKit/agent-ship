# Ship AI Agents - Local Development

This guide covers setting up and running the AI Agents service locally for development.

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.13+
- pipenv (recommended) or pip
- PostgreSQL (optional, for persistent sessions)

### 2. Clone and Setup
```bash
git clone <repository-url>
cd ai-agents
pipenv install
pipenv shell
```

### 3. Environment Configuration
```bash
# Copy environment template
cp env.example .env

# Edit .env with your API keys
# At least one API key is required:
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-key

# Optional: PostgreSQL for persistent sessions
SESSION_STORE_URI=postgresql://ai_agents_user:ai_agents_password@localhost:5432/ai_agents_session_store
```

### 4. Run the Service
```bash
# Start the development server
pipenv run uvicorn src.service.main:app --reload --host 0.0.0.0 --port 7001
```

The service will be available at: http://localhost:7001

## 🗄️ Database Setup (Optional)

For persistent session storage, set up PostgreSQL:

### Using Setup Script
```bash
cd agent_store_deploy
./setup_local_postgres.sh
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

## 🔧 Development Commands

### Run Tests
```bash
pipenv run pytest
```

### Code Formatting
```bash
pipenv run black src/
pipenv run flake8 src/
```

### Type Checking
```bash
pipenv run mypy src/
```

### Install Dependencies
```bash
# Install all dependencies
pipenv install

# Install development dependencies
pipenv install --dev

# Add new dependency
pipenv install package-name
```

## 🧪 Testing the API

### Health Check
```bash
curl http://localhost:7001/health
```

### Agent Chat
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

### API Documentation
- **Swagger UI**: http://localhost:7001/docs
- **ReDoc**: http://localhost:7001/redoc

## 🏗️ Project Structure

```
ai-agents/
├── src/
│   ├── agents/           # Agent implementations
│   ├── service/          # FastAPI service
│   ├── configs/          # Configuration files
│   └── models/           # Data models
├── agent_store_deploy/   # Database setup scripts
├── service_cloud_deploy/ # Deployment scripts
├── postman/             # API testing collection
└── tests/               # Test files
```

## 🔍 Debugging

### Enable Debug Logging
```bash
# Set in .env file
LOG_LEVEL=DEBUG
```

### View Logs
```bash
# Logs are written to dev_app.log
tail -f dev_app.log
```

### Database Debugging
```bash
# Connect to local PostgreSQL
psql -h localhost -p 5432 -U ai_agents_user -d ai_agents_session_store

# Check session tables
\dt
SELECT * FROM sessions LIMIT 5;
```

## 🚨 Common Issues

### 1. Port Already in Use
```bash
# Kill process using port 7001
lsof -ti:7001 | xargs kill -9
```

### 2. Database Connection Failed
- Check if PostgreSQL is running: `brew services list | grep postgresql`
- Verify connection string in `.env`
- Check database exists: `psql -l | grep ai_agents_session_store`

### 3. Import Errors
```bash
# Ensure you're in the virtual environment
pipenv shell

# Reinstall dependencies
pipenv install --dev
```

### 4. API Key Issues
- Verify at least one API key is set in `.env`
- Check key is valid and has sufficient credits
- Test with a simple curl request

## 🔄 Session Storage

### In-Memory Sessions (Default)
- Sessions stored in memory
- Lost when service restarts
- Good for development and testing

### Database Sessions (Optional)
- Sessions persisted to PostgreSQL
- Survive service restarts
- Set `SESSION_STORE_URI` in `.env`

## 📚 Related Documentation

- [Main README](README.md) - High-level architecture
- [Heroku Deployment](service_cloud_deploy/heroku/README.md) - Production deployment
- [Agent Store Deploy](agent_store_deploy/README.md) - Database setup
- [Postman Collection](postman/README.md) - API testing
