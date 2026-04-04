# Cache Writing & Reading Strategies

## The Core Question

> [!info] When does data get into the cache? When does it get written back to the DB? Six patterns — each with a different answer.

---

## Cache-Aside (Lazy Loading)

> [!info] The most common pattern. App manages the cache manually.

```
Read request
→ check cache
  → hit  → return from cache ✓
  → miss → fetch from DB → store in cache → return
```

App is responsible for populating and managing the cache. Data only gets cached when actually requested.
	
**What's good:**
```
Only caches what's needed     → no wasted memory
Simple mental model           → app controls everything
```

**What's bad:**
```
First request always slow     → cold cache miss on every new key
Stale data possible           → DB updated externally, cache not invalidated
```

**Classic example:** Instagram feed — first load is a cache miss, subsequent loads are fast.

---

## Read-Through

> [!info] Cache sits in front of DB and handles misses automatically. App only talks to the cache.

```
Read request
→ goes to cache
  → hit  → return from cache ✓
  → miss → CACHE fetches from DB → stores → returns
```

**Difference from cache-aside:**
```
Cache-aside    → YOUR APP fetches DB on miss, populates cache
Read-through   → THE CACHE fetches DB on miss, populates itself
```

**What's good:**
```
Cleaner app code    → app never talks directly to DB for reads
Cache always in sync with reads
```

**What's bad:**
```
First request still slow      → miss is just handled by cache instead of app
Cache must know how to talk to DB → more complex cache setup
```

---

## Write-Through

> [!info] Every write goes to cache AND DB synchronously. Both confirmed before returning success.

```
Write request
→ write to cache
→ write to DB
→ both confirmed → return success ✓
```

**What's good:**
```
Cache always consistent with DB     → no stale reads after writes
No data loss risk                   → DB always has the latest
```

**What's bad:**
```
Every write is slower               → must wait for both cache + DB
Write latency doubles               → not suitable for write-heavy systems
```

**Use when:** data is read immediately after being written — user profile updates, settings, preferences.

---

## Write-Back (Write-Behind)

> [!info] Write to cache immediately, sync to DB asynchronously later.

```
Write request
→ write to cache → return success immediately ✓
→ DB write happens in background some time later
```

**What's good:**
```
Extremely fast writes    → user doesn't wait for DB
Great for write-heavy    → absorbs write spikes
```

**What's bad:**
```
Data loss risk           → cache crashes before flushing → writes lost forever
Complexity               → need background flush mechanism
```

**Classic example:** Google Docs — typing feels instant. DB write happens every few seconds in the background. Internet dies mid-typing → you lose a few characters.

---

## Write-Around

> [!info] Write directly to DB, skip the cache entirely.

```
Write request
→ write to DB directly (cache untouched)
→ next read → cache miss → fetches fresh from DB → populates cache
```

**What's good:**
```
Cache not polluted with write-once data    → memory saved for hot reads
```

**What's bad:**
```
Next read after write is always a miss     → slight latency spike after writes
```

**Use when:** write-once data that's rarely read back — logs, audit trails, analytics events. No point caching something you'll never read again.

---

## The Full Picture

```
Cache-aside    → app manages cache, lazy, most common, slight staleness possible
Read-through   → cache manages itself on miss, cleaner app code
Write-through  → write to both synchronously, always consistent, slower writes
Write-back     → write to cache only, fastest writes, risk of data loss
Write-around   → skip cache on write, good for write-once data
```

> [!important] Most systems use **cache-aside for reads** + **write-through or write-around for writes** as the default combination. Write-back only when write speed is critical and some data loss is acceptable.

> [!tip] Proactive cache population strategies (Refresh-Ahead, Cache Warming) are covered in [[04-Population-Strategies]] — after TTL and eviction are explained in [[03-Eviction-Policies]].
