# 🛠️ Development Setup Script

#!/bin/bash

# Setup development environment for AI Benchmark Service

set -e

echo "🚀 Setting up AI Benchmark Service development environment..."

# Check if running on supported OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Detected macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Detected Linux"
else
    echo "❌ Unsupported OS: $OSTYPE"
    exit 1
fi

# Check for required tools
echo "🔍 Checking for required tools..."

REQUIRED_TOOLS=("python3" "pip3" "docker" "docker-compose" "git")
MISSING_TOOLS=()

for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! command -v "$tool" &> /dev/null; then
        MISSING_TOOLS+=("$tool")
    fi
done

if [ ${#MISSING_TOOLS[@]} -ne 0 ]; then
    echo "❌ Missing required tools: ${MISSING_TOOLS[*]}"
    echo "Please install the missing tools and try again."
    exit 1
fi

echo "✅ All required tools found!"

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install development dependencies
echo "🔧 Installing development tools..."
pip install pytest pytest-cov pytest-asyncio black flake8 mypy bandit safety

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs grafana/provisioning prometheus

# Copy example environment file
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️ Please update .env with your actual API keys and configuration"
fi

# Build Docker images
echo "🐳 Building Docker images..."
docker-compose build

# Start services
echo "🚀 Starting development services..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "🔍 Checking service status..."
docker-compose ps

echo "🎉 Development environment setup complete!"
echo ""
echo "Available commands:"
echo "  make dev        - Start development environment"
echo "  make test       - Run all tests"
echo "  make dev-logs   - View development logs"
echo "  make dev-down   - Stop development environment"
echo ""
echo "API endpoints:"
echo "  http://localhost:8000          - Main API"
echo "  http://localhost:8000/docs     - API Documentation"
echo "  http://localhost:3000          - Grafana (admin/admin)"
echo "  http://localhost:9090          - Prometheus"
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"