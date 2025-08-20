"""
Herramientas básicas para el servidor MCP
"""
import asyncio
from .health import readiness_check, liveness_check, comprehensive_health_check
from .audit_repo import run_audit
from .terminal_tools import TerminalTools
from .endpoint_detector import detect_service_endpoints, auto_health_check
from .testing_tools import TestingTools, run_docker_test, run_pytest_coverage, run_specific_test
from .api_analyzer import analyze_api_service, generate_api_docs

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
    async def audit_orchestrator_test_suite(service_name: str, test_type: str = "pytest", additional_args: str = "") -> dict:
        """
        Ejecuta la suite de tests para un servicio usando el orquestador con formato docker exec.
        
        Args:
            service_name: Nombre del servicio/contenedor Docker (ej: "mcp-service")
            test_type: Tipo de test a ejecutar (default: "pytest")
            additional_args: Argumentos adicionales para los tests
        
        Returns:
            Resultado de la ejecución de tests usando docker exec
        """
        from .audit_repo import AuditOrchestrator
        orchestrator = AuditOrchestrator()
        return await orchestrator.run_test_suite(service_name, test_type, additional_args)
    
    @mcp.tool()
    async def audit_orchestrator_tests_with_coverage(service_name: str, coverage_args: str = "--cov=src --cov-report=html") -> dict:
        """
        Ejecuta tests con coverage para un servicio usando el orquestador con formato docker exec.
        
        Args:
            service_name: Nombre del servicio/contenedor Docker (ej: "mcp-service")
            coverage_args: Argumentos de coverage
        
        Returns:
            Resultado de la ejecución de tests con coverage usando docker exec
        """
        from .audit_repo import AuditOrchestrator
        orchestrator = AuditOrchestrator()
        return await orchestrator.run_tests_with_coverage(service_name, coverage_args)
    
    @mcp.tool()
    async def audit_orchestrator_comprehensive_audit(service_name: str, include_tests: bool = True) -> dict:
        """
        Ejecuta una auditoría completa incluyendo health checks y tests usando docker exec.
        
        Args:
            service_name: Nombre del servicio/contenedor Docker (ej: "mcp-service")
            include_tests: Si incluir tests en la auditoría (default: True)
        
        Returns:
            Resultado completo de la auditoría con health checks y tests
        """
        from .audit_repo import AuditOrchestrator
        orchestrator = AuditOrchestrator()
        return await orchestrator.run_comprehensive_audit(service_name, include_tests)
    
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
    
    @mcp.tool()
    async def docker_test_execute(service_name: str, test_command: str = "pytest", additional_args: str = "") -> dict:
        """
        Ejecuta tests en un contenedor Docker usando docker exec.
        
        Args:
            service_name: Nombre del servicio/contenedor Docker (ej: "mcp-service")
            test_command: Comando de testing a ejecutar (default: "pytest")
            additional_args: Argumentos adicionales para el comando de testing
        
        Returns:
            Resultado de la ejecución de tests con formato docker exec
        """
        return await run_docker_test(service_name, test_command, additional_args)
    
    @mcp.tool()
    async def docker_test_pytest_coverage(service_name: str, coverage_args: str = "--cov=src --cov-report=html") -> dict:
        """
        Ejecuta pytest con coverage en un contenedor Docker usando docker exec.
        
        Args:
            service_name: Nombre del servicio/contenedor Docker (ej: "mcp-service")
            coverage_args: Argumentos de coverage adicionales
        
        Returns:
            Resultado de la ejecución con coverage usando docker exec
        """
        return await run_pytest_coverage(service_name, coverage_args)
    
    @mcp.tool()
    async def docker_test_specific_file(service_name: str, test_file: str, additional_args: str = "") -> dict:
        """
        Ejecuta un archivo de test específico en un contenedor Docker usando docker exec.
        
        Args:
            service_name: Nombre del servicio/contenedor Docker (ej: "mcp-service")
            test_file: Ruta al archivo de test (ej: "tests/test_health.py")
            additional_args: Argumentos adicionales
        
        Returns:
            Resultado de la ejecución del test específico usando docker exec
        """
        return await run_specific_test(service_name, test_file, additional_args)
    
    @mcp.tool()
    async def docker_test_with_markers(service_name: str, marker: str, additional_args: str = "") -> dict:
        """
        Ejecuta tests con un marcador específico en un contenedor Docker usando docker exec.
        
        Args:
            service_name: Nombre del servicio/contenedor Docker (ej: "mcp-service")
            marker: Marcador de pytest (ej: "slow", "integration", "unit")
            additional_args: Argumentos adicionales
        
        Returns:
            Resultado de la ejecución de tests con marcador usando docker exec
        """
        return await TestingTools.run_test_with_markers(service_name, marker, additional_args)
    
    @mcp.tool()
    async def docker_test_parallel(service_name: str, num_workers: int = 4, additional_args: str = "") -> dict:
        """
        Ejecuta tests en paralelo usando pytest-xdist en un contenedor Docker usando docker exec.
        
        Args:
            service_name: Nombre del servicio/contenedor Docker (ej: "mcp-service")
            num_workers: Número de workers para ejecución paralela (default: 4)
            additional_args: Argumentos adicionales
        
        Returns:
            Resultado de la ejecución de tests paralelos usando docker exec
        """
        return await TestingTools.run_parallel_tests(service_name, num_workers, additional_args)
    
    @mcp.tool()
    async def docker_test_verbose(service_name: str, test_command: str = "pytest", additional_args: str = "") -> dict:
        """
        Ejecuta tests con salida verbose en un contenedor Docker usando docker exec.
        
        Args:
            service_name: Nombre del servicio/contenedor Docker (ej: "mcp-service")
            test_command: Comando de testing a ejecutar (default: "pytest")
            additional_args: Argumentos adicionales
        
        Returns:
            Resultado de la ejecución con salida verbose usando docker exec
        """
        return await TestingTools.run_tests_with_verbose_output(service_name, test_command, additional_args)
    
    @mcp.tool()
    async def docker_test_html_report(service_name: str, report_dir: str = "test_reports", additional_args: str = "") -> dict:
        """
        Ejecuta tests generando un reporte HTML en un contenedor Docker usando docker exec.
        
        Args:
            service_name: Nombre del servicio/contenedor Docker (ej: "mcp-service")
            report_dir: Directorio para el reporte HTML (default: "test_reports")
            additional_args: Argumentos adicionales
        
        Returns:
            Resultado de la ejecución con reporte HTML usando docker exec
        """
        return await TestingTools.run_tests_with_html_report(service_name, report_dir, additional_args)
    
    @mcp.tool()
    async def docker_test_junit_report(service_name: str, report_file: str = "junit.xml", additional_args: str = "") -> dict:
        """
        Ejecuta tests generando un reporte JUnit XML en un contenedor Docker usando docker exec.
        
        Args:
            service_name: Nombre del servicio/contenedor Docker (ej: "mcp-service")
            report_file: Archivo de reporte JUnit XML (default: "junit.xml")
            additional_args: Argumentos adicionales
        
        Returns:
            Resultado de la ejecución con reporte JUnit XML usando docker exec
        """
        return await TestingTools.run_tests_with_junit_report(service_name, report_file, additional_args)
    
    @mcp.tool()
    async def docker_test_custom_command(service_name: str, test_command: str, additional_args: str = "") -> dict:
        """
        Ejecuta un comando de testing personalizado en un contenedor Docker usando docker exec.
        
        Args:
            service_name: Nombre del servicio/contenedor Docker (ej: "mcp-service")
            test_command: Comando de testing personalizado (ej: "python -m pytest", "tox")
            additional_args: Argumentos adicionales
        
        Returns:
            Resultado de la ejecución del comando personalizado usando docker exec
        """
        return await TestingTools.run_custom_test_command(service_name, test_command, additional_args)
    
    @mcp.tool()
    async def api_analyze_service(base_url: str, swagger_path: str = None, timeout_ms: int = 10000) -> dict:
        """
        Analiza una API completa desde una URL base, detectando y entendiendo su estructura.
        
        Args:
            base_url: URL base del servicio (ej: "https://api.miservicio.com")
            swagger_path: Ruta específica del Swagger (opcional, se detecta automáticamente)
            timeout_ms: Timeout en milisegundos para la detección y análisis (default: 10000)
        
        Returns:
            Análisis completo de la API incluyendo endpoints, modelos, tags y estadísticas
        """
        return await analyze_api_service(base_url, swagger_path, timeout_ms)
    
    @mcp.tool()
    async def api_generate_documentation(base_url: str, swagger_path: str = None, timeout_ms: int = 10000) -> dict:
        """
        Genera documentación inteligente y completa de una API.
        
        Args:
            base_url: URL base del servicio (ej: "https://api.miservicio.com")
            swagger_path: Ruta específica del Swagger (opcional, se detecta automáticamente)
            timeout_ms: Timeout en milisegundos para la detección y análisis (default: 10000)
        
        Returns:
            Documentación completa con ejemplos de uso, patrones identificados y recomendaciones
        """
        return await generate_api_docs(base_url, swagger_path, timeout_ms)
    
    @mcp.tool()
    async def api_comprehensive_audit(base_url: str, swagger_path: str = None, timeout_ms: int = 10000) -> dict:
        """
        Realiza una auditoría completa de una API: análisis + documentación + health check.
        
        Args:
            base_url: URL base del servicio (ej: "https://api.miservicio.com")
            swagger_path: Ruta específica del Swagger (opcional, se detecta automáticamente)
            timeout_ms: Timeout en milisegundos (default: 10000)
        
        Returns:
            Auditoría completa con análisis de API, documentación y verificación de salud
        """
        # Primero analizar la API
        api_analysis = await analyze_api_service(base_url, swagger_path, timeout_ms)
        
        if not api_analysis["success"]:
            return {
                "success": False,
                "error": "No se pudo analizar la API",
                "details": api_analysis
            }
        
        # Generar documentación
        api_docs = await generate_api_docs(base_url, swagger_path, timeout_ms)
        
        # Realizar health check
        health_check = await auto_health_check(base_url, timeout_ms)
        
        return {
            "success": True,
            "api_url": base_url,
            "timestamp": asyncio.get_event_loop().time(),
            "api_analysis": api_analysis,
            "api_documentation": api_docs,
            "health_check": health_check,
            "comprehensive_summary": {
                "api_title": api_analysis["analysis"]["info"]["title"],
                "api_version": api_analysis["analysis"]["info"]["version"],
                "total_endpoints": api_analysis["analysis"]["statistics"]["total_endpoints"],
                "total_models": api_analysis["analysis"]["statistics"]["total_models"],
                "complexity_level": api_analysis["analysis"]["statistics"]["openapi_version"],
                "has_authentication": api_analysis["analysis"]["security"]["requires_authentication"],
                "health_status": health_check.get("health_check", {}).get("overall_status", "unknown") if health_check.get("success") else "failed",
                "recommendations": api_analysis["analysis"].get("recommendations", [])
            }
        }
    