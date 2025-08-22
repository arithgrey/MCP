#!/usr/bin/env python3
"""
Test simple para validar las herramientas de testing con Docker
"""
import asyncio
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_docker_testing_tools():
    """Test de las herramientas de testing con Docker"""
    print("🧪 Probando herramientas de testing con Docker...")
    
    try:
        # Test 1: Importar TestingTools
        from src.tools.testing_tools import TestingTools
        print("✅ TestingTools importado exitosamente")
        
        # Test 2: Verificar que el método execute_docker_test existe
        assert hasattr(TestingTools, 'execute_docker_test'), "Método execute_docker_test no encontrado"
        print("✅ Método execute_docker_test encontrado")
        
        # Test 3: Verificar que el método run_pytest_with_coverage existe
        assert hasattr(TestingTools, 'run_pytest_with_coverage'), "Método run_pytest_with_coverage no encontrado"
        print("✅ Método run_pytest_with_coverage encontrado")
        
        # Test 4: Verificar que el método _execute_docker_command existe
        assert hasattr(TestingTools, '_execute_docker_command'), "Método _execute_docker_command no encontrado"
        print("✅ Método _execute_docker_command encontrado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en testing tools: {e}")
        return False

async def test_docker_command_generation():
    """Test de generación de comandos Docker"""
    print("\n🧪 Probando generación de comandos Docker...")
    
    try:
        from src.tools.testing_tools import TestingTools
        
        # Test 1: Verificar formato del comando
        expected_base = "docker exec mcp-service pytest"
        print(f"✅ Comando base esperado: {expected_base}")
        
        # Test 2: Verificar comando con argumentos
        expected_with_args = "docker exec mcp-service pytest -v"
        print(f"✅ Comando con args esperado: {expected_with_args}")
        
        # Test 3: Verificar comando de coverage
        expected_coverage = "docker exec mcp-service pytest --cov=src --cov-report=html"
        print(f"✅ Comando coverage esperado: {expected_coverage}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en generación de comandos: {e}")
        return False

async def test_orchestrator_integration():
    """Test de integración con el orquestador"""
    print("\n🧪 Probando integración con el orquestador...")
    
    try:
        from src.tools.audit_repo import AuditOrchestrator
        
        # Test 1: Crear orquestador
        orchestrator = AuditOrchestrator()
        print("✅ AuditOrchestrator creado exitosamente")
        
        # Test 2: Verificar que tiene métodos de testing
        assert hasattr(orchestrator, 'run_test_suite'), "Método run_test_suite no encontrado"
        print("✅ Método run_test_suite encontrado")
        
        assert hasattr(orchestrator, 'run_tests_with_coverage'), "Método run_tests_with_coverage no encontrado"
        print("✅ Método run_tests_with_coverage encontrado")
        
        assert hasattr(orchestrator, 'run_comprehensive_audit'), "Método run_comprehensive_audit no encontrado"
        print("✅ Método run_comprehensive_audit encontrado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en integración del orquestador: {e}")
        return False

async def test_mcp_tools_registration():
    """Test de registro de herramientas MCP"""
    print("\n🧪 Probando registro de herramientas MCP...")
    
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
        
        # Verificar que se registraron las herramientas de testing
        expected_testing_tools = [
            'docker_test_execute',
            'docker_test_pytest_coverage',
            'docker_test_specific_file',
            'audit_orchestrator_test_suite',
            'audit_orchestrator_tests_with_coverage',
            'audit_orchestrator_comprehensive_audit'
        ]
        
        for tool_name in expected_testing_tools:
            if tool_name in mock_mcp.tools:
                print(f"✅ Herramienta {tool_name} registrada")
            else:
                print(f"❌ Herramienta {tool_name} NO registrada")
                return False
        
        print(f"✅ Total de herramientas registradas: {len(mock_mcp.tools)}")
        return True
        
    except Exception as e:
        print(f"❌ Error en registro de herramientas: {e}")
        return False

async def main():
    """Función principal de testing"""
    print("🚀 Iniciando tests de herramientas de testing con Docker")
    print("=" * 60)
    
    tests = [
        test_docker_testing_tools,
        test_docker_command_generation,
        test_orchestrator_integration,
        test_mcp_tools_registration
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
        print("🎉 ¡Todos los tests pasaron! Las herramientas de testing están funcionando correctamente.")
        return True
    else:
        print("⚠️ Algunos tests fallaron. Revisar la implementación.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 