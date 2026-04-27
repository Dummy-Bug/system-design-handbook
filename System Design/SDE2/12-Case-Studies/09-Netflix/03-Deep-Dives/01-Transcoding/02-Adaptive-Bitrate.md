## The Problem With Pure Speed Measurement

The naive ABR approach is simple: after every chunk download, measure the speed, pick the highest quality that fits. If speed is 40 Mbps, pick 4K. If speed drops to 2 Mbps, pick 480p.

The problem is that mobile networks fluctuate constantly. Speed jumps up and down every few seconds. If the client strictly follows speed measurement, this happens:

```
chunk 44 → measured speed: 38 Mbps → picks 4K
chunk 45 → measured speed: 2 Mbps  → picks 480p
chunk 46 → measured speed: 35 Mbps → picks 4K
chunk 47 → measured speed: 3 Mbps  → picks 480p
```

Every 4 seconds the quality jumps — crisp, blurry, crisp, blurry. The video never freezes but it looks terrible. This constant up-down quality switching is called **oscillation**.

---

## The Buffer — The Missing Signal

The client does not fetch chunks one at a time and immediately play them. It fetches ahead — downloading several chunks in advance and storing them in memory, waiting to be played. This waiting area is called the **buffer**.

Think of it like a water tank. The download fills it, the player drains it. As long as the tank has water, playback is smooth.

The buffer level tells you something that raw speed cannot: **how much time do you have before the video freezes?**

Two scenarios with identical network speed:

```
Scenario A → buffer has 25 seconds loaded → can afford slow download → try 4K
Scenario B → buffer has 3 seconds loaded  → cannot afford slow download → drop to 480p
```

Same speed. Completely different right answer. Pure speed measurement misses this entirely.

---

## Why Buffer Beats Speed

Say the client is streaming at 4K and the network drops for 1 second. Pure speed measurement panics — immediately drops to 480p. But the buffer had 20 seconds of 4K already loaded. The network recovered before those buffered chunks were even played. The quality drop was completely unnecessary.

Buffer-based ABR doesn't panic. It looks at the buffer and says — I have 20 seconds loaded, I can afford to wait and see if the network recovers before making any quality decision.

This also kills oscillation. A brief speed dip does not trigger a quality change if the buffer is healthy. The algorithm only reacts when the buffer itself is actually in trouble.

---

## Buffer-Based ABR — BOLA

The algorithm defines buffer thresholds. Say buffer capacity is 30 seconds:

```
Buffer > 20 seconds              → safe zone    → push quality up
Buffer 10-20 seconds             → neutral zone → hold current quality
Buffer 10-20 seconds + speed ok  → nudge quality up slowly
Buffer < 10 seconds              → danger zone  → drop quality immediately
```

Buffer level is the primary signal. Speed is a secondary signal used only in the neutral zone to slowly nudge quality up when conditions are consistently good.

This algorithm is called **BOLA** (Buffer Occupancy based Lyapunov Algorithm) — it is what Netflix actually uses.

---

## Drop Fast, Recover Slow

The algorithm is deliberately asymmetric. When the buffer enters the danger zone, it drops quality immediately — no hesitation. When the buffer recovers, it raises quality slowly — one step at a time, only after several chunks confirm the improvement is stable.

The reason: raising quality too fast brings oscillation back. If the algorithm jumps to 4K the moment speed looks good, and speed dips again two chunks later, you get the same up-down problem.

Drop fast. Recover slow.

---

## The Hard Rule — Never Freeze

Between two bad outcomes, freezing is always worse than a quality drop. A quality drop from 1080p to 720p is barely noticeable. A freeze — the spinner, the broken playback — is jarring.

So the one rule that overrides everything else: **never let the buffer run empty**. Even if that means dropping all the way to 480p. Quality is a nice-to-have. No freeze is a hard requirement.

---

## Startup Phase — The Exception

BOLA assumes the buffer already has some content. But when you first click play, the buffer is empty. The thresholds don't apply — the danger zone logic would trap the client at 480p forever, even on a 100 Mbps connection, because the buffer is always below 10 seconds during startup.

So the startup phase uses a completely separate logic: **ignore buffer thresholds, use speed only, ramp up quality aggressively.**

```
Startup phase → speed-based only → ramp up as fast as speed allows
Steady state  → BOLA takes over  → buffer thresholds drive all decisions
```

Once the buffer crosses the safe threshold — say 10 seconds loaded — the algorithm switches from startup mode to steady state. From that point, BOLA runs the show.

> [!info] Why startup starts at 480p
> The client has no speed measurement before the first chunk downloads. It always fetches chunk 1 at 480p — safe, tiny, fast. That download gives it the first speed measurement. From chunk 2 onwards, startup mode ramps up quality based on that measurement.
