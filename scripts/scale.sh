# 📁 scripts/scale.sh

#!/bin/bash

# Scale script for AI Benchmark Service

set -e

echo "⚖️ Scaling AI Benchmark Service..."

# Check if replicas count is provided
if [ $# -eq 0 ]; then
    echo "❌ Usage: $0 <replicas>"
    echo "Example: $0 5"
    echo ""
    echo "Current replica count:"
    kubectl get deployment/benchmark-service -n benchmark-service -o jsonpath='{.spec.replicas}'
    exit 1
fi

REPLICAS=$1
NAMESPACE="benchmark-service"

# Show current status
echo "🔍 Current deployment status:"
kubectl get deployment/benchmark-service -n $NAMESPACE

# Scale deployment
echo "🔄 Scaling deployment to $REPLICAS replicas..."
kubectl scale deployment/benchmark-service -n $NAMESPACE --replicas=$REPLICAS

# Wait for scaling to complete
echo "⏳ Waiting for scaling to complete..."
kubectl rollout status deployment/benchmark-service -n $NAMESPACE --timeout=300s

# Check service status
echo "🔍 Checking service status..."
kubectl get pods -n $NAMESPACE
kubectl get deployment/benchmark-service -n $NAMESPACE

echo "✅ Scaling completed successfully!"