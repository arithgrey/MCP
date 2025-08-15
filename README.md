# Servicio MCP Dockerizado

Servidor MCP (Model Context Protocol) que se ejecuta con Docker Compose.

## 🚀 Inicio Rápido

### Construir y ejecutar
```bash
./docker-build.sh
```

### Comandos manuales
```bash
# Construir imagen
docker-compose build

# Ejecutar servicio
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicio
docker-compose down
```

## 🔧 Configuración

- **Puerto**: 8000
- **Transporte**: SSE (Server-Sent Events)
- **Token MCP**: test123

## 📊 Estado del Servicio

```bash
# Ver estado
docker-compose ps

# Ver logs
docker-compose logs -f
```

## 🔍 Inspección MCP

Una vez ejecutándose:
```bash
mcp-inspector http://127.0.0.1:8000/sse
```

## 🐛 Solución de Problemas

```bash
# Reconstruir imagen
docker-compose build --no-cache

# Limpiar recursos
docker-compose down --volumes
``` 