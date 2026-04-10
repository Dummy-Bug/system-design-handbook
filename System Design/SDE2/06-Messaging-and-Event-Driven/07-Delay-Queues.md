# Delay Queues

> [!info] A delay queue holds a message invisibly until a specified time has passed, then makes it visible to consumers. The consumer never sees it until the delay expires — from the consumer's perspective the message just appears when it's ready.

---

## The problem

Some work doesn't need to happen immediately — it needs to happen at a specific future time, and that time is different for every entity. A cron job scanning the entire DB every minute to find "what's due now?" is wasteful at scale.

---

## Cron vs Delay Queue

**Bad cron approach for Netflix autopay:**
```
Every minute, cron runs:
→ SELECT * FROM subscriptions WHERE next_billing_date <= NOW()
→ 100 million users → scanning 100 million rows every minute → expensive, slow
```

**Delay queue approach:**
```
User subscribes on Jan 15
→ Drop message in delay queue with delay until Feb 15
→ Feb 15 arrives → message becomes visible → billing service charges the user
→ Success → drop next message with delay until Mar 15
```

No polling, no DB scans. 100 million users = 100 million independently timed messages sitting quietly in the queue. Each one wakes up exactly when it's needed.

---

## The key rule

> **Per-entity schedule → delay queue. Global schedule → cron job.**

Cron jobs are fine for global scheduled tasks — "run this report every night at midnight" affects everyone the same way. But when each entity has its own individual schedule, cron becomes a DB scan nightmare.

---

## Real use cases

```
Netflix/Spotify autopay    → each user's billing date is different, per-entity schedule
WhatsApp disappearing msgs → delete message exactly 7 days after sending
Failed payment retry       → retry after 30 mins, then 1hr, then 2hrs (exponential backoff)
Scheduled notifications    → "remind me about this in 3 hours"
```

> [!danger] Don't use delay queues for condition-based triggers. "Send notification when driver is 5 mins away" is not time-based — it's triggered by an ETA calculation being met. Delay queues are for purely time-based scheduling only, not for waiting until a condition is true.

> [!tip] **Interview framing:** "I'd use a delay queue here rather than a cron job — the schedule is per-entity, not global. Each entity gets its own message with its own timer. No DB polling, scales to any number of users, and each job fires exactly when it's supposed to."
