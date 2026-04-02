# Throughput

> [!question] How many requests can your system handle per second?
> That's throughput. Unlike latency which measures one request, throughput measures the system's total capacity.

---

## Latency vs Throughput — the distinction

You already know latency — how long one request takes.

Throughput is different. It doesn't care about one request. It asks: **how much total work can the system process per unit of time?**

One server responds to your request in 50ms — that's latency.  
Can that same server handle 10 requests simultaneously? 1,000? 100,000? — that's throughput.

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

## A concrete example

One server handles each request in 100ms.

That means it can handle **10 requests per second** maximum — each request occupies the server for 100ms, and there are 1000ms in a second.

Add a second identical server → **20 requests per second**.  
Add 10 servers → **100 requests per second**.

Same latency per request. Throughput doubled, then multiplied by 10.

> [!tip] This is the core idea behind horizontal scaling
> You don't make each server faster. You add more servers to increase throughput.
> Latency stays the same. Capacity grows.

---

## Why throughput matters in system design

When an interviewer gives you a scale requirement — *"the system needs to handle 500,000 users per day"* — your first job is to convert that into QPS. That number then drives every architecture decision.

- Low throughput requirement → a single server might be fine
- High throughput requirement → you need load balancers, multiple servers, database replicas

We'll cover exactly how to calculate QPS from user numbers in the Estimation phase.
