"""Write a reviewable catalog candidate after real release pins are available."""
import argparse
import copy
import json
import os
from pathlib import Path
import re
import stat
import sys

MAX_CATALOG_BYTES = 1_048_576
_MACOS_SYSTEM_SYMLINKS = {Path("/var"), Path("/tmp"), Path("/etc")}


def check_no_symlink_chain(path):
    current = Path(path)
    while True:
        if current.is_symlink():
            if not (sys.platform == "darwin" and current in _MACOS_SYSTEM_SYMLINKS):
                raise ValueError(f"Refusing symlink path: {current}")
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


def read_bounded_json(path, max_bytes=MAX_CATALOG_BYTES):
    target = Path(path)
    check_no_symlink_chain(target)
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(target, flags)
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise ValueError(f"Expected a regular file: {target}")
        if st.st_size > max_bytes:
            raise ValueError(f"JSON input exceeds {max_bytes} byte limit: {target}")
        raw = os.read(fd, max_bytes + 1)
        if len(raw) > max_bytes:
            raise ValueError(f"JSON input exceeds {max_bytes} byte limit: {target}")
    finally:
        os.close(fd)
    return json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_reject_duplicate_keys)


def prepare(catalog, row, commit, checksum):
    if not re.fullmatch(r"[a-f0-9]{40}", commit):
        raise ValueError("Supply the real immutable 40-character release commit.")
    if not re.fullmatch(r"[a-f0-9]{64}", checksum):
        raise ValueError("Supply the SHA-256 of that commit's downloaded codeload ZIP.")
    result = copy.deepcopy(catalog)
    if "legends-cloudflare" in result["modules"]:
        raise ValueError("Module already exists; review an update instead of initial admission.")
    alias = result.setdefault("aliases", {}).get("legends-cloudflare-kit")
    if alias and alias != "legends-cloudflare":
        raise ValueError("Legacy alias already belongs to another module.")
    if "legends-cloudflare-kit" in result["modules"]:
        raise ValueError("Legacy module exists; review its migration explicitly.")
    parts = result["version"].split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise ValueError("Expected a three-part numeric catalog version.")
    result["version"] = ".".join([parts[0], parts[1], str(int(parts[2]) + 1)])
    result["modules"]["legends-cloudflare"] = {**row, "commit": commit, "sha256": checksum}
    result["aliases"]["legends-cloudflare-kit"] = "legends-cloudflare"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        catalog = read_bounded_json(args.catalog)
        row = read_bounded_json(root / "docs" / "catalog-entry.candidate.json")
        candidate = prepare(catalog, row, args.commit, args.sha256)
        check_no_symlink_chain(args.output)
        with args.output.open("x", encoding="utf-8") as handle:
            json.dump(candidate, handle, indent=2)
            handle.write("\n")
    except (ValueError, OSError, UnicodeDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps({"status": "candidate_only", "output": str(args.output),
                      "catalog_version": candidate["version"],
                      "next": "Validate and test against the real public archive before publishing."}))


if __name__ == "__main__":
    main()
