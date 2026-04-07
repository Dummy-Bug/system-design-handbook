# Interview Cheatsheet — Latency, Throughput, Bandwidth & Percentiles

> [!question] The interviewer says "design WhatsApp". What's the first thing you do?
> You don't draw boxes. You figure out what kind of system this is by assessing all four metrics first.

---

## Why This Matters

Without this step, everything you say is vague:
- *"The system should be fast"* — fast by what measure? For whom? At what scale?
- *"We need high throughput"* — how high? How do you know?

Percentiles are what make the other three metrics **concrete and defensible**. Without them you're throwing buzzwords. With them you have real numbers that justify every architecture decision you make.

---

## The Three Questions to Ask First

For every system the interviewer gives you, run through these three questions before drawing anything:

---

### Question 1 — Is this latency sensitive?

**Ask yourself**: is there a human waiting for a response in real time?

| Answer | What it means |
|---|---|
| Yes — user is waiting | Latency is critical. Optimize hard for it. |
| No — background job, batch process | Latency is not the concern. Focus elsewhere. |

**Examples:**
- WhatsApp message delivery → yes, someone is staring at the screen waiting → latency critical
- YouTube video upload → no, you click upload and go make tea → latency not critical
- Google Search → yes, user is waiting for results → latency critical
- Nightly analytics report → no, runs at 2am → latency irrelevant

---

### Question 2 — What's the throughput demand?

**Ask yourself**: how many requests per second at peak?

Do a quick back of envelope:
```
Daily active users × actions per user per day = total daily requests
Total daily requests / 86,400 seconds = average RPS
Average RPS × 3 to 5 = peak RPS
```

That number tells you whether one server is enough or whether you need horizontal scaling, sharding, and load balancers.

| Peak RPS | What it implies |
|---|---|
| < 1,000 | Single server might handle it |
| 1,000 – 10,000 | Multiple servers, load balancer needed |
| 10,000 – 100,000 | Caching, read replicas, horizontal scaling |
| 100,000+ | Sharding, distributed architecture |

**Example — WhatsApp:**
```
2 billion users, each sends 10 messages/day
= 20 billion messages/day
= 20B / 86,400 ≈ 230,000 messages/second average
× 5 for peak = ~1,000,000 RPS
```
One server handles ~1,000 RPS. You need ~1,000 servers minimum. This immediately tells you the architecture must be distributed.

---

### Question 3 — Is bandwidth a concern?

**Ask yourself**: is this system moving large amounts of data per request?

| Data per request | Bandwidth concern? |
|---|---|
| Text, small JSON (< 1KB) | No — throughput and latency dominate |
| Images, documents (100KB – 10MB) | Yes — bandwidth starts to matter |
| Video, large files (10MB+) | Critical — bandwidth is the primary bottleneck |

> [!info] The same system can have different bottlenecks for different features
> WhatsApp text messages → latency and throughput problem, bandwidth is fine
> WhatsApp media (photos, videos) → now bandwidth is a serious concern
> Design each feature path separately.

---

## Step 4 — Attach Percentiles to Make It Concrete

Now take your three answers and put real numbers on them using percentiles.

Without percentiles → *"low latency"*  
With percentiles → *"P99 latency under 200ms"*

That's the difference between a vague statement and a design target.

| Metric | How to express it with percentiles |
|---|---|
| Latency | *"P99 latency under Xms"* — 99% of requests must complete within X |
| Throughput | *"System must handle Y RPS at P95"* — 95% of the time traffic is under Y, design for peak |
| Bandwidth | *"P95 of file uploads complete within Z seconds for a NMB file"* |

---

## Worked Examples

### WhatsApp
| Metric | Assessment | Target |
|---|---|---|
| Latency | Human waiting for message — critical | P99 < 200ms for message delivery |
| Throughput | 1M RPS at peak | P95 sustained, design for 1M RPS peak |
| Bandwidth | Text only = tiny. Media = large | Text: not a concern. Media: CDN + compression needed |

### YouTube
| Metric | Assessment | Target |
|---|---|---|
| Latency | Upload — not critical. Playback start — critical | P99 < 3s for video playback start |
| Throughput | 500 hours of video uploaded per minute, billions of views | P95 read throughput must handle 10M+ concurrent viewers |
| Bandwidth | Video is massive — critical | CDN mandatory, adaptive bitrate streaming (serve lower quality on slow connections) |

### Google Search
| Metric | Assessment | Target |
|---|---|---|
| Latency | User waiting for results — extremely critical | P99 < 500ms, P50 < 100ms |
| Throughput | 100,000+ searches per second globally | Distributed across thousands of servers |
| Bandwidth | Text results — small. Images — moderate | CDN for image results |

### Dropbox
| Metric | Assessment | Target |
|---|---|---|
| Latency | Sync in background — not critical | P95 < 5s for small file sync |
| Throughput | Millions of sync events per day | Moderate — not the main concern |
| Bandwidth | Files can be large — critical | Chunked uploads, delta sync, compression |

---

## The Full Mental Checklist

Every time you get a system design question, run this before touching the diagram:

- [ ] Is a human waiting for a response? → sets your latency target → pick P99 or P999
- [ ] How many requests per second at peak? → sets your throughput target → drives scaling decisions
- [ ] How large is the data per request? → sets your bandwidth concern → drives CDN, compression, chunking decisions
- [ ] State all three as concrete numbers with percentiles before designing

> [!tip] What a strong hire says vs what a weak hire says
> ❌ Weak: *"We need low latency and high throughput"*
>
> ✅ Strong: *"This is a real-time chat system. P99 message delivery must be under 200ms since users are actively waiting. At 500M DAU sending 20 messages per day we're looking at ~115K RPS average and ~500K RPS peak — that rules out a single server architecture immediately. Messages are text so bandwidth is not a concern, but media sharing will need a CDN."*
>
> Same knowledge. Completely different impression.
