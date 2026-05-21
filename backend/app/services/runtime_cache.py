from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from time import monotonic
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class _CacheEntry(Generic[V]):
    expires_at: float
    value: V


class TTLCache(Generic[K, V]):
    def __init__(self, ttl_seconds: int = 300) -> None:
        self.ttl_seconds = max(0, ttl_seconds)
        self._entries: dict[K, _CacheEntry[V]] = {}

    def get(self, key: K) -> V | None:
        entry = self._entries.get(key)
        if entry is None:
            return None

        if entry.expires_at <= monotonic():
            self._entries.pop(key, None)
            return None

        return deepcopy(entry.value)

    def set(self, key: K, value: V) -> None:
        if self.ttl_seconds <= 0:
            return

        self._entries[key] = _CacheEntry(
            expires_at=monotonic() + self.ttl_seconds,
            value=deepcopy(value),
        )
