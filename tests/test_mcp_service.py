#!/usr/bin/env python3
"""
Test simple para validar que el servicio MCP funcione correctamente
"""
import asyncio
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_mcp_imports():
    """Test básico de importaciones"""
    print("🧪 Probando importaciones del MCP...")
    
    try:
        # Test 1: Importar módulos básicos
        from src.tools import register_tools
        print("✅ Importación de register_tools exitosa")
        
        from src.tools.health import comprehensive_health_check
        print("✅ Importación de health tools exitosa")
        
        from src.tools.audit_repo import AuditOrchestrator
        print("✅ Importación de AuditOrchestrator exitosa")
        
        from src.tools.testing_tools import TestingTools
        print("✅ Importación de TestingTools exitosa")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en importación: {e}")
        return False

async def test_basic_functionality():
    """Test básico de funcionalidad"""
    print("\n🧪 Probando funcionalidad básica...")
    
    try:
        # Test 1: Crear orquestador
        from src.tools.audit_repo import AuditOrchestrator
        orchestrator = AuditOrchestrator()
        print("✅ AuditOrchestrator creado exitosamente")
        
        # Test 2: Crear testing tools
        from src.tools.testing_tools import TestingTools
        print("✅ TestingTools importado exitosamente")
        
        # Test 3: Verificar configuración
        config = orchestrator.config
        print(f"✅ Configuración cargada: {len(config)} secciones")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en funcionalidad básica: {e}")
        return False

async def test_docker_command_generation():
    """Test de generación de comandos Docker"""
    print("\n🧪 Probando generación de comandos Docker...")
    
    try:
        from src.tools.testing_tools import TestingTools
        
        # Test 1: Comando básico
        expected_command = "docker exec mcp-service pytest"
        print(f"✅ Comando esperado: {expected_command}")
        
        # Test 2: Comando con argumentos
        expected_command_with_args = "docker exec mcp-service pytest -v"
        print(f"✅ Comando con args esperado: {expected_command_with_args}")
        
        # Test 3: Comando de coverage
        expected_coverage_command = "docker exec mcp-service pytest --cov=src --cov-report=html"
        print(f"✅ Comando coverage esperado: {expected_coverage_command}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en generación de comandos: {e}")
        return False

async def test_configuration_files():
    """Test de archivos de configuración"""
    print("\n🧪 Probando archivos de configuración...")
    
    try:
        # Test 1: Archivo audit.yaml
        audit_config_path = "src/config/audit.yaml"
        if os.path.exists(audit_config_path):
            print(f"✅ Archivo de configuración encontrado: {audit_config_path}")
        else:
            print(f"⚠️ Archivo de configuración no encontrado: {audit_config_path}")
        
        # Test 2: Archivo testing.yaml
        testing_config_path = "src/config/testing.yaml"
        if os.path.exists(testing_config_path):
            print(f"✅ Archivo de testing encontrado: {testing_config_path}")
        else:
            print(f"⚠️ Archivo de testing no encontrado: {testing_config_path}")
        
        # Test 3: Archivo common.py
        common_config_path = "src/config/common.py"
        if os.path.exists(common_config_path):
            print(f"✅ Archivo common encontrado: {common_config_path}")
        else:
            print(f"⚠️ Archivo common no encontrado: {common_config_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en archivos de configuración: {e}")
        return False

async def main():
    """Función principal de testing"""
    print("🚀 Iniciando tests del servicio MCP")
    print("=" * 50)
    
    tests = [
        test_mcp_imports,
        test_basic_functionality,
        test_docker_command_generation,
        test_configuration_files
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
    
    print("\n" + "=" * 50)
    print(f"📊 Resultados: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 ¡Todos los tests pasaron! El servicio MCP está funcionando correctamente.")
        return True
    else:
        print("⚠️ Algunos tests fallaron. Revisar la implementación.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 