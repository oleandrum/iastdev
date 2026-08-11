# Contributing

Issues and pull requests are welcome — this project is young and real-world Sanskrit text (both
Classical/Purāṇic and, eventually, Vedic) will surface cases the current design hasn't hit yet.

## Before you file an issue

If you hit a conversion that looks wrong, please include:

- The exact IAST input (copy/paste, not retyped — subtle Unicode differences, e.g. precomposed vs.
  combining diacritics, matter a lot here).
- The Devanagari output you got.
- The Devanagari output you expected, and why (a source/reference is very helpful).
- Whether you tested with a real compiled `.tec` table (`teckit_compile iastdev.map`) or with
  `tests/test_conversion.py`'s simulator — these can, in principle, disagree, and that gap is
  itself useful information (see README.md Status section).

## Before you propose a change

Read [docs/DESIGN.md](docs/DESIGN.md) first, especially if your change touches:

- Anything that might make the map infer meaning from a bare letter sequence (see the Om
  discussion) — this kind of change will very likely be declined in favour of an explicit,
  unambiguous input signal instead.
- Case handling — see the "realistic case patterns" note in `docs/DESIGN.md`.
- The vowel/inherent-a mechanism — see "Single-pass architecture" in `docs/DESIGN.md`.

## Making a change

1. **Edit `tools/gen.py`**, not `iastdev.map` directly. The map is generated; hand edits will be
   overwritten and won't get case-symmetry coverage for free.
2. Regenerate and test:
   ```bash
   python3 tools/build_map.py
   python3 tests/test_conversion.py
   ```
3. Add a test word to `tests/test_conversion.py` covering your change — a real, attested Sanskrit
   word is much more useful than a synthetic string.
4. If you can, also compile with real TECkit (`teckit_compile iastdev.map`) and confirm the
   `.tec` output matches. This project doesn't yet have that confirmation for the current rule
   set (see README.md) — closing that gap for any part of the map is a very welcome contribution
   on its own, even without a specific bug to report.
5. Update `CHANGELOG.md` (Keep a Changelog format) and, if the change is a new design decision
   rather than a routine addition, `docs/DESIGN.md`.
6. Open a pull request describing the real-world text/use case that prompted the change.

## Style

- All documentation and code comments in English (this repo is public).
- Keep `tools/gen.py`'s data-table style: plain data (tuples/lists), not TECkit syntax — leave the
  TECkit rule generation to `tools/build_map.py`'s helper functions.
