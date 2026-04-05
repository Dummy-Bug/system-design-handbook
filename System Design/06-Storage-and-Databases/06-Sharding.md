# Database Sharding

---

## The Problem Replication Doesn't Solve

You're running Twitter. 1 billion users. You've already added replicas to handle read traffic. But the primary is still struggling.

Replication copies the same data to multiple servers — every server still holds **all** the data:

```
Replication:
  Primary  → all 1 billion rows
  Replica1 → all 1 billion rows  (copy)
  Replica2 → all 1 billion rows  (copy)

Reads distributed ✓
Writes? Still all go to one primary ✗
Storage? Every server stores everything ✗
```

You're distributing reads, not the data itself. The primary still handles every write, and every server still needs enough disk for the entire dataset.

The fix is **Sharding** — split the data itself across multiple servers. Each server holds only a fraction.

```
Sharding:
  Shard 1 → users 1 - 250M
  Shard 2 → users 250M - 500M
  Shard 3 → users 500M - 750M
  Shard 4 → users 750M - 1B
```

Each server now holds 250 million rows instead of 1 billion. Writes are distributed too — writes for user_id 1 go to Shard 1, writes for user_id 600M go to Shard 2.

> [!info] **Sharding** — horizontally partitioning data across multiple servers so each server holds a subset of rows. Unlike replication, each shard has unique data.

---

## Vertical Partitioning — Splitting by Column

Everything above is **horizontal partitioning** — splitting rows across servers. But there's another axis: splitting by column.

Say your users table has 50 columns — name, email, bio, profile picture URL, privacy settings, notification preferences, last_login, follower_count, and so on. Most queries only need 2 or 3 of those. But every time you query a row, the database loads the entire row from disk — all 50 columns — even if you only asked for name and email.

The fix is **vertical partitioning** — split the wide table into narrower tables by access pattern:

```
users_core      → user_id, username, email          (every query)
users_profile   → user_id, bio, avatar_url           (profile page only)
users_settings  → user_id, privacy, notifications    (settings page only)
```

Now a feed query that only needs username loads only `users_core`. The bio and settings columns never touch the disk. Reads get faster, I/O drops.

> [!info] **Vertical partitioning** — splitting a wide table into narrower tables by column access pattern. Each table holds only the columns that are accessed together. Related by the same primary key.

The trade-off is that queries needing data from multiple partitions now require a JOIN. But that's usually a better problem to have than loading 50 columns on every single read.

---

## The Shard Key — Most Important Decision

The shard key is the column you use to decide which shard a row belongs to. The wrong choice breaks everything.

**Bad shard key — country_id:**

```
Shard 1 (India)   → 1.4 billion users → overwhelmed ✗
Shard 2 (USA)     → 340 million users → very busy ✗
Shard 3 (Vatican) → 800 users         → basically idle ✗
```

**Bad shard key — created_at (time-based):**

```
Shard Jan → old data, no new writes, just reads
Shard Feb → old data, no new writes, just reads
Shard Mar → ALL new writes hammering this one shard ✗
```

**Good shard key — user_id:**

```
High cardinality   → billions of unique values → distributes evenly ✓
Immutable          → user_id never changes → row never moves shards ✓
Always queryable   → every query includes user_id → always know which shard ✓
Even distribution  → no single user_id has disproportionate data ✓
```

A good shard key must be:

```
High cardinality   → many distinct values → even distribution
Immutable          → never changes → rows never need to migrate
Evenly distributed → no value dominates
Always present     → in every query so you always know which shard to hit
```

---

## The Three Sharding Strategies

You know you need to shard. You've picked a shard key. Now — how do you actually decide which row goes to which shard?

### Range-Based Sharding

The simplest approach — divide the key space into ranges:

```
Shard 1 → user_id 1 - 25M
Shard 2 → user_id 25M - 50M
Shard 3 → user_id 50M - 75M
Shard 4 → user_id 75M - 100M
```

Users sign up sequentially. user_id 99,000,001 goes to Shard 4. user_id 99,000,002 also goes to Shard 4. All new writes hammer the last shard — every single new signup hits the same server while the others sit idle. Same hotspot problem as the `created_at` shard key.

Range-based sharding is useful when you *want* data locality — say you're archiving old logs and only ever query recent ones. But for general user data, it creates hotspots.

### Hash-Based Sharding

Hash the key to decide the shard:

```
shard = hash(user_id) % N
```

Even distribution — no hotspots, no sequential clustering. This is the standard approach and what consistent hashing improves upon.

The trade-off: no control over where a specific user lands. user_id 1 might hash to Shard 3, and user_id 1's friend might hash to Shard 1. Related data scatters across shards. Cross-shard joins happen constantly for social graph queries.

### Directory-Based Sharding

Instead of a formula, you maintain an explicit lookup table — a directory that maps every key to a shard:

```
Directory (lookup table):
  user_id 1        → Shard 2
  user_id 2        → Shard 1
  user_id 500M     → Shard 2   ← deliberately placed with user 1
```

This solves the co-location problem that hash-based sharding can't. If user 1 and their friends need to live on the same shard, you can explicitly place them there. Moving a user to a different shard is just an update to the lookup table — no rehashing, no data migration.

The trade-off: every single read and write must first consult this directory — an extra network hop on every query. And the directory itself becomes a **SPOF** — if it goes down, nothing in the system can route anywhere.

```
Range-based      → split key space into ranges
                   problem: sequential inserts all hit the last shard (hotspot)

Hash-based       → hash the key to pick a shard
                   problem: no control over placement, related data scatters

Directory-based  → explicit lookup table: key → shard
                   problem: directory is a SPOF and a performance bottleneck
```

---

## Naive Hashing vs Consistent Hashing

**Naive hashing:**

```
shard = user_id % 4

user_id 423,891,204 % 4 = 0 → Shard 1
user_id 100,000,001 % 4 = 1 → Shard 2
```

Simple. Works great — until you add a 5th shard:

```
user_id 423,891,204 % 5 = 4 → Shard 5  ✗ completely different shard!
```

~80% of all data remaps to a different shard. You have to migrate hundreds of millions of rows while the system is live. Catastrophic.

**Consistent hashing:**

Place shards on a ring. Each key maps to the nearest shard clockwise. Adding a shard only affects the slice between it and its neighbour:

```
Before: Shard1 ── Shard2 ── Shard3 ── Shard4 (ring)

Add Shard5 between Shard2 and Shard3:
  Only data in the Shard2→Shard5 slice moves
  Everything else → completely untouched ✓
  ~1/N of data remaps instead of ~80%
```

---

## The Cross-Shard Join Problem

Before sharding — users and tweets on the same server, JOIN is easy:

```
Single Server:
┌─────────────────────────────────┐
│  Users table                    │
│  user_id │ username             │
│  1       │ alice                │
│  2       │ bob                  │
│                                 │
│  Tweets table                   │
│  tweet_id │ user_id │ text      │
│  101      │ 1       │ "hello"   │
│  102      │ 2       │ "world"   │
└─────────────────────────────────┘

SELECT users.username, tweets.text
FROM tweets JOIN users ON tweets.user_id = users.user_id
→ both tables on same server → easy ✓
```

After sharding by user_id:

```
Shard 1 (user_id 1-500M):          Shard 2 (user_id 500M-1B):
┌──────────────────────┐           ┌──────────────────────┐
│  alice (user_id 1)   │           │  charlie (600M)      │
│  her tweets          │           │  his tweets          │
└──────────────────────┘           └──────────────────────┘
```

Alice retweets charlie. Alice is on Shard 1, charlie is on Shard 2:

```
Tweet on Shard 1:
  tweet_id │ user_id │ retweet_of_user_id
  103      │ 1       │ 600M   ← charlie is on Shard 2!

SELECT users.username, tweets.text
FROM tweets JOIN users ON tweets.user_id = users.user_id
→ tweets on Shard 1, charlie's data on Shard 2
→ database cannot JOIN across two different servers ✗
```

The database engine can only JOIN tables on the same server. It has no concept of reaching out to another server mid-query.

**Fix 1 — Application-level JOIN:**

```
App server:
  Step 1 → query Shard 1 → fetch alice's tweets
  Step 2 → query Shard 2 → fetch charlie's user data
  Step 3 → join results in memory on app server

Database JOIN    → optimised, uses indexes, fast
Application JOIN → two network round trips + join in memory → more latency ✗
```

**Fix 2 — Co-location (better):**

Design your shard key so related data always lands on the same shard. For Twitter, shard by `user_id` and store the user's profile, tweets, and follows all on the same shard:

```
Shard 1:
  alice → her profile + all her tweets + her follows
  bob   → his profile + all his tweets + his follows
```

Alice's feed query never crosses shards for her own data. Cross-shard only happens when viewing someone on a different shard — handled in the app layer.

---

## Resharding — The Painful Part

Your startup launches with 4 shards. Two years later you have 10x users and need 16 shards. Even with consistent hashing, moving data while the system is live is dangerous:

```
During resharding:
  Row X is being moved from Shard 1 → Shard 3

  Write comes in for Row X:
    → Shard 1? (old location, still being migrated)
    → Shard 3? (new location, not fully there yet)
    → wrong answer either way → data loss or inconsistency

  Slower responses as DBs busy redistributing data
```

**Strategies to reduce the pain:**

```
1. Over-shard upfront   → start with 256 shards from day 1
                          adding servers = move whole shards, not split them
                          no row-level migration ✓

2. Double writes        → write to both old and new shard during migration
                          reads check new shard first, fall back to old
                          stop writing to old once migration complete ✓

3. Maintenance window   → pause writes briefly during cutover
                          simplest but means downtime ✗
```

> [!important] The best time to think about resharding is **before you need it**. Over-sharding upfront is cheap. Emergency resharding under load is one of the most dangerous operations in distributed systems — plan for it months in advance.

---

## Summary

```
Sharding         → split data across servers, each holds a fraction
                   solves: write bottleneck, storage limits, what replication can't fix

Vertical partitioning → split wide table by column access pattern
                        users_core / users_profile / users_settings
                        reduces I/O — queries only load columns they need

Shard key        → must be high cardinality, immutable, evenly distributed
                   good: user_id   bad: country_id, created_at

Sharding strategies:
  Range-based      → simple, hotspot problem on sequential inserts
  Hash-based       → even distribution, no control over co-location
  Directory-based  → full control, but SPOF + extra hop on every query

Consistent hashing → adding shards only remaps ~1/N of data
                     naive hashing remaps ~80% on any topology change

Cross-shard joins → database can't JOIN across servers
                    fix: co-locate related data, or join in app layer

Hotspot          → bad shard key concentrates load on one shard
                   India shard vs Vatican shard problem

Resharding       → painful, data moves while system is live
                   best solution: over-shard upfront
```
