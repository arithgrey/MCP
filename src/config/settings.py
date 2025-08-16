"""
Configuración del servidor MCP
"""
from pathlib import Path

# Configuración básica
SERVER_NAME = "hola-mundo-mcp"
BASE_DIR = Path(__file__).parent.parent.parent

# Configuración del servidor
SERVER_CONFIG = {
    "transport": "stdio",  # Transporte estándar para MCP
    "port": 8000  # Puerto para modo SSE (testing)
}

# Token de proxy para el inspector
import os
os.environ["MCP_PROXY_TOKEN"] = "test123"

# Configuración del watchdog
WATCH_CONFIG = {
    "recursive": True
}
