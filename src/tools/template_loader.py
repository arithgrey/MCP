"""
Cargador de plantillas de configuración para el inspector de estructura
"""
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from src.core.template_models import TemplateConfig, StructureTemplate, ScoringConfig
from src.core.models import FilePreventionRule, FileCreationPolicy


class TemplateLoader:
    """Cargador de plantillas desde archivos YAML"""
    
    def __init__(self, template_path: str = None):
        if template_path is None:
            self.template_path = Path("src/config/structure_templates.yaml")
        else:
            self.template_path = Path(template_path)
        self._config: Optional[TemplateConfig] = None
    
    def load_templates(self) -> TemplateConfig:
        """Carga las plantillas desde el archivo YAML"""
        try:
            if not self.template_path.exists():
                print(f"Warning: Archivo de plantillas no encontrado en {self.template_path}")
                return self._create_default_config()
            
            with open(self.template_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
            
            # Cargar configuración de prevención de archivos primero
            file_prevention_data = data.get("file_prevention", {})
            file_prevention = None
            if file_prevention_data:
                from src.core.models import FilePreventionRule, FileCreationPolicy, PathPreventionRule
                
                # Crear reglas de prevención
                makefiles_data = file_prevention_data.get("makefiles", {})
                shell_scripts_data = file_prevention_data.get("shell_scripts", {})
                path_prevention_data = file_prevention_data.get("path_prevention", {})
                
                makefiles_rule = FilePreventionRule(**makefiles_data)
                shell_scripts_rule = FilePreventionRule(**shell_scripts_data)
                path_prevention_rule = PathPreventionRule(**path_prevention_data)
                
                file_prevention = FileCreationPolicy(
                    makefiles=makefiles_rule,
                    shell_scripts=shell_scripts_rule,
                    path_prevention=path_prevention_rule,
                    other_restricted=file_prevention_data.get("other_restricted", [])
                )
            
            # Cargar plantilla por defecto con file_prevention
            default_data = data.get("default", {})
            if file_prevention:
                default_data["file_prevention"] = file_prevention
            default_template = StructureTemplate(**default_data)
            
            # Cargar configuración de scoring
            scoring_data = data.get("scoring", {})
            scoring = ScoringConfig(**scoring_data)
            
            return TemplateConfig(
                default=default_template,
                scoring=scoring,
                file_prevention=file_prevention
            )
            
        except Exception as e:
            print(f"Warning: Error al cargar plantillas desde {self.template_path}: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> TemplateConfig:
        """Crea configuración por defecto si no se pueden cargar las plantillas"""
        from src.core.template_models import RequiredFile, FileQuality, QualityPattern
        
        # Reglas de prevención por defecto
        makefile_prevention = FilePreventionRule(
            file_type="makefile",
            enabled=True,
            blocked_patterns=["Makefile", "makefile", "GNUmakefile", "*.mk"],
            allowed_exceptions=[],
            django_microservice_patterns=[],
            error_message="❌ NO SE PERMITEN MAKEFILES en este proyecto",
            alternatives=[
                "docker-compose.yml para orquestación de servicios",
                "scripts/ para tareas personalizadas",
                "pyproject.toml para comandos Python"
            ]
        )
        
        shell_script_prevention = FilePreventionRule(
            file_type="shell_script",
            enabled=True,
            blocked_patterns=["*.sh"],
            allowed_exceptions=["entrypoint.sh"],
            django_microservice_patterns=[
                "manage.py", "app/settings.py", "app/wsgi.py", "app/asgi.py",
                "settings.py", "wsgi.py", "asgi.py"
            ],
            error_message="❌ NO SE PERMITEN SCRIPTS .SH excepto entrypoint.sh para microservicios Django",
            alternatives=[
                "Dockerfile para configuración de contenedor",
                "docker-compose.yml para orquestación",
                "requirements.txt para dependencias Python"
            ]
        )
        
        # Regla de prevención de rutas relativas problemáticas
        from src.core.models import PathPreventionRule
        path_prevention = PathPreventionRule(
            rule_type="relative_path",
            enabled=True,
            blocked_patterns=[
                "../", "./", "*/../*", "*/./*",
                "from ..", "from .", "import ..", "import ."
            ],
            allowed_exceptions=[
                "from . import",  # Imports relativos válidos dentro del mismo paquete
                "from .. import"  # Imports relativos válidos hacia paquetes padre
            ],
            error_message="❌ NO SE PERMITEN RUTAS RELATIVAS PROBLEMÁTICAS que salgan del contexto del proyecto",
            alternatives=[
                "Usa rutas absolutas desde la raíz del proyecto",
                "Usa imports absolutos: from src.tools import",
                "Usa variables de entorno para rutas dinámicas",
                "Usa pathlib.Path para manejo robusto de rutas",
                "Define rutas base en configuración centralizada"
            ],
            severity="critical"
        )
        
        file_prevention = FileCreationPolicy(
            makefiles=makefile_prevention,
            shell_scripts=shell_script_prevention,
            path_prevention=path_prevention,
            other_restricted=[]
        )
        
        # Plantilla por defecto
        default_template = StructureTemplate(
            name="Estándar Mínimo de Microservicios",
            description="Verificación de estructura básica obligatoria para microservicios",
            required_files=[
                RequiredFile(
                    name="Dockerfile",
                    description="Archivo de containerización",
                    required=True,
                    weight=20
                ),
                RequiredFile(
                    name="docker-compose.yml",
                    description="Archivo de orquestación",
                    required=True,
                    weight=20
                ),
                RequiredFile(
                    name=".gitignore",
                    description="Archivo de exclusión de Git",
                    required=True,
                    weight=15
                ),
                RequiredFile(
                    name="tests/",
                    description="Directorio de tests",
                    required=True,
                    weight=15,
                    type="directory",
                    must_contain=["*.py"]
                )
            ],
            dockerfile_quality=FileQuality(
                patterns=[
                    QualityPattern(
                        name="expose_port",
                        regex="EXPOSE\\s+\\d+",
                        description="Puerto expuesto correctamente",
                        weight=5,
                        required=False
                    ),
                    QualityPattern(
                        name="avoid_copy_all",
                        regex="COPY\\s+\\.\\s+\\.",
                        description="Evita COPY . . sin .dockerignore",
                        weight=-10,
                        required=False,
                        warning="uses COPY . . without .dockerignore"
                    )
                ]
            ),
            file_prevention=file_prevention
        )
        
        # Configuración de scoring por defecto
        scoring = ScoringConfig(
            base_weights={
                "required_file": 20,
                "optional_file": 10,
                "required_directory": 15,
                "optional_directory": 8
            },
            thresholds={
                "complete": 80,
                "incomplete": 50,
                "poor": 0
            },
            warning_penalty=2,
            bonus_features={
                "multi_stage_build": 10,
                "health_check": 8,
                "test_coverage": 5
            }
        )
        
        return TemplateConfig(
            default=default_template,
            scoring=scoring
        )
    
    def get_template(self) -> StructureTemplate:
        """Obtiene la plantilla por defecto"""
        if self._config is None:
            self._config = self.load_templates()
        
        return self._config.default
    
    def get_scoring_config(self) -> ScoringConfig:
        """Obtiene la configuración de scoring"""
        if self._config is None:
            self._config = self.load_templates()
        
        return self._config.scoring
    
    def reload_templates(self) -> None:
        """Recarga las plantillas desde el archivo"""
        self._config = None
        self.load_templates()
    
    def get_template_info(self) -> Dict[str, Any]:
        """Obtiene información de la plantilla actual"""
        template = self.get_template()
        
        return {
            "name": template.name,
            "description": template.description,
            "total_required_files": len([f for f in template.required_files if f.required]),
            "total_optional_files": len([f for f in template.required_files if not f.required]),
            "has_dockerfile_quality": template.dockerfile_quality is not None,
            "has_compose_quality": template.compose_quality is not None,
            "has_gitignore_quality": template.gitignore_quality is not None,
            "has_tests_quality": template.tests_quality is not None
        } 