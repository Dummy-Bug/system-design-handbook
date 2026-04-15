
> [!info] The minimum state needed — one integer per user per conversation
> You don't need to store messages anywhere new. They're already in DynamoDB. You just need to know where Bob stopped receiving.

---

## The insight

The messages table already has everything:

```
Table: messages
  PK: conversation_id
  SK: seq_no
  All messages, safely stored, in order
```

The full content of every message Alice sent is already there. The problem isn't storage — it's knowing the resume point.

When Bob reconnects, the server needs to answer one question per conversation:

```
"What was the last seq_no Bob successfully received?"
```

If the answer is `seq=41`, the server fetches everything with `SK > 41` from DynamoDB and pushes it to Bob. That's the entire offline delivery mechanism.

The minimum state needed is one integer:

```
last_delivered_seq for Bob in conv_abc123 = 41
```

---

## Why this is enough

```
Bob was last delivered seq=41

Alice sent while Bob was offline:
  seq=42 "hey"
  seq=43 "where are you?"
  seq=44 "hello??"

On reconnect:
  query DynamoDB: PK=conv_abc123, SK > 41
  → returns seq 42, 43, 44
  → push all three to Bob in order
```

No separate message store. No duplicated data. No scanning through everything. One integer, one DynamoDB range query, done.

---

## What this integer represents

`last_delivered_seq` is not just for offline recovery — it is the permanent record of delivery state. It gets updated every time a message is successfully delivered to Bob, online or offline. When Bob is online, it stays current. When Bob goes offline, it simply stops updating — and that gap becomes the catch-up range on reconnect.

This is the foundation the pending deliveries table is built on.
