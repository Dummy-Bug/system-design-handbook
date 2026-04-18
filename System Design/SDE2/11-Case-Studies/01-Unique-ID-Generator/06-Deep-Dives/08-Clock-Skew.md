# Clock Skew — When Time Goes Backwards

## The assumption Snowflake relies on

Snowflake encodes a millisecond timestamp in the most significant bits of every ID. The entire time-sortability guarantee rests on one assumption: **time always moves forward**. Every new ID gets a timestamp greater than or equal to the previous one.

This assumption can break.

---

## How server clocks drift

Server clocks are not perfect. The crystal oscillator inside every machine runs slightly fast or slow due to hardware imperfections — a few parts per million off. Over time, this causes the clock to drift away from real time.

NTP (Network Time Protocol) corrects this periodically by adjusting the server's clock. If the clock was running fast, NTP pulls it backwards. If it was running slow, NTP pushes it forward.

The forward correction is harmless. The **backward correction is dangerous**.

---

## What happens when the clock jumps back

Say a server has been generating IDs normally. NTP detects the clock has drifted 5ms fast and corrects it — pulling the clock back from T=1000ms to T=995ms.

**Sortability breaks:**

```
T=1000ms → ID generated, timestamp=1000, sequence=50  → issued to caller A
           NTP correction: clock jumps back to T=995ms
T=995ms  → ID generated, timestamp=995, sequence=0   → issued to caller B
```

Caller B's ID has timestamp=995, which is smaller than caller A's timestamp=1000. But caller B's ID was generated **after** caller A's. Sorting by ID now gives wrong chronological order. Sortability is broken.

**Duplicates happen on sequence counter reset:**

The sequence counter resets to 0 at the start of each new millisecond. When the clock jumps back, the server thinks it's back at T=995ms and resets the counter to 0 — even though it already issued sequences 0, 1, 2... at T=995ms earlier.

```
Round 1 — before clock correction:
  T=995ms: issued sequence 0, 1, 2, 3... → callers already have these IDs

NTP correction: clock jumps back to T=995ms

Round 2 — after clock correction:
  T=995ms: sequence resets to 0
           issues sequence 0, 1, 2, 3... → different callers get same IDs
```

`timestamp=995, sequence=0` was issued twice to two different callers. Collision. Permanent data corruption.

---

## The fix — wait

When a server detects that the current clock timestamp is less than the last timestamp it used, it simply **refuses to generate IDs until the clock catches up**.

```
Last used timestamp = 1000ms
Current clock      = 995ms   ← moved backwards, STOP

Server waits...
Current clock      = 996ms   ← still behind
Current clock      = 997ms   ← still behind
Current clock      = 998ms   ← still behind
Current clock      = 999ms   ← still behind
Current clock      = 1000ms  ← caught up, safe to generate again ✅
```

No IDs are generated during the wait. Requests queue up for a few milliseconds and are served once the clock catches up.

---

## Is this wait acceptable?

NTP clock corrections are typically **1–10 milliseconds**. The server pauses for at most 10ms. At peak load of 10M IDs/second, that means ~100,000 requests wait a few milliseconds — but none of them fail. They just experience a tiny delay, imperceptible to any end user.

The alternative is generating duplicate IDs — permanent, unrecoverable data corruption. A few milliseconds of queuing is infinitely preferable.

> [!info] The system is not "unavailable" during the wait
> Requests don't fail — they queue up for a millisecond and get served immediately after. True unavailability means requests fail with an error. Queuing for 1–10ms is not unavailability.

---

## Why not use a monotonic clock?

Operating systems provide two types of clocks:

**Wall clock** — actual time of day. Can jump forwards or backwards due to NTP corrections.

**Monotonic clock** — only ever moves forward. Never goes backwards. Used for measuring elapsed time (e.g. "how long did this operation take?").

Using a monotonic clock eliminates the clock skew problem entirely — time can never go backwards, no waiting needed.

But there's a trade-off: monotonic clocks measure nanoseconds since the process started, not real calendar time. The timestamp inside the ID becomes meaningless outside the context of that specific machine's uptime. You can no longer look at an ID and know approximately when it was created.

**Wall clock + wait is the right choice** because:
- Real calendar time is embedded in every ID
- Duplicate prevention via the wait strategy (rare, short, no requests fail)
- Sortability is preserved
- The wait is imperceptible in practice

Twitter's Snowflake, Discord, and most production implementations use wall clock with the wait strategy.

---

## Summary

| Scenario | What happens | Fix |
|---|---|---|
| Clock moves forward | Normal operation | Nothing needed |
| Clock moves backward | Sortability breaks, duplicates possible | Wait until clock catches up |
| NTP correction magnitude | Typically 1–10ms | Wait is imperceptible |
| Using monotonic clock | No skew, but no real calendar time | Not recommended — loses timestamp meaning |
