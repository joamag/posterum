from unittest import IsolatedAsyncioTestCase

from posterum import MemoryCache


class TestCache(IsolatedAsyncioTestCase):
    def setUp(self):
        self.cache = MemoryCache()

    def test_set_and_get(self):
        self.cache.set("key", "value")
        self.assertEqual(self.cache.get("key"), "value")

        self.cache["other_key"] = "value"
        self.assertEqual(self.cache.get("other_key"), "value")

        self.cache.set("key", "value", ttl=-1.0)
        self.assertEqual(self.cache.get("key"), None)

    def test_delete(self):
        self.cache.set("key", "value")
        self.assertTrue(self.cache.contains("key"))
        self.cache.delete("key")
        self.assertFalse(self.cache.contains("key"))

        self.cache["key"] = "value"
        self.assertTrue(self.cache.contains("key"))
        del self.cache["key"]
        self.assertFalse(self.cache.contains("key"))

    def test_contains(self):
        self.cache.set("key", "value")
        self.assertTrue(self.cache.contains("key"))
        self.assertFalse(self.cache.contains("non_existent_key"))

        self.cache["key"] = "value"
        self.assertTrue("key" in self.cache)
        self.assertFalse("non_existent_key" in self.cache)

        self.cache.set("key", "value", ttl=-1.0)
        self.assertFalse(self.cache.contains("key"))

    def test_magic_methods(self):
        self.cache["key"] = "value"
        self.assertEqual(self.cache["key"], "value")
        del self.cache["key"]
        self.assertFalse("key" in self.cache)
