"""Verify build-time data mirror and packaged resources."""
import hashlib
from importlib import metadata as importlib_metadata
from pathlib import Path
import posixpath
import re
import tempfile
import unittest
from urllib.parse import unquote

from legends_cloudflare.resources import MAX_FILE_BYTES, ResourceError, resolve_resources, verify_root

ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
REQUIRED_DATA = [
    "legends_cloudflare/_data/README.md",
    "legends_cloudflare/_data/LICENSE",
    "legends_cloudflare/_data/NOTICE",
    "legends_cloudflare/_data/THIRD_PARTY_NOTICES.md",
    "legends_cloudflare/_data/SUPPORT.md",
    "legends_cloudflare/_data/CONTRIBUTING.md",
    "legends_cloudflare/_data/CODE_OF_CONDUCT.md",
    "legends_cloudflare/_data/PRIVACY.md",
    "legends_cloudflare/_data/AGENTS.md",
    "legends_cloudflare/_data/docs/AGENT-RECIPE.md",
    "legends_cloudflare/_data/knowledge/cloudflare/pack.json",
    "legends_cloudflare/_data/wiki/index.md",
    "legends_cloudflare/_data/references/sources.md",
    "legends_cloudflare/_data/templates/change-receipt.md",
    "legends_cloudflare/_data/skills/cto-legends/SKILL.md",
    "legends_cloudflare/_data/SECURITY.md",
    "legends_cloudflare/_data/CHANGELOG.md",
    "legends_cloudflare/_data/.legends-module",
    "legends_cloudflare/_data/.legends-router-pin",
]


def load_mirror():
    try:
        import setuptools  # noqa: F401
    except ImportError:
        raise unittest.SkipTest("setuptools is required to evaluate the data mirror")
    raw = (ROOT / "setup.py").read_text(encoding="utf-8")
    source = raw.replace("from setuptools import setup", "# setup() stubbed", 1)
    namespace = {"setup": lambda *args, **kwargs: None}
    exec(source, namespace)
    return namespace


def mirror_members():
    namespace = load_mirror()
    return {rel.as_posix(): src for src, rel in namespace["iter_mirror_sources"](ROOT)}


def local_target(raw):
    if raw.startswith(("https://", "http://", "mailto:", "#", "data:")):
        return None
    target = unquote(raw.split("#", 1)[0].split("?", 1)[0]).strip()
    return target or None


def check_membership(members):
    errors = []
    dirs = {"."}
    for name in members:
        parent = posixpath.dirname(name)
        while parent and parent != ".":
            dirs.add(parent)
            parent = posixpath.dirname(parent)
    for page in sorted(name for name in members if name.endswith(".md")):
        text = members[page].read_text(encoding="utf-8-sig")
        for raw in LINK_RE.findall(text):
            target = local_target(raw)
            if target is None:
                continue
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(page), target))
            if resolved == "." or resolved.startswith(".."):
                errors.append(f"Escapes mirror: {page}: {raw}")
            elif resolved not in members and resolved not in dirs:
                errors.append(f"Dangling in mirror: {page}: {raw}")
    return errors


class PackagingTest(unittest.TestCase):
    def test_mirror_sources_exist_and_links_resolve(self):
        members = mirror_members()
        for key in ("README.md", "LICENSE", "AGENTS.md", "docs/AGENT-RECIPE.md",
                    "knowledge/cloudflare/pack.json", "wiki/index.md"):
            self.assertIn(key, members)
        self.assertEqual(check_membership(members), [])

    def test_checkout_resources_resolve(self):
        report = resolve_resources()
        self.assertTrue(report["ok"])
        self.assertTrue(report["complete"])
        self.assertTrue(Path(report["recipe"]).is_file())
        self.assertGreaterEqual(len(report["pack_files"]), 9)

    def test_missing_resources_raise(self):
        with self.assertRaises(ResourceError):
            resolve_resources(Path("/nonexistent/legends-cloudflare-pkg"))

    def test_verify_root_rejects_oversized_and_duplicate_key_pack(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir(parents=True)
            (root / "knowledge" / "cloudflare" / "vault").mkdir(parents=True)
            recipe = root / "docs" / "AGENT-RECIPE.md"
            recipe.write_text("# Recipe\n", encoding="utf-8")
            pack_manifest = root / "knowledge" / "cloudflare" / "pack.json"
            pack_manifest.write_text(
                '{"files":[{"path":"index.md","sha256":"00"}],"files":[]}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ResourceError, "Invalid knowledge pack manifest"):
                verify_root(root)

            vault_file = root / "knowledge" / "cloudflare" / "vault" / "index.md"
            vault_file.write_bytes(b"x" * (MAX_FILE_BYTES + 1))
            digest = hashlib.sha256(vault_file.read_bytes()).hexdigest()
            pack_manifest.write_text(
                f'{{"files":[{{"path":"index.md","sha256":"{digest}"}}]}}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ResourceError, "exceeds"):
                verify_root(root)

    def test_verify_root_rejects_symlink(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir(parents=True)
            (root / "knowledge" / "cloudflare" / "vault").mkdir(parents=True)
            recipe = root / "docs" / "AGENT-RECIPE.md"
            recipe.write_text("# Recipe\n", encoding="utf-8")
            pack_manifest = root / "knowledge" / "cloudflare" / "pack.json"
            pack_manifest.write_text('{"files":[]}', encoding="utf-8")
            orig_is_symlink = Path.is_symlink

            def fake_is_symlink(self_path):
                if self_path.name == "AGENT-RECIPE.md":
                    return True
                return orig_is_symlink(self_path)

            with patch.object(Path, "is_symlink", fake_is_symlink):
                with self.assertRaisesRegex(ResourceError, "Symlink refused"):
                    verify_root(root)


class WheelSmoke(unittest.TestCase):
    def test_installed_wheel_ships_full_mirror(self):
        target = None
        for dist in importlib_metadata.distributions():
            if (dist.metadata["Name"] or "").lower() == "legends-cloudflare":
                anchor = getattr(dist, "_path", None)
                if anchor is not None and Path(anchor).suffix == ".dist-info":
                    target = dist
                    break
        if target is None:
            self.skipTest("requires installed legends-cloudflare wheel")
        names = {str(entry).replace("\\", "/") for entry in (target.files or [])}
        missing = [name for name in REQUIRED_DATA if name not in names]
        self.assertEqual(missing, [])
