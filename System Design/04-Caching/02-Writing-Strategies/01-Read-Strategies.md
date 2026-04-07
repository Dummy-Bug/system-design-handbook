# Read Strategies — Cache-Aside and Read-Through

> [!question] A read request comes in. The data might be in cache, or it might not. Who is responsible for fetching it from the DB on a miss — your application, or the cache itself?

---

## Cache-Aside (Lazy Loading)

> [!info] The most common pattern. The application manages the cache manually.

```
Read request arrives
→ check cache
  → HIT  → return from cache ✓
  → MISS → app fetches from DB → app stores in cache → return
```

The application is responsible for both checking the cache and populating it on a miss. Data only gets cached when actually requested — lazy loading.

**What's good:**
```
Only caches what's actually needed  → no wasted memory on cold data
Simple mental model                 → app has full control
Cache failure doesn't break reads   → app can fall back to DB directly
```

**What's bad:**
```
First request always slow           → cold cache miss on every new key
Stale data possible                 → if DB is updated externally and
                                       cache isn't explicitly invalidated,
                                       old value stays until TTL expires
```

**Classic example:** Instagram feed — first load after a cache miss takes the full DB round trip. Every subsequent load is a cache hit and feels instant.

---

## Read-Through

> [!info] The cache sits in front of the DB and handles misses automatically. The application only ever talks to the cache.

```
Read request arrives
→ goes to cache
  → HIT  → cache returns value ✓
  → MISS → CACHE fetches from DB → cache stores value → cache returns
```

The key difference from Cache-Aside: on a miss, it's the **cache** that fetches from the DB and populates itself — not your application code.

**What's different from Cache-Aside:**
```
Cache-Aside    → YOUR APP fetches DB on miss, populates cache
Read-Through   → THE CACHE fetches DB on miss, populates itself
```

**What's good:**
```
Cleaner application code   → app never calls DB directly for reads
Separation of concerns     → caching logic lives in the cache layer, not app
```

**What's bad:**
```
First request still slow         → miss is just handled by cache instead of app
Cache must know how to query DB  → more complex cache configuration
Less flexible                    → harder to apply custom logic on miss
```

**When to use:** systems where you want a clean abstraction between application and database — the app treats the cache as if it were the database.

---

## Comparison

| | Cache-Aside | Read-Through |
|---|---|---|
| Who fetches on miss | Application | Cache itself |
| App complexity | Higher (app handles miss) | Lower (cache handles miss) |
| Cache complexity | Lower | Higher (needs DB connection) |
| Flexibility | High | Lower |
| Use when | App needs control over miss logic | Clean separation is priority |
