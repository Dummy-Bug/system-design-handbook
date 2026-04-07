# Search Engines — Overview

> [!info] What is a search engine (in system design)?
> A specialized data store built around an **inverted index** — a data structure that maps words to the documents containing them. It enables fast, relevant, ranked full-text search that a relational database fundamentally cannot provide.

---

## The Core Problem

SQL databases were designed for structured queries on exact values. The moment a user types a free-text search query, SQL breaks down in three ways:

1. **Performance** — `LIKE '%word%'` forces a full table scan. No index helps. O(n) every time.
2. **Relevance** — exact string match only. "cancelling" ≠ "cancellation". Real matches get missed.
3. **Ranking** — SQL has no concept of "most relevant first". Results come back in arbitrary order.

Search engines solve all three problems at once.

---

## The Key Ideas (in order)

| Concept | What it solves |
|---|---|
| Inverted index | Fast lookup — word → document list, O(1) instead of O(n) scan |
| Indexing pipeline | Relevance — tokenize, normalize, stem so "cancelling" matches "cancellation" |
| TF-IDF / BM25 | Ranking — score documents by how relevant they are to the query |
| Shards | Scale — split the index across machines |
| Replicas | Fault tolerance + read throughput |

---

## Where It Fits in System Design

```
Source of truth (PostgreSQL)
        │
        ▼ CDC (Debezium)
Elasticsearch (secondary search index)
        │
        ▼
User search results (ranked, relevant)
```

> [!important] Elasticsearch is never the source of truth
> Always a secondary index kept in sync via CDC. The primary DB is still SQL.

---

## When to Mention in an Interview

- Product search ("I'd use Elasticsearch for full-text search + ranking")
- Log search ("ELK stack — Elasticsearch for log search")
- Type-ahead ("prefix queries on the inverted index")
- Any system where users search free-text content
