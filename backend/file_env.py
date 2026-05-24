from __future__ import annotations

from functools import lru_cache
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent


def _parse_env_text(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue

        if value[:1] == value[-1:] and value[:1] in {'"', "'"}:
            value = value[1:-1]
        elif " #" in value:
            value = value.split(" #", 1)[0].rstrip()

        values[key] = value
    return values


@lru_cache(maxsize=8)
def _load_backend_file_env_cached(root_dir: str) -> dict[str, str]:
    env_root = Path(root_dir)
    values: dict[str, str] = {}
    path = env_root / ".env"
    if path.exists():
        values.update(_parse_env_text(path.read_text(encoding="utf-8")))

    return values


def load_backend_file_env(root_dir: Path | None = None) -> dict[str, str]:
    env_root = root_dir or BACKEND_ROOT
    return dict(_load_backend_file_env_cached(str(env_root.resolve())))


def clear_backend_file_env_cache() -> None:
    _load_backend_file_env_cached.cache_clear()


def get_backend_env_value(name: str, default: str = "") -> str:
    return load_backend_file_env().get(name, default)


def get_backend_env_int(name: str, default: int) -> int:
    raw = get_backend_env_value(name, str(default)).strip()
    try:
        return int(raw)
    except ValueError:
        return default


def get_backend_env_flag(name: str, default: bool = False) -> bool:
    raw = load_backend_file_env().get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}
