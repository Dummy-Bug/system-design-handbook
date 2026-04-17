## The Challenge — Bytes Over JSON

Before we look at the endpoints, there's one thing that shapes the entire API design: **the value is opaque bytes**.

Our KV store doesn't care what's inside the value — it could be a string, a number, a serialized protobuf, or an image thumbnail. The store just holds the raw bytes and gives them back unchanged.

But our API uses JSON, and JSON is text-only. You can't put raw bytes inside a JSON string — some byte values are invalid UTF-8, some are control characters that break parsers, and some (like `"`) would terminate the string mid-value.

The solution is **base64 encoding**. Here's the full flow — who does what:

```
Client (e.g. WhatsApp backend, user profile service — whoever is using our KV store)
  has raw bytes (image, protobuf, whatever)
  → base64-encodes the bytes into a safe text string
  → sends JSON to our API: { "value": "U29tZSBkYXRh" }

Our KV store (the server — the system we're designing)
  receives the JSON
  → base64-decodes the string back to raw bytes
  → stores the raw bytes on disk (no base64 bloat in storage)

Later, client calls GET
  → our KV store reads raw bytes from disk
  → base64-encodes them back into a text string
  → returns JSON: { "value": "U29tZSBkYXRh" }

Client receives JSON
  → base64-decodes back to raw bytes
  → has the original data again
```

Base64 only exists during the JSON transport — it's the packaging for shipping bytes over a text-only format. On disk, it's always raw bytes, so there's no storage penalty. The ~33% size overhead only applies to network traffic. (See the next file for a full explanation of why base64 and not other approaches.)

---

## Put — Store a Key-Value Pair

```
POST /api/v1/item

Request body:
{
  "key":   "user:123:name",
  "value": "U29tZSBkYXRh",        // base64-encoded bytes
  "ttl":   86400                   // optional — seconds until auto-expiry
}

Response 201 Created:
{
  "key":       "user:123:name",
  "timestamp": 1713400000000       // server-assigned write timestamp
}
```

**Why does the response include a timestamp?**

This is the key design decision in the API. When the server writes your data, it assigns a timestamp to that write. Returning it to the client enables **read-your-own-writes consistency** — without forcing every read to be strongly consistent.

Here's the scenario it solves. You write `put("balance", "500")`. The server acks with `timestamp: 1002`. Immediately after, you read `get("balance")` with eventual consistency. The replica you hit might still have the old value `"400"` at `timestamp: 1001`. Without the timestamp, you'd think your write failed.

But if your `put` response gave you `timestamp: 1002`, you can tell the `get` request: "give me a value at least as recent as 1002." If the replica only has 1001, the system knows it's stale — it either waits for replication to catch up or routes you to a replica that has your write.

**Why a timestamp and not a version number?**

A version number (1, 2, 3, ...) would need a **central coordinator** to hand out sequential numbers. In a leaderless system with 1,200 nodes, that coordinator becomes a bottleneck and single point of failure.

Timestamps don't need coordination — each node uses its own clock. The trade-off is clock drift: two nodes might disagree on what time it is by a few milliseconds. Real systems handle this:

- **Cassandra** uses Last-Write-Wins with timestamps — accepts that clock skew might rarely pick the wrong winner
- **DynamoDB** uses vector clocks to detect conflicts rather than blindly resolving them

For the API layer, timestamp is the right choice — it's coordination-free and the client can use it for read-your-own-writes. How the server handles clock skew internally is a deep dive topic, not an API concern.

**Why is TTL optional?**

Not every key needs to expire. A user profile lives forever. A session token expires in 30 minutes. Making TTL optional means the default is "keep forever" and the client opts into expiry when the use case demands it.

**What if the key already exists?**

The value is silently overwritten. No error, no conflict response. Same behavior as a HashMap: same key, second value wins. The new timestamp replaces the old one. This is the standard behavior across DynamoDB, Cassandra, and Redis.

---

## Get — Retrieve a Value by Key

```
GET /api/v1/item?key=user:123:name&consistency=eventual

Response 200 OK:
{
  "key":       "user:123:name",
  "value":     "U29tZSBkYXRh",       // base64-encoded bytes
  "timestamp": 1713400000000          // when this value was written
}

Response 404 Not Found:
{
  "key":   "user:123:name",
  "error": "key not found"
}
```

**The consistency parameter — this is the most important API decision.**

The client chooses on every read: `consistency=strong` or `consistency=eventual`. This is how tunable consistency shows up in the API.

```
consistency=eventual  (default)
  → Server reads from any single replica
  → Fastest possible — p99 < 10ms
  → Might return a value that's a few milliseconds behind the latest write
  → Good for: user profiles, feature flags, session data

consistency=strong
  → Server reads from a quorum (majority of replicas)
  → Slower — p99 < 50ms (must wait for multiple nodes to respond)
  → Guaranteed to return the latest write
  → Good for: financial balances, inventory counts, anything where stale = wrong
```

The client says **what they want** (strong or eventual), not **how to achieve it** (R=2, W=2, N=3). Quorum numbers are server-side implementation details. If you exposed R, W, N in the API, every application developer would need to understand distributed systems just to read a key. That's bad API design.

DynamoDB does exactly this — a single `ConsistentRead: true/false` parameter. Clean and simple.

**Why does the response include the timestamp?**

Same reason as the `put` response — it tells the client which version they're looking at. If the client previously wrote at `timestamp: 1002` but the `get` returns `timestamp: 1001`, the client knows they got a stale replica and can retry or escalate to a strong read.

**Why is consistency only on GET, not on PUT?**

Writes always need to be durable — you always write to a quorum (W=2 out of N=3). There's no "fast but unreliable write" option for a database that's someone's source of truth. The speed-vs-correctness trade-off only makes sense on the read path, where returning slightly stale data is sometimes acceptable.

---

## Delete — Remove a Key-Value Pair

```
DELETE /api/v1/item?key=user:123:name

Response 200 OK:
{
  "key":     "user:123:name",
  "deleted": true
}

Response 200 OK (key didn't exist):
{
  "key":     "user:123:name",
  "deleted": true
}
```

**Why 200 even when the key doesn't exist?**

This is an **idempotent delete**. Imagine the client sends a delete, the server processes it, but the response is lost due to a network failure. The client retries. If the second call returned 404, the client would think something went wrong — but the delete already succeeded on the first call.

Returning 200 on both calls means retries are always safe. Same result whether called once or ten times. The client's intent was "make sure this key doesn't exist" — and it doesn't, regardless of whether it was this call or a previous one that removed it.

**How is delete actually implemented?**

The server doesn't physically erase the data immediately. It writes a **tombstone** — a special marker that says "this key has been deleted." Reads that encounter the tombstone return 404. A background compaction process later cleans up the tombstone and the old data from disk.

Why tombstones? Because in a distributed system, you can't just delete from one node — you need all replicas to know the key is gone. The tombstone replicates to all nodes through the same mechanism as normal writes. If you just erased the data on one node, another replica would still have it and might "resurrect" the key during anti-entropy repair.

---

## Full API Summary

```
POST   /api/v1/item                    Put (create or overwrite)
GET    /api/v1/item?key=...&consistency=...   Get (tunable consistency)
DELETE /api/v1/item?key=...            Delete (idempotent)
```

```
Consistency parameter (GET only):
  eventual  → any single replica, fast, default
  strong    → quorum read, slower, guaranteed latest

TTL parameter (POST only):
  optional  → seconds until auto-expiry, default is keep forever

Timestamp (in all responses):
  server-assigned → enables read-your-own-writes without forcing strong consistency
```

---

> [!tip] Interview framing
> "Three endpoints: POST to put (returns timestamp for read-your-own-writes), GET with a consistency parameter (eventual by default, strong on demand — client says what they want, not the quorum numbers), DELETE which is idempotent (200 even if key doesn't exist, because retries must be safe). Values are base64-encoded in JSON for transport, decoded to raw bytes for storage. Consistency is only tunable on reads — writes always go to quorum because this is a source of truth, you don't get a 'fast but maybe lost' write option."
