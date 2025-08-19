"""
Herramientas de terminal para el servidor MCP
"""
import asyncio
import subprocess
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from .audit_repo import AuditOrchestrator, run_audit
from .health import comprehensive_health_check


class TerminalTools:
    """Herramientas para ejecutar comandos de terminal y health checks"""
    
    @staticmethod
    async def execute_command(command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        """
        Ejecuta un comando de terminal de forma asíncrona
        
        Args:
            command: Comando a ejecutar
            cwd: Directorio de trabajo (opcional)
        
        Returns:
            Dict con el resultado de la ejecución
        """
        try:
            # Ejecutar comando de forma asíncrona
            process = await asyncio.create_subprocess_exec(
                *command.split(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "success": process.returncode == 0,
                "return_code": process.returncode,
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore'),
                "command": command,
                "cwd": cwd or "."
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command,
                "cwd": cwd or "."
            }
    
    @staticmethod
    async def health_check_service(
        base_url: str, 
        readiness_path: str = "/readiness", 
        liveness_path: str = "/liveness",
        max_latency_ms: int = 300
    ) -> Dict[str, Any]:
        """
        Realiza un health check a un servicio específico
        
        Args:
            base_url: URL base del servicio
            readiness_path: Ruta del endpoint de readiness
            liveness_path: Ruta del endpoint de liveness
            max_latency_ms: Latencia máxima permitida en ms
        
        Returns:
            Resultado del health check
        """
        try:
            result = await comprehensive_health_check(
                base_url=base_url,
                readiness_path=readiness_path,
                liveness_path=liveness_path,
                max_latency_ms=max_latency_ms
            )
            
            return {
                "success": True,
                "service_url": base_url,
                "timestamp": result.get("timestamp", ""),
                "overall_status": result.get("overall_status", "unknown"),
                "readiness": result.get("readiness", {}),
                "liveness": result.get("liveness", {})
            }
            
        except Exception as e:
            return {
                "success": False,
                "service_url": base_url,
                "error": str(e)
            }
    
    @staticmethod
    async def run_health_audit(config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Ejecuta una auditoría completa de health check
        
        Args:
            config_path: Ruta opcional al archivo de configuración
        
        Returns:
            Resultados de la auditoría
        """
        try:
            results = await run_audit(config_path)
            
            # Generar reporte legible
            orchestrator = AuditOrchestrator(config_path)
            report = orchestrator.generate_report(results)
            
            return {
                "success": True,
                "results": results,
                "report": report
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def batch_health_check(services: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Ejecuta health checks para múltiples servicios
        
        Args:
            services: Lista de servicios con formato [{"name": "servicio1", "url": "http://..."}]
        
        Returns:
            Resultados de todos los checks
        """
        try:
            orchestrator = AuditOrchestrator()
            
            # Convertir lista a dict para el orquestador
            services_dict = {service["name"]: service["url"] for service in services}
            
            results = await orchestrator.run_batch_check(services_dict)
            report = orchestrator.generate_report(results)
            
            return {
                "success": True,
                "results": results,
                "report": report
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def get_system_info() -> Dict[str, Any]:
        """
        Obtiene información básica del sistema
        
        Returns:
            Información del sistema
        """
        try:
            # Comandos para obtener información del sistema
            commands = {
                "os": "uname -a",
                "memory": "free -h",
                "disk": "df -h",
                "processes": "ps aux | head -10"
            }
            
            results = {}
            for info_type, command in commands.items():
                result = await TerminalTools.execute_command(command)
                results[info_type] = result
            
            return {
                "success": True,
                "system_info": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            } 