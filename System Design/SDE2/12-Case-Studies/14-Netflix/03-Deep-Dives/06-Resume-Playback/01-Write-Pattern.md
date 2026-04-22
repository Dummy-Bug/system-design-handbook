# Resume Playback — Write Pattern

## What Has to Happen While You Watch

Resume playback sounds like a simple read — open Netflix, get your position back. But the hard part is the write side. For resume to work across devices and survive crashes, Netflix has to continuously save your position while you are watching.

The client fires `POST /api/v1/stream/progress` every 4 seconds — one write per chunk consumed, silently in the background. The user never sees it. But it never stops for the entire duration of playback.

The reason for 4 seconds specifically: each video chunk is 4 seconds of video. Saving once per chunk means your position is always accurate to within 4 seconds. A phone crash, a dead battery, a lost connection — the worst case is losing 4 seconds of progress. That is acceptable.

Saving only on app close would be simpler — but if the app crashes, the network drops, or the phone battery dies, you lose everything since the last save. Saving every 4 seconds makes the failure window small.

---

## The Write Volume Problem

Netflix has 150M DAU. At peak hour, 20% are actively streaming — that is 30M concurrent streamers. Every one of them fires a write every 4 seconds:

```
30M peak streamers ÷ 4 seconds = 7,500,000 writes per second
```

7.5 million writes per second. The record itself is tiny — just three fields:

```
user_id          8 bytes
movie_id         8 bytes
position_seconds 8 bytes
─────────────────────────
total            24 bytes per write
```

This is not a storage problem. 24 bytes × 7.5M writes/second = 180 MB/second of data — manageable. It is a **write throughput** problem. PostgreSQL handles ~10,000 writes per second on a single node. 7.5M writes per second is 750× that limit.

---

## Cassandra — Built for This Workload

Cassandra's LSM tree storage engine batches writes into memory first, then flushes them to disk sequentially. Sequential disk writes are orders of magnitude faster than the random disk writes PostgreSQL does for indexed updates. This is why Cassandra handles millions of writes per second where PostgreSQL cannot.

The schema is simple — no joins, no complex queries, just write fast and read by key:

```
Partition Key  → user_id   (distributes load evenly across all nodes)
Clustering Key → movie_id  (enables per-movie lookup within a user's partition)
```

Every user's resume positions live on one node — the node that owns that user's partition. Writing a position update goes directly to that node, no cross-node coordination needed.

> [!info] Full Cassandra reasoning in the DB deep dive
> The choice of Cassandra over PostgreSQL, the hot partition analysis, and the write throughput math are covered in full in `03-Deep-Dives/04-DB/02-User-Data-DB.md`. This file focuses on how that write pattern connects to the resume playback experience.
