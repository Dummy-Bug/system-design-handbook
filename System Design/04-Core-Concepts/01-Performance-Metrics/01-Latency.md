# Latency

> [!question] How long does one request take from start to finish?
> That duration is latency.

---

## The Restaurant Analogy

You sit down and order pasta. The clock starts.

The waiter walks to the kitchen, the chef cooks it, the waiter walks back, the plate lands on your table. The clock stops.

**That total time = latency.**

It doesn't matter how many other tables are being served. Latency is only about **your one request**.

---

## Where does the time actually go?

A request doesn't teleport. Time is spent at every step:

| Step | What's happening |
|---|---|
| **Network** | Data physically travelling over wires between client and server |
| **Queuing** | Your request sitting in a waiting line before a thread picks it up |
| **Compute** | The server doing actual work — business logic, calculations |
| **I/O** | Reading from a database or disk |

> [!warning] I/O is almost always the dominant cost
> This is the one that surprises beginners. The server doing calculations is fast. Waiting for data from disk is what kills latency.

---

## Why is a database call so slow?

Your server has two places it can get data from:

**RAM** — memory that lives inside the server itself. Accessing it is nearly instant because it's physically right there on the same chip. Like grabbing something off your desk.

**Disk** — where the DB permanently stores its data. This is a completely separate physical device. Every time your server needs data from the DB, it has to:
1. Send a request to the disk — *"give me this data"*
2. Wait for the disk to physically locate it
3. Transfer it back

That round trip is slow. And the reason databases live on disk — not RAM — is that **disk survives a server restart**. RAM gets wiped the moment the power goes off. You can't store your users' data there permanently.

> [!info] The numbers that make this real
> | Where data lives | Time to access |
> |---|---|
> | RAM | ~100 nanoseconds |
> | SSD (disk) | ~150 microseconds |
> | HDD (spinning disk) | ~10 milliseconds |
> | Network call (same datacenter) | ~0.5 milliseconds |
> | Network call (US → Europe) | ~150 milliseconds |
>
> SSD is **1,500x slower** than RAM.
> HDD is **100,000x slower** than RAM.

This single fact explains why caching exists — you're just copying frequently needed data from slow disk into fast RAM so the next request doesn't have to wait.

---

## High latency vs Low latency

Not every system needs to be fast. But you need to **know your target**.

- **Low latency systems** — Google Search (~200ms), stock trading (~1ms), games (<50ms)
- **High latency is acceptable** — batch report generation (minutes), video transcoding (hours)

> [!tip] In an interview — never say "the system should be fast"
> Always give a specific number. Example: *"latency should be under 100ms"*
