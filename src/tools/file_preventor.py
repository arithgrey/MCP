"""
Motor de prevención de archivos no permitidos
Previene la creación de Makefiles y scripts .sh no autorizados
"""
import re
from pathlib import Path
from typing import List, Tuple, Optional
from src.core.models import FilePreventionRule, FileCreationPolicy


class FilePreventor:
    """Preventor de archivos no permitidos según las reglas de la plantilla"""
    
    def __init__(self, file_prevention: FileCreationPolicy):
        self.file_prevention = file_prevention
    
    def can_create_file(self, file_path: Path, service_path: Path) -> Tuple[bool, str, List[str]]:
        """
        Verifica si se puede crear un archivo según las reglas de prevención
        
        Args:
            file_path: Ruta del archivo a verificar
            service_path: Ruta del microservicio
            
        Returns:
            (permitido, mensaje_error, alternativas_recomendadas)
        """
        filename = file_path.name
        
        # Verificar Makefiles
        if self._is_makefile(filename):
            rule = self.file_prevention.makefiles
            if not rule.enabled:
                return True, "", []
            
            return False, rule.error_message, rule.alternatives
        
        # Verificar Scripts .sh
        if self._is_shell_script(filename):
            rule = self.file_prevention.shell_scripts
            if not rule.enabled:
                return True, "", []
            
            # Verificar si es una excepción permitida
            if self._is_legitimate_django_entrypoint(file_path, service_path, rule):
                return True, "", []
            
            return False, rule.error_message, rule.alternatives
        
        # Verificar rutas relativas problemáticas
        if self._has_problematic_relative_paths(file_path, service_path):
            rule = self.file_prevention.path_prevention
            if not rule.enabled:
                return True, "", []
            
            return False, rule.error_message, rule.alternatives
        
        # Verificar otras reglas restringidas
        for other_rule in self.file_prevention.other_restricted:
            if not other_rule.enabled:
                continue
            
            if self._matches_pattern(filename, other_rule.blocked_patterns):
                return False, other_rule.error_message, other_rule.alternatives
        
        return True, "", []
    
    def _is_makefile(self, filename: str) -> bool:
        """Verifica si el archivo es un Makefile"""
        makefile_patterns = [
            r"^[Mm]akefile$",
            r"^[Mm]akefile\..*$",
            r"^[Gg][Nn][Uu][Mm]akefile$"
        ]
        
        return any(re.match(pattern, filename) for pattern in makefile_patterns)
    
    def _is_shell_script(self, filename: str) -> bool:
        """Verifica si el archivo es un script shell"""
        return filename.endswith('.sh')
    
    def _matches_pattern(self, filename: str, patterns: List[str]) -> bool:
        """Verifica si el nombre del archivo coincide con algún patrón"""
        for pattern in patterns:
            if pattern.startswith('*'):
                # Patrón glob simple
                if filename.endswith(pattern[1:]):
                    return True
            elif '*' in pattern:
                # Patrón glob con comodín en medio
                regex_pattern = pattern.replace('*', '.*')
                if re.match(regex_pattern, filename):
                    return True
            else:
                # Patrón exacto
                if filename == pattern:
                    return True
        
        return False
    
    def _is_legitimate_django_entrypoint(self, file_path: Path, service_path: Path, rule: FilePreventionRule) -> bool:
        """
        Verifica si un entrypoint.sh es legítimo para un microservicio Django
        
        Args:
            file_path: Ruta del archivo entrypoint.sh
            rule: Regla de prevención para scripts shell
            
        Returns:
            True si es un entrypoint.sh legítimo para Django
        """
        # Verificar que esté en la raíz del microservicio
        if file_path.parent != service_path:
            return False
        
        # Verificar que sea entrypoint.sh (no otro .sh)
        if file_path.name != "entrypoint.sh":
            return False
        
        # Verificar que esté en la lista de excepciones permitidas
        if "entrypoint.sh" not in rule.allowed_exceptions:
            return False
        
        # Verificar que el microservicio tenga estructura Django
        django_indicators = rule.django_microservice_patterns or [
            "manage.py",
            "app/settings.py",
            "app/wsgi.py",
            "app/asgi.py",
            "settings.py",
            "wsgi.py",
            "asgi.py"
        ]
        
        has_django_structure = any(
            (service_path / indicator).exists() 
            for indicator in django_indicators
        )
        
        return has_django_structure
    
    def _has_problematic_relative_paths(self, file_path: Path, service_path: Path) -> bool:
        """
        Verifica si el archivo contiene rutas relativas problemáticas
        
        Args:
            file_path: Ruta del archivo a verificar
            service_path: Ruta del microservicio
            
        Returns:
            True si contiene rutas relativas problemáticas
        """
        if not file_path.exists():
            return False
        
        try:
            content = file_path.read_text()
            
            # Verificar patrones de rutas relativas problemáticas
            rule = self.file_prevention.path_prevention
            if not rule.enabled:
                return False
            
            for pattern in rule.blocked_patterns:
                if pattern in content:
                    # Verificar si es una excepción permitida
                    if not self._is_allowed_relative_path(content, pattern, rule):
                        return True
            
            return False
            
        except Exception:
            # Si no se puede leer el archivo, no es problemático
            return False
    
    def _is_allowed_relative_path(self, content: str, pattern: str, rule) -> bool:
        """
        Verifica si una ruta relativa está permitida por las excepciones
        
        Args:
            content: Contenido del archivo
            pattern: Patrón detectado
            rule: Regla de prevención de rutas
            
        Returns:
            True si la ruta está permitida
        """
        for exception in rule.allowed_exceptions:
            if exception in content:
                return True
        
        return False
    
    def get_prevention_summary(self, service_path: Path) -> dict:
        """
        Obtiene un resumen de las reglas de prevención aplicadas
        
        Args:
            service_path: Ruta del microservicio
            
        Returns:
            Resumen de las reglas de prevención
        """
        return {
            "makefiles_blocked": self.file_prevention.makefiles.enabled,
            "shell_scripts_blocked": self.file_prevention.shell_scripts.enabled,
            "path_prevention_enabled": self.file_prevention.path_prevention.enabled,
            "other_rules_count": len(self.file_prevention.other_restricted),
            "django_patterns": self.file_prevention.shell_scripts.django_microservice_patterns,
            "makefile_alternatives": self.file_prevention.makefiles.alternatives,
            "shell_alternatives": self.file_prevention.shell_scripts.alternatives,
            "path_alternatives": self.file_prevention.path_prevention.alternatives
        }
    
    def validate_service_structure(self, service_path: Path) -> List[dict]:
        """
        Valida la estructura del servicio contra las reglas de prevención
        
        Args:
            service_path: Ruta del microservicio
            
        Returns:
            Lista de violaciones encontradas
        """
        violations = []
        
        for file_path in service_path.rglob("*"):
            if file_path.is_file():
                can_create, error_msg, alternatives = self.can_create_file(file_path, service_path)
                
                if not can_create:
                    violations.append({
                        "file_path": str(file_path.relative_to(service_path)),
                        "error_message": error_msg,
                        "alternatives": alternatives,
                        "severity": "high"
                    })
        
        return violations 