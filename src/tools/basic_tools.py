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
from .structure_inspector import inspect_microservice_structure, inspect_repository_structure
from datetime import datetime
from pathlib import Path
from .claude_rules import load_claude_rules
from .claude_rules import (
    start_claude_watcher,
    stop_claude_watcher,
    is_claude_watcher_running,
    get_cached_claude_rules,
)

def register_tools(mcp):
    """Registra todas las herramientas básicas"""
    
    @mcp.tool()
    def get_claude_rules() -> dict:
        """
        Lee y devuelve las reglas del archivo CLAUDE.md del proyecto.
        Returns: { success: bool, path: str, content: str }
        """
        return load_claude_rules()

    @mcp.tool()
    def claude_watcher_start(poll_interval_sec: float = 1.0) -> dict:
        """Inicia el watcher de CLAUDE.md (sondeo)."""
        return start_claude_watcher(poll_interval_sec)

    @mcp.tool()
    def claude_watcher_stop() -> dict:
        """Detiene el watcher de CLAUDE.md."""
        return stop_claude_watcher()

    @mcp.tool()
    def claude_watcher_status() -> dict:
        """Devuelve el estado del watcher de CLAUDE.md."""
        return is_claude_watcher_running()

    @mcp.tool()
    def get_cached_claude() -> dict:
        """Devuelve el contenido cacheado de CLAUDE.md (inicia watcher si no corre)."""
        return get_cached_claude_rules()

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
    
    @mcp.tool()
    async def audit_service_architecture(service_path: str, base_path: str = ".", generate_todo_md: bool = True) -> dict:
        """
        Realiza auditoría completa de arquitectura de un microservicio con perfil de arquitecto senior.
        Incluye análisis de estructura básica, principios de arquitectura y generación de plan de acciones TODO.
        
        Args:
            service_path: Ruta al microservicio a auditar (ej: "src", "services/auth", "microservices/user-service")
            base_path: Ruta base del repositorio (default: ".")
            generate_todo_md: Si generar y guardar el archivo TODO.md (default: True)
        
        Returns:
            Reporte completo de auditoría de arquitectura con análisis de principios y plan de acciones TODO
        """
        try:
            from .structure_inspector import (
                analyze_microservice_architecture_advanced,
                generate_architecture_todo_plan,
                inspect_microservice_structure,
                generate_and_save_todo_md
            )
            
            # Resolver rutas de manera más robusta
            from pathlib import Path
            current_dir = Path.cwd()
            
            # Si service_path es relativo, resolverlo desde current_dir
            if not Path(service_path).is_absolute():
                resolved_service_path = (current_dir / service_path).resolve()
            else:
                resolved_service_path = Path(service_path)
            
            # Si base_path es ".", usar el directorio del servicio
            if base_path == ".":
                resolved_base_path = resolved_service_path.parent
            else:
                resolved_base_path = Path(base_path)
            
            # Análisis de estructura básica
            structure_report = inspect_microservice_structure(str(resolved_service_path), str(resolved_base_path))
            
            # Análisis avanzado de arquitectura
            architecture_analysis = analyze_microservice_architecture_advanced(str(resolved_service_path), str(resolved_base_path))
            
            # Generar plan de acciones TODO
            todo_actions = generate_architecture_todo_plan(str(resolved_service_path), str(resolved_base_path))
            
            # Generar y guardar archivo TODO.md si se solicita
            todo_md_path = None
            if generate_todo_md:
                try:
                    todo_md_path = generate_and_save_todo_md(str(resolved_service_path), str(resolved_base_path))
                except Exception as e:
                    print(f"⚠️  Advertencia: No se pudo generar el archivo TODO.md: {e}")
            
            # Calcular score general
            overall_score = (structure_report.score + architecture_analysis.architecture_score) / 2
            
            # Determinar estado general
            if overall_score >= 80:
                overall_status = "EXCELLENT"
            elif overall_score >= 60:
                overall_status = "GOOD"
            elif overall_score >= 40:
                overall_status = "FAIR"
            elif overall_score >= 20:
                overall_status = "POOR"
            else:
                overall_status = "CRITICAL"
            
            # Generar resumen ejecutivo
            executive_summary = f"""
            Análisis de Arquitectura del Microservicio: {service_path}
            
            Estado General: {overall_status} (Score: {overall_score:.1f}/100)
            
            Estructura Básica: {structure_report.status.value.upper()} (Score: {structure_report.score:.1f}/100)
            Arquitectura: {architecture_analysis.architecture_status} (Score: {architecture_analysis.architecture_score:.1f}/100)
            
            Principios de Arquitectura:
            - DRY (Don't Repeat Yourself): {'✅ CUMPLE' if architecture_analysis.drp_compliance else '❌ VIOLACIÓN'}
            - TDD (Test Driven Development): {'✅ CUMPLE' if architecture_analysis.tdd_implementation else '❌ VIOLACIÓN'}
            - Pruebas de Integración: {'✅ CUMPLE' if architecture_analysis.integration_tests else '❌ VIOLACIÓN'}
            - Datos Faker: {'✅ CUMPLE' if architecture_analysis.faker_data_usage else '❌ VIOLACIÓN'}
            - Escalabilidad: {'✅ CUMPLE' if architecture_analysis.scalability_features else '❌ VIOLACIÓN'}
            
            Violaciones Detectadas: {architecture_analysis.total_violations}
            - Críticas: {architecture_analysis.critical_violations}
            - Altas: {architecture_analysis.high_violations}
            - Medias: {architecture_analysis.medium_violations}
            - Bajas: {architecture_analysis.low_violations}
            
            Acciones TODO Prioritarias: {len([a for a in todo_actions if a.priority in ['CRITICAL', 'HIGH']])}
            
            {'📄 Archivo TODO.md generado: ' + todo_md_path if todo_md_path else '📄 Archivo TODO.md no generado'}
            """
            
            # Recomendaciones prioritarias
            priority_recommendations = []
            for action in todo_actions[:5]:  # Top 5 acciones
                priority_recommendations.append(f"[{action.priority}] {action.action}: {action.description}")
            
            return {
                "success": True,
                "service_name": service_path,
                "service_path": str(Path(base_path) / service_path),
                "timestamp": datetime.now().isoformat(),
                
                # Análisis de estructura básica
                "structure_report": structure_report.dict(),
                
                # Análisis avanzado de arquitectura
                "architecture_analysis": architecture_analysis.dict(),
                
                # Plan de acciones TODO
                "todo_actions": [action.dict() for action in todo_actions],
                
                # Archivo TODO.md generado
                "todo_md_generated": todo_md_path is not None,
                "todo_md_path": todo_md_path,
                
                # Resumen ejecutivo
                "executive_summary": executive_summary.strip(),
                "overall_score": overall_score,
                "overall_status": overall_status,
                
                # Recomendaciones prioritarias
                "priority_recommendations": priority_recommendations,
                
                # Métricas clave
                "key_metrics": {
                    "structure_score": structure_report.score,
                    "architecture_score": architecture_analysis.architecture_score,
                    "total_violations": architecture_analysis.total_violations,
                    "critical_violations": architecture_analysis.critical_violations,
                    "todo_actions_count": len(todo_actions),
                    "priority_actions_count": len([a for a in todo_actions if a.priority in ['CRITICAL', 'HIGH']])
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "error",
                "service_path": service_path
            }
    
    @mcp.tool()
    async def get_structure_template_info(template_path: str = None) -> dict:
        """
        Obtiene información sobre la plantilla de estructura actual.
        
        Args:
            template_path: Ruta opcional al archivo de plantilla
        
        Returns:
            Información de la plantilla de estructura
        """
        try:
            from .template_loader import TemplateLoader
            
            loader = TemplateLoader(template_path)
            template_info = loader.get_template_info()
            
            return {
                "success": True,
                "template_info": template_info,
                "template_path": str(loader.template_path)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "error"
            }
    