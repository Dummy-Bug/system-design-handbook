# Stack Atom 09 — Monotonic candidate stack (farthest/widest) · log

| Date | Event | Result |
|---|---|---|
| 2026-06-15 | **Gap identified:** Atom 06 covers only NEAREST greater/smaller (`{next,prev}×{greater,smaller}`); the "farthest/widest pair" reflex was never installed. Surfaced on Maximum Width Ramp (LC 962) — user solved it via O(n log n) index-sort, having *seen* the mono path but bailed to the map ("felt easier"). The 06 reflex correctly didn't fire — wrong pattern, not a weak reflex. | gap → new atom |
| 2026-06-15 | Derived the mechanic Socratically (domination ⇒ strictly-decreasing candidate stack ⇒ reverse sweep ⇒ pop = farthest partner) | ✓ led, not self-derived (**acquisition**) |

**Status:** acquired (install), **NOT a clean self-derived rep.** Mono-Stack blind-spot stays **1/2** → 2nd rep owed on a *fresh* problem (carried #9 max-chunks) where the reflex must fire cold.
**Owned (drill slot, later):** name in <5s cold; nail the **nearest (06) vs farthest (08)** discriminator without prompting.
