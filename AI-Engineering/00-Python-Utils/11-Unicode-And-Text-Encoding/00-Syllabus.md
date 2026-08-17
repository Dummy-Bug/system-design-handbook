#python #unicode #encoding #tokenization #indic #python-utils #syllabus

# 11 · Unicode & Text Encoding — Syllabus

15 concepts. **Generic** — how text works in Python, ahead of any tokenizer.

> The most Sarvam-specific folder here, and the one with the least overlap with anything else in this vault. Their Week 2 asks, verbatim, for **text normalization utilities handling Unicode NFC/NFD and Indic grapheme cluster boundaries** — and token fertility on Devanagari is a number they publish and compete on (1.4–2.1 tokens/word vs 3.0–4.0+ for generic tokenizers). None of that is reachable without this layer.

**Why this sits last:** it depends on nothing above it and nothing above it depends on it. Order it anywhere — it's placed at the end because it's the most specialised, not the least important.

**Currency check (2026-08-04):** stable in Python; the moving part is the Unicode standard version bundled with your interpreter (`unicodedata.unidata_version`), which matters if you're handling recently-added scripts or emoji. `str.isascii()` is 3.7+. Verify the current `regex` package behaviour if relying on it for `\X` grapheme matching, since the stdlib `re` does not support it.

---

## A · The model

**1. `str` vs `bytes` — the distinction everything rests on**
`str` is a sequence of Unicode code points; `bytes` is a sequence of 8-bit values. Encoding converts one to the other, decoding reverses it. Every text bug is ultimately a confusion between these two.

**2. Encode and decode**
`.encode()` / `.decode()`, the default UTF-8, and `errors=` (`strict`, `ignore`, `replace`, `surrogateescape`). When each is defensible — `ignore` almost never is.

**3. `UnicodeDecodeError` in the wild**
Reading a file with the wrong assumed encoding, mojibake, BOMs, and `utf-8-sig`. What to do when the encoding genuinely isn't known.

**4. Code points, and what UTF-8 actually does**
Variable-width encoding: ASCII in one byte, most Latin/Greek/Cyrillic in two, **Devanagari and most Indic scripts in three**. This byte-count asymmetry is the root of the token-fertility gap and worth understanding numerically, not vaguely.

## B · Why one character is not one thing

**5. Code point ≠ character ≠ grapheme**
The three-level distinction. A user-perceived character (a grapheme cluster) can span several code points — and `len()` counts code points, so `len()` is not the number of characters a reader sees.

**6. Grapheme clusters**
Combining marks, and specifically **Indic consonant clusters**: a consonant plus virama plus consonant plus vowel sign is **one** perceived character across multiple code points. Splitting or truncating naively lands mid-cluster and corrupts the text. Sarvam names this requirement explicitly.

**7. Grapheme-aware operations in practice**
The stdlib gives you no grapheme iteration; the `regex` package's `\X` and dedicated segmentation libraries do. What **truncate this string to 100 characters** should actually mean.

**8. `unicodedata`**
`category()`, `name()`, `combining()`, `normalize()`. The stdlib's window into what a code point actually **is** — the tool for writing a script-aware normaliser.

## C · Normalisation

**9. NFC, NFD, NFKC, NFKD**
Composed vs decomposed, canonical vs compatibility. Why two visually identical strings can compare unequal, and why that breaks deduplication, cache keys, and exact-match evaluation.

**10. Choosing a form**
NFC as the usual storage/transport default; NFD when you need to inspect or strip combining marks; the compatibility forms as lossy and therefore a deliberate choice, not a default.

**11. Case folding and comparison**
`.casefold()` vs `.lower()`, why Turkish dotless-i is the classic counterexample, and why case-insensitive comparison is not `lower() == lower()`.

**12. Building a normalisation pipeline**
Order of operations: decode → normalise → strip zero-width/control characters → collapse whitespace → optionally case-fold. Idempotence as the property to test for, and knowing which steps are lossy.

## D · Where this meets tokenization

**13. Byte-level BPE**
Why modern tokenizers operate on **bytes** rather than characters: no out-of-vocabulary problem, any input encodable. The consequence — a single Devanagari character is three bytes, so a script the tokenizer wasn't trained on fragments into many tokens.

**14. Token fertility**
Tokens per word as a measurable quantity. How to compute it for a given corpus and tokenizer, why 1.4–2.1 vs 3.0–4.0 is roughly a **2× difference in both cost and effective context length** for the same text, and how to benchmark two tokenizers against each other on the same Indic corpus.

**15. Code-switching and mixed-script text**
Hindi and English alternating inside one sentence — Sarvam's stated requirement. Script detection, per-script normalisation rules, and why a single global normalisation pass can be wrong for mixed input.

---

## Deferred

| Topic | Goes to |
|---|---|
| BPE training/merge algorithm, tokenizer internals | outside this vault (Sarvam Month 1, Week 2) |
| Embeddings and chunking | outside this vault (`07-RAG`) |
| Regex as a general skill | not scheduled — reference material |
| Audio/speech encoding | outside this vault (Sarvam Month 3) |

## Where this already shows up

Nowhere. This is genuinely new surface — and it's the folder that maps most directly onto what Sarvam actually builds, which makes it disproportionately useful for exactly one interview and near-useless for a generic backend one. Worth being clear-eyed about that trade before spending a week here.

## Interview hooks

**Why does the same sentence cost twice as many tokens in Hindi as in English?** — concepts 4, 13, 14 in sequence, and it's a question their own published numbers invite. The follow-up, **how would you measure that?**, is concept 14. Sarvam's Stage 2 screen names **subword tokenization mechanics (how BPE handles Indic morphology)** directly.

## Sources to verify against

- [Unicode HOWTO](https://docs.python.org/3/howto/unicode.html) — the best single starting point
- [`unicodedata`](https://docs.python.org/3/library/unicodedata.html) · [`codecs`](https://docs.python.org/3/library/codecs.html)
- [UAX #15 — Normalization Forms](https://unicode.org/reports/tr15/) · [UAX #29 — Text Segmentation](https://unicode.org/reports/tr29/) (grapheme cluster boundaries, concept 6)
- Sarvam's published tokenizer fertility figures, for concept 14 — benchmark against them rather than trusting them
