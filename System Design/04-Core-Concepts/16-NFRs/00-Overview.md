# Non-Functional Requirements — Overview

> Functional requirements define what the system does. NFRs define how well it does it. Every major design decision traces back to an NFR.

> [!abstract] NFRs are the bridge between a problem statement and architecture decisions. The same feature — "users can post tweets" — has completely different architectures depending on the NFRs. Extract them before designing anything. State them explicitly. Every choice you make should reference back to one.

---

## Functional vs Non-Functional

```
Functional     → what the system does
                 "users can post tweets"
                 "users can follow each other"
                 "users can see a feed"

Non-Functional → how well the system does it
                 "feed loads in under 200ms"
                 "system is available 99.99% of the time"
                 "data is never lost"
```

---

## Why NFRs Come Before Design

Without NFRs, you cannot make a single architecture decision confidently.

```
"Design a feed system"

Without NFRs:             With NFRs:
Which DB? No idea.        Availability > consistency → Cassandra
How many servers? No idea. 500M users, 1M writes/sec → sharding + queues
Cache or not? No idea.    Feed must load < 200ms → cache required
```

> [!important] In every interview — extract NFRs before drawing a single box. Every design decision you make should reference back to one.
> "I'm choosing Cassandra here because the NFR is high availability and eventual consistency is acceptable."

---

## Files in this folder

| File | Topic |
|---|---|
| 01-NFRs-And-Design-Decisions.md | All 6 NFRs — what each forces, what each costs |
| 02-Conflicting-NFRs.md | When two NFRs fight, how to handle it in interviews |
