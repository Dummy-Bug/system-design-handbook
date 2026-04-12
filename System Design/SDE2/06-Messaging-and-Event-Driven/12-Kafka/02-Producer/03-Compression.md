
> [!info] Compression is applied at the producer, travels through the broker untouched, and is decompressed at the consumer. The broker is a "cold pipe" — it never looks inside the batch. This is what lets one broker move gigabytes per second without a powerful CPU.

---

## The problem compression solves

You have 100,000 ad clicks per second. Each click event is a small JSON object:

```json
{
  "event_type": "ad_click",
  "advertiser_id": "nike",
  "user_id": "user_abc",
  "ad_id": "ad_123",
  "timestamp": 1712000000,
  "country": "US",
  "device": "mobile"
}
```

That's roughly 150–200 bytes per event. At 100k events/sec, that's **15–20 MB/sec** just from producers writing to the broker. Then each partition has 3 replicas, so the broker is replicating that data internally — multiply by 3. And consumers are reading it back — multiply again.

Suddenly one topic's traffic is easily **100–200 MB/sec** in combined network I/O. Scale that to 50 topics on a production cluster and you're saturating your network cards well before you saturate your disk.

Compression is how you cut that number down. Not by a little — by 60–80%. The same 100k events/sec becomes 3–6 MB/sec on the wire instead of 15–20 MB/sec.

---

## Why compression works so well on batches

This is the key insight the batching file set up: **compression finds repetition. One message has almost no repetition. A batch of 100 messages has massive repetition.**

Look at those 100 click events in a batch. Every single one has:
- The same JSON keys: `"event_type"`, `"advertiser_id"`, `"user_id"`, `"ad_id"`, `"timestamp"`, `"country"`, `"device"`
- Similar values: many might share `"advertiser_id": "nike"`, `"country": "US"`, `"device": "mobile"`
- The same structure: same opening `{`, same colons, same commas

A compression algorithm works by finding these repeated byte sequences and replacing them with short references. The first time it sees `"advertiser_id": "nike"` it stores it in full. Every subsequent occurrence in the batch becomes a 2-byte pointer.

A single 200-byte message compressed = still ~180 bytes. You gain almost nothing.
100 messages batched and compressed = 3,000–8,000 bytes instead of 20,000. You just got 60–80% smaller.

This is why batching and compression are always discussed together — batching creates the conditions that make compression effective.

---

## Where in the pipeline compression happens

```
Producer (your app server)
  → collects batch in RAM
  → compresses entire batch (CPU cost here)
  → sends compressed bytes over network  ← smaller payload

Broker (Kafka)
  → receives compressed bytes
  → writes compressed bytes to disk  ← stores as-is, no decompression
  → replicates compressed bytes to followers  ← smaller replication traffic
  → sends compressed bytes to consumer  ← smaller read payload

Consumer (your billing/fraud service)
  → receives compressed batch
  → decompresses (CPU cost here)
  → processes individual messages
```

The broker never unzips or rezips anything. It treats the batch as an opaque blob of bytes — it just stores and forwards it. This is intentional.

---

## Why compression is at the producer, not the broker

The naive design would be: producer sends raw data, broker compresses it before writing to disk.

The problem is the broker is your bottleneck machine. Every partition write goes through it. Every replication goes through it. Every consumer read goes through it. Adding CPU-intensive compression to that machine means the broker's CPU becomes the limiting factor at high throughput.

Your producers are your application servers. You typically have many of them — one per app server instance. If you have 20 app servers each running a producer, you have 20 CPUs available for compression work. Spreading the compression load across 20 machines instead of concentrating it on 3 brokers is strictly better.

Same logic applies to consumers. Decompression cost is paid by your consumer services — each one decompresses its own batches. The broker never touches the compressed bytes except to store and forward them.

```
Without producer-side compression:
  20 producers → broker compresses all writes → broker CPU saturates

With producer-side compression:
  20 producers each compress their own batches
  → broker is a cold pipe: store + forward only
  → broker CPU stays free for replication and serving reads
```

---

## Choosing a compression algorithm

Kafka supports four: `none`, `gzip`, `snappy`, `lz4`, `zstd`.

**Gzip** — highest compression ratio (smallest output), but also the slowest. Uses significantly more CPU than the others. Worth it if your bottleneck is network bandwidth or storage cost and you have CPU headroom on the producer.

**Snappy** — Google's algorithm. Designed for speed over compression ratio. Lower CPU usage, compresses to roughly 50% of gzip's gains. If your producers are under CPU pressure (they're already doing other work), Snappy is the default safe choice.

**LZ4** — similar to Snappy in philosophy but faster at decompression. Good if your consumers are the bottleneck.

**Zstd (Zstandard)** — Facebook's algorithm, added in Kafka 2.1. Best balance of compression ratio and speed. In benchmarks it often beats gzip's compression ratio while running at Snappy's speed. This is the modern default for new deployments.

```
Algorithm   Compression Ratio   CPU Cost    Best For
──────────────────────────────────────────────────────
gzip        highest             highest     bandwidth-constrained, CPU-spare producers
snappy      medium              lowest      CPU-constrained producers
lz4         medium              low         latency-sensitive consumers
zstd        high                medium      general purpose (modern default)
```

For ad click pipelines: **zstd** unless you're on Kafka < 2.1, in which case **snappy**.

---

## When compression doesn't help

Compression only works when there is repetition in the data. Two cases where it won't:

**Already compressed data** — if your messages contain JPEGs, MP4s, or any binary format that's already compressed, running Kafka's compression on top adds CPU cost and saves nothing (or makes it slightly larger). Skip compression for these topics.

**Already encrypted data** — encryption randomizes byte patterns. Compression after encryption gains nothing. If you're encrypting message payloads at the application layer before sending to Kafka, compression should happen before encryption, not after.

---

## The numbers — what compression actually changes

At 100k clicks/sec with 200 bytes per event, ~70% compression:

```
Without compression:
  Network (producer → broker):          20 MB/sec
  Replication (RF=3, 2 extra copies):   40 MB/sec additional
  Consumer reads (5 consumers):        100 MB/sec
  Total cluster network I/O:           ~160 MB/sec

With zstd compression:
  Network (producer → broker):           6 MB/sec
  Replication:                          12 MB/sec additional
  Consumer reads:                       30 MB/sec
  Total cluster network I/O:            ~48 MB/sec
```

You've reduced cluster network traffic by 70%. Same data, same throughput, same number of brokers — three times more headroom before you hit network saturation. Or equivalently: the same cluster can now handle three times the event volume before you need to add hardware.

Storage is the same story. 70% smaller on disk means your 30-day retention window now uses 30% of the disk space it would have without compression.

---

> [!important] The broker's CPU stays free because it never decompresses. It writes compressed bytes to disk, replicates compressed bytes to followers, and sends compressed bytes to consumers. The compression/decompression CPU cost is distributed across your producer fleet and consumer fleet — never concentrated at the broker.

> [!tip] **Interview framing:** "I'd enable zstd compression on the producer. Batching makes it effective — 100 similar JSON events compress to 20–30% of their original size because the repeated keys and values collapse. The broker stays a cold pipe: it stores and forwards compressed bytes without ever unzipping them. This shifts CPU cost to producers and consumers, which you have many of, and keeps the broker free for replication and serving reads. At 100k events/sec it cuts cluster network I/O by 60–70%."
