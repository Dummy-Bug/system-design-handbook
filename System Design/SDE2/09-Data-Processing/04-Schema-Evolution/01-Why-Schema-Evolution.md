
> [!info] Schema evolution is the practice of changing message formats in a way that doesn't break existing producers or consumers. 
> Two rules govern this: backward compatibility (new consumers can read old messages) and forward compatibility (old consumers can read new messages).

## The Problem

In a distributed system, producers and consumers **deploy independently**. You can never guarantee they update at the same time.

Producer adds a new field:
```json
Old: { "order_id": 123, "amount": 50.0 }
New: { "order_id": 123, "amount": 50.0, "currency": "USD" }
```

Consumer hasn't been updated yet. What happens? Depends on how strictly the consumer is written — it might crash, produce wrong results, or silently drop data.

This is the **schema evolution problem** — how do you change message formats without breaking producers or consumers?

---

## Two Compatibility Rules

### Backward Compatibility
**New consumer can read old messages.**

Producer sends old format (no `currency`). Consumer is already updated and expects `currency`.

Consumer must handle missing fields gracefully — use a default value instead of crashing.

```
Old message:  { order_id: 123, amount: 50.0 }
New consumer: reads order_id=123, amount=50.0, currency=DEFAULT ✅
```

### Forward Compatibility
**Old consumer can read new messages.**

Producer sends new format (with `currency`). Consumer is not yet updated.

Consumer must ignore unknown fields gracefully instead of crashing.

```
New message:  { order_id: 123, amount: 50.0, currency: "USD" }
Old consumer: reads order_id=123, amount=50.0, ignores currency ✅
```

---

## Why Rules Aren't Enough

You can document these rules, but you can't rely on every developer remembering to:
- Always set default values for new fields
- Always ignore unknown fields
- Never change field types incompatibly

One mistake and consumers start crashing in production.

The solution: **enforce compatibility automatically** via a Schema Registry — a central gatekeeper that rejects incompatible schema changes before they reach Kafka.

---

## When Schema Evolution Matters Most

- Kafka topics with **long retention** — old messages from months ago must still be readable
- Large teams where producers and consumers are owned by different teams
- Any system where rolling deployments mean old and new versions run simultaneously
