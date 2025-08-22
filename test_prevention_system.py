#!/usr/bin/env python3
"""
Test del sistema de prevención de archivos no permitidos
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.insert(0, str(Path(__file__).parent))

from src.tools.prevention_tools import (
    prevent_makefile_creation,
    audit_makefile_presence,
    suggest_alternatives,
    get_prevention_status
)

def test_prevention_system():
    """Prueba el sistema de prevención"""
    print("🧪 TESTING SISTEMA DE PREVENCIÓN DE ARCHIVOS")
    print("=" * 60)
    
    # Test 1: Estado de prevención
    print("\n1️⃣  Verificando estado de prevención...")
    status = get_prevention_status(".")
    if status["success"]:
        print("✅ Estado de prevención obtenido correctamente")
        print(f"   - Reglas totales: {status['total_rules']}")
        print(f"   - Makefiles bloqueados: {status['prevention_rules']['makefiles']['enabled']}")
        print(f"   - Scripts .sh bloqueados: {status['prevention_rules']['shell_scripts']['enabled']}")
    else:
        print(f"❌ Error: {status['error']}")
        return False
    
    # Test 2: Alternativas para Makefiles
    print("\n2️⃣  Verificando alternativas para Makefiles...")
    alternatives = suggest_alternatives("makefile", ".")
    if alternatives["success"]:
        print("✅ Alternativas para Makefiles obtenidas")
        print(f"   - Mensaje: {alternatives['error_message']}")
        print(f"   - Alternativas: {len(alternatives['alternatives'])} encontradas")
        for alt in alternatives['alternatives'][:3]:
            print(f"     • {alt}")
    else:
        print(f"❌ Error: {alternatives['error']}")
        return False
    
    # Test 3: Alternativas para Scripts Shell
    print("\n3️⃣  Verificando alternativas para Scripts Shell...")
    shell_alternatives = suggest_alternatives("shell_script", ".")
    if shell_alternatives["success"]:
        print("✅ Alternativas para Scripts Shell obtenidas")
        print(f"   - Mensaje: {shell_alternatives['error_message']}")
        print(f"   - Alternativas: {len(shell_alternatives['alternatives'])} encontradas")
        for alt in shell_alternatives['alternatives'][:3]:
            print(f"     • {alt}")
    else:
        print(f"❌ Error: {shell_alternatives['error']}")
        return False
    
    # Test 4: Prevención en directorio actual
    print("\n4️⃣  Verificando prevención en directorio actual...")
    prevention = prevent_makefile_creation(".")
    if prevention["success"]:
        print("✅ Prevención aplicada correctamente")
        print(f"   - Makefiles bloqueados: {prevention['makefiles_blocked']}")
        print(f"   - Violaciones existentes: {len(prevention['existing_violations'])}")
        if prevention['existing_violations']:
            print("   🚨 Violaciones detectadas:")
            for violation in prevention['existing_violations']:
                print(f"     • {violation['file_path']}: {violation['error_message']}")
    else:
        print(f"❌ Error: {prevention['error']}")
        return False
    
    # Test 5: Auditoría de Makefiles
    print("\n5️⃣  Realizando auditoría de Makefiles...")
    audit = audit_makefile_presence(".")
    if audit["success"]:
        print("✅ Auditoría completada correctamente")
        print(f"   - Microservicios encontrados: {audit['total_microservices']}")
        print(f"   - Violaciones totales: {audit['total_makefile_violations']}")
        print(f"   - Prevención activa: Makefiles={audit['prevention_summary']['makefiles_blocked']}, Shell={audit['prevention_summary']['shell_scripts_blocked']}")
    else:
        print(f"❌ Error: {audit['error']}")
        return False
    
    # Test 6: Verificar prevención de rutas relativas
    print("\n6️⃣  Verificando prevención de rutas relativas problemáticas...")
    status_with_paths = get_prevention_status(".")
    if status_with_paths["success"]:
        print("✅ Prevención de rutas verificada correctamente")
        if 'path_prevention' in status_with_paths['prevention_rules']:
            path_rule = status_with_paths['prevention_rules']['path_prevention']
            print(f"   - Rutas relativas bloqueadas: {path_rule['enabled']}")
            print(f"   - Patrones bloqueados: {len(path_rule['blocked_patterns'])}")
            print(f"   - Excepciones permitidas: {len(path_rule['allowed_exceptions'])}")
            print(f"   - Alternativas sugeridas: {len(path_rule['alternatives'])}")
            
            # Mostrar algunas alternativas
            for alt in path_rule['alternatives'][:3]:
                print(f"     • {alt}")
        else:
            print("❌ Regla de prevención de rutas no encontrada")
            return False
    else:
        print(f"❌ Error: {status_with_paths['error']}")
        return False
    
    print("\n🎉 TODOS LOS TESTS PASARON EXITOSAMENTE!")
    print("🛡️  El sistema de prevención está funcionando correctamente")
    print("🚫 Previene Makefiles, scripts .sh y rutas relativas problemáticas")
    return True

if __name__ == "__main__":
    success = test_prevention_system()
    sys.exit(0 if success else 1) 