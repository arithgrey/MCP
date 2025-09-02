#!/usr/bin/env python3
"""
Script simple para probar las plantillas configurables
"""
from src.tools.structure_inspector import inspect_microservice_structure
from src.tools.template_loader import TemplateLoader


def test_default_template():
    """Prueba la plantilla por defecto"""
    print("🔧 Probando plantilla por defecto...")
    
    # Obtener información de la plantilla
    loader = TemplateLoader()
    template_info = loader.get_template_info()
    
    print(f"   Nombre: {template_info['name']}")
    print(f"   Archivos requeridos: {template_info['total_required_files']}")
    print(f"   Archivos opcionales: {template_info['total_optional_files']}")
    
    # Probar inspección del directorio actual
    try:
        result = inspect_microservice_structure(".", ".")
        print(f"   Estado: {result.status}")
        print(f"   Score: {result.score:.1f}/100")
        print(f"   Recomendaciones: {len(result.recommendations)}")
    except Exception as e:
        print(f"   Error: {e}")


def test_custom_template():
    """Prueba con una plantilla personalizada"""
    print(f"\n🎨 Probando plantilla personalizada...")
    
    # Crear una plantilla simple
    custom_template = """
default:
  name: "Plantilla Simple"
  description: "Plantilla básica para pruebas"
  
  required_files:
    - name: "Dockerfile"
      description: "Archivo de containerización"
      required: true
      weight: 30
    
    - name: "docker-compose.yml"
      description: "Archivo de orquestación"
      required: true
      weight: 30
    
    - name: ".gitignore"
      description: "Archivo de exclusión de Git"
      required: true
      weight: 20
    
    - name: "tests/"
      description: "Directorio de tests"
      required: true
      weight: 20
      type: "directory"
      must_contain: ["*.py"]

scoring:
  thresholds:
    complete: 70
    incomplete: 40
    poor: 0
  
  warning_penalty: 2
"""
    
    # Guardar plantilla temporal
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
    temp_file.write(custom_template)
    temp_file.close()
    
    print(f"   Plantilla creada en: {temp_file.name}")
    
    try:
        # Probar con plantilla personalizada
        result = inspect_microservice_structure(".", ".", temp_file.name)
        print(f"   Estado: {result.status}")
        print(f"   Score: {result.score:.1f}/100")
        print(f"   Recomendaciones: {len(result.recommendations)}")
        
        # Comparar con plantilla por defecto
        default_result = inspect_microservice_structure(".", ".")
        print(f"   Score por defecto: {default_result.score:.1f}/100")
        print(f"   Diferencia: {result.score - default_result.score:+.1f} puntos")
        
    except Exception as e:
        print(f"   Error: {e}")
    finally:
        # Limpiar archivo temporal
        import os
        os.unlink(temp_file.name)
        print(f"   Archivo temporal eliminado")


def main():
    """Función principal"""
    print("🧪 PRUEBA DE PLANTILLAS CONFIGURABLES")
    print("=" * 50)
    
    test_default_template()
    test_custom_template()
    
    print(f"\n✅ Pruebas completadas!")


if __name__ == "__main__":
    main() 