
> [!info] The in-memory queue — a buffer inside the app server
> Every request that lands on the app server goes into an in-memory queue before being picked up by a thread. The queue is the buffer that absorbs the spike. When the queue is full, the server rejects.

---

## How the app server processes requests

The app server runs a thread pool — a fixed number of threads that process requests concurrently. When a request arrives, it doesn't go directly to a thread. It joins a queue first. A free thread picks it up when it's ready.

```
Incoming requests → [in-memory queue] → [thread pool] → controller → DynamoDB
```

This is built into the web framework — Go, Java, Node all work this way. You configure two numbers and the framework handles the rest:

```
max_threads: 200      (how many requests processed concurrently)
queue_size:  50,000   (how many requests can wait before rejection)
```

---

## How the numbers are set

You don't guess — you load test. You gradually increase traffic on the app server and measure latency. The point where latency starts spiking is your capacity limit.

Say load testing shows one app server handles 10,000 requests/second comfortably. You set:

```
queue_size = 50,000   (5 seconds of buffer at peak load)
```

At 10K RPS, the queue fills in 5 seconds if no threads are free. Auto-scaling needs 2-3 minutes. So the queue alone isn't enough to absorb the full gap — but combined with some requests being processed normally, it buys significant time before rejections start.

---

## The full flow under load

```
Normal load (5K RPS):
→ Requests arrive → queue at ~50% → threads process → queue stays healthy

Spike (20K RPS):
→ Requests arrive faster than threads process
→ Queue grows: 1K → 5K → 20K → 50K
→ Queue full → new requests rejected (429)
→ Auto-scaling triggers, new servers spin up (2-3 min)
→ Load distributes across new servers
→ Queue drains → system back to normal
```

The queue absorbs the initial spike. Rejections protect the server from crashing. Auto-scaling restores full capacity.

> [!tip] Interview framing
> "Each app server has an in-memory request queue in front of the thread pool — this is standard in any web framework. Queue capacity is set based on load testing. When the queue fills, we reject with 429. Auto-scaling runs in parallel and restores capacity within 2-3 minutes."
