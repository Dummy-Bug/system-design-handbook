## The Problem With Raw Text

You can't dump raw product descriptions straight into the inverted index. Raw text has inconsistencies that break matching.

If a user searches "headphone" (singular, lowercase) and the document says "Headphones" (plural, capital H), a naive index would miss the match — they're different strings. The indexing pipeline is the process that cleans and normalizes text before it enters the index, so that these variations all collapse to the same token.

---

## The Four Steps

Every document passes through this pipeline before being indexed. Every query passes through the same pipeline before being searched. This symmetry is what makes matching work.

### Step 1 — Tokenization

Split the raw text into individual words (called tokens). This handles punctuation, hyphens, special characters.

```
"Wireless Noise-Cancelling Headphones — Premium Quality"
        │
        ▼ tokenize
["Wireless", "Noise", "Cancelling", "Headphones", "Premium", "Quality"]
```

### Step 2 — Normalization

Lowercase everything. "Headphones" and "headphones" are the same word to a human — the index should treat them identically.

```
["Wireless", "Noise", "Cancelling", "Headphones", "Premium", "Quality"]
        │
        ▼ lowercase
["wireless", "noise", "cancelling", "headphones", "premium", "quality"]
```

### Step 3 — Stop Word Removal

Remove words that appear in almost every document and carry no meaning: "the", "a", "is", "and", "of", "in". These would bloat the index with useless high-frequency entries that match everything and rank nothing.

```
"the best headphones in the world"
        │
        ▼ remove stop words
["best", "headphones", "world"]
```

> [!important] Stop words are the obvious case
> For the non-obvious case — a common word that isn't a stop word (like "headphones" appearing in 9 million out of 10 million documents) — the ranking algorithm (TF-IDF/BM25) handles this by giving it a low IDF score.

### Step 4 — Stemming

Reduce each word to its root form. This is the step that solves the relevance problem from the SQL section.

```
"cancelling"   → "cancel"
"cancellation" → "cancel"
"cancelled"    → "cancel"
"headphones"   → "headphon"
"headphone"    → "headphon"
```

Now when a user searches "noise cancellation" — the pipeline stems it to "cancel". The document that contained "cancelling" was also stemmed to "cancel". They match. The product appears in results.

This is how the search engine understands word variations without knowing anything about language semantics.

---

## The Full Pipeline

```
Raw text:  "Wireless Noise-Cancelling Headphones — Premium Quality"
                │
                ▼ tokenize
        ["Wireless", "Noise", "Cancelling", "Headphones", "Premium", "Quality"]
                │
                ▼ normalize (lowercase)
        ["wireless", "noise", "cancelling", "headphones", "premium", "quality"]
                │
                ▼ stop word removal
        ["wireless", "noise", "cancelling", "headphones", "premium", "quality"]
        (no stop words here, all kept)
                │
                ▼ stemming
        ["wireless", "nois", "cancel", "headphon", "premium", "qualiti"]
                │
                ▼ stored in inverted index
```

The stems — not the original words — are what get stored and searched.

---

## Same Pipeline on the Query Side

> [!important] Critical symmetry
> The exact same pipeline runs on the user's search query. If the user types "Noise Cancellation Headphones", it gets tokenized → lowercased → stop words removed → stemmed to ["nois", "cancel", "headphon"]. These stems are then looked up in the index. This is why it matches documents that went through the same stemming process.

If you only ran the pipeline on documents but not queries (or vice versa), nothing would match.
