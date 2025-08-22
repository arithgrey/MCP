#!/usr/bin/env python3
"""
Test de Auditoría Completa: API Analysis + Health Check
"""
import asyncio
from src.tools.api_analyzer import analyze_api_service, generate_api_docs
from src.tools.endpoint_detector import auto_health_check


async def test_comprehensive_audit():
    """Prueba la auditoría completa del API Analyzer"""
    
    print("🔍 AUDITORÍA COMPLETA: arq-buro-service.tysonprod.com")
    print("=" * 60)
    
    base_url = "https://arq-buro-ssssservice.sss.com"
    swagger_path = "/openapi.json"
    
    # 1. ANÁLISIS COMPLETO DE LA API
    print("📊 PASO 1: ANÁLISIS DE API")
    print("-" * 30)
    
    api_result = await analyze_api_service(base_url, swagger_path)
    
    if api_result["success"]:
        print("✅ API analizada exitosamente!")
        
        info = api_result["analysis"]["info"]
        stats = api_result["analysis"]["statistics"]
        
        print(f"  📊 Título: {info['title']}")
        print(f"  🔢 Versión: {info['version']}")
        print(f"  📍 Total Endpoints: {stats['total_endpoints']}")
        print(f"  🏗️  Total Modelos: {stats['total_models']}")
        print(f"  🌐 Versión OpenAPI: {stats['openapi_version']}")
        
        # Distribución de métodos
        print(f"  📋 Métodos HTTP:")
        for method, count in stats["method_distribution"].items():
            if count > 0:
                print(f"    {method}: {count}")
        
        # Seguridad
        security = api_result["analysis"]["security"]
        print(f"  🔐 Autenticación: {'Sí' if security['requires_authentication'] else 'No'}")
        
    else:
        print(f"❌ Error analizando API: {api_result.get('error')}")
        return
    
    print()
    
    # 2. HEALTH CHECK
    print("🏥 PASO 2: HEALTH CHECK")
    print("-" * 30)
    
    health_result = await auto_health_check(base_url)
    
    if health_result["success"]:
        print("✅ Health check exitoso!")
        
        health_check = health_result["health_check"]
        endpoints_used = health_result["endpoints_used"]
        
        print(f"  📊 Status General: {health_check['overall_status']}")
        print(f"  📍 Endpoints Usados:")
        print(f"    Readiness: {endpoints_used['readiness']}")
        print(f"    Liveness: {endpoints_used['liveness']}")
        
        # Detalles de health checks
        if "checks" in health_check:
            print(f"  📋 Detalles de Health Checks:")
            for check in health_check["checks"]:
                print(f"    - {check['status']}: {check['latency_ms']:.2f}ms")
        else:
            print(f"  📋 Status: {health_check['overall_status']}")
            
    else:
        print(f"❌ Error en health check: {health_result.get('error')}")
    
    print()
    
    # 3. GENERACIÓN DE DOCUMENTACIÓN
    print("📚 PASO 3: GENERACIÓN DE DOCUMENTACIÓN")
    print("-" * 30)
    
    docs_result = await generate_api_docs(base_url, swagger_path)
    
    if docs_result["success"]:
        print("✅ Documentación generada!")
        
        doc_summary = docs_result["documentation"]["summary"]
        print(f"  📊 Nivel de Complejidad: {doc_summary['complexity_level']}")
        print(f"  🎯 Funcionalidad Principal: {', '.join(doc_summary['main_functionality'][:3])}")
        
        # Patrones identificados
        patterns = docs_result["documentation"]["api_patterns"]
        print(f"  🔍 Patrones Identificados:")
        print(f"    - Operaciones CRUD: {patterns['crud_operations']}")
        print(f"    - Endpoints de búsqueda: {patterns['search_endpoints']}")
        print(f"    - Operaciones en lote: {patterns['bulk_operations']}")
        print(f"    - Webhooks: {patterns['webhook_endpoints']}")
        
        # Recomendaciones
        if doc_summary['recommendations']:
            print(f"  💡 Recomendaciones:")
            for rec in doc_summary['recommendations']:
                print(f"    - {rec}")
                
    else:
        print(f"❌ Error generando documentación: {docs_result.get('error')}")
    
    print()
    
    # 4. RESUMEN EJECUTIVO
    print("📋 RESUMEN EJECUTIVO")
    print("=" * 60)
    
    print(f"🌐 Servicio: {base_url}")
    print(f"📊 Título: {info['title']} v{info['version']}")
    print(f"📍 Endpoints: {stats['total_endpoints']}")
    print(f"🏗️  Modelos: {stats['total_models']}")
    print(f"🔐 Autenticación: {'Sí' if security['requires_authentication'] else 'No'}")
    print(f"🏥 Estado de Salud: {health_check['overall_status'] if health_result['success'] else 'Desconocido'}")
    print(f"📚 Complejidad: {doc_summary['complexity_level'] if docs_result['success'] else 'Desconocida'}")
    
    print()
    print("🎉 ¡Auditoría completada exitosamente!")


if __name__ == "__main__":
    asyncio.run(test_comprehensive_audit()) 