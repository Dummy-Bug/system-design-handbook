## The Scaling Problem

An inverted index on a single machine works fine for millions of documents. But at 1 billion product descriptions, you can't fit the entire index in one machine's memory or disk. You need to split it.

Elasticsearch solves this with **shards**.

---

## Shards — Splitting the Index

A shard is an independent, self-contained inverted index. When you have 1 billion documents and 10 shards, each shard holds roughly 100 million documents and builds its own inverted index over those documents.

Documents are distributed across shards — each entire document goes to exactly one shard:

```
Doc 1: "wireless noise cancelling headphones" → Shard 1
Doc 2: "premium wireless earbuds"             → Shard 2
Doc 3: "noise cancelling headphones budget"   → Shard 3
```

Each shard then builds its own inverted index from the documents it owns:

```
Shard 1 index:            Shard 2 index:          Shard 3 index:
wireless → [Doc1]         wireless → [Doc2]        noise → [Doc3]
noise    → [Doc1]         premium  → [Doc2]        headphones → [Doc3]
headphones → [Doc1]       earbuds  → [Doc2]        ...
```

> [!important] The word "wireless" exists in multiple shards
> Because multiple documents across shards contain it. You cannot know which shard has the matching documents for a given query — so every query must go to every shard.

---

## The Query Flow

When a user searches "wireless headphones", a **coordinating node** receives the query and broadcasts it to all shards in parallel:

```
User Query: "wireless headphones"
        │
        ▼
┌──────────────────┐
│  Coordinating    │
│     Node         │  ← receives the query, acts as the brain
└──────────────────┘
        │
        │ broadcasts to ALL shards in parallel
        │
   ┌────┴────┬─────────┐
   ▼         ▼         ▼
Shard 1   Shard 2   Shard 3
searches  searches  searches
locally   locally   locally
   │         │         │
   └────┬────┘─────────┘
        │ each returns its top results + BM25 scores
        ▼
┌──────────────────┐
│  Coordinating    │
│     Node         │  ← merges all results, re-ranks by score globally
└──────────────────┘
        │
        ▼
   Final ranked results → User
```

Each shard returns its local top-N results with scores. The coordinating node merges them all and picks the globally top-ranked documents. This is a scatter-gather pattern.

---

## Replicas — Fault Tolerance and Read Throughput

If a shard's machine dies, those 100 million documents become unsearchable. To protect against this, Elasticsearch maintains **replica shards** — copies of each primary shard stored on different machines:

```
┌─────────────────────────────────────────────────┐
│               Elasticsearch Cluster              │
│                                                  │
│  Node 1              Node 2              Node 3  │
│  ┌──────────┐        ┌──────────┐        ┌────┐  │
│  │ Shard 1  │        │Shard 1   │        │    │  │
│  │ (primary)│───────▶│(replica) │        │... │  │
│  ├──────────┤        ├──────────┤        │    │  │
│  │ Shard 2  │        │          │        │    │  │
│  │(replica) │◀───────│Shard 2   │        │    │  │
│  │          │        │(primary) │        │    │  │
│  └──────────┘        └──────────┘        └────┘  │
└─────────────────────────────────────────────────┘
```

Primary and replica always live on different nodes. If Node 1 dies, Shard 1's replica on Node 2 takes over automatically.

Replicas give you two things:
1. **Fault tolerance** — the replica promotes to primary if the primary dies
2. **Read throughput** — search queries can go to either primary or replica, doubling read capacity

> [!info] Writes go to primary, reads can go to either
> This is exactly what the syllabus means by "shards (write), replicas (read)". All index writes go to the primary shard, which then replicates to replicas. Read queries are load-balanced across primary and replicas.

---

## Writes — The Indexing Path

When a new document is added to Elasticsearch:

```
New document arrives
        │
        ▼
Coordinating node determines shard (by hashing document ID)
        │
        ▼
Document sent to primary shard
        │
        ▼
Primary indexes the document (runs through pipeline, updates inverted index)
        │
        ▼
Primary replicates to replica shards
        │
        ▼
Acknowledge write success to client
```

The document is not searchable until the primary shard **refreshes** its index segment — by default, Elasticsearch does this every 1 second. This means there's up to a 1-second delay between indexing a document and it appearing in search results. This is a known and acceptable trade-off for write throughput.
