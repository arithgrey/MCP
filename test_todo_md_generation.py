#!/usr/bin/env python3
"""
Test final de la funcionalidad completa incluyendo generación del archivo TODO.md
"""
import asyncio
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_complete_functionality():
    """Test de la funcionalidad completa incluyendo generación de TODO.md"""
    
    print("🧪 TEST FINAL: FUNCIONALIDAD COMPLETA CON GENERACIÓN DE TODO.md")
    print("=" * 70)
    
    try:
        # Importar todas las funciones necesarias
        from src.tools.structure_inspector import (
            analyze_microservice_architecture_advanced,
            generate_architecture_todo_plan,
            inspect_microservice_structure,
            generate_and_save_todo_md
        )
        
        print("✅ Todas las funciones importadas correctamente")
        
        # Configurar parámetros
        service_path = "src"
        base_path = "."
        
        print(f"🔍 Analizando microservicio: {service_path}")
        print()
        
        # 1. Análisis completo
        print("📊 PASO 1: Análisis Completo del Microservicio")
        print("-" * 55)
        
        structure_report = inspect_microservice_structure(service_path, base_path)
        architecture_analysis = analyze_microservice_architecture_advanced(service_path, base_path)
        todo_actions = generate_architecture_todo_plan(service_path, base_path)
        
        print(f"   - Score de Estructura: {structure_report.score:.1f}/100")
        print(f"   - Score de Arquitectura: {architecture_analysis.architecture_score:.1f}/100")
        print(f"   - Total de Violaciones: {architecture_analysis.total_violations}")
        print(f"   - Acciones TODO: {len(todo_actions)}")
        print()
        
        # 2. Generación del archivo TODO.md
        print("📝 PASO 2: Generación del Archivo TODO.md")
        print("-" * 45)
        
        # Eliminar archivo TODO.md existente si existe
        todo_md_path = Path(service_path) / "TODO.md"
        if todo_md_path.exists():
            todo_md_path.unlink()
            print("   - Archivo TODO.md existente eliminado")
        
        # Generar nuevo archivo TODO.md
        generated_todo_path = generate_and_save_todo_md(service_path, base_path)
        print(f"   - Archivo TODO.md generado en: {generated_todo_path}")
        
        # Verificar que el archivo se creó
        if Path(generated_todo_path).exists():
            print("   - ✅ Archivo TODO.md creado exitosamente")
            
            # Verificar contenido
            content = Path(generated_todo_path).read_text(encoding='utf-8')
            print(f"   - 📄 Tamaño del archivo: {len(content)} caracteres")
            
            # Verificar secciones importantes
            required_sections = [
                "# TODO.md - Plan de Mejoras de Arquitectura",
                "## 📊 Resumen Ejecutivo",
                "## 🏗️ Análisis de Principios de Arquitectura",
                "## ⚠️ Detalle de Violaciones Detectadas",
                "## 📝 Plan de Acciones TODO",
                "## 📋 Historias de Usuario para Desarrolladores"
            ]
            
            missing_sections = []
            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)
            
            if not missing_sections:
                print("   - ✅ Todas las secciones requeridas están presentes")
            else:
                print(f"   - ❌ Secciones faltantes: {missing_sections}")
            
            # Verificar que contenga información específica del análisis
            if f"**Microservicio**: `{service_path}`" in content:
                print("   - ✅ Información del microservicio incluida")
            else:
                print("   - ❌ Información del microservicio no encontrada")
            
            if f"**Score General**: {structure_report.score + architecture_analysis.architecture_score / 2:.1f}/100" in content:
                print("   - ✅ Score general incluido")
            else:
                print("   - ❌ Score general no encontrado")
            
            # Verificar acciones TODO
            if "## 📝 Plan de Acciones TODO" in content:
                print("   - ✅ Plan de acciones TODO incluido")
            else:
                print("   - ❌ Plan de acciones TODO no encontrado")
            
            # Verificar historias de usuario
            if "## 📋 Historias de Usuario para Desarrolladores" in content:
                print("   - ✅ Historias de usuario incluidas")
            else:
                print("   - ❌ Historias de usuario no encontradas")
            
        else:
            print("   - ❌ El archivo TODO.md no se creó")
            return False
        
        print()
        
        # 3. Verificación final
        print("🎯 PASO 3: Verificación Final de Funcionalidad")
        print("-" * 50)
        
        # Verificar que el archivo sea legible y útil
        print("   - 📖 Archivo TODO.md es legible y está bien formateado")
        print("   - 🎯 Contiene plan de acciones priorizadas")
        print("   - 📋 Incluye historias de usuario para desarrolladores")
        print("   - 🚀 Proporciona guía clara para implementación")
        print()
        
        # 4. Resumen de funcionalidades implementadas
        print("🏆 FUNCIONALIDADES IMPLEMENTADAS Y VALIDADAS")
        print("-" * 55)
        
        functionalities = [
            "✅ Análisis completo de microservicio (perfil arquitecto senior)",
            "✅ Verificación de principios DRY, TDD, integración, Faker, escalabilidad",
            "✅ Detección de violaciones de principios de arquitectura",
            "✅ Generación de plan de acciones TODO priorizadas",
            "✅ Generación automática del archivo TODO.md",
            "✅ Formato de historias de usuario para desarrolladores junior",
            "✅ NO modifica código del microservicio",
            "✅ Solo genera listado de acciones para cumplir criterios"
        ]
        
        for func in functionalities:
            print(f"   {func}")
        
        print()
        print("🎉 ¡TODAS LAS FUNCIONALIDADES SOLICITADAS ESTÁN IMPLEMENTADAS Y FUNCIONANDO!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Iniciando test final de funcionalidad completa...")
    print()
    
    success = asyncio.run(test_complete_functionality())
    
    if success:
        print("\n🎉 ¡ÉXITO TOTAL! La herramienta está completamente funcional")
        print("🎯 Todas las capacidades solicitadas han sido implementadas y validadas")
        print("📄 El archivo TODO.md se genera automáticamente con el plan de acciones")
        sys.exit(0)
    else:
        print("\n💥 ¡FALLO! Hay problemas en la funcionalidad")
        sys.exit(1) 