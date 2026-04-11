# Google Spanner — TrueTime

## The ordering problem

For ACID transactions to work across multiple data centers, the database needs to know the **global order** of transactions. Which transfer happened first? Which balance check was authoritative?

On a single node this is trivial — one clock, one counter, one source of truth.

Across data centers in New York and Tokyo, it's hard. You can't use a central version counter — every cross-region transaction would need to reach that counter, adding 150ms+ of latency per transaction. At millions of TPS, that counter becomes an impossible bottleneck.

You could use local clocks — but clocks on different machines are never perfectly in sync. Even with NTP (Network Time Protocol), clocks drift by a few milliseconds. A 2ms drift means a transaction in Tokyo that actually happened *after* one in New York might appear to have happened *before* it. 
Wrong ordering → wrong results → money disappears or appears from nowhere.

---

## Google's solution: atomic clocks and GPS

Google's insight was to put **atomic clocks and GPS receivers** in every Spanner data center.

**Atomic clocks are accurate to within nanoseconds**. GPS signals are globally synchronized. Together they give each data center an extremely precise, globally coordinated sense of time.

But here's the honest part — even atomic clocks have some tiny uncertainty. Spanner doesn't pretend otherwise. Instead of giving you a single timestamp, it gives you a **bounded uncertainty window**:

```
TrueTime.now() → [earliest: 10:00:00.003, latest: 10:00:00.007]
```

This means: "The true current time is somewhere in this 4ms window. I guarantee it."

This is called **TrueTime** — and the uncertainty window in practice is typically 1–7ms.

---

## What Spanner does with the uncertainty

If two transactions happen close together in time — within each other's uncertainty windows — Spanner genuinely cannot tell which came first from physics alone.

```
Transaction A (New York):  true time somewhere in [10:00:00.001, 10:00:00.009]
Transaction B (Tokyo):     true time somewhere in [10:00:00.002, 10:00:00.010]
```

These windows overlap. Could be A first, could be B first.

Spanner's solution: **wait out the uncertainty**. Before committing a transaction, Spanner waits for the entire uncertainty window to pass. By the time it commits, the timestamp is guaranteed to be in the past — and no other transaction anywhere in the world could have a later timestamp that overlaps with it.

```
Transaction A ready to commit
→ TrueTime uncertainty = 4ms
→ Spanner waits 4ms
→ Commits with timestamp 10:00:00.009
→ Guaranteed: no other transaction in the world has an overlapping timestamp
```

This is not like a lock where other transactions fail and retry. All transactions proceed — they each wait their own uncertainty window, then commit with a globally unique, globally ordered timestamp.

---

## Why this works

After the wait:

```
Transaction A commits at: 10:00:00.009  (waited 4ms)
Transaction B commits at: 10:00:00.010
```

No overlap. Clear global order. A happened before B — provably, with no ambiguity.

The waiting cost is small — 1-7ms — and it happens in parallel for all transactions. You pay a tiny latency penalty in exchange for guaranteed global ordering with no central coordinator.

---

## This is called External Consistency

The guarantee Spanner provides is stronger than even serializable isolation. It's called **external consistency** — if transaction A commits before transaction B starts (in real wall-clock time), then A's timestamp is guaranteed to be lower than B's timestamp in the database. The database's ordering matches real-world causality.

No other distributed database achieves this without hardware assistance. TrueTime — atomic clocks + GPS — is what makes it possible.

> [!important] TrueTime in one sentence
> Instead of asking "what version number is this?" Spanner asks "what is the true time right now, with a known error bound?" — then waits out that error before committing, guaranteeing a globally unique and ordered timestamp for every transaction.

> [!tip] For Google interviews specifically
> Mentioning TrueTime, atomic clocks, and the commit-wait mechanism is a strong signal. You don't need to know the implementation — just: atomic clocks give bounded uncertainty, Spanner waits out that uncertainty before committing, result is external consistency across the globe.
