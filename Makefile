.PHONY: help setup docker-setup docker-up docker-down docker-restart docker-logs docker-build heroku-deploy dev test test-cov lint format type-check clean docs-serve docs-build docs-deploy install install-dev

help: ## Show this help message
	@echo "AgentShip - Available Commands:"
	@echo ""
	@echo "🐳 Docker (Local Development):"
	@echo "  make docker-setup     - First-time setup (builds + starts)"
	@echo "  make docker-up        - Start containers (with hot-reload)"
	@echo "  make docker-down      - Stop containers"
	@echo "  make docker-restart   - Restart containers"
	@echo "  make docker-reload    - Hard reload (down + up, reloads env vars)"
	@echo "  make docker-logs      - View Docker logs"
	@echo "  make docker-build     - Rebuild Docker images"
	@echo ""
	@echo "☁️  Deployment:"
	@echo "  make heroku-deploy     - Deploy to Heroku (one command, includes PostgreSQL)"
	@echo "  make heroku-postgres   - Set up Heroku PostgreSQL only"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup        - Run automated setup script (local development)"
	@echo "  make install      - Install production dependencies"
	@echo "  make install-dev  - Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Start development server (http://localhost:7001)"
	@echo "                      Debug UI available at http://localhost:7001/debug-ui"
	@echo "  make test         - Run all tests"
	@echo "  make test-cov     - Run tests with coverage report"
	@echo "  make lint         - Run code linters (flake8)"
	@echo "  make format       - Format code with black"
	@echo "  make type-check   - Run type checking with mypy"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs-serve   - Serve documentation locally (http://localhost:8000)"
	@echo "  make docs-build   - Build documentation site"
	@echo "  make docs-deploy  - Deploy documentation to GitHub Pages"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean        - Clean temporary files and caches"
	@echo ""

docker-setup: ## One-command Docker setup (recommended)
	@echo "🐳 Running Docker setup..."
	@chmod +x scripts/setup/docker-setup.sh
	@./scripts/setup/docker-setup.sh

docker-up: ## Start Docker containers (with hot-reload)
	@docker compose up -d || docker-compose up -d

docker-down: ## Stop Docker containers
	@docker compose down || docker-compose down

docker-restart: ## Restart Docker containers
	@docker compose restart || docker-compose restart

docker-reload: ## Hard reload containers (down + up, reloads environment variables)
	@echo "🔄 Hard reloading Docker containers..."
	@docker compose down && docker compose up -d || docker-compose down && docker-compose up -d

docker-logs: ## View Docker logs
	@docker compose logs -f || docker-compose logs -f

docker-build: ## Rebuild Docker images
	@docker compose build --no-cache || docker-compose build --no-cache

heroku-deploy: ## Deploy to Heroku (one command, includes PostgreSQL)
	@echo "☁️  Deploying to Heroku..."
	@chmod +x service_cloud_deploy/heroku/deploy_heroku.sh
	@./service_cloud_deploy/heroku/deploy_heroku.sh

heroku-postgres: ## Set up Heroku PostgreSQL only
	@echo "🐘 Setting up Heroku PostgreSQL..."
	@chmod +x agent_store_deploy/setup_heroku_postgres.sh
	@./agent_store_deploy/setup_heroku_postgres.sh

setup: ## Run automated setup script (local development)
	@echo "🚀 Running AgentShip setup..."
	@chmod +x scripts/setup/setup.sh
	@./scripts/setup/setup.sh

install: ## Install production dependencies
	pipenv install

install-dev: ## Install development dependencies
	pipenv install --dev

dev: ## Start development server
	@echo "🚀 Starting AgentShip development server..."
	@echo "📚 API docs will be available at http://localhost:7001/docs"
	@echo "🔄 Server will auto-reload on code changes"
	@echo ""
	pipenv run uvicorn src.service.main:app --reload --host 0.0.0.0 --port 7001

test: ## Run all tests
	pipenv run pytest tests/ -v

test-memory: ## Run memory optimization tests
	pipenv run pytest tests/unit/test_memory_optimizations.py -v

test-cov: ## Run tests with coverage
	pipenv run pytest tests/ --cov=src --cov-report=html --cov-report=term
	@echo ""
	@echo "📊 Coverage report generated in htmlcov/index.html"

test-docker: ## Test memory optimizations in Docker (512MB limit)
	@chmod +x scripts/test_memory_docker.sh
	@./scripts/test_memory_docker.sh

lint: ## Run code linters
	@echo "🔍 Running linters..."
	pipenv run flake8 src/ tests/ --max-line-length=120 --exclude=__pycache__,*.pyc

format: ## Format code with black
	@echo "🎨 Formatting code with black..."
	pipenv run black src/ tests/

type-check: ## Run type checking
	@echo "🔎 Running type checks..."
	pipenv run mypy src/ --ignore-missing-imports || true

clean: ## Clean temporary files and caches
	@echo "🧹 Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "✅ Clean complete"

docs-serve: ## Serve Sphinx documentation locally
	cd docs_sphinx && pipenv run sphinx-autobuild source build/html --host 0.0.0.0 --port 8000

docs-build: ## Build Sphinx documentation
	cd docs_sphinx && pipenv run sphinx-build -b html source build/html

docs-html: docs-build ## Alias for docs-build
	@echo "📚 Documentation built in docs_sphinx/build/html/"

docs-clean: ## Clean Sphinx build files
	rm -rf docs_sphinx/build/*
	rm -rf docs_sphinx/source/_build
