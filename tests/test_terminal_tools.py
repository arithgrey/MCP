"""
Tests unitarios para las herramientas de terminal
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from src.tools.terminal_tools import TerminalTools


class TestTerminalTools:
    """Tests para la clase TerminalTools"""
    
    @pytest.mark.asyncio
    async def test_execute_command_success(self):
        """Verifica la ejecución exitosa de un comando"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            # Mock del proceso
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate.return_value = (
                b"Hello World\n",  # stdout
                b""                 # stderr
            )
            mock_subprocess.return_value = mock_process
            
            result = await TerminalTools.execute_command("echo 'Hello World'")
            
            assert result["success"] is True
            assert result["return_code"] == 0
            assert result["stdout"] == "Hello World\n"
            assert result["stderr"] == ""
            assert result["command"] == "echo 'Hello World'"
            assert result["cwd"] == "."
    
    @pytest.mark.asyncio
    async def test_execute_command_failure(self):
        """Verifica el manejo de comandos que fallan"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.returncode = 1
            mock_process.communicate.return_value = (
                b"",                    # stdout
                b"Command not found\n"  # stderr
            )
            mock_subprocess.return_value = mock_process
            
            result = await TerminalTools.execute_command("invalid_command")
            
            assert result["success"] is False
            assert result["return_code"] == 1
            assert result["stderr"] == "Command not found\n"
    
    @pytest.mark.asyncio
    async def test_execute_command_with_cwd(self):
        """Verifica la ejecución de comandos con directorio de trabajo personalizado"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate.return_value = (b"pwd output\n", b"")
            mock_subprocess.return_value = mock_process
            
            result = await TerminalTools.execute_command("pwd", "/tmp")
            
            assert result["success"] is True
            assert result["cwd"] == "/tmp"
            mock_subprocess.assert_called_once()
            # Verificar que se pasó el directorio de trabajo
            call_args = mock_subprocess.call_args
            assert call_args[1]["cwd"] == "/tmp"
    
    @pytest.mark.asyncio
    async def test_execute_command_exception(self):
        """Verifica el manejo de excepciones durante la ejecución"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_subprocess.side_effect = Exception("Process creation failed")
            
            result = await TerminalTools.execute_command("echo test")
            
            assert result["success"] is False
            assert "Process creation failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_health_check_service_success(self):
        """Verifica un health check exitoso desde terminal"""
        with patch('src.tools.terminal_tools.comprehensive_health_check') as mock_check:
            mock_check.return_value = {
                "overall_status": "healthy",
                "readiness": {"status": "healthy", "latency_ms": 100.0},
                "liveness": {"status": "healthy", "latency_ms": 120.0}
            }
            
            result = await TerminalTools.health_check_service(
                "http://test.com", "/ready", "/live", 300
            )
            
            assert result["success"] is True
            assert result["service_url"] == "http://test.com"
            assert result["overall_status"] == "healthy"
            assert "readiness" in result
            assert "liveness" in result
    
    @pytest.mark.asyncio
    async def test_health_check_service_failure(self):
        """Verifica el manejo de errores en health checks desde terminal"""
        with patch('src.tools.terminal_tools.comprehensive_health_check') as mock_check:
            mock_check.side_effect = Exception("Connection timeout")
            
            result = await TerminalTools.health_check_service("http://test.com")
            
            assert result["success"] is False
            assert result["service_url"] == "http://test.com"
            assert "Connection timeout" in result["error"]
    
    @pytest.mark.asyncio
    async def test_run_health_audit_success(self):
        """Verifica la ejecución exitosa de una auditoría desde terminal"""
        with patch('src.tools.terminal_tools.run_audit') as mock_audit, \
             patch('src.tools.terminal_tools.AuditOrchestrator') as mock_orchestrator_class:
            
            # Mock de la auditoría
            mock_audit.return_value = {
                "total_services": 2,
                "healthy_services": 2,
                "health_percentage": 100.0
            }
            
            # Mock del orquestador para generar reporte
            mock_orchestrator = MagicMock()
            mock_orchestrator.generate_report.return_value = "Reporte generado"
            mock_orchestrator_class.return_value = mock_orchestrator
            
            result = await TerminalTools.run_health_audit()
            
            assert result["success"] is True
            assert result["results"]["total_services"] == 2
            assert result["report"] == "Reporte generado"
    
    @pytest.mark.asyncio
    async def test_run_health_audit_failure(self):
        """Verifica el manejo de errores en auditorías desde terminal"""
        with patch('src.tools.terminal_tools.run_audit') as mock_audit:
            mock_audit.side_effect = Exception("Config file not found")
            
            result = await TerminalTools.run_health_audit()
            
            assert result["success"] is False
            assert "Config file not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_batch_health_check_success(self):
        """Verifica health checks en lote exitosos"""
        services = [
            {"name": "service1", "url": "http://service1.com"},
            {"name": "service2", "url": "http://service2.com"}
        ]
        
        with patch('src.tools.terminal_tools.AuditOrchestrator') as mock_orchestrator_class:
            mock_orchestrator = MagicMock()
            mock_orchestrator.run_batch_check.return_value = {
                "total_services": 2,
                "healthy_services": 2,
                "health_percentage": 100.0
            }
            mock_orchestrator.generate_report.return_value = "Reporte batch"
            mock_orchestrator_class.return_value = mock_orchestrator
            
            result = await TerminalTools.batch_health_check(services)
            
            assert result["success"] is True
            assert result["results"]["total_services"] == 2
            assert result["report"] == "Reporte batch"
            
            # Verificar que se convirtió la lista a dict
            mock_orchestrator.run_batch_check.assert_called_once_with({
                "service1": "http://service1.com",
                "service2": "http://service2.com"
            })
    
    @pytest.mark.asyncio
    async def test_batch_health_check_failure(self):
        """Verifica el manejo de errores en health checks en lote"""
        services = [{"name": "service1", "url": "http://service1.com"}]
        
        with patch('src.tools.terminal_tools.AuditOrchestrator') as mock_orchestrator_class:
            mock_orchestrator_class.side_effect = Exception("Orchestrator failed")
            
            result = await TerminalTools.batch_health_check(services)
            
            assert result["success"] is False
            assert "Orchestrator failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_system_info_success(self):
        """Verifica la obtención exitosa de información del sistema"""
        with patch.object(TerminalTools, 'execute_command') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "stdout": "System info",
                "return_code": 0
            }
            
            result = await TerminalTools.get_system_info()
            
            assert result["success"] is True
            assert "system_info" in result
            assert "os" in result["system_info"]
            assert "memory" in result["system_info"]
            assert "disk" in result["system_info"]
            assert "processes" in result["system_info"]
            
            # Verificar que se llamaron los comandos correctos
            assert mock_execute.call_count == 4
    
    @pytest.mark.asyncio
    async def test_get_system_info_failure(self):
        """Verifica el manejo de errores al obtener información del sistema"""
        with patch.object(TerminalTools, 'execute_command') as mock_execute:
            mock_execute.side_effect = Exception("Command execution failed")
            
            result = await TerminalTools.get_system_info()
            
            assert result["success"] is False
            assert "Command execution failed" in result["error"] 