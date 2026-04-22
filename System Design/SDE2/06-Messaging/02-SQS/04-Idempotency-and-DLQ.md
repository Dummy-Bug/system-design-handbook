
> [!info] SQS delivers at-least-once. Duplicates are possible — a worker can crash after processing but before ACKing, causing the same message to be redelivered. Your consumer must handle this safely. Messages that keep failing get moved to a Dead Letter Queue automatically once they exceed the retry limit.

---

## Implementing idempotency in SQS

The concept is covered in Delivery Guarantees. Here's how you implement it specifically in SQS.

Every SQS message has a system-assigned `MessageId`. Use it as your deduplication key — store it in a `processed_messages` table before doing the actual work.

```java
for (Message message : messages) {
    String messageId = message.messageId();

    // check if already processed
    if (processedMessagesRepo.exists(messageId)) {
        // already done — just ACK and move on
        sqsClient.deleteMessage(DeleteMessageRequest.builder()
            .queueUrl(queueUrl)
            .receiptHandle(message.receiptHandle())
            .build());
        continue;
    }

    // process the job
    VideoTranscodeJob job = parseJob(message.body());
    transcodingService.transcode(job);

    // mark as processed and ACK — ideally in the same DB transaction
    processedMessagesRepo.save(messageId);
    sqsClient.deleteMessage(DeleteMessageRequest.builder()
        .queueUrl(queueUrl)
        .receiptHandle(message.receiptHandle())
        .build());
}
```

> [!important] If you have a business-level unique key (e.g. `order_id`, `video_id`), prefer that over `MessageId`. `MessageId` changes on every redelivery attempt in some edge cases. A business key is stable and more meaningful for debugging.

---

## Configuring DLQ in SQS — redrive policy

You configure a DLQ by attaching a **redrive policy** to your main queue. It has one setting that matters: `maxReceiveCount` — how many times a message can be received before SQS automatically moves it to the DLQ.

```java
// Create the DLQ first
CreateQueueResponse dlqResponse = sqsClient.createQueue(
    CreateQueueRequest.builder()
        .queueName("video-transcoding-dlq")
        .build()
);
String dlqArn = sqsClient.getQueueAttributes(
    GetQueueAttributesRequest.builder()
        .queueUrl(dlqResponse.queueUrl())
        .attributeNames(QueueAttributeName.QUEUE_ARN)
        .build()
).attributes().get(QueueAttributeName.QUEUE_ARN);

// Attach redrive policy to the main queue
String redrivePolicy = String.format(
    "{\"maxReceiveCount\":\"5\",\"deadLetterTargetArn\":\"%s\"}", dlqArn
);

sqsClient.setQueueAttributes(SetQueueAttributesRequest.builder()
    .queueUrl(mainQueueUrl)
    .attributes(Map.of(QueueAttributeName.REDRIVE_POLICY, redrivePolicy))
    .build());
```

After 5 failed delivery attempts (`maxReceiveCount: 5`), SQS automatically moves the message to `video-transcoding-dlq`. The main queue stays clean.

---

## Replaying DLQ messages after a fix

Once you've fixed the bug, you can replay all DLQ messages back onto the main queue using SQS's built-in redrive:

```java
StartMessageMoveTaskRequest replayRequest = StartMessageMoveTaskRequest.builder()
    .sourceArn(dlqArn)
    .destinationArn(mainQueueArn)
    .build();

sqsClient.startMessageMoveTask(replayRequest);
```

SQS moves messages from DLQ back to the main queue at a controlled rate. Workers pick them up and reprocess — this time successfully.

---

> [!tip] **Interview framing:** "I configure a DLQ with `maxReceiveCount: 5`. Any message that fails 5 times gets moved there automatically. I alert on DLQ depth — if it grows, an engineer investigates. Once the bug is fixed, I replay the DLQ back onto the main queue. Consumers are idempotent so replaying is always safe."
