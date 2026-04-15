
> [!info] The schema must serve the access patterns
> DynamoDB is not a relational database — there are no joins, no foreign keys, no flexible queries. The schema must be designed around the exact queries the system will run. Get the partition key and sort key wrong and every query becomes a full table scan.

---

## Messages table

The core table. Every message ever sent lives here.

```
Table: messages

Partition Key: conversation_id       → routes to the right                                             DynamoDB partition

Sort Key:      timestamp#message_id  → composite: chronological order + collision safety

Attributes:
  message_id      (string)   → unique ID, client-generated (UUID or Snowflake)
  
  sender_id       (string)   → who sent the message
  receiver_id     (string)   → denormalized — avoids extra lookup to conversations table
  
  content         (string)   → the message text
  s3_ref          (string)   → nullable — pointer to S3 if                                   message is archived to cold storage
```

---

## Why conversation_id as partition key

DynamoDB distributes data by partition key using consistent hashing. All messages with the same `conversation_id` land on the same partition — which means a single range scan can retrieve an entire conversation's history without touching multiple partitions.

```
Query: PK = "conv_abc123" AND SK BETWEEN t1 AND t2

DynamoDB:
  1. Hash conv_abc123 → find the partition
  2. Scan the sorted SSTable within that partition from t1 to t2
  3. Return results

Cost: one partition read, contiguous disk scan → fast
```

If you used `sender_id` or `message_id` as the partition key, messages for the same conversation would scatter across partitions. Every chat history load would require a scatter-gather across multiple partitions — slow and expensive.

---

## Why timestamp alone is not safe as sort key — and the composite fix

Within a conversation, messages must be returned in chronological order. Using `timestamp` as the sort key works — until two messages in the same conversation arrive at the exact same millisecond. DynamoDB sort keys must be unique within a partition. Two rows with the same `PK + SK` means one silently overwrites the other. A message disappears.

The fix is a **composite sort key** — `timestamp#message_id`:

```
Sort Key: "1713087600000#msg_xyz789"
```

Since `message_id` is unique, the composite sort key is always unique — even if two messages arrive at the same millisecond. And since `timestamp` comes first, chronological ordering is fully preserved.

```
conv_abc123 partition:
  SK: "1713087600000#msg_aaa"  → "hey"
  SK: "1713087600001#msg_bbb"  → "hi!"
  SK: "1713087600001#msg_ccc"  → "how are you?"  ← same ms, different message_id, no collision
```

---

## Why receiver_id is denormalized here

In a pure normalized design, `receiver_id` is derivable from the conversations table — look up `conversation_id`, find the two participants, subtract `sender_id`. But that requires an extra DB call on every message read.

At 10k+ read QPS, that extra call doubles the DB load. Denormalizing `receiver_id` directly into the messages table eliminates it entirely — one read, all the data you need.

This is standard NoSQL practice: **duplicate data to avoid joins**.

---

## The s3_ref field — tiered storage hook

Messages older than 90 days are archived to S3 (covered in the tiered storage deep dive). When a message is archived, `content` is cleared and `s3_ref` is set to the S3 object key:

```
Before archival:
  content: "hey"
  s3_ref:  null

After archival:
  content: null
  s3_ref:  "s3://whatsapp-archive/conv_abc123/msg_xyz789.json"
```

When a client loads chat history and the app server encounters `s3_ref` set, it fetches from S3 transparently. The client sees no difference — just slightly higher latency for very old messages.

---

## The chat history query

```
PK = conv_abc123
SK < "current_timestamp#\xff"   (anything before now)
LIMIT 20
SCAN_INDEX_FORWARD = false      (newest first)
```

Returns 20 most recent messages in the conversation, already sorted. For pagination, the client passes the SK of the oldest message in the current batch as the cursor for the next request.

---

## Summary

```
Table: messages
  PK: conversation_id
  SK: timestamp#message_id     ← composite, collision-safe, chronologically ordered
  Attributes: sender_id, receiver_id, content, message_id, s3_ref

Inbox / conversations table → separate deep dive
Message status (ticks) → separate deep dive
```
