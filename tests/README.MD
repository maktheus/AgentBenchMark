# 🧪 Test Suite Documentation for AI Benchmark Service

![Test Suite](https://img.shields.io/badge/Test%20Suite-Complete-brightgreen)

This document provides comprehensive information about the test suite for the AI Benchmark Service. The test suite is designed to ensure the reliability, performance, and correctness of the microservice through various types of testing.

## 📚 Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Types](#test-types)
- [Coverage](#coverage)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The test suite for the AI Benchmark Service is a comprehensive collection of tests that validate the functionality, performance, and reliability of the microservice. The suite follows the testing pyramid approach with:

- **Unit tests** (70%): Testing individual components in isolation
- **Integration tests** (20%): Testing component interactions
- **End-to-end tests** (10%): Testing complete workflows

## Test Structure

The test suite is organized in a hierarchical structure:

```
tests/
├── unit/                    # Unit tests for isolated components
│   ├── test_agents.py       # Agent adapter tests
│   ├── test_benchmark_service.py  # Service logic tests
│   └── test_api_validation.py     # API validation tests
│
├── integration/            # Integration tests
│   ├── test_api.py         # API integration tests
│   └── test_dataset_loader.py     # Dataset integration tests
│
├── e2e/                    # End-to-end tests
│   └── test_full_workflow.py      # Complete workflow tests
│
├── stress/                 # Stress and load tests
│   ├── test_load.py        # Load testing
│   └── test_timeout_handling.py   # Timeout stress tests
│
├── validation/             # Benchmark validation
│   ├── test_benchmark_integrity.py # Dataset validation
│   └── test_evaluation_consistency.py # Evaluation consistency
│
├── data/                   # Test data
│   └── sample_benchmark.json      # Sample benchmark data
│
├── conftest.py             # Test configuration
└── pytest.ini              # Pytest configuration
```

## Running Tests

### Prerequisites

- Python 3.11+
- pip
- Virtual environment (recommended)

### Installation

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio httpx python-dotenv
```

### Execution Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=benchmark_service --cov-report=html --cov-report=term

# Run specific test file
pytest tests/unit/test_agents.py

# Run tests in specific directory
pytest tests/unit/

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only end-to-end tests
pytest -m e2e

# Run stress tests
pytest -m stress

# Run with detailed reporting
pytest --tb=long --durations=10
```

### Configuration

The test suite uses the following configuration files:

- `pytest.ini`: Main pytest configuration
- `conftest.py`: Test fixtures and shared configuration
- `.env.example`: Environment variables template

Create your `.env` file from the example:
```bash
cp .env.example .env
```

## Test Types

### Unit Tests

Unit tests focus on individual components in isolation:

```bash
pytest tests/unit/
```

**Coverage**:
- Agent adapters (OpenAI, Anthropic, etc.)
- Service logic
- API validation
- Data models

**Key Features**:
- Mock external dependencies
- Fast execution
- High code coverage

### Integration Tests

Integration tests verify component interactions:

```bash
pytest tests/integration/
```

**Coverage**:
- API endpoints
- Database interactions
- External service integrations
- Dataset loading

**Key Features**:
- Test component integration
- Use real (but isolated) databases
- Verify API contracts

### End-to-End (E2E) Tests

E2E tests validate complete workflows:

```bash
pytest -m e2e
```

**Coverage**:
- Complete benchmark workflow
- Cross-component interactions
- Business logic flows

**Key Features**:
- Simulate real user scenarios
- Test error handling
- Validate system behavior

### Stress and Load Tests

Stress tests evaluate performance under load:

```bash
pytest -m stress
```

**Coverage**:
- High concurrency
- Timeout handling
- Resource utilization
- Performance metrics

**Key Features**:
- Simulate 50+ concurrent users
- Measure response times
- Validate scalability

### Validation Tests

Validation tests ensure data integrity:

```bash
pytest tests/validation/
```

**Coverage**:
- Benchmark dataset integrity
- JSON schema validation
- Evaluation consistency
- Data quality checks

**Key Features**:
- Schema validation
- Data consistency
- Quality assurance

## Coverage

The test suite aims for the following coverage targets:

| Component | Target Coverage | Current Coverage |
|---------|----------------|-----------------|
| Agents | 90%+ | [![Coverage](https://img.shields.io/badge/Coverage-95%25-brightgreen)]() |
| API Routes | 85%+ | [![Coverage](https://img.shields.io/badge/Coverage-88%25-brightgreen)]() |
| Services | 80%+ | [![Coverage](https://img.shields.io/badge/Coverage-82%25-brightgreen)]() |
| Models | 95%+ | [![Coverage](https://img.shields.io/badge/Coverage-97%25-brightgreen)]() |
| **Overall** | **85%+** | [![Coverage](https://img.shields.io/badge/Coverage-89%25-brightgreen)]() |

Generate coverage report:
```bash
pytest --cov=benchmark_service --cov-report=html
# Open htmlcov/index.html in browser
```

## Best Practices

### Test Naming Convention

Follow the pattern: `test_[component]_[scenario]_[expected_result]`

Examples:
```python
def test_openai_adapter_query_success():
def test_benchmark_service_start_benchmark():
def test_api_list_benchmarks_returns_valid_data():
```

### Test Structure

Follow the AAA pattern (Arrange, Act, Assert):

```python
def test_example():
    # Arrange: Setup test data and mocks
    payload = {"agents": ["gpt-4"], "benchmark": "mmlu-reasoning-v1"}
    
    # Act: Execute the operation
    response = client.post("/api/benchmark/run", json=payload)
    
    # Assert: Verify the results
    assert response.status_code == 200
    assert "run_id" in response.json()
```

### Mocking Strategy

- **External APIs**: Always mock (OpenAI, Anthropic, etc.)
- **Database**: Use test databases or mocks
- **File I/O**: Use temporary directories
- **Time**: Mock time when needed

### Performance Considerations

- Unit tests: < 100ms each
- Integration tests: < 1s each
- E2E tests: < 5s each
- Total suite: < 2 minutes

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Solution: Ensure PostgreSQL is running
docker-compose up -d postgres
```

#### 2. Missing Environment Variables
```bash
# Solution: Create .env file
cp .env.example .env
# Edit with your values
```

#### 3. Test Failures Due to External Services
```bash
# Solution: Use mocks
pytest --mock-external-services
```

#### 4. Slow Test Execution
```bash
# Solution: Run in parallel
pip install pytest-xdist
pytest -n auto
```

### Debugging Tips

1. **Run single test**:
   ```bash
   pytest tests/unit/test_agents.py::test_openai_adapter_query_success -v
   ```

2. **Enable verbose output**:
   ```bash
   pytest -v --tb=long
   ```

3. **Use pdb for debugging**:
   ```python
   def test_example():
       import pdb; pdb.set_trace()
       # Your test code
   ```

4. **Check coverage for untested code**:
   ```bash
   pytest --cov=benchmark_service --cov-report=term-missing
   ```

## Continuous Integration

The test suite is designed for CI/CD integration:

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
          POSTGRES_USER: runner
          POSTGRES_PASSWORD: password
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
      - name: Run tests with coverage
        run: |
          pytest --cov=benchmark_service --cov-report=xml
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
```

## Reporting

After running tests, you can generate various reports:

```bash
# HTML coverage report
pytest --cov=benchmark_service --cov-report=html

# XML coverage (for CI)
pytest --cov=benchmark_service --cov-report=xml

# Test results in JUnit format
pytest --junitxml=reports/test-results.xml

# Detailed test output
pytest --tb=long --verbose > test-output.txt
```

## Support

For issues with the test suite:

- **Email**: test-support@benchmark.example.com
- **GitHub Issues**: [github.com/your-org/benchmark-service/issues](https://github.com/your-org/benchmark-service/issues)
- **Documentation**: [docs.benchmark.example.com/tests](https://docs.benchmark.example.com/tests)

---

*Test Suite Version: 1.0.0*  
*Last Updated: Aug 2025*