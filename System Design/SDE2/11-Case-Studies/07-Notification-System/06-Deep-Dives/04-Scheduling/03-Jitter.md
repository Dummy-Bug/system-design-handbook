# Jitter — Scheduling

## The Hot Partition Problem

Even with minute buckets, a large marketing campaign creates a spike. Instagram wants to send a flash sale notification to 10M users at exactly 9:00am. All 10M notifications are written with `scheduled_at = 2026-04-19 09:00:00`. They all land in the same minute bucket `2026-04-19-09-00`.

At 9:00:00, the scheduler finds all 10M due notifications and dumps them into Kafka simultaneously. Your workers go from processing a normal sustained load to 10M messages in one second — a 10× spike with zero ramp-up time. Workers get overwhelmed, latency spikes, and some notifications start missing their delivery window.

The fix is **jitter** — deliberately spreading notifications that were scheduled for the same time across a wider window.

---

## Option 1 — Jitter at Intake

When the app server receives a scheduled notification, it adds a small random offset to `scheduled_at` before storing in the Scheduler DB.

**Example:** Instagram schedules 10M notifications for 9:00:00. The app server adds a random offset between 0 and 60 seconds for each:

```
User 1  → stored as 9:00:03
User 2  → stored as 9:00:17
User 3  → stored as 9:00:44
User 4  → stored as 9:00:52
...
User 10M → spread evenly across 9:00:00 to 9:01:00
```

Instead of 10M notifications firing at 9:00:00 exactly, they spread across 60 seconds — ~167K/sec instead of 10M in one second. Workers handle it smoothly with no spike.

**How it's implemented:**
```
stored_scheduled_at = requested_scheduled_at + random(0, 60 seconds)
```

Simple — the jitter is baked in at write time. The scheduler needs no special logic.

---

## Option 2 — Jitter at Dispatch

The scheduler reads all due notifications at 9:00:00 but instead of publishing all 10M to Kafka at once, it staggers the publish rate — say 200K messages/sec — spreading the 10M over 50 seconds.

**Example:**
```
9:00:00 → scheduler publishes 200K to Kafka
9:00:01 → scheduler publishes 200K to Kafka
9:00:02 → scheduler publishes 200K to Kafka
...
9:00:49 → scheduler publishes last 200K to Kafka
```

Workers see a smooth 200K/sec instead of a 10M spike.

---

## Why Option 1 (Intake Jitter) Wins

Option 2 requires the scheduler to track how many messages it has published, maintain a rate limiter, and handle failures mid-dispatch. If the scheduler crashes at 9:00:25, it needs to know it already published 5M messages and resume from there — complex state management.

Option 1 is stateless — the jitter is stored in the DB. The scheduler just reads what's due and publishes it all. No rate limiting logic, no crash recovery complexity.

> [!info] Option 1 vs Option 2
> Option 1 (intake jitter): jitter baked into stored_scheduled_at at write time. Scheduler is stateless — just publish what's due. Simple.
> Option 2 (dispatch jitter): scheduler rate-limits its own publish rate. Requires state, crash recovery, rate limiting logic. Complex.
> Option 1 wins on simplicity.

---

## The Tradeoff — Time-Sensitive Notifications Can't Have Jitter

Option 1 has one problem: the user requested delivery at exactly 9:00:00, but with jitter they get it at 9:00:44. For most notifications that's fine — a birthday message 44 seconds late is imperceptible.

But not all notifications are equal:

- **Birthday notification delayed 44 seconds** → completely fine, user doesn't notice
- **"Happy New Year" campaign** → fine, 60 seconds late is acceptable
- **Bank fraud alert: "Your card was used in Lagos"** → NOT fine. 44 seconds late could mean the user doesn't block the card in time
- **OTP: "Your login code is 482917"** → NOT fine. OTPs expire in 30-60 seconds — jitter could make it arrive after it's already expired

---

## Priority-Based Jitter Rules

The solution is to apply jitter based on notification priority:

| Notification Type | Jitter | Reason |
|---|---|---|
| Marketing campaigns | ± 60 seconds | Bulk sends, timing not critical |
| Birthday / reminders | ± 30 seconds | Approximate timing acceptable |
| Transactional (receipts) | ± 10 seconds | Minor delay tolerable |
| Bank alerts / fraud | No jitter | Time-critical, seconds matter |
| OTPs | No jitter | Expire quickly, cannot be delayed |

The app server checks the notification type at intake and applies jitter only to low-priority types. High-priority notifications are stored with their exact `scheduled_at` unchanged.

> [!danger] Applying jitter to OTPs is a bug
> An OTP that expires in 30 seconds and arrives 44 seconds late is useless. Always exempt time-sensitive notifications from jitter. The priority check at intake must be explicit — defaulting to jitter for all notifications will silently break OTP delivery.
