# 📚 Manual de Uso - MCP Health Check Service

## 🎯 Descripción General

Este MCP (Model Context Protocol) proporciona herramientas avanzadas para monitorear la salud de servicios web, ejecutar comandos de terminal y realizar auditorías automatizadas. Está diseñado para integrarse perfectamente con Cursor y otros clientes MCP.

## 🚀 Instalación y Configuración

### Requisitos Previos
- Cursor con soporte MCP habilitado
- Docker y Docker Compose instalados
- Acceso a servicios web para monitorear

### Configuración Inicial
1. **Clonar el repositorio:**
   ```bash
   git clone <repo-url>
   cd MCP
   ```

2. **Construir y ejecutar el contenedor:**
   ```bash
   docker-compose up --build -d
   ```

3. **Verificar que esté funcionando:**
   ```bash
   docker ps
   # Deberías ver el contenedor mcp-service ejecutándose
   ```

## 🛠️ Herramientas Disponibles

### 🔍 Health Checks Individuales

#### 1. `health_readiness_check`
**Descripción:** Verifica si un servicio está listo para recibir tráfico.

**Parámetros:**
- `base_url` (string, requerido): URL base del servicio (ej: "http://localhost:8080")
- `path` (string, opcional): Ruta del endpoint de readiness (default: "/readiness")
- `max_latency_ms` (integer, opcional): Latencia máxima permitida en ms (default: 300)

**Ejemplo de uso:**
```python
# Verificar readiness de un servicio local
result = await health_readiness_check(
    base_url="http://localhost:8080",
    path="/ready",
    max_latency_ms=500
)

# Verificar readiness con configuración por defecto
result = await health_readiness_check("https://api.miservicio.com")
```

**Respuesta:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "latency_ms": 150.5,
  "response_code": 200,
  "error_message": null,
  "details": {
    "url": "http://localhost:8080/ready",
    "method": "GET",
    "headers": {...}
  }
}
```

#### 2. `health_liveness_check`
**Descripción:** Verifica si un servicio está vivo y funcionando.

**Parámetros:**
- `base_url` (string, requerido): URL base del servicio
- `path` (string, opcional): Ruta del endpoint de liveness (default: "/liveness")
- `max_latency_ms` (integer, opcional): Latencia máxima permitida en ms (default: 300)

**Ejemplo de uso:**
```python
# Verificar liveness de un servicio
result = await health_liveness_check(
    base_url="https://api.miservicio.com",
    path="/health/live",
    max_latency_ms=200
)
```

#### 3. `health_comprehensive_check`
**Descripción:** Realiza un check completo de health (readiness + liveness).

**Parámetros:**
- `base_url` (string, requerido): URL base del servicio
- `readiness_path` (string, opcional): Ruta del endpoint de readiness (default: "/readiness")
- `liveness_path` (string, opcional): Ruta del endpoint de liveness (default: "/liveness")
- `max_latency_ms` (integer, opcional): Latencia máxima permitida en ms (default: 300)

**Ejemplo de uso:**
```python
# Health check completo
result = await health_comprehensive_check(
    base_url="https://api.miservicio.com",
    readiness_path="/health/ready",
    liveness_path="/health/live",
    max_latency_ms=300
)

print(f"Estado general: {result['overall_status']}")
print(f"Readiness: {result['readiness']['status']}")
print(f"Liveness: {result['liveness']['status']}")
```

### 📊 Auditorías y Reportes

#### 4. `audit_repo_run`
**Descripción:** Ejecuta una auditoría completa usando la configuración del archivo YAML.

**Parámetros:**
- `config_path` (string, opcional): Ruta al archivo de configuración (default: usa audit.yaml)

**Ejemplo de uso:**
```python
# Auditoría con configuración por defecto
audit_result = await audit_repo_run()

# Auditoría con archivo personalizado
audit_result = await audit_repo_run("custom_audit.yaml")

print(f"Total de servicios: {audit_result['total_services']}")
print(f"Servicios saludables: {audit_result['healthy_services']}")
print(f"Porcentaje de salud: {audit_result['health_percentage']:.1f}%")
```

**Respuesta:**
```json
{
  "total_services": 3,
  "healthy_services": 2,
  "unhealthy_services": 1,
  "failed_checks": 0,
  "health_percentage": 66.7,
  "timestamp": "2024-01-01T12:00:00",
  "results": [...],
  "errors": []
}
```

### 💻 Herramientas de Terminal

#### 5. `terminal_execute_command`
**Descripción:** Ejecuta comandos de terminal de forma asíncrona.

**Parámetros:**
- `command` (string, requerido): Comando a ejecutar
- `cwd` (string, opcional): Directorio de trabajo

**Ejemplo de uso:**
```python
# Ejecutar comando básico
result = await terminal_execute_command("ls -la")

# Ejecutar comando en directorio específico
result = await terminal_execute_command("pwd", "/tmp")

# Verificar resultado
if result["success"]:
    print(f"Comando exitoso: {result['stdout']}")
else:
    print(f"Error: {result['error']}")
```

**Respuesta:**
```json
{
  "success": true,
  "return_code": 0,
  "stdout": "total 8\ndrwxr-xr-x 2 root root 4096 Jan 1 12:00 .",
  "stderr": "",
  "command": "ls -la",
  "cwd": "/tmp"
}
```

#### 6. `terminal_health_check_service`
**Descripción:** Realiza un health check a un servicio desde terminal con formato mejorado.

**Parámetros:**
- `base_url` (string, requerido): URL base del servicio
- `readiness_path` (string, opcional): Ruta del endpoint de readiness (default: "/readiness")
- `liveness_path` (string, opcional): Ruta del endpoint de liveness (default: "/liveness")
- `max_latency_ms` (integer, opcional): Latencia máxima permitida en ms (default: 300)

**Ejemplo de uso:**
```python
# Health check desde terminal
result = await terminal_health_check_service(
    base_url="https://api.miservicio.com",
    readiness_path="/health/ready",
    liveness_path="/health/live",
    max_latency_ms=300
)

if result["success"]:
    print(f"Servicio: {result['service_url']}")
    print(f"Estado: {result['overall_status']}")
    print(f"Readiness: {result['readiness']['status']}")
    print(f"Liveness: {result['liveness']['status']}")
```

#### 7. `terminal_run_health_audit`
**Descripción:** Ejecuta una auditoría completa con reporte formateado para terminal.

**Parámetros:**
- `config_path` (string, opcional): Ruta al archivo de configuración

**Ejemplo de uso:**
```python
# Ejecutar auditoría con reporte
result = await terminal_run_health_audit()

if result["success"]:
    # Mostrar reporte completo
    print(result["report"])
    
    # Acceder a datos estructurados
    data = result["results"]
    print(f"Resumen: {data['healthy_services']}/{data['total_services']} servicios saludables")
```

#### 8. `terminal_batch_health_check`
**Descripción:** Ejecuta health checks para múltiples servicios en lote.

**Parámetros:**
- `services` (array, requerido): Lista de servicios con formato [{"name": "nombre", "url": "url"}]

**Ejemplo de uso:**
```python
# Lista de servicios a verificar
services = [
    {"name": "API Principal", "url": "https://api.miservicio.com"},
    {"name": "API Secundaria", "url": "https://api2.miservicio.com"},
    {"name": "Frontend", "url": "https://app.miservicio.com"}
]

# Ejecutar checks en lote
result = await terminal_batch_health_check(services)

if result["success"]:
    print(result["report"])
    print(f"Total: {result['results']['total_services']} servicios")
    print(f"Saludables: {result['results']['healthy_services']}")
```

#### 9. `terminal_get_system_info`
**Descripción:** Obtiene información básica del sistema (OS, memoria, disco, procesos).

**Parámetros:** Ninguno

**Ejemplo de uso:**
```python
# Obtener información del sistema
system_info = await terminal_get_system_info()

if system_info["success"]:
    info = system_info["system_info"]
    print(f"OS: {info['os']['stdout']}")
    print(f"Memoria: {info['memory']['stdout']}")
    print(f"Disco: {info['disk']['stdout']}")
    print(f"Procesos: {info['processes']['stdout']}")
```

## 📋 Casos de Uso Comunes

### 🔍 Monitoreo Diario de Servicios
```python
# Verificar estado de servicios críticos
services = [
    {"name": "API Principal", "url": "https://api.miservicio.com"},
    {"name": "Base de Datos", "url": "https://db.miservicio.com"},
    {"name": "Cache", "url": "https://cache.miservicio.com"}
]

# Ejecutar auditoría
result = await terminal_batch_health_check(services)

# Generar reporte
if result["success"]:
    print("📊 REPORTE DIARIO DE SALUD")
    print("=" * 40)
    print(result["report"])
    
    # Alertar si hay problemas
    if result["results"]["health_percentage"] < 80:
        print("⚠️  ALERTA: Servicios con problemas de salud")
```

### 🚨 Monitoreo en Tiempo Real
```python
import asyncio
import time

async def monitor_service(url, service_name):
    """Monitorea un servicio en tiempo real"""
    while True:
        try:
            result = await health_comprehensive_check(url)
            
            if result["overall_status"] == "healthy":
                print(f"✅ {service_name}: Saludable")
            else:
                print(f"❌ {service_name}: Problemas detectados")
                print(f"   Readiness: {result['readiness']['status']}")
                print(f"   Liveness: {result['liveness']['status']}")
            
            # Esperar 30 segundos antes del siguiente check
            await asyncio.sleep(30)
            
        except Exception as e:
            print(f"❌ Error monitoreando {service_name}: {e}")
            await asyncio.sleep(60)

# Ejecutar monitoreo
asyncio.create_task(monitor_service("https://api.miservicio.com", "API Principal"))
```

### 📊 Auditoría de Infraestructura
```python
# Configurar auditoría completa
async def infrastructure_audit():
    """Auditoría completa de infraestructura"""
    
    # 1. Verificar servicios web
    web_services = [
        {"name": "Frontend", "url": "https://app.miservicio.com"},
        {"name": "API", "url": "https://api.miservicio.com"},
        {"name": "Admin", "url": "https://admin.miservicio.com"}
    ]
    
    web_health = await terminal_batch_health_check(web_services)
    
    # 2. Verificar información del sistema
    system_info = await terminal_get_system_info()
    
    # 3. Generar reporte consolidado
    print("🏗️  AUDITORÍA DE INFRAESTRUCTURA")
    print("=" * 50)
    
    if web_health["success"]:
        print("🌐 SERVICIOS WEB:")
        print(web_health["report"])
    
    if system_info["success"]:
        print("\n💻 SISTEMA:")
        print(f"OS: {system_info['system_info']['os']['stdout']}")
        print(f"Memoria: {system_info['system_info']['memory']['stdout']}")
        print(f"Disco: {system_info['system_info']['disk']['stdout']}")

# Ejecutar auditoría
await infrastructure_audit()
```

## ⚙️ Configuración Avanzada

### Archivo de Configuración YAML
El archivo `src/config/audit.yaml` permite configurar:

```yaml
endpoints:
  base_url: "http://localhost:8080"
  readiness: "/readiness"
  liveness: "/liveness"

thresholds:
  http_latency_ms: 300
  coverage_min: 0.80

services:
  local_service:
    name: "Servicio Local"
    base_url: "http://localhost:8080"
    readiness: "/readiness"
    liveness: "/liveness"

alerts:
  enabled: true
  max_consecutive_failures: 3
  notification_channels: ["log", "console"]
```

### Variables de Entorno
```bash
# Configurar el MCP
export MCP_HOST=0.0.0.0
export MCP_PORT=8000
export MCP_PROXY_TOKEN=tu_token_aqui
export PYTHONPATH=/app
```

## 🧪 Testing y Debugging

### Ejecutar Tests
```bash
# Todos los tests
docker exec mcp-service pytest tests/ -v

# Tests específicos
docker exec mcp-service pytest tests/test_health.py -v

# Tests con coverage
docker exec mcp-service pytest tests/ --cov=src --cov-report=term-missing
```

### Debugging
```python
# Habilitar logging detallado
import logging
logging.basicConfig(level=logging.DEBUG)

# Verificar estado de herramientas
from src.tools import register_tools
print("✅ Herramientas registradas correctamente")

# Probar health check básico
from src.tools.health import http_check
import asyncio

async def test_health():
    result = await http_check("http://httpbin.org", "/status/200", 5000)
    print(f"Resultado: {result.status}")

asyncio.run(test_health())
```

## 🚨 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'core'"
**Solución:** Verificar que las importaciones usen `src.core.models` en lugar de `core.models`.

### Error: "Connection timeout"
**Solución:** Aumentar el valor de `max_latency_ms` o verificar conectividad de red.

### Error: "Container not running"
**Solución:** Ejecutar `docker-compose up --build -d` para reconstruir y ejecutar el contenedor.

### Error: "Permission denied" en comandos de terminal
**Solución:** Verificar que el contenedor tenga permisos para ejecutar los comandos solicitados.

## 📚 Referencias Adicionales

- **Documentación MCP**: https://modelcontextprotocol.io/
- **Cursor MCP**: https://cursor.sh/docs/mcp
- **Pytest**: https://docs.pytest.org/
- **Docker**: https://docs.docker.com/

## 🤝 Soporte

Para problemas o preguntas:
1. Revisar los logs del contenedor: `docker logs mcp-service`
2. Verificar que todas las dependencias estén instaladas
3. Ejecutar tests para verificar funcionalidad
4. Revisar la configuración YAML

---

**¡Tu MCP está listo para usar! 🚀**

Con estas herramientas puedes monitorear la salud de tus servicios, ejecutar comandos de terminal y generar reportes detallados, todo desde la comodidad de Cursor. 