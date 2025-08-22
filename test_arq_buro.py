#!/usr/bin/env python3
"""
Script de prueba específico para arq-buro-service.tysonprod.com
"""
import asyncio
from src.tools.endpoint_detector import detect_service_endpoints, auto_health_check


async def test_arq_buro_service():
    """Prueba completa del servicio arq-buro-service"""
    base_url = "https://arq-buro-service.tysonpsssrod.com"
    
    print("🔍 PROBANDO SERVICIO: arq-buro-service.tysonprod.com")
    print("=" * 70)
    
    # 1. Detección automática de endpoints
    print("\n1️⃣ DETECCIÓN AUTOMÁTICA DE ENDPOINTS")
    print("-" * 50)
    
    detection = await detect_service_endpoints(base_url, timeout_ms=10000)
    
    # Mostrar resumen de health endpoints
    health_summary = detection["health"]["summary"]
    print(f"📊 HEALTH ENDPOINTS:")
    print(f"   Probados: {health_summary['total_tested']}")
    print(f"   Encontrados: {health_summary['total_found']}")
    
    if health_summary["best_readiness"]:
        print(f"   ✅ Mejor readiness: {health_summary['best_readiness']['endpoint']}")
        print(f"      Latencia: {health_summary['best_readiness']['latency_ms']:.2f}ms")
    
    if health_summary["best_liveness"]:
        print(f"   ✅ Mejor liveness: {health_summary['best_liveness']['endpoint']}")
        print(f"      Latencia: {health_summary['best_liveness']['latency_ms']:.2f}ms")
    
    if health_summary["best_general"]:
        print(f"   ✅ Mejor general: {health_summary['best_general']['endpoint']}")
        print(f"      Latencia: {health_summary['best_general']['latency_ms']:.2f}ms")
    
    # Mostrar resumen de Swagger
    swagger_summary = detection["swagger"]["summary"]
    print(f"\n📚 SWAGGER ENDPOINTS:")
    print(f"   Probados: {swagger_summary['total_tested']}")
    print(f"   Encontrados: {swagger_summary['total_found']}")
    print(f"   Tiene Swagger: {swagger_summary['has_swagger']}")
    
    if swagger_summary["best_ui"]:
        print(f"   ✅ Mejor UI: {swagger_summary['best_ui']['endpoint']}")
        print(f"      URL: {swagger_summary['best_ui']['url']}")
    
    if swagger_summary["best_api"]:
        print(f"   ✅ Mejor API: {swagger_summary['best_api']['endpoint']}")
        print(f"      URL: {swagger_summary['best_api']['url']}")
    
    # 2. Health check automático
    print(f"\n2️⃣ HEALTH CHECK AUTOMÁTICO")
    print("-" * 50)
    
    health_result = await auto_health_check(base_url, timeout_ms=10000)
    
    if health_result["success"]:
        print("✅ Health check automático exitoso")
        print(f"   Endpoints utilizados:")
        print(f"     Readiness: {health_result['endpoints_used']['readiness']}")
        print(f"     Liveness: {health_result['endpoints_used']['liveness']}")
        
        health_check = health_result["health_check"]
        print(f"\n   📊 RESULTADO DEL HEALTH CHECK:")
        print(f"      Estado general: {health_check['overall_status']}")
        
        if "readiness" in health_check:
            readiness = health_check["readiness"]
            print(f"      Readiness: {readiness['status']} ({readiness['latency_ms']:.2f}ms)")
        
        if "liveness" in health_check:
            liveness = health_check["liveness"]
            print(f"      Liveness: {liveness['status']} ({liveness['latency_ms']:.2f}ms)")
    else:
        print(f"❌ Health check falló: {health_result['error']}")
    
    # 3. Recomendaciones
    print(f"\n3️⃣ RECOMENDACIONES")
    print("-" * 50)
    
    for rec in detection["recommendations"]:
        print(f"   {rec}")
    
    # 4. Resumen final
    print(f"\n4️⃣ RESUMEN FINAL")
    print("-" * 50)
    
    print(f"🌐 Servicio: {base_url}")
    print(f"📊 Health endpoints: {health_summary['total_found']}/27")
    print(f"📚 Swagger: {'✅ Disponible' if swagger_summary['has_swagger'] else '❌ No disponible'}")
    print(f"🏥 Estado: {health_result.get('health_check', {}).get('overall_status', 'unknown') if health_result.get('success') else 'failed'}")
    
    if health_summary["total_found"] >= 2:
        print("🎯 Servicio bien configurado con endpoints de health check")
    elif health_summary["total_found"] == 1:
        print("⚠️  Servicio con configuración mínima de health check")
    else:
        print("🚨 Servicio sin endpoints de health check configurados")
    
    if swagger_summary["has_swagger"]:
        print("📖 Documentación API disponible")
    else:
        print("📚 Sin documentación API detectada")


async def main():
    """Función principal"""
    print("🚀 MCP ENDPOINT DETECTOR - PRUEBA ARQ-BURO-SERVICE")
    print("=" * 70)
    
    await test_arq_buro_service()
    
    print("\n🎉 Prueba completada!")


if __name__ == "__main__":
    asyncio.run(main()) 