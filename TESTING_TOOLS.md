# Herramientas de Testing del MCP

## Descripción General

El MCP ahora incluye herramientas especializadas para ejecutar tests en contenedores Docker usando el formato `docker exec nombre_servicio pytest`. Estas herramientas están integradas en el orquestador y permiten realizar auditorías completas que incluyen tanto health checks como ejecución de tests.

## Características Principales

- ✅ **Ejecución con Docker Exec**: Todos los tests se ejecutan usando `docker exec nombre_servicio pytest`
- ✅ **Integración con Orquestador**: Las herramientas están integradas en el `AuditOrchestrator`
- ✅ **Múltiples Formatos de Test**: Soporte para pytest, coverage, reportes HTML/XML
- ✅ **Configuración Flexible**: Archivo YAML para configurar servicios y parámetros
- ✅ **Health Checks Integrados**: Verificación de salud antes de ejecutar tests

## Herramientas Disponibles

### 1. Herramientas Directas de Testing

#### `docker_test_execute`
Ejecuta tests básicos en un contenedor Docker.

```python
# Ejemplo de uso
result = await docker_test_execute(
    service_name="mcp-service",
    test_command="pytest",
    additional_args="-v"
)
```

#### `docker_test_pytest_coverage`
Ejecuta pytest con coverage.

```python
# Ejemplo de uso
result = await docker_test_pytest_coverage(
    service_name="mcp-service",
    coverage_args="--cov=src --cov-report=html"
)
```

#### `docker_test_specific_file`
Ejecuta un archivo de test específico.

```python
# Ejemplo de uso
result = await docker_test_specific_file(
    service_name="mcp-service",
    test_file="tests/test_health.py",
    additional_args="-v"
)
```

#### `docker_test_with_markers`
Ejecuta tests con marcadores específicos.

```python
# Ejemplo de uso
result = await docker_test_with_markers(
    service_name="mcp-service",
    marker="unit",
    additional_args="-v"
)
```

#### `docker_test_parallel`
Ejecuta tests en paralelo.

```python
# Ejemplo de uso
result = await docker_test_parallel(
    service_name="mcp-service",
    num_workers=4,
    additional_args="-v"
)
```

#### `docker_test_verbose`
Ejecuta tests con salida verbose.

```python
# Ejemplo de uso
result = await docker_test_verbose(
    service_name="mcp-service",
    test_command="pytest",
    additional_args="--tb=short"
)
```

#### `docker_test_html_report`
Genera reportes HTML de los tests.

```python
# Ejemplo de uso
result = await docker_test_html_report(
    service_name="mcp-service",
    report_dir="test_reports",
    additional_args="-v"
)
```

#### `docker_test_junit_report`
Genera reportes JUnit XML.

```python
# Ejemplo de uso
result = await docker_test_junit_report(
    service_name="mcp-service",
    report_file="junit.xml",
    additional_args="-v"
)
```

#### `docker_test_custom_command`
Ejecuta comandos de testing personalizados.

```python
# Ejemplo de uso
result = await docker_test_custom_command(
    service_name="mcp-service",
    test_command="python -m pytest",
    additional_args="--collect-only"
)
```

### 2. Herramientas del Orquestador

#### `audit_orchestrator_test_suite`
Ejecuta la suite de tests usando el orquestador.

```python
# Ejemplo de uso
result = await audit_orchestrator_test_suite(
    service_name="mcp-service",
    test_type="pytest",
    additional_args="-v --tb=short"
)
```

#### `audit_orchestrator_tests_with_coverage`
Ejecuta tests con coverage usando el orquestador.

```python
# Ejemplo de uso
result = await audit_orchestrator_tests_with_coverage(
    service_name="mcp-service",
    coverage_args="--cov=src --cov-report=html --cov-report=term-missing"
)
```

#### `audit_orchestrator_comprehensive_audit`
Ejecuta una auditoría completa (health checks + tests).

```python
# Ejemplo de uso
result = await audit_orchestrator_comprehensive_audit(
    service_name="mcp-service",
    include_tests=True
)
```

## Configuración

### Archivo de Configuración: `src/config/testing.yaml`

```yaml
# Configuración de Docker
docker:
  default_service: "mcp-service"
  network: "mcp-network"
  timeout_seconds: 300

# Configuración de pytest
pytest:
  default_command: "pytest"
  coverage_args: "--cov=src --cov-report=html --cov-report=term-missing"
  verbose_output: true
  parallel_workers: 4

# Configuración de servicios
services:
  mcp_service:
    name: "mcp-service"
    container_name: "mcp-service"
    test_path: "/app/tests"
    pytest_config: "pytest.ini"
```

## Ejemplos de Uso Práctico

### 1. Ejecutar Tests Básicos

```bash
# Usando el MCP desde Cursor
docker_test_execute(
    service_name="mcp-service",
    test_command="pytest",
    additional_args="-v"
)
```

### 2. Ejecutar Tests con Coverage

```bash
# Generar reporte de coverage
docker_test_pytest_coverage(
    service_name="mcp-service",
    coverage_args="--cov=src --cov-report=html --cov-report=term-missing"
)
```

### 3. Ejecutar Tests Específicos

```bash
# Solo tests de health
docker_test_specific_file(
    service_name="mcp-service",
    test_file="tests/test_health.py",
    additional_args="-v"
)

# Solo tests unitarios
docker_test_with_markers(
    service_name="mcp-service",
    marker="unit",
    additional_args="-v"
)
```

### 4. Auditoría Completa

```bash
# Health checks + tests
audit_orchestrator_comprehensive_audit(
    service_name="mcp-service",
    include_tests=True
)
```

## Estructura de Respuesta

Todas las herramientas devuelven un diccionario con la siguiente estructura:

```json
{
    "success": true,
    "status": "passed",
    "service_name": "mcp-service",
    "command": "docker exec mcp-service pytest -v",
    "return_code": 0,
    "stdout": "test output...",
    "stderr": "test errors...",
    "timestamp": "2024-01-01T12:00:00",
    "execution_time_ms": 0
}
```

## Integración con el Orquestador

El `AuditOrchestrator` ahora incluye métodos para:

- `run_test_suite()`: Ejecuta tests usando docker exec
- `run_tests_with_coverage()`: Ejecuta tests con coverage
- `run_comprehensive_audit()`: Auditoría completa con health checks y tests
- `_generate_recommendations()`: Genera recomendaciones basadas en resultados

## Mejores Prácticas

1. **Siempre usar docker exec**: Los tests deben ejecutarse dentro del contenedor
2. **Verificar salud primero**: Usar health checks antes de ejecutar tests
3. **Configurar timeouts**: Establecer timeouts apropiados para tests largos
4. **Generar reportes**: Usar reportes HTML/XML para análisis posterior
5. **Ejecutar en paralelo**: Usar pytest-xdist para tests que lo soporten

## Troubleshooting

### Problemas Comunes

1. **Contenedor no encontrado**: Verificar que el nombre del servicio sea correcto
2. **Tests fallan**: Revisar que pytest esté instalado en el contenedor
3. **Timeout**: Ajustar el timeout en la configuración
4. **Permisos**: Verificar permisos de Docker

### Comandos de Diagnóstico

```bash
# Verificar contenedores activos
docker ps

# Ver logs del contenedor
docker logs mcp-service

# Ejecutar comando manual
docker exec mcp-service pytest --version
```

## Próximas Mejoras

- [ ] Medición de tiempo de ejecución
- [ ] Integración con sistemas de CI/CD
- [ ] Notificaciones por email/Slack
- [ ] Dashboard web para resultados
- [ ] Historial de ejecuciones
- [ ] Comparación de resultados entre ejecuciones 