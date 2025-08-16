"""
Herramientas básicas para el servidor MCP
"""

from .tdd_policy_check import tdd_policy_check

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
    
    @mcp.tool()
    def tdd_policy_check(
        container_name: str,
        repo_root: str = ".",
        since_ref: str = "HEAD~1",
        action: str = "full_check"
    ) -> dict:
        """
        Verifica política TDD y ejecuta tests según la acción especificada.
        
        Args:
            container_name: Nombre del contenedor Docker donde correr pytest
            repo_root: Ruta raíz del repo (default: ".")
            since_ref: Referencia git para analizar cambios (default: "HEAD~1")
            action: Acción a ejecutar - "scan", "run", o "full_check" (default: "full_check")
        
        Returns:
            Dict con resultado estructurado de la verificación
        """
        return tdd_policy_check(container_name, repo_root, since_ref, action)
