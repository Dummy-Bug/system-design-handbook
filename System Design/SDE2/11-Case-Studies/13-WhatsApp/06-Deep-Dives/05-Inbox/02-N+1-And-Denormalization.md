
> [!info] The N+1 problem — and why denormalization is the fix
> Fetching a list then querying each item separately multiplies your DB load by N. Store the preview data directly on the conversation record instead.

---

## The naive approach — N+1 queries

Alice has 50 conversations. The obvious approach:

```
Query 1: fetch conversation_ids for alice
→ returns [conv_1, conv_2, conv_3, ... conv_50]

Then for each conversation_id:
Query 2:  SELECT last_message FROM messages WHERE conv_id = conv_1
Query 3:  SELECT last_message FROM messages WHERE conv_id = conv_2
Query 4:  SELECT last_message FROM messages WHERE conv_id = conv_3
...
Query 51: SELECT last_message FROM messages WHERE conv_id = conv_50
```

1 query to get the list + 50 queries to hydrate each item = **51 queries total**.

This is the N+1 pattern. N is the number of items, +1 is the initial list fetch.

---

## Why this destroys the database at scale

```
500M daily active users
Each user opens their inbox once a day
Naive approach: 500M × 51 queries = 25.5 BILLION DB queries per day
                                      just for inbox loads

With fix:       500M × 1 query  = 500M DB queries per day
```

51× more load on the database. For a feature that runs on every app open, every day, for 500 million users — the naive approach is not survivable.

---

## The fix — denormalization

Instead of going to the messages table to find the last message, store the last message preview directly on the conversation record.

```
conversations table:
  PK = user_id
  SK = last_message_timestamp (inverted for sort order)

  conv_id              | last_message       | last_ts  | unread_count
  ─────────────────────────────────────────────────────────────────────
  conv_alice_bob       | "hey what's up?"   | 9:42am   | 3
  conv_alice_carol     | "see you tmrw"     | 8:30am   | 0
  conv_alice_work      | "standup at 10"    | 8:00am   | 1
```

Now Alice's inbox load is a single query:

```
GET all rows WHERE PK = alice, ordered by SK descending, LIMIT 20
```

One round trip. All 20 rows. Every field needed to render the inbox. Done.

---

## The trade-off — write amplification

Denormalization is not free. Every time a new message is sent in a conversation, you must update the `last_message` and `last_ts` fields on the conversation row.

```
Bob sends message to Alice
→ Write 1: insert into messages table
→ Write 2: update conversations[alice] SET last_message = ..., last_ts = ...
→ Write 3: update conversations[bob]   SET last_message = ..., last_ts = ...
```

A single message send now touches three rows instead of one.

> [!important] Denormalization trades write cost for read cost
> Every message send does more work upfront. In exchange, every inbox load does far less work. For WhatsApp, inbox loads happen far more often than messages are sent — Alice opens her inbox dozens of times a day and sends maybe 20 messages. The trade-off heavily favours the read path.

---

## Why this is the right call at WhatsApp scale

```
Reads  → inbox loads → happen every app open → 500M/day
Writes → message sends → maybe 20 per user/day → 10B/day
```

10B writes sounds like a lot. But each write is a simple key update — cheap. Each inbox load at 51 queries is expensive and happens just as often. Denormalization shifts complexity from the read path (which is latency-sensitive and user-visible) to the write path (which runs in the background on message send).

> [!tip] Interview framing
> "The naive approach has an N+1 problem — one query for conversation IDs, then N queries to fetch last message data. At 500M DAU, that's 25 billion queries per day just for inbox loads. The fix is denormalization: store last_message, last_ts, and unread_count directly on the conversation row. Inbox load becomes a single query. The cost is write amplification — every message send must update the conversation row — but reads far outnumber writes, so the trade-off is correct."
