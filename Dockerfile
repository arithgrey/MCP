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

# Copiar código fuente
COPY src/ ./src/
COPY run_server.py ./

# Exponer puerto 3000 para SSE
EXPOSE 3000

# Variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Comando de inicio - ejecutar watchmedo como solicitaste
CMD ["watchmedo", "auto-restart", \
     "--directory=./", \
     "--pattern=*.py", \
     "--recursive", \
     "--", \
     "python", "run_server.py"] 