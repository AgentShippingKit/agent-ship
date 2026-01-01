# Memory Optimization Guide

## Problem

Heroku eco dyno (512MB limit) is using **909MB (177% of limit)**, causing R14 memory quota exceeded errors.

## Root Causes

### 1. Too Many Gunicorn Workers (PRIMARY ISSUE)
- **Default**: Gunicorn spawns `(2 × CPU cores) + 1` workers (typically 4-8)
- **Each worker** loads ALL dependencies (~200-300MB per worker)
- **Total**: 4-8 workers × 250MB = **1-2GB** ❌

### 2. Unused Heavy Dependencies
These Google Cloud libraries are **listed but never used**:
- `google-cloud-aiplatform` (~100-200MB)
- `google-cloud-bigtable` (~50-100MB)
- `google-cloud-spanner` (~50-100MB)
- `sqlalchemy-spanner` (~20-50MB)

**Total wasted**: ~200-400MB per worker

### 3. Heavy Imports at Module Level
Some libraries initialize clients on import, consuming memory even if unused.

## Solutions

### ✅ 1. Fixed Procfile (IMMEDIATE FIX - DEPLOYED)

Updated to use **1 worker** instead of 4-8:
```bash
web: gunicorn src.service.main:app -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:$PORT \
  --workers 1 \              # Single worker for eco dyno
  --threads 4 \              # Use threads for concurrency
  --timeout 120 \            # Prevent hanging requests
  --max-requests 1000 \      # Restart worker periodically
  --max-requests-jitter 100
```

**Expected**: Reduces memory from ~900MB to ~200-300MB (60-75% reduction)

### ✅ 2. Optimized Imports (IMPLEMENTED)

Heavy imports are now lazy-loaded:
- Azure clients only initialized when `AzureUtils` is used
- Google Cloud libraries not imported (they're not used)

### ✅ 3. Removed Unused Dependencies (COMPLETED)

Removed from `Pipfile`:
- `google-cloud-aiplatform` (~100-200MB)
- `google-cloud-bigtable` (~50-100MB)
- `google-cloud-spanner` (~50-100MB)
- `sqlalchemy-spanner` (~20-50MB)

**Expected**: Additional ~200-400MB reduction per worker

**Next step**: Run `pipenv install` to update your local environment

## Deployment Steps

### Step 1: Procfile Fix (Already Done)
```bash
git add Procfile
git commit -m "Fix: Reduce Gunicorn workers to 1"
git push heroku main
```

### Step 2: Update Dependencies (After Removing Unused)
```bash
pipenv install
pipenv lock
git add Pipfile Pipfile.lock
git commit -m "Remove unused Google Cloud dependencies"
git push heroku main
```

## Expected Results

| Stage | Memory | Status |
|-------|--------|--------|
| **Current** | 909MB (177%) | ❌ R14 errors |
| **After Procfile fix** | ~200-300MB (40-60%) | ✅ Should work |
| **After removing deps** | ~150-200MB (30-40%) | ✅ Comfortable |

## Additional Optimizations

### Limit Agent Discovery
Only load needed agents in production:
```bash
heroku config:set AGENT_DIRECTORIES=src/agents/all_agents/health_assistant_agent
```

### Disable Debug UI
```bash
heroku config:set DEBUG_UI_ENABLED=false
```

### Disable Observability (if not using)
```bash
heroku config:set OBS_ENABLED=false
```

## Monitoring

### Check Memory Usage
```bash
# Heroku logs
heroku logs --tail --app your-app-name | grep "Process running mem"

# Health endpoint (includes memory info)
curl https://your-app.herokuapp.com/health
```

### Health Endpoint Response
```json
{
  "status": "running",
  "memory_mb": 234.56,
  "memory_limit_mb": 512.0,
  "within_limit": true,
  "percent_of_limit": 45.8
}
```

## Why This Happened

1. **Gunicorn defaults**: Designed for servers with more memory
2. **Eco dyno limits**: 512MB is tight for Python + ML/AI dependencies
3. **Unused dependencies**: Heavy libraries consume memory even when not used

## Prevention

1. Always specify worker count in Procfile for memory-constrained environments
2. Regularly audit dependencies - remove unused heavy libraries
3. Use lazy imports for optional/heavy dependencies
4. Monitor memory in staging before production

## Future: ELK Stack Integration

For production monitoring, we'll integrate ELK (Elasticsearch, Logstash, Kibana) stack:
- **Elasticsearch**: Store logs and metrics
- **Logstash**: Process and enrich logs
- **Kibana**: Visualize and analyze

This will provide:
- Centralized logging
- Real-time monitoring
- Advanced analytics
- Alerting capabilities

Setup will be documented separately when implemented.
