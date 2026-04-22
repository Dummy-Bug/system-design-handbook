## What Is Caching

> [!info] Don't recompute or re-fetch something you've already computed. Store the result somewhere fast and serve it from there next time.

```
Instagram feed = 20+ DB queries = ~200ms minimum

With caching:
  First request  → hits DB, builds feed, stores result in cache
  Every request after → served from cache in ~1ms
  → User sees feed in 80ms
```

Same idea as Dynamic Programming memoization — store expensive results so you don't recompute them. The difference is scale: DP lives in one function, caching lives across requests, servers, and users.

---

## The Cache Hierarchy

> [!info] Three layers — each faster but smaller and less shared than the next.

```mermaid
flowchart LR
    A["🟢 Local In-Process<br/>(Guava, Caffeine)<br/>~nanoseconds<br/>no network hop<br/>per-server only"]
    B["🟡 Distributed Cache<br/>(Redis, Memcached)<br/>~1ms<br/>one network hop<br/>shared across all servers"]
    C["🔴 Database<br/>(disk)<br/>~10ms+<br/>network + disk I/O<br/>source of truth"]

    A -->|slower| B
    B -->|slower| C

    style A fill:#d4edda,stroke:#28a745,color:#000
    style B fill:#fff3cd,stroke:#ffc107,color:#000
    style C fill:#f8d7da,stroke:#dc3545,color:#000
```

---

## What To Cache

> [!info] Ask one question: "If this data is 500ms stale, does anything break?"

```mermaid
flowchart LR
    subgraph DO["✅ Cache It"]
        A["Expensive to compute<br/>feed ranking, search results"]
        B["Read frequently<br/>user profiles, session tokens"]
        C["Okay to be slightly stale<br/>like counts, follower counts"]
        D["Static or rarely changes<br/>images, JS/CSS, config"]
    end

    subgraph DONT["❌ Don't Cache It"]
        E["Real-time data<br/>stock prices, live inventory<br/><i>stale = wrong price / double booking</i>"]
        F["Highly sensitive data<br/>passwords, payment details<br/><i>cache is less secured than DB</i>"]
        G["One-time use data<br/>OTPs, single-use tokens<br/><i>not worth the memory</i>"]
    end

    style DO fill:#d4edda,stroke:#28a745,color:#000
    style DONT fill:#f8d7da,stroke:#dc3545,color:#000
    style A fill:#c3e6cb,stroke:#28a745,color:#000
    style B fill:#c3e6cb,stroke:#28a745,color:#000
    style C fill:#c3e6cb,stroke:#28a745,color:#000
    style D fill:#c3e6cb,stroke:#28a745,color:#000
    style E fill:#f5c6cb,stroke:#dc3545,color:#000
    style F fill:#f5c6cb,stroke:#dc3545,color:#000
    style G fill:#f5c6cb,stroke:#dc3545,color:#000
```

> [!important] Caching is primarily a **read** optimization — same data served many times from cache instead of DB. Writes can be cached too but come with trade-offs.

---

## Local vs Distributed Cache

### Local In-Process Cache

Each app server caches data in its own memory.

```
Request 1 → Server 1  → cache miss → fetches DB → stores locally
Request 2 → Server 1  → cache hit  ✓
Request 3 → Server 47 → cache miss → fetches DB again ✗
```

**The problem:**

```
User updates bio
→ Server 1 cache updated
→ Servers 2–100 still serve stale bio
→ inconsistent across servers
```

**Use for:** static config, feature flags, rarely changing data that's safe to be per-server.

---

### Distributed Cache (Redis / Memcached)

One shared cache, all servers read and write to it.

```
Request 1 → any server → cache miss → fetches DB → stores in Redis
Request 2 → any server → cache hit  ✓  (served from Redis)
Request 3 → any server → cache hit  ✓

User updates bio → invalidate one key in Redis → all servers see fresh data immediately
```

**Use for:** shared user data, sessions, feed results, anything that must be consistent across servers.

---

### Two-Level Caching (L1 + L2)

> [!tip] Best of both worlds — used by Instagram, Twitter, and most large-scale systems.

```
Request comes in
→ Check local cache (L1) — nanoseconds
  → hit  → return immediately
  → miss → check Redis (L2) — ~1ms
    → hit  → store in L1, return
    → miss → hit DB → store in Redis (L2) + local (L1) → return
```

```
L1 (local)    → nanoseconds, per-server, inconsistency risk
L2 (Redis)    → ~1ms, shared, consistent
DB            → ~10ms+, source of truth
```

---

## The Trade-off Summary

```
Local cache        → fastest, but inconsistent across servers
Distributed cache  → consistent, ~1ms overhead, shared
Two-level          → fast + consistent, more complexity
CDN                → for static assets, geographically distributed
```

> [!important] Hit ratio matters — if your cache hit rate is below 90%, you're paying the overhead of checking the cache on every request without enough benefit. Target >90% hit ratio before caching is worth the complexity.
