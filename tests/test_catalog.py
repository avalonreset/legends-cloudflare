import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "prepare_catalog", Path(__file__).resolve().parents[1] / "scripts/prepare_catalog.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CatalogTests(unittest.TestCase):
    def test_preserves_other_modules_and_adds_legacy_alias(self):
        before = {"schema": 1, "version": "1.2.3", "modules": {"existing": {"version": "1.0.0"}}}
        result = module.prepare(before, {"repo": "avalonreset/legends-cloudflare"},
                                "a" * 40, "b" * 64)
        self.assertEqual(result["version"], "1.2.4")
        self.assertEqual(result["modules"]["existing"], before["modules"]["existing"])
        self.assertNotIn("legends-cloudflare", before["modules"])
        self.assertEqual(result["aliases"]["legends-cloudflare-kit"], "legends-cloudflare")

    def test_refuses_bad_pins_or_existing_module(self):
        before = {"schema": 1, "version": "1.2.3", "modules": {}}
        with self.assertRaises(ValueError):
            module.prepare(before, {}, "pending", "b" * 64)
        with self.assertRaises(ValueError):
            module.prepare(before, {}, "a" * 40, "pending")
        before["modules"]["legends-cloudflare"] = {}
        with self.assertRaises(ValueError):
            module.prepare(before, {}, "a" * 40, "b" * 64)

    def test_refuses_alias_collision(self):
        before = {"schema": 1, "version": "1.2.3", "modules": {},
                  "aliases": {"legends-cloudflare-kit": "something-else"}}
        with self.assertRaises(ValueError):
            module.prepare(before, {}, "a" * 40, "b" * 64)
