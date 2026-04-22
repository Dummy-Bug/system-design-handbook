
> [!info] The core idea
> A distributed lock in etcd is just a key. The problem — if the server holding the lock crashes, the key is never deleted and the lock is held forever. etcd solves this with leases — every lock has a TTL and auto-expires unless the holder keeps renewing it. Crash = no more renewals = lock auto-released.

---

## The stuck lock problem

Server 3 acquires a lock to run a background job:

```
Server 3 → writes /locks/job = "server-3"
Server 3 crashes mid-job
→ /locks/job still exists
→ no other server can ever acquire it
→ job never runs again
```

Without a TTL, the lock is held forever. The only fix is a human manually deleting the key — not acceptable in production.

---

## Leases — TTL on keys

When Server 3 acquires the lock, it attaches a **TTL (time-to-live)** — say 10 seconds. etcd automatically deletes the key after 10 seconds unless Server 3 renews it.

Server 3 keeps renewing the lease every few seconds while it is alive and working:

```
T=0s  → Server 3 acquires /locks/job with TTL=10s
T=3s  → Server 3 renews → TTL resets to 10s
T=6s  → Server 3 renews → TTL resets to 10s
T=9s  → Server 3 crashes ← no more renewals
T=19s → TTL expires → etcd deletes /locks/job automatically
T=19s → Server 7 acquires lock → picks up the job ✓
```

No human intervention. No stuck locks. The system heals itself.

---

## What about a slow server — not crashed, just slow?

If Server 3 is alive but its network is congested, its renewal message may arrive late. If the TTL expires before the renewal gets through — etcd deletes the key and another server acquires the lock.

Now both Server 3 and Server 7 think they hold the lock. This is the **false expiry** problem — and it is handled by fencing tokens, covered in the next file.

> [!important] TTL is a trade-off
> Too short a TTL → false expiries on slow networks, two servers think they hold the lock
> Too long a TTL → when a server genuinely crashes, the lock stays stuck for too long before another server can pick it up
> Typical production TTL: 10–30 seconds depending on how quickly you need failover
