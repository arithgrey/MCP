from pathlib import Path
from typing import Dict, Any, Optional
import threading
import time

# Configuración por defecto del watcher (intervalo en segundos)
_DEFAULT_POLL_INTERVAL_SEC = 1.0

# Estado global del watcher y caché simple en memoria
_cached_content: Optional[str] = None
_cached_path: Optional[str] = None
_last_mtime: Optional[float] = None
_watcher_thread: Optional[threading.Thread] = None
_stop_event: Optional[threading.Event] = None
_poll_interval: float = _DEFAULT_POLL_INTERVAL_SEC


def _find_repo_root_with_claude(start: Path) -> Path:
    current = start
    # Buscar hacia arriba hasta 8 niveles el primer CLAUDE.md
    for _ in range(8):
        candidate = current / "CLAUDE.md"
        if candidate.exists():
            return current
        if current.parent == current:
            break
        current = current.parent
    # Fallback: directorio original
    return start


def _get_claude_path() -> Path:
    # Partimos desde el directorio "src" del proyecto
    src_dir = Path(__file__).resolve().parents[2]
    repo_root = _find_repo_root_with_claude(src_dir)
    return repo_root / "CLAUDE.md"


def load_claude_rules() -> Dict[str, Any]:
    """Carga el contenido de CLAUDE.md como recurso de reglas.

    Returns:
        dict: { success: bool, path: str, content: str }
    """
    try:
        claude_path = _get_claude_path()
        if not claude_path.exists():
            return {
                "success": False,
                "error": f"CLAUDE.md no encontrado en {claude_path}",
                "path": str(claude_path),
            }
        content = claude_path.read_text(encoding="utf-8")
        return {
            "success": True,
            "path": str(claude_path),
            "content": content,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _refresh_cache_if_needed() -> None:
    global _cached_content, _cached_path, _last_mtime
    path = _get_claude_path()
    if not path.exists():
        return
    try:
        mtime = path.stat().st_mtime
        if _last_mtime is None or mtime != _last_mtime:
            _cached_content = path.read_text(encoding="utf-8")
            _cached_path = str(path)
            _last_mtime = mtime
    except Exception:
        # Evitar romper el watcher por lecturas concurrentes
        pass


def _watcher_loop():
    while _stop_event and not _stop_event.is_set():
        _refresh_cache_if_needed()
        time.sleep(_poll_interval)


def start_claude_watcher(poll_interval_sec: float = _DEFAULT_POLL_INTERVAL_SEC) -> Dict[str, Any]:
    global _watcher_thread, _stop_event, _poll_interval
    if _watcher_thread and _watcher_thread.is_alive():
        return {"success": True, "running": True, "note": "Watcher ya estaba activo"}
    _poll_interval = max(0.1, float(poll_interval_sec))
    _stop_event = threading.Event()
    _watcher_thread = threading.Thread(target=_watcher_loop, daemon=True)
    _watcher_thread.start()
    # Forzar una primera carga
    _refresh_cache_if_needed()
    return {"success": True, "running": True, "poll_interval_sec": _poll_interval}


def stop_claude_watcher() -> Dict[str, Any]:
    global _watcher_thread, _stop_event
    if _stop_event:
        _stop_event.set()
    if _watcher_thread:
        _watcher_thread.join(timeout=2.0)
    running = _watcher_thread.is_alive() if _watcher_thread else False
    return {"success": True, "running": running}


def is_claude_watcher_running() -> Dict[str, Any]:
    running = _watcher_thread.is_alive() if _watcher_thread else False
    return {"success": True, "running": running, "poll_interval_sec": _poll_interval}


def get_cached_claude_rules() -> Dict[str, Any]:
    """Devuelve el contenido en caché del CLAUDE.md. Inicia el watcher si aún no corre."""
    if not (_watcher_thread and _watcher_thread.is_alive()):
        start_claude_watcher(_poll_interval)
    _refresh_cache_if_needed()
    if _cached_content is None:
        # Si aún no hay caché, cargar directamente
        loaded = load_claude_rules()
        if loaded.get("success"):
            return {"success": True, "path": loaded.get("path"), "content": loaded.get("content"), "from_cache": False}
        return loaded
    return {"success": True, "path": _cached_path, "content": _cached_content, "from_cache": True} 