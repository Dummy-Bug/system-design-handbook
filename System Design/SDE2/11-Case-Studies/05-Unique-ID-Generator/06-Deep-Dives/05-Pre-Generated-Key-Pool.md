# Pre-Generated Key Pool — KGS

## The idea

Instead of generating IDs on demand at request time, generate millions of IDs in advance and store them in a pool. When a caller needs an ID, just hand one out from the pool — no generation logic at request time, no counter arithmetic, no coordination.

Think of it like a parking ticket machine that pre-prints 10,000 tickets before the day starts. When a car arrives, just hand one out.

---

## The architecture

A dedicated **Key Generation Service (KGS)** pre-generates IDs and stores them in a database with two tables:

```
unused_keys table  ← IDs ready to be handed out
used_keys table    ← IDs already issued
```

When a caller requests an ID:
1. KGS picks one key from `unused_keys`
2. Moves it to `used_keys`
3. Returns it to the caller

Since the move happens atomically, no two callers ever receive the same key.

---

## The collision problem with multiple KGS machines

One KGS machine is a SPOF. You need multiple. But two KGS machines reading from `unused_keys` simultaneously can both grab the same key.

The naive fix is a lock on the table — only one machine reads at a time. But at high throughput, the lock becomes a bottleneck.

**The smarter fix — batch loading into memory:**

Each KGS machine claims a batch of keys upfront and loads them into its own local memory:

```
KGS-1 claims keys 1–1000     → serves from local memory, no DB calls
KGS-2 claims keys 1001–2000  → serves from local memory, no DB calls
KGS-3 claims keys 2001–3000  → serves from local memory, no DB calls
```

Once a machine has its batch in memory, it serves IDs locally with zero coordination — no DB calls, no locks, no network hops. Extremely fast.

---

## What happens when a KGS machine crashes?

If KGS-1 crashes with 500 keys still in memory (never issued), those 500 keys are lost. IDs 501–1000 will never be given out — there will be a gap in the ID sequence.

Is this a problem?

Our FRs are: globally unique, time-sortable, space-efficient. We never said IDs must be **contiguous**. Gaps are acceptable. The remaining IDs are still unique and still in order. The crash is survivable with no correctness issue.

> [!info] Gaps are fine — missing IDs are not data loss
> A gap in the ID sequence means some numbers were never issued. It does not mean any data was lost or corrupted. The records that were created all have unique, valid IDs. The unused numbers simply cease to exist.

---

## The time-sortability problem

Pre-generated keys are sequential integers — 1, 2, 3, 4... They are monotonically increasing, so they sort correctly by issuance order. ID 1001 was issued before ID 1002.

But just like the Ticket Server, there is no timestamp embedded in the key. You know the *order* but not the *time*. "When exactly was ID 5000 created?" cannot be answered from the ID alone — you need a separate `created_at` column.

For systems that only need ordering (most CRUD operations), this is fine. For systems that need time-range queries ("give me all records created between 2pm and 3pm") without a separate timestamp column, this approach falls short.

---

## Summary

| Property | Pre-Generated Key Pool |
|---|---|
| Globally unique | ✅ |
| Time-sortable | ⚠️ order only, no embedded timestamp |
| SPOF | ✅ multiple KGS machines with batches |
| Coordination-free at request time | ✅ served from local memory |
| Crash survivable | ✅ gaps are acceptable |
| Storage | ✅ can be 64-bit integer |
| Embedded timestamp | ❌ |
