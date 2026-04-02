# Active-Active vs Active-Passive

> [!question] You have redundant servers. But should both serve traffic or should one just wait?
> That's the Active-Active vs Active-Passive decision — and it's primarily about complexity and data consistency, not load.

---

## Active-Passive

Two servers. Server A handles all traffic. Server B sits idle as a hot standby — on, ready, but serving nothing.

```
Users → Load Balancer → Server A (active)
                      → Server B (passive, idle)
```

If Server A dies → traffic switches to Server B → Server B starts serving.

**Pros:**
- Simple — no split traffic, no concurrent writes, no consistency headaches
- Clean failover — B is a fresh copy of A

**Cons:**
- Paying for a server doing nothing 99% of the time
- Small failover delay when switching from A to B
- Until a new passive is set up, you're back to a SPOF

---

## Active-Active

Two servers. Both A and B serve traffic simultaneously. Load is distributed between them.

```
Users → Load Balancer → Server A (active, 50% traffic)
                      → Server B (active, 50% traffic)
```

If Server A dies → Server B absorbs 100% of traffic. No switchover needed — B was already serving.

**Pros:**
- No failover delay — B is already live
- No wasted resources — both servers are doing useful work
- Better load distribution

**Cons:**
- Complex — both servers are writing and reading simultaneously
- Consistency problem — what if A and B both write to the same data at the same time? Conflicts.
- Much harder to manage for stateful components like databases

---

## The Real Deciding Factor — Statefulness

> [!info] This is not primarily a load decision — it's a consistency decision

Before understanding the decision, you need to know what stateless and stateful mean:

**Stateless** — the server does not remember anything between requests. Every request carries all the information the server needs to process it. The server handles it and forgets about it completely.

Example — an API server handling a "get user profile" request. It receives the request, fetches the data, returns it, done. It doesn't remember that request ever happened. Any server can handle any request because none of them hold any state.

**Stateful** — the server remembers things between requests. It holds data that persists and changes over time.

Example — a database. It stores your users' data permanently. If Server A writes a new user record, that data now lives on Server A. If Server B doesn't have that same data, it can't serve it correctly.

---

Now the decision makes sense:

**Stateless components** (app servers, API servers) — Active-Active is easy. Each request is independent, no shared data between servers. Both servers can handle any request without conflicting. It doesn't matter which server handles your request — they all give the same answer.

**Stateful components** (databases, caches) — Active-Active is hard. Two nodes accepting writes simultaneously = potential conflicts. What if Server A and Server B both try to update the same user's balance at the same time? You get inconsistent data, corruption, or split-brain (both think they're the source of truth but have different data).

This is why most databases default to Active-Passive — one primary writer, one replica that only reads.

> [!info] We'll go much deeper into stateless vs stateful in the Scalability section
> This is just enough context to understand the availability decision here.

---

## The Hybrid — What Most Real Systems Use

Stateless app servers → **Active-Active** (simple, no consistency issues)
Databases → **Active-Passive** (one primary writer, replica on standby)

```
Users → Load Balancer → App Server A  ←→  Primary DB (active)
                      → App Server B  ←→  Replica DB (passive)
```

If Primary DB dies → Replica is promoted to Primary → new replica spun up to restore redundancy.

> [!tip] Active-Active for stateless, Active-Passive for stateful
> This is the standard pattern in almost every production system you'll design in interviews.

---

## Quick Reference

| | Active-Passive | Active-Active |
|---|---|---|
| Both servers serving? | No — one idles | Yes — both live |
| Failover delay? | Small delay on switch | None — already active |
| Resource efficiency? | Wasteful | Efficient |
| Complexity? | Simple | Complex |
| Works for databases? | Yes — standard pattern | Hard — consistency issues |
| Works for app servers? | Yes but wasteful | Yes — preferred |
