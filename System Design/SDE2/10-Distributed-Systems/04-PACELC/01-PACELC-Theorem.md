# PACELC Theorem

## Why CAP Was Incomplete

> [!info] CAP theorem only describes trade-offs **during a network partition**. It says nothing about what your system trades away during normal operation.

Partitions are rare. Your system is healthy 99.9% of the time. CAP is silent about that.

```
CAP asks: "partition is happening — consistency or availability?"
CAP ignores: the other 99.9% of the time

The gap: even without a partition, if you want every read to return
         the latest write, you must wait for replicas to confirm.
         That wait = latency.
         Skipping the wait = potentially stale data = weaker consistency.
```

This trade-off — latency vs consistency — exists on **every single request**, failure or not.

PACELC captures it.

---

## The Theorem — An If-Else Statement

> [!info] PACELC is literally an if-else: during a partition, choose A or C. Otherwise, choose L or C.

```
IF   partition happens
THEN choose: Availability  vs  Consistency   (the CAP trade-off)

ELSE (normal operation)
THEN choose: Latency       vs  Consistency   (the new trade-off)
```

The name spells it out:

```
P  → Partition?
A  → Availability     ─┐  what you pick during partition
C  → Consistency      ─┘

E  → Else (normal operation)
L  → Latency          ─┐  what you pick during normal operation
C  → Consistency      ─┘
```

---

## The Four Combinations

Every distributed system gets a two-part label: what it does during partition / what it does normally.

### PA/EL — Available during partition, fast normally

> [!info] Stay up during failures. Be fast during normal operation. Consistency is secondary in both cases.

```
Partition: keep serving → may return stale data          (PA)
Normal:    respond fast → don't wait for replicas        (EL)
```

**Classic examples:** DynamoDB, Cassandra, CouchDB

**Use when:** Availability and speed matter more than perfect freshness. Social feeds, shopping carts, sensor data.

---

### PC/EC — Consistent always

> [!info] Correctness over everything. Refuse requests during partition. Accept higher latency normally.

```
Partition: stop serving → wait for quorum to restore     (PC)
Normal:    wait for replicas to agree before responding  (EC)
```

**Classic examples:** Zookeeper, HBase, Google Spanner

**Use when:** Wrong data causes more damage than being slow or unavailable. Financial transactions, leader election, distributed locks.

---

### PA/EC — Available during partition, consistent normally

> [!info] Strict when healthy. Lenient when a partition forces it.

```
Partition: keep serving → accepts stale data             (PA)
Normal:    enforce consistency → wait for replicas       (EC)
```

**Classic example:** MongoDB (default config)

This is the unusual middle ground — covered in detail in the next file.

---

### PC/EL — ~~Consistent during partition, fast normally~~

> [!danger] This combination doesn't make sense and you will almost never see it in the wild.

```
PC says: "during a partition, refuse requests to stay consistent"
EL says: "normally, respond fast even if data might be stale"

The contradiction:
  You're willing to go down during failures to protect consistency
  But during normal operation you accept stale data anyway?

  You paid the price of unavailability for nothing.
  The whole point of PC is that consistency is sacred.
  Abandoning it in normal operation makes PC meaningless.
```

---

## The Spectrum

```
Strictest ─────────────────────────────────── Loosest

PC/EC  →  consistent always, may be unavailable
PA/EC  →  consistent normally, available during failure
PA/EL  →  available always, fast always, eventual consistency
```

> [!important] Consistency always costs latency. There is no free lunch. Every system picks a side — even when nothing is broken.
