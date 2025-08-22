# ⚙️ Configuración Avanzada - MCP Health Check Service

## 🎯 Descripción

Este documento describe las opciones de configuración avanzada disponibles para personalizar el comportamiento del MCP Health Check Service según tus necesidades específicas.

## 📁 Estructura de Configuración

### Archivo Principal: `src/config/audit.yaml`

```yaml
# Configuración de endpoints por defecto
endpoints:
  base_url: "http://localhost:8080"
  readiness: "/readiness"
  liveness: "/liveness"

# Umbrales de latencia y cobertura
thresholds:
  http_latency_ms: 300
  coverage_min: 0.80

# Configuración de servicios individuales
services:
  api_principal:
    name: "API Principal"
    base_url: "https://api.miservicio.com"
    readiness: "/health/ready"
    liveness: "/health/live"
    max_latency_ms: 200
    critical: true
    
  api_secundaria:
    name: "API Secundaria"
    base_url: "https://api2.miservicio.com"
    readiness: "/ready"
    liveness: "/live"
    max_latency_ms: 300
    critical: false
    
  base_datos:
    name: "Base de Datos"
    base_url: "https://db.miservicio.com"
    readiness: "/health/ready"
    liveness: "/health/live"
    max_latency_ms: 500
    critical: true
    
  cache:
    name: "Cache Redis"
    base_url: "https://cache.miservicio.com"
    readiness: "/ping"
    liveness: "/ping"
    max_latency_ms: 100
    critical: false

# Configuración de alertas
alerts:
  enabled: true
  max_consecutive_failures: 3
  notification_channels: ["log", "console", "email"]
  email:
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "alerts@miservicio.com"
    password: "${SMTP_PASSWORD}"
    recipients: ["admin@miservicio.com", "devops@miservicio.com"]
  
# Configuración de retry y timeout
retry:
  max_attempts: 3
  delay_between_attempts_ms: 1000
  exponential_backoff: true

# Configuración de logging
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "/var/log/mcp_health.log"
  max_file_size_mb: 10
  backup_count: 5

# Configuración de métricas
metrics:
  enabled: true
  prometheus_endpoint: "/metrics"
  custom_metrics:
    - name: "service_uptime"
      type: "gauge"
      description: "Tiempo de actividad del servicio"
    - name: "response_time_p95"
      type: "histogram"
      description: "Percentil 95 del tiempo de respuesta"

# Configuración de notificaciones
notifications:
  slack:
    webhook_url: "${SLACK_WEBHOOK_URL}"
    channel: "#alerts"
    username: "MCP Health Bot"
    icon_emoji: ":warning:"
  
  teams:
    webhook_url: "${TEAMS_WEBHOOK_URL}"
    title: "Health Check Alert"
    
  webhook:
    url: "${WEBHOOK_URL}"
    headers:
      Authorization: "Bearer ${WEBHOOK_TOKEN}"
      Content-Type: "application/json"

# Configuración de escalado
scaling:
  auto_scaling: false
  min_instances: 1
  max_instances: 5
  scale_up_threshold: 80
  scale_down_threshold: 20
```

## 🔧 Variables de Entorno

### Archivo `.env`

```bash
# Configuración del servidor MCP
MCP_HOST=0.0.0.0
MCP_PORT=8000
MCP_PROXY_TOKEN=tu_token_secreto_aqui

# Configuración de base de datos (si usas persistencia)
DATABASE_URL=postgresql://user:password@localhost:5432/mcp_health
REDIS_URL=redis://localhost:6379/0

# Configuración de notificaciones
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/XXX/YYY/ZZZ
WEBHOOK_URL=https://api.miservicio.com/webhooks/health
WEBHOOK_TOKEN=tu_token_webhook

# Configuración de email
SMTP_PASSWORD=tu_password_smtp
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Configuración de logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/mcp_health.log

# Configuración de métricas
PROMETHEUS_ENABLED=true
METRICS_PORT=9090

# Configuración de seguridad
JWT_SECRET=tu_jwt_secret_muy_seguro
API_KEY=tu_api_key_para_acceso_externo

# Configuración de timeouts
HTTP_TIMEOUT_MS=5000
HEALTH_CHECK_INTERVAL_MS=30000
ALERT_COOLDOWN_MS=300000
```

## 🚀 Configuración de Docker

### Dockerfile Avanzado

```dockerfile
# Dockerfile para el servicio MCP con optimizaciones
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    vim \
    htop \
    net-tools \
    iputils-ping \
    telnet \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 mcpuser && \
    mkdir -p /app/logs && \
    chown -R mcpuser:mcpuser /app

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt ./
COPY pyproject.toml ./

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/logs /app/config /app/data && \
    chown -R mcpuser:mcpuser /app

# Cambiar a usuario no-root
USER mcpuser

# Exponer puertos
EXPOSE 8000 9090

# Variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check del contenedor
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando por defecto
CMD ["python", "mcp_server.py", "--sse"]
```

### Docker Compose Avanzado

```yaml
version: '3.8'

services:
  mcp-service:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        BUILD_ENV: production
    container_name: mcp-service
    restart: unless-stopped
    
    # Configuración de recursos
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
    
    # Configuración de red
    networks:
      - mcp-network
      - monitoring-network
    
    # Puertos
    ports:
      - "8000:8000"  # MCP SSE
      - "9090:9090"  # Métricas Prometheus
    
    # Variables de entorno
    environment:
      - MCP_HOST=0.0.0.0
      - MCP_PORT=8000
      - MCP_PROXY_TOKEN=${MCP_PROXY_TOKEN}
      - PYTHONPATH=/app
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    
    # Volúmenes
    volumes:
      - ./src:/app/src:ro
      - ./config:/app/config:ro
      - ./logs:/app/logs
      - ./data:/app/data
      - /var/run/docker.sock:/var/run/docker.sock:ro
    
    # Configuración de health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    
    # Configuración de logging
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    
    # Dependencias
    depends_on:
      - redis
      - postgres
    
    # Configuración de seguridad
    security_opt:
      - no-new-privileges:true
    read_only: false
    tmpfs:
      - /tmp:noexec,nosuid,size=100m

  # Base de datos para persistencia (opcional)
  postgres:
    image: postgres:15-alpine
    container_name: mcp-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=mcp_health
      - POSTGRES_USER=mcpuser
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - mcp-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mcpuser -d mcp_health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis para cache y sesiones (opcional)
  redis:
    image: redis:7-alpine
    container_name: mcp-redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - mcp-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Prometheus para métricas (opcional)
  prometheus:
    image: prom/prometheus:latest
    container_name: mcp-prometheus
    restart: unless-stopped
    ports:
      - "9091:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    networks:
      - monitoring-network
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'

  # Grafana para visualización (opcional)
  grafana:
    image: grafana/grafana:latest
    container_name: mcp-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources:ro
    networks:
      - monitoring-network
    depends_on:
      - prometheus

networks:
  mcp-network:
    driver: bridge
    internal: false
  monitoring-network:
    driver: bridge
    internal: false

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
```

## 📊 Configuración de Métricas

### Archivo de Configuración de Prometheus

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'mcp-service'
    static_configs:
      - targets: ['mcp-service:9090']
    metrics_path: '/metrics'
    scrape_interval: 10s
    
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    metrics_path: '/metrics'
    
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    metrics_path: '/metrics'
```

### Configuración de Grafana

```json
// monitoring/grafana/datasources/prometheus.json
{
  "name": "Prometheus",
  "type": "prometheus",
  "access": "proxy",
  "url": "http://prometheus:9090",
  "isDefault": true
}
```

## 🔐 Configuración de Seguridad

### Archivo de Configuración de Seguridad

```yaml
# security_config.yaml
security:
  # Autenticación
  authentication:
    enabled: true
    method: "jwt"
    jwt_secret: "${JWT_SECRET}"
    token_expiry_hours: 24
    
  # Autorización
  authorization:
    enabled: true
    roles:
      - name: "admin"
        permissions: ["read", "write", "delete", "admin"]
      - name: "operator"
        permissions: ["read", "write"]
      - name: "viewer"
        permissions: ["read"]
    
  # Rate limiting
  rate_limiting:
    enabled: true
    requests_per_minute: 100
    burst_size: 20
    
  # CORS
  cors:
    enabled: true
    allowed_origins:
      - "https://app.miservicio.com"
      - "https://admin.miservicio.com"
    allowed_methods:
      - "GET"
      - "POST"
      - "PUT"
      - "DELETE"
    allowed_headers:
      - "Content-Type"
      - "Authorization"
    
  # HTTPS/TLS
  tls:
    enabled: true
    cert_file: "/etc/ssl/certs/mcp.crt"
    key_file: "/etc/ssl/private/mcp.key"
    ca_file: "/etc/ssl/certs/ca.crt"
```

## 🚨 Configuración de Alertas

### Archivo de Reglas de Prometheus

```yaml
# monitoring/rules/alerts.yml
groups:
  - name: mcp_health_alerts
    rules:
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.instance }} is down"
          description: "Service {{ $labels.instance }} has been down for more than 1 minute"
          
      - alert: HighResponseTime
        expr: http_request_duration_seconds{quantile="0.95"} > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time for {{ $labels.instance }}"
          description: "95th percentile response time is above 500ms"
          
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate for {{ $labels.instance }}"
          description: "Error rate is above 10%"
```

## 📝 Configuración de Logging

### Archivo de Configuración de Logging

```yaml
# logging_config.yaml
logging:
  version: 1
  disable_existing_loggers: false
  
  formatters:
    standard:
      format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
      datefmt: "%Y-%m-%d %H:%M:%S"
    
    detailed:
      format: "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
      datefmt: "%Y-%m-%d %H:%M:%S"
    
    json:
      class: pythonjsonlogger.jsonlogger.JsonFormatter
      format: "%(timestamp)s %(level)s %(name)s %(message)s"
  
  handlers:
    console:
      class: logging.StreamHandler
      level: INFO
      formatter: standard
      stream: ext://sys.stdout
    
    file:
      class: logging.handlers.RotatingFileHandler
      level: DEBUG
      formatter: detailed
      filename: "/app/logs/mcp_health.log"
      maxBytes: 10485760  # 10MB
      backupCount: 5
    
    error_file:
      class: logging.handlers.RotatingFileHandler
      level: ERROR
      formatter: detailed
      filename: "/app/logs/mcp_health_errors.log"
      maxBytes: 10485760  # 10MB
      backupCount: 5
    
    json_file:
      class: logging.handlers.RotatingFileHandler
      level: INFO
      formatter: json
      filename: "/app/logs/mcp_health.json"
      maxBytes: 10485760  # 10MB
      backupCount: 5
  
  loggers:
    src:
      level: DEBUG
      handlers: [console, file, json_file]
      propagate: false
    
    src.tools.health:
      level: INFO
      handlers: [console, file]
      propagate: false
    
    src.tools.audit_repo:
      level: INFO
      handlers: [console, file]
      propagate: false
    
    src.tools.terminal_tools:
      level: WARNING
      handlers: [console, file]
      propagate: false
  
  root:
    level: INFO
    handlers: [console, error_file]
```

## 🔄 Configuración de Monitoreo

### Archivo de Configuración de Monitoreo

```yaml
# monitoring_config.yaml
monitoring:
  # Configuración de health checks
  health_checks:
    interval_seconds: 30
    timeout_seconds: 10
    max_retries: 3
    
  # Configuración de métricas
  metrics:
    collection_interval: 15
    retention_days: 30
    
  # Configuración de alertas
  alerts:
    check_interval: 60
    cooldown_period: 300
    escalation_time: 1800
    
  # Configuración de reportes
  reports:
    daily: true
    weekly: true
    monthly: true
    custom_schedules:
      - name: "business_hours"
        cron: "0 9-17 * * 1-5"
        timezone: "America/New_York"
    
  # Configuración de notificaciones
  notifications:
    channels:
      - type: "email"
        enabled: true
        recipients: ["admin@miservicio.com"]
        template: "email_alert.html"
      
      - type: "slack"
        enabled: true
        channel: "#alerts"
        template: "slack_alert.json"
      
      - type: "webhook"
        enabled: true
        url: "https://api.miservicio.com/webhooks/health"
        method: "POST"
        headers:
          Authorization: "Bearer ${WEBHOOK_TOKEN}"
```

## 🎯 Configuración de Entornos

### Entorno de Desarrollo

```yaml
# config/development.yaml
environment: development

endpoints:
  base_url: "http://localhost:8080"
  readiness: "/health/ready"
  liveness: "/health/live"

thresholds:
  http_latency_ms: 1000
  coverage_min: 0.70

logging:
  level: "DEBUG"
  console_output: true

monitoring:
  health_checks:
    interval_seconds: 60
  metrics:
    enabled: false
  alerts:
    enabled: false
```

### Entorno de Staging

```yaml
# config/staging.yaml
environment: staging

endpoints:
  base_url: "https://staging-api.miservicio.com"
  readiness: "/health/ready"
  liveness: "/health/live"

thresholds:
  http_latency_ms: 500
  coverage_min: 0.80

logging:
  level: "INFO"
  file_output: true

monitoring:
  health_checks:
    interval_seconds: 30
  metrics:
    enabled: true
  alerts:
    enabled: true
    channels: ["slack"]
```

### Entorno de Producción

```yaml
# config/production.yaml
environment: production

endpoints:
  base_url: "https://api.miservicio.com"
  readiness: "/health/ready"
  liveness: "/health/live"

thresholds:
  http_latency_ms: 300
  coverage_min: 0.90

logging:
  level: "WARNING"
  file_output: true
  json_format: true

monitoring:
  health_checks:
    interval_seconds: 15
  metrics:
    enabled: true
    prometheus: true
  alerts:
    enabled: true
    channels: ["email", "slack", "webhook"]
    escalation: true
```

## 🔧 Scripts de Configuración

### Script de Configuración Automática

```bash
#!/bin/bash
# setup_mcp.sh

set -e

echo "🚀 Configurando MCP Health Check Service..."

# Verificar dependencias
command -v docker >/dev/null 2>&1 || { echo "❌ Docker no está instalado"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose no está instalado"; exit 1; }

# Crear directorios necesarios
mkdir -p logs data config monitoring/{prometheus,grafana}

# Copiar archivos de configuración
cp src/config/audit.example.yaml config/audit.yaml
cp monitoring/prometheus.example.yml monitoring/prometheus.yml

# Configurar variables de entorno
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env..."
    cat > .env << EOF
# Configuración del MCP
MCP_HOST=0.0.0.0
MCP_PORT=8000
MCP_PROXY_TOKEN=$(openssl rand -hex 32)

# Configuración de base de datos
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Configuración de Grafana
GRAFANA_PASSWORD=admin

# Configuración de logging
LOG_LEVEL=INFO
EOF
    echo "✅ Archivo .env creado"
fi

# Construir y ejecutar servicios
echo "🔨 Construyendo servicios..."
docker-compose up --build -d

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."
sleep 30

# Verificar estado
echo "🔍 Verificando estado de los servicios..."
docker-compose ps

echo "✅ Configuración completada!"
echo "🌐 MCP Service: http://localhost:8000"
echo "📊 Prometheus: http://localhost:9091"
echo "📈 Grafana: http://localhost:3000 (admin/admin)"
```

## 📚 Referencias de Configuración

- **Docker**: https://docs.docker.com/
- **Docker Compose**: https://docs.docker.com/compose/
- **Prometheus**: https://prometheus.io/docs/
- **Grafana**: https://grafana.com/docs/
- **YAML**: https://yaml.org/spec/
- **Environment Variables**: https://12factor.net/config

---

**Con esta configuración avanzada, tu MCP Health Check Service estará listo para entornos de producción con monitoreo completo, métricas, alertas y escalabilidad! 🚀** 