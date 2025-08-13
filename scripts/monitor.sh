# 📁 scripts/monitor.sh

#!/bin/bash

# Monitoring script for AI Benchmark Service

set -e

echo "🔍 Monitoring AI Benchmark Service..."

NAMESPACE="benchmark-service"

# Check pod status
echo "📋 Pod Status:"
kubectl get pods -n $NAMESPACE

# Check service status
echo -e "\nサービ Service Status:"
kubectl get services -n $NAMESPACE

# Check resource usage
echo -e "\n📊 Resource Usage:"
kubectl top pods -n $NAMESPACE

# Check logs for errors
echo -e "\n📋 Recent Logs (last 10 minutes):"
kubectl logs --since=10m -n $NAMESPACE -l app=benchmark-service --tail=50

# Check HPA status
echo -e "\n📈 Horizontal Pod Autoscaler:"
kubectl get hpa -n $NAMESPACE

# Check network policies
echo -e "\n🔒 Network Policies:"
kubectl get networkpolicies -n $NAMESPACE

# Check persistent volumes
echo -e "\n💾 Persistent Volumes:"
kubectl get pvc -n $NAMESPACE

# Health check
echo -e "\n🏥 Health Check:"
kubectl exec -n $NAMESPACE $(kubectl get pod -n $NAMESPACE -l app=benchmark-service -o jsonpath="{.items[0].metadata.name}") -- \
    curl -f http://localhost:8000/health || echo "Health check failed"

echo -e "\n✅ Monitoring completed!"