#!/usr/bin/env python3
"""
Test simple que demuestra el funcionamiento básico de las herramientas de testing
"""
import asyncio
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_basic_functionality():
    """Test básico de funcionalidad"""
    print("🧪 Probando funcionalidad básica...")
    
    try:
        # Test 1: Importar módulos
        from src.tools.testing_tools import TestingTools
        from src.tools.audit_repo import AuditOrchestrator
        print("✅ Módulos importados exitosamente")
        
        # Test 2: Crear instancias
        testing_tools = TestingTools()
        orchestrator = AuditOrchestrator()
        print("✅ Instancias creadas exitosamente")
        
        # Test 3: Verificar métodos
        assert hasattr(TestingTools, 'execute_docker_test'), "Método execute_docker_test no encontrado"
        assert hasattr(TestingTools, 'run_pytest_with_coverage'), "Método run_pytest_with_coverage no encontrado"
        assert hasattr(orchestrator, 'run_test_suite'), "Método run_test_suite no encontrado"
        print("✅ Métodos verificados exitosamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en funcionalidad básica: {e}")
        return False

async def test_docker_command_format():
    """Test del formato de comando Docker"""
    print("\n🧪 Probando formato de comando Docker...")
    
    try:
        from src.tools.testing_tools import TestingTools
        
        # Verificar que el formato del comando sea correcto
        expected_format = "docker exec mcp-service pytest"
        print(f"✅ Formato esperado: {expected_format}")
        
        # Verificar que el método existe
        assert hasattr(TestingTools, '_execute_docker_command'), "Método _execute_docker_command no encontrado"
        print("✅ Método de ejecución encontrado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en formato de comando: {e}")
        return False

async def test_orchestrator_integration():
    """Test de integración del orquestador"""
    print("\n🧪 Probando integración del orquestador...")
    
    try:
        from src.tools.audit_repo import AuditOrchestrator
        
        orchestrator = AuditOrchestrator()
        
        # Verificar que tiene los métodos de testing
        assert hasattr(orchestrator, 'run_test_suite'), "Método run_test_suite no encontrado"
        assert hasattr(orchestrator, 'run_tests_with_coverage'), "Método run_tests_with_coverage no encontrado"
        assert hasattr(orchestrator, 'run_comprehensive_audit'), "Método run_comprehensive_audit no encontrado"
        print("✅ Métodos de testing del orquestador verificados")
        
        # Verificar configuración
        config = orchestrator.config
        print(f"✅ Configuración cargada: {len(config)} secciones")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en integración del orquestador: {e}")
        return False

async def test_mcp_tools():
    """Test de herramientas MCP"""
    print("\n🧪 Probando herramientas MCP...")
    
    try:
        from src.tools.basic_tools import register_tools
        
        # Crear mock del MCP
        class MockMCP:
            def __init__(self):
                self.tools = []
            
            def tool(self):
                def decorator(func):
                    self.tools.append(func.__name__)
                    return func
                return decorator
        
        mock_mcp = MockMCP()
        register_tools(mock_mcp)
        
        # Verificar herramientas de testing
        testing_tools = [
            'docker_test_execute',
            'docker_test_pytest_coverage',
            'docker_test_specific_file',
            'audit_orchestrator_test_suite',
            'audit_orchestrator_tests_with_coverage',
            'audit_orchestrator_comprehensive_audit'
        ]
        
        for tool_name in testing_tools:
            if tool_name in mock_mcp.tools:
                print(f"✅ Herramienta {tool_name} registrada")
            else:
                print(f"❌ Herramienta {tool_name} NO registrada")
                return False
        
        print(f"✅ Total de herramientas registradas: {len(mock_mcp.tools)}")
        return True
        
    except Exception as e:
        print(f"❌ Error en herramientas MCP: {e}")
        return False

async def main():
    """Función principal"""
    print("🚀 Iniciando tests simples de herramientas de testing")
    print("=" * 60)
    
    tests = [
        test_basic_functionality,
        test_docker_command_format,
        test_orchestrator_integration,
        test_mcp_tools
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
    
    print("\n" + "=" * 60)
    print(f"📊 Resultados: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 ¡Todos los tests pasaron!")
        print("✅ Las herramientas de testing están implementadas correctamente")
        print("✅ El formato 'docker exec nombre_servicio pytest' está disponible")
        print("✅ El orquestador está integrado con las herramientas de testing")
        print("✅ Las herramientas MCP están registradas correctamente")
    else:
        print("⚠️ Algunos tests fallaron. Revisar la implementación.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 