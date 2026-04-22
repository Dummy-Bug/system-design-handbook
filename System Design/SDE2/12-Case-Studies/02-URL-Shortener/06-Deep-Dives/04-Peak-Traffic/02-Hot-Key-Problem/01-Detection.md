
> [!info] The problem
> Consistent hashing maps each short code to one Redis node. When a URL goes viral, all reads for that short code hammer the same node. Before you can fix the hot key problem, you need to detect which keys are hot — in real time, at 100k+ reads/sec.

---

## What "hot key" means

A hot key is a cache key that receives disproportionately high read traffic — enough to overwhelm the single Redis node it lives on.

```
Normal key: a3f8c2 → 500 reads/sec    → fine
Hot key:    x7k2p9 → 800,000 reads/sec → one Redis node at its limit
```

The challenge: you don't know in advance which URL will go viral. Detection must happen automatically at runtime.

---

## Option 1 — G-Counter (CRDT)

A G-Counter is a distributed counter using CRDT (Conflict-free Replicated Data Type). Each app server maintains its own count per key. Counts are periodically merged across all servers — the total is the sum of all per-node counts.

```
App server 1: x7k2p9 → 50,000 reads
App server 2: x7k2p9 → 45,000 reads
App server 3: x7k2p9 → 40,000 reads
Merged total:          135,000 reads → HOT
```

**Why this is overkill:**
- Requires a merge protocol across all app servers — extra network traffic
- Eventual consistency means detection lags — you see the hot key after the fact
- Complex to implement and operate
- You don't need a globally precise count — you just need "is this key hot right now?" Local approximation is good enough

G-Counter is the right tool for distributed counters that need accuracy across nodes. It is the wrong tool for hot key detection where speed and simplicity matter more than precision.

---

## Option 2 — Redis keyspace notifications

Redis can be configured to publish an event every time a key is accessed. App servers subscribe to these events and count accesses per key.

```
Redis config: notify-keyspace-events KEA
Every GET x7k2p9 → Redis publishes event to subscribers
App servers count → x7k2p9 has been accessed 800k times → HOT
```

**Why this is complex:**
- Requires Redis configuration changes
- Every key access generates a pub/sub event — at 800k reads/sec, you're generating 800k events/sec just for monitoring
- This monitoring traffic competes with actual read traffic on the same Redis instance
- You're adding load to the thing you're trying to protect

Keyspace notifications work for low-traffic monitoring use cases. At URL shortener scale, the monitoring overhead is itself a problem.

---

## Option 3 — Local app server counter (the right approach)

Each app server maintains an in-memory counter for every key it reads. No Redis calls, no network traffic, no coordination.

```
App server local counters (sliding 1-second window):
  x7k2p9 → 85,000 reads/sec   ← exceeds threshold → HOT
  a3f8c2 → 200 reads/sec      → normal
  q9m3r7 → 50 reads/sec       → normal
```

If the counter for any key exceeds a threshold — say 50k reads/sec on a single app server — that server flags the key as hot and triggers promotion.

**Why this works:**
- Zero extra infrastructure — just an in-memory hash map
- Zero extra network calls — counting happens locally on every read
- Fast detection — you know within 1 second
- Approximate is fine — you don't need the exact global count, just "is this key being hammered on my server?"

If a key is getting 800k reads/sec across 10 app servers, each server sees ~80k reads/sec. That's well above any reasonable threshold. Every server detects it independently and triggers promotion.

---

## The verdict

```
G-Counter           → distributed precision, overkill, complex, lags
Keyspace notifications → Redis built-in, but adds monitoring load to the hot node
Local counter       → zero infra, zero overhead, fast, good enough ✓
```

Local app server counter wins. Simple beats complex when simple is sufficient.

---

**Next:** Once a hot key is detected, how do you fix it? Two approaches — local app server cache and Redis key replication.
