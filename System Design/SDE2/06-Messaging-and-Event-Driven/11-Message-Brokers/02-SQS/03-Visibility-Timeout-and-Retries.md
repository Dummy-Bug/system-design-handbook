# Visibility Timeout and Retries

> [!info] When a consumer receives an SQS message, that message becomes temporarily invisible to other consumers. If processing succeeds, the consumer deletes it. If not, the message becomes visible again and can be retried.

---

## The failure problem

Suppose a worker pulls an ad click message and starts processing billing updates. Midway, the worker crashes.

Without a lease/invisibility mechanism:

- Another worker could process the same message at the same time
- Or the message could be lost if failure handling is weak

SQS solves this with visibility timeout.

---

## How visibility timeout works

```
1. Worker A receives click_id=abc123
2. SQS hides abc123 from other workers for 60s
3. Worker A processes message
4a. Success -> Worker A calls DeleteMessage -> message removed
4b. Failure/crash -> no delete
5. After 60s timeout, abc123 becomes visible again
6. Worker B can receive and retry
```

This gives safe handoff with retry on failure.

---

## Choosing timeout correctly

Timeout must be longer than normal processing time.

If processing takes ~20 seconds and timeout is 10 seconds:

```
Worker A is still working
timeout expires
Worker B receives same message
duplicate concurrent processing starts
```

A practical baseline is to set timeout comfortably above expected processing time and extend when needed for long tasks.

---

## Retries are normal behavior

In distributed systems, worker restarts, network glitches, and transient dependency failures are expected.

SQS retry behavior is not an edge case. It is the normal path that keeps the system available under failure.

---

> [!important] What it guarantees
> SQS prevents immediate concurrent delivery of the same message during the visibility window and enables automatic redelivery after failure.

> [!danger] What it doesn't guarantee
> Visibility timeout does not eliminate duplicates. Messages can still be delivered again if delete fails or processing exceeds timeout.

---

> [!tip] Interview framing
> "I rely on visibility timeout as a lease. A worker gets exclusive processing time, and if it crashes, the message reappears for retry. I tune timeout based on p95/p99 task duration and keep consumers idempotent for safety."

