"""
Modelos para manejar plantillas de configuración de estructura
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class QualityPattern(BaseModel):
    """Patrón de calidad para validación"""
    name: str
    regex: Optional[str] = None
    content: Optional[str] = None
    description: str
    weight: int
    required: bool = False
    warning: Optional[str] = None


class RequiredFile(BaseModel):
    """Archivo requerido para la estructura"""
    name: str
    description: str
    required: bool
    weight: int
    type: Optional[str] = "file"  # "file" o "directory"
    must_contain: Optional[List[str]] = None


class FileQuality(BaseModel):
    """Criterios de calidad para un tipo de archivo"""
    patterns: List[QualityPattern]


class ScoringConfig(BaseModel):
    """Configuración de scoring"""
    base_weights: Dict[str, int] = {}
    thresholds: Dict[str, int] = {}
    warning_penalty: int = 2
    bonus_features: Dict[str, int] = {}


class StructureTemplate(BaseModel):
    """Plantilla de estructura para microservicios"""
    name: str
    description: str
    required_files: List[RequiredFile]
    dockerfile_quality: Optional[FileQuality] = None
    compose_quality: Optional[FileQuality] = None
    gitignore_quality: Optional[FileQuality] = None
    tests_quality: Optional[FileQuality] = None
    file_prevention: Optional[Any] = None  # Se definirá como FileCreationPolicy


class TemplateConfig(BaseModel):
    """Configuración completa de plantillas"""
    default: StructureTemplate
    scoring: ScoringConfig
    file_prevention: Optional[Any] = None  # Se definirá como FileCreationPolicy 