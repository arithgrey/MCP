# 🚀 Ejemplos Prácticos - MCP Health Check Service

## 📋 Índice de Ejemplos

1. [Monitoreo Básico de Servicios](#monitoreo-básico-de-servicios)
2. [Auditoría Completa de Infraestructura](#auditoría-completa-de-infraestructura)
3. [Monitoreo en Tiempo Real](#monitoreo-en-tiempo-real)
4. [Reportes Automatizados](#reportes-automatizados)
5. [Integración con CI/CD](#integración-con-cicd)
6. [Monitoreo de Microservicios](#monitoreo-de-microservicios)
7. [Alertas y Notificaciones](#alertas-y-notificaciones)
8. [Dashboard de Salud](#dashboard-de-salud)

---

## 🔍 Monitoreo Básico de Servicios

### Ejemplo 1: Verificar un Servicio Individual
```python
# Verificar si un servicio está funcionando
async def check_service_health():
    from src.tools.health import health_comprehensive_check
    
    result = await health_comprehensive_check(
        base_url="https://api.miservicio.com",
        readiness_path="/health/ready",
        liveness_path="/health/live",
        max_latency_ms=500
    )
    
    if result["overall_status"] == "healthy":
        print("✅ Servicio funcionando correctamente")
        print(f"   Readiness: {result['readiness']['status']}")
        print(f"   Liveness: {result['liveness']['status']}")
        print(f"   Latencia: {result['readiness']['latency_ms']:.2f}ms")
    else:
        print("❌ Servicio con problemas")
        print(f"   Estado: {result['overall_status']}")
        if result.get('readiness'):
            print(f"   Readiness: {result['readiness']['status']}")
        if result.get('liveness'):
            print(f"   Liveness: {result['liveness']['status']}")

# Ejecutar
await check_service_health()
```

### Ejemplo 2: Verificar Múltiples Endpoints
```python
# Verificar diferentes endpoints del mismo servicio
async def check_service_endpoints():
    from src.tools.health import health_readiness_check, health_liveness_check
    
    service_url = "https://api.miservicio.com"
    
    # Check readiness
    readiness = await health_readiness_check(
        base_url=service_url,
        path="/health/ready",
        max_latency_ms=300
    )
    
    # Check liveness
    liveness = await health_liveness_check(
        base_url=service_url,
        path="/health/live",
        max_latency_ms=200
    )
    
    print(f"🌐 Servicio: {service_url}")
    print(f"📋 Readiness: {readiness.status} ({readiness.latency_ms:.2f}ms)")
    print(f"💓 Liveness: {liveness.status} ({liveness.latency_ms:.2f}ms)")
    
    # Determinar estado general
    if readiness.status == "healthy" and liveness.status == "healthy":
        print("✅ Servicio completamente saludable")
    elif readiness.status == "healthy":
        print("⚠️  Servicio listo pero con problemas de liveness")
    else:
        print("❌ Servicio no está listo")

await check_service_endpoints()
```

---

## 📊 Auditoría Completa de Infraestructura

### Ejemplo 3: Auditoría de Servicios Críticos
```python
# Auditoría completa de servicios críticos
async def audit_critical_services():
    from src.tools.terminal_tools import terminal_batch_health_check
    
    critical_services = [
        {"name": "API Principal", "url": "https://api.miservicio.com"},
        {"name": "Base de Datos", "url": "https://db.miservicio.com"},
        {"name": "Cache Redis", "url": "https://cache.miservicio.com"},
        {"name": "Frontend", "url": "https://app.miservicio.com"},
        {"name": "Admin Panel", "url": "https://admin.miservicio.com"}
    ]
    
    print("🔍 INICIANDO AUDITORÍA DE SERVICIOS CRÍTICOS")
    print("=" * 60)
    
    result = await terminal_batch_health_check(critical_services)
    
    if result["success"]:
        data = result["results"]
        
        print(f"📊 RESUMEN DE AUDITORÍA")
        print(f"   Total de servicios: {data['total_services']}")
        print(f"   Servicios saludables: {data['healthy_services']}")
        print(f"   Servicios con problemas: {data['unhealthy_services']}")
        print(f"   Porcentaje de salud: {data['health_percentage']:.1f}%")
        
        # Mostrar reporte detallado
        print("\n📋 REPORTE DETALLADO:")
        print(result["report"])
        
        # Alertas
        if data["health_percentage"] < 80:
            print("\n🚨 ALERTA: Múltiples servicios con problemas")
        elif data["health_percentage"] < 100:
            print("\n⚠️  ADVERTENCIA: Algunos servicios tienen problemas")
        else:
            print("\n✅ EXCELENTE: Todos los servicios funcionando correctamente")
    else:
        print(f"❌ Error en la auditoría: {result['error']}")

await audit_critical_services()
```

### Ejemplo 4: Auditoría con Configuración Personalizada
```python
# Auditoría usando archivo de configuración personalizado
async def custom_audit():
    from src.tools.terminal_tools import terminal_run_health_audit
    
    print("⚙️  AUDITORÍA CON CONFIGURACIÓN PERSONALIZADA")
    print("=" * 50)
    
    # Usar archivo de configuración personalizado
    result = await terminal_run_health_audit("custom_audit.yaml")
    
    if result["success"]:
        print("✅ Auditoría completada exitosamente")
        print("\n📊 REPORTE:")
        print(result["report"])
        
        # Analizar resultados
        data = result["results"]
        healthy_count = data["healthy_services"]
        total_count = data["total_services"]
        
        print(f"\n📈 MÉTRICAS:")
        print(f"   Salud general: {data['health_percentage']:.1f}%")
        print(f"   Servicios saludables: {healthy_count}/{total_count}")
        
        # Generar recomendaciones
        if data["health_percentage"] < 50:
            print("   🚨 CRÍTICO: Revisar infraestructura inmediatamente")
        elif data["health_percentage"] < 75:
            print("   ⚠️  ATENCIÓN: Revisar servicios problemáticos")
        else:
            print("   ✅ BUENO: Infraestructura funcionando bien")
    else:
        print(f"❌ Error: {result['error']}")

await custom_audit()
```

---

## 🚨 Monitoreo en Tiempo Real

### Ejemplo 5: Monitoreo Continuo con Alertas
```python
import asyncio
import time
from datetime import datetime

# Monitoreo continuo de servicios
async def continuous_monitoring():
    from src.tools.health import health_comprehensive_check
    
    services = [
        {"name": "API Principal", "url": "https://api.miservicio.com"},
        {"name": "Base de Datos", "url": "https://db.miservicio.com"},
        {"name": "Cache", "url": "https://cache.miservicio.com"}
    ]
    
    print("🔄 INICIANDO MONITOREO CONTINUO")
    print("=" * 40)
    
    while True:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n⏰ {timestamp} - Verificando servicios...")
        
        for service in services:
            try:
                result = await health_comprehensive_check(
                    base_url=service["url"],
                    max_latency_ms=300
                )
                
                status_emoji = "✅" if result["overall_status"] == "healthy" else "❌"
                print(f"{status_emoji} {service['name']}: {result['overall_status']}")
                
                # Alertas para servicios problemáticos
                if result["overall_status"] != "healthy":
                    print(f"   🚨 PROBLEMA DETECTADO en {service['name']}")
                    if result.get("readiness"):
                        print(f"      Readiness: {result['readiness']['status']}")
                    if result.get("liveness"):
                        print(f"      Liveness: {result['liveness']['status']}")
                
            except Exception as e:
                print(f"❌ Error verificando {service['name']}: {e}")
        
        print(f"\n⏳ Esperando 30 segundos para siguiente verificación...")
        await asyncio.sleep(30)

# Ejecutar monitoreo (en producción, usar asyncio.create_task)
# await continuous_monitoring()
```

### Ejemplo 6: Monitoreo con Umbrales Personalizados
```python
# Monitoreo con diferentes umbrales por servicio
async def smart_monitoring():
    from src.tools.health import health_comprehensive_check
    
    service_configs = [
        {
            "name": "API Principal",
            "url": "https://api.miservicio.com",
            "readiness_path": "/health/ready",
            "liveness_path": "/health/live",
            "max_latency": 200,  # Más estricto para API principal
            "critical": True
        },
        {
            "name": "Base de Datos",
            "url": "https://db.miservicio.com",
            "readiness_path": "/ready",
            "liveness_path": "/live",
            "max_latency": 500,  # Más permisivo para DB
            "critical": True
        },
        {
            "name": "Cache",
            "url": "https://cache.miservicio.com",
            "readiness_path": "/health",
            "liveness_path": "/health",
            "max_latency": 1000,  # Muy permisivo para cache
            "critical": False
        }
    ]
    
    print("🧠 MONITOREO INTELIGENTE CON UMBRALES PERSONALIZADOS")
    print("=" * 60)
    
    for config in service_configs:
        try:
            result = await health_comprehensive_check(
                base_url=config["url"],
                readiness_path=config["readiness_path"],
                liveness_path=config["liveness_path"],
                max_latency_ms=config["max_latency"]
            )
            
            # Evaluar estado
            if result["overall_status"] == "healthy":
                print(f"✅ {config['name']}: Saludable")
            else:
                severity = "🚨 CRÍTICO" if config["critical"] else "⚠️  ADVERTENCIA"
                print(f"{severity} {config['name']}: {result['overall_status']}")
                
                # Mostrar detalles del problema
                if result.get("readiness"):
                    readiness = result["readiness"]
                    print(f"   Readiness: {readiness['status']} ({readiness['latency_ms']:.2f}ms)")
                
                if result.get("liveness"):
                    liveness = result["liveness"]
                    print(f"   Liveness: {liveness['status']} ({liveness['latency_ms']:.2f}ms)")
                
        except Exception as e:
            print(f"❌ Error en {config['name']}: {e}")

await smart_monitoring()
```

---

## 📊 Reportes Automatizados

### Ejemplo 7: Generar Reporte Diario
```python
# Generar reporte diario de salud de servicios
async def daily_health_report():
    from src.tools.terminal_tools import terminal_batch_health_check
    from datetime import datetime
    
    print("📅 GENERANDO REPORTE DIARIO DE SALUD")
    print("=" * 50)
    
    # Lista de servicios a monitorear
    services = [
        {"name": "API Principal", "url": "https://api.miservicio.com"},
        {"name": "API Secundaria", "url": "https://api2.miservicio.com"},
        {"name": "Base de Datos", "url": "https://db.miservicio.com"},
        {"name": "Cache Redis", "url": "https://cache.miservicio.com"},
        {"name": "Frontend", "url": "https://app.miservicio.com"},
        {"name": "Admin Panel", "url": "https://admin.miservicio.com"}
    ]
    
    # Ejecutar auditoría
    result = await terminal_batch_health_check(services)
    
    if result["success"]:
        data = result["results"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generar reporte formateado
        report = f"""
📊 REPORTE DIARIO DE SALUD - {timestamp}
{'='*60}

📈 RESUMEN EJECUTIVO:
   • Total de servicios: {data['total_services']}
   • Servicios saludables: {data['healthy_services']}
   • Servicios con problemas: {data['unhealthy_services']}
   • Porcentaje de salud: {data['health_percentage']:.1f}%

🔍 DETALLES POR SERVICIO:
"""
        
        # Agregar detalles de cada servicio
        for service_result in data["results"]:
            status_emoji = "✅" if service_result["overall_status"] == "healthy" else "❌"
            report += f"{status_emoji} {service_result['service_name']}\n"
            report += f"   URL: {service_result['base_url']}\n"
            report += f"   Estado: {service_result['overall_status']}\n"
            
            if service_result.get("readiness"):
                readiness = service_result["readiness"]
                report += f"   Readiness: {readiness['status']} ({readiness['latency_ms']:.2f}ms)\n"
            
            if service_result.get("liveness"):
                liveness = service_result["liveness"]
                report += f"   Liveness: {liveness['status']} ({liveness['latency_ms']:.2f}ms)\n"
            
            report += "\n"
        
        # Agregar recomendaciones
        if data["health_percentage"] >= 90:
            report += "🎉 EXCELENTE: Todos los servicios funcionando correctamente"
        elif data["health_percentage"] >= 75:
            report += "✅ BUENO: La mayoría de servicios funcionando bien"
        elif data["health_percentage"] >= 50:
            report += "⚠️  ATENCIÓN: Varios servicios con problemas"
        else:
            report += "🚨 CRÍTICO: Múltiples servicios fallando"
        
        print(report)
        
        # Guardar reporte en archivo (opcional)
        filename = f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write(report)
        print(f"\n💾 Reporte guardado en: {filename}")
        
    else:
        print(f"❌ Error generando reporte: {result['error']}")

await daily_health_report()
```

---

## 🔄 Integración con CI/CD

### Ejemplo 8: Health Check en Pipeline de CI/CD
```python
# Health check como parte del pipeline de CI/CD
async def ci_cd_health_check():
    from src.tools.health import health_comprehensive_check
    import sys
    
    print("🚀 HEALTH CHECK PARA CI/CD")
    print("=" * 40)
    
    # Servicios a verificar después del deploy
    services = [
        {
            "name": "API Staging",
            "url": "https://staging-api.miservicio.com",
            "readiness_path": "/health/ready",
            "liveness_path": "/health/live",
            "max_latency": 300
        },
        {
            "name": "Frontend Staging",
            "url": "https://staging-app.miservicio.com",
            "readiness_path": "/health",
            "liveness_path": "/health",
            "max_latency": 500
        }
    ]
    
    all_healthy = True
    failed_services = []
    
    for service in services:
        try:
            print(f"🔍 Verificando {service['name']}...")
            
            result = await health_comprehensive_check(
                base_url=service["url"],
                readiness_path=service["readiness_path"],
                liveness_path=service["liveness_path"],
                max_latency_ms=service["max_latency"]
            )
            
            if result["overall_status"] == "healthy":
                print(f"✅ {service['name']}: Saludable")
            else:
                print(f"❌ {service['name']}: {result['overall_status']}")
                all_healthy = False
                failed_services.append(service["name"])
                
        except Exception as e:
            print(f"❌ Error verificando {service['name']}: {e}")
            all_healthy = False
            failed_services.append(service["name"])
    
    # Resultado final para CI/CD
    print(f"\n📊 RESULTADO FINAL:")
    if all_healthy:
        print("✅ TODOS LOS SERVICIOS SALUDABLES")
        print("🚀 DEPLOY EXITOSO - Continuar con el pipeline")
        sys.exit(0)  # Éxito para CI/CD
    else:
        print("❌ ALGUNOS SERVICIOS CON PROBLEMAS")
        print(f"   Servicios fallando: {', '.join(failed_services)}")
        print("🛑 DEPLOY FALLIDO - Revisar servicios")
        sys.exit(1)  # Fallo para CI/CD

await ci_cd_health_check()
```

---

## 🏗️ Monitoreo de Microservicios

### Ejemplo 9: Auditoría de Arquitectura de Microservicios
```python
# Auditoría específica para arquitectura de microservicios
async def microservices_audit():
    from src.tools.terminal_tools import terminal_batch_health_check
    
    print("🏗️  AUDITORÍA DE ARQUITECTURA DE MICROSERVICIOS")
    print("=" * 60)
    
    # Definir microservicios por dominio
    microservices = {
        "🔐 Autenticación": [
            {"name": "Auth Service", "url": "https://auth.miservicio.com"},
            {"name": "User Service", "url": "https://users.miservicio.com"}
        ],
        "💰 Pagos": [
            {"name": "Payment Service", "url": "https://payments.miservicio.com"},
            {"name": "Billing Service", "url": "https://billing.miservicio.com"}
        ],
        "📦 Productos": [
            {"name": "Catalog Service", "url": "https://catalog.miservicio.com"},
            {"name": "Inventory Service", "url": "https://inventory.miservicio.com"}
        ],
        "🚚 Logística": [
            {"name": "Shipping Service", "url": "https://shipping.miservicio.com"},
            {"name": "Tracking Service", "url": "https://tracking.miservicio.com"}
        ]
    }
    
    domain_results = {}
    overall_health = 0
    total_services = 0
    
    for domain, services in microservices.items():
        print(f"\n{domain}")
        print("-" * 40)
        
        # Verificar servicios del dominio
        result = await terminal_batch_health_check(services)
        
        if result["success"]:
            data = result["results"]
            domain_health = data["health_percentage"]
            domain_results[domain] = domain_health
            
            print(f"   Servicios: {data['healthy_services']}/{data['total_services']} saludables")
            print(f"   Salud del dominio: {domain_health:.1f}%")
            
            overall_health += domain_health
            total_services += data["total_services"]
        else:
            print(f"   ❌ Error: {result['error']}")
            domain_results[domain] = 0
    
    # Resumen general
    if total_services > 0:
        overall_percentage = overall_health / len(microservices)
        print(f"\n📊 SALUD GENERAL DE LA ARQUITECTURA:")
        print(f"   Promedio de salud: {overall_percentage:.1f}%")
        
        # Recomendaciones por dominio
        print(f"\n💡 RECOMENDACIONES:")
        for domain, health in domain_results.items():
            if health >= 90:
                print(f"   ✅ {domain}: Excelente")
            elif health >= 75:
                print(f"   ⚠️  {domain}: Revisar ocasionalmente")
            else:
                print(f"   🚨 {domain}: Requiere atención inmediata")
    
    return domain_results

await microservices_audit()
```

---

## 🚨 Alertas y Notificaciones

### Ejemplo 10: Sistema de Alertas Inteligente
```python
# Sistema de alertas basado en umbrales y patrones
async def intelligent_alerting():
    from src.tools.health import health_comprehensive_check
    import asyncio
    
    print("🚨 SISTEMA DE ALERTAS INTELIGENTE")
    print("=" * 50)
    
    # Configuración de alertas
    alert_config = {
        "critical_threshold": 70,    # Porcentaje crítico
        "warning_threshold": 85,     # Porcentaje de advertencia
        "check_interval": 60,        # Segundos entre checks
        "consecutive_failures": 3    # Fallos consecutivos para alerta
    }
    
    # Servicios críticos
    critical_services = [
        {"name": "API Principal", "url": "https://api.miservicio.com"},
        {"name": "Base de Datos", "url": "https://db.miservicio.com"}
    ]
    
    # Historial de fallos
    failure_history = {}
    
    async def check_and_alert():
        while True:
            print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Verificando servicios críticos...")
            
            current_health = 0
            total_services = len(critical_services)
            
            for service in critical_services:
                try:
                    result = await health_comprehensive_check(
                        base_url=service["url"],
                        max_latency_ms=300
                    )
                    
                    if result["overall_status"] == "healthy":
                        current_health += 1
                        # Resetear contador de fallos
                        if service["name"] in failure_history:
                            del failure_history[service["name"]]
                        print(f"✅ {service['name']}: Saludable")
                    else:
                        # Incrementar contador de fallos
                        if service["name"] not in failure_history:
                            failure_history[service["name"]] = 0
                        failure_history[service["name"]] += 1
                        
                        failures = failure_history[service["name"]]
                        print(f"❌ {service['name']}: {result['overall_status']} (fallo #{failures})")
                        
                        # Generar alertas basadas en fallos consecutivos
                        if failures >= alert_config["consecutive_failures"]:
                            print(f"🚨 ALERTA CRÍTICA: {service['name']} fallando consecutivamente")
                            # Aquí podrías enviar notificación por email, Slack, etc.
                        
                except Exception as e:
                    print(f"❌ Error verificando {service['name']}: {e}")
                    # Contar como fallo
                    if service["name"] not in failure_history:
                        failure_history[service["name"]] = 0
                    failure_history[service["name"]] += 1
            
            # Calcular porcentaje de salud
            health_percentage = (current_health / total_services) * 100
            
            print(f"\n📊 SALUD ACTUAL: {health_percentage:.1f}%")
            
            # Generar alertas basadas en umbrales
            if health_percentage <= alert_config["critical_threshold"]:
                print("🚨 ALERTA CRÍTICA: Múltiples servicios críticos fallando")
            elif health_percentage <= alert_config["warning_threshold"]:
                print("⚠️  ADVERTENCIA: Algunos servicios críticos con problemas")
            else:
                print("✅ ESTADO NORMAL: Servicios críticos funcionando")
            
            # Esperar antes del siguiente check
            await asyncio.sleep(alert_config["check_interval"])
    
    # Ejecutar sistema de alertas
    try:
        await check_and_alert()
    except KeyboardInterrupt:
        print("\n🛑 Sistema de alertas detenido")

# Para ejecutar en producción:
# await intelligent_alerting()
```

---

## 📊 Dashboard de Salud

### Ejemplo 11: Generar Dashboard de Salud
```python
# Generar dashboard visual de salud de servicios
async def generate_health_dashboard():
    from src.tools.terminal_tools import terminal_batch_health_check
    from datetime import datetime
    
    print("📊 GENERANDO DASHBOARD DE SALUD")
    print("=" * 50)
    
    # Servicios a monitorear
    services = [
        {"name": "API Principal", "url": "https://api.miservicio.com"},
        {"name": "API Secundaria", "url": "https://api2.miservicio.com"},
        {"name": "Base de Datos", "url": "https://db.miservicio.com"},
        {"name": "Cache Redis", "url": "https://cache.miservicio.com"},
        {"name": "Frontend", "url": "https://app.miservicio.com"},
        {"name": "Admin Panel", "url": "https://admin.miservicio.com"}
    ]
    
    # Ejecutar auditoría
    result = await terminal_batch_health_check(services)
    
    if result["success"]:
        data = result["results"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generar dashboard ASCII
        dashboard = f"""
╔══════════════════════════════════════════════════════════════╗
║                    DASHBOARD DE SALUD                        ║
║                        {timestamp}                           ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  📈 SALUD GENERAL: {data['health_percentage']:>6.1f}%                    ║
║  🔢 TOTAL SERVICIOS: {data['total_services']:>2}                          ║
║  ✅ SALUDABLES: {data['healthy_services']:>2}                              ║
║  ❌ PROBLEMAS: {data['unhealthy_services']:>2}                              ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                    ESTADO POR SERVICIO                       ║
╠══════════════════════════════════════════════════════════════╣
"""
        
        # Agregar estado de cada servicio
        for service_result in data["results"]:
            status_emoji = "✅" if service_result["overall_status"] == "healthy" else "❌"
            service_name = service_result["service_name"][:25].ljust(25)
            status = service_result["overall_status"].ljust(10)
            
            # Obtener latencia si está disponible
            latency = "N/A"
            if service_result.get("readiness") and service_result["readiness"].get("latency_ms"):
                latency = f"{service_result['readiness']['latency_ms']:.0f}ms"
            elif service_result.get("liveness") and service_result["liveness"].get("latency_ms"):
                latency = f"{service_result['liveness']['latency_ms']:.0f}ms"
            
            dashboard += f"║  {status_emoji} {service_name} │ {status} │ {latency:>8} ║\n"
        
        # Agregar pie del dashboard
        dashboard += """╠══════════════════════════════════════════════════════════════╣
║                    RECOMENDACIONES                           ║
"""
        
        # Agregar recomendaciones basadas en la salud
        if data["health_percentage"] >= 95:
            dashboard += "║  🎉 EXCELENTE: Todos los servicios funcionando perfectamente ║\n"
        elif data["health_percentage"] >= 80:
            dashboard += "║  ✅ BUENO: La mayoría de servicios funcionando bien        ║\n"
        elif data["health_percentage"] >= 60:
            dashboard += "║  ⚠️  ATENCIÓN: Varios servicios requieren revisión        ║\n"
        else:
            dashboard += "║  🚨 CRÍTICO: Múltiples servicios con problemas graves     ║\n"
        
        dashboard += """║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
        
        print(dashboard)
        
        # Guardar dashboard en archivo
        filename = f"health_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write(dashboard)
        print(f"💾 Dashboard guardado en: {filename}")
        
    else:
        print(f"❌ Error generando dashboard: {result['error']}")

await generate_health_dashboard()
```

---

## 🎯 Resumen de Ejemplos

Estos ejemplos demuestran la versatilidad y potencia del MCP Health Check Service:

1. **Monitoreo Básico**: Verificación individual y múltiple de servicios
2. **Auditorías**: Evaluación completa de infraestructura
3. **Monitoreo en Tiempo Real**: Verificación continua con alertas
4. **Reportes**: Generación automática de reportes detallados
5. **CI/CD**: Integración en pipelines de deployment
6. **Microservicios**: Auditoría específica para arquitecturas distribuidas
7. **Alertas**: Sistema inteligente de notificaciones
8. **Dashboard**: Visualización clara del estado de salud

Cada ejemplo puede ser adaptado y combinado según las necesidades específicas de tu infraestructura y flujos de trabajo.

---

**¡Con estos ejemplos tienes todo lo necesario para implementar un sistema completo de monitoreo de salud de servicios! 🚀** 