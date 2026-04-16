
> [!info] Salting — spreading one hot partition key across many
> You cannot tell DynamoDB to give a specific partition key its own node. What you can control is the partition key itself. By appending a suffix to the partition key, you split one logical conversation across multiple physical DynamoDB partitions — each handling a fraction of the total traffic.

---

## The core idea

Without salting, all messages for `conv_abc123` go to one partition key:

```
Partition key: conv_abc123
All 4,000 WPS → one DynamoDB partition → throttled at 1,000 WPS
```

With salting, the partition key gets a numeric suffix:

```
Partition keys: conv_abc123#0, conv_abc123#1, conv_abc123#2, conv_abc123#3
4,000 WPS split across 4 partitions → 1,000 WPS each → within limit
```

DynamoDB treats these as completely separate partition keys — they hash to different nodes, have independent throughput limits, and can be read and written independently.

---

## How the suffix is chosen — message_id % N

The suffix is not random. It is derived deterministically from the `message_id`:

```
suffix = message_id % N
partition_key = conversation_id + "#" + suffix
```

Why deterministic? Because on read, the app server needs to know which partition a message went to. With a random suffix, you'd have no way to know — you'd have to query all N partitions for every read. With `message_id % N`, you can derive the partition from the message_id at any time.

But in practice for chat history reads, you don't know the message_ids in advance — you're querying by timestamp. So you always query all N partitions on read regardless. The deterministic suffix mainly prevents duplicate writes on retry (same message_id → same partition → same row → idempotent).

---

## The write path with salting

```
Step 1 — App server receives message write for conv_abc123
Step 2 — Check hot partition registry: conv_abc123 → N=4
Step 3 — Compute suffix: message_id % 4 = 2
Step 4 — Write to partition key: conv_abc123#2
```

For normal conversations (N=1):

```
Step 2 — Check registry: conv_xyz999 → N=1 (or not in registry)
Step 3 — No suffix needed
Step 4 — Write to: conv_xyz999
```

Zero overhead for normal conversations — the registry lookup is a Redis O(1) read (~1ms) that returns N=1, and no salting is applied.

---

## Before and after

```
Before salting (N=1):
  conv_abc123 partition:
    msg_aaa → "hey"        (Alice, t=1000)
    msg_bbb → "hi!"        (Bob,   t=1001)
    msg_ccc → "how r u?"   (Alice, t=1002)
    ...all 4,000 WPS hitting this one partition

After salting (N=4):
  conv_abc123#0 partition:
    msg_aaa → "hey"        (message_id % 4 = 0)
    msg_eee → "lol"        (message_id % 4 = 0)

  conv_abc123#1 partition:
    msg_bbb → "hi!"        (message_id % 4 = 1)

  conv_abc123#2 partition:
    msg_ccc → "how r u?"   (message_id % 4 = 2)

  conv_abc123#3 partition:
    msg_ddd → "good"       (message_id % 4 = 3)

Each partition: ~1,000 WPS → within DynamoDB limit
```

---

> [!important] Salting is transparent to the client
> The client always uses `conversation_id` — it never knows about suffixes. The salting and de-salting happens entirely inside the app server layer. The client sends `conv_abc123`, the app server handles the routing to `conv_abc123#0` through `conv_abc123#3` transparently.
