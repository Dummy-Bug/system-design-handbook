# Write Strategies — Write-Through, Write-Back, Write-Around

> [!question] A write request comes in. Does the cache get updated? Does the DB get updated? In what order? All at once or asynchronously?

---

## Write-Through

> [!info] Every write goes to cache AND DB synchronously. Both confirmed before returning success.

```
Write request arrives
→ write to cache
→ write to DB
→ both confirmed → return success ✓
```

**What's good:**
```
Cache always consistent with DB  → reads always get the latest data
No data loss risk                → DB always has the authoritative value
Simple reasoning                 → cache and DB are always in sync
```

**What's bad:**
```
Every write is slower       → must wait for both cache + DB round trips
Write latency roughly 2x    → not suitable for write-heavy systems
Caches writes that may      → if you write something that's never read,
never be read               → you wasted memory and write latency
```

**Use when:** data is read frequently immediately after being written — user profile updates, settings, preferences, any write that's followed by a near-immediate read.

---

## Write-Back (Write-Behind)

> [!info] Write to cache immediately and return success. DB write happens asynchronously in the background.

```
Write request arrives
→ write to cache → return success immediately ✓
→ DB write happens in background some time later (seconds to minutes)
```

**What's good:**
```
Extremely fast writes    → user doesn't wait for DB round trip at all
Absorbs write spikes     → cache buffers burst writes, DB drains at its pace
Batching possible        → multiple writes can be coalesced before hitting DB
```

**What's bad:**
```
Data loss risk           → cache crashes before flushing to DB
                           → those writes are gone forever
Complexity               → need reliable background flush mechanism
                           → what if flush fails? retry logic needed
```

**Classic example:** Google Docs — typing feels instant because keystrokes write to cache immediately. The DB write happens every few seconds in the background. If your internet dies mid-typing, you lose a few characters — that's the data loss window in action.

**Use when:** write speed is critical, some data loss is acceptable, and you have a reliable flush mechanism (e.g., periodic batch writes with a WAL as backup).

---

## Write-Around

> [!info] Write directly to the DB and skip the cache entirely. The cache is only populated when a read request comes in later.

```
Write request arrives
→ write to DB directly (cache completely untouched)
→ return success ✓

Next read for that data
→ cache miss (never cached the write)
→ fetches from DB
→ populates cache
→ subsequent reads hit cache ✓
```

**What's good:**
```
Cache not polluted with write-once data  → memory preserved for hot reads
No write overhead on cache               → simpler write path
```

**What's bad:**
```
Next read after a write is always a miss → slight latency spike on first read
Not useful if data is read back soon     → you'd benefit more from write-through
```

**Use when:** write-once data that is rarely or never read back — logs, audit trails, analytics events, archived records. No point caching something you'll never read again.

---

## Summary

| Strategy | DB written | Cache updated | Trade-off |
|---|---|---|---|
| Write-Through | Synchronously on write | Synchronously on write | Always consistent — slower writes |
| Write-Back | Asynchronously later | Immediately on write | Fastest writes — data loss risk |
| Write-Around | Immediately on write | Never on write (only on read) | No cache pollution — first read is a miss |

> [!important] Most systems combine strategies per data type
> User profile (read-heavy, low write volume) → Write-Through
> Activity feed events (write-heavy, slight staleness OK) → Write-Back or Write-Around
> Logs and audit trails (write-once, rarely read) → Write-Around
