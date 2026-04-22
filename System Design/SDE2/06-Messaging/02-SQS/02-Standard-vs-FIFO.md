# Standard vs FIFO Queue

> [!info] SQS has two queue types. Standard gives you maximum throughput but doesn't guarantee message order. FIFO gives you strict ordering and deduplication but at a lower throughput ceiling. Choosing between them comes down to one question: does order matter for correctness?

---

## Standard Queue

Standard is the default. AWS delivers messages as fast as possible — throughput is effectively unlimited. The trade-off is that delivery order is not guaranteed.

```
Producer sends: job_1, job_2, job_3

Workers may process in any order:
→ Worker A gets job_3
→ Worker B gets job_1
→ Worker C gets job_2
```

This is fine for most background jobs. When you're resizing 10,000 photos, does it matter if photo_500 gets processed before photo_1? No. The result is the same either way.

**Standard queue characteristics:**
- Unlimited throughput
- At-least-once delivery (rare duplicates possible)
- Best-effort ordering (not guaranteed)

---

## FIFO Queue

FIFO (First In, First Out) guarantees that messages are processed in exactly the order they were sent. It also deduplicates — if the same message is sent twice within a 5-minute window, SQS delivers it only once.

The trade-off: throughput is capped at 300 messages/sec per message group (3,000 with batching).

---

## When order matters — the Amazon order state machine

An Amazon order must go through states in a strict sequence:

```
placed → confirmed → shipped → delivered
```

Each state transition is an event dropped into the queue:

```
{ order_id: "o_123", event: "order_placed"    }
{ order_id: "o_123", event: "order_confirmed" }
{ order_id: "o_123", event: "order_shipped"   }
{ order_id: "o_123", event: "order_delivered" }
```

If "order_shipped" gets processed before "order_confirmed" — the DB shows the order as shipped before it was ever confirmed. The customer gets a shipping notification for an order that might have been cancelled. The warehouse ships something it shouldn't have.

Order is not a nice-to-have here — it is correctness.

---

## Message Groups — how FIFO enforces order end-to-end

Here's the subtle problem. Even with a FIFO queue, if you have two consumers C1 and C2:

```
C1 picks "order_confirmed"  → processing slowly
C2 picks "order_shipped"    → finishes fast → writes to DB first

DB sees: order shipped before confirmed → wrong state
```

The queue delivered them in order, but processing happened out of order. FIFO at the queue level alone isn't enough.

This is where **message group IDs** solve the problem.

You tag each message with a group ID. SQS guarantees that messages within the same group go to exactly one consumer at a time — no two consumers can process messages from the same group simultaneously. SQS locks the group until the current message is ACKed.

```
C1 picks "order_confirmed" (group: o_123) → SQS locks group o_123
C2 tries to pick next → o_123 is locked → C2 gets a message from o_456 instead
C1 ACKs "order_confirmed" → SQS unlocks o_123 → "order_shipped" becomes available
```

Now ordering is guaranteed end-to-end — not just in the queue, but in processing and DB writes too.

Different orders each have their own group and process in parallel:

```
order o_123: placed → confirmed → shipped → delivered  (strict order)
order o_456: placed → confirmed → shipped → delivered  (strict order, in parallel)
order o_789: placed → confirmed → shipped → delivered  (strict order, in parallel)
```

---

## Java code — sending with a message group ID

```java
String queueUrl = "https://sqs.us-east-1.amazonaws.com/123456789012/order-events.fifo";

// Producer: send order confirmed event
SendMessageRequest request = SendMessageRequest.builder()
    .queueUrl(queueUrl)
    .messageBody("{\"order_id\": \"o_123\", \"event\": \"order_confirmed\"}")
    .messageGroupId("o_123")                     // all o_123 events go to one consumer at a time
    .messageDeduplicationId("o_123-confirmed")   // prevents duplicate delivery within 5 min window
    .build();

sqsClient.sendMessage(request);
```

```java
// Consumer: process order events in order
ReceiveMessageRequest receiveRequest = ReceiveMessageRequest.builder()
    .queueUrl(queueUrl)
    .maxNumberOfMessages(10)
    .build();

List<Message> messages = sqsClient.receiveMessage(receiveRequest).messages();

for (Message message : messages) {
    OrderEvent event = parseEvent(message.body());

    switch (event.getType()) {
        case "order_confirmed" -> orderService.confirm(event.getOrderId());
        case "order_shipped"   -> orderService.ship(event.getOrderId());
        case "order_delivered" -> orderService.deliver(event.getOrderId());
    }

    // ACK — this unlocks the group so the next message for this order becomes available
    sqsClient.deleteMessage(DeleteMessageRequest.builder()
        .queueUrl(queueUrl)
        .receiptHandle(message.receiptHandle())
        .build());
}
```

> [!important] The `deleteMessage` call is what unlocks the message group. Until the consumer calls delete, SQS holds the group locked — no other consumer can pick up the next event for that order. This is what makes end-to-end ordering safe.

---

## Decision rule

```
Does order matter for correctness?
→ No  → Standard queue  (photo resize, email sending, video transcoding)
→ Yes → FIFO queue      (order state machines, inventory updates, audit logs)
```

> [!important] Don't default to FIFO "just to be safe." Standard is cheaper, faster, and sufficient for the majority of background job use cases. FIFO's throughput cap can become a bottleneck at high scale — only pay that cost when ordering is genuinely required.

> [!tip] **Interview framing:** "I'd use Standard SQS for transcoding jobs — order doesn't affect the result. For the order state machine I'd use FIFO with a message group per order ID — each order's events are processed in strict sequence while thousands of other orders process in parallel."
