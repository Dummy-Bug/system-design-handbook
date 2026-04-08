# Advanced Kafka — Interview Cheatsheet

---

## 1. Retention & Compaction at a Glance

| Feature | Logic | Best for... |
|---|---|---|
| **Time-based** | Delete after N days | Ad clicks, logs, events (The "History") |
| **Size-based** | Delete if > N GB | Protecting server disk from crashing |
| **Log Compaction** | Keep latest value per key | Wallet balances, user profiles (The "Source of Truth") |

---

## 2. Exactly-Once Breakdown

```
At-Most-Once   →  Commit before processing. Risk: data loss.
At-Least-Once  →  Commit after processing. Risk: duplicates. (Default)
Exactly-Once   →  Idempotence + Transactions. Risk: performance overhead.
```

---

## 3. The "No-DB" Pattern (Kafka as State Store)

When asked how to handle 1M requests/sec for a Billing Service:

**1. The Storage:** Use a **Compacted Topic** as the "Permanent Database."
**2. The Cache:** Load the compacted topic into a **RAM HashMap** at startup.
**3. The Read:** Query the HashMap (nanoseconds) instead of a Database (milliseconds).
**4. The Write:** Use **Kafka Transactions** to update the Balance topic and commit the offset in one atomic step.

---

## 4. Key Interview Trade-offs (L4/L5 level)

**Trade-off: Retention vs. Storage Costs**
> "I'd use a 30-day retention for raw events. If we need to re-train an ML model, we have the history. If we need to save money, we can move older data to S3 (Cold Storage) and delete it from Kafka."

**Trade-off: Idempotent Consumer vs. Transactions**
> "Kafka Transactions are beautiful but heavy. For a standard billing app, I'd prefer the **Idempotent Consumer** pattern (SQL unique constraint). It's simpler to maintain, works with any database, and achieves the same correctness with less overhead."

**Trade-off: Compaction vs. Replay Time**
> "Log Compaction keeps the log small, but if you have 100 million unique users, the 'Replay' at startup will still be slow. I'd pair this with **Checkpointing**—saving the RAM state to a fast local disk (like RocksDB) so we don't have to read from Offset 0 every time."

---

## 5. One-Line Summary for the Recruiter

> "I use **Compacted Topics** to maintain long-term state without a traditional DB, and I combine **Idempotent Producers** with **Transactional Consumers** to ensure that even in a high-scale ad pipeline, we never double-charge a customer."

> [!tip] **L5 Nuance:** Mention that Exactly-Once only works *within* the Kafka ecosystem. If you are calling an external 3rd-party API (like Stripe or an Email service), Kafka cannot "roll back" that external call. You *must* make the external call itself idempotent.
