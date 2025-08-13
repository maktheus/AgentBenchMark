# 📁 scripts/cleanup.sh

#!/bin/bash

# Cleanup script for AI Benchmark Service

set -e

echo "🧹 Cleaning up AI Benchmark Service..."

NAMESPACE="benchmark-service"

# Scale down deployments
echo "⏬ Scaling down deployments..."
kubectl scale deployment/benchmark-service -n $NAMESPACE --replicas=0
kubectl scale deployment/redis -n $NAMESPACE --replicas=0
kubectl scale deployment/postgres -n $NAMESPACE --replicas=0

# Wait for pods to terminate
echo "⏳ Waiting for pods to terminate..."
sleep 30

# Delete completed jobs
echo "🗑 Deleting completed jobs..."
kubectl delete jobs --field-selector status.successful!=0 -n $NAMESPACE

# Clean up old pods
echo "🧼 Cleaning up old pods..."
kubectl delete pods --field-selector=status.phase==Failed -n $NAMESPACE

# Clean up old PVCs (be careful with this in production)
echo "💾 Cleaning up unused PVCs..."
# Uncomment the following line if you want to delete unused PVCs
# kubectl delete pvc --field-selector=status.phase!=Bound -n $NAMESPACE

# Clean up old configmaps and secrets (older than 30 days)
echo "⚙️ Cleaning up old configmaps and secrets..."
# This is a placeholder - implement based on your needs

echo "✅ Cleanup completed successfully!"