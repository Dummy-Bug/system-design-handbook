
## Latency — critical

The ID generator is called inline by other backend systems. Every time a user sends a tweet, places an order, or sends a message — the calling service is blocked waiting for an ID before it can write to the database. If this service is slow, every single write in the entire platform slows down with it.

This is not a background job. It is on the critical path. Latency must be in the single-digit milliseconds at p99.

---

## Availability — critical

If the ID generator is down, the calling service cannot create new records. No new tweets. No new orders. No new messages. The entire write path of every system that depends on this service goes down with it.

High availability is non-negotiable. The service must always return an ID.

---

## Uniqueness — hard correctness requirement, not a trade-off

This is the most important property — and the one most likely to be misunderstood in an interview.

At first glance, uniqueness might look like a consistency problem. You might think: "if I relax consistency, two servers might briefly generate the same ID, but eventually it gets sorted out." That reasoning is wrong, and dangerously so.

If two servers generate the same ID for two different callers, both callers write to the database using that ID as a primary key or foreign key. Now you have two completely different records — a tweet from Alice and an order from Bob — sharing the same ID. The database constraint fires, one write fails, or worse, they silently overwrite each other. There is no recovery path. The data is corrupted permanently.

Uniqueness is not a consistency trade-off. It is a correctness requirement with no eventual fix.

> [!danger] "We can relax consistency here" is wrong
> Consistency in CAP means: if you write a value to Node A, will Node B return that value when you read it? That question doesn't apply to an ID generator — nobody reads from this service. It only generates and returns. There is no shared state to be consistent about, so CAP consistency is simply not relevant here. Don't bring it up in an interview — it shows a misunderstanding of what this service does.

---

## Why CAP doesn't apply the way you'd expect

CAP theorem talks about a system that stores and serves data — you write something, then read it back, and the question is whether all nodes agree on what the current value is.

The ID generator does none of that. A request comes in. An ID goes out. There is no data stored on this service that needs to be replicated or kept in sync across nodes. Each node generates IDs independently.

The real question during a network partition is: should a node stop generating IDs because it can't coordinate with other nodes? The answer is no — because if the design is correct, each node can generate guaranteed-unique IDs on its own, without ever needing to talk to another node. Availability and uniqueness are both achievable simultaneously. This is a design problem, not a CAP trade-off.

---

## Fault Isolation — important

At 10M IDs/second peak, this service will run on multiple nodes. If one node crashes or becomes unresponsive, the callers connected to that node should fail over to another node. The failure of one node must not cascade — other nodes must keep generating IDs normally.

---

## Summary

| NFR | Requirement |
|---|---|
| Latency | Single-digit ms at p99 — on the critical write path |
| Availability | Must always return an ID — write path depends on it |
| Uniqueness | Hard correctness requirement — no duplicate IDs ever |
| Consistency (CAP) | Not applicable — service generates, never stores or serves |
| Fault Isolation | One node down must not affect other nodes |
