> [!question] You've added read replicas. Reads are fine. But writes are still bottlenecked and your disk is nearly full. What do you do?

---

## The problem replication doesn't solve

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

Each server now holds 250 million rows instead of 1 billion. Writes are distributed too — writes for user_id 1 go to Shard 1, writes for user_id 600M go to Shard 3.

> [!info] Sharding
> Horizontally partitioning data across multiple servers so each server holds a subset of rows. Unlike replication, each shard has **unique** data — no two shards hold the same rows.

---

## Sharding is basically multiple primaries — with one key difference

Each shard is its own independent primary accepting writes for its slice of data. So yes — sharding is multiple primaries at the end of the day.

But there's a critical difference from what we discussed in multi-primary replication:

In **multi-primary**, multiple nodes accept writes for the **same data** — that's where conflicts happen. User A updates the same row on Node 1 and Node 2 simultaneously, and the system has to figure out which write wins.

In **sharding**, each node owns a **completely different slice of data** — there's no overlap. Shard 1 owns users 1–250M, Shard 2 owns users 250M–500M. They will never get a conflicting write for the same row because they never share rows.

```
Multi-primary:
  Node A and Node B both own user_id 423 → conflict possible ✗

Sharding:
  Shard 1 owns user_id 423
  Shard 2 owns user_id 600,000,000
  → they never touch each other's data → no conflicts ✓
```

Sharding gives you the write scalability of multi-primary without the conflict problem — because the data is partitioned, not replicated.

And in practice, each shard usually also has its own replicas for read scalability and fault tolerance:

```
Shard 1 Primary → Shard 1 Replica 1
                → Shard 1 Replica 2
Shard 2 Primary → Shard 2 Replica 1
                → Shard 2 Replica 2
```

Sharding for write scalability. Replication within each shard for read scalability and availability. The two work together.

---

## Vertical Partitioning — splitting by column

Everything above is **horizontal sharding** — splitting rows across servers. But there's another axis: splitting by column.

Say your users table has 50 columns — name, email, bio, profile picture URL, privacy settings, notification preferences, last_login, follower_count, and so on. Most queries only need 2 or 3 of those. But every time you query a row, the database loads the entire row from disk — all 50 columns — even if you only asked for name and email.

The fix is **vertical partitioning** — split the wide table into narrower tables by **access pattern**:

```
users_core      → user_id, username, email          (every query needs this)
users_profile   → user_id, bio, avatar_url           (profile page only)
users_settings  → user_id, privacy, notifications    (settings page only)
```

Now a feed query that only needs username loads only `users_core`. The bio and settings columns never touch the disk. Reads get faster, I/O drops.

> [!info] Vertical partitioning
> Splitting a wide table into narrower tables by column access pattern. Each table holds only the columns accessed together. Related by the same primary key.

The trade-off is that queries needing data from multiple partitions now require a JOIN. But that's usually a better problem to have than loading 50 columns on every single read.

---

## Horizontal vs Vertical — when to use each

```
Horizontal sharding  → too many rows, DB can't hold them all or write fast enough
                       split: rows go to different servers

Vertical partitioning → too many columns, queries load more data than they need
                        split: columns go to different tables on same or different servers
```

In practice, most large systems use both — vertical partitioning to keep tables lean, horizontal sharding to distribute row volume across servers.
