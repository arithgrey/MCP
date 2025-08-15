"""
Script principal del servidor MCP
"""
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
    mcp.run(**SERVER_CONFIG)

if __name__ == "__main__":
    run_server()
