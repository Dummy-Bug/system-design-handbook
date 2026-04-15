
> [!info] The first caching instinct — cache recent messages per conversation
> Caching the last N messages per conversation is a natural first idea. The math shows it's viable but the ROI is lower than it first appears.

---

## The idea

When Alice opens a conversation with Bob, the app fetches the last 10 messages from DynamoDB. Those same messages will be fetched again if she closes and reopens the chat. Why go to the DB every time?

The proposal: cache the last N messages per conversation in Redis as a list.

```
Redis list:
  key:   chat:conv_abc
  value: [msg10, msg9, msg8, msg7, msg6, msg5, msg4, msg3, msg2, msg1]
```

On every new message, LPUSH the new message and LTRIM to keep only the last N. The oldest message falls off automatically.

First time Alice opens the chat → cache miss → fetch from DynamoDB → populate Redis. Second time → cache hit → skip the DB entirely.

---

## The math

Does caching messages actually fit in RAM?

**Naive attempt — last 10 messages per conversation:**

```
100M DAU × 10 messages × 250 bytes per message
= 100M × 2,500 bytes
= 250GB
```

250GB just for message caches. That's a large dedicated Redis cluster for a single use case.

**Optimization — last 5 messages:**

```
100M DAU × 5 messages × 250 bytes
= 125GB
```

Still 125GB. Tighter but expensive.

**The TTL insight:**

Not all 100M DAU are actively chatting at the same moment. If you set a TTL of 10 minutes — only conversations with recent activity stay in cache — the working set drops dramatically. In practice, maybe 10-20% of conversations are active in any 10-minute window.

```
125GB × 20% active = ~25GB
```

With LRU eviction plus a short TTL, message caching becomes feasible.

---

## Why it's still not the best target

The reasoning is sound, but there's a subtlety: DynamoDB is already fast. Fetching the last 10 messages from DynamoDB by PK+SK range takes ~2-5ms. You're adding Redis to save 2-5ms on a chat open that the user probably doesn't notice.

More importantly, messages aren't truly immutable from a cache perspective. WhatsApp has "delete for everyone" — a message deleted after being cached means the cache is now serving a ghost message. Every delete event needs to invalidate or update the cache entry. This adds operational complexity.

The maintenance cost (tracking deletes, keeping the list in sync) is real. The latency win is small. Message caching is valid, but the profile cache delivers far higher ROI for much less complexity.

> [!tip] Interview framing
> "Message caching is viable with TTL + LRU, but DynamoDB is already fast for recent messages and delete-for-everyone creates invalidation complexity. I'd prioritise profile caching first — higher read frequency, simpler invalidation, near-static data."
