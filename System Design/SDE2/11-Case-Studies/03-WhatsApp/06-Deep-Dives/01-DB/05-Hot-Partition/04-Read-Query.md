
> [!info] Reads must account for all partitions a conversation has ever used
> Once a conversation is salted, its messages are physically distributed across N DynamoDB partitions. A read that only queries one partition returns incomplete history. The app server must scatter the query across all N partitions and merge the results.

---

## The naive read — broken for salted conversations

Without accounting for salting, a chat history read looks like:

```
Query: PK = conv_abc123, SK < cursor, LIMIT 20, ORDER DESC
```

This works for N=1 conversations. For a salted conversation with max_N=4, this query only hits the unsuffixed partition key — which may contain very few or no messages (all messages went to `#0`, `#1`, `#2`, `#3`). The result is empty or incomplete.

---

## The correct read — scatter-gather

**Step 1** — Check the hot partition registry:

```
GET registry[conv_abc123]
→ max_N = 4
```

**Step 2** — Fire N queries in parallel, one per salted partition:

```
Query 1: PK = conv_abc123#0, SK < cursor, LIMIT 20, ORDER DESC
Query 2: PK = conv_abc123#1, SK < cursor, LIMIT 20, ORDER DESC
Query 3: PK = conv_abc123#2, SK < cursor, LIMIT 20, ORDER DESC
Query 4: PK = conv_abc123#3, SK < cursor, LIMIT 20, ORDER DESC
```

All 4 queries run simultaneously — total latency is bounded by the slowest query, not the sum.

**Step 3** — Merge results by timestamp:

```
Results from all 4 partitions (up to 80 messages total):
  t=1005 "good thanks"   (from #1)
  t=1004 "how are you?"  (from #2)
  t=1003 "hi!"           (from #3)
  t=1002 "hey"           (from #0)
  ...

Sort by timestamp DESC → take top 20
```

**Step 4** — Return the 20 most recent messages to the client.

---

## The fast path for normal conversations

For the 99.9% of conversations that were never hot (max_N=1 or not in registry):

```
GET registry[conv_xyz999]
→ null (not in registry) → treat as N=1

Query: PK = conv_xyz999, SK < cursor, LIMIT 20, ORDER DESC
→ single partition read, no scatter-gather
```

Zero overhead. The scatter-gather only activates for conversations that were ever hot.

---

## Latency impact

```
Normal conversation (N=1):
  1 DynamoDB read → ~5ms

Hot conversation (N=4):
  4 parallel DynamoDB reads → ~5ms (parallel, bounded by slowest)
  + merge 80 messages in memory → ~1ms
  Total → ~6ms

Hot conversation (N=10):
  10 parallel reads → ~5ms
  + merge 200 messages → ~2ms
  Total → ~7ms
```

The scatter-gather adds minimal latency because all queries run in parallel. The merge is in-memory and fast. Even at N=10, the read is only ~2ms slower than a single partition read.

---

## Cursor pagination with scatter-gather

Pagination works the same way — the cursor (timestamp#message_id) is applied to all N partition queries:

```
First page (no cursor):
  All N partitions: LIMIT 20, ORDER DESC → take top 20 overall

Next page (cursor = "1713087600000#msg_xyz789"):
  All N partitions: SK < "1713087600000#msg_xyz789", LIMIT 20, ORDER DESC
  → merge → top 20 messages before the cursor
```

The cursor is consistent across all partitions because it's a sort key value — the same sort key range applies regardless of which salted partition holds the message.

---

> [!tip] Interview framing
> "For salted conversations, reads scatter across all N partitions in parallel and merge by timestamp. Latency is bounded by the slowest partition — not the sum — so N=4 adds only ~1ms over a single read. Normal conversations (N=1) are unaffected. The registry lookup tells the app server whether to scatter or not."
