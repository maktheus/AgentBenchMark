# 🚀 Deployment Guide

This guide provides detailed instructions for deploying the AI Benchmark Service in different environments.

## 📋 Prerequisites

Before deploying, ensure you have:

1. **Docker** (version 20.10 or higher)
2. **Docker Compose** (version 2.10 or higher)
3. **Git** for version control
4. **API keys** for OpenAI and Anthropic (if using cloud agents)

## 🛠️ Local Development Deployment

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/benchmark-service.git
cd benchmark-service
```

### 2. Configure Environment Variables

Copy the example environment file and update with your values:

```bash
cp .env.example .env
```

Edit `.env` with your actual API keys and configuration:

```bash
# Database
DB_HOST=postgres
DB_NAME=benchmark_db
DB_USER=benchmark_user
DB_PASSWORD=benchmark_password

# Agent API Keys
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

### 3. Start the Development Environment

Use the provided script to start all services:

```bash
./scripts/start-dev.sh
```

Or manually with Docker Compose:

```bash
docker-compose up --build -d
```

### 4. Access the Services

- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Local Agent**: http://localhost:8001

## ☁️ Cloud Deployment (Free Tier Options)

### Option 1: Render.com (Free Tier)

Render offers a free tier that's perfect for POC deployments:

1. Fork the repository to your GitHub account
2. Sign up at [render.com](https://render.com)
3. Create a new Web Service:
   - Connect your GitHub repository
   - Set Build Command: `pip install -r requirements.txt`
   - Set Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables from your `.env` file
   - Set plan to "Free"

### Option 2: Railway.app (Free Tier)

Railway provides a simple deployment platform:

1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Initialize project: `railway init`
4. Deploy: `railway up`
5. Add environment variables: `railway variables`

### Option 3: Heroku (Free Tier - Limited)

Note: Heroku's free tier has limitations but works for POC:

1. Install Heroku CLI
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Set buildpack: `heroku buildpacks:set heroku/python`
5. Deploy: `git push heroku main`
6. Set config vars: `heroku config:set KEY=VALUE`

## 🐳 Docker Deployment

### Single Container Deployment

For a simple single-container deployment:

```bash
# Build the image
docker build -t ai-benchmark-service .

# Run the container
docker run -d \\
  --name benchmark-service \\
  -p 8000:8000 \\
  -e OPENAI_API_KEY=your-key \\
  -e ANTHROPIC_API_KEY=your-key \\
  ai-benchmark-service
```

### Multi-Container Deployment

Using the provided docker-compose.yml:

```bash
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🌐 Production Deployment

### Kubernetes Deployment

For production environments, use the provided Kubernetes manifests:

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check pod status
kubectl get pods

# Check service status
kubectl get services
```

### Environment-Specific Configuration

Create environment-specific `.env` files:

```bash
# Development
cp .env.example .env.development

# Staging
cp .env.example .env.staging

# Production
cp .env.example .env.production
```

## 🔧 Configuration Management

### Database Migration

Run database migrations:

```bash
# Using Alembic
alembic upgrade head
```

### Monitoring Setup

The system includes built-in monitoring:

1. **Prometheus**: Metrics collection at `/metrics`
2. **Grafana**: Dashboard visualization
3. **Health Checks**: `/health` and `/ready` endpoints

### Backup and Restore

Regular database backups:

```bash
# Backup
pg_dump -h localhost -U benchmark_user benchmark_db > backup.sql

# Restore
psql -h localhost -U benchmark_user benchmark_db < backup.sql
```

## 🔒 Security Considerations

### API Keys Management

Never commit API keys to version control. Use:

1. Environment variables
2. Secret management systems
3. Kubernetes secrets for production

### Network Security

Configure firewalls to restrict access:

```bash
# Only allow necessary ports
ufw allow 22    # SSH
ufw allow 8000  # API
ufw allow 3000  # Grafana
ufw allow 9090  # Prometheus
ufw enable
```

### Data Encryption

Enable SSL/TLS for production:

```bash
# In docker-compose.yml
ports:
  - "443:8000"
volumes:
  - ./ssl/cert.pem:/app/cert.pem
  - ./ssl/key.pem:/app/key.pem
```

## 📊 Monitoring and Logging

### Health Checks

The system provides built-in health checks:

```bash
# Liveness probe
curl http://localhost:8000/health

# Readiness probe
curl http://localhost:8000/ready
```

### Performance Monitoring

Access Grafana dashboards:

1. Open http://localhost:3000
2. Login with admin/admin
3. Navigate to the AI Benchmark dashboard

### Log Management

View container logs:

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
```

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps
   
   # Restart database service
   docker-compose restart postgres
   ```

2. **API Keys Not Set**
   ```bash
   # Verify environment variables
   docker-compose exec web env | grep API_KEY
   ```

3. **Insufficient Memory**
   ```bash
   # Check system resources
   docker stats
   
   # Adjust Docker resources in Docker Desktop
   ```

### Debugging

Enable debug mode:

```bash
# In .env file
DEBUG=True
LOG_LEVEL=DEBUG
```

View detailed logs:

```bash
docker-compose logs --tail 100 -f web
```

## 🔄 CI/CD Integration

### GitHub Actions

The repository includes GitHub Actions workflows:

```bash
# Workflow files
.github/workflows/ci-cd.yml
.github/workflows/deployment.yml
```

### Automated Testing

Tests run automatically on each push:

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# End-to-end tests
pytest tests/e2e/
```

## 📈 Scaling

### Horizontal Scaling

Scale web services:

```bash
# Scale to 3 instances
docker-compose up --scale web=3 -d
```

### Load Balancing

For production, use a load balancer:

```bash
# Example Nginx configuration
upstream benchmark_service {
    server web1:8000;
    server web2:8000;
    server web3:8000;
}
```

## 📚 Additional Resources

- [API Documentation](http://localhost:8000/docs)
- [Grafana Dashboards](http://localhost:3000)
- [Prometheus Metrics](http://localhost:9090)
- [Project Wiki](https://github.com/your-org/benchmark-service/wiki)

For support, contact: support@benchmark.example.com