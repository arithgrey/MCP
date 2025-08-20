"""
Herramientas básicas para el servidor MCP
"""
import asyncio
from .health import readiness_check, liveness_check, comprehensive_health_check
from .audit_repo import run_audit
from .terminal_tools import TerminalTools
from .endpoint_detector import detect_service_endpoints, auto_health_check

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
    
    @mcp.tool()
    async def auto_detect_endpoints(base_url: str, timeout_ms: int = 5000) -> dict:
        """
        Detecta automáticamente los endpoints de health check y Swagger de un servicio.
        
        Args:
            base_url: URL base del servicio (ej: "https://api.miservicio.com")
            timeout_ms: Timeout en milisegundos para cada endpoint (default: 5000)
        
        Returns:
            Resultado completo de la detección con endpoints encontrados
        """
        return await detect_service_endpoints(base_url, timeout_ms)
    
    @mcp.tool()
    async def auto_health_check_service(base_url: str, timeout_ms: int = 5000) -> dict:
        """
        Realiza un health check automático usando los endpoints detectados del servicio.
        
        Args:
            base_url: URL base del servicio (ej: "https://api.miservicio.com")
            timeout_ms: Timeout en milisegundos para la detección y health check (default: 5000)
        
        Returns:
            Resultado del health check usando los mejores endpoints detectados
        """
        return await auto_health_check(base_url, timeout_ms)
    
    @mcp.tool()
    async def smart_service_audit(base_url: str, timeout_ms: int = 5000) -> dict:
        """
        Auditoría inteligente completa de un servicio: detecta endpoints y realiza health check.
        
        Args:
            base_url: URL base del servicio (ej: "https://api.miservicio.com")
            timeout_ms: Timeout en milisegundos (default: 5000)
        
        Returns:
            Auditoría completa con detección de endpoints y health check
        """
        # Primero detectar endpoints
        detection = await detect_service_endpoints(base_url, timeout_ms)
        
        # Luego realizar health check con los endpoints detectados
        health_check = await auto_health_check(base_url, timeout_ms)
        
        return {
            "service_url": base_url,
            "timestamp": asyncio.get_event_loop().time(),
            "detection": detection,
            "health_check": health_check,
            "summary": {
                "has_health_endpoints": detection["health"]["summary"]["total_found"] > 0,
                "has_swagger": detection["swagger"]["summary"]["has_swagger"],
                "health_status": health_check.get("health_check", {}).get("overall_status", "unknown") if health_check.get("success") else "failed",
                "recommendations": detection["recommendations"]
            }
        }
    