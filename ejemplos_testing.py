#!/usr/bin/env python3
"""
Ejemplos de uso de las herramientas de testing del MCP
Este archivo muestra cómo usar las nuevas herramientas que ejecutan tests con docker exec
"""

import asyncio
from src.tools.testing_tools import TestingTools, run_docker_test
from src.tools.audit_repo import AuditOrchestrator


async def ejemplo_testing_basico():
    """Ejemplo básico de ejecución de tests"""
    print("=== Ejemplo: Testing Básico ===")
    
    # Ejecutar tests básicos
    result = await run_docker_test(
        service_name="mcp-service",
        test_command="pytest",
        additional_args="-v"
    )
    
    print(f"Estado: {result['status']}")
    print(f"Comando ejecutado: {result['command']}")
    print(f"Código de retorno: {result['return_code']}")
    
    if result['stdout']:
        print("Salida estándar:")
        print(result['stdout'][:500] + "..." if len(result['stdout']) > 500 else result['stdout'])
    
    if result['stderr']:
        print("Errores:")
        print(result['stderr'])


async def ejemplo_testing_con_coverage():
    """Ejemplo de ejecución de tests con coverage"""
    print("\n=== Ejemplo: Testing con Coverage ===")
    
    result = await TestingTools.run_pytest_with_coverage(
        service_name="mcp-service",
        coverage_args="--cov=src --cov-report=html --cov-report=term-missing"
    )
    
    print(f"Estado: {result['status']}")
    print(f"Comando ejecutado: {result['command']}")
    
    if result['success']:
        print("✅ Tests ejecutados con coverage exitosamente")
    else:
        print("❌ Error en la ejecución de tests con coverage")


async def ejemplo_testing_archivo_especifico():
    """Ejemplo de ejecución de un archivo de test específico"""
    print("\n=== Ejemplo: Testing de Archivo Específico ===")
    
    result = await TestingTools.run_specific_test_file(
        service_name="mcp-service",
        test_file="tests/test_health.py",
        additional_args="-v"
    )
    
    print(f"Estado: {result['status']}")
    print(f"Archivo de test: tests/test_health.py")
    
    if result['success']:
        print("✅ Archivo de test ejecutado exitosamente")
    else:
        print("❌ Error en la ejecución del archivo de test")


async def ejemplo_testing_con_marcadores():
    """Ejemplo de ejecución de tests con marcadores"""
    print("\n=== Ejemplo: Testing con Marcadores ===")
    
    result = await TestingTools.run_test_with_markers(
        service_name="mcp-service",
        marker="unit",
        additional_args="-v"
    )
    
    print(f"Estado: {result['status']}")
    print(f"Marcador usado: unit")
    
    if result['success']:
        print("✅ Tests unitarios ejecutados exitosamente")
    else:
        print("❌ Error en la ejecución de tests unitarios")


async def ejemplo_testing_paralelo():
    """Ejemplo de ejecución de tests en paralelo"""
    print("\n=== Ejemplo: Testing en Paralelo ===")
    
    result = await TestingTools.run_parallel_tests(
        service_name="mcp-service",
        num_workers=2,
        additional_args="-v"
    )
    
    print(f"Estado: {result['status']}")
    print(f"Workers usados: 2")
    
    if result['success']:
        print("✅ Tests ejecutados en paralelo exitosamente")
    else:
        print("❌ Error en la ejecución de tests en paralelo")


async def ejemplo_testing_con_reportes():
    """Ejemplo de generación de reportes"""
    print("\n=== Ejemplo: Testing con Reportes ===")
    
    # Reporte HTML
    result_html = await TestingTools.run_tests_with_html_report(
        service_name="mcp-service",
        report_dir="test_reports",
        additional_args="-v"
    )
    
    print(f"Reporte HTML - Estado: {result_html['status']}")
    
    # Reporte JUnit XML
    result_junit = await TestingTools.run_tests_with_junit_report(
        service_name="mcp-service",
        report_file="junit.xml",
        additional_args="-v"
    )
    
    print(f"Reporte JUnit - Estado: {result_junit['status']}")


async def ejemplo_orquestador_testing():
    """Ejemplo de uso del orquestador para testing"""
    print("\n=== Ejemplo: Orquestador de Testing ===")
    
    orchestrator = AuditOrchestrator()
    
    # Ejecutar suite de tests
    result = await orchestrator.run_test_suite(
        service_name="mcp-service",
        test_type="pytest",
        additional_args="-v"
    )
    
    print(f"Estado del orquestador: {result['status']}")
    print(f"Tipo de test: {result['test_type']}")
    
    if result['success']:
        print("✅ Orquestador ejecutó tests exitosamente")
    else:
        print("❌ Error en el orquestador")


async def ejemplo_auditoria_completa():
    """Ejemplo de auditoría completa con health checks y tests"""
    print("\n=== Ejemplo: Auditoría Completa ===")
    
    orchestrator = AuditOrchestrator()
    
    result = await orchestrator.run_comprehensive_audit(
        service_name="mcp-service",
        include_tests=True
    )
    
    print(f"Estado general: {result['overall_status']}")
    print(f"Estado de health: {result['summary']['health_status']}")
    print(f"Estado de tests: {result['summary']['test_status']}")
    
    if result['summary']['recommendations']:
        print("Recomendaciones:")
        for rec in result['summary']['recommendations']:
            print(f"  - {rec}")


async def main():
    """Función principal que ejecuta todos los ejemplos"""
    print("🚀 Ejemplos de Herramientas de Testing del MCP")
    print("=" * 50)
    
    try:
        # Ejecutar ejemplos básicos
        await ejemplo_testing_basico()
        await ejemplo_testing_con_coverage()
        await ejemplo_testing_archivo_especifico()
        await ejemplo_testing_con_marcadores()
        await ejemplo_testing_paralelo()
        await ejemplo_testing_con_reportes()
        
        # Ejecutar ejemplos del orquestador
        await ejemplo_orquestador_testing()
        await ejemplo_auditoria_completa()
        
        print("\n✅ Todos los ejemplos ejecutados correctamente")
        
    except Exception as e:
        print(f"\n❌ Error durante la ejecución: {e}")
        print("Asegúrate de que el contenedor 'mcp-service' esté ejecutándose")


if __name__ == "__main__":
    # Ejecutar ejemplos
    asyncio.run(main()) 