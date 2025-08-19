from enum import Enum
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class Status(str, Enum):
    """Estado del health check"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class CheckResult(BaseModel):
    """Resultado de un health check"""
    status: Status
    timestamp: datetime
    latency_ms: float
    response_code: Optional[int] = None
    error_message: Optional[str] = None
    details: Optional[dict] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HealthSummary(BaseModel):
    """Resumen de todos los health checks"""
    overall_status: Status
    checks: list[CheckResult]
    total_checks: int
    healthy_checks: int
    unhealthy_checks: int
    average_latency_ms: float
    timestamp: datetime
