from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
backend_root_str = str(BACKEND_ROOT)
if backend_root_str not in sys.path:
    sys.path.insert(0, backend_root_str)

file_env = importlib.import_module("file_env")


@pytest.fixture(autouse=True)
def isolate_backend_file_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / ".env").write_text("", encoding="utf-8")
    monkeypatch.setattr(file_env, "BACKEND_ROOT", tmp_path)
    file_env.clear_backend_file_env_cache()
    yield
    file_env.clear_backend_file_env_cache()
