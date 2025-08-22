"""
Tests unitarios para las herramientas de health check
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from src.tools.health import http_check, readiness_check, liveness_check, comprehensive_health_check
from src.core.models import Status


class TestHttpCheck:
    """Tests para la función http_check"""
    
    @pytest.mark.asyncio
    async def test_http_check_success(self):
        """Verifica un health check exitoso"""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock de respuesta exitosa
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "application/json"}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value = mock_client_instance
            
            result = await http_check("http://test.com", "/health", 1000)
            
            assert result.status == Status.HEALTHY
            assert result.response_code == 200
            assert result.error_message is None
            assert result.details["url"] == "http://test.com/health"
            assert result.details["method"] == "GET"
    
    @pytest.mark.asyncio
    async def test_http_check_http_error(self):
        """Verifica un health check con error HTTP"""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock de respuesta con error
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.headers = {}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value = mock_client_instance
            
            result = await http_check("http://test.com", "/health", 1000)
            
            assert result.status == Status.UNHEALTHY
            assert result.response_code == 500
            assert result.error_message == "HTTP 500"
    
    @pytest.mark.asyncio
    async def test_http_check_timeout(self):
        """Verifica un health check con timeout"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.get.side_effect = Exception("Timeout")
            mock_client.return_value = mock_client_instance
            
            result = await http_check("http://test.com", "/health", 1000)
            
            assert result.status == Status.UNHEALTHY
            assert result.error_message == "Timeout"
    
    @pytest.mark.asyncio
    async def test_http_check_url_normalization(self):
        """Verifica que las URLs se normalicen correctamente"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value = mock_client_instance
            
            # Test con diferentes formatos de URL
            result1 = await http_check("http://test.com/", "/health", 1000)
            result2 = await http_check("http://test.com", "health", 1000)
            
            assert result1.details["url"] == "http://test.com/health"
            assert result2.details["url"] == "http://test.com/health"


class TestReadinessCheck:
    """Tests para la función readiness_check"""
    
    @pytest.mark.asyncio
    async def test_readiness_check_healthy(self):
        """Verifica un readiness check saludable"""
        with patch('src.tools.health.http_check') as mock_http_check:
            mock_result = MagicMock()
            mock_result.status = Status.HEALTHY
            mock_result.latency_ms = 150.0
            mock_result.dict.return_value = {"status": "healthy", "latency_ms": 150.0}
            
            mock_http_check.return_value = mock_result
            
            result = await readiness_check("http://test.com", "/ready", 300)
            
            assert result.status == Status.HEALTHY
            mock_http_check.assert_called_once_with("http://test.com", "/ready", 600)
    
    @pytest.mark.asyncio
    async def test_readiness_check_degraded(self):
        """Verifica un readiness check degradado por latencia alta"""
        with patch('src.tools.health.http_check') as mock_http_check:
            mock_result = MagicMock()
            mock_result.status = Status.HEALTHY
            mock_result.latency_ms = 500.0  # Mayor que el umbral de 300ms
            mock_result.dict.return_value = {"status": "healthy", "latency_ms": 500.0}
            
            mock_http_check.return_value = mock_result
            
            result = await readiness_check("http://test.com", "/ready", 300)
            
            assert result.status == Status.DEGRADED
            assert "Latencia alta" in result.error_message


class TestLivenessCheck:
    """Tests para la función liveness_check"""
    
    @pytest.mark.asyncio
    async def test_liveness_check_healthy(self):
        """Verifica un liveness check saludable"""
        with patch('src.tools.health.http_check') as mock_http_check:
            mock_result = MagicMock()
            mock_result.status = Status.HEALTHY
            mock_result.latency_ms = 150.0
            mock_result.dict.return_value = {"status": "healthy", "latency_ms": 150.0}
            
            mock_http_check.return_value = mock_result
            
            result = await liveness_check("http://test.com", "/live", 300)
            
            assert result.status == Status.HEALTHY
            mock_http_check.assert_called_once_with("http://test.com", "/live", 600)
    
    @pytest.mark.asyncio
    async def test_liveness_check_unhealthy_high_latency(self):
        """Verifica que liveness sea más estricto con la latencia"""
        with patch('src.tools.health.http_check') as mock_http_check:
            mock_result = MagicMock()
            mock_result.status = Status.HEALTHY
            mock_result.latency_ms = 500.0  # Mayor que el umbral de 300ms
            mock_result.dict.return_value = {"status": "healthy", "latency_ms": 500.0}
            
            mock_http_check.return_value = mock_result
            
            result = await liveness_check("http://test.com", "/live", 300)
            
            assert result.status == Status.UNHEALTHY
            assert "Latencia crítica" in result.error_message


class TestComprehensiveHealthCheck:
    """Tests para la función comprehensive_health_check"""
    
    @pytest.mark.asyncio
    async def test_comprehensive_health_check_success(self):
        """Verifica un health check completo exitoso"""
        with patch('src.tools.health.readiness_check') as mock_readiness, \
             patch('src.tools.health.liveness_check') as mock_liveness:
            
            # Mock readiness check
            mock_readiness_result = MagicMock()
            mock_readiness_result.status = Status.HEALTHY
            mock_readiness_result.dict.return_value = {"status": "healthy", "latency_ms": 100.0}
            mock_readiness.return_value = mock_readiness_result
            
            # Mock liveness check
            mock_liveness_result = MagicMock()
            mock_liveness_result.status = Status.HEALTHY
            mock_liveness_result.dict.return_value = {"status": "healthy", "latency_ms": 120.0}
            mock_liveness.return_value = mock_liveness_result
            
            result = await comprehensive_health_check(
                "http://test.com", "/ready", "/live", 300
            )
            
            assert result["overall_status"] == "healthy"
            assert "readiness" in result
            assert "liveness" in result
            mock_readiness.assert_called_once_with("http://test.com", "/ready", 300)
            mock_liveness.assert_called_once_with("http://test.com", "/live", 300)
    
    @pytest.mark.asyncio
    async def test_comprehensive_health_check_partial_failure(self):
        """Verifica un health check completo con fallo parcial"""
        with patch('src.tools.health.readiness_check') as mock_readiness, \
             patch('src.tools.health.liveness_check') as mock_liveness:
            
            # Mock readiness check fallido
            mock_readiness_result = MagicMock()
            mock_readiness_result.status = Status.UNHEALTHY
            mock_readiness_result.dict.return_value = {"status": "unhealthy", "latency_ms": 500.0}
            mock_readiness.return_value = mock_readiness_result
            
            # Mock liveness check exitoso
            mock_liveness_result = MagicMock()
            mock_liveness_result.status = Status.HEALTHY
            mock_liveness_result.dict.return_value = {"status": "healthy", "latency_ms": 100.0}
            mock_liveness.return_value = mock_liveness_result
            
            result = await comprehensive_health_check(
                "http://test.com", "/ready", "/live", 300
            )
            
            assert result["overall_status"] == "unhealthy"
            assert result["readiness"]["status"] == "unhealthy"
            assert result["liveness"]["status"] == "healthy" 