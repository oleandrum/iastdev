# Changelog

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). This project doesn't
have version tags yet — entries are dated instead until a first tagged release.

## [Unreleased]

### Added
- Placeholder section in `iastdev.map` and notes in `docs/DESIGN.md` for future Vedic pitch-accent
  (udātta/anudātta/svarita) rules, pending a decided source-text notation convention.

## 2026-08-11 — First real `teckit_compile` verification

`tests/test_conversion.py`'s Python simulator had been passing since the rewrite, but the map had
never actually been run through the real TECkit compiler. First compilation attempt surfaced two
real bugs the simulator couldn't catch, since it doesn't model TECkit's own source-syntax rules:

### Fixed
- `tools/gen.py`'s `lit()` helper didn't escape embedded single quotes by doubling them (TECkit's
  own escaping convention for quoted string literals), so `lit("'")` — used for one of the three
  accepted avagraha input spellings, the plain ASCII apostrophe — emitted `'''` (an empty quoted
  string followed by a stray, unterminated quote), which `teckit_compile` rejected outright
  ("no mapping operator found"). `lit()` now doubles embedded quotes generically.
- Even after that fix, `teckit_compile` still rejected the apostrophe-avagraha rule: a quoted
  TECkit string consisting *solely* of an escaped quote (`''''`) fails to compile, even though the
  same doubling escape works fine inside a longer literal (e.g. `'a''b'`). Worked around by
  emitting all three avagraha spellings as `U+XXXX` codepoint tokens instead of quoted literals,
  sidestepping the ambiguity entirely (`tools/build_map.py`).
- The medial (post-consonant) `a`/`A`/`ä`/`Ä` rules — which delete the inherent vowel with no
  Devanagari output — were written as bidirectional (`<>`) rules with an empty right-hand side.
  Because `<>` also defines the reverse (Devanagari → Roman) direction, an empty forward RHS
  implies a reverse rule with a null/zero-width match string, which `teckit_compile` rejects
  ("rule must have non-null match string or post-context"). Changed to the one-directional `>`
  operator for these four deletion rules only (`tools/build_map.py`). This is also the correct
  semantics, not just a workaround: there's no information left to reverse a deletion from, which
  is the same kind of one-way lossiness already documented for case in reverse conversion (see
  `docs/DESIGN.md`).

### Verified
- `iastdev.map` now compiles cleanly with `teckit_compile` (Debian/Ubuntu `teckit` package,
  TECkit 2.5.12).
- Ran the compiled `.tec` table through `txtconv` against the full `tests/test_conversion.py` word
  list plus the three avagraha spellings, danda/double-danda, and digits — output matches the
  simulator exactly, including the load-bearing case: `oṃ`/`auṃ` convert literally to `ओं`/`औं`,
  never to the ॐ ligature, and a literal `ॐ` in the source passes through untouched.
- Regenerated `iastdev.map` from `tools/gen.py`/`tools/build_map.py` after both fixes; simulator
  suite (`tests/test_conversion.py`) still passes in full.

## 2026-08-11 — Ground-up rewrite as `iastdev`

Full rewrite, generated from `tools/gen.py` instead of hand-maintained. Rewritten to fix, by
construction, everything found in the earlier hand-maintained map (see entries below), plus:

### Added
- Single-pass architecture: the old two-pass "strip stray -a" mechanism is gone. `a`/`A` are now
  handled by the same initial/medial rule template as every other vowel (see `docs/DESIGN.md`).
- Explicit, permanent design decision: Devanagari OM (U+0950) is never derived from `oṃ`/`auṃ` or
  any other Roman letter sequence — only produced if already present in the source text.
- Full case-symmetry generation (lower / Title / ALL-CAPS) for every consonant and vowel,
  including previously-missing ALL-CAPS digraph forms (e.g. `KH`, `ṬH`) that didn't exist even in
  the bug-fixed version of the old map.
- Medial (post-consonant) forms for Vedic short e/o (previously only initial-position existed).
- `ä`/`ï`/`ü` alternate legacy input spellings now work in medial position too, and participate
  correctly in the bare-consonant-vs-virāma decision (previously initial-position only).
- `tools/gen.py` / `tools/build_map.py` — the map is now generated from data tables instead of
  hand-written, specifically to prevent case-symmetry drift from recurring.
- `tests/test_conversion.py` — rule-table sanity check against a set of real Sanskrit words
  (still needs confirmation against a real TECkit compiler — see README.md Status section).
- Full documentation set: `README.md`, `docs/DESIGN.md`, `docs/USAGE.md`, `CLAUDE.md`,
  `CONTRIBUTING.md`.

### Changed
- Renamed from `RomDev.map` to `iastdev.map`.

## 2026-08-11 — Bug-fix pass on the original map (pre-rewrite)

Applied as a set of corrections to the original 2010 file, before the ground-up rewrite above
superseded it entirely. Kept here for history / traceability.

### Fixed
- Uppercase Ä (U+00C4) was mapped using the same codepoint as lowercase ä (U+00E4) a second time
  — a duplicate/typo — so uppercase Ä silently failed to convert. Corrected to the real U+00C4.
- `'U+1E6C h'` / `'U+1E6D h'` / `'U+1E0C h'` / `'U+1E0D h'` were written as single quoted literal
  9-character strings in two `UniClass` definitions (`[LTR]`, `[rCons]`), instead of two separate
  tokens (codepoint + quoted `'h'`) as used correctly elsewhere in the same file. As written, they
  could never match real input. Rewritten to the correct two-token form.
- Added missing uppercase medial vowel-sign (matra) rules — only lowercase had them for Ā, I, Ī,
  U, Ū, Ṛ, Ṝ, E, Ai, O, Au, Ḷ, Ḹ, Ṃ, Ḥ (plus the rare candrabindu forms Ĩ/Õ).
- Added missing uppercase word-final consonant+virāma rules — the entire "final cons" section had
  only lowercase Roman consonant spellings.
- Added missing uppercase Ṃ/Ḥ counterparts of the `a+ṃ`/`a+ḥ` sandhi compound rules.

### Noted, not changed
- `Define NUL U+007F` and the `[LTR]` UniClass were unused anywhere in the file — left in place
  but flagged, in case something external depended on them.
- Reverse-direction (Devanagari → Roman) case recovery is inherently lossy given the
  case-insensitive design — not a bug, a property of the scheme (see `docs/DESIGN.md`).

## 2010-03-23 — Original file

`RomDev.map` — the original hand-maintained TECkit mapping this project is descended from
("Updated March 23, 2010 9:53:03 PM EDT" per its header comment).
