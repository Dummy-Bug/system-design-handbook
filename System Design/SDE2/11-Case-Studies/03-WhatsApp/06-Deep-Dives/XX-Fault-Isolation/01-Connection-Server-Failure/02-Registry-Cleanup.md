
> [!info] Cleaning up stale registry entries after a connection server dies
> When server 7 dies, the registry still has 1M entries pointing to it. Without cleanup, any message routed to those users hits a dead server. The fix is a reverse mapping — a Redis Set per server — that lets the cleaner bulk-delete all stale entries in one operation.

---

## The stale registry problem

The connection registry maps each user to their current connection server:

```
user:alice   → server7
user:bob     → server7
user:charlie → server7
... (1M entries pointing to server7)
```

Server 7 is dead. These entries are now stale. Any message addressed to these users will be routed to server 7 — which will fail.

The naive fix is to scan the entire registry for entries pointing to server 7. But the registry is keyed by user ID — Redis has no way to find all entries with a specific value without scanning every key. At 500M users, a full scan is expensive and slow.

---

## The reverse mapping

The solution is to maintain a second data structure alongside the forward registry — a reverse mapping from server to its connected users.

```
Forward mapping (for routing):
  user:alice   → server7
  user:bob     → server7
  user:charlie → server7

Reverse mapping (for cleanup):
  server7:users → { alice, bob, charlie, ... }   Redis Set with 1M entries
```

Every time a user connects to server 7, two writes happen:

```
HSET registry user:alice server7         (forward — for routing)
SADD server7:users alice                 (reverse — for cleanup)
```

Every time a user disconnects cleanly from server 7, two deletes happen:

```
HDEL registry user:alice
SREM server7:users alice
```

---

## The cleanup flow on server death

When the monitoring service detects server 7 is down, it triggers the cleaner:

```
Monitoring detects server7 is dead
→ triggers cleaner job

Cleaner:
→ SMEMBERS server7:users          (get all 1M user IDs — O(N) but one call)
→ bulk DEL user:alice, user:bob, ... (remove all forward registry entries)
→ DEL server7:users               (remove the reverse mapping itself)
→ Done
```

No full registry scan needed. The reverse Set gives the cleaner exactly the list it needs.

---

## Timing

The cleaner runs after monitoring detects the failure — typically within 30-60 seconds. During this window, forward registry entries still point to server 7. Messages addressed to those users during this window hit the stale routing fallback described in the next file.

> [!tip] Interview framing
> "I maintain a reverse mapping — a Redis Set per connection server storing all connected user IDs. When a server dies, the cleaner reads that Set and bulk-deletes all forward registry entries. No full scan needed."
