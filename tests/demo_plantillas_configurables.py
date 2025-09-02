#!/usr/bin/env python3
"""
Script de demostración para plantillas configurables de estructura
"""
import tempfile
import shutil
from pathlib import Path
from src.tools.structure_inspector import (
    BaseStructureInspector,
    inspect_microservice_structure,
    inspect_repository_structure
)
from src.tools.template_loader import TemplateLoader


def create_custom_template():
    """Crea una plantilla personalizada para demostración"""
    template_content = r"""
# Plantilla personalizada para demostración
default:
  name: "Plantilla Personalizada de Demostración"
  description: "Plantilla configurada para mostrar flexibilidad"
  
  required_files:
    - name: "Dockerfile"
      description: "Archivo de containerización"
      required: true
      weight: 25
    
    - name: "docker-compose.yml"
      description: "Archivo de orquestación"
      required: true
      weight: 25
    
    - name: ".gitignore"
      description: "Archivo de exclusión de Git"
      required: true
      weight: 20
    
    - name: "tests/"
      description: "Directorio de tests"
      required: true
      weight: 20
      type: "directory"
      must_contain: ["*.py"]
    
    - name: "README.md"
      description: "Documentación del proyecto"
      required: true
      weight: 10
    
    - name: "config/"
      description: "Directorio de configuración"
      required: false
      weight: 15
      type: "directory"

  dockerfile_quality:
    patterns:
      - name: "expose_port"
        regex: "EXPOSE\\s+\\d+"
        description: "Puerto expuesto correctamente"
        weight: 10
        required: false
        
      - name: "avoid_copy_all"
        regex: "COPY\\s+\\.\\s+\\."
        description: "Evita COPY . . sin .dockerignore"
        weight: -15
        required: false
        warning: "uses COPY . . without .dockerignore"
        
      - name: "use_slim_base"
        regex: "FROM\\s+.*:.*-slim"
        description: "Usa imagen base slim"
        weight: 10
        required: false

  compose_quality:
    patterns:
      - name: "restart_policy"
        regex: "restart:\\s*(unless-stopped|always|on-failure)"
        description: "Política de reinicio definida"
        weight: 10
        required: false
        warning: "no restart policy"
        
      - name: "health_check"
        regex: "healthcheck:"
        description: "Health check configurado"
        weight: 15
        required: false

  gitignore_quality:
    patterns:
      - name: "env_files"
        content: ".env"
        description: "Archivos de entorno"
        weight: 5
        required: false
        warning: "missing .env"
        
      - name: "python_cache"
        content: "__pycache__/"
        description: "Cache de Python"
        weight: 5
        required: false
        warning: "missing __pycache__/"

  tests_quality:
    patterns:
      - name: "test_naming_convention"
        regex: "test_.*\\.py$"
        description: "Convención de nombres de tests"
        weight: 10
        required: false
        warning: "test files don't follow naming convention"

scoring:
  base_weights:
    required_file: 25
    optional_file: 15
    required_directory: 20
    optional_directory: 10
  
  thresholds:
    complete: 85
    incomplete: 60
    poor: 0
  
  warning_penalty: 3
  
  bonus_features:
    multi_stage_build: 15
    health_check: 15
    test_coverage: 10
    documentation: 10
"""
    
    # Crear archivo temporal
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
    temp_file.write(template_content)
    temp_file.close()
    
    return temp_file.name


def demo_default_template():
    """Demuestra el uso de la plantilla por defecto"""
    print("🔧 DEMOSTRACIÓN: Plantilla por Defecto")
    print("=" * 60)
    
    # Crear directorio temporal para pruebas
    temp_dir = Path(tempfile.mkdtemp())
    print(f"📁 Directorio temporal creado: {temp_dir}")
    
    try:
        # Crear un microservicio básico
        service_dir = temp_dir / "basic_service"
        service_dir.mkdir()
        
        # Crear estructura mínima
        (service_dir / "Dockerfile").touch()
        (service_dir / "docker-compose.yml").touch()
        (service_dir / ".gitignore").touch()
        (service_dir / "tests").mkdir()
        (service_dir / "tests" / "test_example.py").touch()
        
        print(f"🏗️  Microservicio básico creado en: {service_dir}")
        
        # Inspección con plantilla por defecto
        print(f"\n🔍 Inspeccionando con plantilla por defecto...")
        result = inspect_microservice_structure("basic_service", temp_dir)
        
        print(f"📊 Resultado:")
        print(f"   Estado: {result.status}")
        print(f"   Score: {result.score:.1f}/100")
        print(f"   Recomendaciones: {len(result.recommendations)}")
        
        # Mostrar información de la plantilla
        inspector = BaseStructureInspector(temp_dir)
        template_info = inspector.get_template_info()
        
        print(f"\n📋 Información de la plantilla:")
        print(f"   Nombre: {template_info['name']}")
        print(f"   Descripción: {template_info['description']}")
        print(f"   Archivos requeridos: {template_info['total_required_files']}")
        print(f"   Archivos opcionales: {template_info['total_optional_files']}")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\n🧹 Directorio temporal eliminado: {temp_dir}")


def demo_custom_template():
    """Demuestra el uso de una plantilla personalizada"""
    print(f"\n🎨 DEMOSTRACIÓN: Plantilla Personalizada")
    print("=" * 60)
    
    # Crear plantilla personalizada
    template_path = create_custom_template()
    print(f"📝 Plantilla personalizada creada en: {template_path}")
    
    # Crear directorio temporal para pruebas
    temp_dir = Path(tempfile.mkdtemp())
    print(f"📁 Directorio temporal creado: {temp_dir}")
    
    try:
        # Crear un microservicio con estructura personalizada
        service_dir = temp_dir / "custom_service"
        service_dir.mkdir()
        
        # Crear estructura según la plantilla personalizada
        (service_dir / "Dockerfile").touch()
        (service_dir / "docker-compose.yml").touch()
        (service_dir / ".gitignore").touch()
        (service_dir / "tests").mkdir()
        (service_dir / "tests" / "test_example.py").touch()
        (service_dir / "README.md").touch()
        (service_dir / "config").mkdir()
        
        print(f"🏗️  Microservicio personalizado creado en: {service_dir}")
        
        # Inspección con plantilla personalizada
        print(f"\n🔍 Inspeccionando con plantilla personalizada...")
        result = inspect_microservice_structure("custom_service", temp_dir, template_path)
        
        print(f"📊 Resultado:")
        print(f"   Estado: {result.status}")
        print(f"   Score: {result.score:.1f}/100")
        print(f"   Recomendaciones: {len(result.recommendations)}")
        
        # Mostrar información de la plantilla personalizada
        inspector = BaseStructureInspector(temp_dir, template_path)
        template_info = inspector.get_template_info()
        
        print(f"\n📋 Información de la plantilla personalizada:")
        print(f"   Nombre: {template_info['name']}")
        print(f"   Descripción: {template_info['description']}")
        print(f"   Archivos requeridos: {template_info['total_required_files']}")
        print(f"   Archivos opcionales: {template_info['total_optional_files']}")
        
        # Comparar con plantilla por defecto
        print(f"\n🔄 Comparación con plantilla por defecto:")
        default_inspector = BaseStructureInspector(temp_dir)
        default_result = default_inspector.inspect_microservice("custom_service")
        
        print(f"   Score con plantilla por defecto: {default_result.score:.1f}/100")
        print(f"   Score con plantilla personalizada: {result.score:.1f}/100")
        print(f"   Diferencia: {result.score - default_result.score:+.1f} puntos")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\n🧹 Directorio temporal eliminado: {temp_dir}")
        
        # Limpiar archivo de plantilla temporal
        try:
            Path(template_path).unlink()
            print(f"🧹 Archivo de plantilla temporal eliminado: {template_path}")
        except:
            pass


def demo_template_flexibility():
    """Demuestra la flexibilidad de las plantillas"""
    print(f"\n🎯 DEMOSTRACIÓN: Flexibilidad de Plantillas")
    print("=" * 60)
    
    # Crear diferentes plantillas para diferentes escenarios
    scenarios = {
        "strict": {
            "name": "Plantilla Estricta",
            "description": "Requisitos muy estrictos para producción",
            "thresholds": {"complete": 95, "incomplete": 80, "poor": 0},
            "warning_penalty": 5
        },
        "lenient": {
            "name": "Plantilla Permisiva",
            "description": "Requisitos básicos para desarrollo",
            "thresholds": {"complete": 60, "incomplete": 30, "poor": 0},
            "warning_penalty": 1
        }
    }
    
    for scenario_name, config in scenarios.items():
        print(f"\n📋 Escenario: {config['name']}")
        print(f"   Descripción: {config['description']}")
        print(f"   Umbrales: {config['thresholds']}")
        print(f"   Penalización por warning: {config['warning_penalty']}")
        
        # Crear plantilla temporal para este escenario
        template_content = f"""
default:
  name: "{config['name']}"
  description: "{config['description']}"
  
  required_files:
    - name: "Dockerfile"
      description: "Archivo de containerización"
      required: true
      weight: 20
    
    - name: "docker-compose.yml"
      description: "Archivo de orquestación"
      required: true
      weight: 20
    
    - name: ".gitignore"
      description: "Archivo de exclusión de Git"
      required: true
      weight: 15
    
    - name: "tests/"
      description: "Directorio de tests"
      required: true
      weight: 15
      type: "directory"
      must_contain: ["*.py"]

scoring:
  base_weights:
    required_file: 20
    optional_file: 10
    required_directory: 15
    optional_directory: 8
  
  thresholds:
    complete: {config['thresholds']['complete']}
    incomplete: {config['thresholds']['incomplete']}
    poor: {config['thresholds']['poor']}
  
  warning_penalty: {config['warning_penalty']}
  
  bonus_features:
    multi_stage_build: 10
    health_check: 8
    test_coverage: 5
"""
        
        # Crear archivo temporal
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        temp_file.write(template_content)
        temp_file.close()
        
        # Crear microservicio de prueba
        temp_dir = Path(tempfile.mkdtemp())
        service_dir = temp_dir / "test_service"
        service_dir.mkdir()
        
        # Estructura básica
        (service_dir / "Dockerfile").touch()
        (service_dir / "docker-compose.yml").touch()
        (service_dir / ".gitignore").touch()
        (service_dir / "tests").mkdir()
        (service_dir / "tests" / "test_example.py").touch()
        
        try:
            # Inspeccionar con esta plantilla
            result = inspect_microservice_structure("test_service", temp_dir, temp_file.name)
            
            print(f"   Resultado: {result.status} (score: {result.score:.1f}/100)")
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            Path(temp_file.name).unlink()


def main():
    """Función principal de demostración"""
    print("🚀 DEMOSTRACIÓN DE PLANTILLAS CONFIGURABLES")
    print("=" * 80)
    print("Mostrando cómo las plantillas permiten personalizar qué archivos analizar\n")
    
    # Ejecutar demostraciones
    demo_default_template()
    demo_custom_template()
    demo_template_flexibility()
    
    print(f"\n🎉 Demostración completada!")
    print("✅ Las plantillas permiten configurar qué archivos analizar")
    print("✅ Se pueden ajustar umbrales y penalizaciones")
    print("✅ La herramienta mantiene compatibilidad hacia atrás")
    print("✅ Se pueden crear plantillas específicas para diferentes necesidades")


if __name__ == "__main__":
    main() 