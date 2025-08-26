"""
Herramientas MCP para prevención de archivos no permitidos
"""
from pathlib import Path
from typing import Dict, List, Any
from src.tools.file_preventor import FilePreventor
from src.tools.template_loader import TemplateLoader


def prevent_makefile_creation(service_path: str) -> Dict[str, Any]:
    """
    Previene la creación de Makefiles en un microservicio
    
    Args:
        service_path: Ruta al microservicio
        
    Returns:
        Resultado de la prevención
    """
    service_path_obj = Path(service_path)
    
    if not service_path_obj.exists():
        return {
            "success": False,
            "error": f"El directorio {service_path} no existe",
            "prevention_applied": False
        }
    
    # Cargar plantilla y crear preventor
    template_loader = TemplateLoader()
    template = template_loader.get_template()
    
    if not hasattr(template, 'file_prevention') or not template.file_prevention:
        return {
            "success": False,
            "error": "No se encontraron reglas de prevención configuradas",
            "prevention_applied": False
        }
    
    file_preventor = FilePreventor(template.file_prevention)
    
    # Verificar si hay Makefiles existentes
    makefile_violations = []
    for file_path in service_path_obj.rglob("*"):
        if file_path.is_file() and file_path.name.lower() in ["makefile", "gnumakefile"]:
            can_create, error_msg, alternatives = file_preventor.can_create_file(file_path, service_path_obj)
            if not can_create:
                makefile_violations.append({
                    "file_path": str(file_path.relative_to(service_path_obj)),
                    "error_message": error_msg,
                    "alternatives": alternatives
                })
    
    # Obtener resumen de prevención
    prevention_summary = file_preventor.get_prevention_summary(service_path_obj)
    
    return {
        "success": True,
        "service_path": service_path,
        "makefiles_blocked": prevention_summary["makefiles_blocked"],
        "existing_violations": makefile_violations,
        "alternatives": prevention_summary["makefile_alternatives"],
        "prevention_applied": True,
        "message": "✅ Prevención de Makefiles activa para este microservicio"
    }


def audit_makefile_presence(base_path: str = ".") -> Dict[str, Any]:
    """
    Audita la presencia de Makefiles en todos los microservicios
    
    Args:
        base_path: Ruta base del repositorio
        
    Returns:
        Reporte de auditoría de Makefiles
    """
    base_path_obj = Path(base_path)
    
    if not base_path_obj.exists():
        return {
            "success": False,
            "error": f"El directorio {base_path} no existe"
        }
    
    # Cargar plantilla
    template_loader = TemplateLoader()
    template = template_loader.get_template()
    
    if not hasattr(template, 'file_prevention') or not template.file_prevention:
        return {
            "success": False,
            "error": "No se encontraron reglas de prevención configuradas"
        }
    
    file_preventor = FilePreventor(template.file_prevention)
    
    # Buscar todos los directorios que podrían ser microservicios
    microservices = []
    for item in base_path_obj.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            # Verificar si tiene estructura de microservicio
            if any([
                (item / "Dockerfile").exists(),
                (item / "docker-compose.yml").exists(),
                (item / "manage.py").exists(),
                (item / "package.json").exists()
            ]):
                microservices.append(item)
    
    # Auditar cada microservicio
    audit_results = []
    total_violations = 0
    
    for service in microservices:
        violations = file_preventor.validate_service_structure(service)
        makefile_violations = [v for v in violations if "Makefile" in v["file_path"] or "makefile" in v["file_path"]]
        
        audit_results.append({
            "service_name": service.name,
            "service_path": str(service),
            "makefile_violations": makefile_violations,
            "total_violations": len(violations),
            "has_makefiles": len(makefile_violations) > 0
        })
        
        total_violations += len(makefile_violations)
    
    return {
        "success": True,
        "base_path": base_path,
        "total_microservices": len(microservices),
        "total_makefile_violations": total_violations,
        "microservices": audit_results,
        "prevention_summary": {
            "makefiles_blocked": file_preventor.file_prevention.makefiles.enabled,
            "shell_scripts_blocked": file_preventor.file_prevention.shell_scripts.enabled
        }
    }


def suggest_alternatives(file_type: str, service_path: str = ".") -> Dict[str, Any]:
    """
    Sugiere alternativas para un tipo de archivo específico
    
    Args:
        file_type: Tipo de archivo ("makefile", "shell_script", "other")
        service_path: Ruta al microservicio
        
    Returns:
        Alternativas recomendadas
    """
    template_loader = TemplateLoader()
    template = template_loader.get_template()
    
    if not hasattr(template, 'file_prevention') or not template.file_prevention:
        return {
            "success": False,
            "error": "No se encontraron reglas de prevención configuradas"
        }
    
    file_prevention = template.file_prevention
    
    if file_type == "makefile":
        rule = file_prevention.makefiles
        alternatives = rule.alternatives
        error_message = rule.error_message
    elif file_type == "shell_script":
        rule = file_prevention.shell_scripts
        alternatives = rule.alternatives
        error_message = rule.error_message
    else:
        return {
            "success": False,
            "error": f"Tipo de archivo '{file_type}' no reconocido"
        }
    
    return {
        "success": True,
        "file_type": file_type,
        "error_message": error_message,
        "alternatives": alternatives,
        "service_path": service_path,
        "recommendation": f"Para {file_type}, considera usar: {', '.join(alternatives[:2])}"
    }


def get_prevention_status(service_path: str = ".") -> Dict[str, Any]:
    """
    Obtiene el estado actual de las reglas de prevención
    
    Args:
        service_path: Ruta al microservicio
        
    Returns:
        Estado de las reglas de prevención
    """
    template_loader = TemplateLoader()
    template = template_loader.get_template()
    
    if not hasattr(template, 'file_prevention') or not template.file_prevention:
        return {
            "success": False,
            "error": "No se encontraron reglas de prevención configuradas"
        }
    
    file_prevention = template.file_prevention
    
    return {
        "success": True,
        "service_path": service_path,
        "prevention_rules": {
            "makefiles": {
                "enabled": file_prevention.makefiles.enabled,
                "blocked_patterns": file_prevention.makefiles.blocked_patterns,
                "error_message": file_prevention.makefiles.error_message,
                "alternatives": file_prevention.makefiles.alternatives
            },
            "shell_scripts": {
                "enabled": file_prevention.shell_scripts.enabled,
                "blocked_patterns": file_prevention.shell_scripts.blocked_patterns,
                "allowed_exceptions": file_prevention.shell_scripts.allowed_exceptions,
                "django_patterns": file_prevention.shell_scripts.django_microservice_patterns,
                "error_message": file_prevention.shell_scripts.error_message,
                "alternatives": file_prevention.shell_scripts.alternatives
            },
            "path_prevention": {
                "enabled": file_prevention.path_prevention.enabled,
                "blocked_patterns": file_prevention.path_prevention.blocked_patterns,
                "allowed_exceptions": file_prevention.path_prevention.allowed_exceptions,
                "error_message": file_prevention.path_prevention.error_message,
                "alternatives": file_prevention.path_prevention.alternatives,
                "severity": file_prevention.path_prevention.severity
            }
        },
        "total_rules": len(file_prevention.other_restricted) + 3
    } 