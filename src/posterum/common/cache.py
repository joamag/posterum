from time import time
from typing import Any, NamedTuple

Key = Any
Value = Any
CacheItem = NamedTuple(
    "CacheItem", [("value", Any), ("timestamp", float), ("timeout", float | None)]
)


class Cache:
    def get(self, key: Key, default: Any | None = None) -> Any:
        raise NotImplementedError()

    def get_item(self, key: Key) -> CacheItem:
        raise NotImplementedError()

    def set(self, key: Key, value: Any, ttl: float | None = None):
        raise NotImplementedError()

    def delete(self, key: Key):
        raise NotImplementedError()

    def contains(self, key: Key) -> bool:
        raise NotImplementedError()

    def timestamp(self, key: Key) -> float:
        raise NotImplementedError()

    def __getitem__(self, key: Key):
        return self.get(key)

    def __setitem__(self, key: Key, value: Value):
        return self.set(key, value)

    def __delitem__(self, key: Key):
        return self.delete(key)

    def __contains__(self, key: Key):
        return self.contains(key)


class MemoryCache(Cache):
    def __init__(self) -> None:
        super().__init__()
        self._cache: dict[str, CacheItem] = {}

    def get(self, key: Key, default: Any | None = None) -> Any:
        value, _, timeout = self._cache.get(key, (default, None, None))
        if not timeout is None and time() > timeout:
            self.delete(key)
            return default
        return value

    def get_item(self, key: Key) -> CacheItem:
        item = self._cache[key]
        _, _, timeout = item
        if not timeout is None and time() > timeout:
            self.delete(key)
            raise KeyError(key)
        return item

    def set(self, key: Key, value: Value, ttl: float | None = None):
        timestamp = time()
        self._cache[key] = (
            CacheItem(value, timestamp, timestamp + ttl)
            if ttl
            else CacheItem(value, timestamp, None)
        )

    def delete(self, key: Key):
        del self._cache[key]

    def contains(self, key: Key) -> bool:
        if not key in self._cache:
            return False
        _, _, timeout = self._cache[key]
        return timeout is None or time() <= timeout

    def timestamp(self, key: Key) -> float:
        _, timestamp, _ = self._cache[key]
        return timestamp
