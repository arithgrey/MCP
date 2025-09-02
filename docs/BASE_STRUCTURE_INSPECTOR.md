# Base Structure Inspector Microservice

## Descripción

La herramienta `base_structure_inspector_microservice` es una nueva funcionalidad del MCP que actúa como **arquitecto de software experto** para verificar si cada microservicio cumple con los estándares técnicos mínimos de arquitectura moderna.

## Características Principales

### ✅ Verificación de Estructura Mínima Obligatoria

La herramienta verifica la existencia de los siguientes elementos en el directorio raíz del microservicio:

1. **`Dockerfile`** - Para containerización
2. **`docker-compose.yml`** - Para orquestación
3. **`.gitignore`** - Para exclusión de archivos innecesarios
4. **Directorio `tests/`** - Con al menos un archivo `.py` dentro

### 🔍 Auditoría Básica de Configuración

#### Dockerfile
- ✅ **EXPOSE** configurado correctamente
- ✅ Evita `COPY . .` sin `.dockerignore`
- ✅ No instala dependencias innecesarias (vim, curl, wget, etc.)

#### docker-compose.yml
- ✅ **volumes** definidos adecuadamente
- ✅ **networks** configurados
- ✅ **depends_on** especificado
- ✅ **restart: unless-stopped** o similar

#### .gitignore
- ✅ Incluye `.env`, `__pycache__/`, `*.pyc`
- ✅ Incluye `node_modules/`, `build/`, `dist/`
- ✅ Incluye `.pytest_cache/`, `*.log`

#### Directorio tests/
- ✅ Archivos siguen el patrón `test_*.py` o `*_test.py`
- ✅ Contiene tests relevantes

## Uso de la Herramienta

### A través del MCP

```python
# Inspección de un microservicio específico
result = await base_structure_inspector_microservice(
    service_path="nombre_servicio",
    base_path="ruta_repositorio"
)

# Auditoría completa del repositorio
result = await base_structure_inspector_microservice(
    base_path="ruta_repositorio"
)
```

### Uso Directo en Python

```python
from src.tools.structure_inspector import (
    inspect_microservice_structure,
    inspect_repository_structure
)

# Inspección de microservicio
report = inspect_microservice_structure("service_name", ".")

# Auditoría del repositorio
audit = inspect_repository_structure(".")
```

## Salida Esperada

### Para Microservicio Individual

```json
{
  "service": "nombre_servicio",
  "path": "ruta_relativa",
  "structure_checks": {
    "Dockerfile": true,
    "docker_compose_yml": true,
    "gitignore": true,
    "tests_dir_exists": true,
    "tests_dir_has_files": true
  },
  "config_quality": {
    "dockerfile_best_practices": ["EXPOSE missing", "installs unnecessary tools"],
    "compose_warnings": ["no restart policy", "no volumes defined"],
    "gitignore_warnings": ["missing .env", "missing __pycache__/"],
    "tests_warnings": ["test file example.py doesn't follow naming convention"]
  },
  "status": "incomplete",
  "score": 74.0,
  "recommendations": [
    "Agregar política de reinicio en docker-compose",
    "Mejorar .gitignore"
  ]
}
```

### Para Auditoría del Repositorio

```json
{
  "total_services": 3,
  "complete_services": 1,
  "incomplete_services": 2,
  "poor_services": 0,
  "average_score": 78.5,
  "services": [...],
  "timestamp": "2025-08-21T19:45:00",
  "overall_status": "incomplete"
}
```

## Estados de Calidad

### StructureStatus

- **`COMPLETE`** (score ≥ 80): Estructura completa y bien configurada
- **`INCOMPLETE`** (score 50-79): Estructura básica presente pero con mejoras necesarias
- **`POOR`** (score < 50): Estructura deficiente o faltante

### Cálculo de Score

- **Estructura básica (60%)**: 12 puntos por cada elemento presente
- **Calidad de configuración (40%)**: 40 puntos base, -2 puntos por cada warning

## Casos de Uso

### 1. Verificación de Nuevos Microservicios
```python
# Verificar que un nuevo microservicio cumple con estándares
report = inspect_microservice_structure("new-service", ".")
if report.status == "complete":
    print("✅ Microservicio cumple con estándares")
else:
    print("⚠️  Mejoras necesarias:", report.recommendations)
```

### 2. Auditoría de Repositorio Completo
```python
# Auditoría completa para CI/CD
audit = inspect_repository_structure(".")
if audit.overall_status == "complete":
    print("✅ Todos los microservicios cumplen estándares")
else:
    print(f"⚠️  {audit.incomplete_services} servicios necesitan mejoras")
```

### 3. Integración en Pipelines
```python
# Verificación automática en builds
for service in audit.services:
    if service.score < 70:
        print(f"❌ {service.service} no cumple estándares mínimos")
        exit(1)
```

## Mejores Prácticas Detectadas

### Dockerfile
```dockerfile
# ✅ Bueno
FROM python:3.9-slim
EXPOSE 8000
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .

# ❌ Evitar
FROM ubuntu:latest
RUN apt-get install vim curl wget
COPY . .
```

### docker-compose.yml
```yaml
# ✅ Bueno
version: '3.8'
services:
  app:
    build: .
    restart: unless-stopped
    volumes:
      - ./data:/app/data
    networks:
      - app-network
    depends_on:
      - db

# ❌ Evitar
version: '3.8'
services:
  app:
    build: .
```

### .gitignore
```gitignore
# ✅ Completo
.env
__pycache__/
*.pyc
node_modules/
build/
dist/
.pytest_cache/
*.log

# ❌ Básico
*.log
```

## Tests y Validación

La herramienta incluye una suite completa de tests que valida:

- ✅ Verificación de estructura básica
- ✅ Auditoría de calidad de configuración
- ✅ Cálculo de scores y estados
- ✅ Generación de recomendaciones
- ✅ Detección automática de servicios
- ✅ Manejo de errores y casos edge

### Ejecutar Tests

```bash
# Todos los tests
docker exec mcp-service python -m pytest tests/test_structure_inspector.py -v

# Tests específicos
docker exec mcp-service python -m pytest tests/test_structure_inspector.py::TestBaseStructureInspector -v
```

## Arquitectura Técnica

### Clases Principales

- **`BaseStructureInspector`**: Clase principal para inspección
- **`StructureChecks`**: Modelo para verificaciones de estructura
- **`ConfigQuality`**: Modelo para calidad de configuración
- **`MicroserviceStructureReport`**: Reporte individual de microservicio
- **`RepositoryStructureAudit`**: Auditoría completa del repositorio

### Patrones de Validación

La herramienta utiliza expresiones regulares y patrones predefinidos para:

- Detectar configuraciones problemáticas en Dockerfile
- Identificar warnings en docker-compose.yml
- Validar contenido de .gitignore
- Verificar convenciones de nombres de tests

## Contribución y Extensión

### Agregar Nuevos Patrones de Validación

```python
# En BaseStructureInspector.__init__()
self.dockerfile_patterns["new_pattern"] = r"patron_regex"
self.compose_patterns["new_check"] = r"nuevo_patron"
```

### Personalizar Umbrales de Score

```python
# Modificar _determine_status()
if score >= 90:  # Cambiar de 80 a 90
    return StructureStatus.COMPLETE
```

## Conclusión

La herramienta `base_structure_inspector_microservice` proporciona una auditoría completa y automatizada de la estructura de microservicios, asegurando que cumplan con los estándares técnicos mínimos de arquitectura moderna. Su integración en el MCP permite su uso tanto programáticamente como a través de la interfaz del modelo de lenguaje. 