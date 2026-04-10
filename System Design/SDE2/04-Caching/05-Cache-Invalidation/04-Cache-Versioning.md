# Cache Versioning

> [!info] Instead of invalidating a key, change the key itself. Old keys expire naturally via TTL. New keys start fresh. No explicit invalidation needed.

---

## How it works

Rather than updating or deleting an existing cache key, you create a new key with a new version embedded in it. Old keys are simply ignored — they expire on their own.

```
Before update:
  cache key: "user:123:profile:v1"   ← current version pointer
  data: { name: "Alice", bio: "old bio" }

User updates profile:
  → write to DB
  → write "user:123:profile:v2" with new data
  → update "user:123:current-version" = "v2"

Next read:
  → fetch "user:123:current-version" → "v2"
  → fetch "user:123:profile:v2" → new data ✓

Old key:
  → "user:123:profile:v1" still exists but nobody reads it
  → expires quietly via TTL
```

No invalidation call. No delete. The old key just ages out.

---

## Where cache versioning shines — CDN static assets

This pattern is most powerful for CDN-hosted static files. Pushing invalidation to CDN edge servers is slow, expensive, and unreliable:

```
Traditional approach (pushing invalidation):
  Deploy new JS bundle
  → send invalidation request to every CDN edge node worldwide
  → propagates in minutes (not seconds)
  → some edge nodes may be temporarily unreachable → inconsistent
  → CDN charges per invalidation request → expensive at scale
```

Cache versioning sidesteps all of this:

```
Versioned URL approach:
  Old bundle: /static/app.js        → serves old code
  New bundle: /static/app.a3f9c2.js → brand new URL, new cache entry everywhere

  → new URL has never been seen by any CDN edge → no stale data to invalidate
  → old URL expires naturally over time
  → zero propagation delay, zero invalidation cost
```

This is why production JS bundles look like `app.a3f9c2.js` — the content hash in the filename IS the version. Change one byte of code, you get a new hash, a new filename, a new cache entry everywhere.

---

## The hidden cost for DB-backed data — double lookups

For CDN assets, versioning is essentially free. For DB-backed data, it adds a lookup cost:

```
Normal cache read:
  → fetch "user:123:profile" → done (1 cache operation)

Versioned cache read:
  → fetch "user:123:current-version" → "v2"     (1st cache operation)
  → fetch "user:123:profile:v2" → data ✓         (2nd cache operation)
```

Every read now requires two cache round trips instead of one. At 10 million reads/day, that's 20 million cache operations. At high scale, this latency adds up.

> [!danger] Cache versioning for DB-backed data doubles your cache round trips
> For static assets on a CDN — ideal, use it everywhere.
> For DB-backed data — event-driven or write-through is simpler and cheaper. The double lookup adds unnecessary overhead unless you have a specific reason for versioning.

---

## When to use

```
✓ CDN static assets (JS, CSS, images) — the canonical use case
✓ Config or feature flag data with infrequent updates
✓ Any data where you want an audit trail of versions

✗ DB-backed data read millions of times per day — double lookup too costly
✗ Frequently updated data — version numbers accumulate rapidly
```
