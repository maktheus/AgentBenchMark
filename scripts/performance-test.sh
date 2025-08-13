# 📁 scripts/performance-test.sh

#!/bin/bash

# Performance test script for AI Benchmark Service

set -e

echo "⚡ Running performance tests..."

# Check if required tools are installed
if ! command -v locust &> /dev/null; then
    echo "Installing locust..."
    pip install locust
fi

# Set variables
HOST=${1:-http://localhost:8000}
USERS=${2:-100}
SPAWN_RATE=${3:-10}
DURATION=${4:-300}

echo "🏃 Running load test with:"
echo "  Host: $HOST"
echo "  Users: $USERS"
echo "  Spawn Rate: $SPAWN_RATE"
echo "  Duration: $DURATION seconds"

# Run load test
locust -f locustfile.py \
    --headless \
    --host $HOST \
    -u $USERS \
    -r $SPAWN_RATE \
    --run-time ${DURATION}s \
    --csv perf-test-results \
    --html perf-test-report.html \
    --only-summary

echo "✅ Performance tests completed!"
echo "Results saved to:"
echo "  perf-test-results_stats.csv"
echo "  perf-test-report.html"