# Service Landings - Microservicio de Landing Pages

## 🎯 Descripción

Microservicio para gestionar múltiples landing pages por producto. Permite crear templates reutilizables y landings específicas para cada producto con configuración personalizada.

## 🏗️ Arquitectura

- **Framework**: Django 4.2.7 + Django REST Framework
- **Base de Datos**: SQLite (MVP) / PostgreSQL (Producción)
- **Contenedorización**: Docker + Docker Compose
- **API**: RESTful con paginación automática
- **Auto-reload**: Gunicorn con StatReloader para desarrollo
- **Documentación**: Swagger/OpenAPI con drf-yasg

## 🚀 Instalación y Ejecución

### Prerrequisitos
- Docker
- Docker Compose

### Pasos de instalación

1. **Clonar el repositorio**
```bash
cd ~/enid_service/services/service-landings
```

2. **Construir y ejecutar**
```bash
docker-compose build
docker-compose up -d
```

3. **Ejecutar migraciones**
```bash
docker exec service-landings-service-landings-1 python manage.py migrate
```

4. **Crear superusuario (opcional)**
```bash
docker exec service-landings-service-landings-1 python manage.py createsuperuser
```

5. **Crear datos de ejemplo**
```bash
docker exec service-landings-service-landings-1 python create_sample_data.py
```

### 🔄 Auto-reload en desarrollo

El microservicio incluye auto-reload automático:
- **Gunicorn** con **StatReloader** detecta cambios en archivos `.py`
- **Reinicio automático** cuando se modifican archivos del código
- **Sin necesidad de reconstruir** la imagen Docker
- **Logs en tiempo real** del proceso de reload

### 📚 Documentación API (Swagger)

El microservicio incluye documentación automática de la API:
- **Swagger UI**: http://localhost:8084/swagger/
- **ReDoc**: http://localhost:8084/redoc/
- **Schema JSON**: http://localhost:8084/swagger.json/
- **Documentación automática** de todos los endpoints
- **Ejemplos de uso** y parámetros

### 🏠 Landing por Defecto

El microservicio incluye una landing por defecto precargada usando **Django Signals** (igual que otros microservicios):
- **Nombre**: "Deportes"
- **Slug**: "kits-para-pasar-al-siguiente-nivel"
- **Product ID**: 999 (especial para landing por defecto)
- **Template**: Deportes Template (tipo hero)
- **Configuración**: Colores verdes (#059669, #10b981)
- **Carga automática**: Al ejecutar migraciones con `DJANGO_RUNNING_MIGRATIONS=True`
- **Archivo**: `app/landing/signals.py`
- **Logs detallados**: Muestra qué templates y landings se crean/existen

### 🗄️ Base de Datos

- **PostgreSQL**: Base de datos principal (puerto 5445)
- **Configuración**: Igual que otros microservicios del proyecto
- **Variables de entorno**:
  - `POSTGRES_DB=landings_db`
  - `POSTGRES_USER=landings_user`
  - `POSTGRES_PASSWORD=landings_password`
  - `POSTGRES_HOST=postgres`
  - `POSTGRES_PORT=5432`

## 📊 Modelos de Datos

### LandingTemplate
- **name**: Nombre del template
- **slug**: Identificador único
- **template_type**: Tipo de template (hero, product, testimonial, etc.)
- **config**: Configuración JSON del template
- **is_active**: Estado activo/inactivo

### Landing
- **name**: Nombre de la landing
- **slug**: Identificador único para URL
- **product_id**: ID del producto en enid-store
- **template**: Template asociado
- **config**: Configuración específica de la landing
- **is_active**: Estado activo/inactivo

## 🔌 API Endpoints

### Templates
- `GET /api/landings/templates/` - Listar templates
- `POST /api/landings/templates/` - Crear template
- `GET /api/landings/templates/{id}/` - Obtener template
- `PUT /api/landings/templates/{id}/` - Actualizar template
- `DELETE /api/landings/templates/{id}/` - Eliminar template
- `GET /api/landings/templates/by_type/?type=hero` - Filtrar por tipo

### Landings
- `GET /api/landings/pages/` - Listar landings
- `POST /api/landings/pages/` - Crear landing
- `GET /api/landings/pages/{id}/` - Obtener landing
- `PUT /api/landings/pages/{id}/` - Actualizar landing
- `DELETE /api/landings/pages/{id}/` - Eliminar landing
- `GET /api/landings/pages/by_product/?product_id=1` - Landings por producto
- `GET /api/landings/pages/search/?q=busqueda` - Buscar landings
- `GET /api/landings/pages/{id}/config/` - Configuración completa

## 🧪 Testing

### Ejecutar tests
```bash
docker exec service-landings-service-landings-1 python manage.py test
```

### Ejecutar tests específicos
```bash
docker exec service-landings-service-landings-1 python manage.py test tests.test_basic
```

## 📝 Ejemplos de Uso

### 1. Crear un template
```bash
curl -X POST http://localhost:8084/api/landings/templates/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mi Template",
    "slug": "mi-template",
    "template_type": "hero",
    "config": {
      "title": "Título por defecto",
      "subtitle": "Subtítulo por defecto"
    }
  }'
```

### 2. Crear una landing
```bash
curl -X POST http://localhost:8084/api/landings/pages/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mi Landing",
    "slug": "mi-landing",
    "product_id": 123,
    "template_id": 1,
    "config": {
      "custom_title": "Título personalizado",
      "custom_subtitle": "Subtítulo personalizado"
    }
  }'
```

### 3. Obtener landings de un producto
```bash
curl http://localhost:8084/api/landings/pages/by_product/?product_id=123
```

## 🔧 Configuración

### Variables de entorno
- `DEBUG`: Modo debug (default: True)
- `SECRET_KEY`: Clave secreta de Django
- `ALLOWED_HOSTS`: Hosts permitidos

### Base de datos
- **Desarrollo**: SQLite (db.sqlite3)
- **Producción**: PostgreSQL (configurar en settings.py)

## 📈 Próximas características

- [ ] Analytics de landings
- [ ] A/B testing
- [ ] Caché con Redis
- [ ] Autenticación JWT
- [ ] Webhooks para notificaciones
- [ ] Dashboard de métricas

## 🤝 Integración con otros servicios

### Enid-Store
El microservicio se integra con `enid-store` mediante el campo `product_id` que referencia al ID del producto en el servicio principal.

### Frontend
El frontend puede consumir las APIs para:
- Mostrar múltiples landings por producto
- Renderizar templates dinámicamente
- Personalizar contenido por landing

## 📞 Soporte

Para soporte técnico o preguntas, contactar al equipo de desarrollo. 