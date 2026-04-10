## Elasticsearch Is Always a Secondary Index

This is the most important architectural point. **Elasticsearch is never your source of truth**. Your relational database (PostgreSQL, MySQL) holds the canonical data. Elasticsearch holds a derived copy optimized for search.

```
User adds/updates product
        │
        ▼
PostgreSQL (source of truth, ACID, durable)
        │
        ▼ CDC pipeline (Debezium reads the WAL/binlog)
        │
        ▼
Elasticsearch (secondary search index, eventually consistent)
        │
        ▼
Search results returned to user
```

If Elasticsearch goes down, you can rebuild it from PostgreSQL. If PostgreSQL goes down, your data is gone. The hierarchy is clear.

> [!danger] Never write directly to Elasticsearch as your primary store
> No ACID guarantees, no transactions, not designed for point writes. Always write to your relational DB first, let CDC propagate to Elasticsearch.

---

## Type-ahead vs Actual Search

When a user is typing in a search box, two different systems handle two different problems:

```
User typing "wireles..."
        │
        ▼ type-ahead suggestions (fast, prefix-based)
    Redis (cached popular queries) or Trie (prefix tree)
    → Returns suggestions instantly as user types

User hits Enter: "wireless headphones"
        │
        ▼ actual search (full-text, ranked)
    Elasticsearch
    → Runs through inverted index, scores with BM25, returns ranked results
```

Type-ahead needs sub-10ms response and only needs prefix matching — Trie or Redis sorted sets handle this. Actual search needs relevance and ranking — Elasticsearch handles this.

---

## Case Study Mapping

**Product search (Amazon, Flipkart):**
- Products stored in PostgreSQL
- CDC syncs to Elasticsearch
- User search goes to Elasticsearch — returns ranked, relevant results
- Faceted filtering (price range, brand, rating) also handled by Elasticsearch

**Log search (ELK Stack):**
- Services write logs → Logstash → Elasticsearch
- Kibana queries Elasticsearch for log search and dashboards
- "Find all 500 errors in the last hour" — Elasticsearch handles this trivially

**YouTube / Google search indexing:**
- Content ingested → processing pipeline → Elasticsearch (or proprietary equivalent)
- CDC pattern: when a video is uploaded, metadata flows through the indexing pipeline
- Ranking involves many more signals than BM25 (watch time, engagement) but inverted index is the foundation

**Type-ahead / autocomplete:**
- Elasticsearch supports prefix queries natively
- For very high throughput type-ahead, Redis sorted sets with prefixes are simpler and faster
- Both are valid — state the trade-off

---

## When to Mention in an Interview

| Scenario | What to say |
|---|---|
| "How would users search for products?" | "I'd use Elasticsearch as a secondary index, kept in sync via CDC from the primary DB. It handles full-text search, stemming, and BM25 ranking." |
| "Why not just SQL LIKE?" | "Full table scan O(n), no stemming so word variations don't match, no ranking — all three fail at scale." |
| "How does Google index the web?" | "At the core is an inverted index — same concept as Elasticsearch, massively distributed across thousands of machines." |
| "How would you build log search?" | "ELK stack — logs flow into Elasticsearch, Kibana for querying. Elasticsearch's inverted index makes full-text log search fast." |

> [!tip] Interview framing
> Always mention the CDC pattern when introducing Elasticsearch. It shows you understand that search is a derived view, not a primary store — and that's the architectural maturity interviewers are looking for at SDE-2.
