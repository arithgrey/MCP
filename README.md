# Servidor MCP con Herramienta de Verificación TDD

Este proyecto implementa un servidor MCP (Model Context Protocol) que incluye una herramienta especializada para verificar el cumplimiento de la política de desarrollo TDD (Test-Driven Development).

## 🚀 Características

### Herramientas Básicas
- `say_hello`: Saludo personalizado
- `sum_numbers`: Suma de dos números
- `list_items`: Lista elementos recibidos

### 🧪 Herramienta TDD (`tdd_policy_check`)
Verifica automáticamente que todo desarrollo siga TDD:

- **`scan`**: Analiza el repo y valida política TDD
- **`run`**: Ejecuta tests con `docker exec <container_name> pytest`
- **`full_check`**: Ejecuta scan y, si pasa, ejecuta tests

## 📋 Política TDD Implementada

1. **TDD siempre**: Por cada módulo nuevo o modificado debe existir al menos un test correspondiente
2. **Ubicación de tests**: Todos los archivos de test deben estar únicamente en `./tests/`
3. **Ejecución de tests**: Usa exactamente `docker exec <container_name> pytest`
4. **Fallo explícito**: Si hay violaciones, `status = "failed"` con detalle

## 🛠️ Instalación y Uso

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
```bash
cp env.example .env
# Editar .env con tus valores
```

### 3. Ejecutar con Docker
```bash
docker-compose up --build
```

### 4. Ejecutar localmente
```bash
python3 run_server.py
```

## 📊 Uso de la Herramienta TDD

### Ejemplo de uso básico
```json
{
  "tool": "tdd_policy_check",
  "input": {
    "action": "full_check",
    "container_name": "mcp-service",
    "since_ref": "HEAD~1"
  }
}
```

### Parámetros disponibles
- `container_name` (requerido): Nombre del contenedor Docker
- `repo_root` (opcional): Ruta raíz del repo (default: ".")
- `since_ref` (opcional): Referencia git para cambios (default: "HEAD~1")
- `action` (opcional): "scan", "run", o "full_check" (default: "full_check")

### Respuesta de ejemplo
```json
{
  "status": "passed",
  "summary": "✅ Política TDD cumplida. 3 tests encontrados en ./tests/",
  "violations": [],
  "metrics": {
    "tests_found": 3,
    "tests_outside_tests_dir": 0,
    "changed_modules": 2,
    "modules_with_tests": 2,
    "duration_seconds": 0
  },
  "cmd_executed": null,
  "stdout": null,
  "stderr": null
}
```

## 🔍 Códigos de Violación

- `TESTS_OUTSIDE_DIR`: Tests encontrados fuera de `./tests/`
- `NO_TESTS_FOUND`: No se encontró la carpeta `./tests/`
- `PYTEST_NOT_FOUND`: pytest no disponible
- `DOCKER_EXEC_FAILED`: Error ejecutando tests en Docker
- `TDD_HEURISTIC_FAILED`: Módulos modificados sin tests correspondientes

## 🧪 Testing

Ejecutar tests localmente:
```bash
python3 -m pytest tests/
```

Ejecutar tests en Docker:
```bash
docker exec mcp-service pytest
```

## 📁 Estructura del Proyecto

```
MCP/
├── src/
│   ├── tools/
│   │   ├── basic_tools.py      # Herramientas básicas
│   │   └── tdd_policy_check.py # Herramienta TDD
│   └── config/
│       └── settings.py         # Configuración
├── tests/                      # Tests del proyecto
├── docker-compose.yml          # Configuración Docker
├── run_server.py               # Servidor principal
└── requirements.txt            # Dependencias
```

## 🌐 Modos de Ejecución

### Modo stdio (recomendado para Cursor)
```bash
python3 run_server.py
```

### Modo SSE (para testing con MCP Inspector)
```bash
python3 run_server.py --sse
```

## 🔧 Desarrollo

### Agregar nueva herramienta
1. Crear archivo en `src/tools/`
2. Importar en `src/tools/__init__.py`
3. Registrar en `src/tools/basic_tools.py`

### Estructura de herramienta MCP
```python
@mcp.tool()
def mi_herramienta(param1: str, param2: int) -> dict:
    """Descripción de la herramienta"""
    # Lógica de la herramienta
    return {"result": "valor"}
```

## 📝 Licencia

Este proyecto está bajo licencia MIT. 