"""
Herramientas básicas para el servidor MCP
"""

def register_tools(mcp):
    """Registra todas las herramientas básicas"""
    
    @mcp.tool()
    def say_hello(name: str) -> str:
        """Devuelve un saludo personalizado."""
        return f"¡Hola {name}!"
    
    @mcp.tool()
    def sum_numbers(a: float, b: float) -> float:
        """Suma dos números."""
        return a + b
    
    @mcp.tool()
    def list_items(items: list) -> str:
        """Lista los elementos recibidos."""
        return "\n".join(f"- {item}" for item in items)
