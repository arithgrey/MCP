from __future__ import annotations
import time
import httpx
from datetime import datetime
from src.core.models import CheckResult, Status


async def http_check(base_url: str, path: str, timeout_ms: int) -> CheckResult:
    """
    Realiza un check HTTP básico a un endpoint
    
    Args:
        base_url: URL base del servicio
        path: Ruta del endpoint
        timeout_ms: Timeout en milisegundos
    
    Returns:
        CheckResult con el resultado del check
    """
    start_time = time.time()
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    
    try:
        async with httpx.AsyncClient(timeout=timeout_ms/1000) as client:
            response = await client.get(url)
            latency_ms = (time.time() - start_time) * 1000
            
            if response.status_code < 400:
                status = Status.HEALTHY
                error_message = None
            else:
                status = Status.UNHEALTHY
                error_message = f"HTTP {response.status_code}"
                
            return CheckResult(
                status=status,
                timestamp=datetime.now(),
                latency_ms=latency_ms,
                response_code=response.status_code,
                error_message=error_message,
                details={
                    "url": url,
                    "method": "GET",
                    "headers": dict(response.headers)
                }
            )
            
    except httpx.TimeoutException:
        latency_ms = (time.time() - start_time) * 1000
        return CheckResult(
            status=Status.UNHEALTHY,
            timestamp=datetime.now(),
            latency_ms=latency_ms,
            error_message="Timeout",
            details={"url": url, "timeout_ms": timeout_ms}
        )
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        return CheckResult(
            status=Status.UNHEALTHY,
            timestamp=datetime.now(),
            latency_ms=latency_ms,
            error_message=str(e),
            details={"url": url}
        )


async def readiness_check(base_url: str, path: str, max_latency_ms: int) -> CheckResult:
    """
    Verifica si el servicio está listo para recibir tráfico
    
    Args:
        base_url: URL base del servicio
        path: Ruta del endpoint de readiness
        max_latency_ms: Latencia máxima permitida en ms
    
    Returns:
        CheckResult con el resultado del check
    """
    result = await http_check(base_url, path, max_latency_ms * 2)
    
    # Ajustar status basado en latencia
    if result.status == Status.HEALTHY and result.latency_ms > max_latency_ms:
        result.status = Status.DEGRADED
        result.error_message = f"Latencia alta: {result.latency_ms:.2f}ms > {max_latency_ms}ms"
    
    return result


async def liveness_check(base_url: str, path: str, max_latency_ms: int) -> CheckResult:
    """
    Verifica si el servicio está vivo y funcionando
    
    Args:
        base_url: URL base del servicio
        path: Ruta del endpoint de liveness
        max_latency_ms: Latencia máxima permitida en ms
    
    Returns:
        CheckResult con el resultado del check
    """
    result = await http_check(base_url, path, max_latency_ms * 2)
    
    # Para liveness, ser más estricto con la latencia
    if result.status == Status.HEALTHY and result.latency_ms > max_latency_ms:
        result.status = Status.UNHEALTHY
        result.error_message = f"Latencia crítica: {result.latency_ms:.2f}ms > {max_latency_ms}ms"
    
    return result


async def comprehensive_health_check(
    base_url: str, 
    readiness_path: str, 
    liveness_path: str, 
    max_latency_ms: int
) -> dict:
    """
    Realiza un check completo de health del servicio
    
    Args:
        base_url: URL base del servicio
        readiness_path: Ruta del endpoint de readiness
        liveness_path: Ruta del endpoint de liveness
        max_latency_ms: Latencia máxima permitida en ms
    
    Returns:
        Dict con los resultados de ambos checks
    """
    readiness_result = await readiness_check(base_url, readiness_path, max_latency_ms)
    liveness_result = await liveness_check(base_url, liveness_path, max_latency_ms)
    
    return {
        "readiness": readiness_result.dict(),
        "liveness": liveness_result.dict(),
        "overall_status": "healthy" if (
            readiness_result.status == Status.HEALTHY and 
            liveness_result.status == Status.HEALTHY
        ) else "unhealthy"
    } 