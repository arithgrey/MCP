"""
Tests unitarios para el orquestador de auditorías
"""
import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock, mock_open
from src.tools.audit_repo import AuditOrchestrator, run_audit
from src.core.models import Status


class TestAuditOrchestrator:
    """Tests para la clase AuditOrchestrator"""
    
    def test_init_with_default_config(self):
        """Verifica la inicialización con configuración por defecto"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            orchestrator = AuditOrchestrator()
            
            assert orchestrator.config["endpoints"]["base_url"] == "http://localhost:8080"
            assert orchestrator.config["endpoints"]["readiness"] == "/readiness"
            assert orchestrator.config["endpoints"]["liveness"] == "/liveness"
            assert orchestrator.config["thresholds"]["http_latency_ms"] == 300
    
    def test_init_with_custom_config(self):
        """Verifica la inicialización con archivo de configuración personalizado"""
        test_config = {
            "endpoints": {
                "base_url": "http://custom.com",
                "readiness": "/custom/ready",
                "liveness": "/custom/live"
            },
            "thresholds": {
                "http_latency_ms": 500
            }
        }
        
        with patch('builtins.open', mock_open(read_data='')):
            with patch('yaml.safe_load', return_value=test_config):
                orchestrator = AuditOrchestrator("custom.yaml")
                
                assert orchestrator.config["endpoints"]["base_url"] == "http://custom.com"
                assert orchestrator.config["endpoints"]["readiness"] == "/custom/ready"
                assert orchestrator.config["thresholds"]["http_latency_ms"] == 500
    
    @pytest.mark.asyncio
    async def test_run_single_check_success(self):
        """Verifica la ejecución exitosa de un health check individual"""
        with patch('src.tools.audit_repo.comprehensive_health_check') as mock_check:
            mock_check.return_value = {
                "overall_status": "healthy",
                "readiness": {"status": "healthy", "latency_ms": 100.0},
                "liveness": {"status": "healthy", "latency_ms": 120.0}
            }
            
            orchestrator = AuditOrchestrator()
            result = await orchestrator.run_single_check("test_service", "http://test.com")
            
            assert result["service_name"] == "test_service"
            assert result["base_url"] == "http://test.com"
            assert result["overall_status"] == "healthy"
            assert "readiness" in result
            assert "liveness" in result
    
    @pytest.mark.asyncio
    async def test_run_single_check_failure(self):
        """Verifica el manejo de errores en health checks individuales"""
        with patch('src.tools.audit_repo.comprehensive_health_check') as mock_check:
            mock_check.side_effect = Exception("Connection failed")
            
            orchestrator = AuditOrchestrator()
            result = await orchestrator.run_single_check("test_service", "http://test.com")
            
            assert result["service_name"] == "test_service"
            assert result["base_url"] == "http://test.com"
            assert result["overall_status"] == "error"
            assert result["error"] == "Connection failed"
    
    @pytest.mark.asyncio
    async def test_run_batch_check_success(self):
        """Verifica la ejecución exitosa de health checks en lote"""
        services = {
            "service1": "http://service1.com",
            "service2": "http://service2.com"
        }
        
        with patch('src.tools.audit_repo.comprehensive_health_check') as mock_check:
            mock_check.return_value = {
                "overall_status": "healthy",
                "readiness": {"status": "healthy", "latency_ms": 100.0},
                "liveness": {"status": "healthy", "latency_ms": 120.0}
            }
            
            orchestrator = AuditOrchestrator()
            result = await orchestrator.run_batch_check(services)
            
            assert result["total_services"] == 2
            assert result["healthy_services"] == 2
            assert result["unhealthy_services"] == 0
            assert result["health_percentage"] == 100.0
            assert len(result["results"]) == 2
    
    @pytest.mark.asyncio
    async def test_run_batch_check_with_failures(self):
        """Verifica el manejo de fallos en health checks en lote"""
        services = {
            "service1": "http://service1.com",
            "service2": "http://service2.com"
        }
        
        with patch('src.tools.audit_repo.comprehensive_health_check') as mock_check:
            # Primer servicio exitoso
            mock_check.side_effect = [
                {"overall_status": "healthy"},
                Exception("Connection failed")
            ]
            
            orchestrator = AuditOrchestrator()
            result = await orchestrator.run_batch_check(services)
            
            assert result["total_services"] == 2
            assert result["healthy_services"] == 1
            assert result["unhealthy_services"] == 1
            assert result["health_percentage"] == 50.0
            assert len(result["results"]) == 1
            assert len(result["errors"]) == 1
    
    @pytest.mark.asyncio
    async def test_run_from_config(self):
        """Verifica la ejecución usando la configuración del archivo"""
        with patch('src.tools.audit_repo.comprehensive_health_check') as mock_check:
            mock_check.return_value = {
                "overall_status": "healthy",
                "readiness": {"status": "healthy"},
                "liveness": {"status": "healthy"}
            }
            
            orchestrator = AuditOrchestrator()
            result = await orchestrator.run_from_config()
            
            assert result["total_services"] == 1
            assert "default_service" in [r["service_name"] for r in result["results"]]
    
    def test_generate_report(self):
        """Verifica la generación de reportes"""
        test_results = {
            "total_services": 2,
            "healthy_services": 1,
            "unhealthy_services": 1,
            "failed_checks": 0,
            "health_percentage": 50.0,
            "timestamp": "2024-01-01T00:00:00",
            "results": [
                {
                    "service_name": "service1",
                    "base_url": "http://service1.com",
                    "overall_status": "healthy",
                    "readiness": {"status": "healthy", "latency_ms": 100.0},
                    "liveness": {"status": "healthy", "latency_ms": 120.0}
                },
                {
                    "service_name": "service2",
                    "base_url": "http://service2.com",
                    "overall_status": "unhealthy",
                    "readiness": {"status": "unhealthy", "latency_ms": 500.0},
                    "liveness": {"status": "healthy", "latency_ms": 150.0}
                }
            ],
            "errors": []
        }
        
        orchestrator = AuditOrchestrator()
        report = orchestrator.generate_report(test_results)
        
        assert "REPORTE DE HEALTH CHECK" in report
        assert "Total de servicios: 2" in report
        assert "Servicios saludables: 1" in report
        assert "Servicios no saludables: 1" in report
        assert "Porcentaje de salud: 50.0%" in report
        assert "✅ service1" in report
        assert "❌ service2" in report


class TestRunAudit:
    """Tests para la función de conveniencia run_audit"""
    
    @pytest.mark.asyncio
    async def test_run_audit_default(self):
        """Verifica la ejecución de auditoría con configuración por defecto"""
        with patch('src.tools.audit_repo.AuditOrchestrator') as mock_orchestrator_class:
            mock_orchestrator = MagicMock()
            mock_orchestrator.run_from_config.return_value = {
                "total_services": 1,
                "healthy_services": 1,
                "health_percentage": 100.0
            }
            mock_orchestrator_class.return_value = mock_orchestrator
            
            result = await run_audit()
            
            assert result["total_services"] == 1
            assert result["healthy_services"] == 1
            assert result["health_percentage"] == 100.0
            mock_orchestrator_class.assert_called_once_with(None)
    
    @pytest.mark.asyncio
    async def test_run_audit_custom_config(self):
        """Verifica la ejecución de auditoría con configuración personalizada"""
        with patch('src.tools.audit_repo.AuditOrchestrator') as mock_orchestrator_class:
            mock_orchestrator = MagicMock()
            mock_orchestrator.run_from_config.return_value = {
                "total_services": 2,
                "healthy_services": 2,
                "health_percentage": 100.0
            }
            mock_orchestrator_class.return_value = mock_orchestrator
            
            result = await run_audit("custom.yaml")
            
            assert result["total_services"] == 2
            mock_orchestrator_class.assert_called_once_with("custom.yaml") 