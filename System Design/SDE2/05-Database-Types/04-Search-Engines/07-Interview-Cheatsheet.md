## Why Not SQL Search?

> [!danger] Three failures of SQL `LIKE` search
> 1. **Performance** — leading wildcard `LIKE '%word%'` = full table scan, O(n), no index
> 2. **Relevance** — exact character match only. "cancelling" ≠ "cancellation"
> 3. **Ranking** — no concept of most relevant first

---

## Inverted Index in One Line

> [!info]
> Flip the mapping: instead of document → words, store word → [document IDs]. Lookup is O(1). Query = look up each word, intersect the lists.

---

## Indexing Pipeline (in order)

```
Raw text
  → Tokenize       (split into words)
  → Normalize      (lowercase)
  → Stop words     (remove "the", "a", "is")
  → Stem           (cancelling → cancel, headphones → headphon)
  → Store in index
```

Same pipeline runs on the query. Symmetry is what makes matching work.

---

## TF-IDF

```
TF  = occurrences in doc / total words in doc
IDF = log(total docs / docs containing term)
TF-IDF = TF × IDF
```

High TF-IDF = frequent in this doc, rare across all docs = genuinely relevant.

**Quick calculation:**
- "headphones" in 100k/10M docs, appears 50x in a 500-word doc → TF-IDF = 0.2
- "premium" in 8M/10M docs, appears 20x in same doc → TF-IDF = 0.004

---

## BM25 vs TF-IDF

| | TF-IDF | BM25 |
|---|---|---|
| TF growth | Linear (keeps growing) | Saturates (diminishing returns) |
| Doc length | Not considered | Normalized |
| Used by | Textbooks | Elasticsearch (production) |

> [!tip] One-liner
> "BM25 caps term frequency so keyword stuffing doesn't inflate scores, and normalizes for document length. It's what Elasticsearch uses by default."

---

## Elasticsearch Architecture

```
Query → Coordinating Node
             │ scatter to all shards in parallel
             ▼
    [Shard1] [Shard2] [Shard3]  ← each has its own inverted index
             │ gather top results + scores
             ▼
        Coordinating Node merges, re-ranks
             │
             ▼
        Final results → User
```

- **Shards** = horizontal split of the index (for scale)
- **Replicas** = copies of each shard (for fault tolerance + read throughput)
- **Writes** → primary shard only
- **Reads** → primary or replica

---

## Key Architectural Pattern

```
PostgreSQL (source of truth)
    │
    ▼ CDC (Debezium)
Elasticsearch (secondary search index)
```

> [!important] Elasticsearch is never the source of truth. Always a derived secondary index.

---

## Type-ahead vs Search

```
Typing "wireles..."  → Redis / Trie  (prefix match, sub-10ms)
Hit Enter            → Elasticsearch (full-text, BM25 ranked)
```

---

## Where to Use

| Use case | Tool |
|---|---|
| Product search | Elasticsearch |
| Log search | Elasticsearch (ELK stack) |
| Type-ahead | Redis sorted sets or Trie |
| Web/content search | Inverted index (Elasticsearch or proprietary) |
| Keeping search in sync | CDC pipeline from primary DB |
