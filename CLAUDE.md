## Política obligatoria de ejecución de tests

- **Todos los tests DEBEN ejecutarse dentro del contenedor del servicio usando Docker.**  
- El ÚNICO formato válido es:

  ```bash
  docker exec <nombre_servicio> pytest
