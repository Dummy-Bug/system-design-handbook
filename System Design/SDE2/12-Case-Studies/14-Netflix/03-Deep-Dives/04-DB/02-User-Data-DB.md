## What Is User Data

Content metadata describes movies and shows. User data describes everything tied to a specific person — what they watched, how far they got, what they rated, what their watch history looks like. This is a completely different access pattern and a completely different DB problem.

The two main categories:

```
Watch history  → which movies/episodes has this user watched or started
Resume position → exactly where in a video did the user stop watching
```

---

## Watch History — Access Patterns

When a user logs in, Netflix needs to:
- Show recently watched titles on the homepage
- Hide already-watched content from recommendations
- Show ratings the user previously gave

Every query is user-first: "give me everything for this user." The relationship is simple — one user to many movies consumed. A single join table handles it:

```
user_watch_history
──────────────────────────────────────────────────
user_id      → 8 bytes
movie_id     → 8 bytes
rating       → 4 bytes
metadata     → 50 bytes (watched_at, completed, etc.)
resume_ts    → 8 bytes
──────────────────────────────────────────────────
total        ≈ 100 bytes per row
```

---

## Sizing Watch History — Do We Need Sharding?

Netflix has 300M MAU. Assume 500M total registered users. Users watch roughly 10 episodes or movies per month — about 0.33 per day. Not all registered users are active daily — assume 150M DAU.

```
Daily writes = 150M users × 0.33 records/day = ~50M records/day
Record size  = 100 bytes

Daily storage = 50M × 100B = 5,000MB = 5 GB/day
180 days      = 5GB × 180  = 900 GB
```

After 180 days, older watch history matters less for active recommendations — a movie a user watched 2 years ago has less signal than what they watched last week. So data older than 180 days moves to cold storage.

```
Hot tier  → PostgreSQL → last 180 days → ~900 GB → fast queries, recent history
Cold tier → S3         → older data    → cheap object storage, batch ML processing
```

900 GB is large but not unmanageable for PostgreSQL with a read replica. Sharding is not needed.

> [!info] Why keep cold data at all
> Old watch history is not useful for real-time queries but is extremely valuable for Netflix's recommendation ML models — which train on years of viewing behaviour. S3 is cheap enough to store it indefinitely for batch processing without it ever touching the live DB.

---

## Write Volume for Watch History

```
150M DAU × 0.33 records/day = 50M records/day
50M ÷ 86,400 seconds        = ~578 writes/second
```

578 writes/second is well within PostgreSQL's comfortable limit of ~10,000 writes/second on a single node. No problem here.

**PostgreSQL handles watch history.**

---

## Resume Timestamps — A Completely Different Problem

Here is where the analysis changes entirely.

Every time a user is actively watching a video, Netflix must continuously record where they are in it. If the user closes the app mid-episode and reopens it later, it resumes from the exact frame they left at. This means Netflix writes the user's current playback position every few seconds — not once per viewing session, but continuously throughout it.

The write happens once per chunk consumed. Each chunk is 4 seconds. So every active user generates one write every 4 seconds.

---

## Sizing Resume Writes — Where PostgreSQL Breaks

Netflix has 150M DAU. Apply the 80-20 rule — 20% are streaming at peak hour:

```
Peak concurrent streamers = 150M × 20% = 30M users
Each user writes every 4 seconds

Writes/second = 30M ÷ 4 = 7,500,000 writes/second
```

7.5 million writes per second. PostgreSQL handles ~10,000 writes/second on a single node. Even with aggressive sharding, you would need thousands of PostgreSQL nodes to absorb this load — operationally nightmarish.

This is not a storage problem. 900 GB of watch history was fine on PostgreSQL. This is a **write throughput** problem — a fundamentally different constraint that requires a fundamentally different tool.

> [!danger] Why PostgreSQL fails for resume timestamps
> It is not about data size — the resume record itself is tiny (user_id + movie_id + timestamp = ~24 bytes). It is about write frequency. 7.5M writes/second is 750x PostgreSQL's single-node limit. No amount of read replicas helps — read replicas only scale reads, not writes.

---

## Cassandra for Resume Timestamps

Cassandra is built for exactly this workload — high write throughput, distributed by design, no joins needed. It handles millions of writes per second across a cluster of nodes with linear horizontal scaling.

The access pattern for resume timestamps is simple:

```
Write → user watches chunk → store (user_id, movie_id, timestamp)
Read  → user opens app     → fetch timestamp WHERE user_id = X AND movie_id = Y
```

No joins. No complex queries. Just write fast and read by key.

---

## Partition Key and Clustering Key Design

Cassandra distributes data across nodes using a partition key. The choice of partition key determines which rows land on which node — and a bad choice creates **hot partitions** where one node handles a disproportionate share of traffic.

**Option 1 — movie_id as partition key:**

All resume timestamps for Inception land on the same partition. Inception has millions of viewers. One node absorbs all writes for every popular title simultaneously.

```
movie_id = Inception → millions of users → one hot partition
                     → one node overwhelmed on every popular release
```

**Option 2 — user_id as partition key:**

All resume timestamps for one user land on the same partition. One user watches a handful of movies at a time — maybe 5-10 active titles. The partition stays small. Consistent hashing distributes 500M users evenly across all nodes.

```
user_id = any user → handful of movies → small, evenly distributed partition
                   → no hot partition regardless of what title is popular
```

user_id is the correct partition key. movie_id becomes the clustering key — it sorts rows within the partition and enables the query "for this user, give me the resume position for this specific movie."

```
Partition Key  → user_id   (distributes load evenly across nodes)
Clustering Key → movie_id  (enables per-movie lookup within the partition)
```

> [!info] Why hot partition matters
> In Cassandra, a partition lives on one node. If that partition is hot — receiving millions of writes per second — that single node becomes the bottleneck regardless of how many other nodes are in the cluster. Choosing user_id as the partition key ensures that the load of a popular title (Squid Game season drop, 30M concurrent viewers) is spread across 500M user partitions on many different nodes — not concentrated on one partition.

---

## Final DB Summary for User Data

```
Watch history     → PostgreSQL
                  → 900 GB / 180 days hot tier
                  → S3 cold tier beyond 180 days
                  → 578 writes/second — within PostgreSQL limits

Resume timestamps → Cassandra
                  → 7.5M writes/second at peak — requires Cassandra
                  → Partition key: user_id
                  → Clustering key: movie_id
```

The key insight: watch history and resume timestamps look similar on the surface — both are user-to-movie records. But resume timestamps have 13,000x higher write frequency than watch history. That single difference changes the entire DB choice.
