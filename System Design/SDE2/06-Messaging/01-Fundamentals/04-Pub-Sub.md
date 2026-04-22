
> [!info] In pub/sub, one message gets delivered to every subscriber independently. Each subscriber gets its own copy and processes it using their own task queue. They don't compete — they all react to the same event in parallel.

---

## The problem a task queue can't solve

When a user posts a photo on Instagram, three services need to react:
- Notification Service — send push notifications to followers
- Feed Service — update follower news feeds
- Moderation Service — run AI content check

If you used a task queue, all three services would compete for the same message. Only one would win. The other two would never know the photo was posted.

```
Task queue:  photo posted → Notification Service wins → Feed and Moderation never see it ✗
```

That's wrong — all three need to run. You need a broadcast, not a job distribution.

---

## How pub/sub works

The pub/sub system has a **fan-out layer** that copies the message into each subscriber's own internal queue. Those internal queues are task queues — each subscriber's workers drain their own queue independently.

```
Producer publishes: { event: "photo_posted", photo_id: 123 }

Pub/Sub fans out:
→ Notification's queue  [photo_posted_123]  ← Notification's workers drain this
→ Feed's queue          [photo_posted_123]  ← Feed's workers drain this
→ Moderation's queue    [photo_posted_123]  ← Moderation's workers drain this
```

So pub/sub is really just:

```
Pub/Sub = fan-out layer + one task queue per subscriber
```

The fan-out copies the message to everyone. Each subscriber then processes their copy the same way a task queue works — one worker picks it up, ACKs, done.

---

## The producer doesn't know who's listening

You register subscribers at configuration time — not in the producer's code.

```
Topic: "photo_posted"
Subscribers: [Notification Service, Feed Service, Moderation Service]
```

The producer just publishes to the topic. The pub/sub system looks up the subscriber list and fans out. The producer never knows or cares how many subscribers exist.

This is the key advantage over a task queue for broadcasts: when a new service needs to react to "photo posted" next month, you add it to the subscriber list — the producer's code doesn't change at all.

---

## What if one subscriber crashes before ACKing?

Each subscriber's copy lives and dies independently. The visibility timeout mechanic is the same as a task queue.

```
Notification queue  → ACKed ✓ → its copy deleted
Feed queue          → ACKed ✓ → its copy deleted
Moderation queue    → service crashes, no ACK
                    → visibility timeout expires
                    → message reappears in Moderation's queue
                    → Moderation Service picks it up again
```

The other two are completely unaffected. Only the failed subscriber's copy gets redelivered.

---

## What if the pub/sub system crashes mid fan-out?

A well-built pub/sub system writes the message to disk **before** ACKing the producer. It also tracks which subscriber queues have already received the copy.

```
Message written to disk ✓
→ Copied to Notification queue ✓
→ Copied to Feed queue ✓
→ System crashes before copying to Moderation queue ✗
→ System restarts → reads from disk
→ sees Moderation queue hasn't received it → delivers it
```

This is why the system ACKs the producer only after the message is durably on disk — a crash can always be recovered from.

---

## Task Queue vs Pub/Sub

| | Task Queue | Pub/Sub |
|---|---|---|
| Message goes to | One worker | All subscribers |
| Workers compete? | Yes — first one wins | No — each gets their own copy |
| Use when | "Do this job" | "This thing happened" |
| New consumer added? | Just add a worker | Add to subscriber list, producer unchanged |
| Example | Resize photo, send email | Order placed, photo posted |

> [!tip] The mental model: task queue is a **shared to-do list** — one item, one worker crosses it off. Pub/Sub is a **broadcast announcement** — everyone hears it and reacts independently.
