# Task Queue

> [!info] A task queue is a pattern for distributing background jobs to a pool of workers. Each job gets picked up by exactly one worker — no duplicates, no two workers doing the same job. The producer drops a job and walks away. Workers drain the queue at their own pace.

---

## What a task queue is NOT

Before the mechanics — the most important thing to understand is what separates a task queue from pub/sub.

A task queue is for **"do this job"**. One job, one worker does it, it's done.

Pub/sub is for **"this thing happened"**. Multiple independent services all need to know about it.

```
Task queue:  order placed → ONE worker picks it up → other services never see it
Pub/Sub:     order placed → ALL subscribers get a copy → each reacts independently
```

Use the wrong one and you either duplicate work (pub/sub for jobs) or silently drop events (task queue for broadcasts).

---

## Real examples

```
Send welcome email after signup        ← one job, one worker sends it
Resize profile photo after upload      ← one job, one worker resizes it
Generate PDF invoice after purchase    ← one job, one worker generates it
Run fraud check after transaction      ← one job, one worker checks it
Transcode video after upload           ← one job, one worker transcodes it
```

All the same shape: do this one thing in the background, exactly once.

---

## How exactly-once is guaranteed — Visibility Timeout

You have 10,000 photo resize jobs and 50 workers all pulling from the same queue. How does the queue make sure two workers don't grab the same photo?

When a worker picks up a job, the queue doesn't delete it immediately. Instead it makes it **invisible** to all other workers for a set time window — say 30 seconds.

```
Worker A requests a job
→ Queue gives photo_1 to Worker A AND hides it from everyone else (one atomic operation)
→ Worker B requests a job → only sees photo_2, photo_3... photo_1 doesn't exist for it
→ Worker A finishes → sends ACK → queue deletes photo_1 permanently
```

The "give and hide" is one **atomic operation** — there is no gap where another worker could sneak in and grab the same job.

> [!important] The queue only deletes a job after receiving an ACK. Until then, it's hidden — not gone. This is what makes crash recovery possible.

---

## What if a worker crashes mid-job?

```
Worker A picks photo_1 → visibility timeout starts (30 seconds)
Worker A crashes at 15 seconds → never sends ACK
30 seconds pass → photo_1 becomes visible again
Worker B picks photo_1 → processes it → ACKs → deleted
```

The job doesn't get lost. It reappears after the timeout and another worker picks it up automatically.

> [!danger] The visibility timeout must be longer than the expected job duration. If resizing takes 45 seconds but your timeout is 30 seconds, the queue assumes the worker crashed and hands the job to a second worker — while the first is still working on it. Now two workers resize the same photo. Set timeout to at least 2x expected job duration.

---

## What if the ACK gets lost?

The worker finishes the job. Sends an ACK. The network drops it. The queue never receives it.

```
Worker A processes photo_1 → done ✓
Worker A sends ACK → network drops it → queue never receives it
Visibility timeout expires → photo_1 becomes visible again
Worker B picks photo_1 → processes it again
```

photo_1 got resized twice. This is **at-least-once delivery** — the queue guarantees the job gets done, but it might get done more than once.

For resizing a photo this is harmless. For charging a credit card it's catastrophic.

The fix is an **idempotent consumer** — before doing the work, check if it was already done. If yes, skip it and ACK. That's covered in Delivery Guarantees.
