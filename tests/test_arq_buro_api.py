#!/usr/bin/env python3
"""
Test del API Analyzer con arq-buro-service.tysonprod.com
"""
import asyncio
import json
from src.tools.api_analyzer import analyze_api_service, generate_api_docs


async def test_arq_buro_api():
    """Prueba el API Analyzer con arq-buro-service"""
    
    print("🔍 ANALIZANDO API: arq-buro-service.tysonprod.com")
    print("=" * 60)
    
    # Analizar la API
    result = await analyze_api_service(
        "https://arq-buro-service.tysonpssssrod.com", 
        "/openapi.json"
    )
    
    if result["success"]:
        print("✅ API analizada exitosamente!")
        print()
        
        # Información básica
        info = result["analysis"]["info"]
        print(f"📊 Título: {info['title']}")
        print(f"🔢 Versión: {info['version']}")
        print(f"📝 Descripción: {info['description']}")
        print()
        
        # Estadísticas
        stats = result["analysis"]["statistics"]
        print(f"📍 Total Endpoints: {stats['total_endpoints']}")
        print(f"🏗️  Total Modelos: {stats['total_models']}")
        print(f"🏷️  Total Tags: {stats['total_tags']}")
        print(f"🌐 Versión OpenAPI: {stats['openapi_version']}")
        print()
        
        # Distribución de métodos
        print("📋 DISTRIBUCIÓN DE MÉTODOS HTTP:")
        for method, count in stats["method_distribution"].items():
            if count > 0:
                print(f"  {method}: {count}")
        print()
        
        # Tags disponibles
        print("🏷️  TAGS DISPONIBLES:")
        for tag in result["analysis"]["tags"]:
            print(f"  - {tag.name}: {tag.description}")
        print()
        
        # Endpoints de ejemplo
        print("📋 ENDPOINTS DE EJEMPLO:")
        endpoints = result["analysis"]["endpoints"]
        for i, endpoint in enumerate(endpoints[:5]):
            print(f"  {i+1}. {endpoint.methods[0]} {endpoint.path}")
            if endpoint.summary:
                print(f"     {endpoint.summary}")
            if endpoint.tags:
                print(f"     Tags: {', '.join(endpoint.tags)}")
            print()
        
        # Seguridad
        security = result["analysis"]["security"]
        print(f"🔐 AUTENTICACIÓN:")
        print(f"  Requiere autenticación: {'Sí' if security['requires_authentication'] else 'No'}")
        if security["security_schemes"]:
            print(f"  Esquemas de seguridad: {list(security['security_schemes'].keys())}")
        print()
        
        # Generar documentación
        print("📚 GENERANDO DOCUMENTACIÓN...")
        docs = await generate_api_docs(
            "https://arq-buro-servicessss.tysonprod.com", 
            "/openapi.json"
        )
        
        if docs["success"]:
            print("✅ Documentación generada!")
            doc_summary = docs["documentation"]["summary"]
            print(f"📊 Nivel de complejidad: {doc_summary['complexity_level']}")
            print(f"🎯 Funcionalidad principal: {', '.join(doc_summary['main_functionality'][:3])}")
            
            if doc_summary['recommendations']:
                print(f"\n💡 RECOMENDACIONES:")
                for rec in doc_summary['recommendations']:
                    print(f"  - {rec}")
        else:
            print(f"❌ Error generando documentación: {docs.get('error')}")
        
    else:
        print(f"❌ Error analizando API: {result.get('error')}")
        print(f"URL probada: {result.get('url')}")


if __name__ == "__main__":
    asyncio.run(test_arq_buro_api()) 