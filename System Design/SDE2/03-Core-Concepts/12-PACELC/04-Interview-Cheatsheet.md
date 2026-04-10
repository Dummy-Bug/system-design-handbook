# PACELC — Interview Cheatsheet

## The One-Liner

> [!info] Say this when PACELC comes up:
>
> "CAP tells you what to sacrifice during failures. PACELC goes further — even without failures, consistency always costs latency. Every system picks a side on both dimensions."

---

## The Two Questions To Ask

```
Question 1 (partition behavior):
  Which is worse — wrong data or no response?
  Wrong data worse  → PC (refuse requests, stay consistent)
  No response worse → PA (serve stale, stay available)

Question 2 (normal operation):
  Can you afford the latency of waiting for replicas?
  No  → EL (respond fast, accept eventual consistency)
  Yes → EC (wait for replicas, enforce freshness)
```

---

## The Four Labels — When To Use Each

| Label | Meaning | Use when |
|---|---|---|
| PA/EL | Available + fast | Social, carts, feeds, anything where brief staleness is fine |
| PC/EC | Consistent always | Financial, locks, coordination, anything where wrong data is catastrophic |
| PA/EC | Available during failure, consistent normally | General-purpose systems, mixed workloads (MongoDB) |
| PC/EL | ~~Consistent during failure, stale normally~~ | Doesn't exist — contradictory |

---

## Applying It — Social Feed (PA/EL)

> [!example] "Design Instagram. What DB and consistency model?"

```
Partition: user's feed must stay up — stale like count is fine     PA
Normal:    respond fast — don't wait for all replicas              EL

"This needs PA/EL. A slightly stale feed is acceptable.
 Going down is not. I'd use Cassandra."
```

---

## Applying It — Payment System (PC/EC)

> [!example] "Design a payment processor. What DB and consistency model?"

```
Partition: refuse requests — wrong balance causes financial loss   PC
Normal:    wait for confirmation — stale balance is unacceptable   EC

"This needs PC/EC. A failed transaction is recoverable.
 A wrong transaction destroys trust. I'd use Postgres or Spanner."
```

---

## Applying It — Real-Time Chat (PA/EL)

> [!example] "Design WhatsApp. What consistency model?"

```
Partition: keep serving — 2 billion users can't go dark            PA
Normal:    respond fast — slight message reordering is acceptable  EL

"This needs PA/EL. Availability for billions is non-negotiable.
 Eventual consistency on message ordering is fine. Cassandra."
```

---

## PACELC vs CAP — The Difference

> [!important] Know when to use each in conversation.

```
CAP  → use when discussing failure behavior
       "During a partition, does this system pick C or A?"

PACELC → use when discussing both failure AND normal behavior
         "At all times, what is this system trading?"

PACELC is a superset of CAP — it includes the CAP trade-off
plus the latency-consistency trade-off during normal operation.
```

---

## Common Traps

> [!warning] Things interviewers specifically test

**"PC/EL exists" trap:**
```
Wrong: "We can be consistent during partitions but fast normally"
Right: "PC/EL is contradictory — if consistency is sacred enough
        to refuse requests during a partition, serving stale data
        normally defeats the whole point. You'll never see this."
```

**"PACELC replaces CAP" trap:**
```
Wrong: "PACELC makes CAP obsolete"
Right: "PACELC extends CAP. The P/A and P/C labels in PACELC
        are exactly the CAP trade-off. PACELC just adds the
        E/L/C dimension for normal operation."
```

**"Tunable means no trade-off" trap:**
```
Wrong: "Cassandra is tunable so it avoids the trade-off"
Right: "Cassandra is PA/EL by default. Tuning to ALL makes it
        behave like PC/EC — but now you pay the latency and
        availability cost. The trade-off still exists.
        Tunable just means you pick per-operation."
```

---

## Quick Reference — System Labels

| System | Label | Reason |
|---|---|---|
| DynamoDB | PA/EL | availability + low latency always |
| Cassandra | PA/EL | massive write throughput, eventual consistency |
| CouchDB | PA/EL | offline-first, conflict resolution on merge |
| Zookeeper | PC/EC | coordination data — wrong info = catastrophe |
| Google Spanner | PC/EC | global financial data, linearizability |
| HBase | PC/EC | strong consistency on Hadoop |
| MongoDB | PA/EC | general purpose, tunable, mixed workloads |

---

## Full Checklist

- [ ] State what PACELC adds over CAP (the EL/EC dimension)
- [ ] Identify the data type → financial/coordination → PC/EC, social/analytics → PA/EL
- [ ] Ask: which is worse during partition — wrong data or no response?
- [ ] Ask: can you afford the latency of waiting for replicas normally?
- [ ] Name the label explicitly (PA/EL, PC/EC, PA/EC)
- [ ] Name the DB and why it matches the label
- [ ] If asked about MongoDB — explain it's a general-purpose middle ground, not the right choice when you need a clear guarantee
- [ ] Never say PC/EL is a valid choice — call it out as contradictory
- [ ] Connect back to CAP: PACELC extends it, doesn't replace it
