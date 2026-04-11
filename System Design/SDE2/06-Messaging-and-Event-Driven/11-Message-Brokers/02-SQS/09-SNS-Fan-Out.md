
> [!info] SQS delivers one message to one consumer — once read, it's deleted forever. When multiple independent services need to react to the same event, you need a fan-out layer. SNS (Simple Notification Service) is that layer — publish once to a topic, SNS pushes copies to all subscribers simultaneously.

---

## The problem SQS alone can't solve

When a customer places an order, three things need to happen independently:

```
Order placed
→ Warehouse needs to reserve inventory
→ Email service needs to send confirmation
→ Recommendations engine needs to update "bought this" data
```

With a single SQS queue:

```
Order placed → order-events-queue

Warehouse Worker grabs it → deleted
→ Email Worker never sees it ✗
→ Recommendations Worker never sees it ✗
```

One message, one consumer, gone forever. SQS cannot deliver the same message to multiple independent services.

---

## What is an SNS Topic?

An SNS topic is a named broadcast channel. Think of it like a YouTube channel — it just exists as a name. Anyone can publish to it. Everyone subscribed gets a copy the moment something is published.

```
SNS Topic = "order-events"
             ↑
        Any service publishes here
```

The topic stores nothing. The moment a message arrives, SNS immediately pushes copies to all subscribers and forgets about it. There is no "pick up later" — SNS is purely a delivery mechanism.

```
SQS = mailbox    → message sits there waiting to be picked up
SNS = megaphone  → shouts to everyone subscribed immediately, stores nothing
```

---

## SNS + SQS fan-out pattern

SNS alone is not enough — if a service is temporarily down when SNS pushes, that copy is gone. SNS doesn't retry, it doesn't buffer.

The complete pattern: SNS fans out to multiple SQS queues. Each service gets its own durable queue.

```
Customer places order
        ↓
   SNS Topic "order-events"
        ↓
   SNS fans out instantly
        ↓
┌───────────────┬──────────────────┬──────────────────────┐
↓               ↓                  ↓
SQS             SQS                SQS
(inventory)     (email)            (recommendations)
↓               ↓                  ↓
Warehouse       Email              ML
Workers         Workers            Workers
```

Each team owns their queue. Each team scales their workers independently — email might need 5 workers, warehouse might need 50. If the email service goes down, its SQS queue buffers the messages until it recovers. The other services are completely unaffected.

---

## What SNS and SQS are each responsible for

```
SNS  → fan-out. One message in, copies pushed to all subscribers. Stores nothing.
SQS  → buffer. Holds each copy until that service's workers drain it.
```

Neither does the other's job. SNS without SQS means a down service loses its copy forever. SQS without SNS means only one service ever sees each message.

---

## Java code — full wiring from SNS topic to SQS consumers

There are three steps: create the queues, subscribe them to the SNS topic, then publish and consume.

```java
SnsClient snsClient = SnsClient.create();
SqsClient sqsClient = SqsClient.create();

// Step 1 — create one SQS queue per consumer type
String inventoryQueueUrl = sqsClient.createQueue(
    CreateQueueRequest.builder().queueName("inventory-queue").build()
).queueUrl();

String emailQueueUrl = sqsClient.createQueue(
    CreateQueueRequest.builder().queueName("email-queue").build()
).queueUrl();

// Step 2 — get each queue's ARN and subscribe it to the SNS topic
String inventoryQueueArn = sqsClient.getQueueAttributes(
    GetQueueAttributesRequest.builder()
        .queueUrl(inventoryQueueUrl)
        .attributeNames(QueueAttributeName.QUEUE_ARN)
        .build()
).attributes().get(QueueAttributeName.QUEUE_ARN);

snsClient.subscribe(SubscribeRequest.builder()
    .topicArn("arn:aws:sns:us-east-1:123456789012:order-events")
    .protocol("sqs")
    .endpoint(inventoryQueueArn)
    .build());

// repeat for email queue — each subscription is independent
```

```java
// Step 3 — producer publishes once to SNS
PublishRequest publishRequest = PublishRequest.builder()
    .topicArn("arn:aws:sns:us-east-1:123456789012:order-events")
    .message("{\"order_id\": \"o_123\", \"user_id\": \"u_456\", \"total\": 99.99}")
    .build();

snsClient.publish(publishRequest);
// SNS immediately pushes a copy to inventory-queue AND email-queue
```

```java
// Step 4 — each service reads from its own SQS queue, completely independently
// Inventory worker — reads from inventory-queue only
List<Message> messages = sqsClient.receiveMessage(
    ReceiveMessageRequest.builder()
        .queueUrl(inventoryQueueUrl)
        .maxNumberOfMessages(10)
        .waitTimeSeconds(20)
        .build()
).messages();

for (Message message : messages) {
    OrderEvent event = parseEvent(message.body());
    inventoryService.reserveStock(event.getOrderId());

    sqsClient.deleteMessage(DeleteMessageRequest.builder()
        .queueUrl(inventoryQueueUrl)
        .receiptHandle(message.receiptHandle())
        .build());
}
// Email worker does the same against email-queue — neither knows the other exists
```

---

## When to use SNS + SQS vs plain SQS

```
One consumer type needs the message
→ plain SQS
→ multiple workers of same type compete, one processes it

Multiple independent consumers need the same message
→ SNS topic + one SQS queue per consumer type
→ each consumer gets their own copy in their own queue
→ their workers drain it independently
```

> [!important] Pub/sub doesn't replace task queues — it deposits into them. SNS is the fan-out layer. The actual work still happens in SQS queues with workers behind them. This is the same idea as the conceptual pub/sub model: **pub/sub = fan-out layer + one task queue per subscriber**. SNS + SQS is just the AWS implementation of that pattern.

> [!danger] SNS topics store nothing. If you publish to a topic with no subscribers, the message is gone. Always subscribe SQS queues to the SNS topic before publishing — never rely on SNS to buffer anything.

> [!tip] **Interview framing:** "I'd use the SNS fan-out pattern here. The order service publishes once to an SNS topic. SNS pushes copies to three SQS queues — one for inventory, one for email, one for recommendations. Each service drains its own queue independently. If one service is slow or down, its queue buffers the messages without affecting the others. Pub/sub doesn't replace task queues — it deposits into them."
