"""Write a reviewable catalog candidate after real release pins are available."""
import argparse
import copy
import json
from pathlib import Path
import re


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
    catalog = json.loads(args.catalog.read_text(encoding="utf-8-sig"))
    row = json.loads((root / "docs/catalog-entry.candidate.json").read_text(encoding="utf-8-sig"))
    try:
        candidate = prepare(catalog, row, args.commit, args.sha256)
        with args.output.open("x", encoding="utf-8") as handle:
            json.dump(candidate, handle, indent=2)
            handle.write("\n")
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps({"status": "candidate_only", "output": str(args.output),
                      "catalog_version": candidate["version"],
                      "next": "Validate and test against the real public archive before publishing."}))


if __name__ == "__main__":
    main()
