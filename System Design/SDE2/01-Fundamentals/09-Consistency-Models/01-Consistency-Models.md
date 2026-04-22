# Consistency Models

## The Core Problem

In a distributed system, writes go to a primary node. Replicas sync in the background. A read hitting a replica might return stale data.

```
You post a photo → write goes to primary
You refresh profile → read hits replica (not synced yet)
Photo isn't there → stale read
```

Consistency models define the rules about how stale a read is allowed to be.

---

## The Spectrum

```
Strictest ──────────────────────────────────────────── Loosest

Linearizability → Strong → Causal → Monotonic → Read-Your-Writes → Eventual
```

Each model includes the guarantees of everything to its right.

---

## Eventual Consistency

> [!info] Replicas will converge to the same value — eventually. No guarantee on when. No guarantee on order.

```
You add item to Amazon cart → write to primary
Friend checks your shared cart → might see old version
→ few milliseconds later → replica syncs → friend sees new item
```

**What it guarantees:** If no new writes happen, all replicas will eventually agree.

**What it doesn't guarantee:** Order of operations. Timing. You might see newer data then older data.

**Why use it:** Maximum availability and performance. No waiting for replicas. System works even during network partitions.

**Classic example:** Amazon shopping cart — availability matters more than perfect consistency. A slightly stale cart is better than a cart that errors out.

---

## Read-Your-Writes

> [!info] You always see your own writes — even if other users still see stale data.

```
You post a photo → write to primary
You refresh → read routed to primary (or synced replica)
→ you see your photo ✓

Your friend refreshes → hits replica (not synced yet)
→ friend doesn't see it → fine
```

**The problem it solves:** You post something and immediately can't see it. Feels broken even if technically working.

**Implementation:**
```
Option 1 → after your write, route your reads to primary
Option 2 → track your write timestamp in session
           only read from replicas that have caught up to that timestamp
```

**Classic example:** Instagram — you always see your own posts immediately. Others may see them slightly later.

---

## Monotonic Reads

> [!info] Once you've seen a value, you never see an older one. Time only moves forward for you.

```
Without monotonic reads:
  Read from Replica A → sees tweet from 5 min ago
  Read from Replica B → sees tweet from 10 min ago  ← older, timeline jumped back
  Read from Replica A → sees tweet from 5 min ago   ← back to newer

With monotonic reads:
  Read from Replica A → sees data up to T=5min
  Next read → must go to replica at T≥5min
              never to a replica further behind
```

**The problem it solves:** Timeline jumping backwards. Seeing newer content then older content then newer again.

**Implementation:** Sticky session routing — stick to same replica, or track latest seen timestamp.

**Classic example:** Twitter/X timeline — once you see a tweet from 3pm, you should never see older tweets appearing above it.

---

## Causal Consistency

> [!info] Operations that are causally related must be seen in the correct order by everyone.

```
Message A: "Hey"          → no dependency
Message B: "Hey back"     → causally depends on A

Any user reading B must have already seen A
Nobody sees "Hey back" before "Hey"
```

**What makes two operations causally related:**
```
B causally depends on A if:
  → B was written after reading A
  → B is a reply to A
  → B references or modifies something A created
```

**What it doesn't order:** Independent operations. Messages in different conversations don't need global ordering.

**Why not linearizability instead:** Linearizability requires global real-time ordering across ALL operations — expensive, hurts availability. Causal only orders what matters — related operations.

**Classic example:** WhatsApp — replies must appear after the original message. But messages in different conversations don't need real-time global ordering. System stays available even on poor networks.

---

## Strong Consistency

> [!info] Every read sees the latest write. All nodes agree on the same value at the same time.

```
You transfer $10,000
You immediately read balance → sees updated amount guaranteed
Any node you read from → same value
```

**How it's achieved:** Quorum reads and writes — R + W > N (majority must agree before confirming).

**The cost:** Every write must be confirmed by a majority of nodes before returning success. Higher latency, lower availability during network issues.

**Classic example:** Bank balance — you must never see stale balance after a transfer.

---

## Linearizability

> [!info] Strong consistency + real wall-clock time ordering. Once a write completes, any read that starts after it must see it — respecting actual real time.

```
Real wall-clock time:
  B commits at 10:00:00.100
  A commits at 10:00:00.900  (A happened later in real life)

Strong consistency → might order A → B (internal clocks may differ)
Linearizability   → must order B → A (respects real wall-clock time)
```

**The extra guarantee:** Operations appear to happen at a single instant in real time. The system's ordering matches actual causality in the physical world.

**The cost:** Requires synchronized clocks across all nodes. Google Spanner uses atomic clocks + GPS receivers in every data center.

**Classic example:** Google Spanner — financial systems requiring true global consistency with real-time ordering.

> [!tip] For SDE-2 interviews
> Know that linearizability is the strictest model, it's what Spanner provides, and it requires synchronized clocks. You don't need the formal proof.

---

## The Full Spectrum

```
Linearizability    → strong consistency + real-time ordering (Spanner)
Strong             → every read sees latest write, quorum required (banks)
Causal             → related ops in order, availability preserved (WhatsApp)
Monotonic Reads    → time never goes backwards for a user (Twitter feed)
Read-Your-Writes   → you see your own writes (Instagram)
Eventual           → replicas converge, maximum availability (Amazon cart)
```

> [!important] Each level includes all guarantees of the levels below it
> Causal consistency also gives you monotonic reads and read-your-writes.
> Strong consistency gives you all of the above except real-time ordering.
