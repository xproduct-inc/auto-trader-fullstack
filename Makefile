.PHONY: help setup install clean lint test run migrate docker-up docker-down infra-up infra-down dev setup-backtest-data validate-backtest-data test-market-observer test-strategy-generator test-risk-manager run-all-agent-tests

# Variables
PYTHON = poetry run python
PYTEST = poetry run pytest
ALEMBIC = poetry run alembic
DOCKER_COMPOSE = docker compose
PYTHONPATH = PYTHONPATH=.

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

setup: ## Initial project setup
	@echo "Setting up project..."
	# Install poetry if not installed
	@command -v poetry >/dev/null 2>&1 || { echo "Installing poetry..."; curl -sSL https://install.python-poetry.org | python3 -; }
	# Configure poetry to create virtual environment in project directory
	poetry config virtualenvs.in-project true
	# Generate lock file
	poetry lock --no-update
	# Install dependencies
	poetry install
	# Create necessary directories
	mkdir -p logs
	mkdir -p grafana/provisioning
	mkdir -p backups
	# Copy environment files
	cp .env.example .env
	cp .env.test .env.local
	# Create initial directories for the project
	mkdir -p src/api/v1/endpoints
	mkdir -p src/core
	mkdir -p src/db/models
	mkdir -p src/services
	mkdir -p src/schemas
	mkdir -p src/agents
	mkdir -p src/utils
	mkdir -p tests/test_api
	@echo "Setup complete! Don't forget to update your .env file with your API keys and configurations"
	@echo "Next steps:"
	@echo "1. Update .env with your configuration"
	@echo "2. Run 'make infra-up' to start infrastructure services"
	@echo "3. Run 'make migrate' to initialize the database"
	@echo "4. Run 'make dev' to start the development server"

install: ## Install dependencies
	poetry install

update: ## Update dependencies
	poetry update

clean: ## Clean up temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf logs/*

format: ## Format code
	poetry run black .
	poetry run isort .

lint: ## Run linters
	poetry run ruff check .
	poetry run black --check .
	poetry run isort --check-only .
	poetry run mypy .

test: ## Run tests
	$(PYTEST) --cov=src tests/ -v

create-migration: ## Create a new migration (usage: make create-migration message="migration message")
	$(ALEMBIC) revision --autogenerate -m "$(message)"

migrate: ## Run all migrations
	$(ALEMBIC) upgrade head

migrate-down: ## Rollback last migration
	$(ALEMBIC) downgrade -1

docker-build: ## Build docker images
	$(DOCKER_COMPOSE) build

docker-up: ## Start all services
	$(DOCKER_COMPOSE) up -d

docker-down: ## Stop all services
	$(DOCKER_COMPOSE) down

docker-logs: ## View logs
	$(DOCKER_COMPOSE) logs -f

start-dev: ## Start development server
	$(PYTHONPATH) $(PYTHON) -m uvicorn src.main:app --reload --host 0.0.0.0 --port 9000

start-prod: ## Start production server
	$(PYTHONPATH) $(PYTHON) -m uvicorn src.main:app --host 0.0.0.0 --port 9000 --workers 4

db-shell: ## Open database shell
	$(DOCKER_COMPOSE) exec db psql -U postgres -d trading_db

redis-shell: ## Open Redis shell
	$(DOCKER_COMPOSE) exec redis redis-cli

init-db: ## Initialize database with initial data
	$(PYTHON) scripts/init_db.py

backup-db: ## Backup database
	@mkdir -p backups
	$(DOCKER_COMPOSE) exec db pg_dump -U postgres trading_db > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db: ## Restore database from backup (usage: make restore-db file=backups/backup_file.sql)
	$(DOCKER_COMPOSE) exec -T db psql -U postgres trading_db < $(file)

check-services: ## Check if all services are running
	@echo "Checking services..."
	@curl -s http://localhost:8000/health || echo "API is not running"
	@echo "\nChecking Prometheus..."
	@curl -s http://localhost:9090/-/healthy || echo "Prometheus is not running"
	@echo "\nChecking Grafana..."
	@curl -s http://localhost:3000/api/health || echo "Grafana is not running"

generate-docs: ## Generate API documentation
	$(PYTHON) scripts/generate_docs.py 

infra-up: ## Start infrastructure services
	$(DOCKER_COMPOSE) up -d

infra-down: ## Stop infrastructure services
	$(DOCKER_COMPOSE) down

dev: infra-up ## Start development environment
	@echo "Starting infrastructure services..."
	@sleep 5  # Wait for services to be ready
	@echo "Starting API server..."
	$(PYTHONPATH) $(PYTHON) -m uvicorn src.main:app --reload --host 0.0.0.0 --port 9000

setup-backtest-data: ## Collect and prepare historical data for backtesting
	@echo "Setting up backtesting data..."
	$(PYTHON) -m src.backtesting.data_collector \
		--config config/backtest_data.yml \
		--output data/historical

validate-backtest-data: ## Validate collected data quality
	$(PYTHON) -m src.backtesting.data_validator \
		--data data/historical \
		--config config/backtest_data.yml

test-market-observer: ## Test Market Observer agent
	$(PYTHON) -m src.backtesting.run_agent_tests --agent market_observer

test-strategy-generator: ## Test Strategy Generator agent
	$(PYTHON) -m src.backtesting.run_agent_tests --agent strategy_generator

test-risk-manager: ## Test Risk Manager agent
	$(PYTHON) -m src.backtesting.run_agent_tests --agent risk_manager

run-all-agent-tests: ## Run all agent tests
	$(PYTHON) -m src.backtesting.run_agent_tests