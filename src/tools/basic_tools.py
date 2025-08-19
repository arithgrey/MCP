"""
Herramientas básicas para el servidor MCP
"""
from .health import readiness_check, liveness_check, comprehensive_health_check
from .audit_repo import run_audit
from .terminal_tools import TerminalTools

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
    async def health_readiness_check(base_url: str, path: str = "/readiness", max_latency_ms: int = 300) -> dict:
        """
        Verifica si un servicio está listo para recibir tráfico.
        
        Args:
            base_url: URL base del servicio (ej: "http://localhost:8080")
            path: Ruta del endpoint de readiness (default: "/readiness")
            max_latency_ms: Latencia máxima permitida en milisegundos (default: 300)
        
        Returns:
            Resultado del check de readiness
        """
        result = await readiness_check(base_url, path, max_latency_ms)
        return result.dict()
    
    @mcp.tool()
    async def health_liveness_check(base_url: str, path: str = "/liveness", max_latency_ms: int = 300) -> dict:
        """
        Verifica si un servicio está vivo y funcionando.
        
        Args:
            base_url: URL base del servicio (ej: "http://localhost:8080")
            path: Ruta del endpoint de liveness (default: "/liveness")
            max_latency_ms: Latencia máxima permitida en milisegundos (default: 300)
        
        Returns:
            Resultado del check de liveness
        """
        result = await liveness_check(base_url, path, max_latency_ms)
        return result.dict()
    
    @mcp.tool()
    async def health_comprehensive_check(
        base_url: str, 
        readiness_path: str = "/readiness", 
        liveness_path: str = "/liveness", 
        max_latency_ms: int = 300
    ) -> dict:
        """
        Realiza un check completo de health de un servicio (readiness + liveness).
        
        Args:
            base_url: URL base del servicio (ej: "http://localhost:8080")
            readiness_path: Ruta del endpoint de readiness (default: "/readiness")
            liveness_path: Ruta del endpoint de liveness (default: "/liveness")
            max_latency_ms: Latencia máxima permitida en milisegundos (default: 300)
        
        Returns:
            Resultado completo del health check
        """
        result = await comprehensive_health_check(base_url, readiness_path, liveness_path, max_latency_ms)
        return result
    
    @mcp.tool()
    async def audit_repo_run(config_path: str = None) -> dict:
        """
        Ejecuta una auditoría completa de health check usando la configuración del archivo YAML.
        
        Args:
            config_path: Ruta opcional al archivo de configuración (default: usa audit.yaml por defecto)
        
        Returns:
            Resultados de la auditoría con reporte formateado
        """
        return await run_audit(config_path)
    
    @mcp.tool()
    async def terminal_execute_command(command: str, cwd: str = None) -> dict:
        """
        Ejecuta un comando de terminal de forma asíncrona.
        
        Args:
            command: Comando a ejecutar (ej: "ls -la", "ps aux")
            cwd: Directorio de trabajo opcional (default: directorio actual)
        
        Returns:
            Resultado de la ejecución del comando
        """
        return await TerminalTools.execute_command(command, cwd)
    
    @mcp.tool()
    async def terminal_health_check_service(
        base_url: str, 
        readiness_path: str = "/readiness", 
        liveness_path: str = "/liveness",
        max_latency_ms: int = 300
    ) -> dict:
        """
        Realiza un health check a un servicio específico desde terminal.
        
        Args:
            base_url: URL base del servicio (ej: "http://localhost:8080")
            readiness_path: Ruta del endpoint de readiness (default: "/readiness")
            liveness_path: Ruta del endpoint de liveness (default: "/liveness")
            max_latency_ms: Latencia máxima permitida en milisegundos (default: 300)
        
        Returns:
            Resultado del health check con formato de terminal
        """
        return await TerminalTools.health_check_service(base_url, readiness_path, liveness_path, max_latency_ms)
    
    @mcp.tool()
    async def terminal_run_health_audit(config_path: str = None) -> dict:
        """
        Ejecuta una auditoría completa de health check con reporte formateado.
        
        Args:
            config_path: Ruta opcional al archivo de configuración
        
        Returns:
            Resultados de la auditoría con reporte legible
        """
        return await TerminalTools.run_health_audit(config_path)
    
    @mcp.tool()
    async def terminal_batch_health_check(services: list) -> dict:
        """
        Ejecuta health checks para múltiples servicios en lote.
        
        Args:
            services: Lista de servicios con formato [{"name": "servicio1", "url": "http://..."}]
        
        Returns:
            Resultados de todos los checks con reporte consolidado
        """
        return await TerminalTools.batch_health_check(services)
    
    @mcp.tool()
    async def terminal_get_system_info() -> dict:
        """
        Obtiene información básica del sistema (OS, memoria, disco, procesos).
        
        Returns:
            Información del sistema obtenida mediante comandos de terminal
        """
        return await TerminalTools.get_system_info()
    
    