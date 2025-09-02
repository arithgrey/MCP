import os
from pathlib import Path


def test_claude_md_exists():
    project_root = Path(__file__).resolve().parent.parent
    claude_path = project_root / "CLAUDE.md"
    assert claude_path.exists(), f"No se encontró CLAUDE.md en {claude_path}"
    assert claude_path.is_file(), "CLAUDE.md no es un archivo regular"


def test_load_claude_rules_integration():
    # Importación directa del lector de reglas (sin mocks)
    from src.tools.claude_rules import load_claude_rules

    result = load_claude_rules()

    assert isinstance(result, dict), "El resultado debe ser un dict"
    assert result.get("success") is True, result

    content = result.get("content", "")
    assert isinstance(content, str) and len(content) > 20, "Contenido de CLAUDE.md vacío o inválido"

    # Aserciones de integración sobre partes clave del contenido real
    assert "MANDATORY Development Workflow" in content, "No se encontró encabezado esperado en CLAUDE.md"
    assert "TDD" in content and "integración" in content, "No se mencionan reglas de TDD de integración"

    # Verificar que la ruta detectada corresponda al archivo real
    expected_path = Path(__file__).resolve().parent.parent / "CLAUDE.md"
    assert Path(result.get("path", "")).resolve() == expected_path.resolve(), "Ruta de CLAUDE.md incorrecta" 