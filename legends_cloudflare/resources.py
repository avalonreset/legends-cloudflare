"""Resolve packaged or source-checkout knowledge resources without network access."""
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

MAX_FILE_BYTES = 1_048_576
_MACOS_SYSTEM_SYMLINKS = {Path("/var"), Path("/tmp"), Path("/etc")}


class ResourceError(RuntimeError):
    """Raised when packaged knowledge resources are missing or corrupted."""


def check_no_symlink_chain(path, stop_at=None):
    target = Path(path)
    stop = Path(stop_at) if stop_at is not None else None
    current = target
    while True:
        if current.is_symlink():
            if not (sys.platform == "darwin" and current in _MACOS_SYSTEM_SYMLINKS):
                raise ResourceError(f"Symlink refused in resource path: {current}")
        if stop is not None and current == stop:
            break
        parent = current.parent
        if parent == current:
            break
        current = parent


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _strict_json_loads(raw_text):
    return json.loads(raw_text, object_pairs_hook=_reject_duplicate_keys)


def _read_bounded_bytes(path, *, max_bytes=MAX_FILE_BYTES, stop_at=None):
    target = Path(path)
    check_no_symlink_chain(target, stop_at=stop_at)
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(target, flags)
    except OSError as exc:
        raise ResourceError(f"Unable to open resource file: {target}") from exc
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise ResourceError(f"Resource path is not a regular file: {target}")
        if st.st_size > max_bytes:
            raise ResourceError(f"Resource file exceeds {max_bytes} byte limit: {target}")
        chunks = []
        total = 0
        while True:
            chunk = os.read(fd, min(65536, max_bytes + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > max_bytes:
                raise ResourceError(f"Resource file exceeds {max_bytes} byte limit: {target}")
        return b"".join(chunks)
    finally:
        os.close(fd)


def candidate_roots(package_dir=None):
    base = Path(package_dir) if package_dir else Path(__file__).resolve().parent
    return [
        ("package_data", (base / "_data").resolve()),
        ("checkout", base.parent.resolve()),
    ]


def verify_root(root):
    root = Path(root)
    if root.is_symlink():
        raise ResourceError(f"Symlink refused in resource root: {root}")
    recipe = root / "docs" / "AGENT-RECIPE.md"
    pack_dir = root / "knowledge"
    pack_manifest = pack_dir / "cloudflare" / "pack.json"
    if not (recipe.exists() or recipe.is_symlink()) or not (
        pack_manifest.exists() or pack_manifest.is_symlink()
    ):
        return None
    _read_bounded_bytes(recipe, max_bytes=MAX_FILE_BYTES, stop_at=root)
    try:
        raw_manifest = _read_bounded_bytes(
            pack_manifest, max_bytes=MAX_FILE_BYTES, stop_at=root
        ).decode("utf-8")
        manifest = _strict_json_loads(raw_manifest)
        entries = manifest["files"]
    except (OSError, UnicodeDecodeError, ValueError, KeyError, TypeError) as exc:
        raise ResourceError("Invalid knowledge pack manifest.") from exc
    if not isinstance(entries, list) or not entries:
        raise ResourceError("Knowledge pack manifest has no files.")
    pack_files = [str(pack_manifest.resolve())]
    vault = pack_manifest.parent / "vault"
    check_no_symlink_chain(vault, stop_at=root)
    resolved_vault = vault.resolve()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ResourceError("Invalid knowledge pack file entry.")
        rel = entry.get("path", "")
        expected = entry.get("sha256", "")
        if not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
            raise ResourceError("Unsafe knowledge pack path.")
        raw_target = vault / rel
        if not (raw_target.exists() or raw_target.is_symlink()):
            raise ResourceError(f"Missing knowledge pack file: {rel}")
        raw_bytes = _read_bounded_bytes(raw_target, max_bytes=MAX_FILE_BYTES, stop_at=root)
        target = raw_target.resolve()
        if not target.is_relative_to(resolved_vault):
            raise ResourceError(f"Unsafe knowledge pack path: {rel}")
        digest = hashlib.sha256(raw_bytes).hexdigest()
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
