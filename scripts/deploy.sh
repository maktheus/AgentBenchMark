# 📁 scripts/deploy.sh

#!/bin/bash

# Deployment script for AI Benchmark Service

set -e

echo "🚀 Deploying AI Benchmark Service..."

# Check if kubectl is installed
if ! command -k &> /dev/null; then
    echo "❌ kubectl is not installed"
    exit 1
fi

# Check if helm is installed
if ! command -v helm &> /dev/null; then
    echo "❌ helm is not installed"
    exit 1
fi

# Set namespace
NAMESPACE="benchmark-service"

# Create namespace if it doesn't exist
if ! kubectl get namespace $NAMESPACE &> /dev/null; then
    echo "📁 Creating namespace $NAMESPACE..."
    kubectl create namespace $NAMESPACE
fi

# Apply Kubernetes manifests
echo "📋 Applying Kubernetes manifests..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/persistentvolumeclaim.yaml
kubectl apply -f k8s/serviceaccount.yaml
kubectl apply -f k8s/networkpolicy.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml

# Wait for deployments to be ready
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=600s deployment/benchmark-service -n $NAMESPACE
kubectl wait --for=condition=available --timeout=600s deployment/redis -n $NAMESPACE
kubectl wait --for=condition=available --timeout=600s deployment/postgres -n $NAMESPACE

# Check service status
echo "🔍 Checking service status..."
kubectl get pods -n $NAMESPACE
kubectl get services -n $NAMESPACE

echo "✅ Deployment completed successfully!"
echo ""
echo "Service endpoints:"
echo "  API: http://api.benchmark.example.com"
echo "  Grafana: http://grafana.benchmark.example.com"
echo "  Prometheus: http://prometheus.benchmark.example.com"