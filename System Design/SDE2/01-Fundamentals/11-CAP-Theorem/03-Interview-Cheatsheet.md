# CAP Theorem — Interview Cheatsheet

## The Four-Step Formula

> Say this out loud in every design interview where storage or consistency comes up.

```
Step 1: What consistency does this data need?
  Financial, locks, leader election → linearizability → CP
  Social, analytics, preferences    → eventual/causal → AP

Step 2: What happens if this system is unavailable?
  Users lose money, critical infra breaks → tolerate unavailability (CP)
  Users see stale feed, minor annoyance   → tolerate staleness (AP)

Step 3: Which is worse — wrong data or no response?
  Wrong data worse  → CP
  No response worse → AP

Step 4: State the choice and justify it
  "This system needs CP because stale [X] would cause [Y]"
  "This system needs AP because unavailability would cause [Y]"
```

---

## Applying It — Payment System (CP)

> [!example] "Design a payment processing system. What consistency model?"

```
Step 1: Financial data — needs linearizability
        Stale balance → charge against non-existent funds → financial loss

Step 2: If unavailable → user sees "try again" → calls support → recoverable

Step 3: Wrong data (double charge, missing debit) is catastrophic
        No response is recoverable

Step 4: "This needs CP. A failed transaction is recoverable.
         A wrong transaction destroys trust and violates regulations."

DB choice: PostgreSQL with SERIALIZABLE isolation
           Or Google Spanner (globally consistent)
```

---

## Applying It — Chat System (AP)

> [!example] "Design WhatsApp. What consistency model?"

```
Step 1: Message delivery — needs availability, not linearizability
        Slight reordering or eventual delivery is acceptable

Step 2: If unavailable → 2 billion users can't send messages → unacceptable

Step 3: Slightly delayed message delivery is annoying
        2 billion users unable to communicate is catastrophic

Step 4: "This needs AP. Availability is non-negotiable at this scale.
         We accept eventual consistency — messages deliver, maybe slightly out of order."

DB choice: Cassandra (AP, eventually consistent, massive write throughput)
```

---

## Applying It — Hotel Booking (CP)

> [!example] "Design a hotel booking system. CP or AP?"

```
Step 1: Inventory (room availability) needs strong consistency
        Stale room count → two users book same room → double booking

Step 2: If unavailable → user retries → minor inconvenience

Step 3: Double booking = hotel ops problem, customer service nightmare
        Unavailability = user tries again in 10 seconds

Step 4: "This needs CP. Double booking is a serious business problem.
         Temporary unavailability is acceptable."

DB choice: PostgreSQL with SELECT FOR UPDATE or SERIALIZABLE
```

---

## Quick Reference — CP or AP?

| System | Choice | One-line reason |
|---|---|---|
| Payment processing | CP | Wrong balance = financial loss |
| Bank transfer | CP | Money cannot be lost or duplicated |
| Hotel booking | CP | Double booking = serious problem |
| Leader election | CP | Stale = split-brain |
| Distributed locks | CP | Stale = race condition |
| Kubernetes config (etcd) | CP | Wrong config = cluster corruption |
| Social feed | AP | Slight staleness acceptable |
| Shopping cart | AP | Availability > perfect consistency |
| Chat messages | AP | Availability for billions of users |
| Like / view counter | AP | Off by a few is fine |
| DNS | AP | Global availability non-negotiable |
| Leaderboard | AP | Approximate is fine |

---

## Things Interviewers Specifically Test

> [!warning] Common traps

**"CA system" trap:**
```
Wrong answer: "We'll sacrifice partition tolerance"
Right answer: "CA doesn't exist in distributed systems.
               Partitions will happen — the real choice is CP or AP."
```

**"C in CAP" trap:**
```
Wrong answer: "C means the data is consistent"
Right answer: "C in CAP specifically means linearizability —
               every read sees the latest write globally.
               AP systems still have eventual consistency — they just
               can't guarantee linearizability during a partition."
```

**"When does CAP apply" trap:**
```
Wrong answer: "CAP governs the whole system"
Right answer: "CAP only describes behavior DURING a network partition.
               During normal operation, you can have both C and A.
               The choice matters for how you behave in failure cases."
```

**"Same DB can be CP or AP" — tunable consistency:**
```
Cassandra with ONE   → AP (available, potentially stale)
Cassandra with ALL   → CP (consistent, may be unavailable)
DynamoDB eventually consistent reads → AP
DynamoDB strongly consistent reads   → CP
```

---

## Full Checklist

- [ ] State P is non-negotiable — partitions WILL happen
- [ ] Identify the data type — financial/locks → CP, social/analytics → AP
- [ ] Identify what "unavailable" costs vs what "stale" costs
- [ ] State which is worse — wrong data or no response
- [ ] Name the CP or AP choice explicitly with justification
- [ ] Name the DB that matches the choice
- [ ] If asked about tunable systems (Cassandra/DynamoDB) — explain per-operation control
- [ ] Never say "CA system" — call it out as a myth
- [ ] Remember: C in CAP = linearizability, not "eventual consistency"
