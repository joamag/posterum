from unittest import IsolatedAsyncioTestCase

from posterum import MemoryCache


class TestCache(IsolatedAsyncioTestCase):
    def setUp(self):
        self.cache = MemoryCache()

    def test_set_and_get(self):
        self.cache.set("key", "value")
        self.assertEqual(self.cache.get("key"), "value")

    def test_delete(self):
        self.cache.set("key", "value")
        self.cache.delete("key")
        self.assertFalse(self.cache.contains("key"))

    def test_contains(self):
        self.cache.set("key", "value")
        self.assertTrue(self.cache.contains("key"))
        self.assertFalse(self.cache.contains("nonexistent_key"))

    def test_magic_methods(self):
        self.cache["key"] = "value"
        self.assertEqual(self.cache["key"], "value")
        del self.cache["key"]
        self.assertFalse("key" in self.cache)
