#!/usr/bin/env python3
"""
Test de la funcionalidad avanzada de análisis de arquitectura
"""
import asyncio
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_advanced_architecture():
    """Test de la funcionalidad avanzada de arquitectura"""
    
    print("🧪 TEST: FUNCIONALIDAD AVANZADA DE ANÁLISIS DE ARQUITECTURA")
    print("=" * 70)
    
    try:
        # Importar las funciones directamente
        from src.tools.structure_inspector import (
            analyze_microservice_architecture_advanced,
            generate_architecture_todo_plan,
            inspect_microservice_structure
        )
        
        print("✅ Funciones importadas correctamente")
        
        # Configurar parámetros
        service_path = "src"
        base_path = "."
        
        print(f"🔍 Analizando microservicio: {service_path}")
        print()
        
        # 1. Análisis de estructura básica
        print("📊 PASO 1: Análisis de Estructura Básica")
        print("-" * 50)
        
        structure_report = inspect_microservice_structure(service_path, base_path)
        print(f"   - Estado: {structure_report.status.value.upper()}")
        print(f"   - Score: {structure_report.score:.1f}/100")
        print(f"   - Verificaciones:")
        print(f"     * Dockerfile: {'✅' if structure_report.structure_checks.Dockerfile else '❌'}")
        print(f"     * docker-compose.yml: {'✅' if structure_report.structure_checks.docker_compose_yml else '❌'}")
        print(f"     * .gitignore: {'✅' if structure_report.structure_checks.gitignore else '❌'}")
        print(f"     * Directorio tests: {'✅' if structure_report.structure_checks.tests_dir_exists else '❌'}")
        print(f"     * Tests con archivos: {'✅' if structure_report.structure_checks.tests_dir_has_files else '❌'}")
        print()
        
        # 2. Análisis avanzado de arquitectura
        print("🏗️  PASO 2: Análisis Avanzado de Arquitectura (Perfil Arquitecto Senior)")
        print("-" * 70)
        
        architecture_analysis = analyze_microservice_architecture_advanced(service_path, base_path)
        
        print(f"   - Score de Arquitectura: {architecture_analysis.architecture_score:.1f}/100")
        print(f"   - Estado: {architecture_analysis.architecture_status}")
        print()
        
        print("🔍 PRINCIPIOS DE ARQUITECTURA VERIFICADOS:")
        print(f"   - DRY (Don't Repeat Yourself): {'✅ CUMPLE' if architecture_analysis.drp_compliance else '❌ VIOLACIÓN'}")
        print(f"   - TDD (Test Driven Development): {'✅ CUMPLE' if architecture_analysis.tdd_implementation else '❌ VIOLACIÓN'}")
        print(f"   - Pruebas de Integración: {'✅ CUMPLE' if architecture_analysis.integration_tests else '❌ VIOLACIÓN'}")
        print(f"   - Datos Faker: {'✅ CUMPLE' if architecture_analysis.faker_data_usage else '❌ VIOLACIÓN'}")
        print(f"   - Escalabilidad: {'✅ CUMPLE' if architecture_analysis.scalability_features else '❌ VIOLACIÓN'}")
        print()
        
        # 3. Detección de violaciones
        print("⚠️  PASO 3: Detección de Violaciones de Principios")
        print("-" * 55)
        
        print(f"🚨 Total de Violaciones: {architecture_analysis.total_violations}")
        print(f"   - Críticas: {architecture_analysis.critical_violations}")
        print(f"   - Altas: {architecture_analysis.high_violations}")
        print(f"   - Medias: {architecture_analysis.medium_violations}")
        print(f"   - Bajas: {architecture_analysis.low_violations}")
        print()
        
        if architecture_analysis.violations:
            print("📋 DETALLE DE VIOLACIONES:")
            for i, violation in enumerate(architecture_analysis.violations, 1):
                print(f"   {i}. [{violation.severity}] {violation.principle.value}")
                print(f"      Descripción: {violation.description}")
                print(f"      Recomendación: {violation.recommendation}")
                if violation.file_path:
                    print(f"      Archivo: {violation.file_path}")
                print()
        
        # 4. Generación de plan de acciones TODO
        print("📝 PASO 4: Plan de Acciones TODO para Cumplir Criterios de Aceptación")
        print("-" * 75)
        
        todo_actions = generate_architecture_todo_plan(service_path, base_path)
        
        print(f"📋 Total de Acciones TODO: {len(todo_actions)}")
        print()
        
        if todo_actions:
            print("🎯 ACCIONES PRIORITARIAS:")
            for i, action in enumerate(todo_actions, 1):
                print(f"   {i}. [{action.priority}] {action.action}")
                print(f"      Descripción: {action.description}")
                print(f"      Esfuerzo Estimado: {action.estimated_effort}")
                if action.dependencies:
                    print(f"      Dependencias: {', '.join(action.dependencies)}")
                if action.files_to_modify:
                    print(f"      Archivos a Modificar: {', '.join(action.files_to_modify)}")
                print()
        
        # 5. Resumen ejecutivo
        print("📊 RESUMEN EJECUTIVO")
        print("-" * 30)
        
        overall_score = (structure_report.score + architecture_analysis.architecture_score) / 2
        
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
        
        print(f"🏆 Estado General: {overall_status}")
        print(f"📈 Score General: {overall_score:.1f}/100")
        print(f"   - Estructura: {structure_report.score:.1f}/100")
        print(f"   - Arquitectura: {architecture_analysis.architecture_score:.1f}/100")
        print()
        
        print(f"🎯 Próximos Pasos Recomendados:")
        priority_actions = [a for a in todo_actions if a.priority in ['CRITICAL', 'HIGH']]
        for i, action in enumerate(priority_actions[:3], 1):
            print(f"   {i}. {action.action}")
        
        print()
        print("✅ Análisis completado. El MCP ha generado un plan de acciones TODO")
        print("   para cumplir con los criterios de aceptación de arquitectura.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Iniciando test de funcionalidad avanzada de arquitectura...")
    print()
    
    success = asyncio.run(test_advanced_architecture())
    
    if success:
        print("\n🎉 ¡ÉXITO! La funcionalidad está funcionando correctamente")
        print("🎯 La herramienta advanced_architecture_audit está lista para usar en el MCP")
        sys.exit(0)
    else:
        print("\n💥 ¡FALLO! La funcionalidad tiene problemas")
        sys.exit(1) 