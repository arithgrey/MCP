#!/usr/bin/env python3
"""
Ejemplos de uso de la herramienta TDD Policy Check
"""

import json
from src.tools.tdd_policy_check import tdd_policy_check, TDDPolicyChecker


def ejemplo_scan_basico():
    """Ejemplo básico de scan"""
    print("=== Ejemplo: Scan Básico ===")
    
    result = tdd_policy_check(
        container_name="mcp-service",
        action="scan"
    )
    
    print(f"Status: {result['status']}")
    print(f"Summary: {result['summary']}")
    print(f"Métricas: {json.dumps(result['metrics'], indent=2)}")
    
    if result['violations']:
        print("\nViolaciones encontradas:")
        for violation in result['violations']:
            print(f"  - {violation['code']}: {violation['message']}")
            if violation['files']:
                print(f"    Archivos: {', '.join(violation['files'])}")
    
    print("\n" + "="*50)


def ejemplo_scan_con_referencia_git():
    """Ejemplo de scan con referencia git específica"""
    print("=== Ejemplo: Scan con Referencia Git ===")
    
    result = tdd_policy_check(
        container_name="mcp-service",
        since_ref="HEAD~2",  # Analizar cambios desde 2 commits atrás
        action="scan"
    )
    
    print(f"Status: {result['status']}")
    print(f"Summary: {result['summary']}")
    print(f"Módulos modificados: {result['metrics']['changed_modules']}")
    print(f"Módulos con tests: {result['metrics']['modules_with_tests']}")
    
    print("\n" + "="*50)


def ejemplo_ejecutar_tests():
    """Ejemplo de ejecución de tests"""
    print("=== Ejemplo: Ejecutar Tests ===")
    
    # Nota: Este ejemplo requiere que el contenedor esté corriendo
    print("⚠️  Nota: Este ejemplo requiere que el contenedor 'mcp-service' esté corriendo")
    
    result = tdd_policy_check(
        container_name="mcp-service",
        action="run"
    )
    
    print(f"Status: {result['status']}")
    print(f"Summary: {result['summary']}")
    print(f"Comando ejecutado: {result['cmd_executed']}")
    
    if result['stdout']:
        print(f"\nSTDOUT:\n{result['stdout']}")
    
    if result['stderr']:
        print(f"\nSTDERR:\n{result['stderr']}")
    
    print("\n" + "="*50)


def ejemplo_check_completo():
    """Ejemplo de verificación completa"""
    print("=== Ejemplo: Check Completo ===")
    
    result = tdd_policy_check(
        container_name="mcp-service",
        since_ref="HEAD~1",
        action="full_check"
    )
    
    print(f"Status: {result['status']}")
    print(f"Summary: {result['summary']}")
    print(f"Métricas completas: {json.dumps(result['metrics'], indent=2)}")
    
    print("\n" + "="*50)


def ejemplo_uso_directo_clase():
    """Ejemplo de uso directo de la clase TDDPolicyChecker"""
    print("=== Ejemplo: Uso Directo de TDDPolicyChecker ===")
    
    checker = TDDPolicyChecker(".", "mcp-service")
    
    # Ejecutar solo el scan
    scan_result = checker.scan("HEAD~1")
    print(f"Scan - Status: {scan_result.status}")
    print(f"Scan - Summary: {scan_result.summary}")
    
    # Verificar métricas específicas
    print(f"Tests encontrados: {scan_result.metrics['tests_found']}")
    print(f"Tests fuera de tests/: {scan_result.metrics['tests_outside_tests_dir']}")
    
    print("\n" + "="*50)


def main():
    """Función principal que ejecuta todos los ejemplos"""
    print("🚀 Ejemplos de Uso de la Herramienta TDD Policy Check\n")
    
    try:
        ejemplo_scan_basico()
        ejemplo_scan_con_referencia_git()
        ejemplo_ejecutar_tests()
        ejemplo_check_completo()
        ejemplo_uso_directo_clase()
        
        print("✅ Todos los ejemplos ejecutados exitosamente")
        
    except Exception as e:
        print(f"❌ Error ejecutando ejemplos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 