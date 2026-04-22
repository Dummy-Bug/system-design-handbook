# MVCC — Multi-Version Concurrency Control

## The Problem It Solves

Even Read-Write locks have a limitation — readers and writers block each other. Writer must wait for readers to finish. Readers must wait for writer to finish.

MVCC removes this entirely.

> [!info] MVCC = readers see a consistent snapshot from when their transaction started. Writers create new versions. Old versions stay until nobody needs them. Nobody blocks anybody.

---

## How It Works — Snapshot Isolation

When a transaction starts, the database takes note of the current moment. Every read within that transaction sees data **as it was at that moment** — regardless of what writers do afterwards.

```
Row versions in database:
  balance = 1000  (version created at transaction T=100)
  balance = 1500  (version created at transaction T=102, after B's write)

User A starts transaction at T=101
  → sees balance = 1000  (the snapshot at T=101)
  → User B writes balance = 1500 at T=102
  → User A still sees balance = 1000  (snapshot doesn't change mid-transaction)
  → User A finishes transaction

Next time User A starts a new transaction at T=103
  → now sees balance = 1500  (latest version)
```

Writer created a new version. Reader kept seeing the old version. **No blocking. No dirty reads.**

---

## The Paginated API Example

> [!example] This is where snapshot isolation really matters

```
User A starts reading article list → snapshot taken at T=200
  API call 1 → Page 1 returned (from T=200 snapshot)
  User scrolls...
  Editor deletes article #47 at T=201
  API call 2 → Page 2 returned (still from T=200 snapshot)
               article #47 still visible ✓ — consistent pagination

User A finishes reading

Next refresh → new transaction at T=202
  → article #47 now gone ✓
```

Without snapshot isolation — article #47 could disappear mid-scroll, page counts shift, user sees duplicate or missing articles.

---

## MVCC vs Optimistic Locking — The Key Difference

> [!important] Same concept (versions) but solves different problems

| | Optimistic Locking | MVCC |
|---|---|---|
| **Protects** | Writers from conflicting writes | Readers from seeing inconsistent data |
| **On conflict** | Fail → retry | Never fails — shows consistent snapshot |
| **Mechanism** | Check version before writing | Show version from transaction start |

```
Optimistic: read v=4 → write → check still v=4? No → fail → retry
MVCC:       started at v=4 → always show v=4 → no failure, no retry
```

Both use versions. Optimistic locking protects **writes**. MVCC protects **reads**.

Modern databases like PostgreSQL use **both together** — MVCC for consistent reads, optimistic/pessimistic locking for write conflicts.

---

## Old Version Cleanup

MVCC keeps multiple versions of every row. Old versions accumulate over time. They need cleanup.

```
PostgreSQL: background process called VACUUM
  → finds row versions no active transaction needs anymore
  → deletes them → reclaims disk space

If VACUUM doesn't run → table bloat → disk fills up → performance degrades
```

You don't need to manage this manually — databases handle it automatically. Know it exists for interviews.

---

> [!tip] Interview framing
> *"I'd rely on MVCC for read consistency — each transaction sees a snapshot from when it started, so readers never block writers and writers never block readers. Paginated reads stay consistent even if data changes mid-scroll. For write conflicts I'd add optimistic or pessimistic locking on top depending on contention level."*
