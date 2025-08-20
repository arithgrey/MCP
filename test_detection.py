#!/usr/bin/env python3
"""
Script de prueba para la detección automática de endpoints
"""
import asyncio
import json
from src.tools.endpoint_detector import detect_service_endpoints, auto_health_check


async def test_endpoint_detection():
    """Prueba la detección automática de endpoints"""
    print("🧪 PROBANDO DETECCIÓN AUTOMÁTICA DE ENDPOINTS")
    print("=" * 60)
    
    # Servicios de prueba
    test_services = [
        "https://httpbin.org",
        "https://jsonplaceholder.typicode.com",
        "https://api.github.com"
    ]
    
    for service_url in test_services:
        print(f"\n🔍 Probando servicio: {service_url}")
        print("-" * 50)
        
        try:
            # Detectar endpoints
            detection = await detect_service_endpoints(service_url, timeout_ms=5000)
            
            # Mostrar resumen
            health_summary = detection["health"]["summary"]
            swagger_summary = detection["swagger"]["summary"]
            
            print(f"📊 HEALTH ENDPOINTS:")
            print(f"   Probados: {health_summary['total_tested']}")
            print(f"   Encontrados: {health_summary['total_found']}")
            
            if health_summary["best_readiness"]:
                print(f"   ✅ Mejor readiness: {health_summary['best_readiness']['endpoint']}")
            if health_summary["best_liveness"]:
                print(f"   ✅ Mejor liveness: {health_summary['best_liveness']['endpoint']}")
            if health_summary["best_general"]:
                print(f"   ✅ Mejor general: {health_summary['best_general']['endpoint']}")
            
            print(f"\n📚 SWAGGER ENDPOINTS:")
            print(f"   Probados: {swagger_summary['total_tested']}")
            print(f"   Encontrados: {swagger_summary['total_found']}")
            print(f"   Tiene Swagger: {swagger_summary['has_swagger']}")
            
            if swagger_summary["best_ui"]:
                print(f"   ✅ Mejor UI: {swagger_summary['best_ui']['endpoint']}")
            if swagger_summary["best_api"]:
                print(f"   ✅ Mejor API: {swagger_summary['best_api']['endpoint']}")
            
            print(f"\n💡 RECOMENDACIONES:")
            for rec in detection["recommendations"]:
                print(f"   {rec}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)


async def test_auto_health_check():
    """Prueba el health check automático"""
    print("\n🏥 PROBANDO HEALTH CHECK AUTOMÁTICO")
    print("=" * 60)
    
    test_service = "https://httpbin.org"
    print(f"🔍 Probando health check automático en: {test_service}")
    
    try:
        result = await auto_health_check(test_service, timeout_ms=5000)
        
        if result["success"]:
            print("✅ Health check automático exitoso")
            print(f"   Endpoints usados:")
            print(f"     Readiness: {result['endpoints_used']['readiness']}")
            print(f"     Liveness: {result['endpoints_used']['liveness']}")
            
            health_check = result["health_check"]
            print(f"   Estado general: {health_check['overall_status']}")
            
            if "readiness" in health_check:
                readiness = health_check["readiness"]
                print(f"   Readiness: {readiness['status']} ({readiness['latency_ms']:.2f}ms)")
            
            if "liveness" in health_check:
                liveness = health_check["liveness"]
                print(f"   Liveness: {liveness['status']} ({liveness['latency_ms']:.2f}ms)")
        else:
            print(f"❌ Health check falló: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Función principal"""
    print("🚀 MCP ENDPOINT DETECTOR - PRUEBAS")
    print("=" * 60)
    
    await test_endpoint_detection()
    await test_auto_health_check()
    
    print("\n🎉 Pruebas completadas!")


if __name__ == "__main__":
    asyncio.run(main()) 