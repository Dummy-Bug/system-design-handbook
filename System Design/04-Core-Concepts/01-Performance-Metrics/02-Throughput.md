# Throughput

> [!question] How many requests can your system handle per second?
> That's throughput. Unlike latency which measures one request, throughput measures the system's total capacity.

---

## Latency vs Throughput — the distinction

You already know latency — how long one request takes, end to end, from the moment the client sends the request to the moment the response arrives back.

Throughput is also measured end to end — a request is only counted as "served" when the full response is back at the client.

The difference is what they're counting:
- **Latency** — how long did that round trip take for one request
- **Throughput** — how many complete round trips happened per second

---

## The units

| Term | Used for |
|---|---|
| **RPS** (Requests Per Second) | General APIs and services |
| **QPS** (Queries Per Second) | Databases specifically |
| **bps / Mbps / Gbps** (bits per second) | Data transfer — video streaming, file uploads |

> [!info] RPS and QPS mean the same thing
> Just different terms depending on context. In interviews you'll hear both — they're interchangeable.

---

## Start simple — one request at a time

At its most basic, a server processes **one request at a time**.

Request comes in → server works on it → sends response back → only then picks up the next one.

If one request takes 100ms:

```
1000ms / 100ms = 10 requests per second
```

That's it. **10 RPS.** Any extra requests arriving during that time just sit in a queue and wait.

---

## Now introduce threads

In reality, servers don't work like this. They use **threads**.

A thread is like a worker inside the server. Each thread handles one request independently. Multiple threads run in parallel — so multiple requests get processed at the same time.

Add 10 threads to that same server:

```
10 threads × 10 requests/sec each = 100 RPS
```

Same server. Same 100ms latency per request. Just 10 workers running in parallel instead of 1.

> [!tip] The formula
> Step 1 — how many requests can one thread handle per second?
> `1000ms / latency per request = requests per second per thread`
>
> Step 2 — multiply by number of threads:
> `Throughput = Threads × (1000ms / Latency per request)`
>
> | Threads | Latency | Requests/sec per thread | Throughput |
> |---|---|---|---|
> | 1 | 100ms | 1000/100 = 10 | 1 × 10 = **10 RPS** |
> | 10 | 100ms | 1000/100 = 10 | 10 × 10 = **100 RPS** |
> | 100 | 100ms | 1000/100 = 10 | 100 × 10 = **1,000 RPS** |

---

## What actually happens under real load

Every web server runs with a **thread pool** — a fixed number of threads ready to handle requests simultaneously.

Here's what happens as traffic grows:

1. Requests arrive → free threads pick them up → processed in parallel ✅
2. More requests arrive than free threads → they sit in a **queue** and wait ⏳
3. Queue fills up completely → server starts **rejecting** requests ❌

That rejection is the **503 Service Unavailable** error. The server isn't broken — every thread is busy and the queue is full. It has no choice but to turn requests away.

This is exactly what happens when a big sale hits Amazon or tickets go on sale for a concert — servers get overwhelmed not because they're broken but because all threads are occupied.

> [!warning] Threads are not free
> Each thread consumes RAM. You can't just set threads to 10,000 and call it done. There's a hard limit based on how much memory the server has. This is a real constraint engineers tune in production.

---

## How to increase throughput

Two levers:

1. **Reduce latency** — if each request is faster, each thread handles more requests per second
2. **Add more threads / more servers** — more parallel workers = more concurrent requests handled


---

## Real world numbers

| System | Throughput |
|---|---|
| A basic single-thread server | ~10–50 RPS |
| A typical production app server (50–200 threads) | ~500–5,000 RPS |
| Nginx (reverse proxy, event-driven) | ~50,000+ RPS on a single machine |
| Google Search | ~100,000+ RPS globally |
| WhatsApp at peak | ~500,000+ messages per second |
| Kafka (message queue) | Millions of messages per second per broker |

> [!info] Why Nginx handles so much more than a typical app server
> Nginx doesn't use one thread per request. It uses an **event-driven** model — a small number of threads handle thousands of connections by never blocking and waiting. This is an advanced topic we'll cover later.
