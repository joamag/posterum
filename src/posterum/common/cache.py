from time import time
from typing import Any


class Cache:
    def get(self, key: str):
        raise NotImplementedError()

    def set(self, key: str, value: Any, ttl: float | None = None):
        raise NotImplementedError()

    def delete(self, key: str):
        raise NotImplementedError()

    def contains(self, key: str):
        raise NotImplementedError()

    def __getitem__(self, key: str):
        return self.get(key)

    def __setitem__(self, key: str, value: Any):
        return self.set(key, value)

    def __delitem__(self, key: str):
        return self.delete(key)

    def __contains__(self, key: str):
        return self.contains(key)


class MemoryCache(Cache):
    def __init__(self):
        super().__init__()
        self._cache: dict[str, tuple[float, Any]] = {}

    def get(self, key: str, default=None):
        value, timeout = self._cache.get(key, (default, None))
        if not timeout is None and time() > timeout:
            self.delete(key)
            return default
        return value

    def set(self, key: str, value: Any, ttl: float | None = None):
        self._cache[key] = (value, (time() + ttl) if ttl else None)

    def delete(self, key: str):
        del self._cache[key]

    def contains(self, key: str):
        if not key in self._cache:
            return False
        _, timeout = self._cache[key]
        return timeout is None or time() <= timeout
