"""
Herramientas de testing para el servidor MCP
Aplicando principio DRY para evitar duplicación
"""
import asyncio
import subprocess
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from src.config.common import CommonConfig, DEFAULT_SERVICE_NAME, DEFAULT_TEST_COMMAND, DEFAULT_COVERAGE_ARGS


class TestingTools:
    """Herramientas para ejecutar tests en contenedores Docker"""
    
    @classmethod
    async def execute_docker_test(cls, service_name: str = None, test_command: str = None, additional_args: str = "") -> Dict[str, Any]:
        """
        Ejecuta tests en un contenedor Docker usando docker exec
        
        Args:
            service_name: Nombre del servicio/contenedor Docker
            test_command: Comando de testing a ejecutar
            additional_args: Argumentos adicionales para el comando de testing
        
        Returns:
            Resultado de la ejecución de tests
        """
        # Usar valores por defecto de la configuración común
        service_name = service_name or DEFAULT_SERVICE_NAME
        test_command = test_command or DEFAULT_TEST_COMMAND
        
        return await cls._execute_docker_command(service_name, test_command, additional_args)
    
    @classmethod
    async def _execute_docker_command(cls, service_name: str, test_command: str, additional_args: str = "") -> Dict[str, Any]:
        """Método interno para ejecutar comandos Docker (DRY)"""
        try:
            # Construir el comando completo
            full_command = f"docker exec {service_name} {test_command}"
            if additional_args:
                full_command += f" {additional_args}"
            
            # Ejecutar el comando
            process = await asyncio.create_subprocess_exec(
                *full_command.split(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Decodificar la salida
            stdout_text = stdout.decode('utf-8') if stdout else ""
            stderr_text = stderr.decode('utf-8') if stderr else ""
            
            # Determinar el estado del test
            success = process.returncode == 0
            status = "passed" if success else "failed"
            
            # Estructura de respuesta consistente (DRY)
            return cls._create_response_dict(
                success=success,
                status=status,
                service_name=service_name,
                command=full_command,
                return_code=process.returncode,
                stdout=stdout_text,
                stderr=stderr_text
            )
            
        except Exception as e:
            return cls._create_response_dict(
                success=False,
                status="error",
                service_name=service_name,
                command=f"docker exec {service_name} {test_command}",
                error=str(e)
            )
    
    @classmethod
    def _create_response_dict(cls, **kwargs) -> Dict[str, Any]:
        """Crea un diccionario de respuesta consistente (DRY)"""
        response = {
            "success": kwargs.get("success", False),
            "status": kwargs.get("status", "error"),
            "service_name": kwargs.get("service_name", ""),
            "command": kwargs.get("command", ""),
            "timestamp": datetime.now().isoformat(),
            "execution_time_ms": 0
        }
        
        # Agregar campos opcionales si existen
        if "return_code" in kwargs:
            response["return_code"] = kwargs["return_code"]
        if "stdout" in kwargs:
            response["stdout"] = kwargs["stdout"]
        if "stderr" in kwargs:
            response["stderr"] = kwargs["stderr"]
        if "error" in kwargs:
            response["error"] = kwargs["error"]
        
        return response
    
    @classmethod
    async def run_pytest_with_coverage(cls, service_name: str = None, coverage_args: str = None) -> Dict[str, Any]:
        """
        Ejecuta pytest con coverage en un contenedor Docker
        
        Args:
            service_name: Nombre del servicio/contenedor Docker
            coverage_args: Argumentos de coverage adicionales
        
        Returns:
            Resultado de la ejecución con coverage
        """
        service_name = service_name or DEFAULT_SERVICE_NAME
        coverage_args = coverage_args or DEFAULT_COVERAGE_ARGS
        
        return await cls._execute_docker_command(
            service_name=service_name,
            test_command="pytest",
            additional_args=coverage_args
        )
    
    @classmethod
    async def run_specific_test_file(cls, service_name: str, test_file: str, additional_args: str = "") -> Dict[str, Any]:
        """
        Ejecuta un archivo de test específico en un contenedor Docker
        
        Args:
            service_name: Nombre del servicio/contenedor Docker
            test_file: Ruta al archivo de test
            additional_args: Argumentos adicionales
        
        Returns:
            Resultado de la ejecución del test específico
        """
        return await cls._execute_docker_command(
            service_name=service_name,
            test_command="pytest",
            additional_args=f"{test_file} {additional_args}".strip()
        )
    
    @classmethod
    async def run_test_with_markers(cls, service_name: str, marker: str, additional_args: str = "") -> Dict[str, Any]:
        """
        Ejecuta tests con un marcador específico en un contenedor Docker
        
        Args:
            service_name: Nombre del servicio/contenedor Docker
            marker: Marcador de pytest (ej: "slow", "integration")
            additional_args: Argumentos adicionales
        
        Returns:
            Resultado de la ejecución de tests con marcador
        """
        return await cls._execute_docker_command(
            service_name=service_name,
            test_command="pytest",
            additional_args=f"-m {marker} {additional_args}".strip()
        )
    
    @classmethod
    async def run_parallel_tests(cls, service_name: str, num_workers: int = 4, additional_args: str = "") -> Dict[str, Any]:
        """
        Ejecuta tests en paralelo usando pytest-xdist en un contenedor Docker
        
        Args:
            service_name: Nombre del servicio/contenedor Docker
            num_workers: Número de workers para ejecución paralela
            additional_args: Argumentos adicionales
        
        Returns:
            Resultado de la ejecución de tests paralelos
        """
        return await cls._execute_docker_command(
            service_name=service_name,
            test_command="pytest",
            additional_args=f"-n {num_workers} {additional_args}".strip()
        )
    
    @classmethod
    async def run_tests_with_verbose_output(cls, service_name: str, test_command: str = "pytest", additional_args: str = "") -> Dict[str, Any]:
        """
        Ejecuta tests con salida verbose en un contenedor Docker
        
        Args:
            service_name: Nombre del servicio/contenedor Docker
            test_command: Comando de testing a ejecutar
            additional_args: Argumentos adicionales
        
        Returns:
            Resultado de la ejecución con salida verbose
        """
        return await cls._execute_docker_command(
            service_name=service_name,
            test_command=test_command,
            additional_args=f"-v {additional_args}".strip()
        )
    
    @classmethod
    async def run_tests_with_html_report(cls, service_name: str, report_dir: str = "test_reports", additional_args: str = "") -> Dict[str, Any]:
        """
        Ejecuta tests generando un reporte HTML en un contenedor Docker
        
        Args:
            service_name: Nombre del servicio/contenedor Docker
            report_dir: Directorio para el reporte HTML
            additional_args: Argumentos adicionales
        
        Returns:
            Resultado de la ejecución con reporte HTML
        """
        return await cls._execute_docker_command(
            service_name=service_name,
            test_command="pytest",
            additional_args=f"--html={report_dir}/report.html --self-contained-html {additional_args}".strip()
        )
    
    @classmethod
    async def run_tests_with_junit_report(cls, service_name: str, report_file: str = "junit.xml", additional_args: str = "") -> Dict[str, Any]:
        """
        Ejecuta tests generando un reporte JUnit XML en un contenedor Docker
        
        Args:
            service_name: Nombre del servicio/contenedor Docker
            report_file: Archivo de reporte JUnit XML
            additional_args: Argumentos adicionales
        
        Returns:
            Resultado de la ejecución con reporte JUnit XML
        """
        return await cls._execute_docker_command(
            service_name=service_name,
            test_command="pytest",
            additional_args=f"--junitxml={report_file} {additional_args}".strip()
        )
    
    @classmethod
    async def run_custom_test_command(cls, service_name: str, test_command: str, additional_args: str = "") -> Dict[str, Any]:
        """
        Ejecuta un comando de testing personalizado en un contenedor Docker
        
        Args:
            service_name: Nombre del servicio/contenedor Docker
            test_command: Comando de testing personalizado
            additional_args: Argumentos adicionales
        
        Returns:
            Resultado de la ejecución del comando personalizado
        """
        return await cls._execute_docker_command(
            service_name=service_name,
            test_command=test_command,
            additional_args=additional_args
        )


# Funciones de conveniencia para uso directo (DRY)
async def run_docker_test(service_name: str = None, test_command: str = None, additional_args: str = "") -> Dict[str, Any]:
    """
    Función de conveniencia para ejecutar tests en Docker
    
    Args:
        service_name: Nombre del servicio/contenedor Docker
        test_command: Comando de testing a ejecutar
        additional_args: Argumentos adicionales
    
    Returns:
        Resultado de la ejecución de tests
    """
    return await TestingTools.execute_docker_test(service_name, test_command, additional_args)


async def run_pytest_coverage(service_name: str = None, coverage_args: str = None) -> Dict[str, Any]:
    """
    Función de conveniencia para ejecutar pytest con coverage
    
    Args:
        service_name: Nombre del servicio/contenedor Docker
        coverage_args: Argumentos de coverage
    
    Returns:
        Resultado de la ejecución con coverage
    """
    return await TestingTools.run_pytest_with_coverage(service_name, coverage_args)


async def run_specific_test(service_name: str, test_file: str, additional_args: str = "") -> Dict[str, Any]:
    """
    Función de conveniencia para ejecutar un test específico
    
    Args:
        service_name: Nombre del servicio/contenedor Docker
        test_file: Archivo de test específico
        additional_args: Argumentos adicionales
    
    Returns:
        Resultado de la ejecución del test específico
    """
    return await TestingTools.run_specific_test_file(service_name, test_file, additional_args) 