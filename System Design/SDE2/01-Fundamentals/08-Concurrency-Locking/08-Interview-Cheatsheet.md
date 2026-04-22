# Interview Cheatsheet — Concurrency & Locking

> [!question] When does concurrency come up in an interview?
> The moment two users can touch the same data. Hotel booking, payment processing, inventory management, order placement — any system where simultaneous access matters.

---

## The Core Decision — Pessimistic vs Optimistic

> [!important] Always ask: "How often will two users fight over the same data simultaneously?"

```
High contention  → Pessimistic locking (SELECT FOR UPDATE)
Low contention   → Optimistic locking (version number check)
```

| Scenario | Contention | Strategy |
|---|---|---|
| Hotel booking last room | High | Pessimistic |
| Flash sale last item | High | Pessimistic |
| User updating own profile | Low | Optimistic |
| Editing a personal document | Low | Optimistic |
| Bank transfer | High | Pessimistic |
| Updating personal settings | Low | Optimistic |

---

## Moment 1 — "How do you prevent double booking?"

*"I'd use pessimistic locking — SELECT FOR UPDATE on the room row. Only one transaction can hold the lock at a time. User A locks the row, checks availability, books, releases. User B waits, then reads 0 availability. No double booking possible."*

---

## Moment 2 — "What about deadlocks?"

*"Two prevention strategies — lock ordering: always acquire locks in the same global order so no circular dependency is possible. And timeouts: if a lock isn't acquired within X seconds, give up and retry. Lock ordering prevents deadlocks structurally; timeouts are the safety net."*

---

## Moment 3 — "How does your database handle concurrent reads and writes?"

*"Modern databases use MVCC — Multi-Version Concurrency Control. Each transaction sees a consistent snapshot from when it started. Writers create new versions of rows, readers see the version that existed at transaction start. Readers never block writers, writers never block readers. Consistent paginated reads even if data changes mid-scroll."*

---

## Moment 4 — "What if the operation spans multiple servers?"

*"DB-level locks only work within a single database. For cross-server coordination I'd use a Redis distributed lock — SET NX PX with a TTL. NX makes it atomic — only one server wins. TTL ensures the lock auto-expires if the server crashes. Sticky sessions are the wrong answer — they create a SPOF."*

---

## Moment 5 — "How do you handle retries safely?"

*"Idempotency keys — client generates a UUID and sends it with every request. My service checks if that key was already processed before proceeding. I forward the same key to downstream services like Stripe. Makes retries safe at every hop — network timeouts can't cause duplicate charges or duplicate orders."*

---

## The Full Decision Framework

```
Two users → same data → simultaneously?
  ↓
What's the contention level?
  High → Pessimistic (SELECT FOR UPDATE)
  Low  → Optimistic (version number)
  ↓
Multiple servers involved?
  Yes → Redis distributed lock (SET NX PX + TTL)
  No  → DB-level lock is sufficient
  ↓
Non-DB operation? (payment API, email, job)
  Yes → Redis lock + idempotency key
  ↓
Reads need consistency across paginated calls?
  Yes → MVCC snapshot isolation (databases handle this automatically)
```

---

## The Full Checklist

- [ ] Identified the contention level — justified pessimistic vs optimistic choice
- [ ] Pessimistic: mentioned `SELECT FOR UPDATE`, deadlock prevention (ordering + timeout)
- [ ] Optimistic: mentioned version number, what happens on conflict (retry)
- [ ] Mentioned MVCC for read consistency — readers never block writers
- [ ] For multi-server: Redis distributed lock with TTL
- [ ] For third-party API calls: idempotency keys at every hop
- [ ] Identified which POST operations need idempotency keys

---

## Quick Reference

```
Race condition:     read + write not atomic → wrong result

Pessimistic:        SELECT FOR UPDATE → one at a time → high contention
Optimistic:         version check on write → retry on conflict → low contention
Deadlock fix:       lock ordering + timeout
Read-Write lock:    readers concurrent, writer exclusive
MVCC:               snapshot isolation → nobody blocks anybody

Distributed lock:   SET key value NX PX 5000
                    NX = atomic, PX = TTL (crash safety)
                    Use when: multiple servers, no DB write, third-party APIs

Idempotency:        UUID per operation → server deduplicates
                    Enforce at every hop: client→you→stripe
                    POST operations need it, GET/PUT do not
```
