# Heroku Deployment

## Quick Deploy

```bash
cd service_cloud_deploy/heroku
./deploy_heroku.sh
```

The deployment script handles:
- Database setup
- Environment variable configuration
- Application deployment
- Health check verification

## Manual Deployment

### 1. Create Heroku App

```bash
heroku create your-app-name
```

### 2. Add PostgreSQL

```bash
heroku addons:create heroku-postgresql:mini
```

### 3. Set Environment Variables

```bash
heroku config:set OPENAI_API_KEY=your_key
heroku config:set SESSION_STORE_URI=$(heroku config:get DATABASE_URL)
```

### 4. Deploy

```bash
git push heroku main
```

## Post-Deployment

- API Documentation: `https://your-app-name.herokuapp.com/docs`
- Health Check: `https://your-app-name.herokuapp.com/health`

## Monitoring

Monitor logs:

```bash
heroku logs --tail
```
