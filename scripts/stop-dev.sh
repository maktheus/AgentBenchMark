# 🛑 Stop Development Environment

#!/bin/bash

# Stop development environment for AI Benchmark Service

echo "⏹ Stopping AI Benchmark Service development environment..."

# Stop services
echo "🐳 Stopping Docker services..."
docker-compose down

echo "✅ Development environment stopped!"
echo ""
echo "To start again: make dev"
echo "To clean everything: make clean"