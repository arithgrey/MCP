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
    RepositoryStructureAudit,
    ArchitectureAnalysis,
    ArchitecturePrinciple,
    PrincipleViolation,
    TODOAction
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
    # Resolver rutas de manera más robusta
    from pathlib import Path
    current_dir = Path.cwd()
    
    # Si service_path es relativo, resolverlo desde current_dir
    if not Path(service_path).is_absolute():
        resolved_service_path = (current_dir / service_path).resolve()
    else:
        resolved_service_path = Path(service_path)
    
    # Si base_path es ".", usar el directorio del servicio
    if base_path == ".":
        resolved_base_path = resolved_service_path.parent
    else:
        resolved_base_path = Path(base_path)
    
    # Crear inspector con la ruta base resuelta
    inspector = BaseStructureInspector(str(resolved_base_path), template_path)
    
    # Usar solo el nombre del directorio del servicio para el análisis
    service_name = resolved_service_path.name
    return inspector.inspect_microservice(service_name)


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


class AdvancedArchitectureInspector:
    """Inspector avanzado de arquitectura para microservicios con perfil de arquitecto senior"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        
        # Patrones para detección de violaciones
        self.dry_patterns = {
            "duplicate_functions": r"def\s+(\w+)\s*\([^)]*\):",
            "duplicate_classes": r"class\s+(\w+)",
            "duplicate_imports": r"from\s+(\w+)\s+import\s+(\w+)",
            "duplicate_constants": r"(\w+)\s*=\s*['\"][^'\"]*['\"]",
            "duplicate_config": r"(\w+):\s*['\"][^'\"]*['\"]"
        }
        
        self.tdd_patterns = {
            "test_files": r"test_.*\.py$|.*_test\.py$",
            "test_methods": r"def\s+test_\w+",
            "test_imports": r"import\s+pytest|from\s+pytest",
            "test_config": r"pytest\.ini|pyproject\.toml|setup\.cfg"
        }
        
        self.integration_patterns = {
            "integration_test_files": r"test_.*integration.*\.py$|.*integration.*test\.py$",
            "integration_markers": r"@pytest\.mark\.integration|@integration|@e2e",
            "docker_compose_tests": r"docker-compose.*test|docker-compose.*integration",
            "test_databases": r"test.*db|test.*database|test.*postgres|test.*mysql"
        }
        
        self.faker_patterns = {
            "faker_imports": r"from\s+faker\s+import|import\s+faker",
            "faker_usage": r"Faker\(\)|faker\.",
            "fake_data_generators": r"fake_|generate_|create_",
            "test_fixtures": r"@pytest\.fixture|def\s+fake_|def\s+generate_"
        }
        
        self.scalability_patterns = {
            "async_await": r"async\s+def|await\s+",
            "connection_pooling": r"pool|connection_pool|max_connections",
            "caching": r"cache|redis|memcached|@lru_cache",
            "load_balancing": r"load_balancer|round_robin|least_connections",
            "horizontal_scaling": r"replicas|instances|scale|kubernetes|docker_swarm",
            "microservices_patterns": r"service_discovery|api_gateway|circuit_breaker"
        }
    
    def analyze_microservice_architecture(self, service_path: str) -> ArchitectureAnalysis:
        """
        Realiza un análisis completo de arquitectura del microservicio
        
        Args:
            service_path: Ruta al microservicio
            
        Returns:
            Análisis completo de arquitectura
        """
        full_path = self.base_path / service_path
        
        if not full_path.exists():
            raise ValueError(f"El directorio {service_path} no existe")
        
        # Análisis de cada principio
        drp_compliance = self._analyze_dry_compliance(full_path)
        tdd_implementation = self._analyze_tdd_implementation(full_path)
        integration_tests = self._analyze_integration_tests(full_path)
        faker_data_usage = self._analyze_faker_usage(full_path)
        scalability_features = self._analyze_scalability_features(full_path)
        
        # Detectar violaciones
        violations = self._detect_architecture_violations(full_path)
        
        # Calcular métricas de violaciones
        total_violations = len(violations)
        critical_violations = len([v for v in violations if v.severity == "CRITICAL"])
        high_violations = len([v for v in violations if v.severity == "HIGH"])
        medium_violations = len([v for v in violations if v.severity == "MEDIUM"])
        low_violations = len([v for v in violations if v.severity == "LOW"])
        
        # Calcular score de arquitectura
        architecture_score = self._calculate_architecture_score(
            drp_compliance, tdd_implementation, integration_tests, 
            faker_data_usage, scalability_features, total_violations
        )
        
        # Determinar estado de arquitectura
        architecture_status = self._determine_architecture_status(architecture_score)
        
        return ArchitectureAnalysis(
            drp_compliance=drp_compliance,
            tdd_implementation=tdd_implementation,
            integration_tests=integration_tests,
            faker_data_usage=faker_data_usage,
            scalability_features=scalability_features,
            violations=violations,
            total_violations=total_violations,
            critical_violations=critical_violations,
            high_violations=high_violations,
            medium_violations=medium_violations,
            low_violations=low_violations,
            architecture_score=architecture_score,
            architecture_status=architecture_status
        )
    
    def _analyze_dry_compliance(self, service_path: Path) -> bool:
        """Analiza el cumplimiento del principio DRY"""
        python_files = list(service_path.rglob("*.py"))
        
        if not python_files:
            return False
        
        # Buscar duplicaciones en funciones, clases, imports, etc.
        function_names = []
        class_names = []
        import_patterns = []
        
        for py_file in python_files:
            try:
                content = py_file.read_text()
                
                # Extraer nombres de funciones
                import re
                functions = re.findall(self.dry_patterns["duplicate_functions"], content)
                function_names.extend(functions)
                
                # Extraer nombres de clases
                classes = re.findall(self.dry_patterns["duplicate_classes"], content)
                class_names.extend(classes)
                
                # Extraer patrones de import
                imports = re.findall(self.dry_patterns["duplicate_imports"], content)
                import_patterns.extend(imports)
                
            except Exception:
                continue
        
        # Verificar duplicaciones
        duplicate_functions = len(function_names) != len(set(function_names))
        duplicate_classes = len(class_names) != len(set(class_names))
        duplicate_imports = len(import_patterns) != len(set(import_patterns))
        
        # Si hay duplicaciones significativas, no cumple DRY
        return not (duplicate_functions or duplicate_classes or duplicate_imports)
    
    def _analyze_tdd_implementation(self, service_path: Path) -> bool:
        """Analiza la implementación de TDD"""
        # Verificar existencia de archivos de test
        test_files = list(service_path.rglob("test_*.py")) + list(service_path.rglob("*_test.py"))
        
        if not test_files:
            return False
        
        # Verificar que los tests estén en el directorio correcto
        tests_dir = service_path / "tests"
        has_tests_dir = tests_dir.exists() and tests_dir.is_dir()
        
        # Verificar configuración de pytest
        pytest_config = (
            (service_path / "pytest.ini").exists() or
            (service_path / "pyproject.toml").exists() or
            (service_path / "setup.cfg").exists()
        )
        
        # Verificar que haya métodos de test
        has_test_methods = False
        for test_file in test_files[:3]:  # Revisar solo los primeros 3 archivos
            try:
                content = test_file.read_text()
                if re.search(self.tdd_patterns["test_methods"], content):
                    has_test_methods = True
                    break
            except Exception:
                continue
        
        return has_tests_dir and pytest_config and has_test_methods
    
    def _analyze_integration_tests(self, service_path: Path) -> bool:
        """Analiza la existencia de pruebas de integración"""
        # Buscar archivos de test de integración
        integration_test_files = list(service_path.rglob("*integration*.py"))
        
        # Buscar en directorio de tests
        tests_dir = service_path / "tests"
        if tests_dir.exists():
            integration_test_files.extend(list(tests_dir.rglob("*integration*.py")))
        
        # Verificar marcadores de integración
        has_integration_markers = False
        for test_file in integration_test_files:
            try:
                content = test_file.read_text()
                if re.search(self.integration_patterns["integration_markers"], content):
                    has_integration_markers = True
                    break
            except Exception:
                continue
        
        # Verificar configuración de docker-compose para tests
        docker_compose_files = list(service_path.rglob("docker-compose*.yml"))
        has_test_compose = False
        for compose_file in docker_compose_files:
            try:
                content = compose_file.read_text()
                if re.search(self.integration_patterns["docker_compose_tests"], content):
                    has_test_compose = True
                    break
            except Exception:
                continue
        
        return len(integration_test_files) > 0 or has_integration_markers or has_test_compose
    
    def _analyze_faker_usage(self, service_path: Path) -> bool:
        """Analiza el uso de Faker para datos de prueba"""
        python_files = list(service_path.rglob("*.py"))
        
        if not python_files:
            return False
        
        # Verificar imports de Faker
        has_faker_imports = False
        has_faker_usage = False
        
        for py_file in python_files:
            try:
                content = py_file.read_text()
                
                if re.search(self.faker_patterns["faker_imports"], content):
                    has_faker_imports = True
                
                if re.search(self.faker_patterns["faker_usage"], content):
                    has_faker_usage = True
                
                if has_faker_imports and has_faker_usage:
                    break
                    
            except Exception:
                continue
        
        return has_faker_imports and has_faker_usage
    
    def _analyze_scalability_features(self, service_path: Path) -> bool:
        """Analiza las características de escalabilidad"""
        python_files = list(service_path.rglob("*.py"))
        yaml_files = list(service_path.rglob("*.yml")) + list(service_path.rglob("*.yaml"))
        
        if not python_files and not yaml_files:
            return False
        
        # Verificar características de escalabilidad en código Python
        has_async = False
        has_caching = False
        has_pooling = False
        
        for py_file in python_files:
            try:
                content = py_file.read_text()
                
                if re.search(self.scalability_patterns["async_await"], content):
                    has_async = True
                
                if re.search(self.scalability_patterns["caching"], content):
                    has_caching = True
                
                if re.search(self.scalability_patterns["connection_pooling"], content):
                    has_pooling = True
                
            except Exception:
                continue
        
        # Verificar características en archivos de configuración
        has_scaling_config = False
        for yaml_file in yaml_files:
            try:
                content = yaml_file.read_text()
                
                if re.search(self.scalability_patterns["horizontal_scaling"], content):
                    has_scaling_config = True
                    break
                    
            except Exception:
                continue
        
        # Se considera escalable si tiene al menos 2 características
        scalability_features_count = sum([has_async, has_caching, has_pooling, has_scaling_config])
        return scalability_features_count >= 2
    
    def _detect_architecture_violations(self, service_path: Path) -> List[PrincipleViolation]:
        """Detecta violaciones de principios de arquitectura"""
        violations = []
        
        # Violaciones de DRY
        if not self._analyze_dry_compliance(service_path):
            violations.append(PrincipleViolation(
                principle=ArchitecturePrinciple.DRY,
                severity="HIGH",
                description="Detectadas duplicaciones en código que violan el principio DRY",
                recommendation="Refactorizar código duplicado en funciones/clases reutilizables"
            ))
        
        # Violaciones de TDD
        if not self._analyze_tdd_implementation(service_path):
            violations.append(PrincipleViolation(
                principle=ArchitecturePrinciple.TDD,
                severity="CRITICAL",
                description="No se implementa Test Driven Development",
                recommendation="Implementar TDD con estructura de tests adecuada y configuración de pytest"
            ))
        
        # Violaciones de pruebas de integración
        if not self._analyze_integration_tests(service_path):
            violations.append(PrincipleViolation(
                principle=ArchitecturePrinciple.INTEGRATION_TESTS,
                severity="HIGH",
                description="Faltan pruebas de integración",
                recommendation="Agregar pruebas de integración con marcadores apropiados y configuración de test"
            ))
        
        # Violaciones de uso de Faker
        if not self._analyze_faker_usage(service_path):
            violations.append(PrincipleViolation(
                principle=ArchitecturePrinciple.FAKER_DATA,
                severity="MEDIUM",
                description="No se utiliza Faker para generar datos de prueba realistas",
                recommendation="Integrar Faker para generar datos de prueba variados y realistas"
            ))
        
        # Violaciones de escalabilidad
        if not self._analyze_scalability_features(service_path):
            violations.append(PrincipleViolation(
                principle=ArchitecturePrinciple.SCALABILITY,
                severity="MEDIUM",
                description="Faltan características de escalabilidad",
                recommendation="Implementar patrones de escalabilidad como async/await, caching, connection pooling"
            ))
        
        return violations
    
    def _calculate_architecture_score(self, drp: bool, tdd: bool, integration: bool, 
                                    faker: bool, scalability: bool, violations: int) -> float:
        """Calcula el score de arquitectura"""
        base_score = 0.0
        
        # Puntos por cada principio cumplido
        if drp:
            base_score += 20.0
        if tdd:
            base_score += 25.0
        if integration:
            base_score += 20.0
        if faker:
            base_score += 15.0
        if scalability:
            base_score += 20.0
        
        # Penalización por violaciones
        violation_penalty = violations * 5.0
        
        return max(0.0, base_score - violation_penalty)
    
    def _determine_architecture_status(self, score: float) -> str:
        """Determina el estado de la arquitectura basado en el score"""
        if score >= 80.0:
            return "EXCELLENT"
        elif score >= 60.0:
            return "GOOD"
        elif score >= 40.0:
            return "FAIR"
        elif score >= 20.0:
            return "POOR"
        else:
            return "CRITICAL"
    
    def generate_todo_actions(self, architecture_analysis: ArchitectureAnalysis, 
                             service_path: str) -> List[TODOAction]:
        """Genera un plan de acciones TODO para mejorar la arquitectura"""
        todo_actions = []
        
        # Acciones para DRY
        if not architecture_analysis.drp_compliance:
            todo_actions.append(TODOAction(
                priority="HIGH",
                principle=ArchitecturePrinciple.DRY,
                action="Refactorizar código duplicado",
                description="Identificar y consolidar funciones, clases e imports duplicados",
                estimated_effort="1-2 days",
                dependencies=[],
                files_to_modify=["src/", "tests/"]
            ))
        
        # Acciones para TDD
        if not architecture_analysis.tdd_implementation:
            todo_actions.append(TODOAction(
                priority="CRITICAL",
                principle=ArchitecturePrinciple.TDD,
                action="Implementar Test Driven Development",
                description="Crear estructura de tests, configurar pytest y escribir tests unitarios",
                estimated_effort="1 week",
                dependencies=[],
                files_to_modify=["tests/", "pytest.ini", "pyproject.toml"]
            ))
        
        # Acciones para pruebas de integración
        if not architecture_analysis.integration_tests:
            todo_actions.append(TODOAction(
                priority="HIGH",
                principle=ArchitecturePrinciple.INTEGRATION_TESTS,
                action="Agregar pruebas de integración",
                description="Crear tests de integración con marcadores apropiados y configuración de test",
                estimated_effort="3-5 days",
                dependencies=["TDD implementation"],
                files_to_modify=["tests/integration/", "docker-compose.test.yml"]
            ))
        
        # Acciones para Faker
        if not architecture_analysis.faker_data_usage:
            todo_actions.append(TODOAction(
                priority="MEDIUM",
                principle=ArchitecturePrinciple.FAKER_DATA,
                action="Integrar Faker para datos de prueba",
                description="Instalar Faker y crear generadores de datos de prueba realistas",
                estimated_effort="1-2 days",
                dependencies=["TDD implementation"],
                files_to_modify=["requirements.txt", "tests/fixtures/", "tests/conftest.py"]
            ))
        
        # Acciones para escalabilidad
        if not architecture_analysis.scalability_features:
            todo_actions.append(TODOAction(
                priority="MEDIUM",
                principle=ArchitecturePrinciple.SCALABILITY,
                action="Implementar características de escalabilidad",
                description="Agregar patrones de escalabilidad como async/await, caching, connection pooling",
                estimated_effort="1 week",
                dependencies=["TDD implementation"],
                files_to_modify=["src/", "docker-compose.yml", "kubernetes/"]
            ))
        
        # Ordenar por prioridad
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        todo_actions.sort(key=lambda x: priority_order.get(x.priority, 4))
        
        return todo_actions
    
    def save_todo_md_file(self, service_path: str, architecture_analysis: ArchitectureAnalysis, 
                          todo_actions: List[TODOAction], structure_report: MicroserviceStructureReport,
                          base_path: str = ".") -> str:
        """
        Genera y guarda el archivo TODO.md con el plan de acciones
        
        Args:
            service_path: Ruta del microservicio
            architecture_analysis: Análisis de arquitectura
            todo_actions: Lista de acciones TODO
            structure_report: Reporte de estructura básica
            base_path: Ruta base del repositorio
            
        Returns:
            Ruta del archivo TODO.md generado
        """
        service_full_path = Path(base_path) / service_path
        
        # Crear directorio TODO si no existe
        todo_dir = service_full_path / "TODO"
        todo_dir.mkdir(exist_ok=True)
        
        # Obtener nombre del servicio desde la ruta
        service_name = Path(service_path).name if service_path != "." else Path(base_path).name
        
        # Crear nombre del archivo con formato todo_nombre_servicio.md
        todo_filename = f"todo_{service_name}.md"
        todo_file_path = todo_dir / todo_filename
        
        # Calcular score general
        overall_score = (structure_report.score + architecture_analysis.architecture_score) / 2
        
        # Determinar estado general
        if overall_score >= 80:
            overall_status = "EXCELLENT"
        elif overall_score >= 60:
            overall_status = "GOOD"
        elif overall_score >= 40:
            overall_status = "FAIR"
        elif overall_score >= 20:
            overall_status = "POOR"
        else:
            overall_status = "CRITICAL"
        
        # Generar contenido del archivo TODO.md
        todo_content = f"""# TODO.md - Plan de Mejoras de Arquitectura

## 📊 Resumen Ejecutivo

**Microservicio**: `{service_path}`  
**Fecha de Análisis**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Estado General**: {overall_status}  
**Score General**: {overall_score:.1f}/100

### 📈 Métricas de Calidad
- **Score de Estructura**: {structure_report.score:.1f}/100
- **Score de Arquitectura**: {architecture_analysis.architecture_score:.1f}/100
- **Total de Violaciones**: {architecture_analysis.total_violations}

## 🏗️ Análisis de Principios de Arquitectura

### ✅ Principios que CUMPLEN
"""
        
        # Agregar principios que cumplen
        if architecture_analysis.drp_compliance:
            todo_content += "- **DRY** (Don't Repeat Yourself): ✅ CUMPLE\n"
        if architecture_analysis.tdd_implementation:
            todo_content += "- **TDD** (Test Driven Development): ✅ CUMPLE\n"
        if architecture_analysis.integration_tests:
            todo_content += "- **Pruebas de Integración**: ✅ CUMPLE\n"
        if architecture_analysis.faker_data_usage:
            todo_content += "- **Datos Faker**: ✅ CUMPLE\n"
        if architecture_analysis.scalability_features:
            todo_content += "- **Escalabilidad**: ✅ CUMPLE\n"
        
        # Agregar principios que NO cumplen
        todo_content += "\n### ❌ Principios que NO CUMPLEN (Requieren Acción)\n"
        
        if not architecture_analysis.drp_compliance:
            todo_content += "- **DRY** (Don't Repeat Yourself): ❌ VIOLACIÓN\n"
        if not architecture_analysis.tdd_implementation:
            todo_content += "- **TDD** (Test Driven Development): ❌ VIOLACIÓN\n"
        if not architecture_analysis.integration_tests:
            todo_content += "- **Pruebas de Integración**: ❌ VIOLACIÓN\n"
        if not architecture_analysis.faker_data_usage:
            todo_content += "- **Datos Faker**: ❌ VIOLACIÓN\n"
        if not architecture_analysis.scalability_features:
            todo_content += "- **Escalabilidad**: ❌ VIOLACIÓN\n"
        
        # Detalle de violaciones
        if architecture_analysis.violations:
            todo_content += f"""
## ⚠️ Detalle de Violaciones Detectadas

Total de Violaciones: {architecture_analysis.total_violations}
- **Críticas**: {architecture_analysis.critical_violations}
- **Altas**: {architecture_analysis.high_violations}
- **Medias**: {architecture_analysis.medium_violations}
- **Bajas**: {architecture_analysis.low_violations}

"""
            
            for i, violation in enumerate(architecture_analysis.violations, 1):
                todo_content += f"""### {i}. [{violation.severity}] {violation.principle.value}

**Descripción**: {violation.description}  
**Recomendación**: {violation.recommendation}

"""
        
        # Plan de acciones TODO
        todo_content += f"""## 📝 Plan de Acciones TODO

### 🎯 Acciones Prioritarias (Ordenadas por Prioridad)

"""
        
        # Agrupar acciones por prioridad
        priority_groups = {
            "CRITICAL": [],
            "HIGH": [],
            "MEDIUM": [],
            "LOW": []
        }
        
        for action in todo_actions:
            priority_groups[action.priority].append(action)
        
        # Generar contenido por prioridad
        for priority in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            actions = priority_groups[priority]
            if actions:
                priority_emoji = {"CRITICAL": "🚨", "HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
                todo_content += f"#### {priority_emoji[priority]} {priority}\n\n"
                
                for i, action in enumerate(actions, 1):
                    todo_content += f"""**{i}. {action.action}**

**Descripción**: {action.description}  
**Esfuerzo Estimado**: {action.estimated_effort}  
**Archivos a Modificar**: {', '.join(action.files_to_modify)}

"""
                    
                    if action.dependencies:
                        todo_content += f"**Dependencias**: {', '.join(action.dependencies)}\n\n"
                    else:
                        todo_content += "\n"
        
        # Historias de usuario
        todo_content += """## 📋 Historias de Usuario para Desarrolladores

### 🎭 Formato de Historia de Usuario

Para cada acción, sigue este formato:

```
Como [rol]
Quiero [funcionalidad]
Para [beneficio]

**Criterios de Aceptación:**
- [ ] Criterio 1
- [ ] Criterio 2
- [ ] Criterio 3

**Estimación**: [tiempo]
**Prioridad**: [CRITICAL/HIGH/MEDIUM/LOW]
```

### 📚 Ejemplos de Historias

#### Ejemplo 1: Implementar TDD
```
Como desarrollador
Quiero implementar Test Driven Development
Para asegurar la calidad del código y facilitar el mantenimiento

**Criterios de Aceptación:**
- [ ] Crear directorio tests/ con estructura adecuada
- [ ] Configurar pytest.ini o pyproject.toml
- [ ] Escribir tests unitarios para funciones existentes
- [ ] Los tests deben pasar al ejecutar pytest

**Estimación**: 1 semana
**Prioridad**: CRITICAL
```

#### Ejemplo 2: Refactorizar Código Duplicado
```
Como desarrollador
Quiero refactorizar código duplicado
Para mejorar la mantenibilidad y reducir la duplicación

**Criterios de Aceptación:**
- [ ] Identificar funciones/clases duplicadas
- [ ] Crear funciones/clases reutilizables
- [ ] Actualizar imports y referencias
- [ ] Verificar que no se rompa funcionalidad existente

**Estimación**: 1-2 días
**Prioridad**: HIGH
```

## 🚀 Próximos Pasos

1. **Revisar acciones CRITICAL** primero
2. **Implementar en orden de prioridad**
3. **Verificar cumplimiento** de cada principio
4. **Actualizar este archivo** con el progreso
5. **Ejecutar análisis nuevamente** para verificar mejoras

## 📞 Soporte

Para dudas sobre la implementación:
- Revisar documentación de cada principio
- Consultar con el equipo de arquitectura
- Usar herramientas de análisis de código estático

---
*Archivo generado automáticamente por MCP Advanced Architecture Inspector*
"""
        
        # Guardar archivo
        try:
            todo_file_path.write_text(todo_content, encoding='utf-8')
            return str(todo_file_path)
        except Exception as e:
            raise Exception(f"No se pudo guardar el archivo TODO.md: {e}")


# Función de conveniencia para análisis avanzado
def analyze_microservice_architecture_advanced(service_path: str, base_path: str = ".") -> ArchitectureAnalysis:
    """
    Analiza la arquitectura de un microservicio con perfil de arquitecto senior
    
    Args:
        service_path: Ruta al microservicio
        base_path: Ruta base del repositorio
        
    Returns:
        Análisis completo de arquitectura
    """
    # Resolver rutas de manera más robusta
    from pathlib import Path
    current_dir = Path.cwd()
    
    # Si service_path es relativo, resolverlo desde current_dir
    if not Path(service_path).is_absolute():
        resolved_service_path = (current_dir / service_path).resolve()
    else:
        resolved_service_path = Path(service_path)
    
    # Si base_path es ".", usar el directorio del servicio
    if base_path == ".":
        resolved_base_path = resolved_service_path.parent
    else:
        resolved_base_path = Path(base_path)
    
    # Crear inspector con la ruta base resuelta
    inspector = AdvancedArchitectureInspector(str(resolved_base_path))
    
    # Usar solo el nombre del directorio del servicio para el análisis
    service_name = resolved_service_path.name
    return inspector.analyze_microservice_architecture(service_name)


def generate_architecture_todo_plan(service_path: str, base_path: str = ".") -> List[TODOAction]:
    """
    Genera un plan de acciones TODO para mejorar la arquitectura
    
    Args:
        service_path: Ruta al microservicio
        base_path: Ruta base del repositorio
        
    Returns:
        Lista de acciones TODO ordenadas por prioridad
    """
    # Resolver rutas de manera más robusta
    from pathlib import Path
    current_dir = Path.cwd()
    
    # Si service_path es relativo, resolverlo desde current_dir
    if not Path(service_path).is_absolute():
        resolved_service_path = (current_dir / service_path).resolve()
    else:
        resolved_service_path = Path(service_path)
    
    # Si base_path es ".", usar el directorio del servicio
    if base_path == ".":
        resolved_base_path = resolved_service_path.parent
    else:
        resolved_base_path = Path(base_path)
    
    # Crear inspector con la ruta base resuelta
    inspector = AdvancedArchitectureInspector(str(resolved_base_path))
    
    # Usar solo el nombre del directorio del servicio para el análisis
    service_name = resolved_service_path.name
    analysis = inspector.analyze_microservice_architecture(service_name)
    return inspector.generate_todo_actions(analysis, service_name)


def generate_and_save_todo_md(service_path: str, base_path: str = ".") -> str:
    """
    Genera y guarda el archivo TODO.md con el plan de acciones
    
    Args:
        service_path: Ruta al microservicio
        base_path: Ruta base del repositorio
        
    Returns:
        Ruta del archivo TODO.md generado
    """
    # Resolver rutas de manera más robusta
    from pathlib import Path
    current_dir = Path.cwd()
    
    # Si service_path es relativo, resolverlo desde current_dir
    if not Path(service_path).is_absolute():
        resolved_service_path = (current_dir / service_path).resolve()
    else:
        resolved_service_path = Path(service_path)
    
    # Si base_path es ".", usar el directorio del servicio
    if base_path == ".":
        resolved_base_path = resolved_service_path.parent
    else:
        resolved_base_path = Path(base_path)
    
    # Crear inspector con la ruta base resuelta
    inspector = AdvancedArchitectureInspector(str(resolved_base_path))
    
    # Usar solo el nombre del directorio del servicio para el análisis
    service_name = resolved_service_path.name
    
    # Obtener análisis de estructura básica
    from .structure_inspector import inspect_microservice_structure
    structure_report = inspect_microservice_structure(service_path, base_path)
    
    # Obtener análisis de arquitectura
    architecture_analysis = inspector.analyze_microservice_architecture(service_name)
    
    # Generar plan TODO
    todo_actions = inspector.generate_todo_actions(architecture_analysis, service_name)
    
    # Guardar archivo TODO.md
    return inspector.save_todo_md_file(service_name, architecture_analysis, todo_actions, structure_report, str(resolved_base_path)) 