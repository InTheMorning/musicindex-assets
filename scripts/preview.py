#!/usr/bin/env python3
"""Write the preview sheets that GitHub shows in the README.

Usage: preview.py

GitHub shows an SVG file at the size that the file states, and it draws
`currentColor` as black. A Lucide icon is 24 px and uses `currentColor`, so it
looks small, and it is almost invisible on the dark GitHub theme. The apps need
the files as they are. These sheets draw each asset larger, in a set color, on
its own background, so they look correct in both GitHub themes.

The sheets are in `previews/`. They are not assets, and the manifest does not
list them. Run this script after each change of an icon or a brand file.
"""
import html
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "previews")
TOKENS = json.load(open(os.path.join(ROOT, "tokens", "tokens.json"), encoding="utf-8"))
DARK = TOKENS["color"]["dark"]
FONT = "Figtree, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"


def inner(svg_text):
    """Return the content and the viewBox of an SVG file."""
    view = re.search(r'viewBox="([^"]+)"', svg_text).group(1)
    body = re.sub(r"^.*?<svg[^>]*>", "", svg_text, count=1, flags=re.S)
    body = re.sub(r"</svg>\s*$", "", body, flags=re.S)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    return body.strip(), view


def icon_sheet():
    names = sorted(f[:-4] for f in os.listdir(os.path.join(ROOT, "icons", "lucide")) if f.endswith(".svg"))
    custom = sorted(f[:-4] for f in os.listdir(os.path.join(ROOT, "icons", "custom")) if f.endswith(".svg"))
    cols, cell, size, pad = 8, 120, 48, 24
    items = [("lucide", n) for n in names] + [("custom", n) for n in custom]
    rows = (len(items) + cols - 1) // cols
    width, height = cols * cell + 2 * pad, rows * cell + 2 * pad + 40
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" rx="16" fill="{DARK["sidebar"]}"/>',
        f'<text x="{pad}" y="{pad + 14}" font-family="{FONT}" font-size="16" font-weight="700" fill="{DARK["text"]}">'
        f'Icons: Lucide 1.43.0 ({len(names)}) and custom ({len(custom)})</text>',
    ]
    for i, (kind, name) in enumerate(items):
        x = pad + (i % cols) * cell
        y = pad + 40 + (i // cols) * cell
        body, view = inner(open(os.path.join(ROOT, "icons", kind, name + ".svg"), encoding="utf-8").read())
        parts.append(f'<rect x="{x + 6}" y="{y + 4}" width="{cell - 12}" height="{cell - 12}" rx="12" fill="{DARK["surface"]}"/>')
        style = (f'fill="none" stroke="{DARK["text"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
                 if kind == "lucide" else "")
        ix = x + (cell - size) / 2
        parts.append(f'<svg x="{ix}" y="{y + 18}" width="{size}" height="{size}" viewBox="{view}" {style}>{body}</svg>')
        label = html.escape(name if kind == "lucide" else name + " *")
        parts.append(f'<text x="{x + cell / 2}" y="{y + cell - 20}" text-anchor="middle" font-family="{FONT}" '
                     f'font-size="12" fill="{DARK["text-muted"]}">{label}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def brand_sheet():
    mark_body, mark_view = inner(open(os.path.join(ROOT, "brand", "musicindex-mark-shape.svg"), encoding="utf-8").read())
    lock_body, lock_view = inner(open(os.path.join(ROOT, "brand", "musicindex-lockup-horizontal.svg"), encoding="utf-8").read())
    width, height = 960, 300
    half = width / 2
    ent = TOKENS["entity"]["dark"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{half}" height="{height}" rx="16" fill="{DARK["background"]}"/>',
        f'<rect x="{half}" width="{half}" height="{height}" rx="16" fill="#ffffff"/>',
        f'<svg x="40" y="40" width="{half - 80}" height="90" viewBox="{lock_view}">{lock_body}</svg>',
        f'<svg x="{half + 40}" y="40" width="{half - 80}" height="90" viewBox="{lock_view}" style="filter:brightness(0)">{lock_body}</svg>',
    ]
    for i, (key, label) in enumerate([("feed", "Album"), ("track", "Track"), ("playlist", "Playlist"), ("artist", "Artist"), ("label", "Label")]):
        x = 40 + i * 84
        parts.append(f'<svg x="{x}" y="170" width="64" height="64" viewBox="{mark_view}" fill="{ent[key]}" fill-opacity="0.45">{mark_body}</svg>')
        parts.append(f'<text x="{x + 32}" y="262" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{DARK["text-muted"]}">{label}</text>')
    parts.append(f'<text x="{half + 40}" y="200" font-family="{FONT}" font-size="14" fill="#1d1d1f">The lockup on light, and the mark shape as the</text>')
    parts.append(f'<text x="{half + 40}" y="222" font-family="{FONT}" font-size="14" fill="#1d1d1f">placeholder of missing art (ADR 0021 R-ART-2).</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, text in (("icons.svg", icon_sheet()), ("brand.svg", brand_sheet())):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"previews/{name}")


if __name__ == "__main__":
    main()
