"""
Detector inteligente de endpoints para health checks y Swagger
"""
import asyncio
import httpx
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
from src.core.models import Status


class EndpointDetector:
    """Detector inteligente de endpoints de health check y Swagger"""
    
    # Rutas comunes de health check
    HEALTH_ENDPOINTS = {
        "readiness": [
            "/health/ready",
            "/health/readiness", 
            "/ready",
            "/readiness",
            "/actuator/health/readiness",
            "/v1/health/ready",
            "/v1/health/readiness",
            "/v1/ready",
            "/v1/readiness",
            "/v1/actuator/health/readiness"
        ],
        "liveness": [
            "/health/live",
            "/health/liveness",
            "/live", 
            "/liveness",
            "/actuator/health/liveness",
            "/v1/health/live",
            "/v1/health/liveness",
            "/v1/live",
            "/v1/liveness",
            "/v1/actuator/health/liveness"
        ],
        "general": [
            "/health",
            "/ping",
            "/status",
            "/v1/health",
            "/v1/ping",
            "/v1/status",
            "/v1/actuator/health"
        ]
    }
    
    # Rutas comunes de Swagger/OpenAPI
    SWAGGER_ENDPOINTS = [
        "/swagger-ui.html",
        "/swagger-ui/index.html",
        "/swagger",
        "/api-docs",
        "/docs",
        "/v1/swagger-ui.html",
        "/v1/swagger-ui/index.html",
        "/v1/swagger",
        "/v1/api-docs",
        "/v1/docs",
        "/v1/actuator/swagger-ui.html",
        "/v1/actuator/swagger-ui/index.html",
        "/v1/actuator/swagger",
        "/v1/actuator/api-docs",
        "/v1/actuator/docs",
        "/swagger.json",
        "/swagger.yaml",
        "/openapi.json",
        "/openapi.yaml",
        "/v1/swagger.json",
        "/v1/swagger.yaml",
        "/v1/openapi.json",
        "/v1/openapi.yaml"
    ]
    
    def __init__(self, timeout_ms: int = 5000):
        self.timeout_ms = timeout_ms
    
    async def detect_health_endpoints(self, base_url: str) -> Dict[str, Dict]:
        """
        Detecta automáticamente los endpoints de health check disponibles
        
        Args:
            base_url: URL base del servicio
            
        Returns:
            Dict con los endpoints detectados y su estado
        """
        results = {
            "readiness": {},
            "liveness": {},
            "general": {},
            "summary": {
                "total_tested": 0,
                "total_found": 0,
                "best_readiness": None,
                "best_liveness": None,
                "best_general": None
            }
        }
        
        # Probar endpoints de readiness
        readiness_results = await self._test_endpoint_group(
            base_url, self.HEALTH_ENDPOINTS["readiness"], "readiness"
        )
        results["readiness"] = readiness_results
        
        # Probar endpoints de liveness
        liveness_results = await self._test_endpoint_group(
            base_url, self.HEALTH_ENDPOINTS["liveness"], "liveness"
        )
        results["liveness"] = liveness_results
        
        # Probar endpoints generales
        general_results = await self._test_endpoint_group(
            base_url, self.HEALTH_ENDPOINTS["general"], "general"
        )
        results["general"] = general_results
        
        # Generar resumen
        self._generate_summary(results)
        
        return results
    
    async def detect_swagger_endpoints(self, base_url: str) -> Dict[str, Dict]:
        """
        Detecta automáticamente los endpoints de Swagger/OpenAPI disponibles
        
        Args:
            base_url: URL base del servicio
            
        Returns:
            Dict con los endpoints de Swagger detectados
        """
        results = {
            "endpoints": {},
            "summary": {
                "total_tested": 0,
                "total_found": 0,
                "best_ui": None,
                "best_api": None,
                "has_swagger": False
            }
        }
        
        # Probar todos los endpoints de Swagger
        for endpoint in self.SWAGGER_ENDPOINTS:
            url = urljoin(base_url, endpoint)
            result = await self._test_single_endpoint(url, "swagger")
            results["endpoints"][endpoint] = result
            
            if result["status"] == Status.HEALTHY:
                results["summary"]["total_found"] += 1
                results["summary"]["has_swagger"] = True
                
                # Categorizar el endpoint
                if any(ui in endpoint for ui in ["swagger-ui", "docs"]):
                    if not results["summary"]["best_ui"] or result["latency_ms"] < results["summary"]["best_ui"]["latency_ms"]:
                        results["summary"]["best_ui"] = {
                            "endpoint": endpoint,
                            "url": url,
                            "latency_ms": result["latency_ms"]
                        }
                elif any(api in endpoint for api in ["swagger.json", "openapi.json", "api-docs"]):
                    if not results["summary"]["best_api"] or result["latency_ms"] < results["summary"]["best_api"]["latency_ms"]:
                        results["summary"]["best_api"] = {
                            "endpoint": endpoint,
                            "url": url,
                            "latency_ms": result["latency_ms"]
                        }
            
            results["summary"]["total_tested"] += 1
        
        return results
    
    async def comprehensive_detection(self, base_url: str) -> Dict[str, Dict]:
        """
        Detección completa de health checks y Swagger
        
        Args:
            base_url: URL base del servicio
            
        Returns:
            Dict con toda la información detectada
        """
        print(f"🔍 Iniciando detección completa para: {base_url}")
        
        # Detectar health endpoints
        health_results = await self.detect_health_endpoints(base_url)
        
        # Detectar Swagger endpoints
        swagger_results = await self.detect_swagger_endpoints(base_url)
        
        # Resultado consolidado
        comprehensive_result = {
            "base_url": base_url,
            "detection_timestamp": asyncio.get_event_loop().time(),
            "health": health_results,
            "swagger": swagger_results,
            "recommendations": self._generate_recommendations(health_results, swagger_results)
        }
        
        return comprehensive_result
    
    async def _test_endpoint_group(self, base_url: str, endpoints: List[str], group_type: str) -> Dict[str, Dict]:
        """Prueba un grupo de endpoints del mismo tipo"""
        results = {}
        
        for endpoint in endpoints:
            url = urljoin(base_url, endpoint)
            result = await self._test_single_endpoint(url, group_type)
            results[endpoint] = result
        
        return results
    
    async def _test_single_endpoint(self, url: str, endpoint_type: str) -> Dict[str, any]:
        """Prueba un endpoint individual"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout_ms/1000) as client:
                response = await client.get(url)
                latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000
                
                # Determinar si es un endpoint válido
                is_valid = self._is_valid_health_endpoint(response, endpoint_type)
                
                if is_valid:
                    status = Status.HEALTHY
                    error_message = None
                else:
                    status = Status.UNHEALTHY
                    error_message = f"Endpoint no válido (HTTP {response.status_code})"
                
                return {
                    "url": url,
                    "status": status,
                    "latency_ms": latency_ms,
                    "response_code": response.status_code,
                    "error_message": error_message,
                    "is_valid": is_valid,
                    "content_type": response.headers.get("content-type", ""),
                    "content_length": len(response.content),
                    "details": {
                        "url": url,
                        "method": "GET",
                        "headers": dict(response.headers)
                    }
                }
                
        except httpx.TimeoutException:
            latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            return {
                "url": url,
                "status": Status.UNHEALTHY,
                "latency_ms": latency_ms,
                "response_code": None,
                "error_message": "Timeout",
                "is_valid": False,
                "content_type": None,
                "content_length": 0,
                "details": {"url": url, "timeout_ms": self.timeout_ms}
            }
        except Exception as e:
            latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            return {
                "url": url,
                "status": Status.UNHEALTHY,
                "latency_ms": latency_ms,
                "response_code": None,
                "error_message": str(e),
                "is_valid": False,
                "content_type": None,
                "content_length": 0,
                "details": {"url": url}
            }
    
    def _is_valid_health_endpoint(self, response: httpx.Response, endpoint_type: str) -> bool:
        """Determina si un endpoint de health check es válido"""
        if response.status_code != 200:
            return False
        
        content_type = response.headers.get("content-type", "").lower()
        content = response.text.lower()
        
        # Para endpoints de health, buscar indicadores de salud
        if endpoint_type in ["readiness", "liveness", "general"]:
            # Verificar si el contenido indica un health check válido
            health_indicators = [
                "status", "healthy", "ready", "live", "up", "ok",
                "health", "state", "condition", "alive", "ping"
            ]
            
            # Verificar si hay algún indicador de salud en el contenido
            has_health_content = any(indicator in content for indicator in health_indicators)
            
            # Para JSON responses, verificar estructura
            if "application/json" in content_type:
                try:
                    import json
                    data = json.loads(response.text)
                    # Verificar si tiene estructura de health check
                    has_health_structure = any(key in data for key in ["status", "health", "state", "components"])
                    return has_health_structure or has_health_content
                except:
                    return has_health_content
            
            # También aceptar respuestas HTML simples para endpoints básicos
            if "text/html" in content_type and len(content) < 1000:
                return has_health_content
            
            return has_health_content
        
        # Para Swagger endpoints
        elif endpoint_type == "swagger":
            swagger_indicators = [
                "swagger", "openapi", "api", "docs", "documentation",
                "swagger-ui", "swagger.json", "openapi.json"
            ]
            return any(indicator in content for indicator in swagger_indicators)
        
        return False
    
    def _generate_summary(self, results: Dict[str, Dict]):
        """Genera un resumen de los resultados de health check"""
        total_tested = 0
        total_found = 0
        
        # Contar endpoints de readiness
        readiness_found = [ep for ep in results["readiness"].values() if ep["is_valid"]]
        if readiness_found:
            best_readiness = min(readiness_found, key=lambda x: x["latency_ms"])
            results["summary"]["best_readiness"] = {
                "endpoint": best_readiness["url"].split("/", 3)[-1] if len(best_readiness["url"].split("/")) > 3 else best_readiness["url"].split("/")[-1],
                "url": best_readiness["url"],
                "latency_ms": best_readiness["latency_ms"]
            }
            total_found += 1
        
        # Contar endpoints de liveness
        liveness_found = [ep for ep in results["liveness"].values() if ep["is_valid"]]
        if liveness_found:
            best_liveness = min(liveness_found, key=lambda x: x["latency_ms"])
            results["summary"]["best_liveness"] = {
                "endpoint": best_liveness["url"].split("/", 3)[-1] if len(best_liveness["url"].split("/")) > 3 else best_liveness["url"].split("/")[-1],
                "url": best_liveness["url"],
                "latency_ms": best_liveness["latency_ms"]
            }
            total_found += 1
        
        # Contar endpoints generales
        general_found = [ep for ep in results["general"].values() if ep["is_valid"]]
        if general_found:
            best_general = min(general_found, key=lambda x: x["latency_ms"])
            results["summary"]["best_general"] = {
                "endpoint": best_general["url"].split("/", 3)[-1] if len(best_general["url"].split("/")) > 3 else best_general["url"].split("/")[-1],
                "url": best_general["url"],
                "latency_ms": best_general["latency_ms"]
            }
            total_found += 1
        
        # Contar totales
        for group in ["readiness", "liveness", "general"]:
            total_tested += len(results[group])
        
        results["summary"]["total_tested"] = total_tested
        results["summary"]["total_found"] = total_found
    
    def _generate_recommendations(self, health_results: Dict, swagger_results: Dict) -> List[str]:
        """Genera recomendaciones basadas en los resultados"""
        recommendations = []
        
        # Recomendaciones de health check
        if not health_results["summary"]["best_readiness"]:
            recommendations.append("⚠️  No se encontraron endpoints de readiness válidos")
        if not health_results["summary"]["best_liveness"]:
            recommendations.append("⚠️  No se encontraron endpoints de liveness válidos")
        if not health_results["summary"]["best_general"]:
            recommendations.append("⚠️  No se encontraron endpoints de health general válidos")
        
        # Recomendaciones de Swagger
        if not swagger_results["summary"]["has_swagger"]:
            recommendations.append("📚 No se detectó documentación Swagger/OpenAPI")
        else:
            if swagger_results["summary"]["best_ui"]:
                recommendations.append(f"✅ Swagger UI disponible en: {swagger_results['summary']['best_ui']['endpoint']}")
            if swagger_results["summary"]["best_api"]:
                recommendations.append(f"📖 API docs disponibles en: {swagger_results['summary']['best_api']['endpoint']}")
        
        # Recomendaciones generales
        if health_results["summary"]["total_found"] >= 2:
            recommendations.append("🎯 Servicio bien configurado con múltiples endpoints de health check")
        elif health_results["summary"]["total_found"] == 1:
            recommendations.append("⚠️  Servicio con configuración mínima de health check")
        else:
            recommendations.append("🚨 Servicio sin endpoints de health check configurados")
        
        return recommendations


# Funciones de conveniencia
async def detect_service_endpoints(base_url: str, timeout_ms: int = 5000) -> Dict[str, Dict]:
    """
    Función de conveniencia para detectar endpoints de un servicio
    
    Args:
        base_url: URL base del servicio
        timeout_ms: Timeout en milisegundos
        
    Returns:
        Resultado completo de la detección
    """
    detector = EndpointDetector(timeout_ms)
    return await detector.comprehensive_detection(base_url)


async def auto_health_check(base_url: str, timeout_ms: int = 5000) -> Dict[str, Dict]:
    """
    Health check automático usando endpoints detectados
    
    Args:
        base_url: URL base del servicio
        timeout_ms: Timeout en milisegundos
        
    Returns:
        Resultado del health check usando los mejores endpoints detectados
    """
    detector = EndpointDetector(timeout_ms)
    detection = await detector.comprehensive_detection(base_url)
    
    # Usar los mejores endpoints detectados para health check
    best_readiness = detection["health"]["summary"]["best_readiness"]
    best_liveness = detection["health"]["summary"]["best_liveness"]
    
    if not best_readiness and not best_liveness:
        return {
            "success": False,
            "error": "No se detectaron endpoints de health check válidos",
            "detection": detection
        }
    
    # Realizar health check con los endpoints detectados
    from .health import comprehensive_health_check
    
    try:
        readiness_path = best_readiness["endpoint"] if best_readiness else None
        liveness_path = best_liveness["endpoint"] if best_liveness else None
        
        if readiness_path and liveness_path:
            health_result = await comprehensive_health_check(
                base_url=base_url,
                readiness_path=readiness_path,
                liveness_path=liveness_path,
                max_latency_ms=timeout_ms
            )
        elif readiness_path:
            health_result = await comprehensive_health_check(
                base_url=base_url,
                readiness_path=readiness_path,
                liveness_path=readiness_path,  # Usar el mismo endpoint
                max_latency_ms=timeout_ms
            )
        else:
            health_result = await comprehensive_health_check(
                base_url=base_url,
                readiness_path=liveness_path,
                liveness_path=liveness_path,
                max_latency_ms=timeout_ms
            )
        
        return {
            "success": True,
            "health_check": health_result,
            "detection": detection,
            "endpoints_used": {
                "readiness": readiness_path,
                "liveness": liveness_path
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "detection": detection
        } 