"""
=========================================================
BursaAI Cache Manager
Version : 6.0 Sprint 5A.0
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from time import monotonic
from typing import Any, Dict, Optional


@dataclass(slots=True)
class CacheEntry:
    value: Any
    created_at: float
    expires_at: Optional[float] = None

    @property
    def expired(self) -> bool:
        return (
            self.expires_at is not None
            and monotonic() >= self.expires_at
        )


class CacheManager:
    """
    Simple in-memory TTL cache.
    """

    def __init__(self):
        self._entries: Dict[str, CacheEntry] = {}

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[float] = None,
    ) -> None:
        now = monotonic()

        expires_at = None

        if ttl_seconds is not None:
            ttl = max(float(ttl_seconds), 0.0)
            expires_at = now + ttl

        self._entries[str(key)] = CacheEntry(
            value=value,
            created_at=now,
            expires_at=expires_at,
        )

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        normalized = str(key)
        entry = self._entries.get(normalized)

        if entry is None:
            return default

        if entry.expired:
            self._entries.pop(normalized, None)
            return default

        return entry.value

    def has(self, key: str) -> bool:
        sentinel = object()
        return self.get(key, sentinel) is not sentinel

    def delete(self, key: str) -> None:
        self._entries.pop(str(key), None)

    def clear(self) -> None:
        self._entries.clear()

    def cleanup(self) -> int:
        expired_keys = [
            key
            for key, entry in self._entries.items()
            if entry.expired
        ]

        for key in expired_keys:
            self._entries.pop(key, None)

        return len(expired_keys)

    def size(self) -> int:
        self.cleanup()
        return len(self._entries)
