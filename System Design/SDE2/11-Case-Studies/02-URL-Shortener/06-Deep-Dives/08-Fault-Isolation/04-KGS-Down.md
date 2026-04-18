
> [!info] KGS crashes — the key pool starts draining
> The Key Generation Service is a background worker that keeps the Redis key pool topped up. If it crashes, the pool doesn't refill. App servers keep consuming keys at 1k/sec. At some point the pool hits zero and creation falls back to live random generation — which at high DB fill rate means expensive collision retries.

---

## How fast does the pool drain?

The pool holds 100 million keys at full capacity. At 1k creations/sec:

```
100,000,000 keys / 1,000 per sec = 100,000 seconds ≈ 27 hours
```

27 hours of runway from a full pool. But KGS might crash when the pool is already partially depleted. Say 5 million keys remain:

```
5,000,000 / 1,000 = 5,000 seconds ≈ 83 minutes
```

83 minutes until pool exhaustion. Not a day — 83 minutes. This is a tight window if nobody is watching.

---

## What happens when the pool hits zero

App servers call `LPOP` and get nothing back. They fall back to live random short code generation — the original approach:

```
Pool empty
→ App server generates random 6-char base62 code
→ Checks DB for collision
→ If collision → regenerate → retry
→ If no collision → INSERT
```

The system stays operational. Creation requests still work. But the collision cost depends entirely on how full the DB is at that point.

```
DB at 10M URLs (early days):  collision rate ~0.018% → almost no retries → fine
DB at 40B URLs (years later): collision rate ~71%    → ~3 retries per creation → noticeable
DB at 53B URLs (near full):   collision rate ~94.6%  → ~18 retries per creation → expensive
```

The fallback degrades gracefully early on and catastrophically late. This is why the fix is not "improve the fallback" — it's "never let the pool run out in the first place."

---

## The fix — two layers of protection

You don't want to discover the pool is empty when creations start failing. You want to know while there's still plenty of runway to recover.

**Layer 1 — auto-recovery:**

```
Pool drops below 20M keys
→ Watcher triggers
→ KGS process auto-restarts (systemd, Kubernetes restartPolicy)
→ KGS resumes sequential generation from where it left off
→ Pool refills
→ Nobody notices
```

20M keys at 1k/sec = 20,000 seconds ≈ 5.5 hours of runway. Plenty of time for auto-restart to kick in and refill before the pool gets anywhere near zero.

**Layer 2 — human alert:**

```
Pool drops below 10M keys
→ Page on-call engineer
→ Something went wrong with auto-restart
→ Human investigates and fixes
```

10M keys = 10,000 seconds ≈ 2.7 hours of runway. Still enough time for a human to respond before pool exhaustion.

---

## Why monitor pool size, not just KGS health

The naive approach is to monitor whether the KGS process is running. That misses a whole class of failures:

```
KGS process is running ✓
KGS is silently failing to connect to Redis ✗
KGS is generating keys but LPUSH is failing ✗
KGS is running but in an infinite retry loop ✗
```

In all of these cases, the process health check says "healthy" but the pool is not being refilled.

Monitoring **pool size** catches all of these. It doesn't matter why the pool isn't being refilled — if the number is dropping and not recovering, something is wrong. This pattern is called a **dead man's switch** — you monitor the output, not the process. If the output stops arriving, the alarm fires regardless of what the process reports about itself.

---

## KGS resuming after crash

KGS generates keys sequentially — 000000, 000001, 000002... It stores the last generated code in a durable location (a DB row or a file). On restart, it reads that value and continues from where it stopped.

```
KGS crashes at: "a3f9k2"
KGS restarts
→ Reads last checkpoint: "a3f9k2"
→ Continues: "a3f9k3", "a3f9k4", ...
```

No keys are duplicated. No keys are skipped. The sequential space is walked exactly once regardless of how many times KGS restarts.

---

> [!tip] Interview framing
> "KGS crashes → pool drains at 1k/sec. At 5M keys remaining: 5M/1k = 5000 seconds = 83 minutes until exhaustion. Fix: two-layer monitoring. Pool below 20M → auto-restart KGS, 5.5 hours of runway. Pool below 10M → page on-call, 2.7 hours of runway. Monitor pool size, not process health — dead man's switch pattern catches silent failures. KGS resumes from checkpoint on restart, no duplicates."
