"""
Configuración común para el MCP
Aplicando principio DRY para evitar duplicación
"""
from typing import Dict, Any
import yaml
from pathlib import Path


class CommonConfig:
    """Configuración común reutilizable"""
    
    # Valores por defecto
    DEFAULT_CONFIG = {
        "docker": {
            "default_service": "mcp-service",
            "network": "mcp-network",
            "timeout_seconds": 300
        },
        "pytest": {
            "default_command": "pytest",
            "coverage_args": "--cov=src --cov-report=html --cov-report=term-missing",
            "verbose_output": True,
            "parallel_workers": 4
        },
        "reports": {
            "html_dir": "test_reports",
            "junit_file": "junit.xml",
            "coverage_dir": "htmlcov"
        },
        "health_check": {
            "enabled": True,
            "endpoints": {
                "readiness": "/readiness",
                "liveness": "/liveness"
            },
            "timeout_ms": 5000
        }
    }
    
    @classmethod
    def load_yaml_config(cls, config_path: str) -> Dict[str, Any]:
        """Carga configuración desde archivo YAML con fallback a valores por defecto"""
        try:
            if Path(config_path).exists():
                with open(config_path, 'r') as file:
                    config = yaml.safe_load(file)
                    # Combinar con valores por defecto
                    return cls._merge_configs(cls.DEFAULT_CONFIG, config)
            else:
                return cls.DEFAULT_CONFIG.copy()
        except Exception:
            return cls.DEFAULT_CONFIG.copy()
    
    @staticmethod
    def _merge_configs(default: Dict[str, Any], custom: Dict[str, Any]) -> Dict[str, Any]:
        """Combina configuración personalizada con valores por defecto"""
        result = default.copy()
        
        def merge_dicts(d1: Dict[str, Any], d2: Dict[str, Any]) -> None:
            for key, value in d2.items():
                if key in d1 and isinstance(d1[key], dict) and isinstance(value, dict):
                    merge_dicts(d1[key], value)
                else:
                    d1[key] = value
        
        merge_dicts(result, custom)
        return result
    
    @classmethod
    def get_docker_config(cls, config_path: str = None) -> Dict[str, Any]:
        """Obtiene configuración de Docker"""
        config = cls.load_yaml_config(config_path or "src/config/testing.yaml")
        return config.get("docker", cls.DEFAULT_CONFIG["docker"])
    
    @classmethod
    def get_pytest_config(cls, config_path: str = None) -> Dict[str, Any]:
        """Obtiene configuración de pytest"""
        config = cls.load_yaml_config(config_path or "src/config/testing.yaml")
        return config.get("pytest", cls.DEFAULT_CONFIG["pytest"])
    
    @classmethod
    def get_health_config(cls, config_path: str = None) -> Dict[str, Any]:
        """Obtiene configuración de health checks"""
        config = cls.load_yaml_config(config_path or "src/config/audit.yaml")
        return config.get("health_check", cls.DEFAULT_CONFIG["health_check"])


# Constantes comunes
DEFAULT_SERVICE_NAME = "mcp-service"
DEFAULT_TEST_COMMAND = "pytest"
DEFAULT_COVERAGE_ARGS = "--cov=src --cov-report=html --cov-report=term-missing"
DEFAULT_TIMEOUT_MS = 300
DEFAULT_READINESS_PATH = "/readiness"
DEFAULT_LIVENESS_PATH = "/liveness" 