#!/bin/bash

# Script para cargar variables de entorno para el servicio MCP

echo "🔧 Cargando variables de entorno..."

# Cargar variables desde env.example
if [ -f env.example ]; then
    export $(cat env.example | grep -v '^#' | xargs)
    echo "✅ Variables de entorno cargadas desde env.example"
else
    echo "⚠️  Archivo env.example no encontrado, usando valores por defecto"
fi

# Mostrar configuración actual
echo "📋 Configuración actual:"
echo "   MCP_HOST: ${MCP_HOST:-0.0.0.0}"
echo "   MCP_PORT: ${MCP_PORT:-3000}"
echo "   MCP_PROXY_TOKEN: ${MCP_PROXY_TOKEN:-test123}"

echo "🚀 Ejecutando docker-compose..."
docker-compose up -d 