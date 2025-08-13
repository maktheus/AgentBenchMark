# 🧪 Run Tests

#!/bin/bash

# Run tests for AI Benchmark Service

set -e

echo "🧪 Running tests for AI Benchmark Service..."

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Please install it:"
    echo "   pip install pytest pytest-asyncio pytest-cov"
    exit 1
fi

# Run tests with coverage
echo "🔍 Running tests with coverage..."
pytest --cov=benchmark_service --cov-report=html --cov-report=term

echo "✅ Tests completed!"
echo ""
echo "Detailed coverage report available at: htmlcov/index.html"