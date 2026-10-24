# musicindex-assets

## What This Repository Is

This repository holds the shared assets of musicindex.org, musicindex-studio
and v4vmm. The assets are the brand files, the Figtree font, the Lucide icons
that the apps use, two custom icons, and the design tokens. It has no app
code.

The musicindex repository owns each rule about these assets. Its ADR 0022
makes this repository the one place for the assets. ADR 0020 and ADR 0021
give the rules for the tokens, the shapes and the art. This repository states
no rule of its own.

## Where The Work Stands

- Created on 2026-10-24 from the copies in `../musicindex/assets`,
  `../musicindex-studio/crates/api/ui/assets` and `../v4vmm/src/assets`. The
  copies in the apps were identical to these files on that day.
- v4vmm also holds `src/assets/music_network_logo_vectorized.svg`. It has the
  bytes of `brand/musicindex-lockup-primary.svg` and another name, so
  `scripts/check.py compare` does not find it.
- The apps do not take their files from here yet. Each app changes when the
  operator starts that work in the app.
- On 2026-10-24, 43 Lucide icons were added for the mockups of the research
  repository. The mockups show the screens of the journeys, for example
  settings, folders, upload, the inbox and the trash. The apps do not use
  them yet. They come from the package `lucide-static` 1.43.0 of the npm
  registry. As for the first 39 icons, the license comment and the class
  attribute are removed.
- No Lucide icon is changed yet. `icons/CHANGES.md` does not exist until the
  first change.

## Working Rules

These rules are advisory. musicindex ADR 0022 owns them.

- Run `python3 scripts/check.py write` in the same commit as each change of a
  file. Then run `python3 scripts/check.py verify`.
- Run `python3 scripts/preview.py` in the same commit as each change of an
  icon or a brand file.
- Keep `icons/lucide/LICENSE-LUCIDE` with the Lucide icons. Record each
  changed Lucide icon in `icons/CHANGES.md`.
- Do not add a file under `brand/` without the permission of the operator.
- Each file is all rights reserved (`LICENSE`), except Figtree (OFL) and the
  Lucide icons (ISC and MIT). Do not put a file with an open license in
  another folder.
- Write prose in ASD-STE100 Simplified Technical English.
