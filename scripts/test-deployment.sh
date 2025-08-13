# 📁 scripts/test-deployment.sh

#!/bin/bash

# Test deployment script for AI Benchmark Service

set -e

echo "🧪 Testing AI Benchmark Service deployment..."

NAMESPACE="benchmark-service"

# Test service connectivity
echo "📡 Testing service connectivity..."
kubectl exec -n $NAMESPACE $(kubectl get pod -n $NAMESPACE -l app=benchmark-service -o jsonpath="{.items[0].metadata.name}") -- \
    curl -f http://localhost:8000/health || echo "❌ Health check failed"

# Test database connectivity
echo "🗄 Testing database connectivity..."
kubectl exec -n $NAMESPACE $(kubectl get pod -n $NAMESPACE -l app=benchmark-service -o jsonpath="{.items[0].metadata.name}") -- \
    pg_isready -h postgres -U benchmark_user || echo "❌ Database connectivity failed"

# Test Redis connectivity
echo "キャッシング Testing Redis connectivity..."
kubectl exec -n $NAMESPACE $(kubectl get pod -n $NAMESPACE -l app=benchmark-service -o jsonpath="{.items[0].metadata.name}") -- \
    redis-cli -h redis ping || echo "❌ Redis connectivity failed"

# Test API endpoints
echo "🌐 Testing API endpoints..."
kubectl exec -n $NAMESPACE $(kubectl get pod -n $NAMESPACE -l app=benchmark-service -o jsonpath="{.items[0].metadata.name}") -- \
    curl -f http://localhost:8000/api/benchmark/list || echo "❌ API endpoints test failed"

# Test benchmark creation
echo "🏁 Testing benchmark creation..."
kubectl exec -n $NAMESPACE $(kubectl get pod -n $NAMESPACE -l app=benchmark-service -o jsonpath="{.items[0].metadata.name}") -- \
    curl -f -X POST http://localhost:8000/api/benchmark/run -H "Content-Type: application/json" -d '{"agents":["gpt-4-turbo"],"benchmark":"mmlu-reasoning-v1"}' || echo "❌ Benchmark creation test failed"

echo "✅ Deployment tests completed!"