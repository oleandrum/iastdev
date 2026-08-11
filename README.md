# iastdev

A modern [TECkit](https://scripts.sil.org/cms/scripts/page.php?site_id=nrsi&id=teckit) mapping
for converting Unicode **IAST** (International Alphabet of Sanskrit Transliteration) to Unicode
**Devanagari**, built for classical / Purāṇic Sanskrit text and designed to be extended toward
Vedic material (Ṛgveda first, possibly Yajurveda later).

Primary direction: **IAST → Devanagari**. The map is written bidirectionally (`<>`) so a reverse
pass is technically possible, but see [docs/DESIGN.md](docs/DESIGN.md#case-and-reversibility)
for an important caveat about case being non-recoverable in reverse.

## Why this exists

Most "blind" Roman→Devanagari converters get the common cases right and then quietly get a
handful of specific, damaging cases wrong — because they infer meaning from bare letter patterns
instead of respecting explicit signals. Two examples this project treats as first-class design
constraints rather than edge cases to patch over:

- A sequence like `oṃ` (o + anusvāra) must **always** convert literally to `ओं`, never to the
  sacred ligature `ॐ` (U+0950) — even though `ॐ` is *also* conventionally pronounced "oṃ". The
  ligature is only ever produced if it's already present in the source text.
- A consonant cluster like `ktra` needs no special "which conjunct did you mean" logic at the
  mapping level — in Unicode there is only one encoding for it (KA + VIRAMA + TA + VIRAMA + RA);
  which ligature/half-form glyph gets drawn is entirely a font-shaping (OpenType) question, not a
  mapping question.

See [docs/DESIGN.md](docs/DESIGN.md) for the full rationale and every other design decision.

## Repository layout

```
iastdev.map        the TECkit mapping itself (generated — do not hand-edit)
tools/gen.py        data tables: consonants, vowels, case variants, codepoints
tools/build_map.py   generates iastdev.map from tools/gen.py
tests/test_conversion.py   rule-table sanity check (NOT a substitute for real TECkit testing)
docs/DESIGN.md       design rationale, the Om problem, conjuncts, case symmetry, extension points
docs/USAGE.md         usage guide with worked examples for specific/tricky mappings
CLAUDE.md              project context for AI coding assistants working in this repo
CHANGELOG.md            version history
```

## Status

✅ **Validated against a real TECkit compiler.** `iastdev.map` compiles cleanly with
`teckit_compile` (tested with the Debian/Ubuntu `teckit` package, TECkit 2.5.12), and the
compiled `.tec` table was run through `txtconv` against the full `tests/test_conversion.py` word
list plus avagraha, danda, and digit rules — output matches the Python simulator exactly,
including the load-bearing case: `oṃ`/`auṃ` always convert literally to `ओं`/`औं`, never to the ॐ
ligature. This first compilation attempt did catch two real bugs the simulator couldn't see
(TECkit source-syntax quoting and bidirectional-rule constraints, not rule-table logic) — see
[CHANGELOG.md](CHANGELOG.md) for details; both are fixed in `tools/gen.py`/`tools/build_map.py`.

The rule logic is also checked with a from-scratch Python simulator (`tests/test_conversion.py`)
that implements the same longest-match / context semantics the map is designed around, and all
current test words pass. That remains a useful fast sanity check on the rule *table* during
development, even though real-compiler verification is now the stronger signal. Contributions
adding more real-compiler test coverage are still very welcome — see
[CONTRIBUTING.md](CONTRIBUTING.md).

Vedic pitch accents (udātta / anudātta / svarita) are **not implemented yet** — there's a
placeholder section at the bottom of `iastdev.map` and notes in `docs/DESIGN.md` on what's needed
to add them once a specific source-text accent convention is settled on.

## Quick start

1. Grab `iastdev.map` and compile it with TECkit (`teckit_compile iastdev.map`) to get a `.tec`
   table, or load the `.map` source directly in tools that support TECkit source mappings
   (e.g. some SIL / Keyman / LibreOffice workflows).
2. See [docs/USAGE.md](docs/USAGE.md) for worked examples of the trickier mappings (retroflex
   digraphs, anusvāra/visarga sandhi, candrabindu, case-insensitivity, punctuation, digits).

## Regenerating the map from source

The map is generated, not hand-written, so that upper/lower-case coverage and consonant/vowel
tables stay internally consistent as the project grows (see `docs/DESIGN.md` for why the earlier
hand-maintained version drifted out of sync).

```bash
python3 tools/build_map.py      # regenerates iastdev.map from tools/gen.py
python3 tests/test_conversion.py    # sanity-checks the rule table
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). In short: edit `tools/gen.py`, not `iastdev.map` directly;
regenerate; run the tests; describe what real-world text prompted the change.

## License

MIT — see [LICENSE](LICENSE).
