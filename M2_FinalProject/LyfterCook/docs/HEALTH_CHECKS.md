# Health Check Endpoints

LyfterCook provides comprehensive health check endpoints for monitoring and orchestration.

## Overview

Three health check endpoints are available:

| Endpoint | Purpose | Use Case |
|----------|---------|----------|
| `/health` | Basic liveness | Simple "is the app running?" check |
| `/health/ready` | Readiness with dependencies | Load balancer / Kubernetes readiness |
| `/health/live` | Process liveness | Kubernetes liveness probe |

---

## Endpoints

### 1. Basic Health Check

**Endpoint**: `GET /health`

**Purpose**: Quick check that the application is running.

**Use For**:
- Simple uptime monitoring
- Basic availability checks
- Development/debugging

**Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "LyfterCook API",
  "version": "2.0.0"
}
```

**Example**:
```bash
curl http://localhost:5000/health
```

---

### 2. Readiness Check

**Endpoint**: `GET /health/ready`

**Purpose**: Verify that all dependencies (database, cache) are available and the service is ready to handle requests.

**Use For**:
- Load balancer health checks
- Kubernetes readiness probes
- Pre-deployment validation
- Monitoring dashboards

**Response** (200 OK - All healthy):
```json
{
  "service": "LyfterCook API",
  "status": "ready",
  "checks": {
    "database": {
      "status": "healthy",
      "type": "PostgreSQL"
    },
    "cache": {
      "status": "healthy",
      "type": "Redis"
    }
  }
}
```

**Response** (503 Service Unavailable - Dependencies down):
```json
{
  "service": "LyfterCook API",
  "status": "not_ready",
  "checks": {
    "database": {
      "status": "unhealthy",
      "error": "could not connect to server"
    },
    "cache": {
      "status": "healthy",
      "type": "Redis"
    }
  }
}
```

**Response** (200 OK - Cache disabled):
```json
{
  "service": "LyfterCook API",
  "status": "ready",
  "checks": {
    "database": {
      "status": "healthy",
      "type": "PostgreSQL"
    },
    "cache": {
      "status": "disabled",
      "type": "Redis"
    }
  }
}
```

**Example**:
```bash
curl http://localhost:5000/health/ready
```

**Status Codes**:
- `200 OK`: Service is ready to handle requests
- `503 Service Unavailable`: One or more dependencies are unavailable

---

### 3. Liveness Check

**Endpoint**: `GET /health/live`

**Purpose**: Verify that the application process is alive and responding.

**Use For**:
- Kubernetes liveness probes
- Process restart triggers
- Deadlock detection

**Response** (200 OK):
```json
{
  "status": "alive",
  "service": "LyfterCook API"
}
```

**Example**:
```bash
curl http://localhost:5000/health/live
```

**Note**: If this endpoint doesn't respond, the application process should be restarted.

---

## Usage Examples

### Development

**Check everything is working**:
```bash
# Basic health
curl http://localhost:5000/health

# Check dependencies
curl http://localhost:5000/health/ready
```

### Monitoring Script

```bash
#!/bin/bash
# Simple health check script

HEALTH=$(curl -s http://localhost:5000/health/ready | jq -r '.status')

if [ "$HEALTH" == "ready" ]; then
    echo "✅ Service is healthy"
    exit 0
else
    echo "❌ Service is not ready"
    exit 1
fi
```

### Python Monitoring

```python
import requests

def check_service_health(base_url="http://localhost:5000"):
    """Check if LyfterCook API is healthy."""
    try:
        # Check readiness (includes dependencies)
        response = requests.get(f"{base_url}/health/ready", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'ready':
                print("✅ Service is ready")
                return True
            else:
                print(f"⚠️ Service not ready: {data}")
                return False
        else:
            print(f"❌ Service unhealthy: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot reach service: {e}")
        return False

# Usage
if __name__ == "__main__":
    check_service_health()
```

---

## Kubernetes Configuration

### Deployment with Probes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lyftercook-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: lyftercook:latest
        ports:
        - containerPort: 5000
        
        # Liveness probe - restart if not responding
        livenessProbe:
          httpGet:
            path: /health/live
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        # Readiness probe - don't send traffic if not ready
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 5000
          initialDelaySeconds: 15
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
```

**Explanation**:
- **Liveness**: If `/health/live` fails 3 times, restart the pod
- **Readiness**: If `/health/ready` fails 2 times, remove from load balancer

---

## Docker Compose Health Check

```yaml
version: '3.8'
services:
  api:
    image: lyftercook:latest
    ports:
      - "5000:5000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health/ready"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

## Load Balancer Configuration

### Nginx Upstream Health Check

```nginx
upstream lyftercook_backend {
    server api1.example.com:5000 max_fails=3 fail_timeout=30s;
    server api2.example.com:5000 max_fails=3 fail_timeout=30s;
    
    # Health check (Nginx Plus feature)
    health_check uri=/health/ready interval=10s fails=3 passes=2;
}
```

### HAProxy Health Check

```
backend lyftercook_api
    option httpchk GET /health/ready
    http-check expect status 200
    
    server api1 10.0.1.10:5000 check inter 10s fall 3 rise 2
    server api2 10.0.1.11:5000 check inter 10s fall 3 rise 2
```

---

## Troubleshooting

### Database Check Fails

**Symptom**:
```json
{
  "status": "not_ready",
  "checks": {
    "database": {
      "status": "unhealthy",
      "error": "connection refused"
    }
  }
}
```

**Solutions**:
1. Check PostgreSQL is running: `pg_isready -h localhost -p 5432`
2. Verify connection settings in `.env`
3. Check network connectivity
4. Review database logs

### Cache Check Fails

**Symptom**:
```json
{
  "status": "not_ready",
  "checks": {
    "cache": {
      "status": "unhealthy",
      "error": "connection timeout"
    }
  }
}
```

**Solutions**:
1. Check Redis is running: `redis-cli ping`
2. Verify REDIS_HOST and REDIS_PORT in `.env`
3. Check if Redis password is required
4. Review Redis logs

**Note**: If cache is disabled (`cache.enabled = False`), the service is still considered ready.

---

## Best Practices

### 1. Use Appropriate Endpoints

- **Simple monitoring**: Use `/health`
- **Load balancer health**: Use `/health/ready`
- **Container orchestration**: Use both `/health/live` and `/health/ready`

### 2. Set Reasonable Timeouts

```yaml
# Kubernetes example
readinessProbe:
  timeoutSeconds: 3  # Short timeout
  periodSeconds: 5   # Check frequently
  
livenessProbe:
  timeoutSeconds: 5   # Slightly longer
  periodSeconds: 10   # Check less frequently
```

### 3. Avoid Restart Loops

- Set `initialDelaySeconds` high enough for app startup
- Use `failureThreshold` to allow transient failures
- Liveness should be less aggressive than readiness

### 4. Monitor Health Check Endpoints

```python
# Add metrics
from prometheus_client import Counter

health_check_counter = Counter('health_check_requests_total', 
                               'Total health check requests',
                               ['endpoint', 'status'])

@app.route('/health/ready')
def readiness_check():
    result, status_code = do_checks()
    health_check_counter.labels(endpoint='ready', status=status_code).inc()
    return result, status_code
```

---

## Security Considerations

### 1. Don't Expose Sensitive Information

❌ **Bad**:
```json
{
  "database": {
    "host": "prod-db-master.internal",
    "password": "secret123"
  }
}
```

✅ **Good**:
```json
{
  "database": {
    "status": "healthy",
    "type": "PostgreSQL"
  }
}
```

### 2. Rate Limiting

Health checks can be abused for DDoS. Consider rate limiting:

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/health/ready')
@limiter.limit("60 per minute")
def readiness_check():
    # ...
```

### 3. Authentication (Optional)

For sensitive environments, require authentication:

```python
@app.route('/health/ready')
@jwt_required(optional=True)  # Allow but log authenticated checks
def readiness_check():
    # Log who's checking
    identity = get_jwt_identity()
    if identity:
        logger.info(f"Health check by {identity}")
    # ...
```

---

## Summary

| Endpoint | Response Time | Checks | Use Case |
|----------|---------------|--------|----------|
| `/health` | ~1ms | None | Basic monitoring |
| `/health/ready` | ~50-100ms | DB + Cache | Load balancer, readiness |
| `/health/live` | ~1ms | None | Liveness probe |

**Key Takeaways**:
- ✅ Use `/health/ready` for production health checks
- ✅ Use `/health/live` for container liveness
- ✅ Set reasonable timeouts and retry policies
- ✅ Monitor health check metrics
- ⚠️ Don't expose sensitive information
