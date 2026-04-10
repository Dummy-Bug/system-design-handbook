# CP vs AP — When to Choose Each

## The Core Question

> [!question] Which is worse for your system — wrong data or no response?

```
Wrong data worse  → CP (stop serving, stay consistent)
No response worse → AP (serve stale, stay available)
```

---

## CP Systems — Consistency over Availability

> [!info] CP systems stop serving requests during a partition rather than risk returning stale or wrong data.

**Behavior during partition:**
```
Partition happens → node can't reach quorum
→ stops accepting reads and writes
→ returns error: "service temporarily unavailable"
→ waits for partition to heal
→ resumes when quorum restored
```

**Why CP is the right choice:**

When wrong data causes more damage than being unavailable.

```
Leader election (ZooKeeper):
  Stale data → two nodes think they're leader → split-brain → data corruption
  Being down → services can't get leader info → temporarily unavailable
  → Down is recoverable. Split-brain is catastrophic.

Payment processing:
  Stale balance → user charges against non-existent funds → financial loss
  Being down → user sees "try again" → calls support
  → Failed payment is recoverable. Wrong payment destroys trust.

Distributed locks (etcd):
  Stale lock info → two processes enter critical section → race condition
  Being down → processes wait → slightly delayed
  → Wait is fine. Race condition corrupts data.
```

**Real-world CP systems:**

| System | Use Case | Why CP |
|---|---|---|
| ZooKeeper | Leader election, distributed locks | Wrong leader info = split-brain |
| etcd | Kubernetes control plane | Wrong config = cluster corruption |
| HBase | Consistent reads at scale | Strong consistency required |
| Google Spanner | Global financial DB | Money = linearizability required |

---

## AP Systems — Availability over Consistency

> [!info] AP systems serve potentially stale data during a partition rather than refusing requests.

**Behavior during partition:**
```
Partition happens → node isolated
→ keeps serving requests
→ returns data it currently has (may be stale)
→ syncs with other nodes when partition heals
→ eventually all nodes converge to same state
```

**Why AP is the right choice:**

When being unavailable causes more damage than slightly stale data.

```
Instagram feed:
  Stale like count → user sees 1000 likes instead of 1002 → nobody notices
  Being down → users leave → engagement drops → revenue lost
  → Slight staleness is fine. Downtime is expensive.

Shopping cart (Amazon):
  Stale cart → item added by spouse not visible yet → minor annoyance
  Being down → user can't shop → lost sale
  → Amazon famously chose AP for carts.

DNS:
  Stale DNS record → user hits old server briefly → minor delay
  DNS down → entire internet breaks
  → Availability is everything for DNS.

Cassandra (social data):
  Stale post count, follower count → off by a few → acceptable
  Down → 2 billion users can't use WhatsApp → unacceptable
```

**Real-world AP systems:**

| System | Use Case | Why AP |
|---|---|---|
| Cassandra | Social data, time-series | Availability > consistency |
| DynamoDB | Shopping carts, sessions | Availability critical |
| CouchDB | Offline-first apps | Must work without connectivity |
| DNS | Name resolution | Global availability non-negotiable |

---

## The Same System, Different Choices

> [!important] The same database can behave as CP or AP depending on configuration

**Cassandra tunable consistency:**
```
Write/Read with ALL   → CP behavior (all replicas must agree)
Write/Read with QUORUM → balanced
Write/Read with ONE   → AP behavior (fastest, most available, potentially stale)
```

**DynamoDB:**
```
Eventually consistent reads → AP (default, lower latency)
Strongly consistent reads   → CP (higher latency, guaranteed fresh)
```

You pick per-operation based on what that specific data requires.

---

## The Decision Framework

```
Step 1: What consistency does this data need?
  Financial, locks, leader election → linearizability → CP
  Social, analytics, preferences    → eventual/causal → AP

Step 2: What happens if the system is unavailable?
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

## System → CP/AP Quick Reference

| System | Choice | Reason |
|---|---|---|
| Payment processing | CP | Wrong balance = financial loss |
| Bank transfer | CP | Money cannot be lost or duplicated |
| Leader election | CP | Stale = split-brain |
| Distributed locks | CP | Stale = race condition |
| Social feed | AP | Slight staleness acceptable |
| Shopping cart | AP | Availability > perfect consistency |
| Chat messages | AP | Availability for billions of users |
| DNS | AP | Global availability non-negotiable |
| Leaderboard | AP | Off by a few = fine |
| Hotel booking | CP | Double booking = serious problem |
