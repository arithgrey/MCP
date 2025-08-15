from mcp.server.fastmcp import FastMCP
from src.config import SERVER_NAME, SERVER_CONFIG
from src.tools import register_tools

def run_server():
    # Crear servidor MCP
    mcp = FastMCP(SERVER_NAME)
    
    # Registrar herramientas
    register_tools(mcp)
    
    # Ejecutar servidor
    print("Iniciando servidor MCP...")
    
    # Configurar host y puerto desde variables de entorno
    import os
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("MCP_PORT", 8000))
    
    print(f"Servidor escuchando en {host}:{port}")
    
    # Usar uvicorn directamente con la aplicación SSE de FastMCP
    import uvicorn
    uvicorn.run(
        mcp.sse_app,
        host=host,
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    run_server()
