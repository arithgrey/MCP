"""
Orquestador de auditorías de health check
"""
import yaml
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
from .health import comprehensive_health_check
from .testing_tools import TestingTools
from src.core.models import HealthSummary, CheckResult, Status
from datetime import datetime


class AuditOrchestrator:
    """Orquestador para ejecutar auditorías de health check"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "src/config/audit.yaml"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Carga la configuración desde el archivo YAML"""
        try:
            with open(self.config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            # Usar configuración por defecto si no existe el archivo
            return {
                "endpoints": {
                    "base_url": "http://localhost:8080",
                    "readiness": "/readiness",
                    "liveness": "/liveness"
                },
                "thresholds": {
                    "http_latency_ms": 300,
                    "coverage_min": 0.80
                }
            }
    
    async def run_single_check(self, service_name: str, base_url: str) -> Dict[str, Any]:
        """
        Ejecuta un health check individual para un servicio
        
        Args:
            service_name: Nombre del servicio
            base_url: URL base del servicio
        
        Returns:
            Resultado del health check
        """
        try:
            result = await comprehensive_health_check(
                base_url=base_url,
                readiness_path=self.config["endpoints"]["readiness"],
                liveness_path=self.config["endpoints"]["liveness"],
                max_latency_ms=self.config["thresholds"]["http_latency_ms"]
            )
            
            return {
                "service_name": service_name,
                "base_url": base_url,
                "timestamp": datetime.now().isoformat(),
                **result
            }
            
        except Exception as e:
            return {
                "service_name": service_name,
                "base_url": base_url,
                "timestamp": datetime.now().isoformat(),
                "overall_status": "error",
                "error": str(e),
                "readiness": None,
                "liveness": None
            }
    
    async def run_batch_check(self, services: Dict[str, str]) -> Dict[str, Any]:
        """
        Ejecuta health checks para múltiples servicios
        
        Args:
            services: Dict con nombre del servicio y URL base
        
        Returns:
            Resultados de todos los checks
        """
        tasks = []
        for service_name, base_url in services.items():
            task = self.run_single_check(service_name, base_url)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Procesar resultados y crear resumen
        successful_results = [r for r in results if not isinstance(r, Exception)]
        failed_results = [r for r in results if isinstance(r, Exception)]
        
        total_services = len(services)
        healthy_services = len([r for r in successful_results if r.get("overall_status") == "healthy"])
        
        summary = {
            "total_services": total_services,
            "healthy_services": healthy_services,
            "unhealthy_services": total_services - healthy_services,
            "failed_checks": len(failed_results),
            "health_percentage": (healthy_services / total_services * 100) if total_services > 0 else 0,
            "timestamp": datetime.now().isoformat(),
            "results": successful_results,
            "errors": [str(e) for e in failed_results] if failed_results else []
        }
        
        return summary
    
    async def run_test_suite(self, service_name: str, test_type: str = "pytest", additional_args: str = "") -> Dict[str, Any]:
        """
        Ejecuta la suite de tests para un servicio usando docker exec
        
        Args:
            service_name: Nombre del servicio/contenedor Docker
            test_type: Tipo de test a ejecutar (default: "pytest")
            additional_args: Argumentos adicionales para los tests
        
        Returns:
            Resultado de la ejecución de tests
        """
        try:
            result = await TestingTools.execute_docker_test(
                service_name=service_name,
                test_command=test_type,
                additional_args=additional_args
            )
            
            return {
                "service_name": service_name,
                "test_type": test_type,
                "timestamp": datetime.now().isoformat(),
                **result
            }
            
        except Exception as e:
            return {
                "service_name": service_name,
                "test_type": test_type,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "status": "error",
                "error": str(e)
            }
    
    async def run_tests_with_coverage(self, service_name: str, coverage_args: str = "--cov=src --cov-report=html") -> Dict[str, Any]:
        """
        Ejecuta tests con coverage para un servicio usando docker exec
        
        Args:
            service_name: Nombre del servicio/contenedor Docker
            coverage_args: Argumentos de coverage
        
        Returns:
            Resultado de la ejecución de tests con coverage
        """
        try:
            result = await TestingTools.run_pytest_with_coverage(
                service_name=service_name,
                coverage_args=coverage_args
            )
            
            return {
                "service_name": service_name,
                "test_type": "pytest_with_coverage",
                "timestamp": datetime.now().isoformat(),
                **result
            }
            
        except Exception as e:
            return {
                "service_name": service_name,
                "test_type": "pytest_with_coverage",
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "status": "error",
                "error": str(e)
            }
    
    async def run_comprehensive_audit(self, service_name: str, include_tests: bool = True) -> Dict[str, Any]:
        """
        Ejecuta una auditoría completa incluyendo health checks y tests
        
        Args:
            service_name: Nombre del servicio/contenedor Docker
            include_tests: Si incluir tests en la auditoría
        
        Returns:
            Resultado completo de la auditoría
        """
        audit_results = {}
        
        # Health check
        try:
            health_result = await self.run_single_check(service_name, f"http://{service_name}:8000")
            audit_results["health_check"] = health_result
        except Exception as e:
            audit_results["health_check"] = {
                "error": str(e),
                "status": "failed"
            }
        
        # Tests (si están habilitados)
        if include_tests:
            try:
                test_result = await self.run_test_suite(service_name)
                audit_results["test_suite"] = test_result
            except Exception as e:
                audit_results["test_suite"] = {
                    "error": str(e),
                    "status": "failed"
                }
        
        # Resumen general
        overall_status = "healthy"
        if audit_results.get("health_check", {}).get("overall_status") != "healthy":
            overall_status = "unhealthy"
        if audit_results.get("test_suite", {}).get("status") == "failed":
            overall_status = "tests_failed"
        
        return {
            "service_name": service_name,
            "overall_status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "audit_results": audit_results,
            "summary": {
                "health_status": audit_results.get("health_check", {}).get("overall_status", "unknown"),
                "test_status": audit_results.get("test_suite", {}).get("status", "unknown"),
                "recommendations": self._generate_recommendations(audit_results)
            }
        }
    
    def _generate_recommendations(self, audit_results: Dict[str, Any]) -> List[str]:
        """
        Genera recomendaciones basadas en los resultados de la auditoría
        
        Args:
            audit_results: Resultados de la auditoría
        
        Returns:
            Lista de recomendaciones
        """
        recommendations = []
        
        # Health check recommendations
        health_check = audit_results.get("health_check", {})
        if health_check.get("overall_status") != "healthy":
            recommendations.append("Revisar la salud del servicio - verificar endpoints de readiness y liveness")
        
        # Test recommendations
        test_suite = audit_results.get("test_suite", {})
        if test_suite.get("status") == "failed":
            recommendations.append("Revisar la suite de tests - verificar que todos los tests pasen")
        elif test_suite.get("status") == "passed":
            recommendations.append("Tests pasando correctamente - considerar agregar más tests para mejorar cobertura")
        
        if not recommendations:
            recommendations.append("Servicio funcionando correctamente - continuar monitoreando")
        
        return recommendations
    
    async def run_from_config(self) -> Dict[str, Any]:
        """
        Ejecuta health checks usando la configuración del archivo YAML
        
        Returns:
            Resultados de los checks
        """
        # Por defecto, usar la configuración del archivo
        base_url = self.config["endpoints"]["base_url"]
        services = {"default_service": base_url}
        
        return await self.run_batch_check(services)
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """
        Genera un reporte legible de los resultados
        
        Args:
            results: Resultados de los health checks
        
        Returns:
            Reporte formateado en texto
        """
        report = []
        report.append("=" * 60)
        report.append("REPORTE DE HEALTH CHECK")
        report.append("=" * 60)
        report.append(f"Timestamp: {results['timestamp']}")
        report.append(f"Total de servicios: {results['total_services']}")
        report.append(f"Servicios saludables: {results['healthy_services']}")
        report.append(f"Servicios no saludables: {results['unhealthy_services']}")
        report.append(f"Porcentaje de salud: {results['health_percentage']:.1f}%")
        report.append(f"Checks fallidos: {results['failed_checks']}")
        report.append("")
        
        if results.get("results"):
            report.append("DETALLES POR SERVICIO:")
            report.append("-" * 40)
            
            for result in results["results"]:
                status_emoji = "✅" if result["overall_status"] == "healthy" else "❌"
                report.append(f"{status_emoji} {result['service_name']}")
                report.append(f"   URL: {result['base_url']}")
                report.append(f"   Estado: {result['overall_status']}")
                
                if result.get("readiness"):
                    readiness = result["readiness"]
                    report.append(f"   Readiness: {readiness['status']} ({readiness['latency_ms']:.2f}ms)")
                
                if result.get("liveness"):
                    liveness = result["liveness"]
                    report.append(f"   Liveness: {liveness['status']} ({liveness['latency_ms']:.2f}ms)")
                
                report.append("")
        
        if results.get("errors"):
            report.append("ERRORES ENCONTRADOS:")
            report.append("-" * 40)
            for error in results["errors"]:
                report.append(f"❌ {error}")
        
        report.append("=" * 60)
        return "\n".join(report)


# Función de conveniencia para uso directo
async def run_audit(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Función de conveniencia para ejecutar una auditoría completa
    
    Args:
        config_path: Ruta opcional al archivo de configuración
    
    Returns:
        Resultados de la auditoría
    """
    orchestrator = AuditOrchestrator(config_path)
    return await orchestrator.run_from_config() 