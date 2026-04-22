
> [!info] SQS (Simple Queue Service) is AWS's fully managed task queue. You don't run any broker infrastructure — AWS handles it. A producer calls `SendMessage`, the message sits in the queue, and a consumer calls `ReceiveMessage` to pull it. SQS handles durability, retries, visibility timeout, and DLQ out of the box. You just write producer and consumer code.

---

## The problem SQS solves

A user uploads a video to YouTube. Before it can go live, the video needs to be transcoded into multiple resolutions — 360p, 720p, 1080p, 4K. Transcoding is CPU-heavy and can take minutes.

If the upload API does transcoding synchronously:

```
User uploads video
→ API starts transcoding (takes 3 minutes)
→ User stares at spinner for 3 minutes
→ API returns "done"
```

That's a terrible experience. The user doesn't need transcoding to finish before they see "Upload successful." They just need the video eventually available.

The right model: accept the upload fast, drop a job in the queue, return immediately. A worker picks up the transcoding job in the background.

```
User uploads video
→ API saves raw video to S3
→ API drops job in SQS: { video_id: "v_123", s3_path: "raw/v_123.mp4" }
→ API returns "Upload successful!" in ~200ms ✓

SQS holds the job.
→ Transcoding worker: ReceiveMessage → transcodes video → DeleteMessage
```

The upload spike on a big content day fills the queue. Workers drain it at whatever rate they can handle. Nothing crashes.

---

## Why teams pick SQS specifically

Every production system needs async job distribution at some point. The question is: do you run your own broker infrastructure or use a managed service?

Self-hosted means: servers to provision, upgrades to manage, disk to monitor, failover to configure, on-call responsibility when it crashes at 3am.

With SQS: three API calls. AWS handles everything else.

```java
String queueUrl = "https://sqs.us-east-1.amazonaws.com/123456789012/video-transcoding-queue";

// producer
SendMessageRequest sendRequest = SendMessageRequest.builder()
    .queueUrl(queueUrl)
    .messageBody("{\"video_id\": \"v_123\"}")
    .build();
sqsClient.sendMessage(sendRequest);

// consumer
ReceiveMessageRequest receiveRequest = ReceiveMessageRequest.builder()
    .queueUrl(queueUrl)
    .maxNumberOfMessages(10)
    .build();
    
List<Message> messages = sqsClient.receiveMessage(receiveRequest).messages();

// done — delete after processing
for (Message message : messages) {
    process(message);
    
    DeleteMessageRequest deleteRequest =        
    DeleteMessageRequest.builder()
        .queueUrl(queueUrl)
        .receiptHandle(message.receiptHandle())
        .build();
        
    sqsClient.deleteMessage(deleteRequest);
}
```

This is why SQS appears in so many AWS system designs — not because it's the most powerful broker (it isn't), but because zero infrastructure overhead is itself a feature at most scales.

---

## The visibility timeout — SQS's core delivery mechanism

When a consumer calls `ReceiveMessage`, SQS doesn't delete the message. It makes it invisible to all other consumers for a configured window — say 30 seconds. This is the visibility timeout.

```
Worker A calls ReceiveMessage → gets video_id: v_123 → SQS hides it from everyone else
Worker A transcodes it → calls DeleteMessage → message gone permanently

OR

Worker A crashes mid-transcode, never calls DeleteMessage
→ Visibility timeout expires (30 seconds)
→ video_id: v_123 reappears in the queue
→ Worker B picks it up and starts over
```

The job doesn't get lost. It reappears and another worker picks it up.

> [!important] The visibility timeout must be longer than your expected job duration. If transcoding takes 5 minutes but your visibility timeout is 30 seconds, SQS assumes the worker crashed and hands the job to a second worker — while the first is still running. Now two workers are transcoding the same video. Set timeout to at least 2x expected job duration.

---

## What SQS is not

SQS is a task queue. Each job goes to exactly one worker. Once a worker ACKs the message, it's deleted — permanently gone.

```
SQS: job picked up → processed → deleted → gone
```

> [!danger] SQS is not pub/sub. If you need multiple independent services to all react to the same event — billing AND analytics AND fraud all processing the same order — a single SQS queue is the wrong tool. Only one worker would get each message. The other services would never see it. That's a pub/sub problem, not a task queue problem.
