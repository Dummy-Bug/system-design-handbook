# Fan-Out on Write

> [!info] Fan-out on write means when a user posts, you immediately update all their followers' feeds in the background. By the time any follower opens the app, the post is already sitting in their feed — fast reads, background writes.

---

## The problem

A user posts a photo. 500 followers need to see it in their feed. You have two choices:

1. Update all 500 feeds right now, at post time
2. Do nothing now, compute the feed when each follower opens the app

Fan-out on write is option 1 — do the work upfront so reads are instant.

---

## Why async — never block the user

Even with only 500 followers, you never do feed updates synchronously in the user's post request. The user doesn't care if their followers' feeds are updated — they just want their post to go live. Making them wait for 500 DB inserts is a terrible experience.

```
User hits Post
→ Save post to DB (post_id: 789, user_id: Alice)
→ Drop one message in queue: { event: "post_created", post_id: 789, user_id: Alice }
→ Return "Posted!" to Alice   ← Alice is done in ~200ms

Queue holds the message.
Feed Service picks it up in the background.
```

---

## The full fan-out on write flow

**Step 1 — Feed Service picks up the message**
```
Reads from queue: { event: "post_created", post_id: 789, user_id: Alice }
```

**Step 2 — Fetch all of Alice's followers**
```sql
SELECT follower_id FROM followers WHERE following_id = Alice
→ returns [Bob, Charlie, Dave, ... 500 followers]
```

**Step 3 — Insert post into every follower's feed**
```sql
INSERT INTO feeds (user_id, post_id) VALUES (Bob, 789)
INSERT INTO feeds (user_id, post_id) VALUES (Charlie, 789)
... 500 inserts (done in batches of 50 for performance)
```

**Step 4 — ACK the queue**
```
Feed Service sends ACK → message deleted from queue
```

**Step 5 — Bob opens Instagram**
```sql
SELECT post_id FROM feeds WHERE user_id = Bob ORDER BY created_at DESC LIMIT 20
→ post_id 789 is already there, instant read
```

---

## The crash problem — and the fix

What if Feed Service crashes after 250 inserts? The message never got ACKed. Visibility timeout expires, message reappears, Feed Service picks it up again and does all 500 inserts. Now 250 followers get duplicate feed entries.

**Fix — DB-level idempotency**

Put a unique constraint on `(user_id, post_id)` in the feeds table. Use `ON CONFLICT DO NOTHING` on every insert.

```sql
INSERT INTO feeds (user_id, post_id) VALUES (Bob, 789)
ON CONFLICT (user_id, post_id) DO NOTHING
```

Now redelivery is completely harmless:

```
First delivery  → inserts 500 feed entries
Crash at 250    → message redelivered
Second delivery → tries all 500 inserts again
                → first 250 already exist → skipped silently
                → last 250 inserted fresh
                → done correctly, no duplicates
```

> [!important] DB-level idempotency via unique constraint is the most reliable approach — enforced at the storage layer, not in application code. No race conditions possible. Application-level "check before insert" has a race condition window between the check and the insert.

---

## When to use fan-out on write

Fan-out on write works well when follower counts are manageable — typically under ~10,000 followers. The write cost at post time is bounded and predictable.

```
Normal user posts (500 followers)
→ 1 queue message
→ 500 DB inserts in background
→ Fast reads for all followers
→ Total cost: manageable
```

> [!danger] Fan-out on write breaks down for celebrities. A celebrity with 10 million followers posting triggers 10 million DB inserts instantly. That's a massive write spike that can overwhelm your DB. Use fan-out on read for celebrities instead.

> [!tip] **Interview framing:** "For normal users I'd use fan-out on write — drop a post_created event in the queue, the Feed Service fetches the follower list and writes to each follower's feed asynchronously. Inserts are idempotent via a unique constraint on (user_id, post_id) so retries are safe. Reads are then O(1) — the feed is pre-computed and waiting."
