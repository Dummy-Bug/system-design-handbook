# Publish-Subscribe (Pub/Sub)

> [!info] In pub/sub, one message gets delivered to every subscriber independently. Each subscriber gets its own copy. They don't compete — they all process the same event in parallel.

---

## The problem point-to-point can't solve

When a user posts a photo on Instagram, three services need to react:
- Notification Service — send push notifications to followers
- Feed Service — update follower news feeds
- Moderation Service — run AI content check

If this was a point-to-point queue, all three services would compete for the same message. Only one would win. The other two would never know the photo was posted. That's wrong — all three need to run.

---

## How pub/sub works

Each subscriber gets its own independent internal queue. When a message is published to a topic, the pub/sub system copies it to every subscriber's queue.

```
Producer publishes: { event: "photo_posted", photo_id: 123 }

Pub/Sub system fans out:
→ Notification Queue  [photo_posted_123]  ← Notification Service reads from here
→ Feed Queue          [photo_posted_123]  ← Feed Service reads from here
→ Moderation Queue    [photo_posted_123]  ← Moderation Service reads from here
```

3 subscribers = 3 separate copies in 3 separate queues. Each queue manages its own ACKs independently.

---

## How the producer knows the publish succeeded

The producer only cares about one thing — did the pub/sub system receive the message.

```
Producer → publishes to topic "photo_posted" → Pub/Sub system ACKs back to producer
```

The producer's job is done. It doesn't wait for Notification Service or Feed Service to process anything.

Think of it like dropping a letter at the post office. Once the post office stamps it "received", you walk away. The post office is now responsible for delivery to all recipients.

---

## How does the pub/sub system know who the subscribers are?

You register subscribers upfront at configuration time — not at runtime.

```
Topic: "photo_posted"
Subscribers: [Notification Service, Feed Service, Moderation Service]
```

When a message arrives, the system looks at this list and copies the message to each subscriber's queue. The producer never knows or cares how many subscribers exist.

---

## What if one subscriber's service crashes before ACKing?

Each subscriber's copy lives and dies independently. Same visibility timeout mechanism as point-to-point.

```
Notification Queue  → ACKed ✓ → its copy deleted
Feed Queue          → ACKed ✓ → its copy deleted
Moderation Queue    → service crashes, no ACK
                    → 30 seconds pass (visibility timeout)
                    → message reappears in Moderation Queue
                    → Moderation Service picks it up again
```

The other two are completely unaffected. Only the failed subscriber's copy gets redelivered.

---

## What if the pub/sub system crashes mid fan-out?

A well-built pub/sub system (Kafka, Google Pub/Sub) writes the message to disk **before** ACKing the producer. It also tracks which subscriber queues have received the message.

```
Message written to disk ✓
→ Copied to Notification Queue ✓
→ Copied to Feed Queue ✓
→ System crashes before copying to Moderation Queue ✗
→ System restarts → reads message from disk
→ sees Moderation Queue hasn't received it → delivers it
```

This is why the pub/sub system only ACKs the producer after the message is durably on disk — not just in memory. A crash can always be recovered from.

---

## Point-to-Point vs Pub/Sub — when to use which

| | Point-to-Point | Pub/Sub |
|---|---|---|
| Message goes to | One consumer | All subscribers |
| Consumers compete? | Yes | No |
| Use when | Distributing work | Broadcasting an event |
| Example | Thumbnail generation, email sending | Photo posted, order placed |

> [!tip] The mental model: point-to-point is a **to-do list** shared by workers — each item done once. Pub/Sub is a **broadcast** — everyone hears the same announcement independently.
