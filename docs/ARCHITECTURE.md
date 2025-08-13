# 🏗️ Architecture Documentation

This document provides a comprehensive overview of the AI Benchmark Service architecture, design decisions, and system components.

## 📐 System Architecture Overview

### High-Level Architecture

```mermaid
graph TD
    A[Client Applications] --> B[API Gateway]
    B --> C[Benchmark Service]
    C --> D[Agent Adapters]
    C --> E[Task Orchestrator]
    C --> F[Evaluation Engine]
    D --> G[Cloud Agents<br/>OpenAI/Anthropic]
    D --> H[Local Agents]
    E --> I[Task Queue<br/>Redis]
    F --> J[Results Storage<br/>PostgreSQL]
    C --> K[Monitoring<br/>Prometheus/Grafana]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
    style E fill:#fce4ec
    style F fill:#f1f8e9
    style G fill:#e0f2f1
    style H fill:#e0f2f1
    style I fill:#bbdefb
    style J fill:#c8e6c9
    style K fill:#ffccbc
```

### Core Components

#### 1. API Gateway
- **Technology**: NGINX/OpenResty
- **Responsibilities**:
  - Request routing and load balancing
  - Authentication and authorization
  - Rate limiting and DDoS protection
  - SSL termination
  - Request/response logging

#### 2. Benchmark Service (Core)
- **Technology**: Python 3.11 + FastAPI
- **Key Features**:
  - RESTful API endpoints
  - Request validation and processing
  - Benchmark orchestration
  - Result aggregation and analysis
  - Real-time status updates

#### 3. Agent Adapters
- **Pattern**: Adapter Pattern
- **Supported Agents**:
  - OpenAI GPT series
  - Anthropic Claude series
  - Custom local agents
  - Generic HTTP/GRPC agents

#### 4. Task Orchestrator
- **Technology**: Celery + Redis
- **Workflow**:
  1. Receive benchmark configuration
  2. Load appropriate dataset
  3. Distribute tasks to agents
  4. Collect responses
  5. Trigger evaluation
  6. Aggregate results

#### 5. Evaluation Engine
- **Capabilities**:
  - Automatic evaluation (template matching)
  - LLM-as-a-Judge for subjective assessment
  - Statistical analysis and metrics calculation
  - Consistency scoring

#### 6. Storage Layer
- **Primary Database**: PostgreSQL (relational data)
- **Object Storage**: MinIO/S3 (datasets, reports)
- **Cache/Queue**: Redis (session, tasks, caching)

#### 7. Monitoring & Observability
- **Metrics**: Prometheus
- **Visualization**: Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing**: Jaeger/OpenTelemetry

## 🧩 Design Patterns and Principles

### Architectural Patterns

#### 1. Microservices Architecture
- **Benefits**:
  - Independent scaling of components
  - Technology diversity
  - Fault isolation
  - Team autonomy

#### 2. Adapter Pattern
```python
# Interface definition
class AgentInterface(ABC):
    @abstractmethod
    async def query(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        pass

# Implementation
class OpenAIAgentAdapter(AgentInterface):
    async def query(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # OpenAI-specific implementation
        pass
    
    def get_info(self) -> Dict[str, Any]:
        return {"name": "openai", "capabilities": ["text-generation"]}
```

#### 3. Observer Pattern (Event-Driven)
```python
# Event system for status updates
class BenchmarkEventManager:
    def __init__(self):
        self.observers = defaultdict(list)
    
    def subscribe(self, event_type: str, observer):
        self.observers[event_type].append(observer)
    
    def notify(self, event_type: str, data):
        for observer in self.observers[event_type]:
            observer.handle_event(data)
```

### Design Principles

#### 1. SOLID Principles

**Single Responsibility Principle**
Each component has one reason to change:
```python
# Good: Each class has single responsibility
class BenchmarkRunner:  # Only runs benchmarks
    pass

class ResultAnalyzer:   # Only analyzes results
    pass

class ReportGenerator:  # Only generates reports
    pass
```

**Open/Closed Principle**
Components are open for extension but closed for modification:
```python
# Base adapter interface
class AgentAdapter(ABC):
    pass

# Extensions without modifying base
class OpenAIAgentAdapter(AgentAdapter):
    pass

class AnthropicAgentAdapter(AgentAdapter):
    pass
```

**Liskov Substitution Principle**
Derived classes can substitute base classes:
```python
# Any AgentAdapter can be used interchangeably
def run_agent_test(adapter: AgentAdapter):
    result = await adapter.query("Test prompt")
    return result

# Works with any adapter implementation
openai_result = run_agent_test(OpenAIAgentAdapter())
anthropic_result = run_agent_test(AnthropicAgentAdapter())
```

#### 2. Separation of Concerns
Different layers handle different responsibilities:

**Presentation Layer**
```python
# API routes - handles HTTP concerns
@app.post("/benchmark/run")
async def run_benchmark_endpoint(request: BenchmarkRequest):
    # Validation, error handling, HTTP response formatting
    pass
```

**Business Logic Layer**
```python
# Service layer - core business logic
class BenchmarkService:
    def process_benchmark(self, config):
        # Orchestration, business rules, workflow
        pass
```

**Data Access Layer**
```python
# Repository pattern - data persistence concerns
class BenchmarkRepository:
    def save_result(self, result):
        # Database operations, connection management
        pass
```

## 📊 Data Flow and Processing

### Complete Benchmark Workflow

```mermaid
sequenceDiagram
    participant Client
    participant APIGateway
    participant BenchmarkService
    participant TaskOrchestrator
    participant AgentAdapters
    participant EvaluationEngine
    participant Storage
    
    Client->>APIGateway: POST /benchmark/run
    APIGateway->>BenchmarkService: Forward request
    BenchmarkService->>TaskOrchestrator: Schedule benchmark
    TaskOrchestrator->>TaskOrchestrator: Load dataset
    loop For each question
        TaskOrchestrator->>AgentAdapters: Distribute to all agents
        par Agent responses
            AgentAdapters->>TaskOrchestrator: Return responses
            TaskOrchestrator->>EvaluationEngine: Send for evaluation
            EvaluationEngine->>EvaluationEngine: Process metrics
            EvaluationEngine->>Storage: Save results
        end
    end
    TaskOrchestrator->>BenchmarkService: Update status
    BenchmarkService->>APIGateway: Return status
    APIGateway->>Client: HTTP response
```

### Data Models

#### Benchmark Run
```python
class BenchmarkRun(BaseModel):
    run_id: str
    status: str  # queued, processing, completed, failed
    agents: List[str]
    benchmark_type: str
    config: Optional[Dict[str, Any]]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    progress: float  # 0.0 to 1.0
    results_url: Optional[str]
```

#### Agent Result
```python
class AgentResult(BaseModel):
    agent_id: str
    metrics: Dict[str, Any]  # accuracy, latency, tokens, consistency
    category_scores: Dict[str, float]  # mathematics, logic, etc.
    raw_responses: List[Dict[str, Any]]  # Individual question responses
```

#### Evaluation Metrics
```python
class EvaluationMetrics:
    def calculate_accuracy(self, correct_answers: int, total_questions: int) -> float:
        return (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    def calculate_consistency(self, responses: List[str]) -> float:
        # Implementation using similarity metrics
        pass
    
    def calculate_efficiency(self, tokens_used: int, time_taken: float) -> float:
        return tokens_used / time_taken if time_taken > 0 else 0
```

## 🛡️ Security Architecture

### Authentication and Authorization

#### API Key Authentication
```python
# Secure API key generation
import secrets
import hashlib

def generate_api_key() -> Tuple[str, str]:
    """Generate secure API key and hash for storage"""
    raw_key = secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    return raw_key, key_hash

# JWT token management
from jose import jwt
from datetime import datetime, timedelta

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

#### Role-Based Access Control (RBAC)
```python
# Permission scopes
PERMISSIONS = {
    "benchmark:read": ["view_benchmarks", "list_benchmarks"],
    "benchmark:write": ["create_benchmarks", "modify_benchmarks"],
    "results:read": ["view_results", "download_reports"],
    "admin:full": ["all_permissions"]
}

# Permission checking
def require_permission(required_permission: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Check user permissions
            user_permissions = get_user_permissions(current_user)
            if required_permission not in user_permissions:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### Data Protection

#### Encryption at Rest
```python
# Database encryption
# PostgreSQL with SSL/TLS
DATABASE_URL = "postgresql://user:pass@host:port/db?sslmode=require"

# Field-level encryption for sensitive data
from cryptography.fernet import Fernet

class SecureField:
    def __init__(self, key: bytes):
        self.cipher_suite = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
```

#### Data in Transit
```python
# HTTPS enforcement
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)

# Mutual TLS for service-to-service communication
SSL_CONTEXT = ssl.create_default_context(
    purpose=ssl.Purpose.CLIENT_AUTH,
    cafile="/path/to/ca.crt"
)
SSL_CONTEXT.load_cert_chain("/path/to/server.crt", "/path/to/server.key")
```

## 📈 Performance and Scalability

### Caching Strategies

#### Multi-Level Caching
```python
# Redis caching for frequently accessed data
import redis

redis_client = redis.Redis(host='redis', port=6379, db=0)

class CacheManager:
    def __init__(self):
        self.redis_client = redis_client
    
    @async_cache(expiration=300)  # 5 minutes
    async def get_benchmark_list(self):
        # Expensive database query
        pass
    
    def cache_evaluation_result(self, run_id: str, result: Dict):
        """Cache evaluation results temporarily"""
        key = f"evaluation:{run_id}"
        self.redis_client.setex(key, 3600, json.dumps(result))  # 1 hour
```

#### CDN for Static Assets
```python
# Static file serving optimization
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")

# CDN configuration for production
# Use services like Cloudflare, AWS CloudFront
CDN_ENABLED = os.getenv("CDN_ENABLED", "false").lower() == "true"
STATIC_BASE_URL = os.getenv("STATIC_BASE_URL", "/static")
```

### Load Balancing and Horizontal Scaling

#### Reverse Proxy Configuration
```nginx
# Nginx configuration for load balancing
upstream benchmark_backend {
    server web1:8000 weight=3;
    server web2:8000 weight=3;
    server web3:8000 backup;
}

server {
    listen 80;
    server_name api.benchmark.example.com;
    
    location / {
        proxy_pass http://benchmark_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Kubernetes Horizontal Pod Autoscaler
```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: benchmark-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: benchmark-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Database Optimization

#### Connection Pooling
```python
# SQLAlchemy connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600
)

# Async database operations
import asyncpg

async def fetch_benchmark_results(run_id: str):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        results = await conn.fetch(
            "SELECT * FROM benchmark_results WHERE run_id = $1 ORDER BY created_at",
            run_id
        )
        return [dict(row) for row in results]
    finally:
        await conn.close()
```

#### Query Optimization
```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_benchmarks_status ON benchmarks(status);
CREATE INDEX idx_benchmarks_created_at ON benchmarks(created_at);
CREATE INDEX idx_benchmark_results_run_id ON benchmark_results(run_id);
CREATE INDEX idx_benchmark_results_agent_id ON benchmark_results(agent_id);

-- Partition large tables
CREATE TABLE benchmark_results_2024_q1 (
    CHECK (created_at >= DATE '2024-01-01' AND created_at < DATE '2024-04-01')
) INHERITS (benchmark_results);
```

## 🛠️ Monitoring and Observability

### Distributed Tracing
```python
# OpenTelemetry integration
from opentelemetry import trace
from opentelemetry.trace import SpanKind
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Initialize tracer
tracer = trace.get_tracer(__name__)

@app.post("/benchmark/run")
async def run_benchmark(request: BenchmarkRequest):
    with tracer.start_as_current_span("run_benchmark", kind=SpanKind.SERVER) as span:
        span.set_attribute("benchmark.type", request.benchmark)
        span.set_attribute("agents.count", len(request.agents))
        
        # Business logic
        result = await process_benchmark(request)
        
        span.set_attribute("result.run_id", result.run_id)
        return result
```

### Metrics Collection
```python
# Prometheus metrics
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

# Instrument endpoints
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    RESPONSE_TIME.labels(endpoint=request.url.path).observe(process_time)
    REQUESTS.labels(
        endpoint=request.url.path,
        method=request.method,
        status=response.status_code
    ).inc()
    
    return response
```

### Structured Logging
```python
# Structured logging for better analysis
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def info(self, message: str, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": "INFO",
            "message": message,
            "data": kwargs
        }
        self.logger.info(json.dumps(log_entry))
    
    def error(self, message: str, **kwargs):
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
```

## 🔧 DevOps and Deployment

### Infrastructure as Code

#### Terraform Configuration
```hcl
# terraform/main.tf
resource "aws_ecs_cluster" "benchmark_cluster" {
  name = "benchmark-cluster"
}

resource "aws_ecs_task_definition" "benchmark_service" {
  family                   = "benchmark-service"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 1024
  memory                   = 2048
  
  container_definitions = jsonencode([
    {
      name      = "web"
      image     = "your-account.dkr.ecr.us-east-1.amazonaws.com/benchmark-service:latest"
      cpu       = 512
      memory    = 1024
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]
    }
  ])
}
```

#### Kubernetes Manifests
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: benchmark-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: benchmark
  template:
    metadata:
      labels:
        app: benchmark
    spec:
      containers:
      - name: web
        image: benchmark-service:latest
        ports:
        - containerPort: 8000
        envFrom:
        - secretRef:
            name: benchmark-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 30
```

### CI/CD Pipeline

#### GitHub Actions Workflow
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: pytest --cov=benchmark_service
    
    - name: Upload coverage
      uses: codecov/codecov-action@v4

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Login to DockerHub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    
    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: your-account/benchmark-service:latest
```

## 📚 Additional Resources

### Related Projects

1. **LangChain**: Framework for building LLM applications
2. **LlamaIndex**: Data framework for LLM applications
3. **Weights & Biases**: ML experiment tracking
4. **Ray**: Distributed computing framework

### Standards and Best Practices

1. **Twelve-Factor App**: Methodology for cloud-native applications
2. **OWASP Top 10**: Security best practices
3. **SOLID Principles**: Object-oriented design principles
4. **Microservices Patterns**: Design patterns for distributed systems

### Further Reading

1. **Designing Data-Intensive Applications** by Martin Kleppmann
2. **Building Microservices** by Sam Newman
3. **Site Reliability Engineering** by Google
4. **Clean Architecture** by Robert C. Martin

This architecture documentation provides a comprehensive overview of the AI Benchmark Service design and implementation. Regular updates ensure that architectural decisions remain current and well-documented.