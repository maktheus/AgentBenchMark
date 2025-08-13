# 👨‍💻 Development Guide

This guide provides comprehensive information for developers working on the AI Benchmark Service.

## 🚀 Getting Started

### Prerequisites

Before you begin development, ensure you have:

1. **Python 3.11+**
2. **Docker** (version 20.10 or higher)
3. **Docker Compose** (version 2.10 or higher)
4. **Git** for version control
5. **Code editor** (VS Code, PyCharm, etc.)

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/your-org/benchmark-service.git
cd benchmark-service

# Setup development environment
make setup

# Start development environment
make dev

# Run tests to verify setup
make test
```

### Project Structure

```
ai-benchmark-service/
├── benchmark_service/          # Main application code
│   ├── agents/                 # Agent adapters and interfaces
│   ├── analytics/              # Analytics and data deduction
│   ├── api/                    # API routes and handlers
│   ├── datasets/               # Benchmark datasets
│   ├── evaluators/             # Result evaluation logic
│   ├── models/                 # Data models and schemas
│   ├── services/               # Business logic services
│   ├── workers/                # Background workers
│   └── __init__.py
├── docs/                       # Documentation
├── grafana/                    # Grafana configuration
├── k8s/                        # Kubernetes manifests
├── locust/                     # Load testing scripts
├── prometheus/                 # Prometheus configuration
├── scripts/                    # Utility scripts
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── e2e/                    # End-to-end tests
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Main Dockerfile
├── requirements.txt            # Python dependencies
├── Makefile                    # Development commands
└── README.md                   # Project overview
```

## 🛠️ Development Workflow

### 1. Create a Feature Branch

```bash
# Create and switch to a new branch
git checkout -b feature/new-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

### 2. Install Dependencies

```bash
# Install new dependencies
pip install new-package-name

# Update requirements.txt
pip freeze > requirements.txt

# Install all dependencies (if needed)
make setup
```

### 3. Write Code

Follow the project's coding standards:

- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Follow PEP 8 style guide
- Use meaningful variable and function names

### 4. Write Tests

```python
# Example test structure
import pytest
from unittest.mock import patch, AsyncMock

def test_example_function():
    """Test description"""
    # Arrange
    # Set up test data and mocks
    
    # Act
    # Execute the function being tested
    
    # Assert
    # Verify the results
    assert expected_result == actual_result
```

### 5. Run Tests

```bash
# Run all tests
make test

# Run specific test types
make test-unit
make test-integration
make test-e2e

# Run tests with coverage
make test-coverage
```

### 6. Code Quality Checks

```bash
# Format code
make format

# Lint code
make lint

# Type checking
make type-check

# Run all quality checks
make quality
```

### 7. Commit Changes

```bash
# Add changed files
git add .

# Commit with conventional commit message
git commit -m "feat: add new benchmark feature"

# Push to remote
git push origin feature/new-feature-name
```

## 🧪 Testing Strategy

### Test Structure

The project follows a three-level testing approach:

1. **Unit Tests** (`tests/unit/`)
   - Test individual functions and classes in isolation
   - Use mocks to isolate dependencies
   - Fast execution (milliseconds)
   - High code coverage target (90%+)

2. **Integration Tests** (`tests/integration/`)
   - Test component interactions
   - Use real (but isolated) services
   - Verify API contracts
   - Moderate execution time (seconds)

3. **End-to-End Tests** (`tests/e2e/`)
   - Test complete workflows
   - Simulate real user scenarios
   - Validate system behavior
   - Slower execution (tens of seconds)

### Writing Unit Tests

```python
import pytest
from unittest.mock import patch, MagicMock
from benchmark_service.agents.openai_adapter import OpenAIAgentAdapter

def test_openai_adapter_success():
    """Test successful OpenAI API call"""
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Test response"}}]
    }
    
    with patch("httpx.AsyncClient.post", return_value=mock_response):
        # Act
        adapter = OpenAIAgentAdapter(config)
        result = await adapter.query("Test prompt")
        
        # Assert
        assert result["response"] == "Test response"
```

### Writing Integration Tests

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_api_endpoint_integration():
    """Test complete API endpoint integration"""
    # Arrange
    payload = {"agents": ["gpt-4"], "benchmark": "test-benchmark"}
    
    # Act
    response = client.post("/api/benchmark/run", json=payload)
    
    # Assert
    assert response.status_code == 200
    assert "run_id" in response.json()
```

### Writing End-to-End Tests

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_complete_benchmark_workflow():
    """Test complete benchmark execution workflow"""
    # 1. Start benchmark
    start_response = client.post("/api/benchmark/run", json=payload)
    assert start_response.status_code == 200
    
    run_id = start_response.json()["run_id"]
    
    # 2. Check status
    status_response = client.get(f"/api/benchmark/{run_id}")
    assert status_response.status_code == 200
    
    # 3. Get results
    results_response = client.get(f"/api/benchmark/results/{run_id}")
    assert results_response.status_code == 200
    
    # 4. Validate results structure
    results = results_response.json()
    assert "agents" in results
    assert "summary" in results
```

## 🐳 Docker Development

### Development Containers

The development environment uses Docker Compose to run all services:

```bash
# Start development environment
make dev

# View logs
make dev-logs

# Stop environment
make dev-down

# Rebuild environment
make dev-rebuild
```

### Customizing Development Environment

Edit `docker-compose.yml` to modify service configurations:

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=true  # Enable debug mode
    volumes:
      - .:/app      # Mount source code for development
```

### Debugging Containers

```bash
# Access container shell
docker-compose exec web bash

# View container logs
docker-compose logs web

# Restart specific service
docker-compose restart web
```

## 📊 Database Development

### Database Schema

The project uses PostgreSQL with the following schema:

```sql
-- Benchmarks table
CREATE TABLE benchmarks (
    id SERIAL PRIMARY KEY,
    run_id UUID UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL,
    agents JSONB,
    benchmark_type VARCHAR(100) NOT NULL,
    config JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    progress DECIMAL(5,2) DEFAULT 0.0
);

-- Results table
CREATE TABLE benchmark_results (
    id SERIAL PRIMARY KEY,
    run_id UUID REFERENCES benchmarks(run_id),
    agent_id VARCHAR(100),
    metrics JSONB,
    category_scores JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Database Migrations

Use Alembic for database migrations:

```bash
# Generate new migration
alembic revision -m "add new feature"

# Apply migrations
make db-migrate

# Reset database
make db-reset
```

### Database Development Tips

```python
# Use connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10
)

# Use context managers for connections
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    conn = engine.connect()
    try:
        yield conn
    finally:
        conn.close()
```

## 📈 Analytics Development

### Adding New Analytics Features

1. **Create new analytics module** in `benchmark_service/analytics/`
2. **Implement analysis methods** with clear input/output contracts
3. **Add unit tests** for new functionality
4. **Integrate with worker** to process results
5. **Expose via API** in appropriate endpoints

### Example Analytics Implementation

```python
class AdvancedAnalytics:
    def __init__(self):
        self.ml_model = self._load_model()
    
    def analyze_performance_trends(self, historical_data):
        """Analyze performance trends over time"""
        # Implementation
        pass
    
    def predict_optimal_configurations(self, agent_performance):
        """Predict optimal configurations for agents"""
        # Implementation
        pass
    
    def _load_model(self):
        """Load machine learning model"""
        # Implementation
        pass
```

## 🤖 Agent Development

### Adding New Agent Types

1. **Create new adapter** in `benchmark_service/agents/`
2. **Implement AgentInterface** methods
3. **Add configuration class** for agent-specific settings
4. **Register adapter** in `benchmark_service/agents/__init__.py`
5. **Add tests** for new adapter
6. **Update worker** to support new agent type

### Example Agent Adapter

```python
from .base import AgentInterface

class CustomAgentAdapter(AgentInterface):
    def __init__(self, config: CustomAgentConfig):
        self.config = config
        self.client = self._create_client()
    
    async def query(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send query to custom agent"""
        try:
            response = await self.client.send_request(prompt, context)
            return {
                "response": response.text,
                "usage": response.usage,
                "latency": response.latency
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "name": "custom-agent",
            "version": self.config.version,
            "capabilities": ["text-generation", "reasoning"]
        }
    
    def _create_client(self):
        """Create HTTP client for agent"""
        # Implementation
        pass
```

## 🔧 Debugging and Troubleshooting

### Common Development Issues

#### 1. Import Errors

```bash
# Solution: Check Python path
export PYTHONPATH=/path/to/project:$PYTHONPATH

# Or use relative imports
from ..agents.openai_adapter import OpenAIAgentAdapter
```

#### 2. Database Connection Issues

```bash
# Check if database is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U benchmark_user -d benchmark_db
```

#### 3. Dependency Issues

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Clear pip cache
pip cache purge

# Check for conflicting dependencies
pip check
```

### Debugging Tools

#### 1. Logging

```python
import logging

logger = logging.getLogger(__name__)

def example_function():
    logger.debug("Debug information")
    logger.info("Process information")
    logger.warning("Warning message")
    logger.error("Error occurred")
    logger.critical("Critical error")
```

#### 2. Debugging with pdb

```python
import pdb

def problematic_function():
    pdb.set_trace()  # Debugger will stop here
    # Your code here
    pass
```

#### 3. Profiling

```python
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Code to profile
    your_function()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Print top 10 functions
```

## 📈 Performance Optimization

### Code Optimization

#### 1. Async/Await Patterns

```python
# Good: Use async for I/O operations
async def process_benchmark(run_id):
    await database_query()
    await external_api_call()

# Bad: Blocking operations in async functions
async def process_benchmark_bad(run_id):
    time.sleep(1)  # This blocks the event loop
```

#### 2. Caching Strategies

```python
import redis
from functools import lru_cache

# Redis caching
redis_client = redis.Redis()

def get_cached_data(key):
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    
    data = compute_expensive_operation()
    redis_client.setex(key, 300, json.dumps(data))
    return data

# In-memory caching
@lru_cache(maxsize=128)
def expensive_function(param):
    # Expensive computation
    return result
```

#### 3. Database Optimization

```python
# Use connection pooling
from sqlalchemy import create_engine

engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=10)

# Use bulk operations
def insert_multiple_results(results):
    with engine.connect() as conn:
        conn.execute(
            benchmark_results.insert(),
            results
        )
```

## 🛡️ Security Development

### Secure Coding Practices

#### 1. Input Validation

```python
from pydantic import BaseModel, validator

class BenchmarkRequest(BaseModel):
    agents: List[str]
    benchmark: str
    
    @validator('agents')
    def validate_agents(cls, v):
        if not v or len(v) > 10:
            raise ValueError('Invalid number of agents')
        return v
```

#### 2. SQL Injection Prevention

```python
# Good: Parameterized queries
cursor.execute("SELECT * FROM benchmarks WHERE run_id = %s", (run_id,))

# Bad: String concatenation
cursor.execute(f"SELECT * FROM benchmarks WHERE run_id = '{run_id}'")
```

#### 3. XSS Prevention

```python
import html

def sanitize_output(data):
    """Sanitize data for HTML output"""
    if isinstance(data, str):
        return html.escape(data)
    return data
```

## 📚 Documentation Development

### API Documentation

The API documentation is auto-generated using FastAPI's built-in OpenAPI support:

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/benchmark/{run_id}")
async def get_benchmark_status(run_id: str):
    """
    Get the status of a specific benchmark run.
    
    Args:
        run_id (str): The unique identifier of the benchmark run
        
    Returns:
        dict: Benchmark status information
        
    Raises:
        HTTPException: If benchmark not found (404)
    """
    # Implementation
    pass
```

### Code Documentation

Follow docstring conventions:

```python
def calculate_accuracy(correct_answers: int, total_questions: int) -> float:
    """
    Calculate accuracy percentage.
    
    Args:
        correct_answers (int): Number of correct answers
        total_questions (int): Total number of questions
        
    Returns:
        float: Accuracy percentage (0-100)
        
    Raises:
        ValueError: If total_questions is zero
        
    Example:
        >>> calculate_accuracy(85, 100)
        85.0
    """
    if total_questions == 0:
        raise ValueError("Total questions cannot be zero")
    
    return (correct_answers / total_questions) * 100
```

## 🔄 CI/CD Integration

### GitHub Actions Workflow

The project includes automated CI/CD workflows:

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on: [push, pull_request]

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
```

### Local Development Testing

```bash
# Run CI/CD pipeline locally
act pull_request

# Or use the same commands as GitHub Actions
pip install -r requirements.txt
pytest --cov=benchmark_service
```

## 🎯 Best Practices

### Code Quality

1. **Follow PEP 8**: Use consistent formatting
2. **Use type hints**: Improve code clarity and catch errors
3. **Write docstrings**: Document all public interfaces
4. **Keep functions small**: Single responsibility principle
5. **Use meaningful names**: Clear, descriptive variable names

### Testing

1. **Test edge cases**: Boundary conditions and error scenarios
2. **Use descriptive test names**: `test_function_name_scenario_expected_result`
3. **Mock external dependencies**: Isolate unit tests
4. **Maintain test data**: Use factories or fixtures
5. **Run tests regularly**: Before each commit

### Performance

1. **Profile before optimizing**: Identify actual bottlenecks
2. **Use async/await**: For I/O bound operations
3. **Cache appropriately**: Avoid repeated expensive operations
4. **Batch operations**: Reduce database round trips
5. **Monitor resource usage**: CPU, memory, disk I/O

### Security

1. **Validate all inputs**: Never trust external data
2. **Sanitize outputs**: Prevent XSS attacks
3. **Use parameterized queries**: Prevent SQL injection
4. **Store secrets securely**: Environment variables, not code
5. **Implement proper authentication**: JWT, API keys

### Documentation

1. **Keep docs updated**: Update with code changes
2. **Use examples**: Show real usage scenarios
3. **Document APIs**: Clear endpoint descriptions
4. **Include error cases**: Expected error responses
5. **Maintain changelog**: Track version changes

This development guide provides comprehensive information for contributing to the AI Benchmark Service. Regular updates to this guide ensure that development practices remain current and effective.