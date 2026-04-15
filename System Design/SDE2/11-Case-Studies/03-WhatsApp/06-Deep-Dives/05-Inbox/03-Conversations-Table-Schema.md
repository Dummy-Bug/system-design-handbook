
> [!info] The conversations table — schema design for the inbox
> One query must return Alice's full conversation list, sorted by most recent first. The schema must support that without N+1 lookups.

---

## What the inbox query needs

Alice opens WhatsApp. Her client needs:

```
For user_id = alice:
  → all conversation rows
  → sorted by last_message_timestamp, most recent first
  → paginated: top 20 first, more on scroll
  → each row contains: conv_id, last_message_preview, last_ts, unread_count
```

Everything needed to render the inbox in a single query. No follow-up lookups per row.

---

## Schema design

```
Table: conversations

PK (partition key) = user_id
SK (sort key)      = last_message_timestamp

Attributes:
  conv_id
  last_message_preview
  unread_count
```

The partition key is `user_id` alone — not `user_id + conv_id`. If you combined both into the partition key, you'd need to know the `conv_id` upfront to query the row, which defeats the purpose. You'd be back to N+1.

With `PK = user_id`, a single query fetches every row for Alice:

```
GET all rows WHERE PK = alice
ORDER BY SK DESC
LIMIT 20
```

Returns Alice's 20 most recent conversations in one round trip.

---

## Why the sort key choice matters

The sort key determines how rows are physically ordered within Alice's partition. DynamoDB (and Cassandra) store rows sorted by SK on disk — so the database can return them in order without scanning and sorting at query time.

If SK is `last_message_timestamp`, the most recent conversation is always at the top. The inbox query is a simple range scan from the top of Alice's partition.

This is the right shape for the read path. But the SK choice has a significant cost on the write path — covered in the next file.

> [!tip] Interview framing
> "PK is user_id — gives us all conversations for a user in one query. SK is last_message_timestamp — gives us sort order for free. Attributes store the denormalized preview data so we never need to join to the messages table."
