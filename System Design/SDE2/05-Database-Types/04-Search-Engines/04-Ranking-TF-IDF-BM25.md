## The Ranking Problem

The inverted index tells you *which* documents match a query. But when 10,000 documents all contain the word "headphones", which one goes first?

The user wants the most relevant result at the top — Google-style. To do this, every matching document needs a **score**, and results are sorted by that score descending.

The scoring algorithm is where the intelligence of a search engine lives.

---

## Term Frequency (TF) — The First Signal

The simplest intuition: if a document mentions "headphones" 50 times, it's probably more about headphones than a document that mentions it once.

```
TF = (number of times term appears in document) / (total words in document)
```

Dividing by total words normalizes for document length — a 10-word document with "headphones" twice is more focused than a 1000-word document with "headphones" twice.

---

## Inverse Document Frequency (IDF) — The Second Signal

TF alone has a fatal flaw. The word "premium" might appear 20 times in a document. But if "premium" appears in 8 million out of 10 million documents, it tells you almost nothing about what makes this document special. Every product uses the word "premium".

IDF penalizes words that appear in many documents and rewards words that are rare across the corpus:

```
IDF = log(total documents / documents containing the term)
```

A word in 100 out of 10 million documents has high IDF — it's rare and meaningful.
A word in 9 million out of 10 million documents has low IDF — it's everywhere and tells you nothing.

---

## TF-IDF — Putting It Together

```
TF-IDF(term, document) = TF × IDF
```

High TF-IDF means: this word appears frequently *in this document* but rarely *across all documents*. That combination signals genuine relevance.

### Worked Example

```
Total documents              = 10,000,000
Docs containing "headphones" = 100,000
Docs containing "premium"    = 8,000,000

Doc A (500 words):
  "headphones" appears 50 times
  "premium" appears 20 times
```

**Scoring "headphones" in Doc A:**
```
TF  = 50 / 500 = 0.1
IDF = log(10,000,000 / 100,000) = log(100) = 2

TF-IDF = 0.1 × 2 = 0.2
```

**Scoring "premium" in Doc A:**
```
TF  = 20 / 500 = 0.04
IDF = log(10,000,000 / 8,000,000) = log(1.25) = 0.097

TF-IDF = 0.04 × 0.097 = 0.0039
```

"Headphones" scores `0.2`. "Premium" scores `0.0039`. Despite "premium" appearing 20 times, it contributes almost nothing to the final score — because it's everywhere.

The final document score for a multi-word query is the **sum of TF-IDF scores for all query terms**. Highest total score = top of results.

> [!info] Why this works
> TF-IDF rewards documents where the query terms are both frequent (TF) and distinctive (IDF). Spammy common words are automatically downweighted by their low IDF. Rare specific words that appear many times in one document push that document to the top.

---

## BM25 — The Production Upgrade

TF-IDF has one remaining flaw: TF grows linearly. A document with "headphones" 500 times scores 10x more than one with 50 times. But does 500 occurrences really make a document 10x more relevant? No — after a point, repetition adds diminishing signal. A document stuffed with a keyword 500 times is likely spam.

BM25 fixes this with a **saturation curve**:

```
TF-IDF:   50 occurrences → 0.1,  500 occurrences → 1.0   (keeps growing linearly)
BM25:     50 occurrences → 0.8,  500 occurrences → 0.95  (flattens out)
```

BM25 also accounts for **document length**. A 50-word product title with "headphones" 5 times is much more focused than a 10,000-word article with "headphones" 5 times buried in it. BM25 normalizes for this — shorter focused documents rank higher for the same term frequency.

The formula:

```
BM25 = IDF × (TF × (k+1)) / (TF + k × (1 - b + b × docLen/avgDocLen))
```

`k` controls how quickly TF saturates. `b` controls how strongly document length affects the score. Both are tunable constants — Elasticsearch sets sensible defaults.

> [!tip] What to say in an interview
> "TF-IDF is the concept — term frequency times inverse document frequency. BM25 is the production-grade version that Elasticsearch uses. It improves on TF-IDF by capping term frequency contribution so keyword stuffing doesn't inflate scores, and normalizing for document length so short focused documents rank higher than long diluted ones. I don't need to tune the formula — Elasticsearch's defaults work well."

> [!danger] Don't memorize the BM25 formula for SDE-2
> Interviewers at Google L4 are not testing information retrieval math. Know what problem BM25 solves and why it's better than raw TF-IDF. That's the entire scope.
