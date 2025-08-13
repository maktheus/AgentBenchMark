# 🧪 Testing Strategy and Implementation

This document outlines the comprehensive testing strategy for the AI Benchmark Service, including unit tests, integration tests, end-to-end tests, and performance testing.

## 📋 Testing Philosophy

### Test Pyramid Approach

```mermaid
graph TD
    A[Unit Tests<br/>70%] --> B[Integration Tests<br/>20%]
    B --> C[End-to-End Tests<br/>10%]
    
    style A fill:#e8f5e8
    style B fill:#fff3e0
    style C fill:#f1f8e9
```

### Testing Principles

1. **Fast Feedback**: Tests should run quickly to provide immediate feedback
2. **Reliable**: Tests should produce consistent results
3. **Independent**: Tests should not depend on each other
4. **Specific**: Each test should verify one specific behavior
5. **Readable**: Tests should be easy to understand and maintain

## 🧪 Unit Testing

### Test Structure

```python
# tests/unit/test_agents.py
import pytest
from unittest.mock import patch, AsyncMock
from agents.openai_adapter import OpenAIAgentAdapter, OpenAIConfig

class TestOpenAIAgentAdapter:
    """Unit tests for OpenAI Agent Adapter"""
    
    @pytest.fixture
    def adapter_config(self):
        """Fixture for adapter configuration"""
        return OpenAIConfig(
            api_key="test-key",
            model="gpt-4-turbo",
            temperature=0.7
        )
    
    @pytest.mark.asyncio
    async def test_successful_query(self, adapter_config):
        """Test successful API query with valid response"""
        # Arrange
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}],
            "usage": {"total_tokens": 50}
        }
        mock_response.elapsed.total_seconds.return_value = 0.5
        
        with patch("httpx.AsyncClient.post", return_value=mock_response):
            # Act
            adapter = OpenAIAgentAdapter(adapter_config)
            result = await adapter.query("Hello", {"context": "test"})
            
            # Assert
            assert result["response"] == "Test response"
            assert result["usage"]["total_tokens"] == 50
            assert 0.4 <= result["latency"] <= 0.6
    
    @pytest.mark.asyncio
    async def test_query_with_http_error(self, adapter_config):
        """Test query handling of HTTP errors"""
        # Arrange
        with patch("httpx.AsyncClient.post", side_effect=httpx.HTTPStatusError(
            "API Error", 
            request=None, 
            response=httpx.Response(500, text="Internal Server Error")
        )):
            # Act
            adapter = OpenAIAgentAdapter(adapter_config)
            result = await adapter.query("Hello")
            
            # Assert
            assert "error" in result
            assert "API Error" in result["error"]
```

### Mocking Strategy

#### HTTP Clients
```python
# Mock external HTTP calls
@patch("httpx.AsyncClient.post")
async def test_external_api_call(mock_post):
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    mock_post.return_value = mock_response
    
    # Test implementation
    result = await service.call_external_api()
    assert result == {"data": "test"}
```

#### Database Connections
```python
# Mock database operations
@patch("sqlalchemy.create_engine")
def test_database_query(mock_engine):
    mock_session = MagicMock()
    mock_engine.return_value.connect.return_value.__enter__.return_value = mock_session
    mock_session.execute.return_value.fetchall.return_value = [("test",)]
    
    # Test implementation
    result = service.query_database()
    assert result == [("test",)]
```

#### Time-Dependent Operations
```python
# Mock time for consistent testing
@patch("time.time")
def test_timeout_logic(mock_time):
    mock_time.side_effect = [0, 5]  # 5 seconds elapsed
    
    # Test implementation
    result = service.operation_with_timeout()
    assert result == "timeout"
```

## 🔗 Integration Testing

### API Integration Tests

```python
# tests/integration/test_api.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestBenchmarkAPI:
    """Integration tests for Benchmark API endpoints"""
    
    def test_create_benchmark_success(self):
        """Test successful benchmark creation"""
        # Arrange
        payload = {
            "agents": ["gpt-4-turbo"],
            "benchmark": "mmlu-reasoning-v1",
            "config": {"temperature": 0.7}
        }
        
        # Act
        response = client.post("/api/benchmark/run", json=payload)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "run_id" in data
        assert data["status"] == "queued"
        assert data["agents"] == ["gpt-4-turbo"]
    
    def test_get_benchmark_status(self):
        """Test retrieving benchmark status"""
        # Arrange
        create_response = client.post("/api/benchmark/run", json={
            "agents": ["gpt-4-turbo"],
            "benchmark": "mmlu-reasoning-v1"
        })
        run_id = create_response.json()["run_id"]
        
        # Act
        response = client.get(f"/api/benchmark/{run_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["run_id"] == run_id
        assert data["status"] in ["queued", "processing", "completed"]
```

### Database Integration Tests

```python
# tests/integration/test_database.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import BenchmarkRun

class TestDatabaseOperations:
    """Integration tests for database operations"""
    
    @pytest.fixture(scope="class")
    def db_session(self):
        """Create database session for testing"""
        engine = create_engine("sqlite:///test.db")
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    def test_create_benchmark_run(self, db_session):
        """Test creating benchmark run in database"""
        # Arrange
        benchmark_run = BenchmarkRun(
            run_id="test-run-123",
            status="queued",
            agents=["gpt-4"],
            benchmark_type="mmlu-reasoning-v1"
        )
        
        # Act
        db_session.add(benchmark_run)
        db_session.commit()
        
        # Assert
        retrieved = db_session.query(BenchmarkRun).filter_by(run_id="test-run-123").first()
        assert retrieved is not None
        assert retrieved.status == "queued"
        assert retrieved.agents == ["gpt-4"]
```

## 🌐 End-to-End Testing

### Complete Workflow Tests

```python
# tests/e2e/test_full_workflow.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestFullBenchmarkWorkflow:
    """End-to-end tests for complete benchmark workflow"""
    
    def test_complete_benchmark_execution(self):
        """Test complete benchmark execution from start to finish"""
        # Step 1: Health check
        health_response = client.get("/health")
        assert health_response.status_code == 200
        assert health_response.json() == {"status": "healthy"}
        
        # Step 2: List available benchmarks
        list_response = client.get("/api/benchmark/list")
        assert list_response.status_code == 200
        benchmarks = list_response.json()
        assert len(benchmarks) > 0
        
        # Step 3: Submit benchmark
        submit_payload = {
            "agents": ["gpt-4-turbo", "claude-3-opus"],
            "benchmark": "mmlu-reasoning-v1",
            "config": {"temperature": 0.7}
        }
        
        submit_response = client.post("/api/benchmark/run", json=submit_payload)
        assert submit_response.status_code == 200
        run_id = submit_response.json()["run_id"]
        
        # Step 4: Monitor progress
        status_response = client.get(f"/api/benchmark/{run_id}")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["run_id"] == run_id
        
        # Step 5: Get results (simulated completion)
        # In real scenario, this would involve waiting for processing
        # For testing, we simulate completion by directly setting results
        
        # Step 6: Verify results structure
        results_payload = {
            "run_id": run_id,
            "benchmark": "mmlu-reasoning-v1",
            "agents": [
                {
                    "id": "gpt-4-turbo",
                    "metrics": {
                        "accuracy": 87.3,
                        "latency_avg": 4.2,
                        "tokens_avg": 1428,
                        "consistency": 4.7
                    },
                    "category_scores": {
                        "mathematics": 92.4,
                        "logical_reasoning": 88.2
                    }
                }
            ],
            "summary": {
                "top_performer": "gpt-4-turbo",
                "critical_observations": [
                    "Melhor desempenho em raciocínio matemático",
                    "Consistência superior em múltiplas categorias"
                ]
            }
        }
        
        # Simulate results being available
        # In production, this would be set by the worker
        import benchmark_service.api.routes as routes
        routes.benchmark_results[run_id] = results_payload
        
        results_response = client.get(f"/api/benchmark/results/{run_id}")
        assert results_response.status_code == 200
        results_data = results_response.json()
        
        # Verify results structure
        assert results_data["run_id"] == run_id
        assert results_data["benchmark"] == "mmlu-reasoning-v1"
        assert len(results_data["agents"]) == 1
        assert results_data["agents"][0]["id"] == "gpt-4-turbo"
        
        # Cleanup
        if run_id in routes.benchmark_results:
            del routes.benchmark_results[run_id]
```

## 📈 Performance Testing

### Load Testing with Locust

```python
# locustfile.py
from locust import HttpUser, task, between, constant_pacing
import random
import uuid

class BenchmarkUser(HttpUser):
    """Load testing user for benchmark service"""
    
    # Wait time between tasks
    wait_time = between(1, 3)
    
    # Available agents for testing
    AGENT_LIST = [
        "gpt-4-turbo",
        "claude-3-opus",
        "gpt-4",
        "claude-3-sonnet"
    ]
    
    # Available benchmarks
    BENCHMARK_TYPES = [
        "mmlu-reasoning-v1",
        "gsm8k-math-v2"
    ]
    
    def on_start(self):
        """Initialize user session"""
        self.headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json"
        }
    
    @task(10)
    def submit_benchmark(self):
        """Submit a new benchmark for processing"""
        payload = {
            "agents": random.sample(self.AGENT_LIST, k=random.randint(1, 3)),
            "benchmark": random.choice(self.BENCHMARK_TYPES),
            "config": {
                "temperature": round(random.uniform(0.1, 1.0), 1),
                "max_tokens": random.randint(512, 2048)
            }
        }
        
        with self.client.post(
            "/api/benchmark/run",
            json=payload,
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(3)
    def check_benchmark_status(self):
        """Check status of a random benchmark"""
        # In a real test, you would track run IDs from submitted benchmarks
        # For demo purposes, we use a fixed ID
        run_id = str(uuid.uuid4())
        
        with self.client.get(
            f"/api/benchmark/{run_id}",
            headers=self.headers,
            catch_response=True
        ) as response:
            # Expect 404 for non-existent benchmark
            if response.status_code == 404:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(1)
    def list_benchmarks(self):
        """List available benchmarks"""
        with self.client.get(
            "/api/benchmark/list",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

# Expected Results for 100 RPS
"""
Type     Name                           # reqs      # fails  |     Avg     Min     Max  Median  |   req/s failures/s
--------|------------------------------|-------|-----------|--------|-------|-------|--------|-------|-----------
POST     /api/benchmark/run             14,235     0(0.00%)  |    412     123    2487     389  |   47.50    0.00
GET      /api/benchmark/{id}             4,028     0(0.00%)  |     98      45     512      95  |   13.45    0.00
GET      /api/benchmark/list             2,015     0(0.00%)  |     76      32     387      72  |    6.73    0.00
--------|------------------------------|-------|-----------|--------|-------|-------|--------|-------|-----------
         Aggregated                     20,278     0(0.00%)  |    312     32    2487     287  |   67.68    0.00
"""
```

### Stress Testing Scenarios

#### High Concurrency Test
```python
# tests/stress/test_high_concurrency.py
import asyncio
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.mark.stress
def test_high_concurrency_stress():
    """Test system under high concurrent load"""
    
    def make_request():
        """Make a single benchmark request"""
        payload = {
            "agents": ["gpt-4-turbo"],
            "benchmark": "mmlu-reasoning-v1"
        }
        return client.post("/api/benchmark/run", json=payload)
    
    # Simulate 100 concurrent requests
    async def run_concurrent_requests():
        tasks = [asyncio.create_task(make_request()) for _ in range(100)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        return responses
    
    # Run the stress test
    responses = asyncio.run(run_concurrent_requests())
    
    # Verify results
    successful_requests = 0
    for response in responses:
        if not isinstance(response, Exception) and response.status_code == 200:
            successful_requests += 1
    
    # Expect at least 95% success rate
    assert successful_requests >= 95, f"Only {successful_requests}/100 requests succeeded"
```

#### Long Duration Test
```python
# tests/stress/test_long_duration.py
import time
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.mark.stress
def test_long_duration_stability():
    """Test system stability over extended period"""
    
    start_time = time.time()
    requests_made = 0
    successful_requests = 0
    
    # Run for 15 minutes
    while time.time() - start_time < 900:  # 15 minutes
        payload = {
            "agents": ["gpt-4-turbo"],
            "benchmark": "mmlu-reasoning-v1"
        }
        
        response = client.post("/api/benchmark/run", json=payload)
        requests_made += 1
        
        if response.status_code == 200:
            successful_requests += 1
        
        # Wait 1 second between requests
        time.sleep(1)
        
        # Periodic check-in
        if requests_made % 60 == 0:  # Every minute
            success_rate = successful_requests / requests_made
            print(f"Progress: {requests_made} requests, {success_rate:.2%} success rate")
    
    # Final assertions
    final_success_rate = successful_requests / requests_made
    assert final_success_rate >= 0.99, f"Success rate {final_success_rate:.2%} below threshold"
    assert requests_made >= 850, f"Too few requests made: {requests_made}"
```

## 🛡️ Security Testing

### Dependency Security Scanning

```bash
# Safety - Check for known vulnerabilities in dependencies
pip install safety
safety check -r requirements.txt

# Bandit - Static analysis for Python security issues
pip install bandit
bandit -r benchmark_service/

# Detect-secrets - Find secrets in code
pip install detect-secrets
detect-secrets scan > .secrets.baseline
```

### API Security Tests

```python
# tests/security/test_api_security.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestAPISecurity:
    """Security tests for API endpoints"""
    
    def test_unauthorized_access(self):
        """Test unauthorized access to protected endpoints"""
        response = client.post("/api/benchmark/run", json={})
        assert response.status_code == 403  # Forbidden
    
    def test_invalid_input_validation(self):
        """Test input validation for malicious payloads"""
        malicious_payload = {
            "agents": ["gpt-4"]; DROP TABLE benchmarks; --",
            "benchmark": "<script>alert('xss')</script>"
        }
        
        response = client.post("/api/benchmark/run", json=malicious_payload)
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_rate_limiting(self):
        """Test API rate limiting"""
        # Make multiple rapid requests
        responses = []
        for _ in range(100):
            response = client.get("/api/benchmark/list")
            responses.append(response)
        
        # Check if rate limiting kicked in
        rate_limited_responses = [r for r in responses if r.status_code == 429]
        assert len(rate_limited_responses) > 0, "Rate limiting not triggered"
```

## 📊 Test Coverage and Reporting

### Coverage Configuration

```python
# pyproject.toml or setup.cfg
[tool.coverage.run]
source = ["benchmark_service"]
omit = [
    "*/tests/*",
    "*/migrations/*",
    "*/venv/*",
    "*/__pycache__/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:"
]

[tool.coverage.html]
directory = "htmlcov"
```

### Coverage Targets

```python
# Target coverage percentages by component
COVERAGE_TARGETS = {
    "core_services": 95,      # Business logic services
    "api_endpoints": 90,       # API route handlers
    "agents": 90,             # Agent adapters
    "evaluators": 95,         # Evaluation logic
    "workers": 85,            # Background workers
    "utils": 80,              # Utility functions
    "models": 90,             # Data models
    "exceptions": 100          # Error handling
}
```

### Coverage Reports

```bash
# Generate coverage report
pytest --cov=benchmark_service --cov-report=html --cov-report=term

# Generate XML report for CI/CD
pytest --cov=benchmark_service --cov-report=xml

# Generate detailed coverage per file
pytest --cov=benchmark_service --cov-report=term-missing
```

## 🚀 Test Automation and CI/CD

### GitHub Actions Workflow

```yaml
# .github/workflows/testing.yml
name: Testing Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-asyncio
    
    - name: Run unit tests
      run: pytest tests/unit/ --cov=benchmark_service
    
    - name: Upload coverage
      uses: codecov/codecov-action@v4
      with:
        file: ./coverage.xml

  integration-tests:
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
        pip install pytest pytest-asyncio
    
    - name: Run integration tests
      run: pytest tests/integration/
      env:
        DATABASE_URL: postgresql://test_user:test_password@localhost:5432/test_db

  e2e-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio
    
    - name: Run end-to-end tests
      run: pytest tests/e2e/

  security-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install security tools
      run: |
        pip install safety bandit
    
    - name: Run dependency security scan
      run: safety check -r requirements.txt
    
    - name: Run static analysis
      run: bandit -r benchmark_service/
```

## 📈 Performance Benchmarks

### Expected Performance Metrics

#### Throughput Targets
```python
# Performance targets by environment
PERFORMANCE_TARGETS = {
    "development": {
        "min_rps": 10,
        "max_latency_p95": 5.0,  # seconds
        "error_rate": 0.01        # 1%
    },
    "staging": {
        "min_rps": 50,
        "max_latency_p95": 2.0,
        "error_rate": 0.005
    },
    "production": {
        "min_rps": 100,
        "max_latency_p95": 1.0,
        "error_rate": 0.001
    }
}
```

#### Resource Utilization
```python
# Expected resource usage
RESOURCE_UTILIZATION = {
    "cpu_utilization": {
        "average": "< 70%",
        "peak": "< 90%"
    },
    "memory_utilization": {
        "average": "< 80%",
        "peak": "< 95%"
    },
    "database_connections": {
        "active": "< 80% of pool",
        "idle": "> 20% of pool"
    }
}
```

### Performance Regression Testing

```python
# tests/performance/test_regression.py
import pytest
import time
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestPerformanceRegression:
    """Performance regression tests"""
    
    @pytest.mark.performance
    def test_api_response_time(self):
        """Test API response time hasn't regressed"""
        start_time = time.time()
        
        response = client.get("/api/benchmark/list")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0, f"Response time {response_time:.3f}s exceeds threshold"
    
    @pytest.mark.performance
    def test_benchmark_creation_time(self):
        """Test benchmark creation time hasn't regressed"""
        payload = {
            "agents": ["gpt-4-turbo", "claude-3-opus"],
            "benchmark": "mmlu-reasoning-v1"
        }
        
        start_time = time.time()
        
        response = client.post("/api/benchmark/run", json=payload)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        assert response.status_code == 200
        assert creation_time < 2.0, f"Creation time {creation_time:.3f}s exceeds threshold"
```

## 📚 Test Documentation Standards

### Test Case Documentation Template

```python
def test_function_name():
    """
    Test Description: Brief description of what this test verifies
    
    Preconditions:
    - List of conditions that must be met before test execution
    
    Test Steps:
    1. Step description
    2. Step description
    3. Step description
    
    Expected Results:
    - What should happen when test executes successfully
    
    Edge Cases Covered:
    - Edge case 1
    - Edge case 2
    
    Failure Conditions:
    - When should this test fail
    """
    pass
```

### Test Data Management

```python
# tests/conftest.py
import pytest
import tempfile
import shutil
from pathlib import Path

@pytest.fixture(scope="session")
def test_data_dir():
    """Create temporary directory for test data"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_benchmark_data():
    """Sample benchmark data for testing"""
    return {
        "benchmark_id": "test-benchmark-v1",
        "description": "Test benchmark for unit testing",
        "categories": ["mathematics", "logic"],
        "data": [
            {
                "id": "math-001",
                "category": "mathematics",
                "question": "What is 2+2?",
                "options": ["A) 3", "B) 4", "C) 5", "D) 6"],
                "answer": "B"
            }
        ]
    }
```

This comprehensive testing documentation provides a complete framework for ensuring the quality, reliability, and performance of the AI Benchmark Service. Regular updates to test suites ensure that the system maintains high quality as new features are added.