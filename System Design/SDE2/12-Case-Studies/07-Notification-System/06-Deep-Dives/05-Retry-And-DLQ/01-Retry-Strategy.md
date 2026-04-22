# Retry Strategy — Retry and DLQ

## The Problem

Your push worker sends a notification to APNs and gets back a 500 error. APNs is temporarily overloaded. The notification has not been delivered. What do you do?

The naive answer is "retry immediately." But if APNs is overloaded and you hammer it with retries from thousands of worker instances simultaneously, you make the overload worse. You need a smarter retry strategy.

---

## Exponential Backoff with Jitter

**Exponential backoff** means each retry waits longer than the previous one — giving the external service time to recover before you hit it again.

```
Attempt 1 (immediate) → fails → wait 1s
Attempt 2             → fails → wait 2s
Attempt 3             → fails → wait 4s
Attempt 4 (final)     → fails → give up
```

But exponential backoff alone has a problem — if 10,000 worker instances all fail at the same time and all wait exactly 1 second before retrying, they all hammer APNs simultaneously again. This is the **thundering herd problem**.

**Jitter** adds a small random offset to each backoff window:

```
Attempt 1 → fails → wait 1s + random(0, 0.5s)   → e.g. 1.3s
Attempt 2 → fails → wait 2s + random(0, 1s)     → e.g. 2.7s
Attempt 3 → fails → wait 4s + random(0, 2s)     → e.g. 5.1s
```

Now retries from different worker instances are spread across a time window instead of arriving simultaneously. APNs sees a gradual ramp-up instead of a spike.

---

## Why Not Rewind the Kafka Offset

The instinct is: if some notifications in a batch fail, don't commit the Kafka offset — let Kafka replay the batch. But this breaks everything.

Kafka offsets are per-partition, not per-message. If you don't commit the offset, Kafka replays the **entire batch** from the last committed offset — including the notifications that already succeeded. Those users get duplicate notifications.

```
Batch of 1000 messages:
- Messages 1-800: delivered successfully ✓
- Messages 801-1000: failed ✗

Don't commit offset → Kafka replays messages 1-1000
→ Users 1-800 get duplicate notifications
→ Messages 801-1000 get retried ✓ but at the cost of 800 duplicates ✗
```

You cannot use Kafka offset rewind for selective retry. You need a different mechanism for failed messages — the DLQ.

---

## Retry Schedule

3 retries is standard practice — enough to handle transient failures (APNs hiccup, network blip) without retrying indefinitely on permanent failures (invalid device token, deactivated account).

```
Total attempts: 4 (1 original + 3 retries)
Total wait time before giving up: 1 + 2 + 4 = 7 seconds (plus jitter)
```

> [!info] Circuit Breaker
> If APNs is returning 500s consistently across many workers, individual retries won't help — APNs is down. A circuit breaker detects sustained failure rates and stops sending requests to APNs entirely for a cooldown period (say 30 seconds). This prevents workers from wasting cycles on guaranteed failures and gives APNs time to recover. After the cooldown, the circuit breaker allows a small number of test requests — if they succeed, it closes and normal traffic resumes.
