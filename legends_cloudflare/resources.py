"""Resolve packaged or source-checkout knowledge resources without network access."""
import hashlib
import json
from pathlib import Path


class ResourceError(RuntimeError):
    """Raised when packaged knowledge resources are missing or corrupted."""


def candidate_roots(package_dir=None):
    base = Path(package_dir) if package_dir else Path(__file__).resolve().parent
    return [
        ("package_data", (base / "_data").resolve()),
        ("checkout", base.parent.resolve()),
    ]


def verify_root(root):
    recipe = root / "docs" / "AGENT-RECIPE.md"
    pack_dir = root / "knowledge"
    pack_manifest = pack_dir / "cloudflare" / "pack.json"
    if not recipe.is_file() or not pack_manifest.is_file():
        return None
    try:
        manifest = json.loads(pack_manifest.read_text(encoding="utf-8"))
        entries = manifest["files"]
    except (OSError, ValueError, KeyError) as exc:
        raise ResourceError("Invalid knowledge pack manifest.") from exc
    if not isinstance(entries, list) or not entries:
        raise ResourceError("Knowledge pack manifest has no files.")
    pack_files = [str(pack_manifest.resolve())]
    vault = pack_manifest.parent / "vault"
    for entry in entries:
        rel = entry.get("path", "")
        expected = entry.get("sha256", "")
        if not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
            raise ResourceError("Unsafe knowledge pack path.")
        target = (vault / rel).resolve()
        if not target.is_relative_to(vault.resolve()) or not target.is_file():
            raise ResourceError(f"Missing knowledge pack file: {rel}")
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        if digest != expected:
            raise ResourceError(f"Knowledge pack hash mismatch: {rel}")
        pack_files.append(str(target))
    return {
        "ok": True,
        "complete": True,
        "root": str(root),
        "recipe": str(recipe.resolve()),
        "pack_dir": str(pack_dir.resolve()),
        "pack_manifest": str(pack_manifest.resolve()),
        "pack_files": pack_files,
    }


def resolve_resources(package_dir=None):
    for source, root in candidate_roots(package_dir):
        verified = verify_root(root)
        if verified is not None:
            verified["source"] = source
            return verified
    raise ResourceError("Unable to locate complete legends-cloudflare knowledge resources.")
