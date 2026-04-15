
> [!info] Two schema options for the conversations table — and why both have a serious cost
> SK = timestamp gives you sort order for free but destroys the write path. SK = conv_id fixes the write path but makes the read path expensive. Neither works alone.

---

## The core tension

The inbox query needs conversations sorted by most recent message. The conversations table gets updated on every message send — which is the most frequent write in the system.

These two requirements pull in opposite directions. The schema that optimises reads hurts writes. The schema that optimises writes breaks reads.

---

## Option A — SK = last_message_timestamp

```
PK = user_id
SK = last_message_timestamp

conversations table:
  (alice, 9:42am) → { conv_id: conv_bob,  message: "hey what's up?" }
  (alice, 8:30am) → { conv_id: conv_carol, message: "see you tmrw"  }
  (alice, 8:00am) → { conv_id: conv_work,  message: "standup at 10" }
```

**Read path:** perfect. One query, sorted order, top 20 returned instantly.

**Write path:** every message send requires a tombstone + insert:

```
Bob sends Alice a message at 9:55am
→ tombstone: DELETE (alice, 9:42am)
→ insert:    (alice, 9:55am) → { conv_id: conv_bob, message: "on my way" }
```

Two writes per message, per participant. At WhatsApp scale:

```
100B messages/day × 2 participants × 2 writes = 400B write operations/day
400B tombstones accumulating on disk between compaction cycles
```

Tombstones degrade read performance, waste disk space, and create compaction pressure. In production Cassandra clusters, this has caused read timeouts and cluster instability — not a theoretical risk.

---

## Option B — SK = conv_id

```
PK = user_id
SK = conv_id

conversations table:
  (alice, conv_bob)   → { last_ts: 9:42am, message: "hey what's up?", unread: 3 }
  (alice, conv_carol) → { last_ts: 8:30am, message: "see you tmrw",   unread: 0 }
  (alice, conv_work)  → { last_ts: 8:00am, message: "standup at 10",  unread: 1 }
```

**Write path:** perfect. The row never moves — conv_id never changes. Every message send is a simple attribute update:

```
Bob sends Alice a message at 9:55am
→ UPDATE (alice, conv_bob) SET last_ts = 9:55am, message = "on my way"
```

One write. No tombstone. No delete.

**Read path:** broken for top K. Rows are stored in `conv_id` order, not timestamp order. To find Alice's 20 most recent conversations:

```
Option: fetch ALL of Alice's conversations, sort in memory, return top 20
```

Alice has 500 conversations. You fetch 500 rows. Throw away 480. Serve 20.

```
500M users × 500 DB reads = 250B DB reads/day
to serve 20 rows per user
```

Worse than Option A's tombstone problem. You've fixed the write path by completely breaking the read path.

---

## The verdict

Neither option works alone:

```
                    Option A                Option B
                    SK = timestamp          SK = conv_id
─────────────────────────────────────────────────────────────────
Write cost          400B tombstones/day     1 attribute update
Read cost           1 query, sorted         fetch all, sort in memory
Operational risk    compaction pressure     250B reads/day
Survivable?         No                      No
```

Option A kills the write path. Option B kills the read path.

The right answer combines both: use Option B's stable rows for the DB (fix the write path), and add a separate sorted index to fix the read path without touching the DB.

> [!tip] Interview framing
> "SK = timestamp gives sorted reads for free but every message send becomes a delete-plus-insert, creating 400 billion tombstones per day at WhatsApp scale. SK = conv_id eliminates tombstones with in-place attribute updates, but now there's no sort order — you'd need to fetch all 500 conversations per user to find the top 20, which is 250 billion DB reads per day. Neither works alone. The solution is stable rows in DB plus a separate sorted index for the read path."
