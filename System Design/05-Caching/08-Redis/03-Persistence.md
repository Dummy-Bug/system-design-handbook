# Redis Persistence

> [!info] Redis is RAM. RAM is wiped on crash or restart. Persistence is how Redis saves its data to disk so it can recover — not for querying like a real DB, just for crash recovery.

Without persistence:

```
Redis crashes → restarts → all keys gone → cold start
→ every request is a cache miss → DB collapses
```

With persistence:

```
Redis crashes → restarts → loads data from disk → warm cache restored
→ DB never sees the spike
```

Disk is only touched on crash recovery. Normal reads and writes still go to RAM — persistence doesn't slow down your cache.

---

## RDB — Periodic Snapshots

Every N minutes, Redis takes a full snapshot of everything in memory and writes it to disk.

```
T=0min  → snapshot saved to disk
T=5min  → snapshot saved to disk
T=7min  → Redis crashes

On restart:
→ loads snapshot from T=5min
→ 2 minutes of writes lost
```

**What's good:**
```
Small file         → compact binary snapshot
Fast restart       → load one file, done
Low overhead       → snapshot runs in background, doesn't block reads/writes
```

**What's bad:**
```
Data loss          → always lose data since last snapshot
Not suitable for   → anything where losing even 1 minute of data is unacceptable
```

---

## AOF — Append Only File

Every write command gets logged to a file on disk immediately.

```
SET user:123 "John"   → appended to file
INCR page:views       → appended to file
ZADD leaderboard 9500 → appended to file

Redis crashes → replays every command from log → full recovery
→ almost zero data loss
```

**What's good:**
```
Durable            → logs every write, minimal data loss
Configurable sync  → can flush to disk every command, every second, or let OS decide
```

**What's bad:**
```
Large file         → every command logged, file grows forever
Slow restart       → replaying thousands of commands takes time
```

---

## Hybrid — RDB + AOF Together

```
AOF  → for durability, minimal data loss on crash
RDB  → for fast restarts, compact recovery file

On crash:
  → load RDB snapshot first   ← restore base state quickly
  → replay only AOF entries since the snapshot ← fill in the gap
  → faster than full AOF replay, more durable than RDB alone
```

This is what Redis recommends for production.

---

## Summary

| Mode | How it works | Restart speed | File size | Data loss risk |
|---|---|---|---|---|
| RDB | Snapshot every N minutes | Fast | Small | Up to N minutes |
| AOF | Log every write | Slow | Large | Near zero |
| Hybrid | RDB for base + AOF for recent writes | Fast | Medium | Near zero — recommended for production |

> [!important] For most caching use cases, some data loss on crash is acceptable — cache is a copy of DB data anyway. RDB alone is often fine. Hybrid is for when you can't afford even a few minutes of cache miss after a restart.
