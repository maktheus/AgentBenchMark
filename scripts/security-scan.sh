# 📁 scripts/security-scan.sh

#!/bin/bash

# Security scan script for AI Benchmark Service

set -e

echo "🛡️ Running security scans..."

# Check if required tools are installed
if ! command -v safety &> /dev/null; then
    echo "Installing safety..."
    pip install safety
fi

if ! command -v bandit &> /dev/null; then
    echo "Installing bandit..."
    pip install bandit
fi

# Run dependency security scan
echo "🔍 Scanning dependencies for vulnerabilities..."
safety check -r requirements.txt

# Run static analysis for security issues
echo "🔎 Running static analysis for security issues..."
bandit -r benchmark_service/ -f json -o security-report.json

# Check for secrets in code
echo "🔑 Checking for secrets in code..."
if command -v detect-secrets &> /dev/null; then
    detect-secrets scan > .secrets.baseline
else
    echo "detect-secrets not found. Skipping secret detection."
fi

# Scan Docker images
echo "🐳 Scanning Docker images for vulnerabilities..."
if command -v docker &> /dev/null && command -v dockle &> /dev/null; then
    dockle ai-benchmark-service:latest
else
    echo "Docker or dockle not found. Skipping Docker image scan."
fi

# Scan Kubernetes manifests
echo "☸️ Scanning Kubernetes manifests for security issues..."
if command -v kube-score &> /dev/null; then
    kube-score score k8s/*.yaml
else
    echo "kube-score not found. Skipping Kubernetes manifest scan."
fi

echo "✅ Security scans completed!"
echo "Security report saved to security-report.json"