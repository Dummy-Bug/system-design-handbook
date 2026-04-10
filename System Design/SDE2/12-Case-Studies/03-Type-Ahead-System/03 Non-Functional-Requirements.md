> NFRs describe **how well** the system must perform.
> For type-ahead, the dominant constraint is speed — a suggestion that arrives after the user has finished typing is useless.

---

## Overview

| Requirement | Target |
|---|---|
| **Read latency** | P50 < 20ms, P99 < 50ms |
| **Availability** | 99.99% uptime |
| **Consistency** | Eventual — optimise for availability |
| **Write latency** | Not critical — async |

---

## 1. Latency

### Why Sub-50ms?

Type-ahead lives or dies by speed. The user's finger is on the keyboard. If suggestions arrive after they've already typed the next character, the UI feels broken.

Human perception thresholds:
```
< 100ms  →  feels instant, no perceptible delay
100–300ms →  noticeable but acceptable
> 300ms  →  feels slow, user loses trust in the feature
```

We target well inside the "feels instant" zone:

| Metric | Target | What it means |
|---|---|---|
| **P50** | < 20ms | Half of all users get suggestions in under 20ms — the typical experience |
| **P99** | < 50ms | 99% of requests respond within 50ms — even slow cases feel instant |

> [!info] From your latency notes
> Network round-trip in the same datacenter = ~0.5ms. RAM lookup = nanoseconds. These targets are achievable **only if** we serve suggestions from an in-memory cache (like Redis) — any disk I/O would blow the budget.

### Write Latency — Not Critical

The increment API (recording a completed search) is **asynchronous** — the user doesn't wait for it. We fire it in the background after they submit. No latency target needed.

---

## 2. Availability — 99.99%

### What 99.99% Actually Means

```
99.99% uptime = 0.01% downtime per year
             = ~52 minutes of downtime per year
             = ~4 minutes per month
```

Compare:
| SLA | Downtime per year |
|---|---|
| 99% | ~3.6 days |
| 99.9% | ~8.7 hours |
| 99.99% | ~52 minutes |
| 99.999% | ~5 minutes |

### Why 99.99% for Type-Ahead?

Type-ahead sits in **every Google search box**. If it goes down:
- Every user's search experience degrades immediately
- It's visible to billions of users simultaneously
- Even 1 hour of downtime per year is too much at this scale

The system must keep serving suggestions during:
- Individual cache node failures
- Partial network outages
- Background index rebuilds (updating the suggestion data)

---

## 3. Consistency vs Availability — The Decision

Since we're distributed (high QPS forces multiple nodes), CAP theorem applies. We must choose.

### What Happens if We Choose Availability?

```
Serve from cache + pre-computed snapshots
Write updates processed asynchronously in background
```

| Result | Impact |
|---|---|
| Suggestions always load | ✅ User never sees empty box |
| Ranking may be slightly stale | ⚠️ "earthquake 2026" may take minutes to trend |
| System survives partial failures | ✅ One node down → others still serve |

User experience: **fast, smooth, forgiving.**

### What Happens if We Choose Consistency?

```
Synchronous writes
Strongly consistent reads
Quorum coordination across nodes
```

| Result | Impact |
|---|---|
| Higher latency per request | ❌ Blows our < 50ms P99 target |
| Throughput bottlenecks | ❌ Can't handle millions of QPS |
| Service stalls on partial failures | ❌ One node slow → all reads wait |

User experience: **slow, fragile, janky.**

### The Risk Analysis

| What if we get it wrong? | Worst case | Severity |
|---|---|---|
| **Consistency is wrong** | Suggestions slightly misordered. Trending topic appears 2 minutes late. | 🟡 Low — user barely notices |
| **Availability is wrong** | Suggestions fail to load. Search box feels broken. Billions of users affected. | 🔴 High — catastrophic UX |

> The cost of being slightly stale is near zero.
> The cost of being unavailable is enormous.

**Decision: Optimise for Availability. Accept eventual consistency.**

This is the same choice made by Google, Amazon, and every large-scale autocomplete system.

---

## 4. Read-Heavy Ratio

Type-ahead is one of the most read-heavy systems you'll design:

```
Every keystroke = 1 read request
Every submitted search = 1 write request

A user typing "paris" (5 chars) generates:
  5 read requests  (one per keystroke, after debouncing ~2-3 actual requests)
  1 write request  (on submission)

Read : Write ratio ≈ 50:1 to 100:1
```

This ratio directly shapes the architecture:
- Reads must be served from **in-memory cache** (Redis)
- Writes can be **batched and async** — no need for real-time consistency
- **Replication** should favour read performance (minimise R in R+W>N)
