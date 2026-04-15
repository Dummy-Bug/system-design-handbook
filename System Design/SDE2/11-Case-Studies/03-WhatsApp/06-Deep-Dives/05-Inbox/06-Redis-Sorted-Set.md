
> [!info] Redis sorted set — fixing Option B's read path
> Option B gives clean writes but no sort order. A Redis sorted set sits in front of the DB and answers "top K conversations" without touching the DB at all.

---

## The gap Option B leaves

With `SK = conv_id`, rows never move — writes are clean. But the DB has no way to return conversations sorted by recency. To find Alice's top 20 most recent conversations you'd have to fetch all 500 and sort in memory — 250B DB reads per day.

The fix: maintain a sorted index separately, in Redis. The DB stores the full conversation data. Redis stores only the sort order.

---

## The sorted set structure

```
Redis sorted set:
  key:    inbox:alice
  member: conv_id
  score:  last_message_timestamp (unix ms)
```

Every conversation Alice has is a member. The score is the timestamp of the last message in that conversation. Redis keeps members sorted by score automatically — highest score (most recent) at the top.

The score is timestamp only — not unread count or anything else. The sorted set answers one question: which conversations are most recent? Unread count, last message preview, avatar — all of that lives in the DB row and gets fetched once you know which conversations to show.

---

## Write path — message arrives

Bob sends Alice a message:

```
→ Write 1: UPDATE conversations[alice][conv_bob]
           SET last_ts = 9:55am, last_message = "on my way", unread_count += 1
           (DynamoDB — durable, attribute update, no tombstone)

→ Write 2: ZADD inbox:alice 1705312500000 conv_bob
           (Redis — updates score in place if conv_bob already exists)
```

Two writes. Both cheap. The Redis ZADD either inserts conv_bob as a new member or updates its score — no delete, no tombstone.

---

## Read path — Alice opens inbox

```
Step 1: ZREVRANGE inbox:alice 0 19
        → Redis returns top 20 conv_ids, sorted by score descending
        → runs entirely in RAM, O(log N + 20)

Step 2: Batch fetch from DynamoDB
        GET conversations WHERE PK = alice AND SK IN [conv_bob, conv_carol, ...]
        → 20 rows, each with last_message, last_ts, unread_count, avatar

Step 3: Return to client
        → client renders inbox
```

Two steps. Redis answers the sort question instantly from RAM. DB serves exactly 20 rows — no waste.

---

## What this looks like end to end

```
                    Option B alone          Option B + Redis
─────────────────────────────────────────────────────────────────
Write cost          1 attribute update      1 DB update + 1 Redis ZADD
Tombstones          zero                    zero
Inbox read          fetch all 500 rows      ZREVRANGE → fetch 20 rows
DB reads/day        250B                    10B (500M users × 20 rows)
Sort done by        app server (memory)     Redis (in place)
```

The extra Redis write on every message send is the price. The payoff is inbox load goes from 500 DB reads to 20.

---

## Why unread_count is not the score

Sorted sets have one score per member. If unread_count were the score, conversations would be ordered by how many unread messages they have — not by recency. Alice's inbox would show the conversation with the most unread messages at the top, not the most recent one.

Unread count is an attribute — it belongs in the DB row where it can be incremented and reset independently. The score is purely for sort order.

> [!tip] Interview framing
> "Option B's stable rows fix the write path but leave no sort order. A Redis sorted set fills that gap — member is conv_id, score is last_message_timestamp. On every message send, ZADD updates the score in place. On inbox load, ZREVRANGE returns the top 20 conv_ids from RAM in microseconds, then a batch DB fetch gets the full row data for exactly those 20 conversations. No tombstones. No wasted DB reads."
