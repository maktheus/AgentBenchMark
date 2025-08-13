# 🤝 Contribution Guide

Thank you for your interest in contributing to the AI Benchmark Service! This guide will help you understand how to contribute effectively to the project.

## 🎯 Getting Started

### Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming and inclusive community for everyone.

### Ways to Contribute

There are many ways to contribute to the AI Benchmark Service:

1. **Code Contributions**
   - Bug fixes
   - New features
   - Performance improvements
   - New agent adapters
   - New benchmark datasets

2. **Documentation**
   - Improving existing documentation
   - Translating documentation
   - Adding examples and tutorials
   - Writing API documentation

3. **Testing**
   - Writing unit tests
   - Writing integration tests
   - Performance testing
   - Security testing

4. **Community Support**
   - Answering questions on GitHub Issues
   - Helping with user support
   - Improving community resources

5. **Design and UX**
   - Improving dashboard designs
   - Creating visual assets
   - Enhancing user experience

## 🛠️ Development Setup

### Prerequisites

Before you start contributing, make sure you have:

1. **Python 3.11+**
2. **Docker** (version 20.10 or higher)
3. **Docker Compose** (version 2.10 or higher)
4. **Git** for version control
5. **Code editor** (VS Code, PyCharm, etc.)

### Setting Up Your Development Environment

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/benchmark-service.git
cd benchmark-service

# 3. Add upstream remote
git remote add upstream https://github.com/original-org/benchmark-service.git

# 4. Install dependencies
make setup

# 5. Start development environment
make dev

# 6. Run tests to verify setup
make test
```

### Project Structure Overview

```
benchmark-service/
├── benchmark_service/          # Main application code
│   ├── agents/               # Agent adapters and interfaces
│   ├── analytics/            # Analytics and data deduction
│   ├── api/                  # API routes and handlers
│   ├── datasets/             # Benchmark datasets
│   ├── evaluators/           # Result evaluation logic
│   ├── models/               # Data models and schemas
│   ├── services/              # Business logic services
│   ├── workers/              # Background workers
│   └── __init__.py
├── docs/                     # Documentation
├── grafana/                  # Grafana configuration
├── k8s/                      # Kubernetes manifests
├── locust/                   # Load testing scripts
├── prometheus/               # Prometheus configuration
├── scripts/                  # Utility scripts
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   ├── e2e/                  # End-to-end tests
│   └── performance/           # Performance tests
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile                # Main Dockerfile
├── requirements.txt          # Python dependencies
├── Makefile                  # Development commands
└── README.md                # Project overview
```

## 📝 Contribution Process

### 1. Find an Issue

Look for issues labeled:
- `good first issue` - Great for newcomers
- `help wanted` - Ready for contribution
- `bug` - Bugs that need fixing
- `enhancement` - Feature requests
- `documentation` - Documentation improvements

### 2. Claim an Issue

Comment on the issue to let others know you're working on it:

```
I'd like to work on this issue. Can you assign it to me?
```

### 3. Create a Branch

Create a new branch for your work:

```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
```

### 4. Make Your Changes

Follow the coding standards and best practices outlined below.

### 5. Write Tests

Ensure your changes are covered by appropriate tests:

```python
# For bug fixes: Add regression tests
# For new features: Add comprehensive tests
# For refactoring: Ensure existing tests still pass
```

### 6. Commit Your Changes

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```bash
# Good commit messages
git commit -m "feat: add support for new agent adapter"
git commit -m "fix: resolve database connection timeout issue"
git commit -m "docs: update API documentation for benchmark endpoints"
git commit -m "test: add unit tests for analytics engine"
git commit -m "perf: optimize benchmark result processing"
```

### 7. Run Tests

Ensure all tests pass:

```bash
# Run all tests
make test

# Run specific test types
make test-unit
make test-integration
make test-e2e

# Check code quality
make quality
```

### 8. Push and Create Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

## 📋 Pull Request Guidelines

### PR Checklist

Before submitting your pull request, ensure you've completed:

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code follows project style guidelines
- [ ] No breaking changes (unless intentional)
- [ ] Commit messages are clear and descriptive
- [ ] PR description explains the changes

### PR Description Template

```markdown
## What does this PR do?

Brief description of the changes.

## Why is this important?

Explanation of why these changes matter.

## How to test?

Instructions for testing the changes.

## Screenshots (if applicable)

Visual evidence of changes.

## Related Issues

Fixes #123
Closes #456
```

### Code Review Process

1. **Automated Checks**
   - CI/CD pipeline runs all tests
   - Code quality checks (linting, formatting)
   - Security scans
   - Dependency checks

2. **Manual Review**
   - At least 2 reviewers required
   - Technical review by maintainers
   - Documentation review
   - Security review (for sensitive changes)

3. **Merge Criteria**
   - All tests passing
   - Code review approvals
   - No unresolved comments
   - CI/CD pipeline success

## 🎨 Coding Standards

### Python Style Guide

Follow [PEP 8](https://peps.python.org/pep-0008/) with these additional guidelines:

#### Imports
```python
# Standard library imports
import os
import sys
from typing import Dict, List, Optional

# Third-party imports
import httpx
import pytest
from fastapi import APIRouter, Depends

# Local application imports
from .models import BenchmarkRun
from .services import BenchmarkService
from ..utils import get_logger
```

#### Function Definitions
```python
def calculate_accuracy(
    correct_answers: int, 
    total_questions: int
) -> float:
    """
    Calculate accuracy percentage.
    
    Args:
        correct_answers: Number of correct answers
        total_questions: Total number of questions
        
    Returns:
        Accuracy percentage (0-100)
        
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

#### Class Definitions
```python
class BenchmarkService:
    """Service for managing benchmark operations."""
    
    def __init__(self, database_url: str):
        """
        Initialize benchmark service.
        
        Args:
            database_url: Database connection URL
        """
        self.database_url = database_url
        self.logger = get_logger(__name__)
    
    async def start_benchmark(
        self, 
        agents: List[str], 
        benchmark_type: str
    ) -> str:
        """
        Start a new benchmark run.
        
        Args:
            agents: List of agent identifiers
            benchmark_type: Type of benchmark to run
            
        Returns:
            Unique run identifier
            
        Raises:
            DatabaseError: If database operation fails
        """
        # Implementation
        pass
```

### Type Hints

Always use type hints for function parameters and return values:

```python
# Good
def process_benchmark(
    agents: List[str], 
    config: Dict[str, Any]
) -> Dict[str, Any]:
    pass

# Bad
def process_benchmark(agents, config):
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int = 42) -> bool:
    """Example function with types documented in the docstring.

    Args:
        param1: The first parameter.
        param2: The second parameter. Defaults to 42.

    Returns:
        True if successful, False otherwise.

    Raises:
        ValueError: If param1 is invalid.
    """
    pass
```

## 🧪 Testing Guidelines

### Test Structure

Follow the AAA pattern (Arrange, Act, Assert):

```python
def test_example():
    """Test example function behavior."""
    # Arrange: Set up test data and mocks
    test_input = "hello world"
    expected_output = "HELLO WORLD"
    
    # Act: Execute the function being tested
    result = example_function(test_input)
    
    # Assert: Verify the results
    assert result == expected_output
```

### Mocking Best Practices

```python
# Use pytest-mock for cleaner mocking
def test_with_mock(mocker):
    """Test with mocked external dependency."""
    # Arrange
    mock_service = mocker.Mock()
    mock_service.process.return_value = {"status": "success"}
    
    # Act
    result = function_under_test(mock_service)
    
    # Assert
    assert result["status"] == "success"
    mock_service.process.assert_called_once_with(expected_args)
```

### Test Data Management

```python
# Use fixtures for reusable test data
@pytest.fixture
def sample_benchmark_config():
    """Sample benchmark configuration for testing."""
    return {
        "agents": ["gpt-4-turbo", "claude-3-opus"],
        "benchmark": "mmlu-reasoning-v1",
        "config": {
            "temperature": 0.7,
            "max_tokens": 1024
        }
    }

def test_benchmark_creation(sample_benchmark_config):
    """Test benchmark creation with sample config."""
    # Use fixture data
    result = create_benchmark(sample_benchmark_config)
    assert result is not None
```

## 📚 Documentation Guidelines

### API Documentation

Use FastAPI's automatic documentation:

```python
@app.post("/benchmark/run")
async def run_benchmark(request: BenchmarkRequest):
    """
    Submit a new benchmark for processing.
    
    This endpoint queues a benchmark for asynchronous processing.
    The benchmark will be executed against the specified agents.
    
    Args:
        request: Benchmark configuration including agents and parameters
        
    Returns:
        Benchmark run information including run ID and status
        
    Example:
        >>> import requests
        >>> response = requests.post(
        ...     "http://localhost:8000/api/benchmark/run",
        ...     json={
        ...         "agents": ["gpt-4-turbo"],
        ...         "benchmark": "mmlu-reasoning-v1"
        ...     }
        ... )
        >>> response.json()
        {
            "run_id": "abc123-def456",
            "status": "queued"
        }
    """
    # Implementation
    pass
```

### Code Comments

Add comments for complex logic:

```python
def complex_algorithm(data: List[Dict]) -> Dict:
    """Process complex data using specialized algorithm."""
    
    # Normalize input data to ensure consistent format
    normalized_data = normalize_input(data)
    
    # Apply weighting based on data importance
    # Higher weights for more recent data points
    weighted_data = apply_weighting(normalized_data)
    
    # Calculate final result using iterative approach
    # This ensures convergence within acceptable tolerance
    result = iterative_calculation(weighted_data, tolerance=0.001)
    
    return result
```

## 🚀 Performance Considerations

### Asynchronous Programming

Use async/await for I/O-bound operations:

```python
# Good: Async for I/O operations
async def fetch_agent_response(agent, prompt):
    """Fetch response from agent asynchronously."""
    async with httpx.AsyncClient() as client:
        response = await client.post(agent.url, json={"prompt": prompt})
        return response.json()

# Bad: Blocking operations in async functions
async def bad_fetch_agent_response(agent, prompt):
    """Avoid blocking operations in async functions."""
    time.sleep(1)  # This blocks the event loop!
    # Implementation
```

### Memory Management

```python
# Use generators for large datasets
def process_large_dataset(data_source):
    """Process large dataset efficiently."""
    for batch in data_source.iter_batches(batch_size=1000):
        yield process_batch(batch)

# Close resources properly
async def database_operation():
    """Perform database operation with proper cleanup."""
    conn = await database.connect()
    try:
        result = await conn.execute(query)
        return result
    finally:
        await conn.close()
```

## 🔒 Security Best Practices

### Input Validation

```python
from pydantic import BaseModel, validator

class BenchmarkRequest(BaseModel):
    """Request model for benchmark submission."""
    agents: List[str]
    benchmark: str
    config: Optional[Dict[str, Any]] = None
    
    @validator('agents')
    def validate_agents(cls, v):
        """Validate agent list."""
        if not v:
            raise ValueError('At least one agent is required')
        if len(v) > 10:
            raise ValueError('Maximum 10 agents allowed')
        return v
    
    @validator('benchmark')
    def validate_benchmark(cls, v):
        """Validate benchmark ID."""
        if not re.match(r'^[a-zA-Z0-9-]+$', v):
            raise ValueError('Invalid benchmark ID format')
        return v
```

### SQL Injection Prevention

```python
# Good: Parameterized queries
async def get_benchmark_status(run_id: str):
    """Get benchmark status safely."""
    query = "SELECT * FROM benchmarks WHERE run_id = $1"
    result = await database.fetch_one(query, run_id)
    return result

# Bad: String concatenation (NEVER do this)
# query = f"SELECT * FROM benchmarks WHERE run_id = '{run_id}'"
```

## 📈 Performance Optimization

### Caching Strategies

```python
import redis
from functools import wraps

def cache_result(expiration=300):
    """Cache function results in Redis."""
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
    """Get list of available benchmarks."""
    # Database query
    pass
```

### Database Optimization

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

# Use bulk operations for large datasets
def insert_multiple_results(results):
    """Insert multiple results efficiently."""
    with engine.connect() as conn:
        conn.execute(benchmark_results.insert(), results)
```

## 🧰 Development Tools

### Makefile Commands

```bash
# Development setup
make setup

# Start development environment
make dev

# Run all tests
make test

# Run specific test types
make test-unit
make test-integration
make test-e2e

# Code quality checks
make quality

# Format code
make format

# Lint code
make lint

# Type checking
make type-check

# Security checks
make security-check

# Clean development environment
make clean
```

### Development Scripts

```bash
# Start development environment
./scripts/start-dev.sh

# Run tests with coverage
./scripts/run-tests.sh

# Deploy to staging
./scripts/deploy-staging.sh

# Backup database
./scripts/backup-db.sh
```

## 📞 Getting Help

### Community Support

- **GitHub Issues**: For bug reports and feature requests
- **Discussions**: For general questions and community discussion
- **Slack/Discord**: Real-time chat (link in README)

### Maintainer Contact

For urgent issues or questions about contributing:

- **Lead Maintainer**: maintainer@benchmark.example.com
- **Security Issues**: security@benchmark.example.com

## 🎉 Recognition

We appreciate all contributions, big and small! Contributors are recognized in:

1. **Release Notes**: All contributors mentioned in release notes
2. **Contributors List**: Maintained in CONTRIBUTORS.md
3. **GitHub Recognition**: Automatic recognition through GitHub
4. **Community Highlights**: Featured in community newsletters

### Contributor Swag

Active contributors receive:
- Project stickers and badges
- Early access to new features
- Invitation to contributor events
- Recognition in annual reports

## 📜 License

By contributing to the AI Benchmark Service, you agree that your contributions will be licensed under the project's MIT License.

---

Thank you for contributing to the AI Benchmark Service! Your efforts help make AI evaluation more accessible and reliable for everyone.