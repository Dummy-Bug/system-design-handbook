# Integer Division (ceil / floor / round / distribute) [1100] — ⏸ PARKED

> **Status: scaffolded, not yet derived.** Created 2026-06-07 as the promotion target for
> the ceil/floor reflex. The *proven* members currently live in
> `00-ranges-and-indices` subtopic **f** (`ceil(T/k)=(T+k−1)/k`, floor companion) — do NOT
> duplicate them here. This folder **activates** (cards get derived Socratically + moved
> in) only when a contest surfaces one of the unproven members below. Emergent-only: the
> folder is parked scaffolding so we don't forget the upgrade path, not pre-built content.

## Why this folder exists (the upgrade trigger)

`00-ranges-and-indices/f` holds ceil/floor as a 2-card sub-operation. That's correct *until*
the division-rounding family grows past ~4 cohesive high-frequency members — at which point
it's its own operation-class (like parity, gcd-lcm, modular) and earns this folder. We
recorded the trigger rather than guessing the size.

## Candidate cards (titles only — derive when a contest proves one)

- **a. ceil / floor core** *(currently in `00-ranges-and-indices/f` — migrate here on activation)*
  - ceil: `ceil(T/k) = (T + k − 1)/k` (integer-only; no `Math.ceil` float trap)
  - floor: `T/k`; remainder `T%k`; identity `T = (T/k)·k + T%k`
- **b. Negative-division trap** *(unproven — strong promote candidate)*
  - Java `/` truncates toward zero (`−7/2 = −3`), so `(T+k−1)/k` ceil **breaks for negatives**
  - use `Math.floorDiv(a,b)` / `Math.floorMod(a,b)` for true floor / non-negative mod
- **c. Round to a multiple of k** *(unproven)*
  - round up: `((a + k − 1)/k)·k` · round down: `(a/k)·k`
- **d. Distribute T into k bins evenly** *(unproven)*
  - exactly `T%k` bins get `ceil(T/k)`, the rest get `floor(T/k)`; max bin = `ceil`, min bin = `floor`

## Activation checklist

1. A contest/zerotrac problem hinges on b, c, or d above.
2. Derive that card Socratically (blank page, not re-read).
3. Migrate `00-ranges-and-indices/f`'s two cards into card **a** here, leave a cross-ref stub behind.
4. Register this topic in `math-reflex-syllabus.md` and flip status PARKED → active.
