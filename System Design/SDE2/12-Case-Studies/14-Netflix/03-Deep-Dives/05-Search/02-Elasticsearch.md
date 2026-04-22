# Search Deep Dive — Elasticsearch

## The Inverted Index

Think about the index at the back of a textbook:

```
Distributed Systems ........ 45, 67, 203
Replication ................ 67, 88, 204
Consistency ................ 88, 203, 210
```

It maps a word to every page number where that word appears. You don't read every page looking for "Replication" — you go straight to the index, find the entry, and jump to pages 67, 88, 204.

An **inverted index** does the same thing for documents. Instead of indexing by document (row → words), it indexes by word (word → documents):

```
"leo"         → [movie_45, movie_89, movie_203, episode_1204 ...]
"dicaprio"    → [movie_45, movie_89, movie_203 ...]
"inception"   → [movie_45]
"thriller"    → [movie_45, movie_67, movie_88 ...]
"stranger"    → [series_12, episode_301, episode_302 ...]
```

Every word that appears anywhere — in any title, description, cast name, or genre tag — gets its own entry pointing to every document containing it. When a user types "leo", the search engine looks up the "leo" entry and gets back the list of matching documents in microseconds. No row scanning, no pattern matching — a direct index lookup.

This is why a dedicated search engine is fundamentally different from `LIKE`. `LIKE` scans documents to find words. An inverted index looks up words to find documents. The direction is reversed, and the performance difference is enormous.

---

## Fuzzy Matching — Tolerating Typos

A user types **"strannger things"** — one extra "n". The inverted index has an entry for "stranger" but not "strannger". Exact lookup returns nothing.

The solution is fuzzy matching, based on **edit distance** — the minimum number of single-character changes (insertions, deletions, substitutions) needed to turn one word into another.

```
"strannger" → "stranger"    remove one 'n'  → edit distance 1
"incpeton"  → "inception"   swap c+p, add i → edit distance 2
"netflx"    → "netflix"     insert i        → edit distance 1
```

Elasticsearch allows fuzzy matching with `fuzziness: AUTO`. For words up to 5 characters, it allows 1 edit. For longer words, 2 edits. "strannger" is 1 edit away from "stranger" — it matches. The user sees Stranger Things instead of a blank page.

> [!info] Same edit distance as DSA
> This is the same Levenshtein distance dynamic programming problem from algorithms. The difference is that Elasticsearch precomputes edit-distance neighbours at index-build time — so at query time it's a lookup, not a DP computation across every word in the index.

---

## Relevance Scoring — Not All Matches Are Equal

When a user searches "leo", multiple documents match. The inverted index returns all of them. But in what order?

PostgreSQL `LIKE` has no concept of order — results come back in whatever order the table scan produces. A documentary that mentions "leo" once in its description ranks the same as the show literally titled "Leo".

Elasticsearch assigns every match a **relevance score** based on how well the document matches the query. You control this through **boost values** — weights you assign to different fields when configuring the index:

```
title field       → boost 3.0   (exact title match is most relevant)
cast field        → boost 2.0   (actor name match is highly relevant)
genre field       → boost 1.5   (genre tag match is relevant)
description field → boost 1.0   (description mention is least relevant)
```

A document where "leo" appears in the title scores 3× higher than one where it only appears in the description. Results come back ranked by score — the most relevant results first.

```
Search: "leo"

Score 9.2  → "Leo"          (title match, boost 3.0 × exact match factor)
Score 7.1  → "Inception"    (cast match — Leonardo DiCaprio, boost 2.0)
Score 6.8  → "The Aviator"  (cast match — Leonardo DiCaprio, boost 2.0)
Score 2.1  → "Titanic"      (description match — "leo" mentioned once, boost 1.0)
```

This is what makes search feel intelligent. The user typed "leo" and Inception appears second — not because the title matches, but because the cast match is weighted highly enough to surface it near the top.

---

## Keeping Elasticsearch in Sync With PostgreSQL

Elasticsearch does not hold the source of truth. PostgreSQL does. Elasticsearch is a read-optimised replica of the same content metadata — structured differently for search, not for transactional queries.

When the transcoding pipeline ingests a new title and writes it to PostgreSQL, Elasticsearch needs to know. The naive approach — write to both simultaneously — creates a distributed consistency problem. If the Elasticsearch write fails, the two systems are out of sync. Rolling back a PostgreSQL write because Elasticsearch failed is more complexity than the problem deserves.

The correct approach is **Change Data Capture (CDC)**. PostgreSQL writes every change — every INSERT, UPDATE, DELETE — to an internal log called the write-ahead log before applying it to the table. A CDC tool called **Debezium** tails this log continuously and publishes every change as an event to Kafka.

```mermaid
flowchart LR
    TP[Transcoding Pipeline] -->|INSERT new title| PG[(PostgreSQL)]
    PG -->|write-ahead log| Deb[Debezium]
    Deb -->|change event| Kafka
    Kafka --> Sync[ES Sync Worker]
    Sync -->|index document| ES[(Elasticsearch)]
```

The transcoding pipeline only ever writes to PostgreSQL — it has no knowledge of Elasticsearch. Debezium picks up the change passively from the log. Kafka buffers the event. The sync worker consumes it and updates the Elasticsearch index.

The staleness window — time between a title being written to PostgreSQL and appearing in search results — is a few seconds. This is completely acceptable. Nobody searches for a title in the exact millisecond it is ingested. Eventual consistency is the right trade-off here.

> [!important] Why CDC over dual-write
> Dual-write (writing to both PostgreSQL and Elasticsearch in the same code path) requires you to handle partial failures — what if PostgreSQL succeeds but Elasticsearch fails? CDC avoids this entirely. The transcoding pipeline writes to one system. CDC asynchronously propagates the change to Elasticsearch. The failure modes are isolated and the source of truth is never in question.

> [!info] What gets indexed
> Each Elasticsearch document contains: movie_id, title, description, cast (array of names), genres (array), release_year. Video chunks, S3 URLs, and resume positions are not indexed — Elasticsearch is only for text search, not for serving actual content.
