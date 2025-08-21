"""
Herramienta para inspeccionar la estructura base de microservicios
Siguiendo estándares técnicos mínimos de arquitectura moderna
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from ..core.models import (
    StructureStatus, 
    StructureChecks, 
    ConfigQuality, 
    MicroserviceStructureReport,
    RepositoryStructureAudit
)
from .template_loader import TemplateLoader


class BaseStructureInspector:
    """Inspector de estructura base para microservicios"""
    
    def __init__(self, base_path: str = ".", template_path: str = None):
        self.base_path = Path(base_path)
        self.template_loader = TemplateLoader(template_path)
        self.template = self.template_loader.get_template()
        self.scoring_config = self.template_loader.get_scoring_config()
        
        # Patrones para validación de contenido (se pueden sobrescribir con plantillas)
        self.dockerfile_patterns = self._get_dockerfile_patterns()
        self.compose_patterns = self._get_compose_patterns()
        self.gitignore_patterns = self._get_gitignore_patterns()
        self.test_patterns = self._get_test_patterns()
    
    def _get_dockerfile_patterns(self) -> Dict[str, str]:
        """Obtiene patrones de Dockerfile desde la plantilla o usa los por defecto"""
        if self.template.dockerfile_quality:
            patterns = {}
            for pattern in self.template.dockerfile_quality.patterns:
                if pattern.regex:
                    patterns[pattern.name] = pattern.regex
            return patterns
        
        # Patrones por defecto
        return {
            "expose_missing": r"EXPOSE\s+\d+",
            "copy_all": r"COPY\s+\.\s+\.",
            "unnecessary_tools": r"(apt-get|yum|apk)\s+install.*(vim|nano|curl|wget)"
        }
    
    def _get_compose_patterns(self) -> Dict[str, str]:
        """Obtiene patrones de docker-compose desde la plantilla o usa los por defecto"""
        if self.template.compose_quality:
            patterns = {}
            for pattern in self.template.compose_quality.patterns:
                if pattern.regex:
                    patterns[pattern.name] = pattern.regex
            return patterns
        
        # Patrones por defecto
        return {
            "restart_policy": r"restart:\s*(unless-stopped|always|on-failure)",
            "volumes_defined": r"volumes:",
            "networks_defined": r"networks:",
            "depends_on": r"depends_on:"
        }
    
    def _get_gitignore_patterns(self) -> List[str]:
        """Obtiene patrones de .gitignore desde la plantilla o usa los por defecto"""
        if self.template.gitignore_quality:
            patterns = []
            for pattern in self.template.gitignore_quality.patterns:
                if pattern.content:
                    patterns.append(pattern.content)
            return patterns
        
        # Patrones por defecto
        return [
            ".env", "__pycache__/", "*.pyc", "node_modules/", 
            "build/", "dist/", ".pytest_cache/", "*.log"
        ]
    
    def _get_test_patterns(self) -> List[str]:
        """Obtiene patrones de tests desde la plantilla o usa los por defecto"""
        if self.template.tests_quality:
            patterns = []
            for pattern in self.template.tests_quality.patterns:
                if pattern.regex:
                    patterns.append(pattern.regex)
            return patterns
        
        # Patrones por defecto
        return [
            r"test_.*\.py$", r".*_test\.py$", r"tests/.*\.py$"
        ]
    
    def inspect_microservice(self, service_path: str) -> MicroserviceStructureReport:
        """
        Inspecciona la estructura de un microservicio específico
        
        Args:
            service_path: Ruta al microservicio
            
        Returns:
            Reporte completo de la estructura
        """
        full_path = self.base_path / service_path
        
        if not full_path.exists():
            raise ValueError(f"El directorio {service_path} no existe")
        
        # Verificaciones básicas de estructura usando la plantilla
        structure_checks = self._check_basic_structure(full_path)
        
        # Auditoría de calidad de configuración
        config_quality = self._audit_config_quality(full_path)
        
        # Cálculo de score y estado usando la configuración de la plantilla
        score = self._calculate_score(structure_checks, config_quality)
        status = self._determine_status(score)
        
        # Generación de recomendaciones
        recommendations = self._generate_recommendations(structure_checks, config_quality)
        
        return MicroserviceStructureReport(
            service=service_path,
            path=str(full_path),
            structure_checks=structure_checks,
            config_quality=config_quality,
            status=status,
            score=score,
            recommendations=recommendations
        )
    
    def inspect_repository(self, service_paths: List[str] = None) -> RepositoryStructureAudit:
        """
        Inspecciona la estructura de todos los microservicios en el repositorio
        
        Args:
            service_paths: Lista de rutas de microservicios (si no se proporciona, se detectan automáticamente)
            
        Returns:
            Auditoría completa de la estructura del repositorio
        """
        if service_paths is None:
            service_paths = self._auto_detect_services()
        
        services = []
        for service_path in service_paths:
            try:
                service_report = self.inspect_microservice(service_path)
                services.append(service_report)
            except Exception as e:
                # Crear reporte de error para servicios problemáticos
                error_report = self._create_error_report(service_path, str(e))
                services.append(error_report)
        
        # Estadísticas agregadas
        total_services = len(services)
        complete_services = sum(1 for s in services if s.status == StructureStatus.COMPLETE)
        incomplete_services = sum(1 for s in services if s.status == StructureStatus.INCOMPLETE)
        poor_services = sum(1 for s in services if s.status == StructureStatus.POOR)
        
        if total_services > 0:
            average_score = sum(s.score for s in services) / total_services
        else:
            average_score = 0.0
        
        # Estado general del repositorio
        if complete_services == total_services:
            overall_status = StructureStatus.COMPLETE
        elif poor_services == 0:
            overall_status = StructureStatus.INCOMPLETE
        else:
            overall_status = StructureStatus.POOR
        
        return RepositoryStructureAudit(
            total_services=total_services,
            complete_services=complete_services,
            incomplete_services=incomplete_services,
            poor_services=poor_services,
            average_score=average_score,
            services=services,
            timestamp=datetime.now(),
            overall_status=overall_status
        )
    
    def _check_basic_structure(self, service_path: Path) -> StructureChecks:
        """Verifica la estructura básica del microservicio usando la plantilla"""
        checks = {}
        
        # Verificar cada archivo requerido según la plantilla
        for required_file in self.template.required_files:
            file_path = service_path / required_file.name
            
            if required_file.type == "directory":
                exists = file_path.exists() and file_path.is_dir()
                has_files = False
                
                if exists and required_file.must_contain:
                    # Verificar que el directorio contenga archivos con los patrones especificados
                    for pattern in required_file.must_contain:
                        if list(file_path.glob(pattern)):
                            has_files = True
                            break
                elif exists:
                    # Si no se especifican patrones, solo verificar que exista
                    has_files = True
                
                checks[required_file.name.replace("/", "_").replace(".", "_")] = exists
                if required_file.name == "tests/":
                    checks["tests_dir_exists"] = exists
                    checks["tests_dir_has_files"] = has_files
            else:
                checks[required_file.name.replace(".", "_")] = file_path.exists()
        
        # Mapear a la estructura esperada
        return StructureChecks(
            Dockerfile=checks.get("Dockerfile", False),
            docker_compose_yml=checks.get("docker_compose_yml", False),
            gitignore=checks.get("gitignore", False),
            tests_dir_exists=checks.get("tests_dir_exists", False),
            tests_dir_has_files=checks.get("tests_dir_has_files", False)
        )
    
    def _audit_config_quality(self, service_path: Path) -> ConfigQuality:
        """Audita la calidad de la configuración usando la plantilla"""
        dockerfile_warnings = self._audit_dockerfile(service_path)
        compose_warnings = self._audit_docker_compose(service_path)
        gitignore_warnings = self._audit_gitignore(service_path)
        tests_warnings = self._audit_tests(service_path)
        
        return ConfigQuality(
            dockerfile_best_practices=dockerfile_warnings,
            compose_warnings=compose_warnings,
            gitignore_warnings=gitignore_warnings,
            tests_warnings=tests_warnings
        )
    
    def _audit_dockerfile(self, service_path: Path) -> List[str]:
        """Audita la calidad del Dockerfile usando la plantilla"""
        warnings = []
        dockerfile_path = service_path / "Dockerfile"
        
        if not dockerfile_path.exists():
            return warnings
        
        try:
            content = dockerfile_path.read_text()
            
            # Usar patrones de la plantilla si están disponibles
            if self.template.dockerfile_quality:
                for pattern in self.template.dockerfile_quality.patterns:
                    if pattern.regex:
                        if pattern.warning and not re.search(pattern.regex, content):
                            warnings.append(pattern.warning)
                        elif pattern.warning and re.search(pattern.regex, content):
                            warnings.append(pattern.warning)
            else:
                # Usar patrones por defecto
                if not re.search(self.dockerfile_patterns["expose_missing"], content):
                    warnings.append("EXPOSE missing")
                
                if re.search(self.dockerfile_patterns["copy_all"], content):
                    warnings.append("uses COPY . . without .dockerignore")
                
                if re.search(self.dockerfile_patterns["unnecessary_tools"], content):
                    warnings.append("installs unnecessary tools")
                
        except Exception:
            warnings.append("unable to read Dockerfile content")
        
        return warnings
    
    def _audit_docker_compose(self, service_path: Path) -> List[str]:
        """Audita la calidad del docker-compose.yml usando la plantilla"""
        warnings = []
        compose_path = service_path / "docker-compose.yml"
        
        if not compose_path.exists():
            return warnings
        
        try:
            content = compose_path.read_text()
            
            # Usar patrones de la plantilla si están disponibles
            if self.template.compose_quality:
                for pattern in self.template.compose_quality.patterns:
                    if pattern.regex and pattern.warning:
                        if not re.search(pattern.regex, content):
                            warnings.append(pattern.warning)
            else:
                # Usar patrones por defecto
                if not re.search(self.compose_patterns["restart_policy"], content):
                    warnings.append("no restart policy")
                
                if not re.search(self.compose_patterns["volumes_defined"], content):
                    warnings.append("no volumes defined")
                
                if not re.search(self.compose_patterns["networks_defined"], content):
                    warnings.append("no networks defined")
                
                if not re.search(self.compose_patterns["depends_on"], content):
                    warnings.append("no depends_on defined")
                
        except Exception:
            warnings.append("unable to read docker-compose.yml content")
        
        return warnings
    
    def _audit_gitignore(self, service_path: Path) -> List[str]:
        """Audita la calidad del .gitignore usando la plantilla"""
        warnings = []
        gitignore_path = service_path / ".gitignore"
        
        if not gitignore_path.exists():
            warnings.append("missing .gitignore file")
            return warnings
        
        try:
            content = gitignore_path.read_text()
            
            # Usar patrones de la plantilla si están disponibles
            if self.template.gitignore_quality:
                for pattern in self.template.gitignore_quality.patterns:
                    if pattern.content and pattern.warning:
                        if pattern.content not in content:
                            warnings.append(pattern.warning)
            else:
                # Usar patrones por defecto
                for pattern in self.gitignore_patterns:
                    if pattern not in content:
                        warnings.append(f"missing {pattern}")
                    
        except Exception:
            warnings.append("unable to read .gitignore content")
        
        return warnings
    
    def _audit_tests(self, service_path: Path) -> List[str]:
        """Audita la calidad de los tests usando la plantilla"""
        warnings = []
        tests_dir = service_path / "tests"
        
        if not tests_dir.exists():
            warnings.append("tests directory missing")
            return warnings
        
        test_files = list(tests_dir.glob("*.py"))
        
        if not test_files:
            warnings.append("no test files found")
            return warnings
        
        # Verificar nombres de archivos de test usando la plantilla
        if self.template.tests_quality:
            for pattern in self.template.tests_quality.patterns:
                if pattern.regex:
                    # Verificar si algún archivo cumple con el patrón
                    pattern_matches = any(re.match(pattern.regex, test_file.name) for test_file in test_files)
                    if not pattern_matches and pattern.warning:
                        warnings.append(pattern.warning)
        else:
            # Usar patrones por defecto
            for test_file in test_files:
                filename = test_file.name
                if not any(re.match(pattern, filename) for pattern in self.test_patterns):
                    warnings.append(f"test file {filename} doesn't follow naming convention")
        
        return warnings
    
    def _calculate_score(self, structure_checks: StructureChecks, config_quality: ConfigQuality) -> float:
        """Calcula el score de calidad del microservicio usando la plantilla"""
        base_score = 0.0
        
        # Calcular score basado en archivos requeridos según la plantilla
        for required_file in self.template.required_files:
            if required_file.type == "directory":
                if required_file.name == "tests/":
                    if structure_checks.tests_dir_exists:
                        base_score += required_file.weight
                else:
                    # Para otros directorios, verificar si existen
                    dir_exists = (self.base_path / required_file.name).exists()
                    if dir_exists:
                        base_score += required_file.weight
            else:
                # Para archivos
                if required_file.name == "Dockerfile" and structure_checks.Dockerfile:
                    base_score += required_file.weight
                elif required_file.name == "docker-compose.yml" and structure_checks.docker_compose_yml:
                    base_score += required_file.weight
                elif required_file.name == ".gitignore" and structure_checks.gitignore:
                    base_score += required_file.weight
        
        # Calidad de configuración usando la configuración de scoring de la plantilla
        config_score = 0.0
        
        # Aplicar bonificaciones por características avanzadas
        if self.template.dockerfile_quality:
            for pattern in self.template.dockerfile_quality.patterns:
                if pattern.weight > 0:  # Solo bonificaciones positivas
                    config_score += pattern.weight
        
        if self.template.compose_quality:
            for pattern in self.template.compose_quality.patterns:
                if pattern.weight > 0:  # Solo bonificaciones positivas
                    config_score += pattern.weight
        
        # Penalizaciones por warnings
        total_warnings = (
            len(config_quality.dockerfile_best_practices) +
            len(config_quality.compose_warnings) +
            len(config_quality.gitignore_warnings) +
            len(config_quality.tests_warnings)
        )
        
        # Cada warning reduce el score según la configuración
        warning_penalty = self.scoring_config.warning_penalty
        config_score -= total_warnings * warning_penalty
        
        return max(0.0, base_score + config_score)
    
    def _determine_status(self, score: float) -> StructureStatus:
        """Determina el estado basado en el score usando la plantilla"""
        thresholds = self.scoring_config.thresholds
        
        if score >= thresholds["complete"]:
            return StructureStatus.COMPLETE
        elif score >= thresholds["incomplete"]:
            return StructureStatus.INCOMPLETE
        else:
            return StructureStatus.POOR
    
    def _generate_recommendations(self, structure_checks: StructureChecks, config_quality: ConfigQuality) -> List[str]:
        """Genera recomendaciones basadas en los hallazgos y la plantilla"""
        recommendations = []
        
        # Recomendaciones basadas en archivos faltantes según la plantilla
        for required_file in self.template.required_files:
            if required_file.required:
                if required_file.name == "Dockerfile" and not structure_checks.Dockerfile:
                    recommendations.append(f"Crear {required_file.name} para {required_file.description}")
                elif required_file.name == "docker-compose.yml" and not structure_checks.docker_compose_yml:
                    recommendations.append(f"Crear {required_file.name} para {required_file.description}")
                elif required_file.name == ".gitignore" and not structure_checks.gitignore:
                    recommendations.append(f"Crear {required_file.name} para {required_file.description}")
                elif required_file.name == "tests/" and not structure_checks.tests_dir_exists:
                    recommendations.append(f"Crear directorio {required_file.name} para {required_file.description}")
        
        # Recomendaciones de calidad
        if config_quality.dockerfile_best_practices:
            recommendations.append("Mejorar Dockerfile siguiendo mejores prácticas")
        if config_quality.compose_warnings:
            recommendations.append("Mejorar docker-compose.yml con políticas de reinicio y volúmenes")
        if config_quality.gitignore_warnings:
            recommendations.append("Mejorar .gitignore con patrones estándar")
        if config_quality.tests_warnings:
            recommendations.append("Mejorar estructura y convenciones de tests")
        
        return recommendations
    
    def _auto_detect_services(self) -> List[str]:
        """Detecta automáticamente los microservicios en el repositorio"""
        services = []
        
        # Verificar si el directorio actual es un microservicio
        if self._is_microservice_directory(self.base_path):
            services.append(".")
        
        # Buscar directorios que podrían ser microservicios
        for item in self.base_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                if self._is_microservice_directory(item):
                    services.append(item.name)
        
        return services
    
    def _is_microservice_directory(self, directory: Path) -> bool:
        """Verifica si un directorio tiene la estructura de microservicio según la plantilla"""
        # Verificar si tiene al menos un archivo requerido obligatorio
        for required_file in self.template.required_files:
            if required_file.required:
                if (directory / required_file.name).exists():
                    return True
        
        return False
    
    def _create_error_report(self, service_path: str, error_message: str) -> MicroserviceStructureReport:
        """Crea un reporte de error para servicios problemáticos"""
        return MicroserviceStructureReport(
            service=service_path,
            path=service_path,
            structure_checks=StructureChecks(
                Dockerfile=False,
                docker_compose_yml=False,
                gitignore=False,
                tests_dir_exists=False,
                tests_dir_has_files=False
            ),
            config_quality=ConfigQuality(
                dockerfile_best_practices=[f"Error: {error_message}"],
                compose_warnings=[],
                gitignore_warnings=[],
                tests_warnings=[]
            ),
            status=StructureStatus.POOR,
            score=0.0,
            recommendations=[f"Resolver error: {error_message}"]
        )
    
    def reload_template(self) -> None:
        """Recarga la plantilla desde el archivo"""
        self.template_loader.reload_templates()
        self.template = self.template_loader.get_template()
        self.scoring_config = self.template_loader.get_scoring_config()
        
        # Actualizar patrones
        self.dockerfile_patterns = self._get_dockerfile_patterns()
        self.compose_patterns = self._get_compose_patterns()
        self.gitignore_patterns = self._get_gitignore_patterns()
        self.test_patterns = self._get_test_patterns()
    
    def get_template_info(self) -> Dict[str, Any]:
        """Obtiene información de la plantilla actual"""
        return self.template_loader.get_template_info()


# Funciones de conveniencia para uso directo
def inspect_microservice_structure(service_path: str, base_path: str = ".", template_path: str = None) -> MicroserviceStructureReport:
    """
    Inspecciona la estructura de un microservicio específico
    
    Args:
        service_path: Ruta al microservicio
        base_path: Ruta base del repositorio
        template_path: Ruta opcional al archivo de plantilla
        
    Returns:
        Reporte de la estructura del microservicio
    """
    inspector = BaseStructureInspector(base_path, template_path)
    return inspector.inspect_microservice(service_path)


def inspect_repository_structure(base_path: str = ".", service_paths: List[str] = None, template_path: str = None) -> RepositoryStructureAudit:
    """
    Inspecciona la estructura de todos los microservicios en el repositorio
    
    Args:
        base_path: Ruta base del repositorio
        service_paths: Lista opcional de rutas de microservicios
        template_path: Ruta opcional al archivo de plantilla
        
    Returns:
        Auditoría completa de la estructura del repositorio
    """
    inspector = BaseStructureInspector(base_path, template_path)
    return inspector.inspect_repository(service_paths) 