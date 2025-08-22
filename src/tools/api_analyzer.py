"""
Analizador inteligente de APIs OpenAPI/Swagger
Permite al MCP entender la estructura completa de una API
"""
import asyncio
import httpx
import json
import yaml
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from datetime import datetime


@dataclass
class APIEndpoint:
    """Representa un endpoint de la API"""
    path: str
    methods: List[str]
    summary: Optional[str]
    description: Optional[str]
    parameters: List[Dict[str, Any]]
    request_body: Optional[Dict[str, Any]]
    responses: Dict[str, Dict[str, Any]]
    tags: List[str]
    operation_id: Optional[str]
    deprecated: bool = False


@dataclass
class APIModel:
    """Representa un modelo/schema de la API"""
    name: str
    type: str
    properties: Dict[str, Any]
    required: List[str]
    description: Optional[str]
    example: Optional[Any]


@dataclass
class APITag:
    """Representa un tag/categoría de la API"""
    name: str
    description: Optional[str]
    external_docs: Optional[Dict[str, str]]


class APIAnalyzer:
    """
    Analizador inteligente de APIs OpenAPI/Swagger
    Permite entender la estructura completa de una API
    """
    
    def __init__(self, timeout_ms: int = 10000):
        self.timeout_ms = timeout_ms
        self.spec_cache = {}
    
    async def analyze_api_from_url(self, base_url: str, swagger_path: str = None) -> Dict[str, Any]:
        """
        Analiza una API completa desde una URL base
        
        Args:
            base_url: URL base del servicio
            swagger_path: Ruta específica del Swagger (opcional)
            
        Returns:
            Análisis completo de la API
        """
        print(f"🔍 Analizando API desde: {base_url}")
        
        # Detectar endpoint de Swagger si no se proporciona
        if not swagger_path:
            swagger_info = await self._detect_swagger_endpoint(base_url)
            if not swagger_info["found"]:
                return {
                    "success": False,
                    "error": "No se pudo detectar endpoint de Swagger/OpenAPI",
                    "detection_attempt": swagger_info
                }
            swagger_path = swagger_info["best_endpoint"]
        
        # Obtener especificación OpenAPI
        spec_url = urljoin(base_url, swagger_path)
        spec = await self._fetch_openapi_spec(spec_url)
        
        if not spec["success"]:
            return spec
        
        # Analizar la especificación
        analysis = await self._analyze_openapi_spec(spec["spec"], base_url)
        
        return {
            "success": True,
            "api_url": base_url,
            "swagger_endpoint": swagger_path,
            "analysis_timestamp": datetime.now().isoformat(),
            "specification": spec["spec"],
            "analysis": analysis
        }
    
    async def _detect_swagger_endpoint(self, base_url: str) -> Dict[str, Any]:
        """Detecta el mejor endpoint de Swagger disponible"""
        swagger_endpoints = [
            "/swagger.json", "/openapi.json", "/swagger.yaml", "/openapi.yaml",
            "/api-docs", "/docs", "/v1/swagger.json", "/v1/openapi.json"
        ]
        
        best_endpoint = None
        best_latency = float('inf')
        
        for endpoint in swagger_endpoints:
            url = urljoin(base_url, endpoint)
            try:
                start_time = asyncio.get_event_loop().time()
                async with httpx.AsyncClient(timeout=self.timeout_ms/1000) as client:
                    response = await client.get(url)
                    latency = (asyncio.get_event_loop().time() - start_time) * 1000
                    
                    if response.status_code == 200:
                        content_type = response.headers.get("content-type", "")
                        if any(ct in content_type.lower() for ct in ["json", "yaml", "text"]):
                            if latency < best_latency:
                                best_latency = latency
                                best_endpoint = endpoint
                                
            except Exception:
                continue
        
        return {
            "found": best_endpoint is not None,
            "best_endpoint": best_endpoint,
            "latency_ms": best_latency if best_endpoint else None
        }
    
    async def _fetch_openapi_spec(self, spec_url: str) -> Dict[str, Any]:
        """Obtiene la especificación OpenAPI desde la URL"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout_ms/1000) as client:
                response = await client.get(spec_url)
                response.raise_for_status()
                
                content_type = response.headers.get("content-type", "")
                
                # Parsear según el tipo de contenido
                if "json" in content_type.lower():
                    spec = response.json()
                elif "yaml" in content_type.lower() or "text/plain" in content_type.lower():
                    try:
                        spec = yaml.safe_load(response.text)
                    except yaml.YAMLError:
                        # Intentar parsear como JSON si falla YAML
                        spec = response.json()
                else:
                    # Intentar parsear como JSON por defecto
                    spec = response.json()
                
                return {"success": True, "spec": spec}
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": spec_url
            }
    
    async def _analyze_openapi_spec(self, spec: Dict[str, Any], base_url: str) -> Dict[str, Any]:
        """Analiza la especificación OpenAPI completa"""
        analysis = {
            "info": self._extract_api_info(spec),
            "servers": self._extract_servers(spec),
            "endpoints": await self._extract_endpoints(spec, base_url),
            "models": self._extract_models(spec),
            "tags": self._extract_tags(spec),
            "security": self._extract_security(spec),
            "statistics": self._generate_statistics(spec)
        }
        
        return analysis
    
    def _extract_api_info(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae información básica de la API"""
        info = spec.get("info", {})
        return {
            "title": info.get("title", "API Sin Título"),
            "version": info.get("version", "1.0.0"),
            "description": info.get("description", "Sin descripción"),
            "contact": info.get("contact", {}),
            "license": info.get("license", {}),
            "terms_of_service": info.get("termsOfService")
        }
    
    def _extract_servers(self, spec: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extrae información de servidores"""
        servers = spec.get("servers", [])
        return [
            {
                "url": server.get("url", ""),
                "description": server.get("description", ""),
                "variables": server.get("variables", {})
            }
            for server in servers
        ]
    
    async def _extract_endpoints(self, spec: Dict[str, Any], base_url: str) -> List[APIEndpoint]:
        """Extrae todos los endpoints de la API"""
        endpoints = []
        paths = spec.get("paths", {})
        
        for path, path_item in paths.items():
            # Obtener métodos HTTP disponibles
            methods = []
            for method in ["get", "post", "put", "delete", "patch", "head", "options"]:
                if method in path_item:
                    methods.append(method.upper())
            
            if not methods:
                continue
            
            # Crear endpoint para cada método
            for method in methods:
                operation = path_item[method.lower()]
                
                endpoint = APIEndpoint(
                    path=path,
                    methods=[method],
                    summary=operation.get("summary"),
                    description=operation.get("description"),
                    parameters=operation.get("parameters", []),
                    request_body=operation.get("requestBody"),
                    responses=operation.get("responses", {}),
                    tags=operation.get("tags", []),
                    operation_id=operation.get("operationId"),
                    deprecated=operation.get("deprecated", False)
                )
                
                endpoints.append(endpoint)
        
        return endpoints
    
    def _extract_models(self, spec: Dict[str, Any]) -> List[APIModel]:
        """Extrae todos los modelos/schemas de la API"""
        models = []
        schemas = spec.get("components", {}).get("schemas", {})
        
        for name, schema in schemas.items():
            model = APIModel(
                name=name,
                type=schema.get("type", "object"),
                properties=schema.get("properties", {}),
                required=schema.get("required", []),
                description=schema.get("description"),
                example=schema.get("example")
            )
            models.append(model)
        
        return models
    
    def _extract_tags(self, spec: Dict[str, Any]) -> List[APITag]:
        """Extrae todos los tags de la API"""
        tags = spec.get("tags", [])
        return [
            APITag(
                name=tag.get("name", ""),
                description=tag.get("description"),
                external_docs=tag.get("externalDocs")
            )
            for tag in tags
        ]
    
    def _extract_security(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae información de seguridad de la API"""
        return {
            "security_schemes": spec.get("components", {}).get("securitySchemes", {}),
            "global_security": spec.get("security", []),
            "requires_authentication": bool(spec.get("security", []))
        }
    
    def _generate_statistics(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Genera estadísticas de la API"""
        paths = spec.get("paths", {})
        schemas = spec.get("components", {}).get("schemas", {})
        tags = spec.get("tags", [])
        
        # Contar métodos HTTP por endpoint
        total_endpoints = 0
        method_counts = {"GET": 0, "POST": 0, "PUT": 0, "DELETE": 0, "PATCH": 0}
        
        for path, path_item in paths.items():
            for method in method_counts.keys():
                if method.lower() in path_item:
                    method_counts[method] += 1
                    total_endpoints += 1
        
        return {
            "total_paths": len(paths),
            "total_endpoints": total_endpoints,
            "total_models": len(schemas),
            "total_tags": len(tags),
            "method_distribution": method_counts,
            "has_authentication": bool(spec.get("security", [])),
            "openapi_version": spec.get("openapi", "unknown")
        }
    
    async def generate_api_documentation(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Genera documentación inteligente de la API"""
        endpoints = analysis["endpoints"]
        models = analysis["models"]
        tags = analysis["tags"]
        
        # Agrupar endpoints por tags
        endpoints_by_tag = {}
        for endpoint in endpoints:
            for tag in endpoint.tags:
                if tag not in endpoints_by_tag:
                    endpoints_by_tag[tag] = []
                endpoints_by_tag[tag].append(endpoint)
        
        # Generar resumen ejecutivo
        summary = {
            "total_endpoints": len(endpoints),
            "total_models": len(models),
            "total_tags": len(tags),
            "main_functionality": self._identify_main_functionality(endpoints),
            "complexity_level": self._assess_complexity(analysis["statistics"]),
            "recommendations": self._generate_api_recommendations(analysis)
        }
        
        return {
            "summary": summary,
            "endpoints_by_tag": endpoints_by_tag,
            "models_overview": self._generate_models_overview(models),
            "api_patterns": self._identify_api_patterns(endpoints),
            "usage_examples": self._generate_usage_examples(endpoints, models)
        }
    
    def _identify_main_functionality(self, endpoints: List[APIEndpoint]) -> List[str]:
        """Identifica la funcionalidad principal de la API"""
        functionality = []
        
        # Analizar patrones en los paths
        path_patterns = {}
        for endpoint in endpoints:
            path_parts = endpoint.path.split("/")
            if len(path_parts) > 1:
                resource = path_parts[1]
                if resource not in path_patterns:
                    path_patterns[resource] = 0
                path_patterns[resource] += 1
        
        # Identificar recursos principales
        main_resources = sorted(path_patterns.items(), key=lambda x: x[1], reverse=True)[:5]
        for resource, count in main_resources:
            if count > 1:  # Solo recursos con múltiples endpoints
                functionality.append(f"{resource} ({count} endpoints)")
        
        return functionality
    
    def _assess_complexity(self, stats: Dict[str, Any]) -> str:
        """Evalúa el nivel de complejidad de la API"""
        total_endpoints = stats["total_endpoints"]
        total_models = stats["total_models"]
        
        if total_endpoints < 10 and total_models < 5:
            return "Baja"
        elif total_endpoints < 50 and total_models < 20:
            return "Media"
        else:
            return "Alta"
    
    def _generate_api_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones para la API"""
        recommendations = []
        stats = analysis["statistics"]
        
        if stats["total_endpoints"] == 0:
            recommendations.append("⚠️ La API no tiene endpoints definidos")
        
        if stats["total_models"] == 0:
            recommendations.append("⚠️ La API no tiene modelos/schemas definidos")
        
        if not stats["has_authentication"]:
            recommendations.append("🔒 Considerar implementar autenticación para la API")
        
        if stats["method_distribution"]["GET"] > stats["method_distribution"]["POST"] * 2:
            recommendations.append("📊 La API está sesgada hacia operaciones de lectura")
        
        if stats["openapi_version"] == "unknown":
            recommendations.append("📚 Especificar versión de OpenAPI para mejor compatibilidad")
        
        return recommendations
    
    def _generate_models_overview(self, models: List[APIModel]) -> Dict[str, Any]:
        """Genera una vista general de los modelos"""
        return {
            "total_models": len(models),
            "model_types": list(set(model.type for model in models)),
            "models_with_examples": len([m for m in models if m.example]),
            "models_with_descriptions": len([m for m in models if m.description])
        }
    
    def _identify_api_patterns(self, endpoints: List[APIEndpoint]) -> Dict[str, Any]:
        """Identifica patrones comunes en la API"""
        patterns = {
            "crud_operations": 0,
            "search_endpoints": 0,
            "bulk_operations": 0,
            "webhook_endpoints": 0
        }
        
        for endpoint in endpoints:
            path_lower = endpoint.path.lower()
            
            # Detectar operaciones CRUD
            if any(method in endpoint.methods for method in ["POST", "PUT", "DELETE"]):
                patterns["crud_operations"] += 1
            
            # Detectar endpoints de búsqueda
            if "search" in path_lower or "query" in path_lower:
                patterns["search_endpoints"] += 1
            
            # Detectar operaciones en lote
            if "bulk" in path_lower or "batch" in path_lower:
                patterns["bulk_operations"] += 1
            
            # Detectar webhooks
            if "webhook" in path_lower or "callback" in path_lower:
                patterns["webhook_endpoints"] += 1
        
        return patterns
    
    def _generate_usage_examples(self, endpoints: List[APIEndpoint], models: List[APIModel]) -> List[Dict[str, Any]]:
        """Genera ejemplos de uso para endpoints principales"""
        examples = []
        
        # Seleccionar endpoints representativos
        representative_endpoints = []
        for endpoint in endpoints:
            if endpoint.summary and len(endpoint.methods) > 0:
                representative_endpoints.append(endpoint)
        
        # Generar ejemplos para los primeros 5 endpoints
        for endpoint in representative_endpoints[:5]:
            example = {
                "endpoint": endpoint.path,
                "method": endpoint.methods[0],
                "summary": endpoint.summary,
                "example_request": self._generate_request_example(endpoint, models),
                "example_response": self._generate_response_example(endpoint)
            }
            examples.append(example)
        
        return examples
    
    def _generate_request_example(self, endpoint: APIEndpoint, models: List[APIModel]) -> Dict[str, Any]:
        """Genera un ejemplo de request para un endpoint"""
        if not endpoint.request_body:
            return {"message": "No requiere body"}
        
        # Buscar schema del request body
        content = endpoint.request_body.get("content", {})
        if "application/json" in content:
            schema = content["application/json"].get("schema", {})
            return self._generate_schema_example(schema, models)
        
        return {"message": "Request body no especificado"}
    
    def _generate_response_example(self, endpoint: APIEndpoint) -> Dict[str, Any]:
        """Genera un ejemplo de response para un endpoint"""
        responses = endpoint.responses
        
        # Buscar response exitoso (200, 201, etc.)
        success_codes = ["200", "201", "202"]
        for code in success_codes:
            if code in responses:
                response = responses[code]
                content = response.get("content", {})
                if "application/json" in content:
                    schema = content["application/json"].get("schema", {})
                    return {
                        "status_code": code,
                        "description": response.get("description", ""),
                        "example": self._generate_schema_example(schema, [])
                    }
        
        return {"message": "Response no especificado"}
    
    def _generate_schema_example(self, schema: Dict[str, Any], models: List[APIModel]) -> Any:
        """Genera un ejemplo basado en un schema"""
        if "example" in schema:
            return schema["example"]
        
        schema_type = schema.get("type", "object")
        
        if schema_type == "string":
            return "ejemplo_string"
        elif schema_type == "integer":
            return 123
        elif schema_type == "number":
            return 123.45
        elif schema_type == "boolean":
            return True
        elif schema_type == "array":
            items = schema.get("items", {})
            return [self._generate_schema_example(items, models)]
        elif schema_type == "object":
            properties = schema.get("properties", {})
            example = {}
            for prop_name, prop_schema in properties.items():
                example[prop_name] = self._generate_schema_example(prop_schema, models)
            return example
        
        return "ejemplo"


# Funciones de conveniencia
async def analyze_api_service(base_url: str, swagger_path: str = None, timeout_ms: int = 10000) -> Dict[str, Any]:
    """
    Función de conveniencia para analizar una API completa
    
    Args:
        base_url: URL base del servicio
        swagger_path: Ruta específica del Swagger (opcional)
        timeout_ms: Timeout en milisegundos
        
    Returns:
        Análisis completo de la API
    """
    analyzer = APIAnalyzer(timeout_ms)
    return await analyzer.analyze_api_from_url(base_url, swagger_path)


async def generate_api_docs(base_url: str, swagger_path: str = None, timeout_ms: int = 10000) -> Dict[str, Any]:
    """
    Genera documentación completa de una API
    
    Args:
        base_url: URL base del servicio
        swagger_path: Ruta específica del Swagger (opcional)
        timeout_ms: Timeout en milisegundos
        
    Returns:
        Documentación completa de la API
    """
    analyzer = APIAnalyzer(timeout_ms)
    analysis = await analyzer.analyze_api_from_url(base_url, swagger_path)
    
    if not analysis["success"]:
        return analysis
    
    docs = await analyzer.generate_api_documentation(analysis["analysis"])
    
    return {
        "success": True,
        "api_url": base_url,
        "documentation": docs,
        "raw_analysis": analysis
    } 