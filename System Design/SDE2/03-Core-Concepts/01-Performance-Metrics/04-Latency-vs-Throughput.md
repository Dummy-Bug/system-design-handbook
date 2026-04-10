# Latency vs Throughput — The Tradeoff

> [!question] If I make my system faster, doesn't throughput automatically go up too?
> Not always. Sometimes fixing one breaks the other.

---

## The Core Tension

> **Optimizing for latency** → process things immediately, no waiting → inefficient use of resources → lower throughput
>
> **Optimizing for throughput** → batch things together, wait to accumulate work → individual requests wait longer → higher latency

You are always trading one for the other. The question is — **which one matters more for your system?**

---

## Example 1 — Database Batch Writes

Your database is getting hammered with writes. Each write goes to disk immediately.

- Latency per write: 10ms
- One thread handles: 1000ms / 10ms = **100 writes per second**

Now you change the approach — instead of writing each record immediately, you collect 100 records and write them all in one batch. One disk operation instead of 100 separate ones.

**What happened to throughput?** Went way up — the disk is doing far less work, processing records in bulk.

**What happened to latency?** The first record that arrives now has to sit and wait for 99 more records before anything gets written. Individual write latency shot up.

You traded fast individual responses for higher total capacity.

---

## Example 2 — Video Streaming

Netflix needs to send you a video. Two approaches:

**Option A** — send one tiny chunk the moment it's ready. You start watching faster. Low latency. But thousands of tiny chunks = thousands of separate network trips = inefficient = low throughput.

**Option B** — buffer and send larger chunks. Fewer network trips, far higher throughput. But now you wait a few seconds before playback starts. Latency went up.

This is why every video player has a loading spinner at the start — Netflix deliberately accepts higher startup latency to serve more users efficiently.

---

## Example 3 — Message Queue (Kafka)

Your service publishes events to Kafka — one event per user action, sent immediately the moment it happens.

Each publish is a separate network call to Kafka. At 100,000 events per second that's 100,000 individual network calls per second. Network overhead is massive. **Throughput suffers.**

Now you batch — collect 500 events, send them all in one network call. Network trips drop from 100,000 to 200 per second. **Throughput skyrockets.**

But the first event in each batch now waits for 499 more events to accumulate before it gets sent. **Latency per event increases.**

Kafka producers do exactly this by default — they have a configurable `linger.ms` setting that controls how long to wait before flushing a batch. Setting it to 0 = low latency, high network overhead. Setting it higher = better throughput, higher latency per message.

---

## The pattern across all examples

All of these are the same tradeoff in different clothes:

> **Make individuals wait → serve more of them overall**

| Scenario | Latency impact | Throughput impact |
|---|---|---|
| DB batch writes | ⬆️ increases | ⬆️ increases |
| Video buffering | ⬆️ increases | ⬆️ increases |
| Process immediately | ⬇️ decreases | ⬇️ decreases |

---

## How to decide which to optimize for

Ask: **what does a bad experience look like for this system?**

- **Chat app** — a message that takes 5 seconds to send is unacceptable. Optimize for latency.
- **Log processing pipeline** — nobody cares if logs arrive 2 seconds late. Optimize for throughput.
- **Payment API** — user is waiting for confirmation. Optimize for latency.
- **Analytics system** — processing billions of events overnight. Optimize for throughput.

> [!tip] In an interview
> When you choose between real-time processing and batching, always state the tradeoff explicitly:
> *"I'm choosing to batch these writes which increases throughput but adds latency — that's acceptable here because this is an analytics pipeline, not a user-facing API."*
