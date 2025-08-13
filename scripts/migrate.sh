# 📁 scripts/migrate.sh

#!/bin/bash

# Database migration script for AI Benchmark Service

set -e

echo "⬆️ Running database migrations..."

NAMESPACE="benchmark-service"

# Check if migration command is provided
if [ $# -eq 0 ]; then
    echo "ℹ️ Usage: $0 [upgrade|downgrade|history]"
    echo "Example: $0 upgrade"
    echo ""
    echo "Available commands:"
    echo "  upgrade   - Apply pending migrations"
    echo "  downgrade - Revert last migration"
    echo "  history   - Show migration history"
    exit 1
fi

COMMAND=$1

# Run migration command
echo "🔄 Running migration command: $COMMAND"
kubectl exec -n $NAMESPACE $(kubectl get pod -n $NAMESPACE -l app=benchmark-service -o jsonpath="{.items[0].metadata.name}") -- \
    alembic $COMMAND

echo "✅ Migration command completed successfully!"
