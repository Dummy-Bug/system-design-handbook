
> [!info] N is not fixed — it grows with traffic
> A conversation doesn't go from 0 to 4,000 WPS instantly. Traffic ramps up. N must grow dynamically as the conversation gets hotter. And critically — N can never decrease, because messages written to old partitions can never be moved.

---

## N grows as traffic grows

The hot partition service monitors total WPS per conversation and adjusts N accordingly:

```
N = ceil(total_WPS / 800)   ← 800 not 1000, leave 20% headroom
```

As traffic ramps:

```
Phase 1 — normal:
  conv_abc123 → 200 WPS
  N = ceil(200/800) = 1
  Partition key: conv_abc123 (no suffix)

Phase 2 — getting hot:
  conv_abc123 → 900 WPS → threshold crossed
  N = ceil(900/800) = 2
  Partition keys: conv_abc123#0, conv_abc123#1
  Each partition: ~450 WPS ✓

Phase 3 — hotter:
  conv_abc123 → 2,200 WPS total
  N = ceil(2200/800) = 3
  Partition keys: conv_abc123#0, conv_abc123#1, conv_abc123#2
  Each partition: ~733 WPS ✓

Phase 4 — peak:
  conv_abc123 → 4,000 WPS
  N = ceil(4000/800) = 5
  Partition keys: conv_abc123#0 through conv_abc123#4
  Each partition: ~800 WPS ✓
```

The registry always stores the **maximum N ever reached**:

```
registry: { conv_abc123: { max_N: 5 } }
```

---

## Why N can never decrease

Suppose the conversation cools down from 4,000 WPS to 100 WPS. Could you set N back to 1?

No. Messages written during the hot period are physically stored in partitions `#0` through `#4`. If you set N=1 and only query `conv_abc123`, you miss all messages in `#1`, `#2`, `#3`, `#4`. Those messages are not lost — they're still in DynamoDB — but you can never read them again without knowing to look in the salted partitions.

```
Messages written when N=5:
  conv_abc123#0 → msg_aaa, msg_eee, ...
  conv_abc123#1 → msg_bbb, msg_fff, ...
  conv_abc123#2 → msg_ccc, msg_ggg, ...
  conv_abc123#3 → msg_ddd, msg_hhh, ...
  conv_abc123#4 → msg_iii, msg_jjj, ...

If you set N=1 and query only conv_abc123:
  → returns nothing (no messages were ever written to the unsuffixed key after N>1)
  → chat history appears empty → catastrophic data loss from user's perspective
```

The rule: **max_N is a high-water mark. It only goes up, never down.**

---

## The cost of keeping N high

When a conversation cools down but max_N stays at 5, every read must still query 5 partitions. This is a permanent read overhead for conversations that were once hot.

At scale, this is acceptable:

```
Hot conversations (ever reached N>1):
  Assume 0.1% of all conversations = 200k conversations
  Each read queries N partitions in parallel → latency bounded by slowest, not sum
  Overhead per read: N parallel DynamoDB reads instead of 1

Normal conversations (N=1 forever):
  No overhead, zero impact
```

The 99.9% of normal conversations are unaffected. The 0.1% that were ever hot pay a small read overhead — a fair price for having handled 4,000 WPS without data loss.

---

> [!tip] Interview framing
> "N grows dynamically as traffic increases — ceil(WPS/800). It never decreases because messages can't be moved between partitions. max_N is a high-water mark stored in the registry. Reads always use max_N to ensure no messages are missed. The read overhead for historically hot conversations is acceptable — they're rare and queries run in parallel."
