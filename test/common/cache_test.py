from time import sleep, time
from unittest import IsolatedAsyncioTestCase

from posterum import Cache, MemoryCache


class TestCache(IsolatedAsyncioTestCase):
    def setUp(self):
        self.cache = MemoryCache()

    def test_not_implemented(self):
        cache = Cache()
        self.assertRaises(NotImplementedError, cache.get, "key")
        self.assertRaises(NotImplementedError, cache.get_item, "key")
        self.assertRaises(NotImplementedError, cache.set, "key", "value")
        self.assertRaises(NotImplementedError, cache.delete, "key")
        self.assertRaises(NotImplementedError, cache.contains, "key")
        self.assertRaises(NotImplementedError, cache.timestamp, "key")

    def test_set_and_get(self):
        self.cache.set("key", "value")
        self.assertEqual(self.cache.get("key"), "value")

        self.cache["other_key"] = "value"
        self.assertEqual(self.cache.get("other_key"), "value")

        self.cache.set("key", "value", ttl=-1.0)
        self.assertEqual(self.cache.get("key"), None)

        self.assertEqual(self.cache.get("non_existent_key"), None)
        self.assertEqual(self.cache.get("non_existent_key", "default"), "default")

    def test_get_item(self):
        self.cache.set("key", "value")
        value, timestamp, timeout = self.cache.get_item("key")
        self.assertEqual(value, "value")
        self.assertEqual(timeout, None)
        self.assertTrue(timestamp <= time())

        self.assertRaises(KeyError, self.cache.get_item, "non_existent_key")

        self.cache.set("key", "value", ttl=-1.0)
        self.assertRaises(KeyError, self.cache.get_item, "key")
        self.assertFalse(self.cache.contains("key"))

    def test_set_ttl(self):
        self.cache.set("key", "value", ttl=3600.0)
        _, timestamp, timeout = self.cache.get_item("key")
        self.assertEqual(timeout, timestamp + 3600.0)

        self.cache.set("permanent", "value")
        self.cache.set("immediate", "value", ttl=0.0)
        sleep(0.01)
        self.assertEqual(self.cache.get("permanent"), "value")
        self.assertEqual(self.cache.get("immediate"), None)

    def test_delete(self):
        self.cache.set("key", "value")
        self.assertTrue(self.cache.contains("key"))
        self.cache.delete("key")
        self.assertFalse(self.cache.contains("key"))

        self.cache["key"] = "value"
        self.assertTrue(self.cache.contains("key"))
        del self.cache["key"]
        self.assertFalse(self.cache.contains("key"))

        self.assertRaises(KeyError, self.cache.delete, "non_existent_key")

    def test_contains(self):
        self.cache.set("key", "value")
        self.assertTrue(self.cache.contains("key"))
        self.assertFalse(self.cache.contains("non_existent_key"))

        self.cache["key"] = "value"
        self.assertTrue("key" in self.cache)
        self.assertFalse("non_existent_key" in self.cache)

        self.cache.set("key", "value", ttl=-1.0)
        self.assertFalse(self.cache.contains("key"))

    def test_timestamp(self):
        before = time()
        self.cache.set("key", "value")
        self.assertTrue(self.cache.timestamp("key") >= before)
        self.assertTrue(self.cache.timestamp("key") <= time())

        self.assertRaises(KeyError, self.cache.timestamp, "non_existent_key")

    def test_magic_methods(self):
        self.cache["key"] = "value"
        self.assertEqual(self.cache["key"], "value")
        del self.cache["key"]
        self.assertFalse("key" in self.cache)
