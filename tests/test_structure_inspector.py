"""
Tests para la herramienta de inspección de estructura de microservicios
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import os

from src.tools.structure_inspector import (
    BaseStructureInspector,
    inspect_microservice_structure,
    inspect_repository_structure
)
from src.core.models import StructureStatus, StructureChecks, ConfigQuality


class TestBaseStructureInspector:
    """Tests para la clase BaseStructureInspector"""
    
    def setup_method(self):
        """Configuración antes de cada test"""
        self.temp_dir = tempfile.mkdtemp()
        self.inspector = BaseStructureInspector(self.temp_dir)
    
    def teardown_method(self):
        """Limpieza después de cada test"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_with_default_path(self):
        """Test de inicialización con ruta por defecto"""
        inspector = BaseStructureInspector()
        assert inspector.base_path == Path(".")
    
    def test_init_with_custom_path(self):
        """Test de inicialización con ruta personalizada"""
        custom_path = "/custom/path"
        inspector = BaseStructureInspector(custom_path)
        assert inspector.base_path == Path(custom_path)
    
    def test_check_basic_structure_all_files_exist(self):
        """Test de verificación de estructura básica con todos los archivos"""
        # Crear estructura completa
        service_dir = Path(self.temp_dir) / "test_service"
        service_dir.mkdir()
        
        # Crear archivos requeridos
        (service_dir / "Dockerfile").touch()
        (service_dir / "docker-compose.yml").touch()
        (service_dir / ".gitignore").touch()
        
        tests_dir = service_dir / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_example.py").touch()
        
        result = self.inspector._check_basic_structure(service_dir)
        
        assert result.Dockerfile is True
        assert result.docker_compose_yml is True
        assert result.gitignore is True
        assert result.tests_dir_exists is True
        assert result.tests_dir_has_files is True
    
    def test_check_basic_structure_missing_files(self):
        """Test de verificación de estructura básica con archivos faltantes"""
        service_dir = Path(self.temp_dir) / "test_service"
        service_dir.mkdir()
        
        # Solo crear algunos archivos
        (service_dir / "Dockerfile").touch()
        (service_dir / "docker-compose.yml").touch()
        # No crear .gitignore ni tests/
        
        result = self.inspector._check_basic_structure(service_dir)
        
        assert result.Dockerfile is True
        assert result.docker_compose_yml is True
        assert result.gitignore is False
        assert result.tests_dir_exists is False
        assert result.tests_dir_has_files is False
    
    def test_audit_dockerfile_with_warnings(self):
        """Test de auditoría de Dockerfile con warnings"""
        service_dir = Path(self.temp_dir) / "test_service"
        service_dir.mkdir()
        
        dockerfile_content = """
        FROM python:3.9
        COPY . .
        RUN apt-get install vim curl
        """
        
        (service_dir / "Dockerfile").write_text(dockerfile_content)
        
        result = self.inspector._audit_dockerfile(service_dir)
        
        assert "EXPOSE missing" in result
        assert "uses COPY . . without .dockerignore" in result
        assert "installs unnecessary tools" in result
    
    def test_audit_dockerfile_no_warnings(self):
        """Test de auditoría de Dockerfile sin warnings"""
        service_dir = Path(self.temp_dir) / "test_service"
        service_dir.mkdir()
        
        dockerfile_content = """
        FROM python:3.9-slim
        EXPOSE 8000
        COPY app.py .
        """
        
        (service_dir / "Dockerfile").write_text(dockerfile_content)
        
        result = self.inspector._audit_dockerfile(service_dir)
        
        assert len(result) == 0
    
    def test_audit_docker_compose_with_warnings(self):
        """Test de auditoría de docker-compose.yml con warnings"""
        service_dir = Path(self.temp_dir) / "test_service"
        service_dir.mkdir()
        
        compose_content = """
        version: '3.8'
        services:
          app:
            image: test:latest
        """
        
        (service_dir / "docker-compose.yml").write_text(compose_content)
        
        result = self.inspector._audit_docker_compose(service_dir)
        
        assert "no restart policy" in result
        assert "no volumes defined" in result
        assert "no networks defined" in result
        assert "no depends_on defined" in result
    
    def test_audit_docker_compose_no_warnings(self):
        """Test de auditoría de docker-compose.yml sin warnings"""
        service_dir = Path(self.temp_dir) / "test_service"
        service_dir.mkdir()
        
        compose_content = """
        version: '3.8'
        services:
          app:
            image: test:latest
            restart: unless-stopped
            volumes:
              - ./data:/app/data
            networks:
              - app-network
            depends_on:
              - db
        networks:
          app-network:
        """
        
        (service_dir / "docker-compose.yml").write_text(compose_content)
        
        result = self.inspector._audit_docker_compose(service_dir)
        
        assert len(result) == 0
    
    def test_audit_gitignore_with_warnings(self):
        """Test de auditoría de .gitignore con warnings"""
        service_dir = Path(self.temp_dir) / "test_service"
        service_dir.mkdir()
        
        gitignore_content = """
        *.log
        build/
        """
        
        (service_dir / ".gitignore").write_text(gitignore_content)
        
        result = self.inspector._audit_gitignore(service_dir)
        
        assert "missing .env" in result
        assert "missing __pycache__/" in result
        assert "missing *.pyc" in result
        assert "missing node_modules/" in result
    
    def test_audit_gitignore_no_warnings(self):
        """Test de auditoría de .gitignore sin warnings"""
        service_dir = Path(self.temp_dir) / "test_service"
        service_dir.mkdir()
        
        gitignore_content = """
        .env
        __pycache__/
        *.pyc
        node_modules/
        build/
        dist/
        .pytest_cache/
        *.log
        """
        
        (service_dir / ".gitignore").write_text(gitignore_content)
        
        result = self.inspector._audit_gitignore(service_dir)
        
        assert len(result) == 0
    
    def test_audit_tests_with_warnings(self):
        """Test de auditoría de tests con warnings"""
        service_dir = Path(self.temp_dir) / "test_service"
        service_dir.mkdir()
        
        tests_dir = service_dir / "tests"
        tests_dir.mkdir()
        
        # Crear archivo con nombre incorrecto
        (tests_dir / "example.py").touch()
        
        result = self.inspector._audit_tests(service_dir)
        
        assert "test file example.py doesn't follow naming convention" in result
    
    def test_audit_tests_no_warnings(self):
        """Test de auditoría de tests sin warnings"""
        service_dir = Path(self.temp_dir) / "test_service"
        service_dir.mkdir()
        
        tests_dir = service_dir / "tests"
        tests_dir.mkdir()
        
        # Crear archivos con nombres correctos
        (tests_dir / "test_example.py").touch()
        (tests_dir / "example_test.py").touch()
        
        result = self.inspector._audit_tests(service_dir)
        
        assert len(result) == 0
    
    def test_calculate_score_perfect(self):
        """Test de cálculo de score perfecto"""
        structure_checks = StructureChecks(
            Dockerfile=True,
            docker_compose_yml=True,
            gitignore=True,
            tests_dir_exists=True,
            tests_dir_has_files=True
        )
        
        config_quality = ConfigQuality()
        
        score = self.inspector._calculate_score(structure_checks, config_quality)
        
        assert score == 100.0
    
    def test_calculate_score_with_warnings(self):
        """Test de cálculo de score con warnings"""
        structure_checks = StructureChecks(
            Dockerfile=True,
            docker_compose_yml=True,
            gitignore=True,
            tests_dir_exists=True,
            tests_dir_has_files=True
        )
        
        config_quality = ConfigQuality(
            dockerfile_best_practices=["EXPOSE missing"],
            compose_warnings=["no restart policy"]
        )
        
        score = self.inspector._calculate_score(structure_checks, config_quality)
        
        assert score == 96.0  # 100 - (2 warnings * 2 points)
    
    def test_determine_status_complete(self):
        """Test de determinación de estado completo"""
        status = self.inspector._determine_status(85.0)
        assert status == StructureStatus.COMPLETE
    
    def test_determine_status_incomplete(self):
        """Test de determinación de estado incompleto"""
        status = self.inspector._determine_status(65.0)
        assert status == StructureStatus.INCOMPLETE
    
    def test_determine_status_poor(self):
        """Test de determinación de estado pobre"""
        status = self.inspector._determine_status(30.0)
        assert status == StructureStatus.POOR
    
    def test_generate_recommendations(self):
        """Test de generación de recomendaciones"""
        structure_checks = StructureChecks(
            Dockerfile=False,
            docker_compose_yml=True,
            gitignore=False,
            tests_dir_exists=True,
            tests_dir_has_files=False
        )
        
        config_quality = ConfigQuality(
            dockerfile_best_practices=["EXPOSE missing"],
            compose_warnings=["no restart policy"]
        )
        
        recommendations = self.inspector._generate_recommendations(structure_checks, config_quality)
        
        assert "Crear Dockerfile para containerización" in recommendations
        assert "Crear .gitignore para excluir archivos innecesarios" in recommendations
        assert "Agregar archivos de test en el directorio tests/" in recommendations
        assert "Mejorar Dockerfile siguiendo mejores prácticas" in recommendations
        assert "Mejorar docker-compose.yml con políticas de reinicio y volúmenes" in recommendations
    
    def test_auto_detect_services(self):
        """Test de detección automática de servicios"""
        # Crear directorios que podrían ser microservicios
        (Path(self.temp_dir) / "service1").mkdir()
        (Path(self.temp_dir) / "service2").mkdir()
        (Path(self.temp_dir) / "service3").mkdir()
        (Path(self.temp_dir) / ".hidden").mkdir()
        
        # Agregar Dockerfile a algunos servicios
        (Path(self.temp_dir) / "service1" / "Dockerfile").touch()
        (Path(self.temp_dir) / "service2" / "docker-compose.yml").touch()
        
        services = self.inspector._auto_detect_services()
        
        assert "service1" in services
        assert "service2" in services
        assert "service3" not in services
        assert ".hidden" not in services
    
    def test_auto_detect_services_includes_current_directory(self):
        """Test de detección automática incluyendo el directorio actual"""
        # Crear un inspector en el directorio actual
        inspector = BaseStructureInspector(".")
        
        # Simular que estamos en un directorio con estructura de microservicio
        with patch.object(inspector, '_is_microservice_directory') as mock_is_microservice:
            # Configurar el mock para que retorne True para el directorio actual
            def side_effect(path):
                return path == inspector.base_path
            
            mock_is_microservice.side_effect = side_effect
            
            services = inspector._auto_detect_services()
            
            # Debería incluir el directorio actual
            assert "." in services
            # Verificar que se llamó para el directorio actual
            assert mock_is_microservice.called
    
    def test_is_microservice_directory(self):
        """Test de verificación de directorio de microservicio"""
        inspector = BaseStructureInspector()
        
        # Crear directorio temporal con estructura de microservicio
        temp_dir = Path(self.temp_dir) / "microservice"
        temp_dir.mkdir()
        
        # Sin archivos - no es microservicio
        assert not inspector._is_microservice_directory(temp_dir)
        
        # Con Dockerfile - es microservicio
        (temp_dir / "Dockerfile").touch()
        assert inspector._is_microservice_directory(temp_dir)
        
        # Limpiar y probar con docker-compose.yml
        (temp_dir / "Dockerfile").unlink()
        (temp_dir / "docker-compose.yml").touch()
        assert inspector._is_microservice_directory(temp_dir)
    
    def test_create_error_report(self):
        """Test de creación de reporte de error"""
        error_report = self.inspector._create_error_report("test_service", "Test error")
        
        assert error_report.service == "test_service"
        assert error_report.status == StructureStatus.POOR
        assert error_report.score == 0.0
        assert "Resolver error: Test error" in error_report.recommendations


class TestStructureInspectorFunctions:
    """Tests para las funciones de conveniencia"""
    
    def setup_method(self):
        """Configuración antes de cada test"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Limpieza después de cada test"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_inspect_microservice_structure(self):
        """Test de la función inspect_microservice_structure"""
        service_dir = Path(self.temp_dir) / "test_service"
        service_dir.mkdir()
        
        # Crear estructura mínima con contenido real
        dockerfile_content = """
        FROM python:3.9-slim
        EXPOSE 8000
        WORKDIR /app
        COPY requirements.txt .
        RUN pip install -r requirements.txt
        COPY app.py .
        CMD ["python", "app.py"]
        """
        (service_dir / "Dockerfile").write_text(dockerfile_content)
        
        compose_content = """
        version: '3.8'
        services:
          app:
            build: .
            restart: unless-stopped
            volumes:
              - ./data:/app/data
            networks:
              - app-network
        networks:
          app-network:
        """
        (service_dir / "docker-compose.yml").write_text(compose_content)
        
        gitignore_content = """
        .env
        __pycache__/
        *.pyc
        node_modules/
        build/
        dist/
        .pytest_cache/
        *.log
        """
        (service_dir / ".gitignore").write_text(gitignore_content)
        
        tests_dir = service_dir / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_example.py").touch()
        
        result = inspect_microservice_structure("test_service", self.temp_dir)
        
        assert result.service == "test_service"
        assert result.status == StructureStatus.COMPLETE
        assert result.score > 0
    
    def test_inspect_repository_structure(self):
        """Test de la función inspect_repository_structure"""
        # Crear múltiples servicios con contenido real
        for i in range(3):
            service_dir = Path(self.temp_dir) / f"service_{i}"
            service_dir.mkdir()
            
            # Dockerfile con EXPOSE
            dockerfile_content = f"""
            FROM python:3.9-slim
            EXPOSE 800{i}
            WORKDIR /app
            COPY app.py .
            CMD ["python", "app.py"]
            """
            (service_dir / "Dockerfile").write_text(dockerfile_content)
            
            # docker-compose.yml con políticas
            compose_content = f"""
            version: '3.8'
            services:
              app_{i}:
                build: .
                restart: unless-stopped
                volumes:
                  - ./data:/app/data
                networks:
                  - app-network
            networks:
              app-network:
            """
            (service_dir / "docker-compose.yml").write_text(compose_content)
            
            # .gitignore completo
            gitignore_content = """
            .env
            __pycache__/
            *.pyc
            node_modules/
            build/
            dist/
            .pytest_cache/
            *.log
            """
            (service_dir / ".gitignore").write_text(gitignore_content)
            
            tests_dir = service_dir / "tests"
            tests_dir.mkdir()
            (tests_dir / "test_example.py").touch()
        
        result = inspect_repository_structure(self.temp_dir)
        
        assert result.total_services == 3
        assert result.complete_services == 3
        assert result.average_score > 80
    
    def test_inspect_microservice_structure_nonexistent(self):
        """Test de inspección de microservicio inexistente"""
        with pytest.raises(ValueError, match="El directorio nonexistent no existe"):
            inspect_microservice_structure("nonexistent", self.temp_dir)

    def test_inspect_microservice_with_specific_path(self):
        """Test de inspección de microservicio con ruta específica"""
        # Crear un microservicio en una ruta específica
        service_path = Path(self.temp_dir) / "specific_service"
        service_path.mkdir()
        
        # Crear estructura completa
        dockerfile_content = """
        FROM python:3.9-slim
        EXPOSE 8000
        WORKDIR /app
        COPY app.py .
        CMD ["python", "app.py"]
        """
        (service_path / "Dockerfile").write_text(dockerfile_content)
        
        compose_content = """
        version: '3.8'
        services:
          app:
            build: .
            restart: unless-stopped
            volumes:
              - ./data:/app/data
            networks:
              - app-network
        networks:
          app-network:
        """
        (service_path / "docker-compose.yml").write_text(compose_content)
        
        gitignore_content = """
        .env
        __pycache__/
        *.pyc
        node_modules/
        build/
        dist/
        .pytest_cache/
        *.log
        """
        (service_path / ".gitignore").write_text(gitignore_content)
        
        tests_dir = service_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_app.py").touch()
        
        # Inspeccionar usando la ruta específica
        result = inspect_microservice_structure("specific_service", self.temp_dir)
        
        # Verificar que se inspeccionó correctamente
        assert result.service == "specific_service"
        assert result.path == str(service_path)
        assert result.status == StructureStatus.COMPLETE
        assert result.score > 80
        
        # Verificar que todos los archivos fueron detectados
        assert result.structure_checks.Dockerfile is True
        assert result.structure_checks.docker_compose_yml is True
        assert result.structure_checks.gitignore is True
        assert result.structure_checks.tests_dir_exists is True
        assert result.structure_checks.tests_dir_has_files is True
    
    def test_inspect_microservice_with_nested_path(self):
        """Test de inspección de microservicio con ruta anidada"""
        # Crear estructura anidada: temp_dir/nested/deep/service
        nested_path = Path(self.temp_dir) / "nested" / "deep" / "service"
        nested_path.mkdir(parents=True)
        
        # Crear estructura básica
        (nested_path / "Dockerfile").touch()
        (nested_path / "docker-compose.yml").touch()
        (nested_path / ".gitignore").touch()
        (nested_path / "tests").mkdir()
        (nested_path / "tests" / "test_example.py").touch()
        
        # Inspeccionar usando la ruta anidada
        result = inspect_microservice_structure("nested/deep/service", self.temp_dir)
        
        # Verificar que se inspeccionó correctamente
        assert result.service == "nested/deep/service"
        assert result.path == str(nested_path)
        assert result.structure_checks.Dockerfile is True
        assert result.structure_checks.docker_compose_yml is True
        assert result.structure_checks.gitignore is True
        assert result.structure_checks.tests_dir_exists is True
        assert result.structure_checks.tests_dir_has_files is True
    
    def test_inspect_microservice_with_absolute_path(self):
        """Test de inspección de microservicio con ruta absoluta"""
        # Crear un microservicio
        service_path = Path(self.temp_dir) / "absolute_service"
        service_path.mkdir()
        
        # Crear estructura básica
        (service_path / "Dockerfile").touch()
        (service_path / "docker-compose.yml").touch()
        (service_path / ".gitignore").touch()
        (service_path / "tests").mkdir()
        (service_path / "tests" / "test_example.py").touch()
        
        # Usar ruta absoluta
        absolute_base_path = service_path.parent.absolute()
        result = inspect_microservice_structure("absolute_service", str(absolute_base_path))
        
        # Verificar que se inspeccionó correctamente
        assert result.service == "absolute_service"
        assert result.path == str(service_path)
        assert result.structure_checks.Dockerfile is True
    
    def test_inspect_microservice_path_not_found(self):
        """Test de inspección con ruta de microservicio que no existe"""
        with pytest.raises(ValueError, match="El directorio nonexistent_service no existe"):
            inspect_microservice_structure("nonexistent_service", self.temp_dir)
    
    def test_inspect_microservice_with_relative_path(self):
        """Test de inspección con ruta relativa"""
        # Crear un microservicio
        service_path = Path(self.temp_dir) / "relative_service"
        service_path.mkdir()
        
        # Crear estructura básica
        (service_path / "Dockerfile").touch()
        (service_path / "docker-compose.yml").touch()
        (service_path / ".gitignore").touch()
        (service_path / "tests").mkdir()
        (service_path / "tests" / "test_example.py").touch()
        
        # Cambiar al directorio del servicio y usar ruta relativa
        original_cwd = Path.cwd()
        try:
            os.chdir(service_path)
            result = inspect_microservice_structure(".", ".")
            
            # Verificar que se inspeccionó correctamente
            assert result.service == "."
            # La ruta puede ser relativa o absoluta, solo verificar que existe
            assert Path(result.path).exists()
            assert result.structure_checks.Dockerfile is True
        finally:
            os.chdir(original_cwd)
    
    def test_inspect_repository_with_specific_service_paths(self):
        """Test de auditoría del repositorio con rutas específicas de servicios"""
        # Crear múltiples servicios en diferentes ubicaciones
        services_to_create = [
            "service_a",
            "subdir/service_b", 
            "deep/nested/service_c"
        ]
        
        for service_path in services_to_create:
            full_path = Path(self.temp_dir) / service_path
            full_path.mkdir(parents=True)
            
            # Crear estructura básica para cada servicio con contenido real
            dockerfile_content = """
            FROM python:3.9-slim
            EXPOSE 8000
            WORKDIR /app
            COPY app.py .
            CMD ["python", "app.py"]
            """
            (full_path / "Dockerfile").write_text(dockerfile_content)
            
            compose_content = """
            version: '3.8'
            services:
              app:
                build: .
                restart: unless-stopped
                volumes:
                  - ./data:/app/data
                networks:
                  - app-network
            networks:
              app-network:
            """
            (full_path / "docker-compose.yml").write_text(compose_content)
            
            gitignore_content = """
            .env
            __pycache__/
            *.pyc
            node_modules/
            build/
            dist/
            .pytest_cache/
            *.log
            """
            (full_path / ".gitignore").write_text(gitignore_content)
            
            tests_dir = full_path / "tests"
            tests_dir.mkdir()
            (tests_dir / "test_example.py").touch()
        
        # Auditoría especificando rutas de servicios
        result = inspect_repository_structure(self.temp_dir, services_to_create)
        
        # Verificar que se inspeccionaron todos los servicios especificados
        assert result.total_services == 3
        assert result.complete_services == 3
        assert result.average_score > 80
        
        # Verificar que cada servicio fue inspeccionado
        service_names = [s.service for s in result.services]
        assert "service_a" in service_names
        assert "subdir/service_b" in service_names
        assert "deep/nested/service_c" in service_names
    
    def test_inspect_repository_auto_detection_vs_specific_paths(self):
        """Test comparando detección automática vs rutas específicas"""
        # Crear servicios en diferentes ubicaciones
        services_to_create = [
            "auto_detected_service",  # En raíz, será detectado automáticamente
            "hidden_service"          # En subdirectorio, no será detectado automáticamente
        ]
        
        for service_path in services_to_create:
            full_path = Path(self.temp_dir) / service_path
            full_path.mkdir(parents=True)
            
            # Crear estructura básica con contenido real para que sea COMPLETE
            dockerfile_content = """
            FROM python:3.9-slim
            EXPOSE 8000
            WORKDIR /app
            COPY app.py .
            CMD ["python", "app.py"]
            """
            (full_path / "Dockerfile").write_text(dockerfile_content)
            
            compose_content = """
            version: '3.8'
            services:
              app:
                build: .
                restart: unless-stopped
                volumes:
                  - ./data:/app/data
                networks:
                  - app-network
            networks:
              app-network:
            """
            (full_path / "docker-compose.yml").write_text(compose_content)
            
            gitignore_content = """
            .env
            __pycache__/
            *.pyc
            node_modules/
            build/
            dist/
            .pytest_cache/
            *.log
            """
            (full_path / ".gitignore").write_text(gitignore_content)
            
            tests_dir = full_path / "tests"
            tests_dir.mkdir()
            (tests_dir / "test_example.py").touch()
        
        # Auditoría con detección automática
        auto_result = inspect_repository_structure(self.temp_dir)
        
        # Auditoría con rutas específicas
        specific_result = inspect_repository_structure(self.temp_dir, services_to_create)
        
        # La detección automática debería encontrar ambos servicios (están en directorios con Dockerfile)
        assert auto_result.total_services == 2
        assert auto_result.complete_services == 2
        
        # Las rutas específicas deberían encontrar ambos servicios
        assert specific_result.total_services == 2
        assert specific_result.complete_services == 2
    
    def test_inspect_microservice_readonly_analysis(self):
        """Test que verifica que la herramienta solo lee archivos, no los modifica"""
        # Crear un microservicio con contenido específico
        service_path = Path(self.temp_dir) / "readonly_service"
        service_path.mkdir()
        
        # Crear archivos con contenido específico
        original_dockerfile_content = """
        FROM python:3.9
        COPY . .
        """
        (service_path / "Dockerfile").write_text(original_dockerfile_content)
        
        original_compose_content = """
        version: '3.8'
        services:
          app:
            build: .
        """
        (service_path / "docker-compose.yml").write_text(original_compose_content)
        
        original_gitignore_content = """
        *.log
        """
        (service_path / ".gitignore").write_text(original_gitignore_content)
        
        # Guardar timestamps originales
        original_dockerfile_mtime = (service_path / "Dockerfile").stat().st_mtime
        original_compose_mtime = (service_path / "docker-compose.yml").stat().st_mtime
        original_gitignore_mtime = (service_path / ".gitignore").stat().st_mtime
        
        # Inspeccionar el microservicio
        result = inspect_microservice_structure("readonly_service", self.temp_dir)
        
        # Verificar que se inspeccionó correctamente
        assert result.service == "readonly_service"
        # Con archivos vacíos y warnings, el score será bajo
        assert result.status == StructureStatus.POOR  # Score bajo por muchos warnings
        
        # Verificar que se detectaron los warnings esperados
        assert "EXPOSE missing" in result.config_quality.dockerfile_best_practices
        assert "uses COPY . . without .dockerignore" in result.config_quality.dockerfile_best_practices
        assert "no restart policy" in result.config_quality.compose_warnings
        assert "missing .env" in result.config_quality.gitignore_warnings
        
        # Verificar que los archivos NO fueron modificados
        assert (service_path / "Dockerfile").stat().st_mtime == original_dockerfile_mtime
        assert (service_path / "docker-compose.yml").stat().st_mtime == original_compose_mtime
        assert (service_path / ".gitignore").stat().st_mtime == original_gitignore_mtime
        
        # Verificar que el contenido NO cambió
        assert (service_path / "Dockerfile").read_text() == original_dockerfile_content
        assert (service_path / "docker-compose.yml").read_text() == original_compose_content
        assert (service_path / ".gitignore").read_text() == original_gitignore_content
        
        # Verificar que solo se proporciona información, no modificaciones
        assert len(result.recommendations) > 0  # Debería tener recomendaciones
        assert "Mejorar Dockerfile siguiendo mejores prácticas" in result.recommendations
        assert "Mejorar docker-compose.yml con políticas de reinicio y volúmenes" in result.recommendations
        assert "Mejorar .gitignore con patrones estándar" in result.recommendations 