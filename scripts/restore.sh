# 📁 scripts/restore.sh

#!/bin/bash

# Restore script for AI Benchmark Service

set -e

echo "🔄 Restoring AI Benchmark Service from backup..."

# Check if backup file is provided
if [ $# -eq 0 ]; then
    echo "❌ Usage: $0 <backup_timestamp>"
    echo "Example: $0 20240101_120000"
    exit 1
fi

BACKUP_TIMESTAMP=$1
BACKUP_DIR="./backups"
NAMESPACE="benchmark-service"

# Check if backup exists
if [ ! -f "$BACKUP_DIR/database_backup_$BACKUP_TIMESTAMP.sql" ]; then
    echo "❌ Backup files not found for timestamp: $BACKUP_TIMESTAMP"
    exit 1
fi

echo "🔍 Found backup files for timestamp: $BACKUP_TIMESTAMP"

# Stop services temporarily
echo "⏸ Stopping services..."
kubectl scale deployment/benchmark-service -n $NAMESPACE --replicas=0
kubectl scale deployment/redis -n $NAMESPACE --replicas=0
kubectl scale deployment/postgres -n $NAMESPACE --replicas=0

# Wait for services to stop
echo "⏳ Waiting for services to stop..."
sleep 30

# Restore PostgreSQL database
echo "🗄 Restoring PostgreSQL database..."
kubectl exec -i -n $NAMESPACE $(kubectl get pod -n $NAMESPACE -l app=postgres -o jsonpath="{.items[0].metadata.name}") -- \
    psql -U benchmark_user benchmark_db < $BACKUP_DIR/database_backup_$BACKUP_TIMESTAMP.sql

# Restore configuration
echo "⚙️ Restoring configuration..."
kubectl apply -f $BACKUP_DIR/config_backup_$BACKUP_TIMESTAMP.yaml
kubectl apply -f $BACKUP_DIR/secrets_backup_$BACKUP_TIMESTAMP.yaml

# Start services
echo "▶️ Starting services..."
kubectl scale deployment/benchmark-service -n $NAMESPACE --replicas=3
kubectl scale deployment/redis -n $NAMESPACE --replicas=1
kubectl scale deployment/postgres -n $NAMESPACE --replicas=1

# Wait for services to start
echo "⏳ Waiting for services to start..."
kubectl wait --for=condition=available --timeout=600s deployment/benchmark-service -n $NAMESPACE
kubectl wait --for=condition=available --timeout=600s deployment/redis -n $NAMESPACE
kubectl wait --for=condition=available --timeout=600s deployment/postgres -n $NAMESPACE

# Check service status
echo "🔍 Checking service status..."
kubectl get pods -n $NAMESPACE

echo "✅ Restore completed successfully!"
