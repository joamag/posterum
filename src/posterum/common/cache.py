from typing import Any


class Cache:
    def get(self, key: str):
        raise NotImplementedError()

    def set(self, key: str, value: Any):
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
        self._cache = {}

    def get(self, key: str):
        return self._cache.get(key)

    def set(self, key: str, value: Any):
        self._cache[key] = value

    def delete(self, key: str):
        del self._cache[key]

    def contains(self, key: str):
        return key in self._cache
