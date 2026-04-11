
> [!info] A delay queue holds a message invisibly for a specified duration, then makes it visible to consumers. The consumer never sees it until the delay expires — from the consumer's perspective, the message just appears when it's ready to be processed.


## The problem

Some work doesn't need to happen now — it needs to happen at a specific point in the future. And that future point is different for every entity.

Netflix has 100 million subscribers. Each one has their own billing date. How do you charge each person on exactly the right day?

The naive approach is a cron job:

```
Every minute, cron runs:
SELECT * FROM subscriptions WHERE next_billing_date <= NOW()
→ 100 million rows scanned every minute
→ Most rows return nothing — 99.99% of users aren't due right now
→ Pure waste at scale
```

The problem with cron here isn't that it's scheduled — it's that you're scanning everyone to find the few who are due. You're doing O(all users) work to find O(due today) results.

---

## How a delay queue solves it

Instead of scanning, each user's billing event is a message sitting in the queue with its own timer.

```
User subscribes on Jan 15
→ Drop message in delay queue: { user_id: 9981, event: "charge" }, delay until Feb 15
→ Message is invisible until Feb 15
→ Feb 15 arrives → message becomes visible → billing worker picks it up → charges user
→ Success → drop next message with delay until Mar 15
```

100 million users = 100 million independently timed messages sitting quietly. Each one wakes up exactly when needed. No DB scans, no wasted work.

---

## How the delay actually works

The queue stores a `visible_after` timestamp on each message. Workers only see messages where `visible_after <= now`.

```
Message enqueued at 10:00:00 with 30 minute delay
→ visible_after = 10:30:00
→ Workers poll at 10:15:00 → message doesn't exist for them
→ Workers poll at 10:30:01 → message appears → picked up
```

It's the same visibility mechanism as a normal task queue — except the invisible period is intentional and time-based rather than being a crash-recovery window.

---

## The key rule

> **Per-entity schedule → delay queue. Global schedule → cron job.**

Cron is fine when the schedule is the same for everyone: "run this report every night at midnight." That's one job, one time, everyone affected equally.

When each entity has its own individual schedule, cron forces you to scan all entities to find the ones that are due. That's the wrong tool.

---

## Retry with exponential backoff

A payment fails. But why it failed determines how you retry.

**Technical failure** — network timeout, payment provider temporarily down. The card is fine, the user has money. Retry automatically in minutes — the user doesn't need to know.

```
Payment fails → reason: "provider_unavailable"
→ Drop message in delay queue with 30 min delay, retry_count: 1
→ 30 minutes later → worker picks it up → succeeds ✓
```

**Payment failure** — card declined, insufficient funds. Retrying in minutes is pointless. But retrying over days makes sense — the user might top up their account, get paid, or update their card.

This is exactly what Netflix does:

```
Day 0  → charge fails (insufficient funds) → notify user → schedule retry for Day 1
Day 1  → retry → still failing → schedule retry for Day 3
Day 3  → retry → still failing → schedule retry for Day 7
Day 7  → retry → still failing → schedule retry for Day 14
Day 14 → retry → still failing → suspend account
```

The user consented to the subscription — Netflix keeps trying over days hoping they sort out their payment. Each retry is a delay queue message with a longer delay. The only difference from a technical retry is you also notify the user so they know to act.

---

## WhatsApp disappearing messages

When you enable disappearing messages, every message you send needs to be deleted exactly 7 days later. That's a per-message schedule — each message has its own deletion time.

```
Alice sends message at 10:00 on Jan 1
→ Message stored in DB
→ Drop message in delay queue: { message_id: "msg_abc", action: "delete" }, delay 7 days

Jan 8 at 10:00 → message becomes visible in queue
→ Worker picks it up → deletes message from DB → done
```

100 million messages sent per day = 100 million independently timed deletion events queued up. Each one fires exactly 7 days after its message was sent.

---

## Real use cases

```
Netflix/Spotify autopay        → each user's billing date is different
WhatsApp disappearing messages → delete exactly 7 days after sending
Failed payment retry           → technical: minutes apart, payment: days apart
"Remind me in 3 hours"         → notification scheduled per user request
Order auto-cancellation        → cancel order if not confirmed within 15 minutes
Email verification expiry      → invalidate token exactly 24 hours after sending
```

---

> [!danger] Don't use delay queues for condition-based triggers. "Send notification when driver is 5 minutes away" is not time-based — it's triggered by an ETA condition being met. Delay queues are for purely time-based scheduling only. Condition-based triggers belong in a different pattern (event-driven, polling, or push from the service that detects the condition).

> [!tip] **Interview framing:** "I'd use a delay queue here rather than a cron job — the schedule is per-entity, not global. Each entity gets its own message with its own timer. No DB scanning, scales to any number of users, and each job fires exactly when it's supposed to. For retries, I'd use exponential backoff — each failed attempt enqueues the next retry with a longer delay."
