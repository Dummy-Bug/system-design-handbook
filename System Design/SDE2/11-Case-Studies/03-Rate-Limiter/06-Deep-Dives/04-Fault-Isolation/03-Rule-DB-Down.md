
## Rule DB Down

The Rule DB is the only persistent store in the rate limiter system. But unlike Redis, it is not in the critical request path. The rate limiter never queries the Rule DB during request processing.

---

## Why Rule DB Down Has Zero Request Path Impact

Every rate limiter instance loads all rules into an in-process HashMap at startup and refreshes every 30 seconds via a background polling thread. The request path only ever touches this in-memory HashMap — never the DB directly.

```
Request arrives:
  rule = hashmap.get("free:/api/v1/login")  ← nanosecond, in-process
  → no network call, no DB involved

Background thread (every 30 seconds):
  SELECT * FROM rate_limit_rules
  → reload HashMap
  → Rule DB being down only affects this background thread
```

When the Rule DB goes down, the background refresh fails silently. The HashMap continues serving the last successfully loaded rules. Request processing is completely unaffected.

---

## Stale Rules During Outage

The only impact of a Rule DB outage: rule changes made during the outage don't propagate. If an admin updates `/login` from 5 req/min to 3 req/min while the DB is down, rate limiter instances keep enforcing 5 req/min until:

1. Rule DB recovers
2. Next background poll succeeds (within 30 seconds of recovery)
3. HashMaps refresh across all instances

A stale rule for the duration of the outage plus 30 seconds is completely acceptable. Rules change rarely — maybe once a week. A brief enforcement of an outdated threshold has negligible real-world impact.

---

## Recovery

When the Rule DB comes back up:
```
Background thread: next poll attempt succeeds
HashMap reloaded with latest rules
All rate limiter instances converge within one polling cycle (30 seconds)
```

No manual intervention needed. Recovery is automatic.

---

## Summary

```
Impact on requests : zero — HashMap serves all rule lookups
Impact on updates  : rule changes don't propagate during outage
Stale rules        : enforced until DB recovery + next poll
Recovery           : automatic within 30 seconds of DB recovery
Design principle   : DB is config storage only, never in hot path
```
