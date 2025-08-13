# 🛠️ Operations Manual

This document provides comprehensive operational guidance for maintaining and managing the AI Benchmark Service.

## 📋 System Architecture Overview

### Core Components

1. **API Gateway** (FastAPI)
   - RESTful API endpoints
   - Request routing and validation
   - Authentication and authorization

2. **Benchmark Service** (Python/FastAPI)
   - Core business logic
   - Benchmark orchestration
   - Result processing and analytics

3. **Database** (PostgreSQL)
   - Benchmark metadata storage
   - Results persistence
   - Analytics data storage

4. **Caching/Queue** (Redis)
   - Task queue management
   - Session caching
   - Rate limiting

5. **Monitoring** (Prometheus/Grafana)
   - Metrics collection
   - Dashboard visualization
   - Alerting

6. **Agents** (Multiple Types)
   - OpenAI API integration
   - Anthropic API integration
   - Local agent support

## 🚦 Health Checks and Monitoring

### Endpoint Health Checks

```bash
# Liveness probe - indicates if service is running
curl -f http://localhost:8000/health || echo "Service DOWN"

# Readiness probe - indicates if service can handle requests
curl -f http://localhost:8000/ready || echo "Service NOT READY"
```

### Service Status Monitoring

Check individual service status:

```bash
# Database connectivity
docker-compose exec postgres pg_isready

# Redis connectivity
docker-compose exec redis redis-cli ping

# API service logs
docker-compose logs web
```

### Custom Health Metrics

The system exposes Prometheus metrics at `/metrics`:

```bash
# View available metrics
curl http://localhost:8000/metrics | grep benchmark

# Example metrics
benchmark_requests_total{endpoint="/api/benchmark/run",method="POST",status="200"} 42
benchmark_response_time_seconds_bucket{le="0.1"} 15
benchmark_active_runs 3
```

## 📊 Performance Monitoring

### Key Performance Indicators

1. **API Response Time**
   - Target: < 1 second for 95% of requests
   - Alert: > 2 seconds for sustained period

2. **Throughput**
   - Target: > 50 requests per second
   - Alert: < 10 requests per second

3. **Error Rate**
   - Target: < 0.1%
   - Alert: > 1%

4. **Database Performance**
   - Query response time < 100ms
   - Connection pool utilization < 80%

### Grafana Dashboards

Access pre-configured dashboards:

1. **System Overview**: CPU, memory, disk usage
2. **API Performance**: Request rates, response times
3. **Database Metrics**: Query performance, connections
4. **Benchmark Analytics**: Success rates, agent performance

### Alerting Rules

Configure alerts in Prometheus:

```yaml
# High error rate
- alert: HighErrorRate
  expr: rate(benchmark_requests_total{status=~"5.."}[5m]) > 0.01
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "High error rate on benchmark service"

# High latency
- alert: HighLatency
  expr: histogram_quantile(0.95, rate(benchmark_response_time_seconds_bucket[5m])) > 2
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "High latency on benchmark service"
```

## 🔧 Maintenance Procedures

### Routine Maintenance

#### Daily Tasks

1. **Log Rotation**
   ```bash
   # Docker logs are automatically rotated
   # Check log sizes
   docker-compose logs --tail 100 web
   ```

2. **Database Maintenance**
   ```bash
   # Check database size
   docker-compose exec postgres psql -U benchmark_user -d benchmark_db -c "SELECT pg_size_pretty(pg_database_size('benchmark_db'));"
   
   # Run VACUUM (if needed)
   docker-compose exec postgres psql -U benchmark_user -d benchmark_db -c "VACUUM ANALYZE;"
   ```

#### Weekly Tasks

1. **System Updates**
   ```bash
   # Update Docker images
   docker-compose pull
   docker-compose up --build -d
   ```

2. **Backup Verification**
   ```bash
   # Test backup restoration (in staging environment)
   # This should be done in a separate staging environment
   ```

#### Monthly Tasks

1. **Security Updates**
   ```bash
   # Update dependencies
   pip list --outdated
   pip install --upgrade -r requirements.txt
   ```

2. **Performance Review**
   - Analyze Grafana dashboards
   - Review system resource usage
   - Optimize database queries if needed

### Database Maintenance

#### Backup Procedures

```bash
# Create backup
docker-compose exec postgres pg_dump -U benchmark_user benchmark_db > backup_$(date +%Y%m%d).sql

# Compressed backup
docker-compose exec postgres pg_dump -U benchmark_user benchmark_db | gzip > backup_$(date +%Y%m%d).sql.gz
```

#### Restore Procedures

```bash
# Restore from backup
docker-compose exec -T postgres psql -U benchmark_user benchmark_db < backup.sql

# Restore from compressed backup
gunzip -c backup.sql.gz | docker-compose exec -T postgres psql -U benchmark_user benchmark_db
```

#### Database Optimization

```bash
# Analyze and vacuum
docker-compose exec postgres psql -U benchmark_user benchmark_db -c "ANALYZE;"

# Reindex (if needed)
docker-compose exec postgres psql -U benchmark_user benchmark_db -c "REINDEX DATABASE benchmark_db;"
```

## 🚨 Incident Response

### Common Issues and Solutions

#### 1. Service Unreachable

**Symptoms**: API returns 502/503 errors

**Diagnosis**:
```bash
# Check if containers are running
docker-compose ps

# Check service logs
docker-compose logs web

# Check network connectivity
docker-compose exec web ping postgres
```

**Resolution**:
```bash
# Restart affected services
docker-compose restart web

# If database issue
docker-compose restart postgres
```

#### 2. Database Connection Issues

**Symptoms**: Database connection timeouts, "too many connections" errors

**Diagnosis**:
```bash
# Check database connections
docker-compose exec postgres psql -U benchmark_user benchmark_db -c "SELECT count(*) FROM pg_stat_activity;"

# Check connection pool settings
docker-compose exec web env | grep DB_
```

**Resolution**:
```bash
# Increase database connections (temporarily)
docker-compose exec postgres psql -U benchmark_user benchmark_db -c "ALTER SYSTEM SET max_connections = 200;"

# Restart PostgreSQL
docker-compose restart postgres
```

#### 3. High Memory Usage

**Symptoms**: System becomes slow, OOM killer activates

**Diagnosis**:
```bash
# Check container memory usage
docker stats --no-stream

# Check system memory
free -h
```

**Resolution**:
```bash
# Restart containers to free memory
docker-compose restart

# Adjust resource limits in docker-compose.yml
# Add mem_limit to services
```

### Escalation Procedures

#### Level 1: Basic Troubleshooting (Operations Team)

1. Restart affected services
2. Check logs for obvious errors
3. Verify resource utilization
4. If unresolved in 30 minutes, escalate to Level 2

#### Level 2: Advanced Troubleshooting (DevOps Team)

1. Deep dive into logs and metrics
2. Database query analysis
3. Network connectivity checks
4. If unresolved in 2 hours, escalate to Level 3

#### Level 3: Expert Troubleshooting (Architecture Team)

1. Code-level debugging
2. System architecture review
3. Performance optimization
4. External dependency issues

## 🔒 Security Operations

### Access Control

#### User Management

```bash
# Add new database user
docker-compose exec postgres psql -U benchmark_user benchmark_db -c "CREATE USER newuser WITH PASSWORD 'password';"

# Grant permissions
docker-compose exec postgres psql -U benchmark_user benchmark_db -c "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO newuser;"
```

#### API Key Rotation

```bash
# Update environment variables
echo "NEW_API_KEY=sk-new-key" >> .env

# Restart services
docker-compose restart web
```

### Security Monitoring

#### Log Analysis

```bash
# Check for failed login attempts
docker-compose logs web | grep "401\|403"

# Check for suspicious activity
docker-compose logs web | grep "error\|exception" -i
```

#### Security Scans

```bash
# Dependency security check
pip install safety
safety check -r requirements.txt

# Container security scan
docker scan ai-benchmark-service
```

## 📈 Capacity Planning

### Resource Requirements

#### Minimum Requirements

- CPU: 2 cores
- Memory: 4GB RAM
- Disk: 10GB free space
- Network: 100Mbps connectivity

#### Recommended Requirements

- CPU: 4 cores
- Memory: 8GB RAM
- Disk: 50GB free space
- Network: 1Gbps connectivity

### Scaling Guidelines

#### Horizontal Scaling

```bash
# Scale web services
docker-compose up --scale web=3 -d

# Scale workers (when implemented)
docker-compose up --scale worker=2 -d
```

#### Vertical Scaling

Monitor resource usage and upgrade:

1. **CPU-bound**: Increase CPU cores
2. **Memory-bound**: Increase RAM
3. **Disk-bound**: Increase storage
4. **Network-bound**: Upgrade network bandwidth

## 📊 Backup and Disaster Recovery

### Backup Strategy

#### Full Backups

- Frequency: Daily
- Retention: 30 days
- Storage: Secure, encrypted location

#### Incremental Backups

- Frequency: Hourly
- Retention: 7 days
- Storage: Local fast storage

#### Configuration Backups

- Frequency: On change
- Retention: Indefinite
- Storage: Version control system

### Recovery Procedures

#### Database Recovery

```bash
# Stop application services
docker-compose stop web

# Restore database from backup
docker-compose exec -T postgres psql -U benchmark_user benchmark_db < backup.sql

# Start services
docker-compose start web
```

#### Complete System Recovery

1. Restore infrastructure (if using cloud)
2. Restore database from backup
3. Deploy application code
4. Restore configuration files
5. Test system functionality

### Business Continuity

#### High Availability Setup

```yaml
# docker-compose.ha.yml
version: '3.8'
services:
  web1:
    # ... web service configuration
  web2:
    # ... web service configuration
  loadbalancer:
    image: nginx
    # ... load balancer configuration
```

#### Disaster Recovery Plan

1. **Detection**: Automated monitoring alerts
2. **Assessment**: Determine impact scope
3. **Activation**: Execute recovery procedures
4. **Recovery**: Restore services in priority order
5. **Validation**: Verify system functionality
6. **Communication**: Notify stakeholders

## 📋 Change Management

### Deployment Process

#### Blue-Green Deployment

```bash
# Deploy new version to green environment
docker-compose -f docker-compose.green.yml up -d

# Test new version
curl -f http://green-host:8000/health

# Switch traffic to green
# (Update load balancer configuration)

# Decommission blue
docker-compose -f docker-compose.blue.yml down
```

#### Rolling Update

```bash
# Update one service at a time
docker-compose up --scale web=2 -d
docker-compose up --scale web=3 -d
docker-compose up --scale web=4 -d
```

### Testing Procedures

#### Pre-Deployment Testing

1. **Unit Tests**: `pytest tests/unit/`
2. **Integration Tests**: `pytest tests/integration/`
3. **End-to-End Tests**: `pytest tests/e2e/`
4. **Performance Tests**: Load testing with Locust
5. **Security Tests**: Dependency scanning

#### Post-Deployment Validation

1. **Health Checks**: Verify all endpoints
2. **Smoke Tests**: Basic functionality test
3. **Performance Tests**: Monitor response times
4. **Monitoring**: Verify metrics collection

## 📚 Documentation and Knowledge Management

### Documentation Updates

Maintain up-to-date documentation:

1. **API Documentation**: Auto-generated from code
2. **Operational Guides**: Updated with procedures
3. **Architecture Diagrams**: Reflect current state
4. **Troubleshooting Guides**: Based on incident reports

### Knowledge Sharing

#### Post-Incident Reviews

After major incidents:

1. Document root cause
2. Update procedures
3. Share lessons learned
4. Update training materials

#### Regular Training

Schedule regular training sessions:

1. **New Team Members**: Onboarding training
2. **Existing Team**: Quarterly refresher
3. **Tool Updates**: When new tools are adopted
4. **Process Changes**: When procedures are updated

## 📞 Support and Communication

### Support Channels

#### Internal Support

- **Slack Channel**: #benchmark-service-support
- **Email Group**: benchmark-support@company.com
- **Ticketing System**: Jira Service Desk

#### External Support

- **Vendor Support**: Contact information for third-party services
- **Community Support**: GitHub issues, forums
- **Professional Services**: Consulting partners

### Communication Plans

#### Scheduled Maintenance

1. **Notification**: 48 hours in advance
2. **Impact Assessment**: Document affected services
3. **Rollback Plan**: Procedures if issues occur
4. **Post-Maintenance**: Validation and notification

#### Emergency Maintenance

1. **Immediate Notification**: All stakeholders
2. **Real-time Updates**: Status every 30 minutes
3. **Post-Incident Report**: Detailed analysis
4. **Preventive Measures**: Actions to prevent recurrence

## 📈 Performance Optimization

### Database Optimization

#### Query Optimization

```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_benchmarks_status ON benchmarks(status);
CREATE INDEX idx_benchmarks_created_at ON benchmarks(created_at);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM benchmarks WHERE status = 'completed';
```

#### Connection Pooling

Configure connection pooling in application:

```python
# In database configuration
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 10
```

### Caching Strategies

#### Redis Caching

```python
# Cache frequently accessed data
import redis

redis_client = redis.Redis(host='redis', port=6379, db=0)

# Cache benchmark list
redis_client.setex('benchmarks_list', 300, json.dumps(benchmarks))
```

#### API Response Caching

```python
# Cache API responses
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Add caching headers
@app.get("/api/benchmark/list")
async def list_benchmarks():
    # Check cache first
    cached = redis_client.get('benchmarks_list')
    if cached:
        return json.loads(cached)
    
    # Generate response and cache
    response = get_benchmarks_from_db()
    redis_client.setex('benchmarks_list', 300, json.dumps(response))
    return response
```

### Resource Optimization

#### Container Resource Limits

```yaml
# In docker-compose.yml
services:
  web:
    # ... other configuration
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

#### Application-Level Optimization

```python
# Use async/await for I/O operations
async def process_benchmark(run_id):
    # Non-blocking operations
    await database_query()
    await external_api_call()
    
# Connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10
)
```

This operations manual provides comprehensive guidance for maintaining and managing the AI Benchmark Service. Regular updates to this document ensure that operational knowledge is preserved and can be effectively transferred between team members.