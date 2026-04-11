# Scaling SQS Consumers

> [!info] Scaling SQS efficiently comes down to three things: long polling to avoid wasted API calls when the queue is empty, batching to reduce API overhead at high volume, and autoscaling workers based on queue depth so lag stays under control during traffic spikes.

---

## Long Polling — stop hammering empty queues

By default, `ReceiveMessage` returns immediately even if there are no messages. A worker running a tight polling loop hits the SQS API hundreds of times per minute for nothing.

```
Short polling (default):
Worker polls → queue empty → returns immediately → worker polls again
Worker polls → queue empty → returns immediately → worker polls again
... 100 empty API calls per minute, all wasted
```

Long polling tells SQS to wait up to 20 seconds for a message before returning. If a message arrives during that wait, it returns immediately. If nothing arrives in 20 seconds, it returns empty.

```
Long polling:
Worker polls with wait=20s → queue empty → SQS waits
→ message arrives at second 7 → SQS returns it immediately ✓
→ or nothing arrives → returns empty after 20s, worker polls again
```

Result: far fewer API calls, lower cost, and no wasted CPU on constant empty responses.

```java
ReceiveMessageRequest request = ReceiveMessageRequest.builder()
    .queueUrl(queueUrl)
    .maxNumberOfMessages(10)
    .waitTimeSeconds(20)  // long polling — wait up to 20 seconds
    .build();

List<Message> messages = sqsClient.receiveMessage(request).messages();
```

---

## Batching — reduce API overhead at scale

`ReceiveMessage` returns up to 10 messages per call. `DeleteMessageBatch` deletes up to 10 in one call. Always use both.

```
Processing 100,000 messages without batching:
→ 100,000 ReceiveMessage calls
→ 100,000 DeleteMessage calls
→ 200,000 API calls total

Processing 100,000 messages with batch size 10:
→ 10,000 ReceiveMessage calls
→ 10,000 DeleteMessageBatch calls
→ 20,000 API calls total  ← 10x fewer
```

```java
// Batch delete after processing
List<DeleteMessageBatchRequestEntry> entries = messages.stream()
    .map(msg -> DeleteMessageBatchRequestEntry.builder()
        .id(msg.messageId())
        .receiptHandle(msg.receiptHandle())
        .build())
    .collect(Collectors.toList());

sqsClient.deleteMessageBatch(DeleteMessageBatchRequest.builder()
    .queueUrl(queueUrl)
    .entries(entries)
    .build());
```

---

## Autoscaling workers from queue depth

Adding more workers speeds up drain rate. But you don't want workers running at full scale when the queue is empty — that wastes money. You scale based on two SQS metrics:

**`ApproximateNumberOfMessagesVisible`** — how many jobs are waiting. If this grows, consumers can't keep up with producers.

**`ApproximateAgeOfOldestMessage`** — how old is the oldest job sitting in the queue. A video that's been waiting 30 minutes to be transcoded is a business problem.

```
Scale out when:
→ queue depth > 1,000 messages   (backlog building up)
→ oldest message age > 5 minutes (jobs sitting too long)

Scale in when:
→ queue depth < 100 for 10 minutes  (queue draining, workers idle)
```

On AWS, this is wired directly into an Auto Scaling Group targeting these CloudWatch metrics. Workers scale up automatically when a traffic spike hits and scale back down when the queue drains.

---

> [!tip] **Interview framing:** "I'd enable long polling with a 20-second wait time and batch receive/delete in groups of 10 to minimize API overhead. For scaling, I'd autoscale workers based on `ApproximateNumberOfMessagesVisible` and `ApproximateAgeOfOldestMessage` — the age metric is especially important because it directly reflects how long jobs are waiting, which maps to user-visible latency."
