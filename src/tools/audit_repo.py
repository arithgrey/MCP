"""
Orquestador de auditorías de health check
"""
import yaml
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from .health import comprehensive_health_check
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
    results = await orchestrator.run_from_config()
    return results 