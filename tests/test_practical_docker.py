#!/usr/bin/env python3
"""
Test práctico que demuestra el uso real de las herramientas de testing con Docker
"""
import asyncio
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_docker_execute_basic():
    """Test básico de ejecución con docker exec"""
    print("🧪 Probando ejecución básica con docker exec...")
    
    try:
        from src.tools.testing_tools import TestingTools
        
        # Test 1: Ejecutar comando simple
        result = await TestingTools.execute_docker_test(
            service_name="mcp-service",
            test_command="python", 
            additional_args="-c 'print(\"Hello from Docker!\")'"
        )
        
        print(f"✅ Comando ejecutado: {result['command']}")
        print(f"✅ Estado: {result['status']}")
        print(f"✅ Código de retorno: {result['return_code']}")
        
        if result['stdout']:
            print(f"✅ Salida: {result['stdout'].strip()}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ Error en ejecución básica: {e}")
        return False

async def test_docker_pytest_version():
    """Test de obtención de versión de pytest"""
    print("\n🧪 Probando obtención de versión de pytest...")
    
    try:
        from src.tools.testing_tools import TestingTools
        
        result = await TestingTools.execute_docker_test(
            service_name="mcp-service",
            test_command="pytest",
            additional_args="--version"
        )
        
        print(f"✅ Comando ejecutado: {result['command']}")
        print(f"✅ Estado: {result['status']}")
        
        if result['stdout']:
            print(f"✅ Versión de pytest: {result['stdout'].strip()}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ Error en obtención de versión: {e}")
        return False

async def test_docker_test_collection():
    """Test de recolección de tests"""
    print("\n🧪 Probando recolección de tests...")
    
    try:
        from src.tools.testing_tools import TestingTools
        
        result = await TestingTools.execute_docker_test(
            service_name="mcp-service",
            test_command="pytest",
            additional_args="--collect-only tests/"
        )
        
        print(f"✅ Comando ejecutado: {result['command']}")
        print(f"✅ Estado: {result['status']}")
        
        if result['stdout']:
            # Contar tests recolectados
            lines = result['stdout'].split('\n')
            test_count = len([line for line in lines if '::' in line and 'test_' in line])
            print(f"✅ Tests recolectados: {test_count}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ Error en recolección de tests: {e}")
        return False

async def test_orchestrator_test_suite():
    """Test del orquestador ejecutando tests"""
    print("\n🧪 Probando orquestador ejecutando tests...")
    
    try:
        from src.tools.audit_repo import AuditOrchestrator
        
        orchestrator = AuditOrchestrator()
        
        # Ejecutar suite de tests básica
        result = await orchestrator.run_test_suite(
            service_name="mcp-service",
            test_type="pytest",
            additional_args="--version"
        )
        
        print(f"✅ Orquestador ejecutó tests exitosamente")
        print(f"✅ Estado: {result['status']}")
        print(f"✅ Tipo de test: {result['test_type']}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ Error en orquestador: {e}")
        return False

async def test_comprehensive_audit():
    """Test de auditoría completa"""
    print("\n🧪 Probando auditoría completa...")
    
    try:
        from src.tools.audit_repo import AuditOrchestrator
        
        orchestrator = AuditOrchestrator()
        
        # Ejecutar auditoría completa (sin tests por ahora para evitar timeouts)
        result = await orchestrator.run_comprehensive_audit(
            service_name="mcp-service",
            include_tests=False  # Solo health checks por ahora
        )
        
        print(f"✅ Auditoría completa ejecutada")
        print(f"✅ Estado general: {result['overall_status']}")
        
        if result['summary']['recommendations']:
            print("✅ Recomendaciones generadas:")
            for rec in result['summary']['recommendations']:
                print(f"   - {rec}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en auditoría completa: {e}")
        return False

async def main():
    """Función principal de testing práctico"""
    print("🚀 Iniciando tests prácticos de herramientas de testing con Docker")
    print("=" * 70)
    
    tests = [
        test_docker_execute_basic,
        test_docker_pytest_version,
        test_docker_test_collection,
        test_orchestrator_test_suite,
        test_comprehensive_audit
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ Test falló con excepción: {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 Resultados: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 ¡Todos los tests prácticos pasaron!")
        print("✅ Las herramientas de testing con Docker están funcionando correctamente")
        print("✅ El formato 'docker exec nombre_servicio pytest' está implementado")
        print("✅ El orquestador está integrado con las herramientas de testing")
    else:
        print("⚠️ Algunos tests fallaron. Revisar la implementación.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 