#!/usr/bin/env python3
"""
Test específico para la prevención de rutas relativas problemáticas
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.insert(0, str(Path(__file__).parent))

from src.tools.prevention_tools import get_prevention_status
from src.tools.file_preventor import FilePreventor
from src.tools.template_loader import TemplateLoader

def test_path_prevention():
    """Prueba la prevención de rutas relativas problemáticas"""
    print("🧪 TESTING PREVENCIÓN DE RUTAS RELATIVAS PROBLEMÁTICAS")
    print("=" * 70)
    
    # Test 1: Verificar que la regla de prevención de rutas esté activa
    print("\n1️⃣  Verificando regla de prevención de rutas...")
    status = get_prevention_status(".")
    if status["success"]:
        print("✅ Estado de prevención obtenido correctamente")
        print(f"   - Reglas totales: {status['total_rules']}")
        print(f"   - Makefiles bloqueados: {status['prevention_rules']['makefiles']['enabled']}")
        print(f"   - Scripts .sh bloqueados: {status['prevention_rules']['shell_scripts']['enabled']}")
        
        # Verificar si existe la regla de prevención de rutas
        if 'path_prevention' in status['prevention_rules']:
            print(f"   - Rutas relativas bloqueadas: {status['prevention_rules']['path_prevention']['enabled']}")
        else:
            print("   ❌ Regla de prevención de rutas no encontrada")
            return False
    else:
        print(f"❌ Error: {status['error']}")
        return False
    
    # Test 2: Verificar el FilePreventor directamente
    print("\n2️⃣  Verificando FilePreventor...")
    template_loader = TemplateLoader()
    template = template_loader.get_template()
    
    if hasattr(template, 'file_prevention') and template.file_prevention:
        file_preventor = FilePreventor(template.file_prevention)
        prevention_summary = file_preventor.get_prevention_summary(Path("."))
        
        print("✅ FilePreventor configurado correctamente")
        print(f"   - Prevención de rutas activa: {prevention_summary['path_prevention_enabled']}")
        print(f"   - Alternativas para rutas: {len(prevention_summary['path_alternatives'])} encontradas")
        
        # Mostrar algunas alternativas
        for alt in prevention_summary['path_alternatives'][:3]:
            print(f"     • {alt}")
    else:
        print("❌ FilePreventor no configurado")
        return False
    
    # Test 3: Crear un archivo de prueba con rutas problemáticas
    print("\n3️⃣  Creando archivo de prueba con rutas problemáticas...")
    test_file = Path("test_problematic_paths.py")
    
    problematic_content = '''
# Este archivo contiene rutas relativas problemáticas
import sys
sys.path.append("../")  # ❌ RUTA PROBLEMÁTICA
sys.path.append("./")   # ❌ RUTA PROBLEMÁTICA

from ..core.models import *  # ❌ IMPORT RELATIVO PROBLEMÁTICO
from .utils import *         # ❌ IMPORT RELATIVO PROBLEMÁTICO

# Rutas de archivos problemáticas
config_path = "../config/settings.yaml"  # ❌ RUTA PROBLEMÁTICA
data_path = "./data/input.csv"          # ❌ RUTA PROBLEMÁTICA
'''
    
    try:
        test_file.write_text(problematic_content)
        print("✅ Archivo de prueba creado")
    except Exception as e:
        print(f"❌ Error creando archivo de prueba: {e}")
        return False
    
    # Test 4: Verificar que el FilePreventor detecte las rutas problemáticas
    print("\n4️⃣  Verificando detección de rutas problemáticas...")
    
    can_create, error_msg, alternatives = file_preventor.can_create_file(test_file, Path("."))
    
    if not can_create:
        print("✅ Ruta problemática detectada correctamente")
        print(f"   - Mensaje de error: {error_msg}")
        print(f"   - Alternativas sugeridas: {len(alternatives)}")
        
        for alt in alternatives[:3]:
            print(f"     • {alt}")
    else:
        print("❌ Ruta problemática NO detectada")
        return False
    
    # Test 5: Verificar que se permitan imports relativos válidos
    print("\n5️⃣  Verificando imports relativos válidos...")
    
    valid_content = '''
# Este archivo contiene imports relativos válidos
from . import utils          # ✅ IMPORT RELATIVO VÁLIDO
from ..core import models    # ✅ IMPORT RELATIVO VÁLIDO

# Rutas absolutas válidas
from src.tools import FilePreventor  # ✅ IMPORT ABSOLUTO
from pathlib import Path             # ✅ IMPORT ESTÁNDAR
'''
    
    valid_file = Path("test_valid_paths.py")
    valid_file.write_text(valid_content)
    
    can_create_valid, _, _ = file_preventor.can_create_file(valid_file, Path("."))
    
    if can_create_valid:
        print("✅ Imports relativos válidos permitidos correctamente")
    else:
        print("❌ Imports relativos válidos bloqueados incorrectamente")
        return False
    
    # Limpiar archivos de prueba
    test_file.unlink(missing_ok=True)
    valid_file.unlink(missing_ok=True)
    
    print("\n🎉 TODOS LOS TESTS DE PREVENCIÓN DE RUTAS PASARON EXITOSAMENTE!")
    print("🛡️  El sistema previene rutas relativas problemáticas correctamente")
    return True

if __name__ == "__main__":
    success = test_path_prevention()
    sys.exit(0 if success else 1) 