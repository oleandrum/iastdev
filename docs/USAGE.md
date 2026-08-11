# Usage guide

Worked examples for `iastdev.map`, focused on the primary direction: **IAST → Devanagari**.
For *why* the map behaves this way, see [DESIGN.md](DESIGN.md).

## 1. The basic rule: is a vowel next?

A consonant is written **bare** (its inherent vowel implied) whenever *any* vowel — including
plain `a` — follows it. Otherwise it takes a **virāma** (्):

```
rāma   →  र ा म        (r + ā-matra + bare m; the inherent "a" needs no mark at all)
kṛṣṇa  →  क ृ ष ् ण     (ष्ण is a real cluster — the virāma there is correct)
```

## 2. Initial vs. medial vowels

A vowel not preceded by a Roman consonant (word start, or after another vowel) becomes an
independent Devanagari letter; otherwise it becomes a matra sign:

```
iṣṭa   → इ ष ् ट     ('i' word-initial → इ, an independent letter)
viṣa   → व ि ष        ('i' after 'v' → ि, a matra sign)
```

## 3. Case is phonemic-neutral — including ALL CAPS

Upper/lower case never changes the sound; length is carried only by diacritics. This works
throughout the word, not just at the start:

```
kṛṣṇa   → कृष्ण   (ordinary lowercase)
Kṛṣṇa   → कृष्ण   (Title Case — typical for a proper noun)
KṚṢṆA   → कृष्ण   (ALL CAPS — typical for a heading)
```

Digraphs (aspirates, and the retroflex/dental `ṭh`/`ḍh` pairs) support all three realistic case
patterns too:

```
maṭha  → मठ
Maṭha  → मठ
MAṬHA  → मठ
```

## 4. Anusvāra / visarga sandhi

The special two-token `a + ṃ` / `a + ḥ` sequences avoid emitting a redundant independent अ where
one isn't needed, and correctly *do* emit one when the preceding context is itself a vowel:

```
śivaṃ    → शिवं     ('a'+'ṃ' directly after a consonant → just ं, no extra अ)
namaḥ    → नमः      ('a'+'ḥ' directly after a consonant → just ः)
devāṃ    → देवां     ('a'+'ṃ' after a vowel (here ā) → अं, i.e. the "Vaṃ" pattern)
```

A plain `ṃ`/`ḥ` occurring after an already-marked vowel (not part of an `a+ṃ`/`a+ḥ` pair) converts
directly and unconditionally:

```
kiṃ  → किं
```

## 5. Om (ॐ) — never inferred, always explicit

`oṃ` and `auṃ` **always** convert literally — never to the sacred ligature:

```
oṃ    → ओं   (never ॐ)
auṃ   → औं
```

If you want the ligature itself, type it directly as Devanagari in your source text — it's
already Devanagari, so it passes through untouched:

```
ॐ  → ॐ
```

## 6. Consonant clusters (conjuncts)

No special handling is needed or attempted — see [DESIGN.md](DESIGN.md#the-conjunct-problem-ktra)
for why. Just make sure word boundaries in your source text are marked with real spaces:

```
saṃskṛta  → संस्कृत
kutra     → कुत्र
```

## 7. Candrabindu combinations

Rare, but supported, for nasalised i/o:

```
ĩ (U+0129)  → matra + ँ   e.g. medial: k + ĩ → किँ
õ (U+00F5)  → matra + ँ   e.g. medial: k + õ → कोँ
```

## 8. Vedic short e / o

Classical Sanskrit e/o are always long; Vedic texts also have **short** e/o, written here with a
breve diacritic:

```
ĕ (U+0115) / Ŏ (U+014E)  → short e / short o, both independent-letter and medial (matra) forms
```
```
ĕka  → ऍक     (Vedic short e, word-initial — distinct from the ordinary long e → एक)
```

Vedic pitch accents (udātta/anudātta/svarita) are **not implemented yet** — see
[DESIGN.md](DESIGN.md#vedic-pitch-accents-udātta--anudātta--svarita--not-yet-implemented).

## 9. Punctuation, digits, avagraha

```
'  or  ’  or  U+02BC   →  ऽ   (avagraha — three accepted input spellings)
/                      →  ।   (single daṇḍa)
//                     →  ॥   (double daṇḍa)
0-9 (ASCII digits)     →  ०-९  (Devanagari digits)
```

## 10. Alternate umlaut input (legacy / OCR compatibility)

A handful of Latin-1 umlaut characters are accepted as alternate spellings for short a/i/u,
carried over for compatibility with older scanned/OCR'd sources that may use them:

```
ä / Ä  →  a
ï / Ï  →  i
ü / Ü  →  u
```

---

## Quick reference table

| IAST | Initial | Medial (matra) |
|---|---|---|
| a | अ | *(none — inherent)* |
| ā | आ | ा |
| i | इ | ि |
| ī | ई | ी |
| u | उ | ु |
| ū | ऊ | ू |
| ṛ | ऋ | ृ |
| ṝ | ॠ | ॄ |
| ḷ | ऌ | ॢ |
| ḹ | ॡ | ॣ |
| ĕ (Vedic short e) | ऎ | ॆ |
| e | ए | े |
| ai | ऐ | ै |
| ŏ (Vedic short o) | ऒ | ॊ |
| o | ओ | ो |
| au | औ | ौ |
| ṃ | — | ं |
| ḥ | — | ः |
| any consonant, no vowel following | — | consonant + ् |
