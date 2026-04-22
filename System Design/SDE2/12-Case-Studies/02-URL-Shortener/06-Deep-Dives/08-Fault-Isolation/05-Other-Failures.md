
> [!info] Other failure scenarios — why they're not deep dives
> These scenarios come up in interviews but don't require deep architectural discussion. Knowing *why* they're trivial or out of scope is as important as knowing the answer.

---

## App server crash

App servers are **stateless**. They hold no user data, no session state, no in-memory DB. The only thing they hold is a local batch of pre-generated keys (up to 100) — which are throwaway values anyway.

When an app server crashes:
```
Auto-scaling detects instance unhealthy (failed health check)
→ Spins up replacement instance
→ New instance registers with API Gateway
→ Traffic reroutes to healthy instances in seconds
```

No data loss. No user impact beyond a brief spike in latency while the replacement spins up. This is exactly why stateless design matters — crashes become a non-event.

---

## Malicious URLs

A user creates a short URL pointing to a phishing site, malware download, or scam page. The short URL works correctly — it redirects as designed. But it's being used to cause harm.

This is a **content moderation problem**, not a system design problem. Solutions exist (Google Safe Browsing API, URL scanning services, user reporting) but they involve policy decisions, legal considerations, and moderation workflows that are outside the scope of a system design interview at SDE-2 level.

If an interviewer pushes on this: acknowledge it, say you'd integrate a URL scanning service at creation time, and move on.

---

## Duplicate long URLs

User A creates a short URL for `https://example.com`.
User B creates a short URL for `https://example.com`.

Do they get the same short code or different ones?

This is a **product/business decision**, not an architectural one:
- **Different codes** — simpler, no deduplication logic needed, each user owns their link independently
- **Same code** — saves DB space, but now two users share a link. If one deletes it, the other loses theirs.

For a URL shortener at this scale, different codes is the standard choice. The DB space saved by deduplication is negligible compared to the complexity it adds.

---

## URL expiry

Short URLs don't need to live forever. After a configurable TTL (say 1 year), expired URLs should be cleaned up.

```
Nightly background job:
→ DELETE FROM urls WHERE expires_at < NOW()
→ Run during off-peak hours
→ Freed short codes return to the available pool
```

Simple cron job. No architectural complexity. The only nuance: deleted short codes can be reused — they go back into the KGS pool. Make sure the "used keys" set in KGS is updated when a URL expires so the code can be safely reassigned.

---

> [!tip] Interview framing
> "App server crash is a non-event — stateless, auto-scaling replaces it in seconds. Malicious URLs are a content moderation problem, out of scope. Duplicate long URLs are a product decision — different codes is simpler and standard. URL expiry is a nightly DELETE job during off-peak hours, freed codes return to the KGS pool."
