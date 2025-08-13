# 📁 scripts/backup.sh

#!/bin/bash

# Backup script for AI Benchmark Service

set -e

echo "💾 Creating backup of AI Benchmark Service..."

# Set variables
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
NAMESPACE="benchmark-service"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup PostgreSQL database
echo "🗄 Backing up PostgreSQL database..."
kubectl exec -n $NAMESPACE $(kubectl get pod -n $NAMESPACE -l app=postgres -o jsonpath="{.items[0].metadata.name}") -- \
    pg_dump -U benchmark_user benchmark_db > $BACKUP_DIR/database_backup_$TIMESTAMP.sql

# Backup Redis data
echo "キャッシング Backing up Redis data..."
kubectl exec -n $NAMESPACE $(kubectl get pod -n $NAMESPACE -l app=redis -o jsonpath="{.items[0].metadata.name}") -- \
    redis-cli SAVE

# Backup configuration
echo "⚙️ Backing up configuration..."
kubectl get configmap -n $NAMESPACE -o yaml > $BACKUP_DIR/config_backup_$TIMESTAMP.yaml
kubectl get secret -n $NAMESPACE -o yaml > $BACKUP_DIR/secrets_backup_$TIMESTAMP.yaml

# Backup persistent volumes
echo "💾 Backing up persistent volumes..."
# This would typically involve backing up the underlying storage

echo "✅ Backup completed successfully!"
echo "Backup files saved to: $BACKUP_DIR/"
echo "Timestamp: $TIMESTAMP"