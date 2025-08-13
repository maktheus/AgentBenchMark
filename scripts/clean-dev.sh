# 🧹 Clean Development Environment

#!/bin/bash

# Clean development environment for AI Benchmark Service

echo "🧹 Cleaning AI Benchmark Service development environment..."

# Stop services
echo "⏹ Stopping Docker services..."
docker-compose down -v --remove-orphans

# Remove Docker images
echo "🗑 Removing Docker images..."
docker-compose down --rmi all

# Clean volumes
echo "🗂 Cleaning Docker volumes..."
docker volume prune -f

# Remove Python cache
echo "🐍 Cleaning Python cache..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
rm -rf .mypy_cache htmlcov

# Remove virtual environment
echo "💥 Removing virtual environment..."
rm -rf venv

# Clean data directories
echo "📂 Cleaning data directories..."
rm -rf data/* logs/*

echo "✅ Development environment cleaned!"
echo ""
echo "To set up again: make setup"