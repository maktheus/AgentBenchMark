# 📡 API Documentation

This document provides comprehensive documentation for the AI Benchmark Service REST API.

## 📋 API Overview

The AI Benchmark Service API provides programmatic access to benchmark management, execution, and result analysis for AI agents.

### Base URL

```
https://api.benchmark.example.com/v1
```

For local development:
```
http://localhost:8000/api
```

### Authentication

All API requests require authentication via Bearer token:

```http
Authorization: Bearer YOUR_API_KEY
```

### Rate Limiting

- **Free Tier**: 100 requests per hour
- **Pro Tier**: 1,000 requests per hour
- **Enterprise Tier**: 10,000 requests per hour

### Response Format

All API responses are in JSON format:

```json
{
  "data": {...},
  "meta": {...},
  "links": {...}
}
```

## 🔐 Authentication Endpoints

### POST /auth/token

Generate an API token for authentication.

**Request:**
```bash
curl -X POST https://api.benchmark.example.com/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your-password"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### POST /auth/register

Register a new user account.

**Request:**
```bash
curl -X POST https://api.benchmark.example.com/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "secure-password",
    "name": "John Doe"
  }'
```

**Response:**
```json
{
  "id": "user-123",
  "email": "newuser@example.com",
  "name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z"
}
```

## 🏃 Benchmark Management Endpoints

### POST /benchmark/run

Submit a new benchmark for processing.

**Permissions Required:** `benchmark:write`

**Request:**
```bash
curl -X POST https://api.benchmark.example.com/v1/benchmark/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agents": ["gpt-4-turbo", "claude-3-opus"],
    "benchmark": "mmlu-reasoning-v1",
    "config": {
      "temperature": 0.7,
      "max_tokens": 1024
    }
  }'
```

**Response:**
```json
{
  "run_id": "bf9d8e7a-1b2c-4d3e-8f7a-6b5c4d3e2f1a",
  "status": "queued",
  "created_at": "2024-01-01T10:30:00Z",
  "agents": ["gpt-4-turbo", "claude-3-opus"],
  "benchmark": "mmlu-reasoning-v1"
}
```

### GET /benchmark/{run_id}

Get the status of a specific benchmark run.

**Permissions Required:** `benchmark:read`

**Request:**
```bash
curl -X GET https://api.benchmark.example.com/v1/benchmark/bf9d8e7a-1b2c-4d3e-8f7a-6b5c4d3e2f1a \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
  "run_id": "bf9d8e7a-1b2c-4d3e-8f7a-6b5c4d3e2f1a",
  "status": "completed",
  "progress": 1.0,
  "started_at": "2024-01-01T10:30:00Z",
  "completed_at": "2024-01-01T10:32:27Z",
  "results_url": "/v1/results/bf9d8e7a-1b2c-4d3e-8f7a-6b5c4d3e2f1a"
}
```

### GET /benchmark/list

List all available benchmarks.

**Permissions Required:** `benchmark:read`

**Request:**
```bash
curl -X GET https://api.benchmark.example.com/v1/benchmark/list \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
[
  {
    "id": "mmlu-reasoning-v1",
    "name": "MMLU Reasoning Benchmark v1",
    "description": "Avaliação de raciocínio lógico baseada no MMLU",
    "categories": ["mathematics", "formal_logic"],
    "question_count": 150
  },
  {
    "id": "gsm8k-math-v2",
    "name": "GSM8K Math Benchmark v2",
    "description": "Problemas matemáticos de escola primária",
    "categories": ["arithmetic", "algebra"],
    "question_count": 850
  }
]
```

## 📊 Results Endpoints

### GET /results/{run_id}

Get detailed results for a completed benchmark.

**Permissions Required:** `results:read`

**Request:**
```bash
curl -X GET https://api.benchmark.example.com/v1/results/bf9d8e7a-1b2c-4d3e-8f7a-6b5c4d3e2f1a \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
  "run_id": "bf9d8e7a-1b2c-4d3e-8f7a-6b5c4d3e2f1a",
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
```

### GET /results/{run_id}/analysis

Get detailed analysis of benchmark results.

**Permissions Required:** `results:read`

**Request:**
```bash
curl -X GET https://api.benchmark.example.com/v1/results/bf9d8e7a-1b2c-4d3e-8f7a-6b5c4d3e2f1a/analysis \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
  "timestamp": "2024-01-01T10:32:27Z",
  "benchmark_id": "mmlu-reasoning-v1",
  "total_agents": 2,
  "performance_metrics": {
    "gpt-4-turbo": {
      "accuracy_analysis": {
        "value": 87.3,
        "rating": "Excellent"
      },
      "latency_analysis": {
        "value": 4.2,
        "rating": "Good"
      }
    }
  },
  "comparative_analysis": {
    "best_accuracy": "gpt-4-turbo",
    "best_latency": "claude-3-opus"
  },
  "statistical_summary": {
    "accuracy": {
      "mean": 84.7,
      "median": 84.7,
      "std_dev": 2.6
    }
  },
  "insights": [
    "gpt-4-turbo demonstra excelente precisão (≥90%)",
    "claude-3-opus tem excelente tempo de resposta (≤2s)"
  ]
}
```

### GET /results/{run_id}/deductions

Get advanced deductions from benchmark results.

**Permissions Required:** `results:read`

**Request:**
```bash
curl -X GET https://api.benchmark.example.com/v1/results/bf9d8e7a-1b2c-4d3e-8f7a-6b5c4d3e2f1a/deductions \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
  "performance_patterns": {
    "performance_clusters": {
      "0": ["gpt-4-turbo"],
      "1": ["claude-3-opus"]
    }
  },
  "behavioral_insights": {
    "gpt-4-turbo": {
      "score_consistency": "High",
      "category_strengths": ["mathematics"],
      "overall_performance_profile": "High Performance"
    }
  },
  "correlation_analysis": {
    "accuracy_vs_latency_correlation": -0.45,
    "correlation_interpretation": {
      "acc_lat": "Moderate correlation"
    }
  },
  "anomaly_detection": {
    "detected_anomalies": []
  },
  "recommendations": [
    "Considerar fine-tuning para claude-3-opus para melhorar precisão",
    "Otimizar tempo de resposta para gpt-4-turbo"
  ]
}
```

### GET /results/{run_id}/report

Download benchmark results as a PDF report.

**Permissions Required:** `results:read`

**Request:**
```bash
curl -X GET https://api.benchmark.example.com/v1/results/bf9d8e7a-1b2c-4d3e-8f7a-6b5c4d3e2f1a/report \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -o benchmark_report.pdf
```

**Response:**
```
Binary PDF content
Content-Type: application/pdf
Content-Disposition: attachment; filename=benchmark_report_bf9d8e7a-1b2c-4d3e-8f7a-6b5c4d3e2f1a.pdf
```

## 📈 Analytics Endpoints

### GET /analytics/history

Get history of benchmark analyses.

**Permissions Required:** `results:read`

**Request:**
```bash
curl -X GET https://api.benchmark.example.com/v1/analytics/history \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
[
  {
    "timestamp": "2024-01-01T10:32:27Z",
    "benchmark_id": "mmlu-reasoning-v1",
    "total_agents": 2,
    "performance_metrics": {...},
    "comparative_analysis": {...}
  }
]
```

## 🏥 Health Check Endpoints

### GET /health

Check if the service is running.

**Request:**
```bash
curl -X GET https://api.benchmark.example.com/v1/health
```

**Response:**
```json
{
  "status": "healthy"
}
```

### GET /ready

Check if the service is ready to accept requests.

**Request:**
```bash
curl -X GET https://api.benchmark.example.com/v1/ready
```

**Response:**
```json
{
  "status": "ready"
}
```

## 📊 Data Models

### Benchmark Request

```json
{
  "agents": ["string"],
  "benchmark": "string",
  "config": {
    "temperature": 0.7,
    "max_tokens": 1024
  }
}
```

### Benchmark Status

```json
{
  "run_id": "uuid",
  "status": "queued|processing|completed|failed",
  "created_at": "ISO8601 timestamp",
  "started_at": "ISO8601 timestamp",
  "completed_at": "ISO8601 timestamp",
  "progress": 0.0,
  "agents": ["string"],
  "benchmark": "string",
  "config": {}
}
```

### Benchmark Result

```json
{
  "run_id": "uuid",
  "benchmark": "string",
  "agents": [
    {
      "id": "string",
      "metrics": {
        "accuracy": 0.0,
        "latency_avg": 0.0,
        "tokens_avg": 0,
        "consistency": 0.0
      },
      "category_scores": {
        "category_name": 0.0
      }
    }
  ],
  "summary": {
    "top_performer": "string",
    "critical_observations": ["string"]
  }
}
```

## 🚨 Error Responses

### 400 Bad Request

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "agents",
      "reason": "At least one agent is required"
    }
  }
}
```

### 401 Unauthorized

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or missing authentication token"
  }
}
```

### 403 Forbidden

```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "Insufficient permissions to access this resource"
  }
}
```

### 404 Not Found

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found"
  }
}
```

### 429 Too Many Requests

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again later."
  }
}
```

### 500 Internal Server Error

```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred"
  }
}
```

## 📈 Rate Limits

### Free Tier
- **Requests**: 100 per hour
- **Concurrent Benchmarks**: 1
- **Storage**: 100MB
- **Support**: Community forums

### Pro Tier
- **Requests**: 1,000 per hour
- **Concurrent Benchmarks**: 5
- **Storage**: 1GB
- **Support**: Email support (24h response)

### Enterprise Tier
- **Requests**: 10,000 per hour
- **Concurrent Benchmarks**: Unlimited
- **Storage**: 10GB
- **Support**: 24/7 phone support

## 🛠️ SDKs and Libraries

### Python SDK

```python
from ai_benchmark import BenchmarkClient

client = BenchmarkClient(api_key="YOUR_API_KEY")

# Run a benchmark
result = client.run_benchmark(
    agents=["gpt-4-turbo", "claude-3-opus"],
    benchmark="mmlu-reasoning-v1"
)

# Get results
results = client.get_results(result.run_id)
```

### JavaScript SDK

```javascript
import { BenchmarkClient } from '@ai-benchmark/sdk';

const client = new BenchmarkClient({ apiKey: 'YOUR_API_KEY' });

// Run a benchmark
const result = await client.runBenchmark({
    agents: ['gpt-4-turbo', 'claude-3-opus'],
    benchmark: 'mmlu-reasoning-v1'
});

// Get results
const results = await client.getResults(result.runId);
```

## 📞 Support

For API support and questions:

- **Email**: api-support@benchmark.example.com
- **Documentation**: https://docs.benchmark.example.com
- **Status Page**: https://status.benchmark.example.com
- **Community**: https://community.benchmark.example.com

## 📜 Changelog

### v1.0.0 (2024-01-01)
- Initial API release
- Benchmark execution endpoints
- Results retrieval
- Basic analytics

### v1.1.0 (2024-02-01)
- Advanced analytics endpoints
- Performance pattern detection
- Correlation analysis
- Anomaly detection

### v1.2.0 (2024-03-01)
- Machine learning-based deductions
- Enhanced recommendations
- Historical analytics
- Improved error handling

This API documentation provides comprehensive information for integrating with the AI Benchmark Service. For the most up-to-date documentation, please visit our developer portal.