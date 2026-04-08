# SQS Standard vs FIFO

> [!info] SQS offers two queue types. Standard prioritizes throughput and scalability. FIFO prioritizes ordering and deduplication guarantees.

---

## Why this choice matters

In ad systems, not every message has the same correctness requirement.

- Click analytics ingestion can usually tolerate small reordering.
- Billing state transitions often cannot tolerate out-of-order processing.

If you choose the wrong queue type, you either lose correctness or lose throughput headroom.

---

## Standard queue

Standard is the default for high-scale pipelines.

What you get:

- Very high throughput
- At-least-once delivery
- Best-effort ordering (not strict)

Ad-click example:

```
click_1001 and click_1002 are sent in that order
workers may process click_1002 before click_1001
```

For aggregate analytics counters, this is usually acceptable.

---

## FIFO queue

FIFO is for strict processing order and duplicate suppression behavior.

What you get:

- First-in-first-out order within a message group
- Deduplication support
- Lower throughput compared to Standard

Example where FIFO helps:

```
campaign_77_budget_updates:
1. set_budget=500
2. set_budget=300

Out-of-order processing would produce wrong final state.
FIFO preserves intended sequence.
```

---

## Practical decision rule

Use Standard when:

- Event volume is huge
- Slight reordering is acceptable
- You already design consumers to be idempotent

Use FIFO when:

- Order is part of correctness
- You need strict sequencing per logical key
- Lower throughput is acceptable

---

> [!important] What it guarantees
> Standard gives scalable asynchronous delivery with at-least-once behavior. FIFO gives ordered processing within message groups.

> [!danger] What it doesn't guarantee
> FIFO does not mean infinite ordered throughput for all keys globally. Throughput is bounded and tied to ordering constraints.

---

> [!tip] Interview framing
> "For click ingestion I'd pick Standard SQS for scale. For ordered state transitions like campaign budget updates, I'd use FIFO with a message group per campaign to preserve sequence."

