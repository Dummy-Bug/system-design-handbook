
> [!info] The core idea
> Distributed locks work for one global exclusive job — only one server runs the nightly email blast. For per-record processing — millions of items each processed independently — tracking state on the record itself is the right approach. The database becomes the coordination layer. This is how Kafka consumers, SQS workers, and serious job queues work under the hood.

---

## When distributed locks are the wrong tool

Consider this job: fetch all phone numbers from DB, hit an external API to get the Aadhaar number for each, write the result back.

The naive approach — acquire a global lock, process all phone numbers, release the lock. One server runs everything.

Problems immediately:
- The API is slow and flaky — the job takes hours
- If the server crashes halfway, another server re-processes everything from scratch
- The lock is held for hours — massive TTL needed, or constant renewal

A distributed lock is designed for **short, exclusive, global operations** — like "only one server triggers the DB failover". It is not designed for millions of independent units of work spread across hours.

---

## Per-record state tracking — the right approach

Instead of one global lock, track the state of **each record** in the database itself:

```
phone_number   | aadhar_status | aadhar_number
---------------|---------------|---------------
9876543210     | PENDING       | null
9123456789     | IN_FLIGHT     | null          ← being processed right now
9988776655     | DONE          | 1234-5678-9012
9871234560     | DONE          | null          ← API returned null, confirmed
```

States:
- **PENDING** — not yet processed, any server can pick it up
- **IN_FLIGHT** — being processed right now, all other servers skip it
- **DONE** — result written, never touch again (even if result is null)

---

## How this handles every failure case

**Server crashes mid-job:**
```
Server 1 picks up 9123456789 → marks IN_FLIGHT
Server 1 crashes
→ a cleanup job resets IN_FLIGHT → PENDING after timeout
→ Server 2 picks it up again ✓
```

**API returns null due to flakiness:**
```
Server 1 gets null from API
→ writes aadhar_number = null, status = DONE
→ this record is now permanently DONE
→ no other server will ever overwrite it with null again ✓
```

**Two servers race on the same record:**
```
Server 1 and Server 2 both see 9876543210 as PENDING
Both try to update status to IN_FLIGHT simultaneously
→ DB-level atomic compare-and-swap: only one wins
→ loser sees the record is already IN_FLIGHT → skips it ✓
```

The database handles the coordination — not the lock.

---

## The key insight

```
Distributed lock:
→ right for: one global exclusive operation (leader election, nightly cron trigger)
→ wrong for: millions of independent records each needing processing

Per-record state tracking:
→ right for: job queues, bulk processing pipelines, API enrichment jobs
→ the DB is the coordination layer
→ each record carries its own lock implicitly via its status column
```

This pattern is how **Kafka consumer groups** track which messages have been processed (offsets per partition), how **SQS** handles in-flight messages (visibility timeout), and how every serious distributed job queue avoids double processing.

> [!tip] Interview framing
> "For per-record processing, a global distributed lock is the wrong tool — it serializes everything and creates a single point of failure. Instead, track state on each record: PENDING, IN_FLIGHT, DONE. Use an atomic compare-and-swap at the DB layer to claim a record. If the server crashes, a cleanup job resets IN_FLIGHT records after a timeout. This is how SQS visibility timeouts and Kafka consumer offsets work — the storage layer is the coordination layer."
