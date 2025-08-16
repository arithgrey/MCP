"""
Tests para la herramienta de verificación de política TDD
"""

import pytest
from src.tools.tdd_policy_check import TDDPolicyChecker, ViolationCode


def test_tdd_policy_checker_initialization():
    """Test de inicialización del checker"""
    checker = TDDPolicyChecker(".", "test-container")
    assert checker.repo_root.exists()
    assert checker.container_name == "test-container"
    assert checker.tests_dir.name == "tests"


def test_find_tests_outside_tests_dir():
    """Test para encontrar tests fuera del directorio tests/"""
    checker = TDDPolicyChecker(".", "test-container")
    
    # No debería haber tests fuera de tests/ en este repo
    tests_outside = checker._find_tests_outside_tests_dir()
    assert isinstance(tests_outside, list)


def test_count_tests_in_tests_dir():
    """Test para contar tests en el directorio tests/"""
    checker = TDDPolicyChecker(".", "test-container")
    
    # Debería encontrar al menos este archivo de test
    count = checker._count_tests_in_tests_dir()
    assert count >= 1


def test_generate_summary():
    """Test para generar resumen"""
    checker = TDDPolicyChecker(".", "test-container")
    
    # Test con violaciones
    from src.tools.tdd_policy_check import Violation
    violations = [
        Violation(
            code=ViolationCode.TESTS_OUTSIDE_DIR,
            message="Test fuera de tests/",
            files=["test_file.py"]
        )
    ]
    metrics = {"tests_found": 5}
    
    summary = checker._generate_summary(violations, metrics)
    assert "❌" in summary
    assert "violaciones encontradas" in summary
    
    # Test sin violaciones
    summary_no_violations = checker._generate_summary([], metrics)
    assert "✅" in summary_no_violations
    assert "Política TDD cumplida" in summary_no_violations


if __name__ == "__main__":
    pytest.main([__file__]) 