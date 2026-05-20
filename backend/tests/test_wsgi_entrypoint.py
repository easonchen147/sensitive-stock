from __future__ import annotations

import importlib.util
from pathlib import Path


def test_wsgi_entrypoint_imports_backend_app_factory() -> None:
    wsgi_path = Path(__file__).resolve().parents[1] / "wsgi.py"
    spec = importlib.util.spec_from_file_location("smoke_wsgi_entrypoint", wsgi_path)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.application is not None
