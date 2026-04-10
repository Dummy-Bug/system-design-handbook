# Handling Node Failure

> [!question] A cache node goes down. What happens to the keys it owned? What happens to the traffic?

---

## Without replicas — graceful degradation

With consistent hashing, the keys that belonged to the failed node get routed to the next node clockwise on the ring:

```
Before failure:
  Node A → keys 1–25M
  Node B → keys 25M–50M  ← goes down
  Node C → keys 50M–75M

After failure:
  Node A → keys 1–25M
  Node C → keys 25M–75M  ← absorbs Node B's slice

Immediate effect:
  → keys in the 25M–50M range → cache miss (Node B is gone, keys lost)
  → those requests hit DB
  → DB gradually repopulates Node C with those keys
  → after a few minutes, hit rate recovers

Blast radius:
  → only Node B's keys are affected (~1/N of keyspace)
  → Node A's keys: completely unaffected ✓
  → Node C's keys: completely unaffected ✓
```

Consistent hashing limits the blast radius of a single node failure to just that node's keyspace. Without consistent hashing (naive modulo), all keys would need to remap.

---

## With replicas — seamless failover

If each node has a replica, the replica promotes to primary when the primary fails:

```
Node B dies
→ Redis Sentinel detects failure (~10 seconds)
→ Node B's replica promoted to primary
→ keys in 25M–50M range: still available from the replica ✓
→ no cache miss at all ✓
→ brief (~10-30s) window of reduced write availability while failover completes
```

With replication, a single node failure is invisible to users — reads continue serving from the replica.

---

## The thundering herd on recovery

When a failed node comes back online, it starts empty. The keys that were routed to other nodes during the outage now remap back:

```
Node B recovers → consistent hashing routes its keys back to it
→ Node B is empty → cache miss for every key in 25M–50M range
→ all those requests hit DB simultaneously
→ mini stampede
```

**Fix:** bring the recovered node back gradually, using a warm-up period or shadow mode before taking live traffic.

---

## Summary

```
No replicas + consistent hashing:
  Node failure → ~1/N of keys become misses → DB absorbs that traffic briefly
  Keys repopulate naturally as requests come in

With replicas:
  Node failure → replica promotes → seamless, zero cache misses
  Better but costs double the memory

Recovery:
  Empty node comes back → keys remap back → another wave of misses
  Fix: warm up before returning to live traffic
```
