## MANDATORY Development Workflow

**CRITICAL**: Estas reglas son OBLIGATORIAS y no pueden romperse bajo ninguna circunstancia.

0. **Toma siempre el rol de Arquitecto de Software y Desarrollador Senior**  
   - Todas las decisiones, sugerencias y evaluaciones deben realizarse con mentalidad de **arquitectura de software avanzada**.  
   - Se debe priorizar la calidad del código, la escalabilidad, la mantenibilidad y la simplicidad.  
  
1. **Todas las aplicaciones y servicios se ejecutan únicamente con Docker o docker-compose**  
   - No se permite correr aplicaciones directamente en el host.  
   - Cualquier comando debe ser traducido a un `docker exec` o `docker-compose run`.  
   - Ejemplo:  
     - ✅ `docker exec <nombre_servicio> pytest`  
     - ❌ `pytest` en el host  
   - Ejemplo:  
     - ✅ `docker-compose up`  
     - ❌ `python main.py` en el host  

2. **Los tests siempre deben correrse dentro de contenedores**  
   - Formato estándar:  
     ```bash
     docker exec <nombre_servicio> pytest
     ```

3. **Todos los microservicios y librerías deben seguir patrones de diseño SOLID**  
   - Cada clase debe tener una única responsabilidad.  
   - El código debe ser extensible sin necesidad de modificarse (Open/Closed Principle).  
   - Se deben aplicar interfaces claras y principios de inversión de dependencias.

4. **El código debe respetar el principio DRY (Don't Repeat Yourself)**  
   - No se permite duplicar lógica.  
   - Funciones, helpers y módulos reutilizables deben extraerse en directorios adecuados.

5. **Política de Pruebas: TDD, Integración, sin Mocks**  
   - **TDD estricto**: escribir y fallar la prueba **antes** de la implementación.  
   - **Integración end-to-end** obligatoria: pruebas ejercen el sistema real (red interna, contenedor de DB, colas, etc.).  
   - **Prohibido usar mocks/stubs/fakes**: `unittest.mock`, `pytest-mock`, `monkeypatch`, dobles manuales o interceptar I/O.  
   - **Fuentes de datos reales de prueba**: usar contenedores declarados en `docker-compose.test.yml` (DB/Redis/Kafka/etc.).  
   - **Estructura recomendada**:
     ```
     /tests/integration/
       test_<feature>_e2e.py
     ```
   - ✅ Ejemplos correctos:
     - `docker-compose -f docker-compose.test.yml up -d db redis && docker exec <svc> pytest -k integration`
     - Prueba que hace `POST /api/v1/...` y valida respuesta + persistencia real.
   - ❌ Ejemplos prohibidos:
     - `from unittest import mock` / `from unittest.mock import patch`
     - `import pytest; @pytest.fixture(autouse=True) def _fake_db(...): ...`
     - `monkeypatch.setenv(...)` para simular comportamientos.
   - **Notas**: Si se requieren datos, se cargan **fixtures reales** en la DB de pruebas del contenedor (migraciones + seeds).


6. **Las pipelines de CI/CD deben ejecutar siempre los tests con docker-compose**  
   - Ningún paso puede ejecutar dependencias o binarios directamente en el host.  
   - El flujo válido es:  
     ```bash
     docker-compose build
     docker-compose up -d
     docker exec <nombre_servicio> pytest
     ```

7. **El MCP (Model Context Protocol) forma parte del flujo de desarrollo**  
   - MCP está activo y disponible para apoyar en la verificación de **mejores prácticas**.  
   - El agente debe consultar MCP como fuente de verdad para confirmar cumplimiento de:  
     - Uso de Docker y docker-compose.  
     - Respeto de principios SOLID y DRY.  
     - Correcta aplicación de TDD a nivel de integración.  
   - Cualquier desviación identificada por MCP debe documentarse y corregirse antes de aprobar cambios.

8. **La documentación solo se genera cuando los requerimientos han sido verificados**  
   - No se debe documentar automáticamente un cambio o feature en el momento de su implementación.  
   - Primero se debe comprobar que los **nuevos requerimientos han sido logrados** con éxito.  
   - Una vez verificado, el agente debe **preguntar explícitamente** si se desea generar documentación.  
   - Solo en caso afirmativo se procederá a documentar en `/docs` en formato Markdown.

9. **Reglas para Frontend (`@/service-store`)**  
   - Cualquier cambio, implementación o solicitud sobre el frontend **debe realizarse exclusivamente en el directorio `@/service-store`**.  
   - No se deben crear directorios alternos ni modificar rutas fuera de `@/service-store`.  
   - Todas las dependencias, componentes y configuraciones de frontend deben estar centralizadas en `@/service-store`.

10. **Restricciones adicionales**  
   - Está **estrictamente prohibido** crear o utilizar **Makefiles**.  
   - Está **estrictamente prohibido** crear o utilizar archivos **.sh** para automatizar comandos.  
   - Todo flujo debe implementarse únicamente mediante **docker-compose** y comandos explícitos documentados.
