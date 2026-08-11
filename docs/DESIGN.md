# Design notes

This document records *why* the map is built the way it is, so future changes (by a human or an
AI assistant) don't accidentally re-introduce problems that were already solved on purpose.

## Background

`iastdev` grew out of an older, hand-maintained TECkit map from the early Unicode era (~2010).
That file had accumulated several real bugs by the time it was reviewed:

- A duplicated codepoint bug (uppercase Ä was mapped to the same rule as lowercase ä, so
  uppercase Ä silently failed to convert).
- A quoting bug in two `UniClass` definitions where a retroflex-aspirate sequence (`ṭh`/`ḍh`) was
  written as a single quoted literal string instead of two separate tokens, so it could never
  actually match real input.
- Systematic upper/lower-case asymmetry: medial vowel signs and word-final consonants only had
  rules for the lowercase Roman spelling, so a capitalised word (a Title-Case proper noun, or an
  ALL-CAPS heading) would partially fail to convert.
- A two-pass "strip the stray -a" mechanism for handling the inherent vowel, whose correctness
  under real TECkit compilation could not be confirmed (a virama sits between the bare consonant
  and the literal "a" in the first pass's output, and the second pass's strip rule requires them
  to be directly adjacent).

`iastdev` is a ground-up rewrite that fixes all of the above by construction rather than by patch,
and is **generated from a small Python data table** (`tools/gen.py`) instead of hand-written, so
that case-symmetry and completeness can't silently drift again as the sound inventory grows
(e.g. for Vedic material).

## The core problem: "blind" transliteration

A TECkit map (like any purely pattern-based Roman→Devanagari converter) only ever sees a short
window of surrounding characters. It has no concept of word meaning, sacred status, morphology,
or editorial intent. Two concrete failure modes follow directly from that, and both are treated
here as hard design constraints, not edge cases to special-case around later:

### The Om problem

`oṃ` (o + anusvāra) is a perfectly ordinary, frequent Sanskrit syllable that must convert to
`ओं` — an *ordinary* Devanagari O plus anusvāra sign. It happens to also be how the sacred
syllable **ॐ** (Devanagari OM, U+0950) is conventionally pronounced and often transliterated. A
"clever" converter that tries to detect "this must be the sacred Om" from the bare letter sequence
will inevitably also fire on ordinary words/word-final syllables that happen to share the same
spelling — silently corrupting text that was never meant to invoke the special symbol.

**Rule enforced in this map: no rule anywhere derives U+0950 from any Roman letter sequence.**
`oṃ` and `auṃ` always convert literally (`ओं`, `औं`). If the ligature ॐ is wanted, it is typed
directly as Devanagari in the source text — since it's already Devanagari, it simply isn't touched
by any Roman-input rule and passes through unchanged. This was an explicit, confirmed decision
(see project history / issue tracker for the discussion) — **do not "improve" this by adding
heuristic Om detection.**

### The conjunct problem ("ktra")

At the Unicode level there is only one way to encode a consonant cluster: each consonant in
sequence, joined by U+094D VIRAMA, e.g. `क् त् र` (KA+VIRAMA, TA+VIRAMA, RA) for "ktra". There is
no separate codepoint for "the ready-made *tra* conjunct" versus "k, then, separately, tra" —
that distinction doesn't exist in the text encoding at all, only in how a font's shaping engine
*chooses to render* a given virama-joined sequence (traditional ligature vs. stacked half-forms
vs. explicit visible virama, depending on the font's OpenType `blwf`/`pref`/`half`/`akhn` feature
tables and the shaping engine, typically HarfBuzz).

**Consequence for this map:** no special conjunct-detection logic is needed or attempted. The one
real requirement on the *source text* side is that word boundaries are marked with actual spaces,
so that a cluster is never accidentally merged across an unmarked word boundary (e.g. "...kt" at
the end of one word immediately followed by "ra..." at the start of the next, with no space,
would be indistinguishable from a single word's "ktra"). This is a source-text discipline issue,
not something the mapping can or should try to resolve.

## Single-pass architecture

The old map needed two TECkit passes because it emitted a virama for *every* consonant not
immediately followed by a "special" vowel class, then tried to strip the redundant virama+`a`
sequence afterward for the common case of the plain inherent vowel.

`iastdev` avoids this entirely with one unified vowel class, `[rVow]`, that includes **every**
romanised vowel spelling — including `a`/`A` — plus candrabindu forms and anusvāra/visarga
(defensively, in case either directly follows a bare consonant with no vowel in between).

- A consonant becomes **bare** (no virama) whenever *any* member of `[rVow]` follows.
- A consonant otherwise falls back to **consonant + virama**.
- Each vowel — including `a`/`A` — then has exactly two rules of its own:
  - **initial** position (not preceded by a Roman consonant: word start, or after another vowel)
    → the independent Devanagari vowel letter (e.g. अ, इ, उ …)
  - **medial** position (preceded by a Roman consonant) → the matra sign — **except for `a`/`A`**,
    whose medial rule is simply *delete*, since the bare consonant already carries the inherent
    vowel by default.

This means `a`/`A` are handled by the exact same two-rule template as every other vowel, instead
of a special-cased mechanism spanning two passes. It also means the "aa" hiatus case (two `a`s in
a row, e.g. word-initial or across a vowel boundary) falls out of the existing initial-position
rule for free: the second `a` is not preceded by a Roman consonant (the character before it is
`a`, a vowel, not a member of `[rCons]`), so it independently qualifies for the initial-position
rule too — producing अअ, with no dedicated extra rule required.

## Case symmetry

Case carries no phonemic meaning in this scheme (`k`/`K` are the same sound; vowel length is
carried only by macrons/diacritics, e.g. `ā` vs `a`, never by capitalisation). Every consonant and
vowel rule is generated in all *realistic* case patterns:

- single letters: lowercase and UPPERCASE (`k`/`K`)
- digraphs (aspirates, and the diacritic-letter digraphs `ṭh`/`ḍh`): lowercase, Title-case (first
  letter capitalised — the common case for a capitalised proper noun starting with an aspirate),
  and ALL-CAPS (both letters capitalised — the common case for a heading)

Mixed patterns that don't occur in real text (e.g. a lowercase retroflex letter followed by an
uppercase `H`) are deliberately **not** generated — case changes at letter or whole-word
granularity, never in the middle of a single digraph without the first letter also changing.

This symmetry is enforced by generating every rule from `tools/gen.py`'s `case_variants()` helper
rather than being hand-typed, which is what let the old map's asymmetry happen in the first place.
**If you add a new consonant or vowel, add it to the data tables in `tools/gen.py`, not directly
to `iastdev.map`** — the generator will produce full case coverage automatically.

## Case and reversibility

Because case collapses to a single phonemic value on the way in, a **reverse** pass
(Devanagari → Roman) can only ever recover *one* case for a given Devanagari letter — whichever
case variant the compiler resolves the ambiguous reverse mapping to. This is an inherent property
of a case-insensitive scheme, not a bug to be fixed. If a future need arises for round-trip-safe
case preservation, it would require a fundamentally different design (e.g. an out-of-band case
marker), which is out of scope for this project's stated primary use (IAST → Devanagari).

## Extension points

### Vedic short e / o

Already implemented. Vedic short e/o (distinct from the always-long e/o of Classical Sanskrit) are
written with a breve diacritic (`ĕ`/`Ĕ`, `ŏ`/`Ŏ`) and map to the dedicated Unicode Devanagari
codepoints for short e/o, both independent-letter and matra forms
(U+090D/U+0946 and U+0911/U+094A respectively).

### Vedic pitch accents (udātta / anudātta / svarita) — not yet implemented

There's a placeholder comment block at the end of `iastdev.map` listing the likely target
codepoints (U+0951, U+0952, and the Vedic Extensions block U+A8E0–U+A8FF). Before writing actual
rules, we need to settle on:

1. **The Roman-side accent notation** used in the source texts this project will actually
   process (conventions vary significantly between editions/digitisation projects — e.g. an
   acute accent for udātta, a grave or underline for anudātta, a vertical line above for svarita,
   or no explicit udātta marking at all since it's the default/unmarked tone in many editions).
2. **The target codepoint set**, which depends on what the destination font actually supports —
   the base Devanagari block's stress-sign codepoints (U+0951/U+0952) are more widely supported
   than the fuller Vedic Extensions block, but the latter is more precise for Ṛgveda/Yajurveda
   work if the target font implements it.

Open an issue (or update this section directly) once these are decided, and add the rules to
`tools/gen.py` following the same case-symmetry / no-blind-guessing principles as everything else
in this file.
