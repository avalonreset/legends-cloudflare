"""Verify installed wheel resources outside the source checkout."""
import json
from pathlib import Path
import subprocess
import sys


def main():
    completed = subprocess.run([sys.executable, "-m", "legends_cloudflare", "resources"],
                               check=True, capture_output=True, text=True)
    report = json.loads(completed.stdout)
    assert report["ok"] is True, report
    assert report["complete"] is True, report
    assert report["source"] == "package_data", report
    assert Path(report["recipe"]).is_file(), report
    assert Path(report["pack_manifest"]).is_file(), report
    for path in report["pack_files"]:
        assert Path(path).is_file(), path
    print(json.dumps({"ok": True, "source": report["source"], "pack_files": len(report["pack_files"])}))


if __name__ == "__main__":
    main()
