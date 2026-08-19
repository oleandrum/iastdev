# -*- coding: utf-8 -*-
"""
A minimal, from-scratch simulator of the rule semantics this map is DESIGNED
around (longest-match at each position, left/right single-class context
checks). This is NOT a TECkit compiler and won't catch every possible
compiler-level issue -- it validates that the rule TABLE itself is
internally consistent and produces the intended output for representative
words, using the same generator data (tools/gen.py) rather than re-parsing
the .map text.

IMPORTANT: passing this test suite is a necessary sanity check, not proof
that the compiled iastdev.map behaves identically under real TECkit. Always
also test with the actual compiled .tec table (teckit_compile) before
relying on a change in production. See docs/DESIGN.md.

Run from the repository root:   python3 tests/test_conversion.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
from gen import CONSONANTS, VOWELS, CANDRABINDU, ANUSVARA_ROMAN, VISARGA_ROMAN, \
    ANUSVARA_DEVA, VISARGA_DEVA, VIRAMA, ACCENTS, case_variants

# Build: rcons set of strings, rvow set of strings
rcons = set()
for roman, _ in CONSONANTS:
    for v in case_variants(roman):
        rcons.add(v)

rvow = set()
for romans, _, _ in VOWELS:
    rvow.update(romans)
for romans, _, _ in CANDRABINDU:
    rvow.update(romans)
rvow.update(ANUSVARA_ROMAN)
rvow.update(VISARGA_ROMAN)

# Rule table: list of (lhs_str, left_ctx or None, right_ctx or None, output_str)
# left_ctx/right_ctx: ('in', set) or ('notin', set)
rules = []

for roman, deva in CONSONANTS:
    for v in case_variants(roman):
        rules.append((v, None, ('in', rvow), deva))          # bare
        rules.append((v, None, None, deva + VIRAMA))          # fallback

for romans, initial, medial in VOWELS:
    for r in romans:
        rules.append((r, ('notin', rcons), None, initial))
        rules.append((r, ('in', rcons), None, (medial or "")))

for romans, initial, medial in CANDRABINDU:
    for r in romans:
        rules.append((r, ('notin', rcons), None, initial))
        rules.append((r, ('in', rcons), None, medial))

INDEP_A = "\u0905"
for a in ("a", "A"):
    for m in ANUSVARA_ROMAN:
        rules.append((a + m, ('in', rvow), None, INDEP_A + ANUSVARA_DEVA))
    for h in VISARGA_ROMAN:
        rules.append((a + h, ('in', rvow), None, INDEP_A + VISARGA_DEVA))
    for m in ANUSVARA_ROMAN:
        rules.append((a + m, ('in', rcons), None, ANUSVARA_DEVA))
    for h in VISARGA_ROMAN:
        rules.append((a + h, ('in', rcons), None, VISARGA_DEVA))
for m in ANUSVARA_ROMAN:
    rules.append((m, None, None, ANUSVARA_DEVA))
for h in VISARGA_ROMAN:
    rules.append((h, None, None, VISARGA_DEVA))

# Vedic pitch accents: combining mark right after any recognised vowel
# spelling (mirrors [rVow] as left context in iastdev.map -- see CLAUDE.md
# principle #3 and the accent section of tools/build_map.py).
for roman, deva in ACCENTS:
    rules.append((roman, ('in', rvow), None, deva))

# sort candidate rules by LHS length descending so we try longest first
rules.sort(key=lambda r: -len(r[0]))


def convert(word):
    out = []
    i = 0
    n = len(word)
    while i < n:
        matched = False
        for lhs, lctx, rctx, output in rules:
            L = len(lhs)
            if word[i:i+L] != lhs:
                continue
            # left context: previous single input character
            if lctx is not None:
                kind, s = lctx
                prev = word[i-1] if i > 0 else ""
                is_in = prev in s
                if kind == 'in' and not is_in:
                    continue
                if kind == 'notin' and is_in:
                    continue
            # right context: next single input character (after this match)
            if rctx is not None:
                kind, s = rctx
                nxt = word[i+L] if i+L < n else ""
                is_in = nxt in s
                if kind == 'in' and not is_in:
                    continue
                if kind == 'notin' and is_in:
                    continue
            out.append(output)
            i += L
            matched = True
            break
        if not matched:
            out.append(word[i])  # passthrough, unmatched
            i += 1
    return "".join(out)


TESTS = [
    ("rāma", "राम"),
    ("kṛṣṇa", "कृष्ण"),
    ("namaḥ", "नमः"),
    ("śivaṃ", "शिवं"),
    ("devāṃ", "देवां"),
    ("oṃ", "ओं"),          # must NOT become ॐ
    ("auṃ", "औं"),
    ("\u0950", "\u0950"),     # literal Om passes through unchanged
    ("KṚṢṆA", "कृष्ण"),      # ALL CAPS
    ("Kṛṣṇa", "कृष्ण"),      # Title case
    ("gūḍha", "गूढ"),
    ("maṭha", "मठ"),
    ("kutra", "कुत्र"),
    ("iṣṭa", "इष्ट"),
    ("viṣa", "विष"),
    ("dharma", "धर्म"),
    ("saṃskṛta", "संस्कृत"),
    ("aiśvarya", "ऐश्वर्य"),
    # Vedic pitch accents (Rigveda): these check the accent-conversion
    # MECHANISM only -- svarita/double svarita/triple svarita/anudatta each
    # landing on the right output syllable, including after the medial-'a'
    # deletion and after a matra. They are NOT a claim about the actual
    # accentuation of these words in any published Rigveda edition (none of
    # these are even Rigvedic words -- 'rāma' is Classical/epic). A real,
    # attested accented Rigveda verse (e.g. RV 1.1.1) would be a better test
    # per CLAUDE.md's "prefer real attested words" guidance, but hasn't been
    # added here for lack of a verified source at the time of writing -- see
    # CHANGELOG.md.
    ("ka̍", "क॑"),          # ka + svarita (bare consonant's inherent a)
    ("ka̎", "क᳚"),          # ka + double svarita
    ("ka᳛", "क᳛"),          # ka + triple svarita
    ("ka̱", "क॒"),          # ka + anudatta
    ("rā̍ma", "रा॑म"), # svarita after a matra, mid-word
]

ok = True
for src, expected in TESTS:
    got = convert(src)
    status = "OK " if got == expected else "FAIL"
    if got != expected:
        ok = False
    print(f"{status}  {src!r:20} -> {got!r:20} (expected {expected!r})")

print()
if ok:
    print("ALL PASS")
else:
    print("SOME FAILED")
    sys.exit(1)
