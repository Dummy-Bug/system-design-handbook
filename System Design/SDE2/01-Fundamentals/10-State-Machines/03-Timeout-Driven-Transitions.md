# Timeout-Driven Transitions

## Not All Transitions Are User-Triggered

> [!info] Some transitions happen because time passes — not because a user or system event triggered them.

Hotel reservation example:

```
HOLD → CONFIRMED    triggered by: user pays within 10 minutes
HOLD → EXPIRED      triggered by: nobody does anything, 10 minutes pass
```

Nobody clicks "expire this reservation." Time does it. You need a mechanism to detect and apply these transitions automatically.

---

## Option 1 — Background Job (Scheduler)

A scheduled job runs periodically, scans for entities that should have transitioned, and updates them:

```sql
-- runs every minute
UPDATE reservations
SET status = 'EXPIRED'
WHERE status = 'HOLD'
AND created_at < NOW() - INTERVAL '10 minutes'
```

```
Job runs at 10:01 → scans → expires all HOLDs older than 10 mins
Job runs at 10:02 → scans → expires any new ones
...
```

**What's good:**
- Status in DB is always accurate (within job frequency)
- Easy to query — `SELECT * FROM reservations WHERE status = 'HOLD'` is reliable
- Simple to reason about and debug

**The downside:**
- Lag — if job runs every minute, a reservation could stay in HOLD for up to 11 minutes
- Needs infra — a scheduler (cron job, Kubernetes CronJob, Quartz, etc.)

> [!tip] This is the default SDE-2 answer. Clean, visible, operationally sound.

---

## Option 2 — Lazy Expiry (Check At Read Time)

Don't update proactively. When the reservation is fetched, check if it should have expired:

```
fetch reservation → status = HOLD, created_at = 15 mins ago
→ 15 > 10 → treat as EXPIRED
→ optionally write EXPIRED to DB now (lazy update)
→ return EXPIRED to caller
```

**What's good:**
- No background job needed
- No lag from the user's perspective — they immediately see the correct state

**Where it breaks:**

```sql
-- This query returns wrong results with lazy expiry
SELECT * FROM reservations WHERE status = 'HOLD'

→ returns reservations that should be EXPIRED
  but haven't been read yet (so DB still says HOLD)
```

Any query that filters by status becomes unreliable. Reporting, admin tools, downstream systems all see stale state.

> [!warning] Lazy expiry only works when you access entities exclusively by ID — never by status. Most real systems query by status, so lazy expiry breaks them.

---

## Comparison

```
                    Background Job          Lazy Expiry
DB accuracy         always accurate         stale until read
Query by status     reliable                unreliable
Infrastructure      needs scheduler         none
Lag                 job frequency (e.g. 1m) none from user's view
Complexity          low                     low, but hidden bugs
```

---

## The SDE-3 Approach — Delayed Events

> [!tip] Just know this exists. You don't need to design it for SDE-2.

```
On HOLD creation → publish a "check-expiry" event to a message queue
                   with a 10-minute delay

Queue delivers event at T+10min → consumer checks status
  still HOLD → transition to EXPIRED
  already CONFIRMED → ignore
```

Precise timing. No polling. Scales well. But adds message queue infrastructure and complexity.

---

## Default Answer For Interviews

Background job. Say:

> "On reservation creation, I store a `created_at` timestamp. A background job runs every minute scanning for HOLD reservations older than 10 minutes and transitions them to EXPIRED. This keeps the DB status accurate and makes queries by status reliable."
