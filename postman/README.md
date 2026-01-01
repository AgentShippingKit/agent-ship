# AgentShip - API Testing with Postman

This directory contains Postman collections and environments for testing the AI Agents API with organized agent folders.

## 📁 Files

- `AgentsAPI.postman_collection.json` - API collection with organized agent folders
- `Ship_AI_Agents_Environment.postman_environment.json` - Environment variables
- `README.md` - This file

## 🗂️ Collection Organization

The collection is organized into folders for better testing:

### 📋 General Endpoints
- **Health Check** - Service status
- **Root Endpoint** - Welcome message  
- **API Documentation** - Swagger docs

### 🏥 Medical Followup Agent
- **Basic Chat - Chest Pain** - Simple medical case
- **Simple Case - Headache** - Basic headache scenario
- **Complex Case - Shortness of Breath** - Multi-turn conversation
- **Emergency Case - Severe Chest Pain** - Critical medical scenario

### 🗺️ Trip Planner Agent
- **Plan Trip - New York to Paris** - International trip planning
- **Plan Trip - London to Tokyo** - Long-distance trip planning

### 🌐 Translation Agent
- **Translate English to Spanish** - Basic translation
- **Translate French to English** - Reverse translation

### ✈️ Flight Agent
- **Search Flights - NYC to LAX** - Flight search and booking

### 🏨 Hotel Agent
- **Search Hotels - Paris** - Hotel search and booking

### 📋 Summary Agent
- **Summarize Trip Plan** - Trip plan summarization

### 🗄️ Database Agent
- **List Tables** - Show available database tables
- **Get Table Schema - Users** - Display table structure
- **Query Table - Products** - Retrieve table records
- **Search Records - Find User** - Search specific records
- **Get Table Statistics - Orders** - Table analytics
- **Complex Query - Product Analysis** - Advanced database operations

### ❌ Error Tests
- **Invalid Agent** - Test with non-existent agent
- **Missing Required Fields** - Test validation
- **Invalid JSON** - Test malformed requests

## 🚀 Quick Start

### 1. Import Collection
1. Open Postman
2. Click "Import" button
3. Select `AgentsAPI.postman_collection.json`
4. Select `Ship_AI_Agents_Environment.postman_environment.json`

### 2. Set Environment
1. Click the environment dropdown (top right)
2. Select "AgentShip Environment"
3. Verify variables are set correctly

### 3. Test API
1. Select any request from the collection
2. Click "Send"
3. Check the response

## 🌐 Environments

### Local Development
- **Base URL**: `http://localhost:7001`
- **Health Check**: `http://localhost:7001/health`
- **API Docs (Swagger)**: `http://localhost:7001/swagger`
- **API Docs (ReDoc)**: `http://localhost:7001/redoc`
- **Framework Docs**: `http://localhost:7001/docs` (after building with `mkdocs build`)

### Production
- **Base URL**: `https://your-production-url.herokuapp.com` (replace with your actual production URL)
- **Health Check**: `https://your-production-url.herokuapp.com/health`
- **API Docs (Swagger)**: `https://your-production-url.herokuapp.com/swagger`
- **API Docs (ReDoc)**: `https://your-production-url.herokuapp.com/redoc`
- **Framework Docs**: `https://your-production-url.herokuapp.com/docs` (if deployed)

## 📋 Available Endpoints

### Health Check
- **GET** `/health`
- **Description**: Check if the service is running
- **Response**: `{"status": "running"}`

### Agent Chat
- **POST** `/api/agents/chat`
- **Description**: Chat with AI agents
- **Body**: JSON with agent_name, user_id, session_id, query, features

### Root
- **GET** `/`
- **Description**: Welcome message
- **Response**: `{"message": "Welcome to the AgentShip API!"}`

## 🔧 Environment Variables

### Base URLs
- `base_url` - Local development URL
- `base_url_production` - Production URL

### Test Data
- `user_id` - Test user ID (default: "user-123")
- `session_id` - Test session ID (default: "session-456")
- `agent_name` - Agent to test (default: "medical_followup")

## 📝 Sample Requests

### Health Check
```http
GET {{base_url}}/health
```

### Agent Chat - Medical Followup
```json
{
  "agent_name": "medical_followup",
  "user_id": "user-123",
  "session_id": "session-456",
  "query": [
    {
      "speaker": "Patient",
      "text": "I have chest pain"
    },
    {
      "speaker": "Doctor", 
      "text": "Can you describe it?"
    },
    {
      "speaker": "Patient",
      "text": "It's a sharp, stabbing pain that started after lifting heavy boxes"
    }
  ],
  "features": [
    {
      "feature_name": "max_followups",
      "feature_value": 5
    }
  ]
}
```

### Agent Chat - Trip Planner Agent
```json
{
  "agent_name": "trip_planner_agent",
  "user_id": "user-123",
  "session_id": "session-456",
  "query": {
    "source": "New York",
    "destination": "Paris"
  },
  "features": []
}
```

### Agent Chat - Translation Agent
```json
{
  "agent_name": "translation_agent",
  "user_id": "user-123",
  "session_id": "session-456",
  "query": {
    "text": "Hello, how are you?",
    "from_language": "en",
    "to_language": "es"
  },
  "features": []
}
```

### Agent Chat - Database Agent
```json
{
  "agent_name": "database",
  "user_id": "user-123",
  "session_id": "session-456",
  "query": "What tables are available in the database?",
  "features": []
}
```

### Database Agent - Complex Query
```json
{
  "agent_name": "database",
  "user_id": "user-123",
  "session_id": "session-456",
  "query": "Show me all electronics products and their details",
  "features": []
}
```

## 🧪 Testing Scenarios

### 1. Basic Health Check
- Test if service is running
- Should return `{"status": "running"}`

### 2. Medical Followup Agent
- **New Session**: Use a new session_id, should create new session and return followup questions
- **Existing Session**: Use same session_id, should continue conversation
- **Different Cases**: Test various medical scenarios (chest pain, headache, emergency)

### 3. Trip Planner Agent
- **Trip Planning**: Test with different source and destination pairs
- **Complex Routes**: Test multi-city or international trips
- **Date Specifications**: Test with specific travel dates

### 4. Translation Agent
- **Language Pairs**: Test various language combinations
- **Text Length**: Test with short and long text
- **Special Characters**: Test with accented characters

### 5. Flight Agent
- **Route Search**: Test flight searches between different cities
- **Date Flexibility**: Test with flexible date ranges
- **Price Filters**: Test with budget constraints

### 6. Hotel Agent
- **Location Search**: Test hotel searches in different cities
- **Date Ranges**: Test with specific check-in/check-out dates
- **Amenities**: Test with specific hotel requirements

### 7. Summary Agent
- **Trip Summaries**: Test summarization of complex trip plans
- **Key Points**: Verify important details are captured
- **Format**: Test different summary formats

### 8. Database Agent
- **List Tables**: Should return available database tables
- **Schema Queries**: Get table structure and column information
- **Data Queries**: Retrieve records with limits and filters
- **Search Operations**: Find specific records by field values
- **Statistics**: Get table analytics and data insights
- **Complex Queries**: Test natural language database operations

### 9. Error Handling
- Test with invalid agent_name
- Test with malformed request body
- Test missing required fields
- Should return appropriate error messages

## 🔍 Troubleshooting

### Connection Refused
- Check if service is running locally: `curl http://localhost:7001/health`
- Verify environment variables are set correctly
- Check if port 7001 is available

### 404 Not Found
- Verify the endpoint URL is correct
- Check if the service is deployed properly
- Ensure the route exists in the API

### 500 Internal Server Error
- Check service logs for detailed error information
- Verify API keys are set correctly
- Check database connection if using persistent sessions

### Authentication Issues
- Verify API keys are valid and have sufficient credits
- Check if the service is configured correctly
- Ensure environment variables are set

## 📊 Response Examples

### Successful Health Check
```json
{
  "status": "running"
}
```

### Successful Medical Followup Agent Chat
```json
{
  "agent_name": "medical_followup",
  "user_id": "user-123",
  "session_id": "session-456",
  "sender": "SYSTEM",
  "success": true,
  "agent_response": {
    "followup_questions": [
      "Have you experienced any shortness of breath?",
      "Did the pain radiate to your arm or jaw?",
      "Are you experiencing any nausea or sweating?"
    ],
    "count": 3
  }
}
```

### Successful Database Agent Chat
```json
{
  "agent_name": "database",
  "user_id": "user-123",
  "session_id": "session-456",
  "sender": "SYSTEM",
  "success": true,
  "agent_response": "Based on the database query, here are the available tables:\n\n1. **users** - Contains user information (id, name, email, age)\n2. **products** - Contains product catalog (id, name, price, category)\n3. **orders** - Contains order information (id, user_id, product_id, quantity, total)\n\nEach table has sample data that you can query. Would you like me to show you the schema or data from any specific table?"
}
```

### Error Response
```json
{
  "detail": "Agent 'invalid_agent' not found. Available agents: ['medical_followup_agent']"
}
```

## 🔄 Environment Switching

### Switch to Local
1. Select "Ship AI Agents Environment"
2. Ensure `base_url` is set to `http://localhost:7001`
3. Make sure local service is running

### Switch to Production
1. Select "Ship AI Agents Environment"
2. Change `base_url` to your actual production URL (e.g., `https://your-app.herokuapp.com`)
3. Or use `base_url_production` variable

## 📚 Related Documentation

- [Main README](../README.md) - High-level architecture
- [Installation Guide](../docs/getting-started/installation.md) - Local setup guide
- [Heroku Deployment](../service_cloud_deploy/heroku/README.md) - Production deployment
- [Database Setup](../agent_store_deploy/README.md) - Database configuration
