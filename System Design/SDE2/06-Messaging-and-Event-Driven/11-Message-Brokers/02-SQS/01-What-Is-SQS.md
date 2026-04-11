> [!info] SQS (Simple Queue Service) is AWS's fully managed message queue. You don't run any broker infrastructure — AWS handles it. A producer calls `SendMessage`, the message sits in the queue, and a consumer calls `ReceiveMessage` to pull it. SQS handles durability, retries, visibility timeout, and DLQ out of the box. You just write producer and consumer code.

---

## The problem SQS solves

An ad platform handles 20,000 clicks per second normally. During a big sporting event, it jumps to 150,000 clicks per second.

Each click needs significant downstream work:
```
1. Bill the advertiser
2. Update campaign analytics
3. Run fraud checks
4. Update pacing and budget systems
```

If the click API does all this synchronously, three things happen at once:
- Request latency spikes as the billing DB gets hammered
- Fraud service gets overwhelmed and starts timing out
- A slow fraud check makes the user's click confirmation take 3 seconds instead of 30ms

The right model: the click API accepts the event fast, writes it to a queue, returns 200ms to the user, and lets workers drain the queue at their own pace.

```
Click arrives
→ Click API: { click_id, ad_id, campaign_id, ts }
→ SendMessage to SQS
→ Return 200 in ~30ms to user

Queue holds the message.
→ Billing worker: ReceiveMessage → bills advertiser → DeleteMessage
→ Fraud worker: ReceiveMessage → checks click → DeleteMessage
→ Analytics worker: ReceiveMessage → updates stats → DeleteMessage
```

The traffic spike fills the queue. Workers drain it at whatever rate they can handle. Nothing crashes.

---

## Why teams pick SQS specifically

Every production system at some point needs async task distribution. The question is: do you run your own broker (RabbitMQ on EC2) or use a managed service?

Self-hosted RabbitMQ means: brokers to provision, upgrades to manage, disk to monitor, failover to configure, on-call responsibility when it goes down at 3am.

With SQS: you call three API endpoints. AWS handles everything else.

```
Producer: sqs.send_message(QueueUrl="...", MessageBody="...")
Consumer: messages = sqs.receive_message(QueueUrl="...", MaxNumberOfMessages=10)
Done:     sqs.delete_message(QueueUrl="...", ReceiptHandle="...")
```

This is the core reason SQS appears in so many AWS-based system designs — not because it's the most powerful broker (it isn't), but because zero infrastructure overhead is itself a feature at most scales.

---

## The visibility timeout — SQS's core delivery mechanism

When a consumer calls `ReceiveMessage`, SQS doesn't delete the message. It makes it invisible to all other consumers for a configured window (e.g., 30 seconds). This is the visibility timeout.

```
Consumer A calls ReceiveMessage → gets click_id: abc123 → SQS hides it from everyone
Consumer A processes it → calls DeleteMessage → message gone permanently

OR

Consumer A crashes, never calls DeleteMessage
→ Visibility timeout expires (30 seconds)
→ click_id: abc123 reappears in the queue
→ Consumer B picks it up
```

This is how SQS prevents duplicate processing under normal conditions while also ensuring jobs aren't lost when workers crash. The message only disappears after explicit confirmation that the work is done.

> [!important] The visibility timeout must be longer than your expected task processing time. If billing takes 45 seconds but your visibility timeout is 30 seconds, the queue thinks the worker crashed and hands the task to a second worker — while the first is still processing it. Set timeout to at least 2x expected task duration.

---

## What SQS is not

SQS is a task queue. It is not an event stream. Messages are deleted after ACK. There is no replay, no consumer groups reading the same message independently, and no long-term retention.

```
SQS: message received → processed → deleted → gone
Kafka: message received → consumer moves offset → message stays → other consumers can still read it
```

If you need multiple independent services to read the same events, or if you need to replay last week's data, SQS is the wrong choice. Use Kafka.

> [!tip] **Interview framing:** "I'd use SQS to decouple the click ingestion API from slower downstream processing. The API stays fast under traffic spikes — workers drain the queue asynchronously. SQS is managed, so there's no broker infrastructure to operate. The main constraint: if I need multiple independent consumer groups or event replay, I'd switch to Kafka."
