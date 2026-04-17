
## Redis Node Down

Unlike rate limiter nodes, Redis nodes are not interchangeable. Consistent hashing pins each user to a specific Redis node. When that node goes down, you cannot just reroute to another node — the counter state is gone and the routing logic breaks.

---

## Single Redis Node Down

You have 20 Redis nodes. Node 7 crashes. User A is hashed to Node 7.

Rate Limiter Node 1 tries to reach Redis Node 7 for User A's counter — connection refused.

**The rate limiter has two choices:**

**Fail closed** — block all requests for users mapped to Node 7.
```
1/20 of users = 5% of all users get 429 for every request
Full outage for 5% of users until Node 7 recovers
```

**Fail open** — allow all requests for users mapped to Node 7 through.
```
5% of users temporarily unprotected
Downstream services handle the extra load
Brief unprotected window until Node 7 recovers
```

Fail open is the correct choice. The rate limiter is an AP system — availability over consistency. Blocking 5% of all users is a visible outage. Allowing 5% of users through unprotected for a brief window is an acceptable tradeoff. Downstream services have circuit breakers and concurrency limits as a second line of defense.

---

## What Happens to Counters on Recovery

Redis stores everything in RAM. When Node 7 recovers (or restarts), all counters that were on it are gone — wiped. 

User A's first request after Node 7 comes back:
```
Rate limiter looks up User A → hashed to Node 7
Redis Node 7 is back → key doesn't exist → returns 0
Counter starts fresh from zero
User A gets a clean slate
```

This is a fresh start — User A effectively gets a new rate limit window. They may get a few extra requests through during the brief gap. This is acceptable — losing rate limit counters temporarily is not a data integrity problem. The worst case is a user gets slightly more requests than intended for one window period.

> [!important] No replication for rate limit counters
> Adding Redis replication to preserve counters across node failures adds latency to every single request at 400K QPS. The cost is permanent and constant. The benefit (preventing a fresh start for 5% of users during rare node failures) is minimal. Do not replicate rate limit counter state.

---

## Entire Redis Cluster Down

More extreme scenario — all 20 Redis nodes unreachable simultaneously. Usually caused by a network partition between the rate limiter servers and the Redis cluster, not all nodes crashing at once.

When the rate limiter can't reach any Redis node:

```
Layer 2 (Redis) : completely unreachable → fail open for all Redis checks
Layer 1 (local) : still works — in-process memory unaffected
```

The two-layer local counter architecture saves the system here:

```
Each rate limiter node enforces: local_limit = global_limit / num_nodes

With 10 rate limiter nodes and global limit = 5:
  local_limit = 5 / 10 = 1 per node

A user can get through at most:
  1 request × 10 nodes = 5 requests total
  = exactly the global limit, distributed across nodes
```

During a full Redis cluster outage, the system is not completely unprotected. Each rate limiter node independently enforces its local limit. The global enforcement is approximate (depends on even traffic distribution) but not zero. A sophisticated attacker targeting one specific rate limiter node could get through `local_limit` requests per window from that node — but that's a small number and the cluster outage scenario is already extraordinary.

---

## Summary

```
Single node down:
  Detection     : connection refused on Redis call
  Response      : fail open for affected users (~5%)
  Counter loss  : fresh start on node recovery
  User impact   : brief unprotected window for 5% of users

Full cluster down:
  Response      : fail open for Redis checks
                  local counters enforce local_limit per node
                  approximate global enforcement maintained
  User impact   : degraded but not zero protection

Design choice  : no replication of counter state
                 cost (latency on every request) > benefit (preventing fresh start)
```
