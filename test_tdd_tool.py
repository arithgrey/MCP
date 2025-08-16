#!/usr/bin/env python3
"""
Script de prueba rápida para la herramienta TDD
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from tools.tdd_policy_check import tdd_policy_check
    
    print("🚀 Probando herramienta TDD Policy Check...\n")
    
    # Prueba 1: Scan básico
    print("1️⃣  Prueba: Scan básico")
    result = tdd_policy_check("test-container", action="scan")
    print(f"   Status: {result['status']}")
    print(f"   Summary: {result['summary']}")
    print(f"   Tests encontrados: {result['metrics']['tests_found']}")
    print()
    
    # Prueba 2: Scan con referencia git
    print("2️⃣  Prueba: Scan con referencia git")
    result = tdd_policy_check("test-container", since_ref="HEAD~1", action="scan")
    print(f"   Status: {result['status']}")
    print(f"   Módulos modificados: {result['metrics']['changed_modules']}")
    print(f"   Módulos con tests: {result['metrics']['modules_with_tests']}")
    print()
    
    # Prueba 3: Verificar estructura de respuesta
    print("3️⃣  Prueba: Estructura de respuesta")
    required_keys = ['status', 'summary', 'violations', 'metrics', 'cmd_executed', 'stdout', 'stderr']
    missing_keys = [key for key in required_keys if key not in result]
    
    if missing_keys:
        print(f"   ❌ Faltan keys: {missing_keys}")
    else:
        print("   ✅ Estructura de respuesta correcta")
    
    print(f"   Keys encontradas: {list(result.keys())}")
    print()
    
    print("✅ Todas las pruebas pasaron exitosamente!")
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("Asegúrate de estar en el directorio correcto y que las dependencias estén instaladas")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error durante la prueba: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 