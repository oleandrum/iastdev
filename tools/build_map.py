# -*- coding: utf-8 -*-
from gen import CONSONANTS, VOWELS, CANDRABINDU, ANUSVARA_ROMAN, VISARGA_ROMAN, \
    ANUSVARA_DEVA, VISARGA_DEVA, VIRAMA, case_variants, seq, cp, lit

lines = []

def add(s=""):
    lines.append(s)

# ---------------------------------------------------------------------------
HEADER = r"""; iastdev.map — TECkit mapping, IAST (Unicode) <-> Devanagari (Unicode)
; Part of the iastdev project: https://github.com/oleandrum/iastdev
;
; GENERATED FILE — do not hand-edit. Edit tools/gen.py / tools/build_map.py
; and regenerate with:   python3 tools/build_map.py
; (from the repository root). See CONTRIBUTING.md.
;
; Scope: classical / Puranic Sanskrit, with extension points for Vedic
; material (short e/o already included; accent marks: see bottom).
;
; DESIGN NOTES (read before editing — full rationale in docs/DESIGN.md):
;
;  * Single pass, no "strip stray -a" second pass. A single UniClass [rVow]
;    holds every romanised vowel spelling (INCLUDING a/A). Consonants become
;    bare when *any* member of [rVow] follows, and get a virama otherwise.
;    Each vowel then has its own initial-position rule (word start / after
;    another vowel) and medial-position rule (right after a consonant) --
;    'a'/'A' fit the same template as every other vowel: their "medial" rule
;    simply deletes them, since a bare consonant already implies the vowel.
;
;  * Devanagari OM (U+0950) is NEVER produced by any rule in this file.
;    "oṃ" / "auṃ" always convert literally to o+anusvara / au+anusvara
;    (ओं / औं). If you want the ligature ॐ, type it directly in the source
;    text — it is plain Devanagari, so it simply passes through untouched.
;    This is intentional: a "blind" converter must never upgrade ordinary
;    letters into a special/sacred symbol.
;
;  * Consonant clusters ("conjuncts") need NO special handling here: in
;    Unicode, k+t+r and "ktra-as-one-conjunct" are the identical sequence
;    KA + VIRAMA + TA + VIRAMA + RA. Which ligature/half-form glyph gets
;    drawn is entirely up to the font's OpenType shaping (blwf/pref/half
;    features via HarfBuzz), not this mapping. The one thing THIS file
;    depends on is that word boundaries in the source are marked with real
;    spaces, so a cluster is never accidentally split/merged across words.
;
;  * Case carries no phonemic meaning (k/K, kh/Kh/KH are the same sound);
;    length/retroflexion/etc. are carried only by diacritics. Every rule
;    below therefore has full lower/Title/ALL-CAPS coverage.
;
;  * Vedic pitch accents (udātta/anudātta/svarita) are NOT yet included --
;    see the placeholder section near the end of this file. Add rules there
;    once the source-text accent convention is confirmed.

LHSName "UNICODE"
RHSName "UNICODE"

pass(Unicode)

"""
add(HEADER)

# ---------------------------------------------------------------------------
# UniClasses
# ---------------------------------------------------------------------------

# rCons: every consonant, every case variant (needed for the "is the previous
# letter a consonant" check used by the initial-vowel rules)
rcons_members = []
for roman, _ in CONSONANTS:
    for variant in case_variants(roman):
        rcons_members.append(seq(variant))
add("UniClass [rCons] = ( " + " ".join(rcons_members) + " )")
add(";  every romanised consonant spelling (all case variants) -- used only")
add(";  to test 'is the character before this vowel a consonant?'")
add("")

# rVow: every vowel spelling (incl. a/A) + candrabindu forms + anusvara/visarga
# (defensive: lets a consonant go bare if ṃ/ḥ directly follow with no vowel)
rvow_members = []
for romans, _, _ in VOWELS:
    for r in romans:
        rvow_members.append(seq(r))
for romans, _, _ in CANDRABINDU:
    for r in romans:
        rvow_members.append(seq(r))
for r in ANUSVARA_ROMAN + VISARGA_ROMAN:
    rvow_members.append(seq(r))
add("UniClass [rVow] = ( " + " ".join(rvow_members) + " )")
add(";  every romanised vowel spelling (incl. a/A) + candrabindu forms +")
add(";  anusvara/visarga -- drives the bare-consonant-vs-virama decision")
add("")

# ---------------------------------------------------------------------------
# Consonants: bare-when-followed-by-vowel, else virama
# ---------------------------------------------------------------------------
add(";===========================================================")
add("; CONSONANTS")
add(";===========================================================")
for roman, deva in CONSONANTS:
    for variant in case_variants(roman):
        lhs = seq(variant)
        add(f"{lhs} / _ [rVow] <> {cp(deva)}")
    add("")
    for variant in case_variants(roman):
        lhs = seq(variant)
        add(f"{lhs} <> {cp(deva)} {cp(VIRAMA)}")
    add("")

# ---------------------------------------------------------------------------
# Vowels: initial vs medial
# ---------------------------------------------------------------------------
add(";===========================================================")
add("; VOWELS -- initial (word start / after another vowel) and")
add("; medial (right after a consonant) forms")
add(";===========================================================")
for romans, initial, medial in VOWELS:
    for r in romans:
        add(f"{seq(r)} / ^[rCons] _ <> {cp(initial)}")
    if medial is None:
        # One-way deletion (LHS > nothing): the inherent vowel disappears in
        # the medial position with no Devanagari output. This must use the
        # one-directional '>' operator, not '<>' -- a bidirectional rule
        # with an empty RHS also defines a reverse rule with an empty *match*
        # string (nothing -> 'a'), which real teckit_compile rejects as a
        # null/unanchored match. It's also the right semantics: there is no
        # information left to reverse this deletion from, consistent with
        # the case-recoverability caveat already documented for reverse
        # conversion (see docs/DESIGN.md).
        for r in romans:
            add(f"{seq(r)} / [rCons] _ > ")
    else:
        for r in romans:
            add(f"{seq(r)} / [rCons] _ <> " + " ".join(cp(c) for c in medial))
    add("")

add(";--- candrabindu combinations (rare) ---")
for romans, initial, medial in CANDRABINDU:
    for r in romans:
        add(f"{seq(r)} / ^[rCons] _ <> " + " ".join(cp(c) for c in initial))
    for r in romans:
        add(f"{seq(r)} / [rCons] _ <> " + " ".join(cp(c) for c in medial))
    add("")

# ---------------------------------------------------------------------------
# Anusvara / visarga (plain, and the a+ṃ / a+ḥ sandhi compounds)
# ---------------------------------------------------------------------------
add(";===========================================================")
add("; ANUSVARA / VISARGA")
add(";===========================================================")
add("; compounds first (longest match wins, but listed first for readability)")
A_LOWER, A_UPPER = "a", "A"
INDEP_A = "\u0905"
for a in (A_LOWER, A_UPPER):
    for m in ANUSVARA_ROMAN:
        add(f"{seq(a)} {seq(m)} / [rVow] _ <> {cp(INDEP_A)} {cp(ANUSVARA_DEVA)} ; V+a+\u1e43 (e.g. after another vowel)")
add("")
for a in (A_LOWER, A_UPPER):
    for h in VISARGA_ROMAN:
        add(f"{seq(a)} {seq(h)} / [rVow] _ <> {cp(INDEP_A)} {cp(VISARGA_DEVA)} ; V+a+\u1e25")
add("")
for a in (A_LOWER, A_UPPER):
    for m in ANUSVARA_ROMAN:
        add(f"{seq(a)} {seq(m)} / [rCons] _ <> {cp(ANUSVARA_DEVA)} ; consonant+a+\u1e43 -> just anusvara")
add("")
for a in (A_LOWER, A_UPPER):
    for h in VISARGA_ROMAN:
        add(f"{seq(a)} {seq(h)} / [rCons] _ <> {cp(VISARGA_DEVA)} ; consonant+a+\u1e25 -> just visarga")
add("")
add("; plain anusvara / visarga directly after an already-marked vowel")
for m in ANUSVARA_ROMAN:
    add(f"{seq(m)} <> {cp(ANUSVARA_DEVA)}")
for h in VISARGA_ROMAN:
    add(f"{seq(h)} <> {cp(VISARGA_DEVA)}")
add("")

# ---------------------------------------------------------------------------
# Punctuation, avagraha, danda, digits
# ---------------------------------------------------------------------------
add(";===========================================================")
add("; PUNCTUATION")
add(";===========================================================")
add("; avagraha -- three accepted input spellings")
# All three spellings use U+XXXX codepoint notation, not quoted literals: a
# quoted TECkit string consisting solely of an escaped quote (e.g. '''')
# fails to compile under the real teckit_compile even though the doubling
# escape works fine inside a longer literal -- see CHANGELOG.md.
for ch in ("\u02BC", "\u2019", "\u0027"):
    add(f"{cp(ch)} <> {cp(chr(0x093D))}")
add("")
add("; danda / double danda")
add("U+002F U+002F <> U+0965 ; double danda (must be listed before single --")
add(";                          longest match wins regardless, but kept in")
add(";                          this order for readability)")
add("U+002F <> U+0964 ; single danda")
add("")
add("; digits")
for i in range(10):
    add(f"U+{0x30+i:04X} <> U+{0x966+i:04X} ; {i}")
add("")

add(";===========================================================")
add("; DEVANAGARI OM (U+0950) -- deliberately no rule here.")
add("; Any literal ॐ already in the source text passes through unchanged")
add("; (default TECkit behaviour for unmatched input). Do not add a rule")
add("; that derives U+0950 from 'o'/'au' + anusvara -- see design notes")
add("; at the top of this file.")
add(";===========================================================")
add("")

add(";===========================================================")
add("; VEDIC PITCH ACCENTS -- placeholder, not yet implemented.")
add("; Add rules here once the source-text accent convention is known.")
add("; Likely targets:")
add(";   U+0951  DEVANAGARI STRESS SIGN UDATTA")
add(";   U+0952  DEVANAGARI STRESS SIGN ANUDATTA")
add(";   U+1CDA  VEDIC TONE DOUBLE SVARITA  (or U+A8E1 in the Vedic Extensions")
add(";           block, depending on target font's convention)")
add(";   U+A8E0..U+A8FF  Vedic Extensions block (fuller Rigveda/Yajurveda")
add(";           accent + svara repertoire, if the target font supports it)")
add(";===========================================================")
add("")

import os
OUTPUT = "\n".join(lines).rstrip() + "\n"
out_path = os.path.join(os.path.dirname(__file__), "..", "iastdev.map")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(OUTPUT)

print("TOTAL LINES:", len(OUTPUT.splitlines()))
print("Written to", os.path.abspath(out_path))
