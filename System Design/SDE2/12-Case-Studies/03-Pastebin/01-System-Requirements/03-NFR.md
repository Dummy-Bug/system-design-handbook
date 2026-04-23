## Availability — 99.9% uptime

Pastebin is a user-facing, read-heavy service. A user who can't read a paste or can't create one has a bad experience. 99.9% (three nines) gives ~8.7 hours of acceptable downtime per year — enough headroom for deployments and incidents without being so strict that it forces overly expensive infrastructure.

This is a deliberate choice to prioritise availability over strong consistency. In CAP terms, we lean AP — when a network partition happens, we keep serving reads even if some replicas are slightly behind, rather than refusing requests until all nodes agree.

```
99.9%  = ~8.7 hours downtime/year   ← our target
99.99% = ~52 minutes downtime/year  (overkill for Pastebin)
99.5%  = ~43 hours downtime/year    (too loose for a user-facing product)
```

---

## Consistency — Eventual, with one exception

Because we prioritise availability, we accept **eventual consistency** across read replicas. When a paste is created, the write goes to the primary. Read replicas may lag by a few hundred milliseconds before they catch up. That's acceptable — if someone shares a link and a friend clicks it 5 seconds later, the replica will have synced by then.

**The one exception: read-your-own-writes.**

The creator needs to see their paste immediately after creation. If they click their own link right after creating the paste and get a 404, that's a broken experience. So the creator's reads are routed to the primary (or a sync replica) for a short window after creation — typically a few seconds. By the time they share the link externally, the replica has caught up.

```
Normal reads:          → read replica (eventual consistency, fine)
Creator's first read:  → primary or sync replica (read-your-own-writes guarantee)
```

---

## Latency SLO

```
Read  p99 < 50ms   (anyone viewing a paste)
Write p99 < 100ms  (creating a paste, getting back a short code)
```

**Why p99 and not mean or p95?**

Mean hides the long tail entirely. You could have 1% of users waiting 5 seconds and the mean still looks healthy. p95 is better but still lets 5% of requests miss the target — at 3,000 reads/sec peak that's 150 requests per second experiencing bad latency. p99 means 99 out of every 100 requests meet the SLO. Only 30 requests per second at peak are allowed to be slow. That's the right bar for a user-facing product.

Reads get a tighter SLO (50ms) than writes (100ms) because reads are 100× more frequent and the user is waiting to see content. Writes have a slightly looser SLO because the user expects a brief "saving" moment.

---

## Durability — zero data loss after ack

Once a user creates a paste and receives a short code back, that paste must not be lost — even if the server crashes 2 seconds later. This means writes must be persisted to disk (and replicated) before the system acknowledges success to the user. We do not return a short code until the write is durable.

This rules out async write patterns where the ack comes before the disk flush.

---

## Scalability — sharding required

Storage grows to ~150TB over 10 years (3.65B pastes × 10KB each × replication + index overhead). A single Postgres machine handles ~10TB practically. At 150TB, horizontal sharding is unavoidable. This is a known constraint from estimation — the deep dive covers shard key selection and consistent hashing.

---

## Fault Isolation — read and write services fail independently

The read path (view a paste) and the write path (create a paste) must not share failure modes. If the creation service goes down, existing pastes must still be readable. If a read replica crashes, paste creation must still work.

This is achieved by separating the read and write fleets — distinct app server pools, distinct load balancers, so a deployment or crash on the write side does not take down the read side.

---

## Reliability — short codes are immutable and correct

> [!important] A short code must always resolve to exactly the paste it was created with — never someone else's content, never a different version.

This is a reliability guarantee, not a consistency one. It's about correctness: the system does what it's supposed to do, every time. This rules out any design where paste content can be overwritten after creation. Pastes are **write-once** — once created, the content is immutable. Only the creator can delete the paste (which tombstones it), but they cannot change its content.

---

## Summary

```
Availability:     99.9% uptime — AP over CP
Consistency:      Eventual — read replicas may lag briefly
                  Exception: read-your-own-writes for creator
Latency:          p99 < 50ms reads | p99 < 100ms writes
Durability:       Zero loss after ack — sync write to disk before returning short code
Scalability:      Sharding required — 150TB exceeds single-machine limit
Fault isolation:  Read and write services fail independently
Reliability:      Short codes are immutable and always resolve to correct content
```

---

> [!tip] Interview framing
> "Read-heavy user-facing system — prioritise availability over strong consistency, eventual consistency is fine. One exception: read-your-own-writes for the creator. Latency SLOs at p99 — reads p99 < 50ms, writes p99 < 100ms. p99 because mean hides the long tail and p95 still leaves 150 requests/sec at peak with bad latency. Durability: zero loss after ack. Fault isolation: read and write fleets must fail independently."
