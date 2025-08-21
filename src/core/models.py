from enum import Enum
from typing import Optional, List
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


class StructureStatus(str, Enum):
    """Estado de la estructura del microservicio"""
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    POOR = "poor"


class StructureChecks(BaseModel):
    """Verificaciones de estructura básica"""
    Dockerfile: bool
    docker_compose_yml: bool
    gitignore: bool
    tests_dir_exists: bool
    tests_dir_has_files: bool


class ConfigQuality(BaseModel):
    """Calidad de la configuración"""
    dockerfile_best_practices: List[str] = []
    compose_warnings: List[str] = []
    gitignore_warnings: List[str] = []
    tests_warnings: List[str] = []


class MicroserviceStructureReport(BaseModel):
    """Reporte completo de la estructura de un microservicio"""
    service: str
    path: str
    structure_checks: StructureChecks
    config_quality: ConfigQuality
    status: StructureStatus
    recommendations: List[str] = []
    score: float = 0.0


class RepositoryStructureAudit(BaseModel):
    """Auditoría completa de la estructura de todos los microservicios"""
    total_services: int
    complete_services: int
    incomplete_services: int
    poor_services: int
    average_score: float
    services: List[MicroserviceStructureReport]
    timestamp: datetime
    overall_status: StructureStatus
