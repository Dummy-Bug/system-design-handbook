# Delay Queues in SQS

> [!info] SQS supports delay queues via the `DelaySeconds` parameter — but the maximum is **900 seconds (15 minutes)**. For delays beyond that, you need a different pattern: DB + scheduler → SQS workers.

---

## How SQS delay works

When sending a message, you set `DelaySeconds`. SQS hides the message from all consumers until that many seconds have passed.

```java
SendMessageRequest request = SendMessageRequest.builder()
    .queueUrl(queueUrl)
    .messageBody("{\"user_id\": \"9981\", \"action\": \"charge\"}")
    .delaySeconds(900)  // hide for 15 minutes — the maximum SQS allows
    .build();

sqsClient.sendMessage(request);
```

Works perfectly for short delays: order cancellation windows, brief technical retries, email grace periods.

---

## The 15-minute hard cap

SQS `DelaySeconds` maxes out at **900 seconds**. You cannot delay a message for hours, days, or weeks. The API rejects anything above 900.

This means Netflix's multi-day payment retry or WhatsApp's 7-day deletion cannot be implemented with SQS delay queues alone.

---

## The DB + scheduler pattern — for delays beyond 15 minutes

Store the scheduled job in a database. A scheduler queries for due jobs and enqueues them into SQS when the time comes.

```
Job needs to run in 7 days:
→ INSERT INTO scheduled_jobs (job_id, payload, run_at, status)
  VALUES ('job_abc', '{"user_id": 9981}', NOW() + 7 days, 'pending')

Scheduler runs every minute:
→ SELECT * FROM scheduled_jobs WHERE run_at <= NOW() AND status = 'pending'
→ For each due job: SendMessage to SQS (no delay needed — it's already due)
→ Mark status = 'enqueued'

SQS worker picks it up → processes → done
```

The `scheduled_jobs` table has an index on `run_at`. The scheduler only touches rows that are actually due — O(due now), not O(all users).

---

## Why not just process in the scheduler directly — why SQS at all?

This is the right question to ask. If the scheduler already finds due jobs, why enqueue into SQS? Why not just process them inside the scheduler?

```
Scheduler alone:
→ finds 10,000 due billing jobs at midnight
→ processes all 10,000 inside one process, sequentially
→ takes 20 minutes
→ next scheduler tick fires while previous is still running
→ if it crashes at job 5,000 — which ones ran? which didn't?
→ no retry, no fault tolerance, no parallelism
```

The scheduler is just an alarm clock. It's good at one thing: noticing when a job is due. It's bad at doing work at scale.

SQS + workers handle the actual execution:

```
Scheduler + SQS workers:
→ finds 10,000 due jobs
→ enqueues 10,000 messages into SQS (just API calls, done in seconds)
→ 500 workers drain in parallel
→ done in seconds, not 20 minutes
→ worker crashes? visibility timeout → message reappears → another worker retries
→ retry count, DLQ, idempotency — all built in
```

```
Scheduler = finds due jobs, enqueues them (alarm clock)
SQS       = distributes jobs to workers reliably (delivery layer)
Workers   = execute the actual work in parallel (processing layer)
```

Each layer does one thing. Mixing scheduling and execution into one process is fine for 50 jobs. It breaks at Netflix scale.

---

## Netflix retry — correct implementation

```
Day 0 → charge fails
→ INSERT scheduled_jobs: run_at = now + 1 day, retry_count = 1
→ notify user

Day 1 → scheduler sees the job → enqueues into SQS
→ worker retries → still failing
→ INSERT scheduled_jobs: run_at = now + 2 days, retry_count = 2

Day 3 → enqueued → retry → failing → schedule Day 7
Day 7 → enqueued → retry → failing → schedule Day 14
Day 14 → enqueued → retry → failing → suspend account
```

DB handles multi-day timing. SQS handles reliable distributed delivery. Workers handle execution.

---

## Summary

```
Delay < 15 minutes  →  SQS DelaySeconds directly
                        (order cancel window, brief retry, email grace period)

Delay > 15 minutes  →  DB + scheduler → enqueue into SQS when due
                        (Netflix retry, WhatsApp 7-day delete, monthly billing)

Never               →  scheduler processing jobs directly at scale
                        (no parallelism, no retry, single point of failure)
```

> [!tip] **Interview framing:** "SQS delay queues cap at 15 minutes. For short delays I'd use DelaySeconds directly. For multi-day schedules I'd store jobs in a scheduled_jobs table with a run_at index, have a scheduler enqueue due jobs into SQS every minute, and let workers process in parallel. The scheduler is just the alarm clock — SQS and workers handle the reliable distributed execution."
