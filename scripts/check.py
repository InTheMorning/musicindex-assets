#!/usr/bin/env python3
"""Check the asset manifest, or compare the copies of an app with it.

Usage:
  check.py write              Write manifest.json from the files of this repository.
  check.py verify             Exit with 1 when a file differs from manifest.json.
  check.py compare DIR...     For each file in DIR that has the name of an asset,
                              exit with 1 when its bytes differ from the asset.
  check.py css FILE...        Exit with 1 when the CSS tokens of FILE differ from
                              tokens/tokens.json (musicindex ADR 0032 R-DOT-2 and
                              ADR 0029 R-SCALE-1), or when FILE has a free text size.

An app keeps copies of the assets. Run `compare` on the folder of the copies,
for example `check.py compare ../musicindex-studio/crates/api/ui/assets`.
"""
import hashlib
import json
import os
import re
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


def css_values(text, name):
    return {v.strip().lower() for v in re.findall(r"(?<![\w-])" + re.escape(name) + r"\s*:\s*([^;}]+)", text)}


# A text size that is not a free size: a text token, a size relative to the
# text around it, or a display title of musicindex ADR 0029 R-SCALE-2 item 2.
ALLOWED_SIZE = re.compile(r"^(var\(--text-[a-z0-9-]+\)|[0-9.]+em|inherit|clamp\(.*\))$")


def free_sizes(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    found = []
    for match in re.finditer(r"(?<![\w-])font-size\s*:\s*([^;}]+)", text):
        value = match.group(1).strip()
        if not ALLOWED_SIZE.match(value):
            found.append((text.count("\n", 0, match.start()) + 1, value))
    return found


def check_css(paths):
    tokens = json.load(open(os.path.join(ROOT, "tokens", "tokens.json"), encoding="utf-8"))
    dot = tokens["shape"]["type-dot"]
    want = {f"--c-{kind}": {tokens["entity"]["dark"][kind].lower(), tokens["entity"]["light"][kind].lower()}
            for kind in tokens["entity"]["dark"]}
    want["--dot-size"] = {f"{dot['size-px']}px"}
    want["--dot-ring"] = {f"{dot['hollow-ring-px']}px"}
    for style, (size, _, _) in tokens["type"]["web"].items():
        want[f"--text-{style}"] = {f"{size}px", f"{tokens['type']['touch'][style][0]}px"}
    bad = 0
    for path in paths:
        text = open(path, encoding="utf-8").read()
        before = bad
        for name, values in want.items():
            got = css_values(text, name)
            if got != values:
                bad += 1
                print(f"differs: {path} gives {name} as {sorted(got) or 'nothing'}, tokens.json gives {sorted(values)}")
        for line, value in free_sizes(text):
            bad += 1
            print(f"free size: {path}:{line} gives font-size: {value}")
        if bad == before:
            print(f"same: {path} has the entity colors, the type dot and the text styles of tokens.json")
    if bad:
        print("musicindex ADR 0032 R-DOT-2: an app keeps the entity colors and the type dot of tokens.json.")
        print("musicindex ADR 0029 R-SCALE-1: each text size is a text style. Use var(--text-<style>), with the")
        print("type.web size by default and the type.touch size in @media (pointer: coarse).")
        print("Change the CSS token to the tokens.json value, or change tokens.json through a musicindex decision record.")
        sys.exit(1)


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
    if cmd == "css":
        check_css(sys.argv[2:])
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
