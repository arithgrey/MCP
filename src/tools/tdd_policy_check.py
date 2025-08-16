"""
Herramienta MCP para verificar política TDD
Verifica que todo desarrollo siga TDD, ejecuta tests y valida ubicación de archivos de prueba
"""

import subprocess
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ViolationCode(Enum):
    TESTS_OUTSIDE_DIR = "TESTS_OUTSIDE_DIR"
    NO_TESTS_FOUND = "NO_TESTS_FOUND"
    PYTEST_NOT_FOUND = "PYTEST_NOT_FOUND"
    DOCKER_EXEC_FAILED = "DOCKER_EXEC_FAILED"
    TDD_HEURISTIC_FAILED = "TDD_HEURISTIC_FAILED"


@dataclass
class Violation:
    code: ViolationCode
    message: str
    files: List[str]


@dataclass
class TDDCheckResult:
    status: str  # "passed" | "failed"
    summary: str
    violations: List[Violation]
    metrics: Dict[str, Any]
    cmd_executed: Optional[str]
    stdout: Optional[str]
    stderr: Optional[str]


class TDDPolicyChecker:
    def __init__(self, repo_root: str = ".", container_name: str = None):
        self.repo_root = Path(repo_root).resolve()
        self.container_name = container_name
        self.tests_dir = self.repo_root / "tests"
        
    def scan(self, since_ref: str = "HEAD~1") -> TDDCheckResult:
        """Analiza el repo y valida política TDD"""
        violations = []
        metrics = {
            "tests_found": 0,
            "tests_outside_tests_dir": 0,
            "changed_modules": 0,
            "modules_with_tests": 0,
            "duration_seconds": 0
        }
        
        # 1. Verificar que existe carpeta ./tests/
        if not self.tests_dir.exists():
            violations.append(Violation(
                code=ViolationCode.NO_TESTS_FOUND,
                message="No se encontró la carpeta ./tests/",
                files=[]
            ))
            return TDDCheckResult(
                status="failed",
                summary="Falta carpeta de tests",
                violations=violations,
                metrics=metrics,
                cmd_executed=None,
                stdout=None,
                stderr=None
            )
        
        # 2. Verificar que no hay tests fuera de ./tests/
        tests_outside = self._find_tests_outside_tests_dir()
        if tests_outside:
            violations.append(Violation(
                code=ViolationCode.TESTS_OUTSIDE_DIR,
                message=f"Se encontraron {len(tests_outside)} archivos de test fuera de ./tests/",
                files=tests_outside
            ))
            metrics["tests_outside_tests_dir"] = len(tests_outside)
        
        # 3. Contar tests en ./tests/
        tests_in_tests_dir = self._count_tests_in_tests_dir()
        metrics["tests_found"] = tests_in_tests_dir
        
        # 4. Analizar cambios recientes y verificar TDD
        changed_modules = self._get_changed_modules(since_ref)
        metrics["changed_modules"] = len(changed_modules)
        
        modules_with_tests = self._check_modules_have_tests(changed_modules)
        metrics["modules_with_tests"] = modules_with_tests
        
        if changed_modules and modules_with_tests < len(changed_modules):
            violations.append(Violation(
                code=ViolationCode.TDD_HEURISTIC_FAILED,
                message=f"De {len(changed_modules)} módulos modificados, solo {modules_with_tests} tienen tests correspondientes",
                files=changed_modules
            ))
        
        # Determinar status
        status = "passed" if not violations else "failed"
        summary = self._generate_summary(violations, metrics)
        
        return TDDCheckResult(
            status=status,
            summary=summary,
            violations=violations,
            metrics=metrics,
            cmd_executed=None,
            stdout=None,
            stderr=None
        )
    
    def run_tests(self) -> TDDCheckResult:
        """Ejecuta tests con docker exec"""
        if not self.container_name:
            return TDDCheckResult(
                status="failed",
                summary="Nombre del contenedor no especificado",
                violations=[Violation(
                    code=ViolationCode.DOCKER_EXEC_FAILED,
                    message="Nombre del contenedor requerido",
                    files=[]
                )],
                metrics={},
                cmd_executed=None,
                stdout=None,
                stderr=None
            )
        
        cmd = f"docker exec {self.container_name} pytest"
        
        try:
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                cwd=self.repo_root,
                timeout=300  # 5 minutos timeout
            )
            
            status = "passed" if result.returncode == 0 else "failed"
            summary = f"Tests ejecutados con exit code: {result.returncode}"
            
            return TDDCheckResult(
                status=status,
                summary=summary,
                violations=[],
                metrics={},
                cmd_executed=cmd,
                stdout=result.stdout,
                stderr=result.stderr
            )
            
        except subprocess.TimeoutExpired:
            return TDDCheckResult(
                status="failed",
                summary="Timeout ejecutando tests",
                violations=[Violation(
                    code=ViolationCode.DOCKER_EXEC_FAILED,
                    message="Timeout ejecutando tests",
                    files=[]
                )],
                metrics={},
                cmd_executed=cmd,
                stdout=None,
                stderr="Timeout después de 5 minutos"
            )
        except Exception as e:
            return TDDCheckResult(
                status="failed",
                summary=f"Error ejecutando tests: {str(e)}",
                violations=[Violation(
                    code=ViolationCode.DOCKER_EXEC_FAILED,
                    message=f"Error ejecutando tests: {str(e)}",
                    files=[]
                )],
                metrics={},
                cmd_executed=cmd,
                stdout=None,
                stderr=str(e)
            )
    
    def full_check(self, since_ref: str = "HEAD~1") -> TDDCheckResult:
        """Ejecuta scan y si pasa, ejecuta tests"""
        scan_result = self.scan(since_ref)
        
        if scan_result.status == "failed":
            return scan_result
        
        # Si scan pasa, ejecutar tests
        run_result = self.run_tests()
        
        # Combinar métricas
        combined_metrics = {**scan_result.metrics}
        if run_result.metrics:
            combined_metrics.update(run_result.metrics)
        
        # Determinar status final
        final_status = "passed" if run_result.status == "passed" else "failed"
        final_summary = f"Scan: {scan_result.summary}. Tests: {run_result.summary}"
        
        return TDDCheckResult(
            status=final_status,
            summary=final_summary,
            violations=run_result.violations,
            metrics=combined_metrics,
            cmd_executed=run_result.cmd_executed,
            stdout=run_result.stdout,
            stderr=run_result.stderr
        )
    
    def _find_tests_outside_tests_dir(self) -> List[str]:
        """Encuentra archivos de test fuera de ./tests/"""
        test_files = []
        
        for root, dirs, files in os.walk(self.repo_root):
            # Ignorar carpeta tests y .git
            if "tests" in dirs:
                dirs.remove("tests")
            if ".git" in dirs:
                dirs.remove(".git")
            
            for file in files:
                if file.endswith('.py') and (
                    file.startswith('test_') or 
                    file.endswith('_test.py') or
                    'test' in file.lower()
                ):
                    rel_path = os.path.relpath(os.path.join(root, file), self.repo_root)
                    test_files.append(rel_path)
        
        return test_files
    
    def _count_tests_in_tests_dir(self) -> int:
        """Cuenta archivos de test en ./tests/"""
        if not self.tests_dir.exists():
            return 0
        
        count = 0
        for root, dirs, files in os.walk(self.tests_dir):
            for file in files:
                if file.endswith('.py') and (
                    file.startswith('test_') or 
                    file.endswith('_test.py') or
                    'test' in file.lower()
                ):
                    count += 1
        
        return count
    
    def _get_changed_modules(self, since_ref: str) -> List[str]:
        """Obtiene módulos modificados desde una referencia git"""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", f"{since_ref}...HEAD"],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )
            
            if result.returncode != 0:
                return []
            
            changed_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Filtrar solo archivos Python (excluyendo tests)
            python_modules = []
            for file_path in changed_files:
                if file_path.endswith('.py') and not file_path.startswith('tests/'):
                    python_modules.append(file_path)
            
            return python_modules
            
        except Exception:
            return []
    
    def _check_modules_have_tests(self, modules: List[str]) -> int:
        """Verifica cuántos módulos tienen tests correspondientes"""
        if not modules:
            return 0
        
        modules_with_tests = 0
        
        for module_path in modules:
            module_name = Path(module_path).stem
            test_file = self.tests_dir / f"test_{module_name}.py"
            
            if test_file.exists():
                modules_with_tests += 1
                continue
            
            # Buscar test con nombre alternativo
            for test_file in self.tests_dir.glob(f"*{module_name}*test*.py"):
                if test_file.exists():
                    modules_with_tests += 1
                    break
        
        return modules_with_tests
    
    def _generate_summary(self, violations: List[Violation], metrics: Dict[str, Any]) -> str:
        """Genera resumen del resultado del scan"""
        if not violations:
            return f"✅ Política TDD cumplida. {metrics['tests_found']} tests encontrados en ./tests/"
        
        violation_types = [v.code.value for v in violations]
        return f"❌ {len(violations)} violaciones encontradas: {', '.join(violation_types)}"


def tdd_policy_check(
    container_name: str,
    repo_root: str = ".",
    since_ref: str = "HEAD~1",
    action: str = "full_check"
) -> Dict[str, Any]:
    """
    Verifica política TDD y ejecuta tests según la acción especificada.
    
    Args:
        container_name: Nombre del contenedor Docker donde correr pytest
        repo_root: Ruta raíz del repo (default: ".")
        since_ref: Referencia git para analizar cambios (default: "HEAD~1")
        action: Acción a ejecutar - "scan", "run", o "full_check" (default: "full_check")
    
    Returns:
        Dict con resultado estructurado de la verificación
    """
    checker = TDDPolicyChecker(repo_root, container_name)
    
    if action == "scan":
        result = checker.scan(since_ref)
    elif action == "run":
        result = checker.run_tests()
    elif action == "full_check":
        result = checker.full_check(since_ref)
    else:
        return {
            "status": "failed",
            "summary": f"Acción '{action}' no válida. Use 'scan', 'run', o 'full_check'",
            "violations": [],
            "metrics": {},
            "cmd_executed": None,
            "stdout": None,
            "stderr": None
        }
    
    # Convertir resultado a dict serializable
    return {
        "status": result.status,
        "summary": result.summary,
        "violations": [
            {
                "code": v.code.value,
                "message": v.message,
                "files": v.files
            }
            for v in result.violations
        ],
        "metrics": result.metrics,
        "cmd_executed": result.cmd_executed,
        "stdout": result.stdout,
        "stderr": result.stderr
    } 