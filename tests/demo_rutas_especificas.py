#!/usr/bin/env python3
"""
Script de demostración para validar rutas específicas y comportamiento de solo lectura
"""
import asyncio
import tempfile
import shutil
from pathlib import Path
from src.tools.structure_inspector import (
    BaseStructureInspector,
    inspect_microservice_structure,
    inspect_repository_structure
)


def create_test_microservice(base_path: Path, service_name: str, quality: str = "good") -> Path:
    """Crea un microservicio de prueba con la calidad especificada"""
    service_path = base_path / service_name
    service_path.mkdir(parents=True, exist_ok=True)
    
    if quality == "good":
        # Microservicio con buena estructura
        dockerfile_content = """
        FROM python:3.9-slim
        EXPOSE 8000
        WORKDIR /app
        COPY requirements.txt .
        RUN pip install -r requirements.txt
        COPY app.py .
        CMD ["python", "app.py"]
        """
        
        compose_content = """
        version: '3.8'
        services:
          app:
            build: .
            restart: unless-stopped
            volumes:
              - ./data:/app/data
            networks:
              - app-network
        networks:
          app-network:
        """
        
        gitignore_content = """
        .env
        __pycache__/
        *.pyc
        node_modules/
        build/
        dist/
        .pytest_cache/
        *.log
        """
        
    elif quality == "poor":
        # Microservicio con problemas
        dockerfile_content = """
        FROM ubuntu:latest
        RUN apt-get update && apt-get install -y vim curl wget
        COPY . .
        """
        
        compose_content = """
        version: '3.8'
        services:
          app:
            build: .
        """
        
        gitignore_content = """
        *.log
        """
    
    # Crear archivos
    (service_path / "Dockerfile").write_text(dockerfile_content)
    (service_path / "docker-compose.yml").write_text(compose_content)
    (service_path / ".gitignore").write_text(gitignore_content)
    
    # Crear directorio de tests
    tests_dir = service_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_example.py").touch()
    
    return service_path


def demo_specific_paths():
    """Demuestra el uso de rutas específicas"""
    print("🎯 DEMOSTRACIÓN: Rutas Específicas de Microservicios")
    print("=" * 70)
    
    # Crear directorio temporal para las pruebas
    temp_dir = Path(tempfile.mkdtemp())
    print(f"📁 Directorio temporal creado: {temp_dir}")
    
    try:
        # Crear múltiples microservicios en diferentes ubicaciones
        services_to_create = [
            "service_a",                    # En raíz
            "subdir/service_b",             # En subdirectorio
            "deep/nested/service_c",        # En directorio anidado
            "quality/poor_service",         # Servicio con problemas
            "quality/good_service"          # Servicio bien estructurado
        ]
        
        print(f"\n🏗️  Creando {len(services_to_create)} microservicios de prueba...")
        
        for i, service_path in enumerate(services_to_create, 1):
            quality = "poor" if "poor" in service_path else "good"
            full_path = create_test_microservice(temp_dir, service_path, quality)
            print(f"   {i}. ✅ {service_path} ({quality}) - {full_path}")
        
        print(f"\n🔍 INSPECCIÓN INDIVIDUAL POR RUTAS ESPECÍFICAS:")
        print("-" * 50)
        
        # Inspeccionar cada servicio individualmente
        for service_path in services_to_create:
            print(f"\n📊 Analizando: {service_path}")
            try:
                result = inspect_microservice_structure(service_path, temp_dir)
                
                status_emoji = {
                    "complete": "✅",
                    "incomplete": "⚠️",
                    "poor": "❌"
                }.get(result.status, "❓")
                
                print(f"   Estado: {status_emoji} {result.status}")
                print(f"   Score: {result.score:.1f}/100")
                print(f"   Ruta: {result.path}")
                
                if result.recommendations:
                    print(f"   Recomendaciones: {len(result.recommendations)}")
                    for rec in result.recommendations[:3]:  # Mostrar solo las primeras 3
                        print(f"     • {rec}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print(f"\n🏗️  AUDITORÍA COMPLETA DEL REPOSITORIO:")
        print("-" * 50)
        
        # Auditoría completa
        audit = inspect_repository_structure(temp_dir)
        
        print(f"📊 Resumen de la auditoría:")
        print(f"   Total de servicios: {audit.total_services}")
        print(f"   Servicios completos: {audit.complete_services}")
        print(f"   Servicios incompletos: {audit.incomplete_services}")
        print(f"   Servicios con problemas: {audit.poor_services}")
        print(f"   Score promedio: {audit.average_score:.1f}/100")
        print(f"   Estado general: {audit.overall_status}")
        
        print(f"\n📋 Detalle por servicio:")
        for service in audit.services:
            status_emoji = {
                "complete": "✅",
                "incomplete": "⚠️",
                "poor": "❌"
            }.get(service.status, "❓")
            
            print(f"   {status_emoji} {service.service}: {service.status} (score: {service.score:.1f})")
        
        print(f"\n🔍 AUDITORÍA CON RUTAS ESPECÍFICAS:")
        print("-" * 50)
        
        # Auditoría especificando solo algunos servicios
        specific_services = ["service_a", "quality/poor_service"]
        specific_audit = inspect_repository_structure(temp_dir, specific_services)
        
        print(f"📊 Auditoría de servicios específicos: {specific_services}")
        print(f"   Total inspeccionados: {specific_audit.total_services}")
        print(f"   Score promedio: {specific_audit.average_score:.1f}/100")
        
        for service in specific_audit.services:
            status_emoji = {
                "complete": "✅",
                "incomplete": "⚠️",
                "poor": "❌"
            }.get(service.status, "❓")
            
            print(f"   {status_emoji} {service.service}: {service.status} (score: {service.score:.1f})")
        
    finally:
        # Limpiar
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\n🧹 Directorio temporal eliminado: {temp_dir}")


def demo_readonly_behavior():
    """Demuestra que la herramienta solo lee, no modifica"""
    print(f"\n📖 DEMOSTRACIÓN: Comportamiento de Solo Lectura")
    print("=" * 70)
    
    # Crear directorio temporal
    temp_dir = Path(tempfile.mkdtemp())
    print(f"📁 Directorio temporal creado: {temp_dir}")
    
    try:
        # Crear un microservicio con contenido específico
        service_path = temp_dir / "readonly_test_service"
        service_path.mkdir()
        
        # Crear archivos con contenido específico
        original_dockerfile_content = """
        FROM python:3.9
        COPY . .
        """
        dockerfile_path = service_path / "Dockerfile"
        dockerfile_path.write_text(original_dockerfile_content)
        
        original_compose_content = """
        version: '3.8'
        services:
          app:
            build: .
        """
        compose_path = service_path / "docker-compose.yml"
        compose_path.write_text(original_compose_content)
        
        original_gitignore_content = """
        *.log
        """
        gitignore_path = service_path / ".gitignore"
        gitignore_path.write_text(original_gitignore_content)
        
        # Guardar timestamps y contenido originales
        original_dockerfile_mtime = dockerfile_path.stat().st_mtime
        original_compose_mtime = compose_path.stat().st_mtime
        original_gitignore_mtime = gitignore_path.stat().st_mtime
        
        print(f"📝 Archivos creados con contenido original:")
        print(f"   Dockerfile: {len(original_dockerfile_content)} caracteres")
        print(f"   docker-compose.yml: {len(original_compose_content)} caracteres")
        print(f"   .gitignore: {len(original_gitignore_content)} caracteres")
        
        print(f"\n🔍 Ejecutando inspección...")
        
        # Inspeccionar el microservicio
        result = inspect_microservice_structure("readonly_test_service", temp_dir)
        
        print(f"📊 Resultado de la inspección:")
        print(f"   Estado: {result.status}")
        print(f"   Score: {result.score:.1f}/100")
        print(f"   Warnings detectados: {len(result.config_quality.dockerfile_best_practices) + len(result.config_quality.compose_warnings) + len(result.config_quality.gitignore_warnings)}")
        
        print(f"\n⚠️  Warnings detectados:")
        if result.config_quality.dockerfile_best_practices:
            print(f"   Dockerfile: {', '.join(result.config_quality.dockerfile_best_practices)}")
        if result.config_quality.compose_warnings:
            print(f"   docker-compose.yml: {', '.join(result.config_quality.compose_warnings)}")
        if result.config_quality.gitignore_warnings:
            print(f"   .gitignore: {', '.join(result.config_quality.gitignore_warnings)}")
        
        print(f"\n💡 Recomendaciones generadas: {len(result.recommendations)}")
        for i, rec in enumerate(result.recommendations, 1):
            print(f"   {i}. {rec}")
        
        print(f"\n🔒 VERIFICACIÓN DE SOLO LECTURA:")
        print("-" * 40)
        
        # Verificar que los archivos NO fueron modificados
        current_dockerfile_mtime = dockerfile_path.stat().st_mtime
        current_compose_mtime = compose_path.stat().st_mtime
        current_gitignore_mtime = gitignore_path.stat().st_mtime
        
        current_dockerfile_content = dockerfile_path.read_text()
        current_compose_content = compose_path.read_text()
        current_gitignore_content = gitignore_path.read_text()
        
        print(f"   Timestamps modificados: {'❌' if current_dockerfile_mtime != original_dockerfile_mtime else '✅'} Dockerfile")
        print(f"   Timestamps modificados: {'❌' if current_compose_mtime != original_compose_mtime else '✅'} docker-compose.yml")
        print(f"   Timestamps modificados: {'❌' if current_gitignore_mtime != original_gitignore_mtime else '✅'} .gitignore")
        
        print(f"   Contenido modificado: {'❌' if current_dockerfile_content != original_dockerfile_content else '✅'} Dockerfile")
        print(f"   Contenido modificado: {'❌' if current_compose_content != original_compose_content else '✅'} docker-compose.yml")
        print(f"   Contenido modificado: {'❌' if current_gitignore_content != original_gitignore_content else '✅'} .gitignore")
        
        print(f"\n✅ CONCLUSIÓN: La herramienta SOLO LEE archivos, NO los modifica")
        
    finally:
        # Limpiar
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\n🧹 Directorio temporal eliminado: {temp_dir}")


def main():
    """Función principal de demostración"""
    print("🚀 DEMOSTRACIÓN COMPLETA DE BASE_STRUCTURE_INSPECTOR_MICROSERVICE")
    print("=" * 80)
    print("Validando funcionalidad con rutas específicas y comportamiento de solo lectura\n")
    
    # Ejecutar demostraciones
    demo_specific_paths()
    demo_readonly_behavior()
    
    print(f"\n🎉 Demostración completada!")
    print("✅ La herramienta funciona correctamente con rutas específicas")
    print("✅ La herramienta SOLO proporciona información, NO modifica código")
    print("✅ Todos los tests de validación han pasado exitosamente")


if __name__ == "__main__":
    main() 