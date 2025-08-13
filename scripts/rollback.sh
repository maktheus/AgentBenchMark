# 📁 scripts/rollback.sh

#!/bin/bash

# Rollback script for AI Benchmark Service

set -e

echo "⏪ Rolling back AI Benchmark Service..."

# Check if revision is provided
if [ $# -eq 0 ]; then
    echo "❌ Usage: $0 <revision_number>"
    echo "Example: $0 3"
    echo ""
    echo "Available revisions:"
    kubectl rollout history deployment/benchmark-service -n benchmark-service
    exit 1
fi

REVISION=$1
NAMESPACE="benchmark-service"

# Show current status
echo "🔍 Current deployment status:"
kubectl get deployment/benchmark-service -n $NAMESPACE

# Perform rollback
echo "🔄 Rolling back to revision $REVISION..."
kubectl rollout undo deployment/benchmark-service -n $NAMESPACE --to-revision=$REVISION

# Wait for rollback to complete
echo "⏳ Waiting for rollback to complete..."
kubectl rollout status deployment/benchmark-service -n $NAMESPACE --timeout=600s

# Check service status
echo "🔍 Checking service status..."
kubectl get pods -n $NAMESPACE
kubectl get deployment/benchmark-service -n $NAMESPACE

echo "✅ Rollback completed successfully!"