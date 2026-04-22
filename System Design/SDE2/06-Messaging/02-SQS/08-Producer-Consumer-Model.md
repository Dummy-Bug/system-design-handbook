
> [!info] Any number of producers can send to a queue. Any number of consumers can read from a queue — but they all compete. Every message goes to exactly one consumer and is deleted after ACK. No other consumer, from any service, ever sees it again.


## Multiple producers — any service can send

Any service can call `SendMessage` on an SQS queue. You can have one producer or ten producers — SQS doesn't care where messages come from.

```
Upload Service     → SendMessage → video-transcoding-queue
Admin Dashboard    → SendMessage → video-transcoding-queue
Batch Import Tool  → SendMessage → video-transcoding-queue

All three are pushing jobs into the same queue.
Workers drain it without caring who sent what.
```

---

## One queue per job type — not optional

SQS doesn't enforce what goes into a queue, but mixing job types is a mistake.

If a video transcoding worker picks up a photo resize job, it has no idea how to process it — it fails. The message gets redelivered. Another worker picks it up. Fails again. Eventually hits the DLQ. Job lost, resources wasted on every retry.

```
Mixed queue — wrong:
Queue: [transcode_video, resize_photo, transcode_video]

Video Worker picks up resize_photo → fails → redelivered → fails → DLQ ✗
```

**One queue per job type — correct:**

```
video-transcoding-queue  →  transcoding workers only
photo-resize-queue       →  resize workers only
email-sending-queue      →  email workers only
```

Now workers only ever compete against their own service instances — any instance picking up the job is capable of handling it. Different queues also get their own visibility timeouts (video transcoding takes minutes, email takes milliseconds) and their own independently scaled worker pools.

---

## Multiple consumers — but they compete

Multiple consumers can connect to the same queue. This is how you scale workers — spin up more consumers to drain the queue faster.

But they all compete for the same messages:

```
Queue: [job_1, job_2, job_3]

Worker A grabs job_1 → SQS hides it → Worker A processes → deletes → gone
Worker B grabs job_2 → SQS hides it → Worker B processes → deletes → gone
Worker C grabs job_3 → SQS hides it → Worker C processes → deletes → gone
```

Each job goes to exactly one worker. Once deleted, it is gone permanently — no other worker, from any service, ever sees it.

---

## The fundamental limitation

Because each message is deleted after one consumer reads it, SQS cannot deliver the same message to multiple independent services.

```
Queue: [order_1, order_2, order_3]

Billing Worker grabs order_1 → deleted
→ Fraud Worker never sees order_1 ✗

Fraud Worker grabs order_2 → deleted
→ Billing Worker never sees order_2 ✗
```

If you need both Billing and Fraud to process every order, a single SQS queue can't do it. Each message only gets one life.

> [!important] SQS = one message, one consumer, one time. Multiple consumers connected to the same queue just means faster draining — they're still competing, not cooperating. If multiple independent services need to react to the same message, that requires a different pattern — covered in the next files.
