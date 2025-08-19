# MCP Health Check Service

Un servidor MCP (Model Context Protocol) completo para validar la salud de servicios web con capacidades de terminal integradas.

## 🚀 Características

- **Health Checks Automatizados**: Verificación de endpoints de readiness y liveness
- **Configuración YAML**: Configuración flexible de servicios y umbrales
- **Herramientas de Terminal**: Ejecución de comandos y monitoreo del sistema
- **Auditorías en Lote**: Verificación de múltiples servicios simultáneamente
- **Reportes Detallados**: Generación de reportes legibles con métricas
- **Integración MCP**: Compatible con Cursor y otros clientes MCP

## 🏗️ Arquitectura

```
src/
├── config/           # Configuración y esquemas
├── core/            # Modelos de datos
├── tools/           # Herramientas MCP
│   ├── health.py           # Health checks HTTP
│   ├── audit_repo.py       # Orquestador de auditorías
│   ├── terminal_tools.py   # Herramientas de terminal
│   └── basic_tools.py      # Registro de herramientas
└── tests/           # Tests unitarios
```

## 🛠️ Instalación

1. **Clonar el repositorio**:
```bash
git clone <repo-url>
cd MCP
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Configurar el archivo de auditoría**:
```bash
cp src/config/audit.example.yaml src/config/audit.yaml
# Editar src/config/audit.yaml según tus necesidades
```

## 📋 Configuración

### Archivo `audit.yaml`

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
```

## 🚀 Uso

### 1. Iniciar el servidor MCP

```bash
# Modo stdio (recomendado para Cursor)
python mcp_server.py

# Modo SSE para testing
python mcp_server.py --sse
```

### 2. Herramientas Disponibles

#### Health Checks Individuales

- `health_readiness_check`: Verifica readiness de un servicio
- `health_liveness_check`: Verifica liveness de un servicio
- `health_comprehensive_check`: Check completo (readiness + liveness)

#### Auditorías

- `audit_repo_run`: Ejecuta auditoría usando configuración YAML
- `terminal_run_health_audit`: Auditoría con reporte formateado
- `terminal_batch_health_check`: Health checks en lote

#### Herramientas de Terminal

- `terminal_execute_command`: Ejecuta comandos de terminal
- `terminal_get_system_info`: Información del sistema
- `terminal_health_check_service`: Health check con formato de terminal

### 3. Ejemplos de Uso

#### Health Check Básico
```python
# Verificar readiness
result = await health_readiness_check(
    base_url="http://localhost:8080",
    path="/readiness",
    max_latency_ms=300
)

# Verificar liveness
result = await health_liveness_check(
    base_url="http://localhost:8080",
    path="/liveness",
    max_latency_ms=300
)
```

#### Auditoría Completa
```python
# Ejecutar auditoría con configuración por defecto
audit_result = await audit_repo_run()

# Ejecutar auditoría con archivo personalizado
audit_result = await audit_repo_run("custom_audit.yaml")
```

#### Comandos de Terminal
```python
# Ejecutar comando
result = await terminal_execute_command("ls -la")

# Obtener información del sistema
sys_info = await terminal_get_system_info()
```

## 🧪 Testing

Ejecutar las pruebas:

```bash
python test_mcp.py
```

## 📊 Monitoreo

El MCP proporciona métricas detalladas:

- **Estado del servicio**: HEALTHY, UNHEALTHY, DEGRADED, UNKNOWN
- **Latencia**: Tiempo de respuesta en milisegundos
- **Códigos de respuesta**: HTTP status codes
- **Errores**: Mensajes de error detallados
- **Reportes**: Resúmenes consolidados con porcentajes de salud

## 🔧 Desarrollo

### Estructura del Proyecto

- **`mcp_server.py`**: Punto de entrada principal
- **`src/tools/health.py`**: Lógica de health checks HTTP
- **`src/tools/audit_repo.py`**: Orquestador de auditorías
- **`src/tools/terminal_tools.py`**: Herramientas de terminal
- **`src/core/models.py`**: Modelos de datos Pydantic

### Agregar Nuevas Herramientas

1. Crear función en el módulo apropiado
2. Registrar en `src/tools/basic_tools.py`
3. Agregar documentación y tipos

### Testing

```bash
# Ejecutar tests unitarios
python -m pytest tests/

# Ejecutar script de prueba
python test_mcp.py
```

## 🌐 Integración con Cursor

1. **Configurar Cursor** para usar el MCP
2. **Importar herramientas** en tu workspace
3. **Usar comandos** directamente desde el chat

## 📝 Licencia

MIT License

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📞 Soporte

Para soporte o preguntas:

- Abre un issue en GitHub
- Revisa la documentación
- Consulta los ejemplos de uso 