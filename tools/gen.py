# -*- coding: utf-8 -*-
"""
Generator for a modernised, single-pass TECkit map (IAST Unicode <-> Devanagari),
built for classical/Puranic Sanskrit with extension points for Vedic material.

Design principles (per user requirements):
  1. Never guess special/sacred symbols (Om etc.) from ordinary letter sequences.
     Devanagari U+0950 (Om) is only ever produced if it's already present in the
     input (default TECkit passthrough) -- no rule ever emits it.
  2. Consonant clusters (conjuncts) are just consonant+virama+consonant in
     Unicode -- there is no separate "which conjunct glyph" decision to make at
     the mapping level; that's a font/shaping (OpenType) concern, not a mapping
     concern. So no special-casing is needed for "ktra" type sequences, AS LONG
     AS word boundaries (spaces) are present in the source text.
  3. Full upper/lower case symmetry throughout (case carries no phonemic
     meaning in this scheme; length is carried by macrons/diacritics only).
  4. Single unified vowel class drives both (a) whether a consonant is bare or
     virama-final, and (b) which vowel sign is attached -- including 'a' itself,
     which is handled by the SAME initial/medial template as every other vowel
     (initial -> independent letter; medial -> deleted, since it's inherent).
     This removes the old two-pass "strip stray -a" mechanism entirely.
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def cp(ch):
    """Render a single Unicode character as TECkit 'U+XXXX' notation."""
    return "U+%04X" % ord(ch)

def lit(s):
    """Render a literal ASCII/plain string as a quoted TECkit token.

    Embedded single quotes are doubled, per TECkit's escaping convention for
    quoted string literals (e.g. a literal apostrophe becomes '''' -- open
    quote, doubled quote for the escaped ', close quote).
    """
    return "'%s'" % s.replace("'", "''")

def token(s):
    """
    Render one input/output *character* as a TECkit token:
    plain ASCII -> quoted literal; anything else -> U+XXXX.
    """
    if ord(s) < 0x80:
        return lit(s)
    return cp(s)

def seq(s):
    """
    Render a Python string as a *space-separated sequence* of TECkit tokens,
    one token per character, EXCEPT that a run of consecutive plain-ASCII
    characters is combined into a single quoted literal (matches the house
    style already used in the source file for things like 'kh').
    """
    out = []
    buf = ""
    for ch in s:
        if ord(ch) < 0x80:
            buf += ch
        else:
            if buf:
                out.append(lit(buf)); buf = ""
            out.append(cp(ch))
    if buf:
        out.append(lit(buf))
    return " ".join(out)

# ---------------------------------------------------------------------------
# Consonants: (iast_lower, devanagari_bare_codepoint_as_char)
# ---------------------------------------------------------------------------

CONSONANTS = [
    ("k", "\u0915"), ("kh", "\u0916"), ("g", "\u0917"), ("gh", "\u0918"), ("\u1e45", "\u0919"),
    ("c", "\u091A"), ("ch", "\u091B"), ("j", "\u091C"), ("jh", "\u091D"), ("\u00F1", "\u091E"),
    ("\u1e6d", "\u091F"), ("\u1e6dh", "\u0920"), ("\u1e0d", "\u0921"), ("\u1e0dh", "\u0922"), ("\u1e47", "\u0923"),
    ("t", "\u0924"), ("th", "\u0925"), ("d", "\u0926"), ("dh", "\u0927"), ("n", "\u0928"),
    ("p", "\u092A"), ("ph", "\u092B"), ("b", "\u092C"), ("bh", "\u092D"), ("m", "\u092E"),
    ("y", "\u092F"), ("r", "\u0930"), ("l", "\u0932"), ("v", "\u0935"),
    ("\u015B", "\u0936"), ("\u1e63", "\u0937"), ("s", "\u0938"), ("h", "\u0939"),
]

VIRAMA = "\u094D"

def case_variants(roman):
    """
    Given a lowercase IAST consonant spelling (1 or 2 Python chars -- the 2nd,
    if present, is always 'h' for aspirates), return the list of realistic
    case-variant spellings: all-lower, Title (first letter caps, used at the
    start of a capitalised proper noun), and ALL-CAPS (used in headings).
    A mixed form like retroflex-lower + 'H' is intentionally excluded --
    it never occurs in real text (case only changes at letter or whole-word
    granularity, not mid-digraph without the first letter also changing).
    """
    if len(roman) == 1:
        return [roman, roman.upper()]
    base, h = roman[0], roman[1]
    return [
        base + h,                # lower:  kh / \u1e6dh
        base.upper() + h,        # Title:  Kh / \u1e6ch
        base.upper() + h.upper() # CAPS:   KH / \u1e6cH
    ]

# ---------------------------------------------------------------------------
# Vowels: (roman_token_list, initial_deva, medial_deva_or_None)
# medial_deva == None  =>  delete on match (used only for plain 'a')
# ---------------------------------------------------------------------------

VOWELS = [
    (["a", "A", "\u00E4", "\u00C4"],           "\u0905", None),        # a / \u00e4(\u00e4) alt spelling
    (["\u0101", "\u0100"],                     "\u0906", "\u093E"),    # \u0101
    (["i", "I", "\u00EF", "\u00CF"],           "\u0907", "\u093F"),    # i / \u00ef alt spelling
    (["\u012B", "\u012A"],                     "\u0908", "\u0940"),    # \u012b
    (["u", "U", "\u00FC", "\u00DC"],           "\u0909", "\u0941"),    # u / \u00fc alt spelling
    (["\u016B", "\u016A"],                     "\u090A", "\u0942"),    # \u016b
    (["\u1E5B", "\u1E5A"],                     "\u090B", "\u0943"),    # \u1e5b
    (["\u1E5D", "\u1E5C"],                     "\u0960", "\u0944"),    # \u1e5d
    (["\u1E37", "\u1E36"],                     "\u090C", "\u0962"),    # \u1e37
    (["\u1E39", "\u1E38"],                     "\u0961", "\u0963"),    # \u1e39
    (["\u0115", "\u0114"],                     "\u090D", "\u0946"),    # \u0115 (Vedic short e)
    (["e", "E"],                               "\u090F", "\u0947"),    # e
    (["ai", "Ai", "AI"],                       "\u0910", "\u0948"),    # ai
    (["\u014F", "\u014E"],                     "\u0911", "\u094A"),    # \u014f (Vedic short o)
    (["o", "O"],                               "\u0913", "\u094B"),    # o
    (["au", "Au", "AU"],                       "\u0914", "\u094C"),    # au
]

# Candrabindu combinations (independent-letter + candrabindu, matra + candrabindu)
CANDRABINDU = [
    (["\u0129", "\u0128"], "\u0907\u0901", "\u093F\u0901"),  # i-tilde -> i + candrabindu
    (["\u00F5", "\u00D5"], "\u0913\u0901", "\u094B\u0901"),  # o-tilde -> o + candrabindu
]

ANUSVARA_ROMAN = ["\u1e43", "\u1e42"]   # \u1e43 / \u1e42
VISARGA_ROMAN  = ["\u1e25", "\u1e24"]   # \u1e25 / \u1e24
ANUSVARA_DEVA  = "\u0902"
VISARGA_DEVA   = "\u0903"

# ---------------------------------------------------------------------------
# Vedic pitch accents (Rigveda phase): (roman_combining_mark, deva_combining_mark)
# ---------------------------------------------------------------------------
# Roman-side notation matches the author's published IAST keyboard layout
# (https://github.com/oleandrum/macos-iast-keyboard): combining diacritics
# typed immediately after the accented vowel, same as how Unicode combining
# marks normally work. Devanagari targets follow ACTUAL practice in printed
# Rigveda Samhita editions rather than Unicode character NAMES, which are
# misleading here -- see docs/DESIGN.md for the U+0951 naming trap.
#
# Deliberately excluded: an explicit udatta mark. Printed Rigveda Samhita
# editions leave udatta unmarked (it's the default/unmarked tone), and the
# obvious Unicode candidate by name, U+0951 DEVANAGARI STRESS SIGN UDATTA,
# is the mark actually used below for svarita -- a separate udatta rule
# would collide with it. See docs/DESIGN.md.
ACCENTS = [
    ("\u030d", "\u0951"),  # combining vertical line above -> svarita
    ("\u030e", "\u1cda"),  # combining double vertical line above -> double svarita
    ("\u1cdb", "\u1cdb"),  # vedic tone triple svarita (identity: already a
                            # valid Devanagari-combining mark on the Roman side)
    ("\u0331", "\u0952"),  # combining macron below -> anudatta
]

print("data loaded:", len(CONSONANTS), "consonants,", len(VOWELS), "vowel groups")
