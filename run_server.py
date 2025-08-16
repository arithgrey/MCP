import sys
from mcp.server.fastmcp import FastMCP
from src.config import SERVER_NAME, SERVER_CONFIG
from src.tools import register_tools

def run_server():
    # Crear servidor MCP
    mcp = FastMCP(SERVER_NAME)
    
    # Registrar herramientas
    register_tools(mcp)
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1 and sys.argv[1] == "--sse":
        # Modo SSE para testing con MCP Inspector
        print("Iniciando servidor MCP en modo SSE para testing...")
        
        # Configurar host y puerto desde variables de entorno
        import os
        host = os.getenv("MCP_HOST", "127.0.0.1")
        port = int(os.getenv("MCP_PORT", 8000))
        
        print(f"Servidor SSE escuchando en {host}:{port}")
        print("Usa MCP Inspector para probar: http://localhost:8000")
        
        # Usar uvicorn con la aplicación SSE de FastMCP
        import uvicorn
        uvicorn.run(
            mcp.sse_app,
            host=host,
            port=port,
            log_level="info"
        )
    else:
        # Modo stdio estándar para MCP (recomendado para Cursor)
        print("Iniciando servidor MCP con transporte stdio estándar...")
        print("Este modo es ideal para integración con Cursor y otros clientes MCP")
        
        # Usar el método estándar de MCP
        mcp.run()

if __name__ == "__main__":
    run_server()
