
> [!info] The core idea
> Every machine has its own hardware clock. These clocks are never perfectly in sync because of tiny physical imperfections in the hardware. Over time they drift apart — meaning you cannot trust wall clock timestamps across machines to tell you what happened first.

---

## Why clocks drift — the physics

Every computer has a tiny component called a **crystal oscillator** — a quartz crystal with electricity applied to it. Quartz has a special property: when you apply electricity to it, it physically vibrates. The computer counts those vibrations to measure time. Think of it like a metronome inside your chip.

The frequency tells you how many times the crystal vibrates per second:

```
Frequency = 32,768 Hz → vibrates 32,768 times per second
```

And the time period — how long one vibration takes — is:

```
T = 1 / f
T = 1 / 32,768 = 0.0000305 seconds per vibration
```

The computer counts vibrations and converts that to time. Every 32,768 vibrations = 1 second.

---

## Where drift comes from

No two crystals are perfectly identical. One server's crystal might vibrate at 32,768 Hz, another at 32,770 Hz — a tiny difference in manufacturing.

```
Server A crystal: 32,768 Hz → T = 0.0000305s per vibration → counts time correctly
Server B crystal: 32,770 Hz → T = 0.0000304s per vibration → each vibration is slightly shorter
```

Server B thinks 32,768 vibrations passed — but slightly less than 1 real second actually passed. Over millions of vibrations, this tiny error accumulates. After hours, Server B is slightly ahead of Server A. After days, it's noticeably off.

This is called **clock drift** — clocks on different machines slowly diverge over time purely because of hardware imperfections.

---

## Why this breaks distributed systems

Say you have two servers — S1 and S2. A user sends a message on S1 at what S1 thinks is **10:00:00**. Another user sends a message on S2 at what S2 thinks is **09:59:58**.

If you order events by timestamp, S2's message looks like it came first — even if it actually happened after S1's message.

```
S1 records event at: 10:00:00
S2 records event at: 09:59:58  ← looks earlier, but actually happened later
```

You cannot trust wall clock timestamps across machines to tell you what happened first.

