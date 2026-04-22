
> [!info] SQS, RabbitMQ, and Kafka are all message brokers — they all sit between producers and consumers. But they solve different core problems, and treating them as interchangeable "message queues" leads to wrong design decisions. The real distinction is what each one is at its core: SQS is a managed task queue, RabbitMQ is a routing-first broker, and Kafka is a retained event log.

---

## Why the mental model matters before comparing features

A common mistake in system design interviews is to jump straight to comparing features: "Kafka has partitions, RabbitMQ has exchanges, SQS has visibility timeout." All true. All beside the point.

The choice between them should start at the model level — what is the fundamental contract each one offers? Because if you pick the wrong model, no feature comparison will save you.

---

## SQS — do this job

The mental model for SQS is a to-do list for background jobs.

A producer says: "here is a unit of work, some worker should do it exactly once." SQS holds onto the job, hands it to exactly one worker, hides it from others while the worker is processing, and deletes it once the worker ACKs completion.

```
Order placed
→ SQS: { task: "send_confirmation_email", order_id: 123, user: "alice@example.com" }
→ Email worker picks it up
→ Sends the email
→ ACKs → message deleted permanently
```

The job is gone after it's done. SQS does not keep history. Another service that wants to know "what orders were placed today" can't ask SQS — it's already deleted everything. SQS is a delivery pipe, not a log.

This is fine — it's exactly what you want for background job distribution. The job is done; there's no reason to keep it.

---

## RabbitMQ — route this message

The mental model for RabbitMQ is a post office with a smart sorting facility.

A producer says: "here is a message, route it to the right destination(s)." RabbitMQ has an exchange layer that looks at the message and its routing key, then decides which queues should receive a copy. One message can go to one queue, multiple queues, or zero queues depending on the routing rules you configured.

```
Ad click event arrives at exchange "ad.events"
→ Routing key: "display.fraud_watch"

Bindings:
"display.*"       → analytics.queue        ← Analytics workers get it

"*.fraud_watch"   → fraud.queue            ← Fraud workers get it

Result: two separate queues each receive the message
        Billing workers don't get it (no matching binding)
```

RabbitMQ also deletes messages after consumers ACK them — like SQS. No history, no replay. But the routing flexibility is far richer than SQS.

---

## Kafka — this event happened, write it to history

The mental model for Kafka is a newspaper archive.

A producer says: "this event happened — record it." Kafka appends it to an ordered log on disk and keeps it for 7 days (or 30 days, or forever). Any number of consumer groups can read the log independently, each tracking its own position (offset). Reading a message does not remove it — other readers can still get it.

```
Ad click arrives at Kafka topic "ad-clicks"
→ Appended to the log at offset 10,000,423
→ Billing Service reads from offset 10,000,423 → processes it
→ Fraud Service reads from offset 10,000,423 → processes it  (same event, same offset)
→ New ML Service launched 2 weeks later → reads from offset 0, replays all history

Message is still in the log. Nothing was deleted.
```

This is fundamentally different from SQS and RabbitMQ. The message is not "consumed and destroyed." It's "read by whoever wants to, and kept for the retention period."

---

## The core distinction

```
SQS       → a job that needs to be done once, then gone

RabbitMQ  → a message that needs to reach the right destination(s), then gone

Kafka     → an event that happened, kept in the log for everyone to read
```

| | SQS | RabbitMQ | Kafka |
|---|---|---|---|
| Message deleted after read? | Yes, after ACK | Yes, after ACK | No — retained for N days |
| Multiple consumers read same message? | No — one worker per message | No — one worker per queue per message | Yes — every consumer group reads independently |
| Replay old messages? | No | No | Yes — replay from any offset |
| Routing flexibility? | None (one queue, one consumer) | Rich (exchanges, bindings, wildcards) | None by default (partition by key) |
| Throughput ceiling? | Very high (fully managed) | Medium-high | Extremely high |

> [!danger] The most common mistake: using Kafka for task distribution because "it's more powerful." Kafka is the wrong model for tasks. If you're trying to distribute 10,000 image resize jobs to 50 workers, you want SQS or RabbitMQ. Kafka retains all those jobs in the log forever — you don't want 10,000 old resize jobs hanging around, and each Kafka partition can only be consumed by one worker, limiting parallelism.

> [!tip] **Interview framing:** "The choice starts with what kind of thing I'm sending. If it's a background job that should be done once and gone — SQS or RabbitMQ. If it needs routing to different consumers — RabbitMQ. If it's an event that should be retained and multiple consumer groups should process independently — Kafka. The mental model drives the choice; features are secondary."
