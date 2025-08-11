# 📚 Documentação Completa: Microserviço de Benchmark de Agents

![AI Benchmark Service Architecture](https://i.imgur.com/8ZkRj7l.png)

## 📌 Tabela de Conteúdos

- [1. Visão Geral](#1-visão-geral)
- [2. Arquitetura do Sistema](#2-arquitetura-do-sistema)
  - [2.1 Componentes Principais](#21-componentes-principais)
  - [2.2 Fluxo de Dados](#22-fluxo-de-dados)
  - [2.3 Diagrama de Componentes](#23-diagrama-de-componentes)
- [3. Documentação da API](#3-documentação-da-api)
  - [3.1 Autenticação](#31-autenticação)
  - [3.2 Endpoints](#32-endpoints)
  - [3.3 Exemplos de Uso](#33-exemplos-de-uso)
- [4. Configuração e Implantação](#4-configuração-e-implantação)
  - [4.1 Requisitos](#41-requisitos)
  - [4.2 Configuração Local](#42-configuração-local)
  - [4.3 Implantação em Produção](#43-implantação-em-produção)
- [5. Monitoramento e Observabilidade](#5-monitoramento-e-observabilidade)
  - [5.1 Métricas-Chave](#51-métricas-chave)
  - [5.2 Dashboard do Grafana](#52-dashboard-do-grafana)
  - [5.3 Alertas](#53-alertas)
- [6. Testes e Validação](#6-testes-e-validação)
  - [6.1 Testes de Unidade](#61-testes-de-unidade)
  - [6.2 Testes de Carga](#62-testes-de-carga)
  - [6.3 Benchmark de Referência](#63-benchmark-de-referência)
- [7. Operações e Manutenção](#7-operações-e-manutenção)
  - [7.1 Troubleshooting](#71-troubleshooting)
  - [7.2 Atualizações](#72-atualizações)
  - [7.3 Backup e Recuperação](#73-backup-e-recuperação)
- [8. Extensibilidade e Contribuição](#8-extensibilidade-e-contribuição)
  - [8.1 Adicionando Novos Agents](#81-adicionando-novos-agents)
  - [8.2 Criando Novos Benchmarks](#82-criando-novos-benchmarks)
  - [8.3 Contribuição para o Projeto](#83-contribuição-para-o-projeto)
- [9. Apêndices](#9-apêndices)
  - [9.1 Glossário](#91-glossário)
  - [9.2 Referências](#92-referências)

---

## 1. Visão Geral

O **Microserviço de Benchmark de Agents** é uma solução completa para avaliação padronizada de agentes de inteligência artificial, incluindo modelos de linguagem grandes (LLMs), agentes autônomos e sistemas baseados em IA. O sistema permite comparar agentes em múltiplas dimensões de desempenho com métricas objetivas e reprodutíveis.

### 🎯 Objetivos Principais

- **Padronização**: Executar benchmarks consistentes com metodologia clara
- **Comparabilidade**: Permitir comparação justa entre diferentes agentes
- **Transparência**: Tornar métricas e metodologia acessíveis
- **Escalabilidade**: Suportar avaliação de múltiplos agentes simultaneamente
- **Extensibilidade**: Facilitar a adição de novos agents e benchmarks

### 📊 Métricas Avaliadas

| Categoria | Métricas |
|-----------|----------|
| **Precisão** | Exatidão, Taxa de Acerto, Consistência |
| **Desempenho** | Latência, Throughput, P95/P99 |
| **Capacidades** | Raciocínio, Matemática, Ética, Segurança |
| **Custo** | Uso de Tokens, Custo Estimado |
| **Qualidade** | Coerência, Hallucinação, Alinhamento |

### 🌐 Casos de Uso

- **Desenvolvedores de IA**: Comparar modelos durante desenvolvimento
- **Equipes de Produto**: Selecionar agentes para integração em produtos
- **Pesquisadores**: Validar hipóteses sobre capacidades de agentes
- **Organizações Regulatórias**: Avaliar conformidade com padrões

---

## 2. Arquitetura do Sistema

### 2.1 Componentes Principais

#### **API Gateway**
- **Função**: Ponto único de entrada para todas as requisições
- **Tecnologia**: NGINX
- **Recursos**:
  - Roteamento inteligente
  - Autenticação JWT e API Keys
  - Rate limiting configurável
  - Logging detalhado

#### **Serviço de Benchmark (Core)**
- **Tecnologia**: Python 3.11 + FastAPI
- **Principais Responsabilidades**:
  - Receber e validar requisições de benchmark
  - Orquestrar execução de tarefas
  - Coletar e processar resultados
  - Gerar relatórios

#### **Sistema de Agents (Adapters)**
- **Padrão**: Adapter Pattern
- **Estrutura**:
  ```mermaid
  classDiagram
      class AgentInterface {
          <<interface>>
          + query(prompt: str, context: dict) dict
          + get_info() dict
      }
      
      class OpenAIAgentAdapter {
          - client: httpx.AsyncClient
          - config: OpenAIConfig
          + query(prompt: str, context: dict) dict
          + get_info() dict
      }
      
      class AnthropicAgentAdapter {
          - client: httpx.AsyncClient
          - config: AnthropicConfig
          + query(prompt: str, context: dict) dict
          + get_info() dict
      }
      
      AgentInterface <|.. OpenAIAgentAdapter
      AgentInterface <|.. AnthropicAgentAdapter
  ```

#### **Orquestrador de Tarefas**
- **Tecnologia**: Celery + Redis
- **Fluxo**:
  1. Recebe configuração do benchmark
  2. Carrega dataset apropriado
  3. Distribui tarefas para agents
  4. Coleta respostas
  5. Dispara avaliação

#### **Sistema de Avaliação**
- **Avaliação Automática**:
  - Comparação com gabarito
  - Métricas tradicionais (BLEU, ROUGE)
  - Análise de tokens
- **LLM-as-a-Judge**:
  - Uso de modelo confiável para avaliação subjetiva
  - Prompting estruturado para consistência
  - Sistema de ponderação de votos

#### **Armazenamento**
- **Resultados**: PostgreSQL (relacional)
- **Datasets**: MinIO/S3 (objeto)
- **Cache/Fila**: Redis

### 2.2 Fluxo de Dados

```mermaid
sequenceDiagram
    participant User as Usuário
    participant API as API Gateway
    participant Service as Benchmark Service
    participant Orchestrator as Orchestrator
    participant Agents as Agents
    participant Evaluator as Evaluator
    participant DB as PostgreSQL
    
    User->>API: POST /benchmark/run
    API->>Service: Encaminha requisição
    Service->>Orchestrator: Cria run_id e enfileira
    Orchestrator->>Orchestrator: Carrega dataset
    loop Para cada tarefa
        Orchestrator->>Agents: Envia para todos agents
        par Respostas dos agents
            Agents->>Orchestrator: Respostas
            Orchestrator->>Evaluator: Envia para avaliação
            Evaluator->>Evaluator: Processa métricas
            Evaluator->>DB: Salva resultados
        end
    end
    Orchestrator->>Service: Atualiza status
    Service->>API: Retorna status
    API->>User: Resposta HTTP
```

### 2.3 Diagrama de Componentes

```mermaid
C4Context
  title Arquitetura do Microserviço de Benchmark

  Person(usuario, "Usuário", "Inicia e consulta benchmarks")
  System_Ext(openai, "OpenAI API", "Agentes GPT")
  System_Ext(anthropic, "Anthropic API", "Agentes Claude")
  System_Ext(custom_agents, "Agentes Personalizados", "HTTP/GRPC")

  System(benchmark_service, "Microserviço de Benchmark", "Core do sistema")
  SystemDb(postgres, "PostgreSQL", "Resultados e configurações")
  SystemCache(redis, "Redis", "Cache e fila de tarefas")
  SystemDb(minio, "MinIO/S3", "Datasets e relatórios")

  Rel(usuario, benchmark_service, "HTTP (API REST)")
  Rel(benchmark_service, openai, "API Key (HTTPS)")
  Rel(benchmark_service, anthropic, "API Key (HTTPS)")
  Rel(benchmark_service, custom_agents, "HTTP/GRPC")
  Rel(benchmark_service, postgres, "SQL (JDBC)")
  Rel(benchmark_service, redis, "Celery Tasks")
  Rel(benchmark_service, minio, "S3 API")

  Boundary(infra, "Infraestrutura") {
    System_Ext(grafana, "Grafana", "Monitoramento")
    System_Ext(prometheus, "Prometheus", "Métricas")
    System_Ext(jaeger, "Jaeger", "Tracing Distribuído")
  }

  Rel(benchmark_service, grafana, "Metrics (Prometheus)")
  Rel(benchmark_service, jaeger, "Traces (OpenTelemetry)")
```

---

## 3. Documentação da API

### 3.1 Autenticação

Todas as requisições requerem autenticação via token Bearer:

```http
GET /benchmark/list HTTP/1.1
Host: api.benchmark.example.com
Authorization: Bearer <SEU_API_KEY>
```

- **Obtenção de API Key**: Via painel administrativo ou processo de onboarding
- **Escopo de Permissões**:
  - `benchmark:read`: Consultar benchmarks
  - `benchmark:write`: Criar novos benchmarks
  - `results:read`: Acessar resultados detalhados

### 3.2 Endpoints

#### `POST /benchmark/run` - Iniciar Novo Benchmark

**Descrição**: Submete uma nova execução de benchmark para processamento assíncrono

**Parâmetros**:

| Campo | Tipo | Obrigatório | Descrição | Exemplo |
|-------|------|-------------|-----------|---------|
| agents | array | Sim | Lista de agents a serem avaliados | `["gpt-4", "claude-3"]` |
| benchmark | string | Sim | ID do benchmark a ser executado | `"mmlu-reasoning-v1"` |
| config | object | Não | Configurações específicas do benchmark | `{"temperature": 0.7}` |

**Exemplo de Requisição**:
```json
{
  "agents": ["gpt-4-turbo", "claude-3-opus"],
  "benchmark": "mmlu-reasoning-v1",
  "config": {
    "temperature": 0.7,
    "max_tokens": 1024
  }
}
```

**Resposta de Sucesso (202 Accepted)**:
```json
{
  "run_id": "bf9d8e7a-1b2c-4d3e-8f7a-6b5c4d3e2f1a",
  "status": "queued",
  "created_at": "2024-05-15T14:30:00Z"
}
```

#### `GET /benchmark/{id}` - Consultar Status

**Descrição**: Obtém o status atual de uma execução de benchmark

**Parâmetros**:
- `id` (path): ID da execução (UUID)

**Resposta**:
```json
{
  "run_id": "bf9d8e7a-1b2c-4d3e-8f7a-6b5c4d3e2f1a",
  "status": "completed",
  "progress": 1.0,
  "started_at": "2024-05-15T14:30:00Z",
  "completed_at": "2024-05-15T14:32:27Z",
  "results_url": "/results/bf9d8e7a-1b2c-4d3e-8f7a-6b5c4d3e2f1a"
}
```

#### `GET /results/{id}` - Obter Resultados

**Descrição**: Retorna resultados detalhados de um benchmark concluído

**Parâmetros**:
- `id` (path): ID da execução (UUID)

**Resposta**:
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

#### `GET /benchmark/list` - Listar Benchmarks Disponíveis

**Descrição**: Retorna lista de benchmarks disponíveis para execução

**Resposta**:
```json
[
  {
    "id": "mmlu-reasoning-v1",
    "name": "MMLU Reasoning Benchmark v1",
    "description": "Avaliação de raciocínio lógico baseada no MMLU",
    "categories": ["mathematics", "formal_logic", "symbolic_reasoning"],
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

### 3.3 Exemplos de Uso

#### Executando um Benchmark Básico

```bash
curl -X POST https://api.benchmark.example.com/benchmark/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agents": ["gpt-4-turbo", "claude-3-opus"],
    "benchmark": "mmlu-reasoning-v1"
  }'
```

#### Monitorando o Progresso

```bash
curl -X GET https://api.benchmark.example.com/benchmark/bf9d8e7a-1b2c-4d3e-8f7a-6b5c4d3e2f1a \
  -H "Authorization: Bearer YOUR_API_KEY"
```

#### Obtendo Resultados Formatados

```bash
# Resultado JSON
curl -X GET https://api.benchmark.example.com/results/bf9d8e7a-1b2c-4d3e-8f7a-6b5c4d3e2f1a \
  -H "Authorization: Bearer YOUR_API_KEY"

# Relatório PDF
curl -X GET https://api.benchmark.example.com/results/bf9d8e7a-1b2c-4d3e-8f7a-6b5c4d3e2f1a/report \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -o benchmark_report.pdf
```

---

## 4. Configuração e Implantação

### 4.1 Requisitos

#### Ambiente de Desenvolvimento
- Python 3.11+
- Docker 20.10+
- Docker Compose 2.10+
- PostgreSQL 15+
- Redis 7+

#### Ambiente de Produção
- Kubernetes 1.25+
- PostgreSQL RDS ou cluster gerenciado
- Redis ElastiCache ou cluster gerenciado
- S3/MinIO para armazenamento de objetos
- Prometheus/Grafana para monitoramento

### 4.2 Configuração Local

#### Passo 1: Clonar o repositório
```bash
git clone https://github.com/your-org/benchmark-service.git
cd benchmark-service
```

#### Passo 2: Configurar variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto:
```env
# Banco de Dados
POSTGRES_URL=postgresql://user:pass@postgres:5432/benchmark
REDIS_URL=redis://redis:6379/0

# Configuração de Agents
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=xxx

# Workers
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Segurança
SECRET_KEY=your_strong_secret_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Armazenamento
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

#### Passo 3: Iniciar serviços com Docker Compose
```bash
docker-compose up --build -d
```

#### Passo 4: Executar migrações do banco
```bash
docker-compose exec web alembic upgrade head
```

#### Passo 5: Acessar a documentação da API
Abra em seu navegador:
```
http://localhost:8000/docs
```

### 4.3 Implantação em Produção

#### Arquitetura de Produção Recomendada

![Production Architecture](https://i.imgur.com/5GjKZQl.png)

#### Passo 1: Configurar Secrets no Kubernetes
```bash
kubectl create secret generic benchmark-secrets \
  --from-literal=OPENAI_API_KEY=your_key \
  --from-literal=ANTHROPIC_API_KEY=your_key \
  --from-literal=SECRET_KEY=strong_secret
```

#### Passo 2: Aplicar manifestos Kubernetes
```bash
kubectl apply -f k8s/
```

#### Passo 3: Configurar Ingress
```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: benchmark-ingress
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/rewrite-target: /$1
spec:
  rules:
  - host: api.benchmark.example.com
    http:
      paths:
      - path: /(.*)
        pathType: Prefix
        backend:
          service:
            name: benchmark-service
            port:
              number: 80
```

#### Passo 4: Configurar Horizontal Pod Autoscaler
```bash
kubectl apply -f k8s/horizontal-pod-autoscaler.yaml
```

#### Estratégia de Release
- **Canary Releases**: 5% de tráfego inicial, aumentando gradualmente
- **Health Checks**: `/health` para liveness, `/ready` para readiness
- **Rollback Automático**: Se taxa de erro > 1% ou latência P95 > 5s

---

## 5. Monitoramento e Observabilidade

### 5.1 Métricas-Chave

#### Métricas de Disponibilidade
| Métrica | Limite Aceitável | Ação |
|---------|------------------|------|
| Taxa de Sucesso | > 99.5% | Investigar erros 5xx |
| Tempo Médio de Resposta | < 1s | Otimizar agents lentos |
| Erros 5xx | < 0.5% | Verificar logs de erro |

#### Métricas de Desempenho
| Métrica | Limite Aceitável | Ação |
|---------|------------------|------|
| Latência P95 | < 2s | Ajustar timeout |
| Throughput | > 50 RPS | Escalar workers |
| Taxa de Erro | < 0.1% | Investigar causa |

#### Métricas de Agentes
| Métrica | Descrição |
|---------|-----------|
| Precisão por Categoria | % de respostas corretas por domínio |
| Latência por Agent | Tempo médio de resposta |
| Uso de Tokens | Tokens consumidos por tarefa |
| Consistência | Variação nas respostas para inputs similares |

### 5.2 Dashboard do Grafana

![Grafana Dashboard](https://i.imgur.com/6XfYz9l.png)

**Configuração Completa**:
- [Download do JSON do Dashboard](grafana/dashboards/benchmark-dashboard.json)
- [Configuração de Provisionamento](grafana/provisioning/)

**Principais Painéis**:
1. **Taxa de Solicitação por Status**: Monitora sucesso/erros
2. **Latência Percentis**: P50, P95, P99
3. **Uso de Tokens por Agent**: Comparação de custo
4. **Throughput de Tarefas**: Tarefas iniciadas vs concluídas
5. **Taxa de Sucesso**: Visão geral da saúde do serviço

### 5.3 Alertas

#### Alertas Críticos (PagerDuty/Slack)
| Alerta | Condição | Ação |
|--------|----------|------|
| **Alta Taxa de Erro** | `rate(http_request_duration_seconds_count{status_code!~"2.."}[5m]) > 0.01` | Investigar imediatamente |
| **Latência Elevada** | `histogram_quantile(0.95, rate(...)) > 5` | Escalar workers |
| **Baixo Throughput** | `rate(benchmark_task_completed_total[5m]) < 10` | Verificar agents |
| **Falha no Banco** | `up{job="postgres"} == 0` | Contato com DBA |

#### Alertas de Aviso (Email)
| Alerta | Condição |
|--------|----------|
| Uso de Tokens Anômalo | `increase(agent_token_usage_total[1h]) > 2 * avg_over_time(...[24h])` |
| Baixa Utilização de Recursos | `avg(rate(container_cpu_usage_seconds_total[5m])) < 0.3` |
| Tarefas Estagnadas | `benchmark_task_started_total - benchmark_task_completed_total > 100` |

---

## 6. Testes e Validação

### 6.1 Testes de Unidade

#### Estrutura de Testes
```
tests/
├── unit/
│   ├── test_agents.py
│   ├── test_benchmark.py
│   └── test_evaluation.py
├── integration/
│   ├── test_api.py
│   └── test_dataset_loader.py
└── e2e/
    └── test_full_workflow.py
```

#### Exemplo de Teste de Unidade
```python
# tests/unit/test_agents.py
import pytest
from agents.openai_adapter import OpenAIAgentAdapter, OpenAIConfig

@pytest.mark.asyncio
async def test_openai_adapter_success(mocker):
    """Testa resposta bem-sucedida do adapter OpenAI"""
    # Configura mock
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Test response"}}],
        "usage": {"total_tokens": 50}
    }
    mock_response.elapsed.total_seconds.return_value = 0.5
    
    mocker.patch("httpx.AsyncClient.post", return_value=mock_response)
    
    # Configura adapter
    config = OpenAIConfig(api_key="test-key")
    adapter = OpenAIAgentAdapter(config)
    
    # Executa teste
    result = await adapter.query("Hello", {"context": "test"})
    
    # Verifica resultados
    assert result["response"] == "Test response"
    assert result["usage"]["total_tokens"] == 50
    assert 0.4 <= result["latency"] <= 0.6
```

#### Cobertura de Testes
- **Mínimo Aceitável**: 80% de cobertura
- **Componentes Críticos**: 95%+ (sistema de avaliação, orquestração)
- **Relatório Automático**: Integrado ao pipeline CI/CD

### 6.2 Testes de Carga

#### Configuração do Locust
```python
# locustfile.py
class BenchmarkUser(HttpUser):
    wait_time = between(1, 5)
    
    @task(7)
    def submit_benchmark(self):
        payload = {
            "agents": random.sample(AGENT_LIST, k=random.randint(1, 3)),
            "benchmark": random.choice(BENCHMARK_TYPES),
            "config": generate_random_config()
        }
        
        with self.client.post(
            "/benchmark/run", 
            json=payload,
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code != 202:
                response.failure(f"Unexpected status code: {response.status_code}")
```

#### Resultados Esperados para 100 RPS
```
Type     Name                                                # reqs      # fails  |     Avg     Min     Max  Median  |   req/s failures/s
--------|---------------------------------------------------|-------|-----------|--------|-------|-------|--------|-------|-----------
POST     /benchmark/run                                      14,235     0(0.00%)  |    412     123    2487     389  |   47.50    0.00
GET      /benchmark/{id}                                      4,028     0(0.00%)  |     98      45     512      95  |   13.45    0.00
GET      /benchmark/list                                      2,015     0(0.00%)  |     76      32     387      72  |    6.73    0.00
--------|---------------------------------------------------|-------|-----------|--------|-------|-------|--------|-------|-----------
         Aggregated                                          20,278     0(0.00%)  |    312     32    2487     287  |   67.68    0.00
```

#### Critérios de Aceitação
- **Throughput**: > 80 RPS sustentado por 15 minutos
- **Latência P95**: < 2 segundos para submissão
- **Taxa de Erro**: < 0.1%
- **Estabilidade**: Nenhuma queda durante o teste

### 6.3 Benchmark de Referência

#### Protocolo de Benchmark
1. **Preparação**:
   - Limpar cache
   - Reiniciar workers
   - Carregar dataset pré-definido

2. **Execução**:
   - Executar 3 vezes para cada agent
   - Usar seeds fixos para reprodutibilidade
   - Registrar métricas detalhadas

3. **Avaliação**:
   - Comparar com resultados de referência
   - Analisar variações significativas
   - Gerar relatório detalhado

#### Dataset de Referência (MMLU Reasoning)
```json
{
  "benchmark_id": "mmlu-reasoning-v1",
  "description": "MMLU subset for logical reasoning evaluation",
  "categories": ["mathematics", "formal_logic", "symbolic_reasoning"],
  "total_questions": 150,
  "data": [
    {
      "id": "math-001",
      "category": "mathematics",
      "question": "If a car travels at 60 km/h for 2.5 hours...",
      "options": ["A) 45 km/h", "B) 48 km/h", "C) 52 km/h", "D) 55 km/h"],
      "answer": "C",
      "rationale": "Total distance = (60*2.5) + (40*1.5) = 210 km..."
    }
  ]
}
```

#### Resultados de Referência Esperados
| Agent | Precisão Geral | Matemática | Lógica Formal | Raciocínio Simbólico | Latência Média |
|-------|----------------|------------|---------------|----------------------|----------------|
| GPT-4 | 87.3% | 92.4% | 88.2% | 82.0% | 4.2s |
| Claude-3 | 82.1% | 85.6% | 84.0% | 80.4% | 6.8s |
| Llama-3 | 78.5% | 82.3% | 76.8% | 75.2% | 5.1s |

---

## 7. Operações e Manutenção

### 7.1 Troubleshooting

#### Problema Comum #1: Erros 500 ao Submeter Benchmarks
- **Sintomas**:
  - Respostas HTTP 500
  - Logs mostram `Database connection timeout`
  
- **Causa Provável**:
  - Conexões com o PostgreSQL esgotadas
  
- **Solução**:
  ```bash
  # Verificar conexões ativas
  kubectl exec -it <postgres-pod> -- psql -c "SELECT * FROM pg_stat_activity;"
  
  # Ajustar pool de conexões
  # No arquivo de configuração do serviço:
  DATABASE_POOL_SIZE=20
  DATABASE_MAX_OVERFLOW=10
  ```

#### Problema Comum #2: Agents Não Respondem
- **Sintomas**:
  - Status "running" por muito tempo
  - Logs mostram timeouts com APIs de agents
  
- **Causa Provável**:
  - Limite de taxa excedido nas APIs de agents
  - Configuração incorreta de chaves API
  
- **Solução**:
  ```bash
  # Verificar métricas de agents
  kubectl exec -it <grafana-pod> -- grafana-cli plugins ls
  
  # Ajustar configuração de rate limiting
  AGENT_RATE_LIMIT_OPENAI=60  # 60 requisições/minuto
  AGENT_RATE_LIMIT_ANTHROPIC=45
  ```

#### Fluxo de Diagnóstico
```mermaid
graph TD
    A[Problema Reportado] --> B{Erro no Cliente?}
    B -->|Sim| C[Verificar Requisição]
    B -->|Não| D{Erro no Serviço?}
    D -->|Sim| E[Verificar Logs do Serviço]
    D -->|Não| F{Erro nos Agents?}
    F -->|Sim| G[Verificar Conexão com Agents]
    F -->|Não| H{Erro no Banco?}
    H -->|Sim| I[Verificar Conexões com Banco]
    H -->|Não| J[Verificar Infraestrutura]
```

### 7.2 Atualizações

#### Ciclo de Release
- **Patch Releases** (semanal): Correções de bugs críticos
- **Minor Releases** (mensal): Novos features não quebráveis
- **Major Releases** (trimestral): Mudanças significativas

#### Checklist de Release
1. [ ] Testes de unidade e integração passando
2. [ ] Teste de carga com resultados aceitáveis
3. [ ] Documentação atualizada
4. [ ] Schema de banco migrado com sucesso
5. [ ] Canary release com 5% de tráfego
6. [ ] Rollout completo após 1 hora sem problemas

#### Rollback Procedure
1. Reverter para a versão anterior no Kubernetes:
   ```bash
   kubectl rollout undo deployment/benchmark-service
   ```
2. Verificar saúde do sistema:
   ```bash
   kubectl get pods -l app=benchmark
   curl http://api.benchmark.example.com/health
   ```
3. Monitorar métricas críticas por 30 minutos

### 7.3 Backup e Recuperação

#### Estratégia de Backup
- **Frequência**:
  - Resultados: Backup a cada 4 horas
  - Configurações: Backup diário
  - Datasets: Backup semanal

- **Localização**:
  - Região primária: AWS us-east-1
  - Região secundária: AWS eu-west-1

#### Procedimento de Recuperação
1. Restaurar banco de dados:
   ```bash
   pg_restore -h <DB_HOST> -U <USER> -d <DB_NAME> backup.dump
   ```
2. Restaurar datasets:
   ```bash
   aws s3 cp s3://backup-bucket/datasets/ ./datasets --recursive
   ```
3. Validar integridade:
   ```bash
   python validate_backups.py --dataset-path ./datasets
   ```

#### RTO/RPO
- **RTO (Recovery Time Objective)**: < 30 minutos
- **RPO (Recovery Point Objective)**: < 4 horas

---

## 8. Extensibilidade e Contribuição

### 8.1 Adicionando Novos Agents

#### Passo 1: Criar Adapter
```python
# agents/my_new_agent.py
from typing import Dict, Any
from .base import AgentInterface

class MyNewAgentConfig:
    api_key: str
    endpoint: str = "https://api.myagent.com/v1"
    timeout: float = 30.0

class MyNewAgentAdapter(AgentInterface):
    def __init__(self, config: MyNewAgentConfig):
        self.config = config
        # Inicialização do cliente
    
    async def query(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        # Implementação da chamada à API
        pass
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": "my-new-agent",
            "version": "1.0.0",
            "capabilities": ["text-generation", "reasoning"]
        }
```

#### Passo 2: Registrar no Sistema
```python
# agents/__init__.py
from .my_new_agent import MyNewAgentAdapter

# Mapeamento de nomes para adapters
AGENT_ADAPTERS = {
    "my-new-agent": MyNewAgentAdapter,
    # outros agents...
}
```

#### Passo 3: Adicionar Testes
```python
# tests/unit/test_my_new_agent.py
import pytest
from agents.my_new_agent import MyNewAgentAdapter, MyNewAgentConfig

@pytest.mark.asyncio
async def test_my_new_agent():
    config = MyNewAgentConfig(api_key="test")
    adapter = MyNewAgentAdapter(config)
    result = await adapter.query("Hello")
    assert "response" in result
```

### 8.2 Criando Novos Benchmarks

#### Estrutura de Dataset
```json
{
  "benchmark_id": "custom-benchmark-v1",
  "description": "Custom benchmark for specific use case",
  "categories": ["category1", "category2"],
  "metadata": {
    "source": "internal",
    "total_questions": 100,
    "difficulty": "medium"
  },
  "data": [
    {
      "id": "q001",
      "category": "category1",
      "question": "What is 2+2?",
      "options": ["A) 3", "B) 4", "C) 5", "D) 6"],
      "answer": "B",
      "rationale": "Basic arithmetic: 2+2=4",
      "expected_metrics": {
        "min_reasoning_steps": 1,
        "expected_time": 5.0
      }
    }
  ]
}
```

#### Processo de Adição
1. Criar arquivo JSON no formato acima
2. Armazenar em `datasets/custom-benchmark-v1.json`
3. Registrar no sistema:
   ```python
   # services/dataset_loader.py
   BENCHMARK_DATASETS = {
       "custom-benchmark-v1": "datasets/custom-benchmark-v1.json",
       # outros benchmarks...
   }
   ```
4. Adicionar testes de validação

### 8.3 Contribuição para o Projeto

#### Diretrizes de Contribuição
1. **Fork do repositório**
2. **Criar branch feature**:
   ```bash
   git checkout -b feature/my-feature
   ```
3. **Implementar mudanças** com testes
4. **Atualizar documentação**
5. **Submeter Pull Request** com descrição detalhada

#### Checklist de Pull Request
- [ ] Testes cobrindo novas funcionalidades
- [ ] Documentação atualizada
- [ ] Nenhuma quebra de compatibilidade
- [ ] Mensagens de commit claras e descritivas
- [ ] Formatação do código seguindo padrões

#### Processo de Revisão
1. Análise técnica pelo mantenedor
2. Testes de integração automática
3. Discussão de possíveis melhorias
4. Aprovação por 2 revisores
5. Merge após CI/CD passar

---

## 9. Apêndices

### 9.1 Glossário

| Termo | Definição |
|-------|-----------|
| **Agent** | Modelo de IA ou sistema avaliado no benchmark |
| **Benchmark** | Conjunto padronizado de tarefas para avaliação |
| **Adapter** | Componente que padroniza interface com agents |
| **Orquestrador** | Componente que gerencia execução de benchmarks |
| **LLM-as-a-Judge** | Uso de modelo de linguagem para avaliação subjetiva |
| **Throughput** | Número de operações concluídas por unidade de tempo |
| **P95 Latency** | Latência máxima para 95% das requisições |

### 9.2 Referências

#### Benchmarks Padrão
- **MMLU**: Massive Multitask Language Understanding
- **GSM8K**: Grade School Math 8K
- **BigBench**: Beyond the Imitation Game Benchmark
- **TruthfulQA**: Measuring Truthfulness in Language Models

#### Frameworks Relacionados
- **LangChain**: Framework para aplicações com LLMs
- **LlamaIndex**: Ferramenta para recuperação de informações
- **Weights & Biases**: Plataforma de experimentação de ML

#### Recursos Adicionais
- [Documentação OpenAPI](https://spec.openapis.org/oas/v3.0.3)
- [Guia de Boas Práticas de Microserviços](https://microservices.io)
- [Padrões de Projeto para Sistemas Distribuídos](https://docs.microsoft.com/en-us/azure/architecture/patterns/)

---

## 📬 Suporte e Contato

Para suporte técnico ou perguntas sobre o projeto:

- **Email**: support@benchmark.example.com
- **Issues no GitHub**: [github.com/your-org/benchmark-service/issues](https://github.com/your-org/benchmark-service/issues)
- **Documentação Completa**: [docs.benchmark.example.com](https://docs.benchmark.example.com)

---

© 2024 AI Benchmark Service. Todos os direitos reservados.  
Esta documentação é parte do projeto open source AI Benchmark Service.  
Contribuições são bem-vindas via GitHub.