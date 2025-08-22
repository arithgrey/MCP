#!/usr/bin/env python3
"""
Servicio de prueba con endpoints de health check y Swagger
"""
from flask import Flask, jsonify
import time

app = Flask(__name__)

@app.route('/v1/health/ready', methods=['GET'])
def health_ready():
    """Endpoint de readiness"""
    return jsonify({
        "status": "ready",
        "timestamp": time.time(),
        "service": "test-service"
    })

@app.route('/v1/health/live', methods=['GET'])
def health_live():
    """Endpoint de liveness"""
    return jsonify({
        "status": "alive",
        "timestamp": time.time(),
        "service": "test-service"
    })

@app.route('/v1/actuator/health/readiness', methods=['GET'])
def actuator_ready():
    """Endpoint de readiness estilo Spring Boot"""
    return jsonify({
        "status": "UP",
        "components": {
            "db": {"status": "UP"},
            "cache": {"status": "UP"}
        }
    })

@app.route('/v1/actuator/health/liveness', methods=['GET'])
def actuator_live():
    """Endpoint de liveness estilo Spring Boot"""
    return jsonify({
        "status": "UP",
        "components": {
            "ping": {"status": "UP"}
        }
    })

@app.route('/v1/health', methods=['GET'])
def health_general():
    """Endpoint de health general"""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "uptime": time.time()
    })

@app.route('/v1/swagger-ui.html', methods=['GET'])
def swagger_ui():
    """Swagger UI"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Swagger UI</title>
    </head>
    <body>
        <h1>Swagger UI</h1>
        <p>Documentación de la API</p>
    </body>
    </html>
    """

@app.route('/v1/api-docs', methods=['GET'])
def api_docs():
    """API docs en formato JSON"""
    return jsonify({
        "swagger": "2.0",
        "info": {
            "title": "Test Service API",
            "version": "1.0.0"
        },
        "paths": {
            "/v1/health/ready": {
                "get": {
                    "summary": "Health check readiness"
                }
            },
            "/v1/health/live": {
                "get": {
                    "summary": "Health check liveness"
                }
            }
        }
    })

@app.route('/v1/docs', methods=['GET'])
def docs():
    """Documentación general"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Documentation</title>
    </head>
    <body>
        <h1>API Documentation</h1>
        <h2>Health Endpoints</h2>
        <ul>
            <li><a href="/v1/health/ready">/v1/health/ready</a> - Readiness check</li>
            <li><a href="/v1/health/live">/v1/health/live</a> - Liveness check</li>
            <li><a href="/v1/health">/v1/health</a> - General health</li>
        </ul>
        <h2>Swagger</h2>
        <ul>
            <li><a href="/v1/swagger-ui.html">/v1/swagger-ui.html</a> - Swagger UI</li>
            <li><a href="/v1/api-docs">/v1/api-docs</a> - API docs JSON</li>
        </ul>
    </body>
    </html>
    """

@app.route('/v1/swagger.json', methods=['GET'])
def swagger_json():
    """Swagger JSON"""
    return jsonify({
        "swagger": "2.0",
        "info": {
            "title": "Test Service API",
            "version": "1.0.0"
        }
    })

if __name__ == '__main__':
    print("🚀 Iniciando servicio de prueba...")
    print("📍 Endpoints disponibles:")
    print("   Health: /v1/health/ready, /v1/health/live, /v1/health")
    print("   Actuator: /v1/actuator/health/readiness, /v1/actuator/health/liveness")
    print("   Swagger: /v1/swagger-ui.html, /v1/api-docs, /v1/docs, /v1/swagger.json")
    print("🌐 Servidor ejecutándose en http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True) 