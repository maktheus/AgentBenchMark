# 🚀 Start Development Environment

#!/bin/bash

# Start development environment for AI Benchmark Service

set -e

echo "🚀 Starting AI Benchmark Service development environment..."

# Check if already running
if docker-compose ps | grep -q "Up"; then
    echo "⚠️ Development environment is already running!"
    echo "Use 'make dev-logs' to view logs or 'make dev-down' to stop."
    exit 0
fi

# Start services
echo "🐳 Starting Docker services..."
docker-compose up --build -d

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 15

# Check service status
echo "🔍 Service status:"
docker-compose ps

echo "🎉 Development environment started!"
echo ""
echo "API endpoints:"
echo "  http://localhost:8000          - Main API"
echo "  http://localhost:8000/docs     - API Documentation"
echo "  http://localhost:3000          - Grafana (admin/admin)"
echo "  http://localhost:9090          - Prometheus"
echo "  http://localhost:8001          - Local Agent"
echo ""
echo "To view logs: make dev-logs"
echo "To stop: make dev-down"