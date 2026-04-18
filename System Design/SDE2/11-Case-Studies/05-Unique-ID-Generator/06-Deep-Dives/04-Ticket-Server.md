# Ticket Server — Shared Counter

## The idea

Multiple ID generator servers each have independent counters that collide. The fix seems obvious — instead of each server managing its own counter, have one **central authority** that owns the counter. Every server asks the central authority for the next number before returning an ID.

```
ID Server A ──→ Central Counter (DB or Redis) ──→ returns 1001
ID Server B ──→ Central Counter (DB or Redis) ──→ returns 1002
```

Since the central counter handles one request at a time atomically, no two servers ever get the same number.

---

## Why Redis over a relational database

A relational database can serve as the central counter, but it involves disk writes and transaction overhead — slow for a service that needs to return IDs in single-digit milliseconds.

Redis is a better fit. The `INCR` command is:
- **Atomic** — read-and-increment happens as one operation, no race condition
- **In-memory** — no disk I/O, nanosecond latency
- **Simple** — one command, no transactions needed

```
INCR global_counter → returns 1001
INCR global_counter → returns 1002
INCR global_counter → returns 1003
```

Each call is guaranteed to return a unique, incrementing value.

---

## The problem — SPOF

Redis is now the single point of failure for the entire ID generation system. If Redis goes down, no ID can be generated anywhere — every write to every service in the platform stops.

The instinct is to add more Redis nodes. But this creates a new problem: two Redis nodes with independent counters both start at 1 and immediately collide. To keep counters in sync across multiple nodes, you'd need replication — and replication introduces lag. During that lag, two nodes could return the same counter value.

You can't have both **high availability** and **no collisions** with a shared counter without coordination. And coordination adds latency — exactly what we're trying to avoid.

---

## One partial fix — range-based batching

Instead of each ID server calling Redis for every single ID, each ID server calls Redis once to claim a **batch of IDs**:

```
ID Server A claims range 1–1000     → serves IDs 1, 2, 3... locally
ID Server B claims range 1001–2000  → serves IDs 1001, 1002, 1003... locally
```

Now Redis is called once per thousand IDs instead of once per ID. Reduces load on Redis significantly. No coordination needed between ID servers — they operate from their own local range.

But the SPOF problem remains. Redis is still the single point of coordination for assigning ranges. And claiming a batch still requires a network hop to Redis — just less frequently.

---

## Why time-sortability is weak here

The counter increments globally across all servers. ID 1001 was issued before ID 1002 — so IDs are sortable by issuance order. That much works.

But there is no timestamp embedded in the ID. If you need to answer "when exactly was this record created?" you cannot extract that from the ID alone. You need a separate `created_at` column.

For many systems, order is enough. For audit logs, time-range queries, and debugging at scale, the lack of an embedded timestamp becomes a real operational gap.

---

## Summary

| Property | Ticket Server |
|---|---|
| Globally unique | ✅ |
| Time-sortable | ⚠️ order only, no embedded timestamp |
| SPOF | ❌ Redis is a single point of failure |
| Coordination-free | ❌ every batch requires a Redis call |
| Storage | ✅ can be 64-bit integer |
