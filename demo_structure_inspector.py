#!/usr/bin/env python3
"""
Script de demostración para la herramienta base_structure_inspector_microservice
"""
import asyncio
import json
from src.tools.structure_inspector import (
    BaseStructureInspector,
    inspect_microservice_structure,
    inspect_repository_structure
)


async def demo_microservice_inspection():
    """Demuestra la inspección de un microservicio específico"""
    print("🔍 DEMOSTRACIÓN: Inspección de Microservicio")
    print("=" * 60)
    
    try:
        # Inspeccionar el MCP actual
        result = inspect_microservice_structure(".", ".")
        
        print(f"📊 Resultado de la inspección:")
        print(f"   Servicio: {result.service}")
        print(f"   Estado: {result.status}")
        print(f"   Score: {result.score}/100")
        print(f"   Ruta: {result.path}")
        
        print(f"\n✅ Verificaciones de estructura:")
        checks = result.structure_checks
        print(f"   Dockerfile: {'✅' if checks.Dockerfile else '❌'}")
        print(f"   docker-compose.yml: {'✅' if checks.docker_compose_yml else '❌'}")
        print(f"   .gitignore: {'✅' if checks.gitignore else '❌'}")
        print(f"   Directorio tests/: {'✅' if checks.tests_dir_exists else '❌'}")
        print(f"   Archivos de test: {'✅' if checks.tests_dir_has_files else '❌'}")
        
        print(f"\n⚠️  Calidad de configuración:")
        quality = result.config_quality
        if quality.dockerfile_best_practices:
            print(f"   Dockerfile: {', '.join(quality.dockerfile_best_practices)}")
        if quality.compose_warnings:
            print(f"   docker-compose.yml: {', '.join(quality.compose_warnings)}")
        if quality.gitignore_warnings:
            print(f"   .gitignore: {', '.join(quality.gitignore_warnings)}")
        if quality.tests_warnings:
            print(f"   Tests: {', '.join(quality.tests_warnings)}")
        
        if result.recommendations:
            print(f"\n💡 Recomendaciones:")
            for i, rec in enumerate(result.recommendations, 1):
                print(f"   {i}. {rec}")
        
    except Exception as e:
        print(f"❌ Error durante la inspección: {e}")


async def demo_repository_audit():
    """Demuestra la auditoría completa del repositorio"""
    print(f"\n🏗️  DEMOSTRACIÓN: Auditoría del Repositorio")
    print("=" * 60)
    
    try:
        # Auditoría completa del repositorio
        result = inspect_repository_structure(".")
        
        print(f"📊 Resumen de la auditoría:")
        print(f"   Estado general: {result.overall_status}")
        print(f"   Total de servicios: {result.total_services}")
        print(f"   Servicios completos: {result.complete_services}")
        print(f"   Servicios incompletos: {result.incomplete_services}")
        print(f"   Servicios con problemas: {result.poor_services}")
        print(f"   Score promedio: {result.average_score:.1f}/100")
        
        if result.services:
            print(f"\n📋 Detalle por servicio:")
            for service in result.services:
                status_emoji = {
                    "complete": "✅",
                    "incomplete": "⚠️",
                    "poor": "❌"
                }.get(service.status, "❓")
                
                print(f"   {status_emoji} {service.service}: {service.status} (score: {service.score:.1f})")
                
                if service.recommendations:
                    print(f"      Recomendaciones: {len(service.recommendations)}")
        
    except Exception as e:
        print(f"❌ Error durante la auditoría: {e}")


async def demo_custom_inspection():
    """Demuestra la inspección personalizada"""
    print(f"\n🎯 DEMOSTRACIÓN: Inspección Personalizada")
    print("=" * 60)
    
    try:
        # Crear inspector personalizado
        inspector = BaseStructureInspector(".")
        
        # Verificar si el directorio actual es un microservicio
        is_microservice = inspector._is_microservice_directory(inspector.base_path)
        print(f"¿Es el directorio actual un microservicio? {'✅ Sí' if is_microservice else '❌ No'}")
        
        # Detectar servicios automáticamente
        services = inspector._auto_detect_services()
        print(f"Servicios detectados automáticamente: {services}")
        
        # Mostrar patrones de validación
        print(f"\n🔍 Patrones de validación configurados:")
        print(f"   Dockerfile: {len(inspector.dockerfile_patterns)} patrones")
        print(f"   docker-compose.yml: {len(inspector.compose_patterns)} patrones")
        print(f"   .gitignore: {len(inspector.gitignore_patterns)} patrones")
        print(f"   Tests: {len(inspector.test_patterns)} patrones")
        
    except Exception as e:
        print(f"❌ Error durante la inspección personalizada: {e}")


async def main():
    """Función principal de demostración"""
    print("🚀 DEMOSTRACIÓN DE BASE_STRUCTURE_INSPECTOR_MICROSERVICE")
    print("=" * 80)
    print("Esta herramienta verifica si cada microservicio cumple con los estándares")
    print("técnicos mínimos de arquitectura moderna.\n")
    
    # Ejecutar demostraciones
    await demo_microservice_inspection()
    await demo_repository_audit()
    await demo_custom_inspection()
    
    print(f"\n🎉 Demostración completada!")
    print("La herramienta está lista para ser usada a través del MCP.")


if __name__ == "__main__":
    asyncio.run(main()) 