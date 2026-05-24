from __future__ import annotations

from pathlib import Path

from file_env import clear_backend_file_env_cache, load_backend_file_env


def test_backend_file_env_reads_backend_dotenv_file(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text(
        "BACKEND_AUTH_ADMIN_USERNAME=dotenv-admin\n"
        "BACKEND_AUTH_TOKEN_SECRET=dotenv-secret\n"
        "BACKEND_HTTP_TIMEOUT=9\n",
        encoding="utf-8",
    )

    clear_backend_file_env_cache()
    payload = load_backend_file_env(tmp_path)

    assert payload["BACKEND_AUTH_ADMIN_USERNAME"] == "dotenv-admin"
    assert payload["BACKEND_HTTP_TIMEOUT"] == "9"
    assert payload["BACKEND_AUTH_TOKEN_SECRET"] == "dotenv-secret"
