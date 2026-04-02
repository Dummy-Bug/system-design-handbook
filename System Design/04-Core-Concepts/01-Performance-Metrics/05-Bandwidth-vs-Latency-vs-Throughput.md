# Bandwidth vs Latency vs Throughput

> [!question] These three keep coming up together — what exactly is each one measuring?
> They sound related but they are three completely different rulers measuring three different things.

---

## The Three Rulers

| Metric | What it measures | Unit |
|---|---|---|
| **Latency** | Time for one round trip | milliseconds (ms) |
| **Throughput** | How many requests per second | RPS / QPS |
| **Bandwidth** | How many bits of data flow per second | Mbps / Gbps |

---

## The Critical Distinctions

### Latency doesn't care about data size
Whether your request carries 1 byte or 1 MB — latency only measures the round trip time. A ping to a server is essentially 0 bytes of data but it still has latency. Data size is irrelevant.

### Throughput counts requests, not data
A system processing 10,000 requests per second has high throughput — even if each request is just a tiny 10 byte ping. Throughput is about **how many**, not **how much data**.

### Bandwidth counts data, not requests
A system serving one user downloading a 4K movie is transferring massive amounts of data per second — high bandwidth usage. But throughput is just 1 request. Bandwidth is about **how much data**, not **how many requests**.

---

## Where the confusion comes from

Throughput and bandwidth both feel like "capacity" metrics — and they are, just for different things.

| Scenario | Throughput | Bandwidth |
|---|---|---|
| Millions of tiny API pings | Very high | Very low |
| One user downloading a 4K movie | Very low | Very high |
| Millions of users streaming HD video | Very high | Very high |
| One user sending a chat message | Very low | Very low |

> [!info] You can have high throughput with low bandwidth and vice versa
> They are independent. Always check both separately.

---

## A single analogy that covers all three

Imagine a highway full of trucks delivering packages:

- **Latency** — how long does one truck take to travel from warehouse to destination and back?
- **Throughput** — how many trucks complete their delivery per hour?
- **Bandwidth** — how many kilograms of packages are delivered per hour in total?

A truck's travel time (latency) doesn't change based on how many other trucks are on the road.
More trucks per hour = higher throughput.
Bigger packages per truck = higher bandwidth usage.

---

## How to apply this in every case study

For every system you design, ask all three questions:

**1. Latency** — is response time for a single request acceptable?
- Chat message → must be under 100ms, user is waiting
- Batch report → minutes are fine, nobody is waiting

**2. Throughput** — can the system handle the volume of requests?
- Social media feed → millions of users refreshing simultaneously
- Internal admin dashboard → a few hundred users, no problem

**3. Bandwidth** — is the data volume manageable?
- Video streaming → massive, need CDN and compression
- Text-based chat → tiny, bandwidth is not the concern

> [!tip] The three questions to ask for every case study
> Before designing anything, identify which of these is the bottleneck:
> - **Latency** — is response time for a single request too slow? (e.g. chat message delay)
> - **Throughput** — can the system handle the volume of requests? (e.g. 100K users hitting the API simultaneously)
> - **Bandwidth** — is the volume of data being transferred too large for the pipe? (e.g. serving 4K video to millions)
>
> Each has completely different solutions. A bandwidth problem is not solved by adding more servers. A throughput problem is not solved by moving servers closer to users. Identify the bottleneck first, then design.

> [!warning] Each bottleneck has a different solution
> - Latency problem → move data closer to users (cache, CDN, edge servers)
> - Throughput problem → add more servers, more threads, horizontal scaling
> - Bandwidth problem → compress data, upgrade network pipes, use CDN for large files
>
> Solving the wrong bottleneck wastes time and money. Identify which one is failing first.
