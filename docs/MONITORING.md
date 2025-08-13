# 📊 Monitoring Guide

This guide provides comprehensive information about monitoring the AI Benchmark Service, including metrics, alerts, dashboards, and troubleshooting procedures.

## 📈 Key Metrics and Monitoring

### Service Health Metrics

#### API Performance
- **Request Rate**: Number of requests per second
- **Response Time**: 50th, 95th, and 99th percentiles
- **Error Rate**: HTTP 4xx and 5xx errors
- **Throughput**: Requests processed successfully

#### Database Performance
- **Query Response Time**: Average and 95th percentile
- **Connection Pool Usage**: Active vs. available connections
- **Database Size**: Growth trends and capacity
- **Slow Queries**: Queries taking > 1 second

#### System Resources
- **CPU Usage**: Overall and per-container utilization
- **Memory Usage**: RSS and cache memory
- **Disk I/O**: Read/write operations per second
- **Network Traffic**: Incoming and outgoing bandwidth

#### Application-Specific Metrics
- **Active Benchmarks**: Currently running benchmark jobs
- **Benchmark Queue Length**: Pending benchmark requests
- **Agent Performance**: Accuracy, latency, and token usage by agent
- **Cache Hit Rate**: Redis cache effectiveness

### Prometheus Metrics

The service exposes metrics at `/metrics` endpoint:

```bash
# View available metrics
curl http://localhost:8000/metrics

# Example metrics
# HELP benchmark_requests_total Total number of benchmark requests
# TYPE benchmark_requests_total counter
benchmark_requests_total{endpoint="/api/benchmark/run",method="POST",status="200"} 42

# HELP benchmark_response_time_seconds Response time histogram
# TYPE benchmark_response_time_seconds histogram
benchmark_response_time_seconds_bucket{le="0.1"} 15
benchmark_response_time_seconds_bucket{le="0.5"} 38
benchmark_response_time_seconds_bucket{le="1.0"} 42
benchmark_response_time_seconds_count 42
benchmark_response_time_seconds_sum 21.5

# HELP benchmark_active_runs Number of currently active benchmark runs
# TYPE benchmark_active_runs gauge
benchmark_active_runs 3

# HELP benchmark_agent_accuracy Accuracy percentage for each agent
# TYPE benchmark_agent_accuracy gauge
benchmark_agent_accuracy{agent="gpt-4-turbo"} 87.3
benchmark_agent_accuracy{agent="claude-3-opus"} 82.1
```

### Custom Application Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Request counter
REQUESTS = Counter(
    'benchmark_requests_total',
    'Total number of benchmark requests',
    ['endpoint', 'method', 'status']
)

# Response time histogram
RESPONSE_TIME = Histogram(
    'benchmark_response_time_seconds',
    'Response time histogram',
    ['endpoint'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, float('inf'))
)

# Active runs gauge
ACTIVE_RUNS = Gauge(
    'benchmark_active_runs',
    'Number of currently active benchmark runs'
)

# Agent accuracy gauge
AGENT_ACCURACY = Gauge(
    'benchmark_agent_accuracy',
    'Accuracy percentage for each agent',
    ['agent']
)

# Instrument endpoints
@app.post("/api/benchmark/run")
async def run_benchmark(request: BenchmarkRequest):
    start_time = time.time()
    
    try:
        # Process benchmark
        result = await process_benchmark(request)
        
        # Record metrics
        REQUESTS.labels(
            endpoint='/api/benchmark/run',
            method='POST',
            status='200'
        ).inc()
        
        RESPONSE_TIME.labels(endpoint='/api/benchmark/run').observe(
            time.time() - start_time
        )
        
        ACTIVE_RUNS.inc()
        
        return result
        
    except Exception as e:
        REQUESTS.labels(
            endpoint='/api/benchmark/run',
            method='POST',
            status='500'
        ).inc()
        
        raise e
```

## 📊 Grafana Dashboards

### System Overview Dashboard

This dashboard provides a high-level view of system health:

1. **Service Status Panel**
   - Health check status (green/red indicators)
   - Uptime percentage
   - Last restart time

2. **Resource Utilization Panel**
   - CPU usage by container
   - Memory usage and limits
   - Disk space utilization
   - Network I/O

3. **API Performance Panel**
   - Request rate (RPS)
   - Response time percentiles
   - Error rate trend
   - Throughput metrics

### API Performance Dashboard

Detailed API performance monitoring:

1. **Endpoint Performance**
   - Response time by endpoint
   - Request volume by endpoint
   - Error distribution by endpoint
   - HTTP status code breakdown

2. **Latency Analysis**
   - 50th, 95th, 99th percentile trends
   - Latency distribution histograms
   - Slow request identification
   - Correlation with system resources

3. **Throughput Metrics**
   - Requests per second trends
   - Successful vs. failed requests
   - API usage by client/user
   - Rate limiting events

### Database Performance Dashboard

Database-specific monitoring:

1. **Query Performance**
   - Average query response time
   - Slow query identification
   - Query volume trends
   - Cache hit ratios

2. **Connection Metrics**
   - Active connections
   - Connection pool utilization
   - Failed connection attempts
   - Connection lifetime statistics

3. **Storage Metrics**
   - Database size growth
   - Table size distribution
   - Index usage efficiency
   - Backup status and size

### Benchmark Analytics Dashboard

Specialized dashboard for benchmark metrics:

1. **Benchmark Execution**
   - Active benchmark jobs
   - Queue length and processing rate
   - Completion time trends
   - Success/failure rates

2. **Agent Performance Comparison**
   - Accuracy by agent and benchmark
   - Latency comparison across agents
   - Token usage efficiency
   - Cost analysis per agent

3. **Results Analysis**
   - Performance trends over time
   - Category-wise performance
   - Statistical analysis of results
   - Anomaly detection

## 🔔 Alerting Rules

### Critical Alerts (PagerDuty/Slack)

#### High Error Rate
```yaml
- alert: HighErrorRate
  expr: rate(benchmark_requests_total{status=~"5.."}[5m]) > 0.01
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "High error rate on benchmark service ({{ $value }}%)"
    description: "Error rate above 1% for more than 2 minutes"
```

#### Service Unavailable
```yaml
- alert: ServiceDown
  expr: up{job="benchmark-service"} == 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "Benchmark service is down"
    description: "Service has been down for more than 1 minute"
```

#### High Latency
```yaml
- alert: HighLatency
  expr: histogram_quantile(0.95, rate(benchmark_response_time_seconds_bucket[5m])) > 5
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "High latency on benchmark service ({{ $value }}s)"
    description: "95th percentile response time above 5 seconds"
```

#### Database Connection Issues
```yaml
- alert: DatabaseConnectionIssues
  expr: rate(pg_stat_database_deadlocks[5m]) > 1
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "Database connection issues detected"
    description: "High rate of database deadlocks or connection failures"
```

### Warning Alerts (Email)

#### Moderate Error Rate
```yaml
- alert: ModerateErrorRate
  expr: rate(benchmark_requests_total{status=~"5.."}[5m]) > 0.005
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Moderate error rate on benchmark service ({{ $value }}%)"
    description: "Error rate above 0.5% for more than 5 minutes"
```

#### High Resource Usage
```yaml
- alert: HighCPUUsage
  expr: rate(container_cpu_usage_seconds_total[5m]) > 0.8
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High CPU usage ({{ $value }}%)"
    description: "CPU usage above 80% for more than 5 minutes"
```

#### Low Disk Space
```yaml
- alert: LowDiskSpace
  expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.1
  for: 1m
  labels:
    severity: warning
  annotations:
    summary: "Low disk space ({{ $value }}% remaining)"
    description: "Disk space below 10% threshold"
```

#### Benchmark Queue Backlog
```yaml
- alert: BenchmarkQueueBacklog
  expr: benchmark_queue_length > 50
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "Benchmark queue backlog ({{ $value }} jobs)"
    description: "Benchmark queue has more than 50 jobs pending for 10 minutes"
```

## 🛠️ Monitoring Setup

### Prometheus Configuration

```yaml
# prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'benchmark-service'
    static_configs:
      - targets: ['web:8000']
    
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:9187']
    
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:9121']
```

### Grafana Configuration

```yaml
# grafana/provisioning/datasources/prometheus.yml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    access: proxy
    isDefault: true
```

### Docker Monitoring Exporters

```yaml
# docker-compose.yml additions for monitoring
services:
  postgres-exporter:
    image: wrouesnel/postgres_exporter
    environment:
      - DATA_SOURCE_NAME=postgresql://benchmark_user:benchmark_password@postgres:5432/benchmark_db?sslmode=disable
    ports:
      - "9187:9187"
    depends_on:
      - postgres

  redis-exporter:
    image: oliver006/redis_exporter
    ports:
      - "9121:9121"
    depends_on:
      - redis
```

## 📈 Performance Baselines

### Expected Performance Metrics

#### API Response Times
- **95th Percentile**: < 1 second
- **99th Percentile**: < 2 seconds
- **Average**: < 500 milliseconds

#### Throughput Targets
- **Sustained RPS**: > 50 requests per second
- **Peak RPS**: > 200 requests per second
- **Concurrent Benchmarks**: 10+ simultaneous jobs

#### Database Performance
- **Query Response Time**: < 100 milliseconds (95th percentile)
- **Connection Pool Usage**: < 80% peak utilization
- **Cache Hit Rate**: > 90% for frequently accessed data

#### Resource Utilization
- **CPU Usage**: < 70% average, < 90% peak
- **Memory Usage**: < 80% of allocated memory
- **Disk I/O**: < 80% of maximum IOPS
- **Network Bandwidth**: < 70% of available bandwidth

### Scalability Benchmarks

#### Vertical Scaling
- **2x CPU**: 40% improvement in throughput
- **2x Memory**: 25% improvement in concurrent benchmarks
- **SSD Storage**: 60% improvement in database queries

#### Horizontal Scaling
- **2x Web Instances**: 90% improvement in throughput
- **Load Balancing**: Even distribution of requests
- **Database Read Replicas**: 50% improvement in read queries

## 🚨 Troubleshooting Guide

### Common Monitoring Issues

#### 1. Metrics Not Appearing

**Symptoms**: Grafana dashboards show "No data" or gaps in metrics

**Diagnosis**:
```bash
# Check if metrics endpoint is accessible
curl http://localhost:8000/metrics

# Check Prometheus target status
# Access Prometheus UI at http://localhost:9090/targets

# Check container logs
docker-compose logs web
```

**Resolution**:
```bash
# Restart affected services
docker-compose restart web

# Check firewall rules
# Ensure port 8000 is accessible from Prometheus

# Verify metrics instrumentation
# Check if Prometheus client is properly initialized
```

#### 2. High Latency Alerts

**Symptoms**: Frequent high latency alerts

**Diagnosis**:
```bash
# Check system resources
docker stats

# Check database performance
docker-compose exec postgres psql -U benchmark_user -d benchmark_db -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 5;"

# Check slow query logs
docker-compose logs postgres | grep "duration"
```

**Resolution**:
```bash
# Optimize database queries
# Add missing indexes
# Review query execution plans

# Scale resources
# Increase CPU/Memory allocation
# Add database read replicas

# Implement caching
# Cache frequently accessed data
# Use Redis for session storage
```

#### 3. Database Connection Issues

**Symptoms**: "Too many connections" errors, database timeouts

**Diagnosis**:
```bash
# Check current connections
docker-compose exec postgres psql -U benchmark_user -d benchmark_db -c "SELECT count(*) FROM pg_stat_activity;"

# Check connection pool settings
docker-compose exec web env | grep DATABASE_POOL

# Check for long-running queries
docker-compose exec postgres psql -U benchmark_user -d benchmark_db -c "SELECT pid, query_start, query FROM pg_stat_activity WHERE state = 'active' ORDER BY query_start;"
```

**Resolution**:
```bash
# Increase database connection limits
docker-compose exec postgres psql -U benchmark_user -d benchmark_db -c "ALTER SYSTEM SET max_connections = 200;"

# Optimize connection pooling
# Adjust pool size and overflow settings
# Implement connection timeouts

# Terminate long-running queries
docker-compose exec postgres psql -U benchmark_user -d benchmark_db -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'active' AND query_start < now() - interval '5 minutes';"
```

### Alert Investigation Procedures

#### 1. High Error Rate Investigation

```bash
# Check recent errors
docker-compose logs web | grep "ERROR\|Exception" | tail -20

# Check specific error patterns
docker-compose logs web | grep "404\|500" | tail -50

# Look for correlation with requests
docker-compose logs web | grep "benchmark/run" | tail -100
```

#### 2. High CPU Usage Investigation

```bash
# Check per-container CPU usage
docker stats --no-stream

# Check top processes in container
docker-compose exec web top

# Check for specific resource-intensive operations
docker-compose logs web | grep "processing\|benchmark" | tail -20
```

#### 3. Database Performance Issues

```bash
# Check slow query logs
docker-compose logs postgres | grep "duration" | tail -10

# Check database statistics
docker-compose exec postgres psql -U benchmark_user -d benchmark_db -c "SELECT * FROM pg_stat_database;"

# Check for table bloat
docker-compose exec postgres psql -U benchmark_user -d benchmark_db -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size FROM pg_tables WHERE schemaname='public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

## 📊 Log Analysis

### Structured Logging

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        
    def info(self, message, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": "INFO",
            "message": message,
            "data": kwargs
        }
        self.logger.info(json.dumps(log_entry))
        
    def error(self, message, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": "ERROR",
            "message": message,
            "data": kwargs
        }
        self.logger.error(json.dumps(log_entry))

# Usage
logger = StructuredLogger(__name__)
logger.info("Benchmark started", run_id="abc123", agents=["gpt-4"])
logger.error("Benchmark failed", run_id="abc123", error="Timeout")
```

### Log Aggregation

```bash
# Centralized logging with ELK stack
# docker-compose.yml additions:

# elasticsearch:
#   image: elasticsearch:7.17.0
#   environment:
#     - discovery.type=single-node
#   ports:
#     - "9200:9200"
# 
# logstash:
#   image: logstash:7.17.0
#   volumes:
#     - ./logstash/pipeline:/usr/share/logstash/pipeline
#   depends_on:
#     - elasticsearch
# 
# kibana:
#   image: kibana:7.17.0
#   ports:
#     - "5601:5601"
#   depends_on:
#     - elasticsearch
```

### Log Analysis Patterns

```bash
# Find error patterns
grep "ERROR" logs/app.log | grep -oE '"message":"[^"]*"' | sort | uniq -c | sort -nr

# Analyze request patterns
grep "benchmark/run" logs/app.log | grep "POST" | wc -l

# Track performance issues
grep "duration" logs/app.log | awk '{print $NF}' | sort -n | tail -10

# Monitor specific benchmark runs
grep "run_id:abc123" logs/app.log
```

## 📈 Performance Optimization

### Query Optimization

```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_benchmarks_status ON benchmarks(status);
CREATE INDEX idx_benchmarks_created_at ON benchmarks(created_at);
CREATE INDEX idx_benchmark_results_run_id ON benchmark_results(run_id);

-- Analyze query performance
EXPLAIN ANALYZE SELECT b.*, r.* 
FROM benchmarks b 
JOIN benchmark_results r ON b.run_id = r.run_id 
WHERE b.status = 'completed' 
ORDER BY b.created_at DESC 
LIMIT 10;
```

### Caching Strategies

```python
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='redis', port=6379, db=0)

def cache_result(expiration=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            
            return result
        return wrapper
    return decorator

# Usage
@cache_result(expiration=600)
async def get_benchmark_list():
    # Database query
    pass
```

### Resource Optimization

```python
# Connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Optimize pool settings
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,        # Number of connections to maintain
    max_overflow=10,     # Additional connections beyond pool_size
    pool_timeout=30,     # Seconds to wait for connection
    pool_recycle=3600    # Seconds before recycling connections
)

# Async database operations
import asyncio
import asyncpg

async def fetch_benchmark_results(run_id):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        results = await conn.fetch(
            "SELECT * FROM benchmark_results WHERE run_id = $1",
            run_id
        )
        return results
    finally:
        await conn.close()
```

## 📚 Monitoring Tools and Resources

### Essential Monitoring Tools

1. **Prometheus**: Metrics collection and storage
2. **Grafana**: Visualization and dashboarding
3. **Alertmanager**: Alert routing and deduplication
4. **Elasticsearch**: Log aggregation and search
5. **Logstash**: Log processing and transformation
6. **Kibana**: Log visualization
7. **Fluentd**: Log collection and forwarding

### Monitoring Best Practices

1. **Golden Signals**: Latency, Traffic, Errors, Saturation
2. **SLI/SLO/SLA**: Define and monitor service level objectives
3. **Alerting Philosophy**: Alert on symptoms, not causes
4. **Dashboard Design**: Focus on actionable information
5. **Log Structuring**: Use structured logging for better analysis
6. **Performance Baselines**: Establish normal performance patterns
7. **Capacity Planning**: Monitor resource utilization trends

This monitoring guide provides comprehensive coverage of observability practices for the AI Benchmark Service. Regular updates and reviews ensure that monitoring remains effective as the system evolves.