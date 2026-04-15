
> [!info] Server-assigned timestamps are better than client timestamps — but still not reliable for ordering across multiple servers
> The server lives in a datacenter with NTP sync. Its clock is far more accurate than a user's phone. But "more accurate" is not the same as "globally consistent across all servers."

---

## Why server timestamps seem like the fix

Instead of trusting Alice's phone clock, let the server stamp each message when it arrives:

```
Alice sends "hey" → arrives at Server A → Server A assigns timestamp=4:20:00.100
Bob sends "hi"   → arrives at Server B → Server B assigns timestamp=4:20:00.099
```

Server clocks are NTP-synced. They're accurate to within milliseconds. The time machine problem (10-minute clock skew between phones) disappears entirely.

But look at those two timestamps again.

---

## The multi-server problem

We have multiple WebSocket servers. Alice is connected to Server A. Bob is connected to Server B. Their messages arrive at different servers.

Even with NTP, two different servers can disagree on the current time by a few milliseconds. NTP synchronization is not perfect — it corrects for drift but cannot eliminate it entirely. Two servers in the same datacenter might be off from each other by 1-5ms at any given moment.

```
Alice sends "hey" → Server A → assigns 4:20:00.100
Bob sends "hi"   → Server B → assigns 4:20:00.099  (Server B is 1ms behind Server A)

Sort by server timestamp:
  Bob:   "hi"   — 4:20:00.099  ← appears first
  Alice: "hey"  — 4:20:00.100  ← appears second
```

Bob's reply appears before Alice's original message. Same time machine problem, just scaled down from 10 minutes to 1 millisecond. Visually it looks like ordering is broken.

---

## The core issue with any timestamp-based approach

Timestamps measure wall-clock time. Wall-clock time is physical — it depends on the accuracy of the clock measuring it. Any system with multiple clocks (multiple servers, multiple clients) will have clock disagreement. The disagreement might be tiny, but it exists, and it can flip the ordering of closely-timed events.

For ordering purposes, what you actually need is not "what time did this message arrive" but rather "what is the globally agreed-upon sequence position of this message." Those are fundamentally different questions.

Time answers the first. A sequence number answers the second.

> [!important] The insight
> Timestamps measure physical time. Ordering requires logical sequence. These are different things. Use a sequence number, not a timestamp, for ordering.
