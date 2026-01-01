# Deployment

## Overview

The framework is designed for production deployment with minimal configuration. It includes deployment scripts and guides for popular platforms.

## Supported Platforms

- **[Heroku](heroku.md)**: One-click deployment with PostgreSQL addon
- **Docker**: Containerized deployment for any platform
- **Cloud Run**: Google Cloud deployment (coming soon)
- **AWS**: ECS/Lambda deployment (coming soon)

## Deployment Checklist

- [ ] Set environment variables
- [ ] Configure database connection
- [ ] Set up observability (optional)
- [ ] Configure agent discovery directories
- [ ] Run health checks
- [ ] Monitor logs and metrics

## Environment Variables

Ensure all required environment variables are set in your deployment environment. See [Configuration](../getting-started/configuration.md) for details.

## Health Checks

The framework provides a health check endpoint:

```bash
curl http://your-deployment-url/health
```

## Monitoring

Use Opik integration for production monitoring:

- Request/response tracing
- Performance metrics
- Token usage tracking
- Error logging
