# 🔒 Security Guide

This document outlines the security measures, best practices, and guidelines for the AI Benchmark Service.

## 🛡️ Security Architecture

### Defense in Depth Strategy

The AI Benchmark Service implements multiple layers of security:

1. **Network Security**
   - Container isolation
   - Service-to-service communication controls
   - Firewall rules and port restrictions

2. **Application Security**
   - Input validation and sanitization
   - Authentication and authorization
   - Secure coding practices

3. **Data Security**
   - Encryption at rest and in transit
   - Access controls and permissions
   - Audit logging

4. **Infrastructure Security**
   - Container image scanning
   - Runtime security monitoring
   - Regular security updates

### Security Boundaries

#### External Interfaces

- **Public API**: RESTful endpoints with authentication
- **Admin Interface**: Protected administrative functions
- **Monitoring Endpoints**: Metrics and health checks

#### Internal Components

- **Database**: PostgreSQL with role-based access
- **Cache**: Redis with authentication
- **Message Queue**: Redis with access controls
- **File Storage**: Local filesystem with permissions

## 🔑 Authentication and Authorization

### API Authentication

The service uses API key-based authentication:

```http
GET /api/benchmark/list HTTP/1.1
Host: api.benchmark.example.com
Authorization: Bearer YOUR_API_KEY
```

#### API Key Management

```python
# Generate secure API keys
import secrets
import hashlib

def generate_api_key():
    """Generate a cryptographically secure API key"""
    raw_key = secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    return raw_key, key_hash

# Store only the hash in database
# Return the raw key to user only once
```

#### Key Rotation

```bash
# Rotate API keys periodically
# 1. Generate new key
# 2. Distribute to users
# 3. Enable both old and new keys temporarily
# 4. Disable old key after migration period
# 5. Remove old key from system
```

### Role-Based Access Control (RBAC)

#### Permission Scopes

1. **benchmark:read** - View benchmark information
2. **benchmark:write** - Create and modify benchmarks
3. **results:read** - Access benchmark results
4. **admin:full** - Administrative privileges

#### Implementation

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

def require_permission(permission: str):
    def verify_permission(credentials: HTTPAuthorizationCredentials = Depends(security)):
        # Verify API key and check permissions
        api_key = credentials.credentials
        user_permissions = get_user_permissions(api_key)
        
        if permission not in user_permissions:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions"
            )
        
        return credentials
    return verify_permission

# Usage in endpoints
@app.get("/api/benchmark/list")
async def list_benchmarks(
    credentials: HTTPAuthorizationCredentials = Depends(require_permission("benchmark:read"))
):
    # Implementation
    pass
```

## 🔐 Data Protection

### Encryption

#### Data at Rest

```python
# Database encryption
# PostgreSQL with SSL/TLS
DATABASE_URL = "postgresql://user:pass@host:port/db?sslmode=require"

# File encryption for sensitive data
from cryptography.fernet import Fernet

# Generate key
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Encrypt sensitive data
encrypted_data = cipher_suite.encrypt(b"sensitive information")

# Decrypt data
decrypted_data = cipher_suite.decrypt(encrypted_data)
```

#### Data in Transit

```python
# HTTPS enforcement
from fastapi import FastAPI
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()
app.add_middleware(HTTPSRedirectMiddleware)

# SSL/TLS configuration in production
# Use reverse proxy (Nginx) with SSL termination
```

### Data Masking

```python
# Mask sensitive information in logs
import re

def mask_sensitive_data(data):
    """Mask sensitive information in logs"""
    # Mask API keys
    data = re.sub(r'Bearer [a-zA-Z0-9_-]{32,}', 'Bearer ***MASKED***', data)
    
    # Mask database credentials
    data = re.sub(r'postgresql://[^:]+:[^@]+@', 'postgresql://***:***@', data)
    
    return data
```

## 🛡️ Input Validation and Sanitization

### API Input Validation

```python
from pydantic import BaseModel, validator
import re

class BenchmarkRequest(BaseModel):
    agents: List[str]
    benchmark: str
    config: Optional[Dict[str, Any]] = None
    
    @validator('agents')
    def validate_agents(cls, v):
        if not v:
            raise ValueError('At least one agent is required')
        if len(v) > 10:
            raise ValueError('Maximum 10 agents allowed')
        return v
    
    @validator('benchmark')
    def validate_benchmark(cls, v):
        # Validate benchmark ID format
        if not re.match(r'^[a-zA-Z0-9-]+$', v):
            raise ValueError('Invalid benchmark ID format')
        return v
```

### SQL Injection Prevention

```python
# Use parameterized queries
import psycopg2

def get_benchmark_status(run_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Safe - parameterized query
    cursor.execute("SELECT * FROM benchmarks WHERE run_id = %s", (run_id,))
    
    # Unsafe - string concatenation (NEVER do this)
    # cursor.execute(f"SELECT * FROM benchmarks WHERE run_id = '{run_id}'")
    
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result
```

### XSS Prevention

```python
# Sanitize output for web interfaces
import html

def sanitize_output(data):
    """Sanitize data for safe HTML output"""
    if isinstance(data, str):
        return html.escape(data)
    elif isinstance(data, dict):
        return {k: sanitize_output(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_output(item) for item in data]
    return data
```

## 🕵️‍♂️ Security Monitoring

### Audit Logging

```python
import logging
from datetime import datetime

# Configure audit logger
audit_logger = logging.getLogger('audit')
audit_handler = logging.FileHandler('audit.log')
audit_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
audit_handler.setFormatter(audit_formatter)
audit_logger.addHandler(audit_handler)
audit_logger.setLevel(logging.INFO)

def log_audit_event(event_type, user_id, details):
    """Log security-relevant events"""
    audit_logger.info(
        f"AUDIT: {event_type} - User: {user_id} - Details: {details}"
    )

# Usage examples
log_audit_event("API_KEY_GENERATED", "admin", {"key_id": "abc123"})
log_audit_event("BENCHMARK_CREATED", "user123", {"benchmark_id": "test-bench"})
log_audit_event("UNAUTHORIZED_ACCESS", "anonymous", {"endpoint": "/admin"})
```

### Intrusion Detection

```python
# Monitor for suspicious activity
from collections import defaultdict
import time

class SecurityMonitor:
    def __init__(self):
        self.request_counts = defaultdict(list)
        self.failed_logins = defaultdict(int)
    
    def log_request(self, ip_address):
        """Log incoming requests for rate limiting"""
        now = time.time()
        self.request_counts[ip_address].append(now)
        
        # Keep only recent requests (last 5 minutes)
        cutoff = now - 300
        self.request_counts[ip_address] = [
            timestamp for timestamp in self.request_counts[ip_address]
            if timestamp > cutoff
        ]
        
        # Check for rate limiting
        if len(self.request_counts[ip_address]) > 100:  // 100 requests per 5 minutes
            self.alert_rate_limiting(ip_address)
    
    def log_failed_login(self, ip_address):
        """Track failed login attempts"""
        self.failed_logins[ip_address] += 1
        
        if self.failed_logins[ip_address] > 5:  // 5 failed attempts
            self.alert_brute_force(ip_address)
    
    def alert_rate_limiting(self, ip_address):
        """Alert on potential DoS attack"""
        print(f"ALERT: Rate limiting triggered for IP {ip_address}")
        // Send alert to security team
    
    def alert_brute_force(self, ip_address):
        """Alert on potential brute force attack"""
        print(f"ALERT: Brute force attempt detected from IP {ip_address}")
        // Send alert to security team
        // Consider blocking IP temporarily
```

### Vulnerability Scanning

```bash
// Dependency security scanning
pip install safety
safety check -r requirements.txt

// Container image scanning
docker scan ai-benchmark-service

// Static code analysis
pip install bandit
bandit -r benchmark_service/

// Dockerfile security analysis
docker scout cves ai-benchmark-service
```

## 🔥 Incident Response

### Security Incident Classification

#### Critical (P1)
- Data breach or exposure
- System compromise
- API key compromise
- Denial of service

#### High (P2)
- Unauthorized access attempts
- Suspicious activity patterns
- Configuration vulnerabilities
- Dependency security issues

#### Medium (P3)
- Failed login attempts
- Rate limiting triggers
- Minor configuration issues
- Outdated dependencies

#### Low (P4)
- Informational findings
- Minor security improvements
- Documentation updates
- Best practice recommendations

### Incident Response Procedures

#### Initial Response (0-30 minutes)

1. **Containment**
   - Isolate affected systems
   - Block malicious IP addresses
   - Disable compromised accounts
   - Stop vulnerable services

2. **Assessment**
   - Determine scope of impact
   - Identify attack vectors
   - Preserve evidence
   - Document timeline

3. **Communication**
   - Notify security team
   - Alert stakeholders
   - Coordinate response efforts
   - Prepare incident report

#### Investigation (30 minutes - 24 hours)

1. **Forensic Analysis**
   - Review logs and metrics
   - Analyze system state
   - Identify root cause
   - Determine attack methods

2. **Impact Assessment**
   - Data exposure analysis
   - System integrity check
   - User impact evaluation
   - Business impact assessment

3. **Remediation Planning**
   - Develop fix strategy
   - Prioritize actions
   - Estimate timeline
   - Resource allocation

#### Recovery (24-72 hours)

1. **System Restoration**
   - Apply security patches
   - Update configurations
   - Restore from clean backups
   - Verify system integrity

2. **Validation**
   - Security testing
   - Functional testing
   - Performance testing
   - User acceptance testing

3. **Monitoring**
   - Enhanced monitoring
   - Alert tuning
   - Log analysis
   - Performance metrics

#### Post-Incident (72+ hours)

1. **Lessons Learned**
   - Root cause analysis
   - Process improvements
   - Technology enhancements
   - Training needs

2. **Documentation**
   - Incident report
   - Timeline documentation
   - Evidence preservation
   - Recovery procedures

3. **Prevention**
   - Security controls implementation
   - Policy updates
   - Training programs
   - Regular assessments

## 🔧 Security Best Practices

### Development Security

#### Secure Coding Guidelines

1. **Input Validation**
   - Validate all inputs
   - Use allowlists, not blocklists
   - Sanitize output
   - Handle errors gracefully

2. **Authentication Security**
   - Use strong password policies
   - Implement multi-factor authentication
   - Rotate credentials regularly
   - Store passwords securely

3. **Authorization Security**
   - Principle of least privilege
   - Role-based access control
   - Regular permission reviews
   - Audit access logs

4. **Data Protection**
   - Encrypt sensitive data
   - Minimize data retention
   - Secure data transmission
   - Implement data loss prevention

#### Code Review Security Checklist

- [ ] Input validation implemented
- [ ] Authentication properly enforced
- [ ] Authorization checks in place
- [ ] Sensitive data properly handled
- [ ] Error messages don't leak information
- [ ] Dependencies are up to date
- [ ] Security headers configured
- [ ] Logging doesn't include sensitive data

### Infrastructure Security

#### Container Security

```dockerfile
// Use minimal base images
FROM python:3.11-slim

// Run as non-root user
RUN useradd -m appuser
USER appuser

// Copy only necessary files
COPY --chown=appuser:appuser requirements.txt .
COPY --chown=appuser:appuser . .

// Remove build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
```

#### Network Security

```yaml
// docker-compose.yml
version: '3.8'
services:
  web:
    // ... other configuration
    networks:
      - frontend
      - backend
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
      - /var/run

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  // No external access
```

#### Environment Security

```bash
// Secure file permissions
chmod 600 .env
chmod 644 docker-compose.yml
chmod 755 scripts/*.sh

// Secure directory permissions
chmod 755 .
chmod 755 benchmark_service/
chmod 644 benchmark_service/**/*.py

// Remove sensitive files from version control
echo ".env" >> .gitignore
echo "secrets/" >> .gitignore
echo "*.key" >> .gitignore
```

### Compliance and Standards

#### GDPR Compliance

```python
// Data subject rights implementation
class UserDataManager:
    def export_user_data(self, user_id):
        """Export all user data (Right to Data Portability)"""
        // Implementation
        
    def delete_user_data(self, user_id):
        """Delete user data (Right to Erasure)"""
        // Implementation
        
    def update_user_data(self, user_id, data):
        """Update user data (Right to Rectification)"""
        // Implementation
```

#### SOC 2 Compliance

- [ ] Security policies documented
- [ ] Access controls implemented
- [ ] Monitoring and logging in place
- [ ] Incident response procedures
- [ ] Regular security assessments
- [ ] Employee security training

## 🛡️ Security Testing

### Automated Security Testing

#### Dependency Scanning

```bash
// Safety - Python dependency security
pip install safety
safety check -r requirements.txt

// Bandit - Python security linter
pip install bandit
bandit -r benchmark_service/

// Docker Scout - Container image scanning
docker scout cves ai-benchmark-service
```

#### Configuration Scanning

```bash
// Check Dockerfile security
docker scout recommendations ai-benchmark-service

// Check for secrets in code
pip install detect-secrets
detect-secrets scan > .secrets.baseline
```

#### Runtime Security

```bash
// Container runtime monitoring
docker run --security-opt=no-new-privileges \
           --read-only \
           --tmpfs /tmp \
           ai-benchmark-service
```

### Manual Security Testing

#### Penetration Testing

1. **Reconnaissance**
   - Identify exposed endpoints
   - Map attack surface
   - Gather version information

2. **Exploitation Attempts**
   - SQL injection testing
   - XSS testing
   - Authentication bypass attempts
   - Authorization escalation testing

3. **Post-Exploitation**
   - Data exfiltration attempts
   - Privilege escalation
   - Persistence mechanisms

#### Security Code Review

```python
// Example of insecure code
def get_user_data(user_id):
    // VULNERABLE: Direct string concatenation
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
    return cursor.fetchall()

// SECURE: Parameterized queries
def get_user_data_secure(user_id):
    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    return cursor.fetchall()
```

## 📚 Security Resources

### Training and Awareness

#### Security Training Programs

1. **Developer Security Training**
   - Secure coding practices
   - Common vulnerabilities
   - Security testing methods
   - Incident response procedures

2. **Operations Security Training**
   - Infrastructure security
   - Monitoring and alerting
   - Patch management
   - Backup and recovery

3. **User Security Training**
   - Password security
   - Phishing awareness
   - Social engineering
   - Data protection

### Security Tools and Resources

#### Open Source Security Tools

1. **Static Analysis**
   - Bandit (Python)
   - Safety (Dependencies)
   - Detect-secrets

2. **Dynamic Analysis**
   - OWASP ZAP
   - SQLMap
   - Nikto

3. **Container Security**
   - Docker Scout
   - Clair
   - Trivy

#### Security Standards and Frameworks

1. **OWASP Top 10**
   - Injection
   - Broken Authentication
   - Sensitive Data Exposure
   - XML External Entities
   - Broken Access Control
   - Security Misconfiguration
   - Cross-Site Scripting
   - Insecure Deserialization
   - Using Components with Known Vulnerabilities
   - Insufficient Logging & Monitoring

2. **NIST Cybersecurity Framework**
   - Identify
   - Protect
   - Detect
   - Respond
   - Recover

3. **ISO 27001**
   - Information security management
   - Risk assessment
   - Security controls
   - Continuous improvement

This security guide provides comprehensive coverage of security measures for the AI Benchmark Service. Regular updates and reviews ensure that security practices remain current and effective against evolving threats.