# Distributed Locking

## Why Database Locks Aren't Enough

Database-level locks (pessimistic, optimistic) work within a single database. But modern systems run **multiple application servers** — each with their own memory, no shared state.

```
User double-clicks "Place Order"
  Request 1 → hits Server 1
  Request 2 → hits Server 2 (0.5 seconds later)

Server 1 checks DB → no order yet → proceeds
Server 2 checks DB → no order yet → proceeds (before Server 1 finished writing)

Result: duplicate order created
```

Each server's local lock is invisible to the other. You need a **shared lock** that all servers can see.

---

## Redis Distributed Lock

Redis is the standard solution — it's fast, single-threaded (atomic operations guaranteed), and shared across all servers.

```
Server 1 receives request → SET lock:order:user123 "locked" NX PX 5000
Server 2 receives request → SET lock:order:user123 "locked" NX PX 5000

Redis is single-threaded → only one SET wins

Server 1 wins → lock acquired → places order → DEL lock:order:user123
Server 2 loses → lock exists → fails fast → return "order already processing"
```

**The Redis command:**
```
SET key value NX PX milliseconds
```

- `NX` — only set if **N**ot e**X**ists (atomic check + set in one operation)
- `PX 5000` — auto-expire after 5000 milliseconds

---

## Why TTL (Expiry) Is Critical

> [!danger] Without expiry — a crashed server holds the lock forever

```
Server 1 acquires lock
Server 1 crashes mid-operation
Lock never released
No other server can ever acquire it
System permanently stuck
```

With TTL:
```
Server 1 acquires lock with PX 5000 (5 second expiry)
Server 1 crashes
Lock auto-expires after 5 seconds
Server 2 can now acquire lock → retries operation safely
```

TTL = **crash safety built into the lock.**

---

## Why Not Sticky Sessions?

Sticky sessions pin each user to a specific server — same user always hits same server, no cross-server conflicts.

> [!warning] Sticky sessions = SPOF

```
User pinned to Server 1
Server 1 dies
User's session gone
All in-flight requests for that user → lost
System must reroute user → session state lost
```

Redis distributed lock is better — servers remain stateless, any server handles any request, Redis lock coordinates access.

---

## When to Use Distributed Locking vs DB Locking

| Scenario | Use |
|---|---|
| Single DB, operation touches DB rows | DB-level lock (`SELECT FOR UPDATE`) |
| Multiple databases or sharded DB | Redis distributed lock |
| Operation has NO database write | Redis distributed lock |

**The third case is the most important:**

```
Operations with no DB write that still need coordination:
  → Sending an email notification (don't send twice)
  → Calling Stripe payment API (don't charge twice)
  → Triggering a background job (don't run twice)
  → Calling any third-party API (idempotency)

No database row to lock → DB lock useless → Redis lock required
```

---

> [!tip] Interview framing
> *"For cross-server coordination I'd use a Redis distributed lock — SET NX PX with a TTL for crash safety. DB-level locks only work within a single database. For operations that don't touch the DB at all — payment API calls, email sending — Redis is the only option to prevent duplicate execution across servers."*
