# AgentShip Dockerfile
# Multi-stage build for optimized production image

FROM python:3.13-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for building (including PostgreSQL dev libraries for psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv
RUN pip install --no-cache-dir pipenv

# Copy dependency files
COPY Pipfile Pipfile.lock ./

# Install dependencies
RUN pipenv install --deploy --system

# Production stage
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=7001

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder (includes pipenv and all dependencies)
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create non-root user for security (before copying files)
RUN useradd --create-home --shell /bin/bash app

# Copy application code (excludes files in .dockerignore)
COPY --chown=app:app . .

# Explicitly ensure branding folder is copied (must be after COPY . .)
# This ensures branding assets are available even if .dockerignore affects it
COPY --chown=app:app branding/ /app/branding/

# Build Sphinx documentation (if source exists)
# This ensures /docs endpoint serves the built documentation
# Note: All Python packages (including sphinx) are already installed from builder stage
RUN if [ -d "docs_sphinx/source" ]; then \
        cd docs_sphinx && \
        python -m sphinx -b html source build/html || echo "Warning: Sphinx build failed, /docs will show fallback page"; \
    fi

# Ensure app user owns /app directory and can write to it
RUN chown -R app:app /app && chmod -R u+w /app

USER app

# Expose port
EXPOSE 7001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:7001/health || exit 1

# Run the application
CMD ["uvicorn", "src.service.main:app", "--host", "0.0.0.0", "--port", "7001"]

