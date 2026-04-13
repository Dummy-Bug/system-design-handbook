
> [!info] The core idea
> Instead of pretending to know the exact time, TrueTime admits the uncertainty and gives you a guaranteed interval — the true time is somewhere inside this window. When two transaction windows don't overlap, ordering is guaranteed. When they do overlap, Spanner waits until they separate before committing.

---

## The problem TrueTime solves

Even with GPS receivers and atomic clocks in every data center, some microseconds pass between receiving a time signal and your server actually using it. Hardware takes time to process. Signals take time to travel even within a building. The true time cannot be known with zero uncertainty.

NTP deals with this by pretending the uncertainty doesn't exist — it gives you one number and hopes it's close enough. TrueTime takes a different approach: **admit the uncertainty and bound it**.

---

## The uncertainty window

Instead of returning a single timestamp, TrueTime.now() returns an interval:

```
TrueTime.now() → [earliest, latest]
```

This interval means: "the true time is guaranteed to be somewhere inside this window — no earlier than earliest, no later than latest."

The window is calculated as:

```
earliest = last known accurate time - maximum possible drift since last sync
latest   = last known accurate time + maximum possible drift since last sync
```

---

## A concrete example

Say the GPS receiver last synced at exactly **10:00:00.000** and Google knows their hardware can drift at most **2ms** between syncs.

Think of it like checking your watch at 10:00:00 and knowing your watch can be off by at most 2 seconds. Someone asks you the time without you checking again — you can't say exactly, but you can guarantee:

```
It's at least 09:59:58  (what if my watch was 2 seconds fast?)
It's at most 10:00:02  (what if my watch was 2 seconds slow?)
```

TrueTime does the same:

```
Last synced time = 10:00:00.000
Maximum drift    = 2ms

earliest = 10:00:00.000 - 2ms = 09:59:59.998
latest   = 10:00:00.000 + 2ms = 10:00:00.002

TrueTime.now() → [09:59:59.998, 10:00:00.002]
```

The true time is somewhere inside that 4ms window. TrueTime guarantees it cannot be outside.

> [!important] Typical TrueTime uncertainty
> On most days the window is under 1ms. On bad days (GPS outage, falling back to atomic clock) it can be up to 7ms. Still far tighter than NTP's 1-10ms — and critically, the bound is guaranteed, not just estimated.

---

## How Spanner uses this — ordering transactions

TrueTime's uncertainty window only matters when two transactions are writing to the **same data** at the same time. Spanner needs to decide which transaction happened first before committing either one.

Say two clients are updating the same bank account simultaneously — one hits Server 1, one hits Server 2:

```
Client 1 → Server 1 → wants to update account X
Client 2 → Server 2 → wants to update account X
```

Spanner calls TrueTime.now() on both servers and compares the windows.

**Case 1 — Windows do not overlap:**

```
Server 1: [10:00:00.998, 10:00:01.002]
Server 2: [10:00:01.003, 10:00:01.007]
```

Server 2's earliest possible time is after Server 1's latest possible time. No overlap. Spanner knows with **100% confidence** that Server 1's transaction happened before Server 2's. Safe to commit in that order immediately.

**Case 2 — Windows overlap:**

```
Server 1: [10:00:00.998, 10:00:01.002]
Server 2: [10:00:00.999, 10:00:01.003]
```

The windows overlap — both transactions might have happened at the same moment. Spanner cannot be sure which came first.

---

## Commit wait — what Spanner does when windows overlap

When windows overlap, Spanner does not guess. It **waits** — holds the commit until enough time has passed that the windows no longer overlap.

```
Windows overlap → Spanner waits → windows separate → now safe to commit in guaranteed order
```

This is called **commit wait**. It adds a small latency — a few milliseconds — but the payoff is that Spanner can guarantee globally consistent ordering of transactions across data centers, without any coordination between servers.

> [!tip] Interview framing
> "TrueTime doesn't claim to know the exact time — it returns a bounded uncertainty interval. If two transaction windows don't overlap, ordering is guaranteed and Spanner commits immediately. If they overlap, Spanner waits until they separate. This gives Spanner external consistency — something no distributed database had achieved at global scale before."
