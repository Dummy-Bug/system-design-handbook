# Long Polling, Batching, and Consumer Scaling

> [!info] At high volume, SQS efficiency depends on how consumers read and delete messages. Long polling reduces empty fetches, batching reduces API calls, and autoscaling keeps queue lag under control.

---

## Why naive polling is expensive

If workers poll too frequently with short polling, many receive calls return no messages.

At scale, this creates:

- unnecessary API cost
- wasted CPU cycles
- noisy autoscaling signals

Long polling fixes this by letting the receive call wait briefly for messages instead of returning immediately.

---

## Long polling

Use receive wait time (up to 20 seconds) so workers spend less time doing empty polls.

```
Worker calls ReceiveMessage(wait=20s)
→ if message exists, returns immediately
→ if queue is briefly empty, waits before returning
```

This is especially useful when traffic is bursty.

---

## Batching

SQS supports receiving/deleting messages in batches (up to 10 per request).

At `100,000` messages:

```
No batching:
~100,000 receive calls + ~100,000 delete calls

Batch size 10:
~10,000 receive calls + ~10,000 delete calls
```

That is a major reduction in API overhead.

---

## Scaling consumers from queue pressure

Producer rate and worker capacity drift over time. Consumer fleet should scale from queue metrics.

Useful signals:

- `ApproximateNumberOfMessagesVisible` (backlog)
- `ApproximateAgeOfOldestMessage` (delay)

Simple policy:

```
if backlog > X or oldest_age > Y:
    scale out workers
if backlog low for sustained window:
    scale in workers
```

Oldest message age is often the most meaningful latency signal for business impact.

---

> [!important] What it guarantees
> These techniques improve efficiency, reduce cost, and control processing lag under burst traffic.

> [!danger] What it doesn't guarantee
> Polling and scaling policies cannot fix non-idempotent consumers or broken downstream dependencies.

---

> [!tip] Interview framing
> "I enable long polling and batch receive/delete to reduce SQS API overhead. Then I autoscale workers based on backlog and oldest-message age so click processing delay stays within SLO during campaign spikes."

