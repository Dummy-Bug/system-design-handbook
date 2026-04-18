
## Rule Storage

Rules define what the rate limiter enforces — which endpoint allows how many requests per window, for which type of user. Getting the storage model right matters because the rate limiter reads rules on every single request.

---

## What a Rule Is

A rule answers one question: for a given user tier hitting a given endpoint, what is the maximum number of requests allowed in what time window?

```
free user   + /login   → 5 requests per 60 seconds
premium user + /login  → 20 requests per 60 seconds
free user   + /search  → 100 requests per 60 seconds
premium user + /search → 500 requests per 60 seconds
```

---

## Why Not Per-User Rules

The first instinct is to store rules per user — User A gets limit 5, User B gets limit 100. But think about the scale:

```
200M users × 50 endpoints = 10 billion rows
```

A configuration table with 10 billion rows. An admin cannot set rules at per-user granularity — it's unmaintainable. And if every user has the same rule anyway, you're storing the same value 200M times.

The right model is **user tiers** — a small set of categories that rules apply to:

```
free, premium, admin, internal-service
```

Every user belongs to one tier. Rules are defined per tier. 50 endpoints × 4 tiers = 200 rows total. Manageable, auditable, changeable.

---

## Schema

```sql
CREATE TABLE rate_limit_rules (
    tier        VARCHAR(50)  NOT NULL,   -- "free", "premium", "admin"
    endpoint    VARCHAR(200) NOT NULL,   -- "/api/v1/login"
    max_limit   INT          NOT NULL,   -- max requests allowed
    window_sec  INT          NOT NULL,   -- window size in seconds
    created_at  TIMESTAMP    NOT NULL,
    updated_at  TIMESTAMP    NOT NULL,
    PRIMARY KEY (tier, endpoint)
);
```

**Why `(tier, endpoint)` as primary key?**

Every rule lookup queries by both tier AND endpoint together:

```sql
SELECT max_limit, window_sec
FROM rate_limit_rules
WHERE tier = 'free' AND endpoint = '/api/v1/login'
```

Making `(tier, endpoint)` the primary key means this query hits a B-tree index directly — O(log n) lookup, effectively instant for 200 rows.

Neither column alone works as a primary key — there are multiple tiers per endpoint and multiple endpoints per tier. The combination is always unique.

---

## How the Rate Limiter Gets the User's Tier

The API gateway extracts the user's tier from the JWT auth token before calling the rate limiter. JWT tokens have a `tier` claim baked in at login time:

```json
{
  "user_id": "abc123",
  "tier": "premium",
  "exp": 1745086800
}
```

The rate limiter receives `tier` as part of the request (alongside `user_id`, `ip_address`, `endpoint`). No extra DB lookup needed to find the user's tier.

If no tier is present in the token — unauthenticated request — default to `free`.

---

## In-Process Cache — No DB Call Per Request

The Rule DB has at most ~200 rows. Rules change rarely — maybe once a week when an admin updates a threshold.

Hitting the Rule DB on every request at 400K QPS would add a DB round trip to every single request path. At even 1ms per DB call, that's 1ms added to every request — a 10% budget hit against the <10ms NFR, just for a config lookup.

The solution: load all rules into a **HashMap in the rate limiter's own process memory** at startup. Refresh on a polling interval — every 30 seconds.

```
Startup:
  SELECT * FROM rate_limit_rules
  → load into HashMap<String, Rule>
    key: "free:/api/v1/login"
    value: {max_limit: 5, window_sec: 60}

Every request:
  rule = hashmap.get(tier + ":" + endpoint)
  → nanosecond lookup, no network call

Every 30 seconds:
  background thread polls DB
  → reloads HashMap with latest rules
```

When an admin updates a rule in the DB, it propagates to all rate limiter instances within one polling cycle — at most 30 seconds. This is completely acceptable. You are not updating rules 400K times per second — you update them once a month. A 30-second propagation delay for a config change is a non-issue.

---

## What the HashMap Looks Like

```
"free:/api/v1/login"     → {max_limit: 5,   window_sec: 60}
"free:/api/v1/search"    → {max_limit: 100, window_sec: 60}
"free:/api/v1/payment"   → {max_limit: 3,   window_sec: 60}
"premium:/api/v1/login"  → {max_limit: 20,  window_sec: 60}
"premium:/api/v1/search" → {max_limit: 500, window_sec: 60}
"premium:/api/v1/payment"→ {max_limit: 10,  window_sec: 60}
```

200 rows × ~100 bytes each = ~20KB in memory. Essentially free.

---

## What Happens If the Rule DB Goes Down

The rate limiter already has all rules loaded in memory. A Rule DB outage has zero impact on the request path — the HashMap continues serving lookups from its last loaded state.

The only impact: rule updates made during the outage won't propagate until the DB recovers and the next poll succeeds. A stale rule for a few minutes is acceptable.

> [!tip] Interview framing
> "Rules are stored in a small DB table keyed on (tier, endpoint) — maybe 200 rows total. The rate limiter loads all rules into an in-process HashMap at startup and refreshes every 30 seconds. Every request lookup is a HashMap.get() — nanoseconds, no network. Rule DB going down has zero impact on the request path since the cache keeps serving. Propagation delay of 30 seconds for rule changes is acceptable."

---

## Summary

```
Schema         : (tier, endpoint) composite PK
                 max_limit + window_sec per rule
                 ~200 rows total

Tier lookup    : JWT token carries tier claim
                 default to "free" if missing

In-process cache: HashMap loaded at startup
                  refreshed every 30 seconds via background poll
                  ~20KB memory, nanosecond lookup

DB outage      : zero impact on request path
                 stale rules served until DB recovers
```
