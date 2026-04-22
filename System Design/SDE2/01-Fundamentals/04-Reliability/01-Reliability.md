> [!question] Your system is up and users can reach it. But are they getting correct answers?
> That's reliability. And it's a completely different problem from availability.

---

## What it is

You've already covered availability — keeping the system reachable. But a system can be perfectly available and completely broken at the same time.

Reliability is the next layer — ensuring that when the system responds, the response is **correct**.

**Reliability = the system gives correct answers consistently over time.**

Not just "is it running" — but "when it runs, does it do the right thing?"

---

## Available but Wrong — It Happens More Than You Think

**Example 1 — Pricing bug**
Your e-commerce site is up. Users can access it. But due to a bug in the pricing service, every product is showing $0. The system is available — users are getting responses. But it is unreliable — the responses are wrong.

**Example 2 — Message ordering bug**
Your chat app is up. Messages are being delivered. But due to a replication lag bug, some users are seeing messages out of order. Available? Yes. Reliable? No.

**Example 3 — Stale cache**
Your news feed is loading. But the cache hasn't been invalidated and users are seeing posts from 3 hours ago as "new". Available? Yes. Reliable? No — the data is stale.

> [!warning] Availability and reliability are independent problems
> A system can be fully available and completely unreliable at the same time. How they differ and how to solve each — see `04-Reliability-vs-Availability.md`.
