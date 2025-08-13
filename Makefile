# 🛠️ Makefile for AI Benchmark Service

# Variables
PROJECT_NAME = ai-benchmark-service
PYTHON = python3
PIP = pip3
DOCKER_COMPOSE = docker-compose

# Colors
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

# Help target
.PHONY: help
help:
	@echo "$(BLUE)🚀 $(PROJECT_NAME) - Development Commands$(NC)"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "$(YELLOW)Setup:$(NC)"
	@echo "  setup            Setup development environment"
	@echo "  clean            Clean development environment"
	@echo ""
	@echo "$(YELLOW)Development:$(NC)"
	@echo "  dev              Start development environment"
	@echo "  dev-down         Stop development environment"
	@echo "  dev-logs         Show development logs"
	@echo "  dev-rebuild      Rebuild and restart development environment"
	@echo ""
	@echo "$(YELLOW)Testing:$(NC)"
	@echo "  test             Run all tests"
	@echo "  test-unit        Run unit tests"
	@echo "  test-integration Run integration tests"
	@echo "  test-e2e         Run end-to-end tests"
	@echo "  test-coverage    Run tests with coverage report"
	@echo ""
	@echo "$(YELLOW)Code Quality:$(NC)"
	@echo "  format           Format code with Black"
	@echo "  lint             Lint code with Flake8"
	@echo "  type-check       Type check with MyPy"
	@echo "  security-check   Run security checks"
	@echo "  quality          Run all code quality checks"
	@echo ""
	@echo "$(YELLOW)Database:$(NC)"
	@echo "  db-migrate       Run database migrations"
	@echo "  db-reset         Reset database"
	@echo "  db-backup        Create database backup"
	@echo "  db-restore       Restore database from backup"
	@echo ""
	@echo "$(YELLOW)Deployment:$(NC)"
	@echo "  build            Build Docker images"
	@echo "  push             Push Docker images to registry"
	@echo ""
	@echo "$(YELLOW)Monitoring:$(NC)"
	@echo "  logs             Show application logs"
	@echo "  metrics          Show system metrics"
	@echo "  status           Show service status"

# Setup development environment
.PHONY: setup
setup:
	@echo "$(GREEN)🚀 Setting up development environment...$(NC)"
	@./scripts/setup-dev.sh

# Clean development environment
.PHONY: clean
clean:
	@echo "$(YELLOW)🧹 Cleaning development environment...$(NC)"
	@./scripts/clean-dev.sh

# Start development environment
.PHONY: dev
dev:
	@echo "$(GREEN)🚀 Starting development environment...$(NC)"
	@./scripts/start-dev.sh

# Stop development environment
.PHONY: dev-down
dev-down:
	@echo "$(YELLOW)⏹ Stopping development environment...$(NC)"
	@./scripts/stop-dev.sh

# Show development logs
.PHONY: dev-logs
dev-logs:
	@echo "$(BLUE)📜 Development logs:$(NC)"
	@$(DOCKER_COMPOSE) logs -f

# Rebuild development environment
.PHONY: dev-rebuild
dev-rebuild:
	@echo "$(GREEN)🏗 Rebuilding development environment...$(NC)"
	@$(DOCKER_COMPOSE) down
	@$(DOCKER_COMPOSE) up --build -d

# Run all tests
.PHONY: test
test:
	@echo "$(GREEN)🧪 Running all tests...$(NC)"
	@./scripts/run-tests.sh

# Run unit tests
.PHONY: test-unit
test-unit:
	@echo "$(GREEN)🔬 Running unit tests...$(NC)"
	@$(PYTHON) -m pytest tests/unit/ -v

# Run integration tests
.PHONY: test-integration
test-integration:
	@echo "$(GREEN)🔗 Running integration tests...$(NC)"
	@$(PYTHON) -m pytest tests/integration/ -v

# Run end-to-end tests
.PHONY: test-e2e
test-e2e:
	@echo "$(GREEN)🌐 Running end-to-end tests...$(NC)"
	@$(PYTHON) -m pytest tests/e2e/ -v

# Run tests with coverage
.PHONY: test-coverage
test-coverage:
	@echo "$(GREEN)📊 Running tests with coverage...$(NC)"
	@$(PYTHON) -m pytest --cov=benchmark_service --cov-report=html --cov-report=term

# Format code
.PHONY: format
format:
	@echo "$(GREEN)🎨 Formatting code with Black...$(NC)"
	@$(PYTHON) -m black .

# Lint code
.PHONY: lint
lint:
	@echo "$(GREEN)🧹 Linting code with Flake8...$(NC)"
	@$(PYTHON) -m flake8 .

# Type check
.PHONY: type-check
type-check:
	@echo "$(GREEN)🔍 Type checking with MyPy...$(NC)"
	@$(PYTHON) -m mypy .

# Run security checks
.PHONY: security-check
security-check:
	@echo "$(GREEN)🛡️ Running security checks...$(NC)"
	@$(PIP) install safety bandit
	@safety check -r requirements.txt
	@bandit -r benchmark_service/

# Run all code quality checks
.PHONY: quality
quality: format lint type-check security-check

# Run database migrations
.PHONY: db-migrate
db-migrate:
	@echo "$(GREEN)⬆️ Running database migrations...$(NC)"
	@$(DOCKER_COMPOSE) exec web alembic upgrade head

# Reset database
.PHONY: db-reset
db-reset:
	@echo "$(YELLOW)🔄 Resetting database...$(NC)"
	@$(DOCKER_COMPOSE) exec postgres psql -U benchmark_user -d benchmark_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Create database backup
.PHONY: db-backup
db-backup:
	@echo "$(GREEN)💾 Creating database backup...$(NC)"
	@$(DOCKER_COMPOSE) exec postgres pg_dump -U benchmark_user benchmark_db > backup_$(shell date +%Y%m%d_%H%M%S).sql

# Restore database from backup
.PHONY: db-restore
db-restore:
	@echo "$(YELLOW)🔄 Restoring database from backup...$(NC)"
	@echo "$(RED)⚠️ This will overwrite existing data. Are you sure? (Ctrl+C to cancel)$(NC)"
	@read -p "Press Enter to continue..."
	@$(DOCKER_COMPOSE) exec -T postgres psql -U benchmark_user benchmark_db < backup.sql

# Build Docker images
.PHONY: build
build:
	@echo "$(GREEN)🏗 Building Docker images...$(NC)"
	@$(DOCKER_COMPOSE) build

# Push Docker images to registry
.PHONY: push
push:
	@echo "$(GREEN)⬆️ Pushing Docker images to registry...$(NC)"
	@docker push ai-benchmark-service:latest

# Show application logs
.PHONY: logs
logs:
	@echo "$(BLUE)📜 Application logs:$(NC)"
	@$(DOCKER_COMPOSE) logs -f web

# Show system metrics
.PHONY: metrics
metrics:
	@echo "$(GREEN)📈 System metrics:$(NC)"
	@docker stats --no-stream

# Show service status
.PHONY: status
status:
	@echo "$(BLUE)📊 Service status:$(NC)"
	@$(DOCKER_COMPOSE) ps

# Default target
.DEFAULT_GOAL := help