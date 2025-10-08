# Ship AI Agents - Heroku Deployment

This directory contains scripts and documentation for deploying the AI Agents service to Heroku.

## 📁 Files

- `deploy_heroku.sh` - Main deployment script for the AI Agents service
- `README.md` - This file

## 🚀 Quick Deploy

```bash
# Deploy the AI Agents service to Heroku
./deploy_heroku.sh
```

## 🔧 Prerequisites

1. **Heroku CLI** installed and logged in
   ```bash
   heroku login
   ```

2. **Git repository** initialized
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

3. **Environment variables** configured in `.env` file
   - At least one API key: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `GOOGLE_API_KEY`
   - Optional: `LOG_LEVEL`, `ENVIRONMENT`

## 📊 App Information

- **App Name**: `ai-agents-alpha`
- **URL**: `https://your-app-name.herokuapp.com/` (replace with your actual URL)
- **Plan**: Eco (512MB memory)
- **Database**: PostgreSQL (essential-0 plan)

## 🔍 Debugging Commands

### Check App Status
```bash
# Check if app is running
heroku ps --app ai-agents-alpha

# Check app info
heroku apps:info --app ai-agents-alpha
```

### View Logs
```bash
# View recent logs
heroku logs --app ai-agents-alpha --num 50

# Follow logs in real-time
heroku logs --tail --app ai-agents-alpha
```

### Check Environment Variables
```bash
# View all environment variables
heroku config --app ai-agents-alpha

# Check specific variable
heroku config:get SESSION_STORE_URI --app ai-agents-alpha
```

### Database Operations
```bash
# Connect to PostgreSQL database
heroku pg:psql --app ai-agents-alpha

# Check database info
heroku addons:info heroku-postgresql --app ai-agents-alpha

# View database tables
heroku pg:psql --app ai-agents-alpha -c "\dt"
```

### Restart App
```bash
# Restart the app
heroku restart --app ai-agents-alpha

# Restart specific dyno
heroku restart web.1 --app ai-agents-alpha
```

## 🛠️ Common Issues & Solutions

### 1. Memory Quota Exceeded (R14 Error)
**Problem**: App using more than 512MB memory
**Solution**: 
- Upgrade to Basic plan: `heroku ps:scale web=1:basic --app ai-agents-alpha`
- Or optimize memory usage in code

### 2. Logging Configuration Error
**Problem**: `ValueError: Unable to configure handler 'file'`
**Solution**: Already fixed - Heroku uses console logging only

### 3. Database Connection Issues
**Problem**: `Database related module not found`
**Solution**: 
- Check if `psycopg2-binary` is in requirements.txt
- Verify `SESSION_STORE_URI` is set correctly

### 4. App Won't Start
**Problem**: App crashes on startup
**Solution**:
```bash
# Check logs for errors
heroku logs --app ai-agents-alpha --num 100

# Check if all dependencies are installed
heroku run pip list --app ai-agents-alpha
```

## 🔄 Redeploy

```bash
# Make changes and redeploy
git add .
git commit -m "Your changes"
git push heroku main
```

## 📈 Monitoring

### Health Check
```bash
# Test health endpoint
curl https://your-app-name.herokuapp.com/health

# Expected response: {"status":"running"}
```

### API Documentation
- **Swagger UI**: `https://your-app-name.herokuapp.com/docs`
- **ReDoc**: `https://your-app-name.herokuapp.com/redoc`

## 🗄️ Database Setup

The PostgreSQL database is set up separately using the agent store deployment scripts:

```bash
# Set up PostgreSQL storage
cd ../../agent_store_deploy
./setup_heroku_postgres.sh
```

## 📝 Environment Variables

### Required
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key  
- `GOOGLE_API_KEY` - Google API key
- `SESSION_STORE_URI` - PostgreSQL connection string (set automatically)

### Optional
- `LOG_LEVEL` - Logging level (default: INFO)
- `ENVIRONMENT` - Environment name (default: production)

## 🔗 Related Documentation

- [Main README](../../README.md) - High-level architecture
- [Local Development](../../LOCAL_DEVELOPMENT.md) - Local setup guide
- [Agent Store Deploy](../../agent_store_deploy/README.md) - PostgreSQL setup
- [Postman Collection](../../postman/README.md) - API testing guide