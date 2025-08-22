#!/usr/bin/env python3
"""
Test del API Analyzer - Demuestra las nuevas capacidades del MCP
"""
import asyncio
import json
from src.tools.api_analyzer import analyze_api_service, generate_api_docs, APIAnalyzer


async def test_api_analyzer():
    """Prueba las funcionalidades del API Analyzer"""
    
    print("🚀 Probando API Analyzer del MCP")
    print("=" * 50)
    
    # URLs de ejemplo para probar
    test_apis = [
        "https://petstore.swagger.io/v2",
        "https://api.github.com",
        "https://jsonplaceholder.typicode.com"
    ]
    
    for api_url in test_apis:
        print(f"\n🔍 Analizando API: {api_url}")
        print("-" * 40)
        
        try:
            # Análisis completo de la API
            analysis = await analyze_api_service(api_url, timeout_ms=15000)
            
            if analysis["success"]:
                print(f"✅ API analizada exitosamente")
                print(f"📊 Título: {analysis['analysis']['info']['title']}")
                print(f"🔢 Versión: {analysis['analysis']['info']['version']}")
                print(f"📍 Endpoints: {analysis['analysis']['statistics']['total_endpoints']}")
                print(f"🏗️  Modelos: {analysis['analysis']['statistics']['total_models']}")
                print(f"🏷️  Tags: {analysis['analysis']['statistics']['total_tags']}")
                print(f"🔐 Autenticación: {'Sí' if analysis['analysis']['security']['requires_authentication'] else 'No'}")
                
                # Mostrar algunos endpoints de ejemplo
                endpoints = analysis["analysis"]["endpoints"]
                if endpoints:
                    print(f"\n📋 Endpoints de ejemplo:")
                    for i, endpoint in enumerate(endpoints[:3]):
                        print(f"  {i+1}. {endpoint.methods[0]} {endpoint.path}")
                        if endpoint.summary:
                            print(f"     {endpoint.summary}")
                
                # Generar documentación
                print(f"\n📚 Generando documentación...")
                docs = await generate_api_docs(api_url, timeout_ms=15000)
                
                if docs["success"]:
                    print(f"✅ Documentación generada")
                    summary = docs["documentation"]["summary"]
                    print(f"📊 Nivel de complejidad: {summary['complexity_level']}")
                    print(f"🎯 Funcionalidad principal: {', '.join(summary['main_functionality'][:3])}")
                    
                    if summary['recommendations']:
                        print(f"💡 Recomendaciones:")
                        for rec in summary['recommendations'][:3]:
                            print(f"  - {rec}")
                
            else:
                print(f"❌ Error al analizar API: {analysis.get('error', 'Error desconocido')}")
                
        except Exception as e:
            print(f"❌ Excepción durante el análisis: {str(e)}")
        
        print("\n" + "=" * 50)


async def test_specific_api():
    """Prueba con una API específica (Petstore)"""
    
    print("\n🎯 Prueba específica con Petstore API")
    print("=" * 50)
    
    api_url = "https://petstore.swagger.io/v2"
    
    try:
        # Crear instancia del analizador
        analyzer = APIAnalyzer(timeout_ms=15000)
        
        # Análisis paso a paso
        print(f"🔍 Detectando endpoint de Swagger...")
        swagger_info = await analyzer._detect_swagger_endpoint(api_url)
        
        if swagger_info["found"]:
            print(f"✅ Swagger detectado en: {swagger_info['best_endpoint']}")
            print(f"⏱️  Latencia: {swagger_info['latency_ms']:.2f}ms")
            
            # Obtener especificación
            print(f"📥 Obteniendo especificación OpenAPI...")
            spec_url = f"{api_url}{swagger_info['best_endpoint']}"
            spec = await analyzer._fetch_openapi_spec(spec_url)
            
            if spec["success"]:
                print(f"✅ Especificación obtenida")
                print(f"📊 Versión OpenAPI: {spec['spec'].get('openapi', 'N/A')}")
                
                # Analizar
                print(f"🔬 Analizando especificación...")
                analysis = await analyzer._analyze_openapi_spec(spec["spec"], api_url)
                
                print(f"✅ Análisis completado")
                print(f"📋 Endpoints encontrados: {len(analysis['endpoints'])}")
                print(f"🏗️  Modelos encontrados: {len(analysis['models'])}")
                print(f"🏷️  Tags encontrados: {len(analysis['tags'])}")
                
                # Mostrar algunos modelos
                if analysis['models']:
                    print(f"\n🏗️  Modelos de ejemplo:")
                    for i, model in enumerate(analysis['models'][:3]):
                        print(f"  {i+1}. {model.name} ({model.type})")
                        if model.description:
                            print(f"     {model.description[:100]}...")
                
            else:
                print(f"❌ Error al obtener especificación: {spec.get('error')}")
        else:
            print(f"❌ No se detectó endpoint de Swagger")
            
    except Exception as e:
        print(f"❌ Excepción durante la prueba específica: {str(e)}")


def main():
    """Función principal"""
    print("🧪 Test del API Analyzer del MCP")
    print("Este test demuestra las nuevas capacidades para entender APIs")
    
    # Ejecutar tests
    asyncio.run(test_api_analyzer())
    asyncio.run(test_specific_api())
    
    print("\n🎉 Test completado!")
    print("\n💡 El MCP ahora puede:")
    print("  - Detectar automáticamente endpoints de Swagger/OpenAPI")
    print("  - Leer y parsear especificaciones completas")
    print("  - Entender la estructura de la API")
    print("  - Analizar endpoints, métodos, parámetros")
    print("  - Generar documentación inteligente")
    print("  - Identificar patrones y hacer recomendaciones")


if __name__ == "__main__":
    main() 