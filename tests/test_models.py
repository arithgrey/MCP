"""
Tests unitarios para los modelos de datos
"""
import pytest
from datetime import datetime
from src.core.models import Status, CheckResult, HealthSummary


class TestStatus:
    """Tests para el enum Status"""
    
    def test_status_values(self):
        """Verifica que los valores del enum sean correctos"""
        assert Status.HEALTHY == "healthy"
        assert Status.UNHEALTHY == "unhealthy"
        assert Status.DEGRADED == "degraded"
        assert Status.UNKNOWN == "unknown"
    
    def test_status_in_enum(self):
        """Verifica que los valores estén en el enum"""
        assert "healthy" in Status
        assert "unhealthy" in Status
        assert "degraded" in Status
        assert "unknown" in Status


class TestCheckResult:
    """Tests para el modelo CheckResult"""
    
    def test_check_result_creation(self):
        """Verifica la creación de un CheckResult válido"""
        timestamp = datetime.now()
        result = CheckResult(
            status=Status.HEALTHY,
            timestamp=timestamp,
            latency_ms=150.5,
            response_code=200,
            error_message=None,
            details={"url": "http://test.com"}
        )
        
        assert result.status == Status.HEALTHY
        assert result.timestamp == timestamp
        assert result.latency_ms == 150.5
        assert result.response_code == 200
        assert result.error_message is None
        assert result.details == {"url": "http://test.com"}
    
    def test_check_result_with_error(self):
        """Verifica la creación de un CheckResult con error"""
        result = CheckResult(
            status=Status.UNHEALTHY,
            timestamp=datetime.now(),
            latency_ms=500.0,
            response_code=500,
            error_message="Internal Server Error",
            details={"url": "http://test.com"}
        )
        
        assert result.status == Status.UNHEALTHY
        assert result.error_message == "Internal Server Error"
        assert result.response_code == 500
    
    def test_check_result_minimal(self):
        """Verifica la creación de un CheckResult con campos mínimos"""
        result = CheckResult(
            status=Status.UNKNOWN,
            timestamp=datetime.now(),
            latency_ms=0.0
        )
        
        assert result.status == Status.UNKNOWN
        assert result.response_code is None
        assert result.error_message is None
        assert result.details is None
    
    def test_check_result_serialization(self):
        """Verifica que el modelo se pueda serializar a dict"""
        timestamp = datetime.now()
        result = CheckResult(
            status=Status.HEALTHY,
            timestamp=timestamp,
            latency_ms=100.0,
            response_code=200
        )
        
        result_dict = result.dict()
        assert result_dict["status"] == "healthy"
        assert result_dict["latency_ms"] == 100.0
        assert result_dict["response_code"] == 200


class TestHealthSummary:
    """Tests para el modelo HealthSummary"""
    
    def test_health_summary_creation(self):
        """Verifica la creación de un HealthSummary válido"""
        timestamp = datetime.now()
        checks = [
            CheckResult(
                status=Status.HEALTHY,
                timestamp=timestamp,
                latency_ms=100.0
            ),
            CheckResult(
                status=Status.UNHEALTHY,
                timestamp=timestamp,
                latency_ms=500.0
            )
        ]
        
        summary = HealthSummary(
            overall_status=Status.DEGRADED,
            checks=checks,
            total_checks=2,
            healthy_checks=1,
            unhealthy_checks=1,
            average_latency_ms=300.0,
            timestamp=timestamp
        )
        
        assert summary.overall_status == Status.DEGRADED
        assert len(summary.checks) == 2
        assert summary.total_checks == 2
        assert summary.healthy_checks == 1
        assert summary.unhealthy_checks == 1
        assert summary.average_latency_ms == 300.0
        assert summary.timestamp == timestamp
    
    def test_health_summary_serialization(self):
        """Verifica que HealthSummary se pueda serializar"""
        timestamp = datetime.now()
        summary = HealthSummary(
            overall_status=Status.HEALTHY,
            checks=[],
            total_checks=0,
            healthy_checks=0,
            unhealthy_checks=0,
            average_latency_ms=0.0,
            timestamp=timestamp
        )
        
        summary_dict = summary.dict()
        assert summary_dict["overall_status"] == "healthy"
        assert summary_dict["total_checks"] == 0
        assert summary_dict["average_latency_ms"] == 0.0 