> [!info] Every write in DynamoDB is replicated to 3 servers across availability zones. What happens when you read immediately after writing depends on which consistency mode you choose — and DynamoDB lets you pick per read, not per table.

---

## Why consistency is a question at all

When you write to DynamoDB, the write goes to a primary node and replicates to 2 replicas **asynchronously**. The write is acknowledged once 2 of 3 nodes confirm it (quorum write). But the third replica might lag behind by a few milliseconds.

If you immediately read after writing, you might hit that lagging replica and see stale data.

```
Write: user email = "new@example.com"  → acknowledged ✓
Read 10ms later → hits replica that hasn't caught up yet
→ returns "old@example.com"  ✗
```

DynamoDB gives you a choice about how tso handle this.

---

## Two consistency modes

**Eventually consistent read** — default

```
→ might hit any replica, including one that's slightly behind
→ stale by up to a few hundred milliseconds
→ cheaper: costs 0.5x read units
→ faster: no coordination needed
```

**Strongly consistent read**

```
→ guaranteed to return the latest written value
→ reads from the primary node only
→ costs 2x read units
→ slightly higher latency
```

---

## When to use which

The decision is straightforward — ask "does it matter if this read is 200ms stale?"

```
Eventually consistent  →  social feeds, like counts, view counts,
                           recommendations, leaderboards
                       →  stale by a second? user doesn't notice or care

Strongly consistent    →  profile updates (user just changed their email)
                       →  payment and order status
                       →  messages sent (must appear immediately)
                       →  anything where the user just wrote and expects to see it
```

> [!tip] Default to eventually consistent. Only pay the 2x cost when the user would notice staleness — typically anything they just modified themselves.

---

## Global Tables — multi-region replication

If your users are spread across continents, a single-region DynamoDB forces every read and write to travel to that region. India to US-East is 200ms round trip — that's just geography.

Global Tables solves this by keeping a full copy of your table in multiple regions, all kept in sync automatically:

```
us-east-1  ←→  ap-south-1  ←→  eu-west-1
   ↕               ↕               ↕
 US users      India users     EU users

Write goes to nearest region → replicates to all others in the background
Read goes to nearest region  → fast, local
```

An Indian user writes → hits Mumbai → replicates async to US and EU.
An Indian user reads → hits Mumbai → no cross-continental trip.

> [!important] Global Tables replication is **asynchronous** — same as multi-primary replication you've seen elsewhere. This means Global Tables reads are eventually consistent across regions. If a US user and an Indian user edit the same record simultaneously, DynamoDB uses last-writer-wins conflict resolution.

---

```
Single region:
  Eventually consistent  →  cheap, fast, fine for most reads
  Strongly consistent    →  2x cost, reads from primary, use when freshness matters

Multi-region (Global Tables):
  Async replication across regions
  Low latency everywhere
  Eventually consistent cross-region by definition
  Conflict resolution: last-writer-wins
```
