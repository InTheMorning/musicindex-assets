#!/usr/bin/env python3
"""Check the asset manifest, or compare the copies of an app with it.

Usage:
  check.py write              Write manifest.json from the files of this repository.
  check.py verify             Exit with 1 when a file differs from manifest.json.
  check.py compare DIR...     For each file in DIR that has the name of an asset,
                              exit with 1 when its bytes differ from the asset.

An app keeps copies of the assets. Run `compare` on the folder of the copies,
for example `check.py compare ../musicindex-studio/crates/api/ui/assets`.
"""
import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MANIFEST = os.path.join(ROOT, "manifest.json")
FOLDERS = ("brand", "fonts", "icons", "tokens")
LICENSES = {
    "brand": "All rights reserved (LICENSE)",
    "fonts": "SIL Open Font License 1.1 (fonts/figtree/OFL.txt)",
    "icons/lucide": "ISC, with MIT for the Feather-derived icons (icons/lucide/LICENSE-LUCIDE)",
    "icons/custom": "All rights reserved (LICENSE)",
    "tokens": "All rights reserved (LICENSE)",
}


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def license_of(rel):
    for prefix in sorted(LICENSES, key=len, reverse=True):
        if rel.startswith(prefix + "/"):
            return LICENSES[prefix]
    return "unknown"


def scan():
    files = {}
    for folder in FOLDERS:
        for base, _, names in os.walk(os.path.join(ROOT, folder)):
            for name in sorted(names):
                path = os.path.join(base, name)
                rel = os.path.relpath(path, ROOT)
                files[rel] = {"sha256": sha256(path), "bytes": os.path.getsize(path), "license": license_of(rel)}
    return dict(sorted(files.items()))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    cmd = sys.argv[1]
    if cmd == "write":
        with open(MANIFEST, "w", encoding="utf-8") as f:
            json.dump({"files": scan()}, f, indent=2)
            f.write("\n")
        print(f"manifest.json: {len(scan())} files")
        return
    manifest = json.load(open(MANIFEST, encoding="utf-8"))["files"]
    if cmd == "verify":
        now = scan()
        bad = sorted(set(now) ^ set(manifest)) + [k for k in now if k in manifest and now[k]["sha256"] != manifest[k]["sha256"]]
        for k in bad:
            print(f"differs: {k}")
        if bad:
            print("Run `scripts/check.py write` in the same commit as the change of the asset.")
            sys.exit(1)
        print(f"{len(now)} files agree with manifest.json")
        return
    if cmd == "compare":
        by_name = {}
        for rel, info in manifest.items():
            by_name.setdefault(os.path.basename(rel), []).append((rel, info["sha256"]))
        bad = 0
        for folder in sys.argv[2:]:
            for base, _, names in os.walk(folder):
                for name in sorted(names):
                    if name not in by_name:
                        continue
                    path = os.path.join(base, name)
                    digest = sha256(path)
                    matches = [rel for rel, h in by_name[name] if h == digest]
                    if matches:
                        print(f"same: {path} = {matches[0]}")
                    else:
                        bad += 1
                        print(f"differs: {path} has the name of {by_name[name][0][0]}, but other bytes")
        if bad:
            print("Copy the asset from musicindex-assets, or change the asset through a musicindex decision record.")
            sys.exit(1)
        return
    print(__doc__)
    sys.exit(2)


if __name__ == "__main__":
    main()
