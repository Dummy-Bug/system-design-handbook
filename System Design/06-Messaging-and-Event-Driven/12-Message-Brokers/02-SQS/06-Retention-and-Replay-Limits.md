# Retention and Replay Limits

> [!info] SQS is a queue for asynchronous processing, not a long-term event archive. Messages remain only for the configured retention period (up to 14 days), then expire.

---

## Why this matters

In ad-click systems, sometimes you must reprocess historical events:

- billing bug discovered last week
- attribution logic changed
- downstream table corruption needs rebuild

If the only copy of events is in SQS and retention has passed, old events are gone.

---

## Retention behavior

Each SQS message has a lifetime bounded by queue retention policy.

```
message sent at T0
retention = 4 days
if unprocessed by T0+4d -> message expires
```

This is correct for task queues, where the goal is timely processing, not indefinite history.

---

## Practical design for ad clicks

Use two tracks:

```
Track 1 (real-time processing):
Click API -> SQS -> workers -> billing/analytics/fraud

Track 2 (durable history):
Click API -> durable raw store (e.g., S3/data lake)
```

SQS handles near-real-time async workload. Durable storage preserves audit/reprocessing capability.

---

## Replay mindset

If replay requirements are part of core business correctness, plan replay architecture explicitly instead of assuming the queue can be rewound forever.

For interviews, this is a strong signal: you understand the difference between "processing pipeline" and "history/audit pipeline."

---

> [!important] What it guarantees
> SQS retention guarantees temporary durable buffering for asynchronous work.

> [!danger] What it doesn't guarantee
> SQS does not provide unlimited historical replay. Expired messages cannot be recovered from the queue.

---

> [!tip] Interview framing
> "I'd use SQS for real-time click processing, but I'd also persist raw click events to durable storage for audits and backfills. Queue retention is finite, so replay needs a separate long-term data path."

