
> [!info] In RabbitMQ, delivering a message to a consumer and deleting it from the queue are two separate steps. A message is only deleted after the consumer explicitly acknowledges it (`ACK`). If processing fails, the consumer rejects it (`NACK`) and decides whether it should be retried or discarded.

---

## Why delivery and deletion are separate

Imagine RabbitMQ delivers an order processing message to a worker:

```
{ 
	order_id: "o_123", 
	user_id: "u_456", 
	total: 99.99, 
	task: "reserve_inventory" 
}
```

If RabbitMQ deleted the message the moment it handed it to the worker, a worker crash mid-processing would lose that order forever. No retry, no recovery — the message is just gone.

So RabbitMQ keeps the message in an **unacked state** during processing. The message is off the queue (no other worker can pick it up), but it hasn't been deleted yet. It's in limbo — waiting for the consumer to report back.

```
Normal queue:   [msg_A] [msg_B] [msg_C]
                   ↓
Worker picks up msg_A
                   ↓
Unacked state:  msg_A held by worker (invisible to others)
Queue:          [msg_B] [msg_C]
                   ↓
Worker finishes → ACK → msg_A deleted
```

If the worker crashes while msg_A is unacked, RabbitMQ detects the lost connection and puts msg_A back on the queue for another worker to pick up.

---

## ACK — processing succeeded

The worker processed the message successfully. Tell RabbitMQ it's safe to delete it.

```java
channel.basicConsume(queueName, false, (consumerTag, delivery) -> {
    try {
        OrderEvent event = parseEvent(delivery.getBody());
        inventoryService.reserveStock(event.getOrderId());

        channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);
        // ↑ message deleted from queue

    } catch (Exception e) {
        // handle failure below
    }
}, consumerTag -> {});
```

The `false` in `basicConsume` means manual acknowledgement — RabbitMQ will not auto-delete on delivery.

---

## NACK with requeue=true — transient failure, try again

The worker failed but the failure is temporary — a downstream database timed out, an external API returned 503. The message itself is fine. Retry it.

```java
channel.basicNack(
    delivery.getEnvelope().getDeliveryTag(),
    false,       // single message
    true         // requeue=true → put it back on the queue
);
```

```
Worker picks up order_123 → DB times out
→ NACK(requeue=true)
→ RabbitMQ puts order_123 back on queue
→ another worker (or same worker) picks it up and retries
```

---

## NACK with requeue=false — permanent failure, stop retrying

The message itself is broken — malformed JSON, unknown event type, a schema version the worker doesn't understand. Requeueing it will just make the same worker fail again, forever. Send it to the dead-letter queue instead.

```java
channel.basicNack(
    delivery.getEnvelope().getDeliveryTag(),
    false,       // single message
    false        // requeue=false → discard or dead-letter
);
```

```
Worker picks up order_123 → JSON is malformed, can't parse
→ NACK(requeue=false)
→ RabbitMQ routes to Dead Letter Queue (if configured)
→ ops team investigates the bad message later
```

---

## The three outcomes

```
ACK                  → done, delete the message

NACK(requeue=true)   → transient failure, put it back, let another worker retry

NACK(requeue=false)  → permanent failure, don't retry, route to DLQ
```

The consumer is responsible for deciding which outcome applies. RabbitMQ just acts on whatever the consumer tells it.

---

> [!danger] If a consumer processes the message successfully but crashes before sending ACK, RabbitMQ will redeliver the message to another worker — which will process it again. This means **duplicate processing is possible**. Your consumers must be idempotent — processing the same message twice should produce the same result as processing it once.

> [!important] `requeue=true` on a broken message creates an infinite loop — the message fails, gets requeued, gets picked up, fails again, forever. Always send genuinely broken messages to the DLQ with `requeue=false`. Use retry queues with delays for transient failures rather than blind requeue. Covered in the retries file.

> [!tip] **Interview framing:** "In RabbitMQ, delivery and deletion are separate. The message stays unacked while the worker processes it — if the worker crashes, RabbitMQ redelivers it. On success the worker ACKs and the message is deleted. On transient failure it NACKs with requeue=true. On permanent failure — bad payload, unknown schema — it NACKs with requeue=false and the message goes to the DLQ. Consumers must be idempotent because a crash after processing but before ACK causes redelivery."
