# Instagram Feed Generation — The Fan-Out Worker

Fan-out on write means every post gets pushed into every follower's feed cache. Someone has to do that work — and how you structure it determines whether posting feels instant or broken.

---

## The synchronous trap

The most natural implementation is to do the fan-out inside the post API itself. User hits post, the server saves the photo to the DB, loops through all followers, updates their Redis sorted sets, then returns success.

For a user with 100 followers this is fine — a few hundred milliseconds of extra work, barely noticeable. But Instagram isn't built for 100-follower accounts. Take a user with 1 million followers. The API server is now doing 1 million Redis writes before it can respond. The user stares at a spinner for seconds, waiting for their own post to go through.

The problem isn't that the work is too expensive — it's that the user is waiting for work they don't need to wait for. Their followers' feeds updating is a background concern. It has nothing to do with whether the post was saved successfully.

---

## Decoupling post from fan-out

The fix is to separate the two concerns entirely. The post API does exactly two things: save the post to the DB, and return success to the user. Fan-out happens asynchronously in the background.

```
User posts photo
      ↓
API saves post to DB
      ↓
API drops a message onto a queue  →  returns success to user immediately
                                              ↓
                                    Fan-out worker picks up message
                                              ↓
                                    Fetches all followers from DB
                                              ↓
                                    Pushes post into each follower's Redis sorted set
```

The user's post is live the moment the DB write completes. Feed updates propagate in the background — the user never waits for them.

---

## Choosing the queue — SQS or Kafka?

At 1,000 posts/sec, both SQS and Kafka handle the volume easily. The right choice comes from the consumption pattern, not the throughput numbers.

Kafka shines when multiple independent consumers each need to process the same event. If a single post needed to simultaneously update feeds, trigger the notification system, update the search index, and feed an analytics pipeline — one Kafka topic with four consumer groups each doing their own thing makes sense. One event, four independent readers.

But here the job is singular: one message goes in, one worker fans out to followers, done. There's no second consumer that independently needs the same post event. Running Kafka for this would be setting up a distributed commit log to serve one reader — the complexity isn't justified.

SQS handles this cleanly. It's a simple queue with at-least-once delivery — if the fan-out worker crashes mid-way through processing, the message becomes visible again after the visibility timeout and another worker picks it up. No messages are lost.

---

## At-least-once delivery and duplicates

At-least-once means the same post could theoretically be fanned out twice — worker crashes after updating half the followers, restarts, and processes the same message again from the beginning.

This sounds like it would cause duplicate posts in feeds. It doesn't. Redis sorted sets are naturally idempotent — each element is identified by its member value, which includes the `post_id`. If the same post gets inserted into a sorted set twice with the same score, Redis overwrites the existing entry. No duplicate appears.

The queue's at-least-once guarantee combined with Redis's idempotent writes means the fan-out is safe to retry freely, with no additional deduplication logic needed.

---

> [!tip] Interview framing
> The key insight is separating post latency from fan-out latency — the user should never wait for background work. Then for the queue choice, reason through the consumption pattern: one event, one consumer type, no multiple independent readers. That rules out Kafka. SQS is the right tool, and knowing why Kafka would be over-engineering here is what makes the answer strong.
