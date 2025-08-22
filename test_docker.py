#!/usr/bin/env python3
"""
Script de prueba para ejecutar tests con Docker
"""
import subprocess
import sys
import os


def run_docker_tests():
    """Ejecuta los tests usando Docker"""
    container_name = "mcp-service"
    
    print("🐳 Ejecutando tests con Docker...")
    print("=" * 50)
    
    try:
        # Comando para ejecutar tests
        cmd = f"docker exec {container_name} pytest tests/ -v"
        print(f"Comando: {cmd}")
        
        # Ejecutar el comando
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # Mostrar salida
        if result.stdout:
            print("\n📤 STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("\n⚠️  STDERR:")
            print(result.stderr)
        
        # Mostrar resultado
        print(f"\n🎯 Resultado: {'✅ EXITOSO' if result.returncode == 0 else '❌ FALLÓ'}")
        print(f"Código de salida: {result.returncode}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error ejecutando tests: {e}")
        return False


def run_specific_test(test_path):
    """Ejecuta un test específico"""
    container_name = "mcp-service"
    
    print(f"🧪 Ejecutando test específico: {test_path}")
    print("=" * 50)
    
    try:
        cmd = f"docker exec {container_name} pytest {test_path} -v"
        print(f"Comando: {cmd}")
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            print("\n📤 STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("\n⚠️  STDERR:")
            print(result.stderr)
        
        print(f"\n🎯 Resultado: {'✅ EXITOSO' if result.returncode == 0 else '❌ FALLÓ'}")
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error ejecutando test: {e}")
        return False


def run_tests_with_coverage():
    """Ejecuta tests con coverage"""
    container_name = "mcp-service"
    
    print("📊 Ejecutando tests con coverage...")
    print("=" * 50)
    
    try:
        cmd = f"docker exec {container_name} pytest tests/ --cov=src --cov-report=term-missing -v"
        print(f"Comando: {cmd}")
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            print("\n📤 STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("\n⚠️  STDERR:")
            print(result.stderr)
        
        print(f"\n🎯 Resultado: {'✅ EXITOSO' if result.returncode == 0 else '❌ FALLÓ'}")
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error ejecutando tests con coverage: {e}")
        return False


def main():
    """Función principal"""
    print("🚀 MCP Health Check - Ejecutor de Tests Docker")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "coverage":
            success = run_tests_with_coverage()
        elif command == "test" and len(sys.argv) > 2:
            test_path = sys.argv[2]
            success = run_specific_test(test_path)
        else:
            print("❌ Comando no válido")
            print("Uso:")
            print("  python test_docker.py                    # Ejecuta todos los tests")
            print("  python test_docker.py coverage          # Tests con coverage")
            print("  python test_docker.py test tests/test_models.py  # Test específico")
            sys.exit(1)
    else:
        # Ejecutar todos los tests por defecto
        success = run_docker_tests()
    
    # Salir con código apropiado
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 