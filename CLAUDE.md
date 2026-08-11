# CLAUDE.md

Context for Claude (or any AI assistant) working in this repository. Read this before making
changes — several design decisions here are intentional and should not be "fixed" without
understanding why first. Full rationale: [docs/DESIGN.md](docs/DESIGN.md).

## What this project is

`iastdev.map` is a TECkit mapping that converts Unicode IAST → Unicode Devanagari, for classical/
Purāṇic Sanskrit, with room to grow toward Vedic (Ṛgveda, possibly Yajurveda) material. Primary
direction is IAST → Devanagari; the map is written bidirectionally but reverse conversion cannot
recover original letter case (see docs/DESIGN.md).

## The one thing to never do

**Never add a rule that infers a special/sacred symbol from an ordinary letter sequence.** The
canonical example: `oṃ`/`auṃ` must always convert literally (`ओं`/`औं`), never to the ॐ ligature
(U+0950) — even though ॐ is conventionally pronounced the same way. If literal ॐ is wanted, the
user types it directly as Devanagari and it passes through untouched (default TECkit behaviour for
unmatched input — no rule is needed or wanted for this). This was a deliberate, explicit decision.
If you're tempted to add heuristic detection for this or any similar case, stop and raise it as an
issue instead of implementing it.

## How the map is built

`iastdev.map` is a **generated file** — do not hand-edit it directly; edits will be lost on the
next regeneration and, more importantly, hand-editing is exactly how the previous version of this
project (a 2010-era hand-maintained map) accumulated case-symmetry bugs and a broken quoting bug
that went unnoticed for years.

- `tools/gen.py` — data tables (consonants, vowels, codepoints) and the `case_variants()` /
  `seq()` / `cp()` helpers that turn a bare IAST spelling into full lower/Title/ALL-CAPS coverage.
- `tools/build_map.py` — imports `gen.py` and emits `iastdev.map`.
- To add a sound (e.g. a Vedic accent-bearing vowel, or an additional consonant), add it to the
  data tables in `gen.py`, then run:
  ```bash
  python3 tools/build_map.py
  python3 tests/test_conversion.py
  ```
  Do not write the corresponding TECkit rules by hand in `iastdev.map`.

## Testing

`tests/test_conversion.py` is a from-scratch Python simulator of the map's intended rule
semantics (longest match, left/right context checks) — **not** a real TECkit compiler. It's a
useful fast sanity check on the rule *table* (case coverage, no accidental rule collisions,
correct handling of the worked examples in `docs/USAGE.md`), but a passing test suite is not
proof of correct behaviour under real TECkit compilation, since the simulator doesn't model
TECkit's own source-syntax rules (quoting/escaping, bidirectional-rule constraints, etc.) —
exactly the kind of thing that has bitten this map before (see CHANGELOG.md's "First real
`teckit_compile` verification" entry: a quoting bug and a bidirectional-deletion-rule bug that
`test_conversion.py` couldn't have caught, since both are about TECkit's own grammar, not the
map's semantics). `iastdev.map` has since been confirmed to compile and run correctly with a real
`teckit_compile` / `txtconv` (see the Status section in README.md), but that confirmation only
covers the rules and inputs actually exercised — whenever you add a new rule to `gen.py`, prefer
re-verifying with `teckit_compile iastdev.map` and a real conversion test over trusting the
simulator alone.

When adding a new test word to `tests/test_conversion.py`, prefer a real, attested Sanskrit word
over a synthetic one — it's much more likely to surface a genuine edge case.

## Design principles to preserve

1. **No blind pattern-guessing of meaning.** If a conversion decision depends on something the
   mapping can't actually know from local letter context (word boundaries, editorial intent,
   sacred/ordinary status), don't guess — require an explicit, unambiguous signal in the source
   text instead (see the Om example above).
2. **Full case symmetry**, generated, not hand-typed. See docs/DESIGN.md § Case symmetry for
   exactly which case patterns are realistic (lower / Title / ALL-CAPS) and which are deliberately
   excluded (mixed-case within a single digraph).
3. **Single-pass architecture.** The `[rVow]` class (in `gen.py`, mirrored as a `UniClass` in the
   generated map) includes `a`/`A` alongside every other vowel, specifically so the
   bare-consonant-vs-virāma decision and the vowel-attachment decision are both driven by one
   uniform mechanism. Don't reintroduce a second pass or a separate "strip stray -a" step.
4. **Conjuncts are a font-shaping concern, not a mapping concern.** Don't add cluster-detection
   logic to the map; if a real-world rendering problem shows up, it almost always belongs in a
   font/shaping bug report, not here. See docs/DESIGN.md § The conjunct problem.

## Repository conventions

- English for all documentation and code comments (this repo is public).
- Keep `CHANGELOG.md` updated (Keep a Changelog format) for anything that changes generated
  output, even a single new rule.
- New design decisions of the same weight as the Om/conjunct ones belong in `docs/DESIGN.md`, not
  just in a commit message or issue thread — the goal is that a future contributor (human or AI)
  never has to rediscover *why* by trial and error.
