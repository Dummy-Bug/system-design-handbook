
> [!info] The edge cases that break the happy path
> The salting mechanism works cleanly when everything is running. These are the scenarios where something goes wrong — a user was offline when the conversation was salted, Redis restarts, or a new app server comes up cold.

---

## Edge case 1 — User was offline during salting

**Scenario:**
- `conv_abc123` was normal (N=1) when Bob went offline
- While Bob was offline, the conversation got hot — N bumped to 4
- Messages were written to `conv_abc123#0` through `conv_abc123#3`
- Bob reconnects

**What happens without the fix:**
Bob's client requests chat history. If the app server handling Bob's request doesn't know about the salting, it queries only `conv_abc123` (N=1) and finds nothing — all messages were written to the salted partitions. Bob sees an empty chat or missing messages.

**The fix:**
The registry lookup happens at the **app server** on every read — not at the client. Bob's client just asks for `conv_abc123` history. The app server:

```
1. GET registry[conv_abc123] → max_N = 4
2. Scatter-gather across conv_abc123#0 through #3
3. Return complete history to Bob
```

Bob being offline during the salting is irrelevant — the registry is the source of truth, and it's always consulted on every read. Bob's client is completely unaware of salting.

---

## Edge case 2 — Redis restarts

**Scenario:**
Redis holding the hot partition registry crashes and restarts.

**What happens:**
- Redis with AOF replays the log and recovers all registry entries
- Recovery time depends on AOF file size — for a registry with millions of entries, replay takes seconds to minutes
- During recovery, app servers get null from registry lookups → treat all conversations as N=1 → queries miss salted partitions

**The fix — warm-up from DynamoDB:**
On Redis restart, before serving traffic, the hot partition service rebuilds the registry from a backup:

```
Option A: DynamoDB backup table
  → On every registry update, also write to a DynamoDB table: conversation_id → max_N
  → On Redis restart: scan DynamoDB backup → repopulate Redis
  → Slower recovery but zero data loss

Option B: AOF replay (no backup needed)
  → Redis replays AOF on restart automatically
  → If AOF is intact, full recovery with no manual intervention
  → AOF corruption is rare but possible
```

For production, use both — AOF as the fast path, DynamoDB backup as the fallback if AOF is corrupted.

**During the recovery window:**
App servers should detect Redis unavailability and fall back to reading from the DynamoDB backup table directly. Slower (~5-10ms instead of ~1ms) but correct.

---

## Edge case 3 — New app server comes up cold

**Scenario:**
A new app server is added to the fleet (auto-scaling during peak traffic). It has no local state — no counters, no cached registry entries.

**What happens:**
- Registry lookups: the new server queries Redis fresh on every request → correct, no issue
- Local WPS counters: start at 0 → the server will under-detect hot conversations until counters build up

**The fix:**
The local WPS counter is a detection mechanism, not a routing mechanism. Under-detection on a new server means it takes slightly longer to detect that a conversation is hot — but the registry already has the correct max_N from when the conversation was first detected as hot by other servers. Writes and reads are routed correctly regardless. The new server's detection will catch up within a few seconds as traffic flows through it.

---

## Edge case 4 — Hot partition service crashes

**Scenario:**
The service that consumes from the Redis Stream and updates the registry goes down.

**What happens:**
- Existing registry entries remain intact — max_N doesn't decrease, existing salting still works
- New hot conversations are not detected — their N stays at 1 even as they exceed 1,000 WPS
- DynamoDB throttling begins for newly hot conversations

**The fix:**
- Run multiple instances of the hot partition service — if one crashes, others continue consuming from the Redis Stream
- Redis Stream retains unprocessed events — when the service recovers, it replays missed events and catches up
- Add alerting on DynamoDB throttle metrics — a sudden spike in `ProvisionedThroughputExceeded` errors signals the hot partition service may be down

---

## Summary

| Edge Case | Risk | Fix |
|---|---|---|
| User offline during salting | Missing messages on reconnect | Registry always consulted on read — client unaware of salting |
| Redis restart | Registry unavailable during recovery | AOF replay (fast) + DynamoDB backup (fallback) |
| New app server cold start | Slow hot detection | Doesn't affect routing — registry in Redis is authoritative |
| Hot partition service crash | New hot conversations not detected | Multiple instances + Redis Stream replay on recovery |
