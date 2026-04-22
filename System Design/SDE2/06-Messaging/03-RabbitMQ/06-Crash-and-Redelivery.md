
> [!info] If a consumer crashes before sending ACK, RabbitMQ redelivers the message to another worker. The work may have already happened — RabbitMQ has no way to know. This creates duplicate processing risk. Your consumers must be idempotent.

---

## The crash scenario

An inventory worker picks up an order and starts reserving stock:

```
1. RabbitMQ delivers order_123 to Worker A
2. Worker A calls inventoryService.reserveStock("order_123")  ← succeeds
3. Worker A crashes (OOM, network drop, pod eviction)
4. Worker A never sends ACK
```

From Worker A's point of view, the work is done — stock is reserved.
From RabbitMQ's point of view, the message is still unacknowledged. It was never confirmed.

RabbitMQ sees the connection drop and redelivers order_123 to Worker B.

```
Worker A: [reserve_stock] → [CRASH] ← no ACK sent
                                   ↓
                    RabbitMQ detects connection drop
                                   ↓
Worker B: [reserve_stock] ← receives order_123 again
```

Worker B now double-reserves stock for the same order.

---

## The redelivered flag

RabbitMQ marks redelivered messages with a flag you can inspect:

```java
channel.basicConsume(queueName, false, (consumerTag, delivery) -> {
    boolean isRedeliver = delivery.getEnvelope().isRedeliver();
    String orderId = parseOrderId(delivery.getBody());

    if (isRedeliver) {
        // This message was delivered before — the previous consumer may have
        // already processed it. Check before acting.
        log.warn("Redelivered message for order {}", orderId);
    }

    processOrder(orderId, isRedeliver);
    channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);

}, consumerTag -> {});
```

`isRedeliver = true` means at least one previous consumer received this message and didn't ACK it.

> [!important] `isRedeliver = false` does NOT mean the message has never been processed. It only means this specific delivery attempt is the first one. The previous worker may have processed it, crashed, and had its connection closed — RabbitMQ then redelivers it with `isRedeliver = true` to the next worker. But there are edge cases (broker restarts, queue migrations) where `isRedeliver` can be `false` even on a message that was processed before.

---

## Making the consumer idempotent

The safest pattern: check whether the order was already processed before doing the work.

```java
void processOrder(String orderId) {
    // Check if this order was already handled
    if (processedOrdersStore.contains(orderId)) {
        log.info("Order {} already processed, skipping", orderId);
        return;  // ACK will still be sent — message is safe to delete
    }

    // Do the actual work
    inventoryService.reserveStock(orderId);

    // Mark as processed AFTER the work succeeds
    processedOrdersStore.add(orderId);
}
```

The `processedOrdersStore` can be Redis, a database table, or any durable store. The key is that it survives worker crashes.

```
First delivery:
  processedOrdersStore.contains("order_123") → false
  → inventoryService.reserveStock("order_123") ← runs
  → processedOrdersStore.add("order_123")
  → ACK sent

Worker crashes, message redelivered:
  processedOrdersStore.contains("order_123") → true
  → skip, ACK sent, no duplicate work
```

---

## The atomic write problem

One more edge: what if the worker reserves stock, then crashes before marking it processed?

```
1. inventoryService.reserveStock("order_123")  ← succeeds
2. processedOrdersStore.add("order_123")       ← CRASH here
3. ACK never sent
4. Redelivery to Worker B
5. processedOrdersStore.contains("order_123")  → false (never written)
6. inventoryService.reserveStock("order_123")  ← runs again
```

To prevent this, write to the processed store in the same transaction as the business operation where possible — or use database-level upserts that are safe to run twice:

```java
// Instead of a plain insert that fails on duplicate:
inventoryService.reserveStockIdempotent(orderId);
// Internal: INSERT INTO reservations ... ON CONFLICT (order_id) DO NOTHING
```

An upsert makes the operation inherently safe to run twice — the second run is a no-op.

---

> [!danger] `isRedeliver = true` is a hint, not a guarantee. Don't use it as your only protection against duplicates. A message can be processed, the processed-store write can fail, and the message redelivered with `isRedeliver = true` — and your check would still pass incorrectly if the store never recorded it. Always make the business operation itself idempotent.

> [!tip] **Interview framing:** "Consumer crashes before ACK → RabbitMQ redelivers to another worker — the first worker may have already done the work. I check `isRedeliver` as a signal but the real protection is idempotency: check a durable processed-orders store before acting, or use database upserts that are safe to run twice. This is the at-least-once delivery trade-off — RabbitMQ guarantees the message won't be lost, but can't guarantee it won't be processed more than once."
