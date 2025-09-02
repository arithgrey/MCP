import time
from pathlib import Path


def test_claude_watcher_detects_changes(tmp_path: Path = None):
    # Importar herramientas sin mocks
    from src.tools.claude_rules import (
        start_claude_watcher,
        stop_claude_watcher,
        get_cached_claude_rules,
        _get_claude_path,
    )

    # Asegurar watcher activo
    start = start_claude_watcher(0.2)
    assert start.get("success") and start.get("running"), start

    # Ruta real del archivo CLAUDE.md
    claude_path = _get_claude_path()
    original = claude_path.read_text(encoding="utf-8")

    try:
        # Leer cache inicial
        first = get_cached_claude_rules()
        assert first.get("success") is True
        assert "content" in first and len(first["content"]) > 0

        # Modificar archivo añadiendo una línea temporal
        marker = f"\nAUTO_TEST_MARKER_{int(time.time())}\n"
        claude_path.write_text(original + marker, encoding="utf-8")

        # Esperar a que el watcher detecte el cambio
        deadline = time.time() + 5
        updated = None
        while time.time() < deadline:
            updated = get_cached_claude_rules()
            if updated.get("success") and marker.strip() in updated.get("content", ""):
                break
            time.sleep(0.2)

        assert updated and updated.get("success") is True, updated
        assert marker.strip() in updated.get("content", ""), "Watcher no reflejó el cambio a tiempo"

    finally:
        # Revertir cambios del archivo para no ensuciar el repo
        claude_path.write_text(original, encoding="utf-8")
        stop = stop_claude_watcher()
        assert stop.get("success") is True 