# 📁 scripts/update.sh

#!/bin/bash

# Update script for AI Benchmark Service

set -e

echo "🔄 Updating AI Benchmark Service..."

# Check if running on supported OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Detected macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Detected Linux"
else
    echo "❌ Unsupported OS: $OSTYPE"
    exit 1
fi

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found"
    exit 1
fi

# Check for Kubernetes
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found"
    exit 1
fi

# Build new Docker images
echo "🏗 Building new Docker images..."
docker-compose build

# Push images to registry
echo "⬆️ Pushing images to registry..."
docker push ai-benchmark-service:latest

# Update Kubernetes deployment
echo "♻️ Updating Kubernetes deployment..."
kubectl set image deployment/benchmark-service web=ai-benchmark-service:latest -n benchmark-service

# Wait for rollout to complete
echo "⏳ Waiting for rollout to complete..."
kubectl rollout status deployment/benchmark-service -n benchmark-service --timeout=600s

# Check service status
echo "🔍 Checking service status..."
kubectl get pods -n benchmark-service

echo "✅ Update completed successfully!"