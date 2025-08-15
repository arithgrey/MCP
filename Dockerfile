# Dockerfile para el servicio MCP
FROM python:3.11-slim

# Instalar dependencias del sistema mínimas
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt ./

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .


# Exponer puerto 3000 para SSE
EXPOSE 3000

# Variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1g_s   

# Configura el entrypoint para ejecutar las migraciones y levantar el servidor
ENTRYPOINT ["/app/watch.sh"]
