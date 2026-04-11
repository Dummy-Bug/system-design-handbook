# TTL and Session Storage in DynamoDB

## DynamoDB has built-in TTL

DynamoDB lets you set an expiry timestamp on any item. You just add an `expires_at` attribute with a Unix timestamp:

```json
{
  "thread_id":  "abc-123",
  "checkpoint":  { "...langgraph state..." },
  "expires_at":  1718000000
}
```

You tell DynamoDB which attribute is the TTL attribute, and it automatically deletes items after that time passes. No cron job, no cleanup script, no manual delete queries — AWS handles it.

---

## The catch — DynamoDB TTL is eventual

When the `expires_at` timestamp passes, DynamoDB does not delete the item instantly. It marks it for deletion and cleans it up in the background:

```
expires_at = 10:00 AM

10:00 AM         →  item marked expired
10:00 to ~10:48  →  item might still be readable
within 48 hours  →  item is actually deleted from disk
```

AWS guarantees deletion within **48 hours** — not instantly. This means your application can still read an expired item in the window between expiry and actual deletion.

> [!danger] TTL is for storage cleanup — not access control
> Never rely on DynamoDB TTL alone to enforce expiry. If your code does `get_item(session_id)` and the item comes back, it might already be logically expired. Always validate expiry in your application:

```python
item = get_item(session_id)
if item and item["expires_at"] > now():
    # valid
else:
    # treat as expired regardless of what DynamoDB returned
```

---

## When eventual TTL is fine — LangGraph checkpointers

For LangGraph state checkpointers, eventual TTL is perfectly acceptable. A stale checkpoint sitting around for a few extra hours after expiry is harmless — it's just temporary state that will eventually be cleaned up. The access pattern is:

```
partition key  →  thread_id
sort key       →  checkpoint_timestamp

"give me the latest checkpoint for thread X"
→  single partition lookup
→  fast, durable, zero ops
```

DynamoDB is the right call here — write-heavy, keyed access, durable, fully managed on AWS, TTL for cleanup.

---

## When eventual TTL is not enough — user sessions

For user session data, eventual TTL is a problem. An expired session must not be accessible — if a user logs out or their session expires, reading stale session data is a security issue.

This is where Redis comes in:

```
Redis TTL:
expires_at = 10:00 AM
10:00:01 AM  →  GET session:abc  →  nil  ✓ gone instantly

DynamoDB TTL:
expires_at = 10:00 AM
10:00:01 AM  →  GET session:abc  →  might still return data ✗
```

Redis enforces TTL **at read time** — the moment the key expires, Redis will not return it. It's gone from the application's perspective instantly.

---

## The production pattern — right tool for right job

```
LangGraph checkpointer  →  DynamoDB
                            write-heavy, keyed by thread_id
                            durable, zero ops, relaxed TTL is fine

User session data        →  Redis
                            strict TTL enforced at read time
                            sub-millisecond reads
                            expired session must never be returned
```

---

## TTL strictness across all major databases

Redis is the only mainstream database where TTL is strict and enforced at read time. Every other database treats TTL as a best-effort background cleanup:

```
Redis           →  strict — enforced at read time, gone instantly ✓
Cassandra       →  eventual — tombstone, cleaned up during compaction
DynamoDB        →  eventual — cleaned up within 48 hours
MongoDB         →  eventual — TTL index runs every ~60 seconds
Postgres        →  no built-in TTL — you write cron jobs manually
MySQL           →  no built-in TTL — you write cron jobs manually
```

> [!important] The rule
> Whenever strict expiry is a hard requirement — user sessions, OTP codes, rate limit windows — Redis is the answer, regardless of what else you're using for storage.

---

## The full architecture

```
Redis       →  strict TTL, user sessions, sub-millisecond reads
DynamoDB    →  durable storage, LangGraph state, relaxed TTL, zero ops
```

They're not competing — they coexist at different layers solving different problems.

> [!tip] Interview framing
> "For session storage I'd use Redis — TTL is enforced at read time, so an expired session is gone instantly. For checkpointer state or activity logs I'd use DynamoDB — durable, write-heavy, zero ops on AWS, and the eventual TTL cleanup is fine since stale state sitting around for a few hours has no impact."
