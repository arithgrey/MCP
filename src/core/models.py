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


# Nuevos modelos para análisis avanzado de arquitectura
class ArchitecturePrinciple(str, Enum):
    """Principios de arquitectura a verificar"""
    DRY = "DRY"
    TDD = "TDD"
    INTEGRATION_TESTS = "INTEGRATION_TESTS"
    FAKER_DATA = "FAKER_DATA"
    SCALABILITY = "SCALABILITY"


class PrincipleViolation(BaseModel):
    """Violación de un principio de arquitectura"""
    principle: ArchitecturePrinciple
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    recommendation: str


class ArchitectureAnalysis(BaseModel):
    """Análisis completo de arquitectura del microservicio"""
    drp_compliance: bool  # DRY - Don't Repeat Yourself
    tdd_implementation: bool  # Test Driven Development
    integration_tests: bool  # Pruebas de integración
    faker_data_usage: bool  # Uso de Faker para datos de prueba
    scalability_features: bool  # Características de escalabilidad
    
    violations: List[PrincipleViolation] = []
    total_violations: int = 0
    critical_violations: int = 0
    high_violations: int = 0
    medium_violations: int = 0
    low_violations: int = 0
    
    architecture_score: float = 0.0
    architecture_status: str = "UNKNOWN"


class TODOAction(BaseModel):
    """Acción TODO para mejorar la arquitectura"""
    priority: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    principle: ArchitecturePrinciple
    action: str
    description: str
    estimated_effort: str  # "1-2 hours", "1 day", "1 week", etc.
    dependencies: List[str] = []
    files_to_modify: List[str] = []


class ArchitectureAuditReport(BaseModel):
    """Reporte completo de auditoría de arquitectura"""
    service_name: str
    service_path: str
    timestamp: datetime
    
    # Análisis de estructura básica
    structure_report: MicroserviceStructureReport
    
    # Análisis avanzado de arquitectura
    architecture_analysis: ArchitectureAnalysis
    
    # Plan de acciones TODO
    todo_actions: List[TODOAction]
    
    # Resumen ejecutivo
    executive_summary: str
    overall_score: float
    overall_status: str
    
    # Recomendaciones prioritarias
    priority_recommendations: List[str]


class FilePreventionRule(BaseModel):
    """Regla de prevención para tipos de archivos"""
    file_type: str  # "makefile", "shell_script", "other"
    enabled: bool = True
    blocked_patterns: List[str]
    allowed_exceptions: List[str] = []
    django_microservice_patterns: List[str] = []
    error_message: str
    alternatives: List[str] = []


class PathPreventionRule(BaseModel):
    """Regla de prevención para rutas problemáticas"""
    rule_type: str  # "relative_path", "parent_directory", "context_escape"
    enabled: bool = True
    blocked_patterns: List[str]
    allowed_exceptions: List[str] = []
    error_message: str
    alternatives: List[str] = []
    severity: str = "high"  # "low", "medium", "high", "critical"


class FileCreationPolicy(BaseModel):
    """Política de creación de archivos"""
    makefiles: FilePreventionRule
    shell_scripts: FilePreventionRule
    path_prevention: PathPreventionRule
    other_restricted: List[FilePreventionRule] = []


class PreventionViolation(BaseModel):
    """Violación de reglas de prevención de archivos"""
    file_path: str
    rule_type: str
    error_message: str
    alternatives: List[str]
    timestamp: datetime = datetime.now()
    severity: str = "high"  # "low", "medium", "high", "critical"
