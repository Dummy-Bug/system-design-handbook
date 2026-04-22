
> [!info] The core idea
> Clocks drift apart because of crystal oscillator imperfections. NTP fixes this by periodically asking a highly accurate external server what time it is and correcting your local clock. But network delay means NTP can only get you within 1-10ms of the true time — never perfectly exact. And that few milliseconds is enough to get the ordering of events wrong in a fast distributed system.

---

## Why not just use atomic clocks in every server?

The obvious fix to clock drift is to use a clock that never drifts. Atomic clocks do exactly that — instead of counting crystal vibrations, they count energy transitions of cesium atoms. Atomic transitions are a fundamental property of nature — not affected by manufacturing differences, temperature, or voltage. Every cesium atom in the universe behaves exactly the same way. Result: atomic clocks drift less than **1 second in 100 million years**.

So why doesn't every server just have one?

Cost. A single atomic clock costs **tens of thousands of dollars**. A data center running thousands of servers cannot put an atomic clock in each one. It's simply not economically feasible.

So the practical compromise the industry landed on is this — a small number of atomic clocks exist in the world as global reference points. Every server periodically asks one of these reference points "what time is it right now?" and corrects its local crystal clock based on the answer. That protocol is called **NTP — Network Time Protocol**.

---

## How NTP works

The atomic-clock-backed reference servers sit at the top of a hierarchy. Your server doesn't talk to them directly — it talks to intermediate NTP servers that have already synced with the reference. The idea is simple: your drifting crystal clock periodically gets corrected by asking a more accurate clock over the network.

But here's the problem. When your server sends a request to the NTP server, that request travels over a network. Networks have delay. By the time the response arrives back at your server, the timestamp inside that response is already slightly old.

NTP solves this by estimating how long the network trip took, using four timestamps:

```
T1 → your server sends the request       (your clock)
T2 → NTP server receives the request     (NTP server clock)
T3 → NTP server sends the response       (NTP server clock)
T4 → your server receives the response   (your clock)
```

From these four numbers, NTP calculates the network delay:

```
Total round trip time  = T4 - T1
NTP server processing  = T3 - T2
Network travel time    = (T4 - T1) - (T3 - T2)
One way delay          = Network travel time / 2
```

Your server takes the timestamp T3 from the response, adds the one way delay, and estimates what the true time is right now.

> [!danger] This assumes the network is symmetric — and it never is
> The entire calculation assumes the trip from your server → NTP took exactly the same time as NTP → your server. But real networks are asymmetric. One direction might be congested, routed differently, or just slower. This asymmetry cannot be measured or corrected. It is the fundamental reason NTP can only get you within **1-10 milliseconds** of the true time — never perfectly exact.

---

## How NTP corrects your clock — slewing

Once NTP knows your clock is off, it cannot just jump the time forward or backward instantly. The reason is that everything on your server depends on time — cron jobs, token expiry, log timestamps, scheduled tasks. If the clock suddenly jumps back 5 seconds, a cron job that already ran might run again. If the clock jumps forward, scheduled jobs that were supposed to run during those skipped seconds get missed entirely.

So NTP uses a technique called **slewing** — instead of jumping, it gradually speeds up or slows down your clock until it catches up to the correct time:

```
Normal:  1 real second = 1 clock second
Slewing: 1 real second = 0.9998 clock seconds  ← clock slowed slightly to fall back
         1 real second = 1.0002 clock seconds  ← clock sped up slightly to catch up
```

The adjustment is tiny — measured in PPM — so you'd never notice it in practice. A minute still feels like a minute. But over thousands of seconds the clock quietly closes the gap and catches up to the correct time.

If the drift is too large — say hundreds of seconds off — slewing would take too long to correct. In that case NTP does a hard reset and jumps the clock directly. This is rare and is treated as an exceptional situation that may need manual intervention.

---

## The bottom line

Even with NTP running on every machine in your data center, two servers can still be a few milliseconds apart at any given moment. And in a fast distributed system processing thousands of events per second, a few milliseconds is enough to get the ordering of events completely wrong.

Two servers both running NTP, both within 5ms of true time, could still disagree by 10ms. If two events happen 2ms apart on different servers, NTP cannot tell you which one came first. You need a completely different approach — one that does not rely on wall clock time at all.
