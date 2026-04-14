
> [!info] A DB shard primary goes down
> With 8 shards each holding a primary and 2 secondaries, losing one primary is not a full system failure. But the impact is precise and worth understanding — reads, writes, and RYOW are all affected differently.

---

## What happens immediately

Shard 3 primary dies. The system detects it via health checks. Leader election begins — one of the two secondaries gets promoted to primary.

This process takes **30-60 seconds** in a typical Postgres setup with Patroni or a similar HA manager. During that window, shard 3 has no writable node.

---

## Reads — mostly unaffected

This is the counterintuitive part. Most people assume losing a primary kills reads too. It doesn't.

Shard 3 had 1 primary + 2 secondaries. The primary died. **The 2 secondaries are still running.**

```
Redirect request → Redis cache → HIT → return 301 ✓ (never touched DB)
Redirect request → Redis cache → MISS → shard 3 needed
                → Primary dead, but secondaries alive
                → Route to secondary → served ✓
```

The vast majority of redirects never hit the DB at all — Redis absorbs 80%+. For the remainder that miss cache and need shard 3, the secondaries are still available and serving reads. No impact on redirects.

---

## Writes — fail for 60 seconds

Creation requests use consistent hashing to route to a specific shard. ~1/8 of all creations route to shard 3.

```
Creation request → consistent hashing → shard 3
→ Must write to primary (writes always go to primary)
→ Primary is dead
→ New primary not yet elected (30-60s window)
→ Write fails → user gets 500 error
```

During the 60-second failover window, ~1/8 of all URL creation requests fail. The other 7/8 shards are unaffected — their primaries are healthy.

Once the new primary is elected, writes to shard 3 resume normally.

---

## RYOW — fails for a precise window of users

Read-Your-Own-Writes uses a `ryow_until` cookie. When the cookie is valid, the app server routes the read to the shard primary — not a secondary — to guarantee the user sees their freshly created URL.

This becomes a problem when the primary dies:

```
T=0s    User creates short URL → written to shard 3 primary
        App server sets cookie: ryow_until = now + 30s

T=10s   Shard 3 primary crashes

T=15s   User clicks their new short URL
        App server reads ryow_until cookie → still valid
        Consistent hashing → shard 3 → go to primary
        Primary is dead → request fails → 500 error
```

The user created their URL, got the short code, and now it doesn't work. From their perspective the system is broken.

But the impact is narrow:

```
Users affected = created a URL on shard 3
                 within the 30-second ryow_until window
                 before the crash
```

After 30 seconds, the cookie expires. Those same requests route to secondaries and work fine. Only the unlucky users in that specific 30-second window on shard 3 experience the failure.

---

## Complete impact summary

```
Redirects (Redis hit)    → unaffected ✓
Redirects (cache miss)   → secondaries serve them ✓
New creations            → ~1/8 fail during 60s failover window
RYOW reads               → fail for users who created in last 30s on shard 3
```

1/8 of the system is partially degraded for ~60 seconds. 7/8 of the system is completely unaffected. This is the value of sharding — failures are contained to a single shard.

---

## After failover completes

```
T=60s   New primary elected on shard 3
T=60s   etcd updated: shard-3/primary → new IP
T=60s   App servers read new topology from etcd
T=60s   Writes to shard 3 resume
T=60s   RYOW routes to new primary correctly
T=60s   Full system restored
```

The only lasting concern: the new primary was a secondary that may have been slightly behind on replication. Any writes that were in-flight to the old primary when it crashed may be lost — this is the replication lag window. In practice, with synchronous replication or small async lag, this is a very small number of writes, potentially zero.

---

> [!danger] Common misconception
> Losing a primary does not kill reads for that shard. Secondaries are still alive and still serve read traffic. The real damage is to writes (no primary to write to) and RYOW (cookie forces read to primary which is dead).

---

> [!tip] Interview framing
> "Shard primary dies → 30-60s failover window. Reads unaffected — secondaries still serve cache misses. Writes fail for ~1/8 of creations during the window — those hashing to that shard. RYOW fails for users who created a URL on that shard within the last 30 seconds — their cookie says go to primary, primary is dead. After failover, etcd updates topology, app servers pick up new primary IP, full recovery."
