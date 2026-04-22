## Bitrate — The Streaming-Specific Term

Bitrate is how much data the server sends to one viewer every second to keep their video playing smoothly. It is not the total file size. It is a continuous, per-second flow of data that never stops until the user pauses or closes the app.

Higher resolution means more pixels per frame, which means more data per second. A 4K stream needs 25x more data per second than a 480p stream.

> [!info] Bitrate by resolution
> **480p** → ~1 Mbps
> **720p** → ~3 Mbps
> **1080p** → ~5 Mbps
> **4K** → ~25 Mbps

Bitrate exists as a concept because streaming is **continuous**. The server does not send one response and stop — it keeps sending data every second for the entire duration of the video. You need a word for **how much data per second for this one ongoing stream** — that is bitrate.

---

## The Four Terms in a Streaming System

> [!info] Bitrate
> How much data can travel through **one stream** per second — e.g. 25 Mbps for a 4K viewer

> [!info] Bandwidth
> How much data travels across **all streams** per second — e.g. 500 Tbps at peak across 20M viewers
> **Bandwidth = Bitrate × Concurrent Streams**

> [!info] Throughput
> How many concurrent streams are being served — e.g. 20M concurrent streams

> [!info] Latency
> Time from pressing play to the first frame appearing — Netflix targets under 2 seconds

Latency in streaming is not the same as API latency. Once playback begins, latency no longer matters — what matters is that the bitrate is sustained continuously without interruption.

---

## The Same Terms in a Non-Streaming System

In a normal request-response system — like a search API or a payment service — there is no continuous data flow. A request comes in, a response goes out, and the connection closes.

> [!info] Throughput
> Requests served per second — e.g. 30,000 req/sec

> [!info] Latency
> Time for one request end to end — e.g. 200ms

> [!info] Bandwidth
> Total data across all responses per second — e.g. 30,000 × 1KB = 30 MB/sec

> [!danger] Bitrate does not exist in non-streaming systems
> The closest equivalent is **payload size per request** — how many bytes one response carries. But since each response is a one-time event and not a continuous flow, you would never call it a bitrate.

---

## Why This Distinction Matters

If you treat Netflix like a normal API system and calculate QPS the way you would for a search engine, your numbers will be completely wrong. A search query is one request — done in 200ms. A Netflix stream is one connection that stays open for 2 hours, continuously consuming 25 Mbps.

> [!important] The key shift in thinking
> **Non-streaming** → count requests per second
> **Streaming** → count concurrent open connections × bitrate per connection
