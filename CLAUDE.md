## MANDATORY Development Workflow

**CRITICAL**: Estas reglas son OBLIGATORIAS y no pueden romperse bajo ninguna circunstancia.

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

5. **Se debe aplicar siempre TDD (Test Driven Development)**  
   - Las pruebas deben escribirse **antes** de implementar la lógica de negocio.  
   - Las pruebas deben ser a nivel **integración**, nunca basadas en mocks.  
   - Cada feature debe estar cubierta por escenarios reales simulando el flujo end-to-end.  
   - Los tests unitarios son opcionales, pero las pruebas de integración son obligatorias.

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
