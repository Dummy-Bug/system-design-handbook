# Stack Atom 06 — Monotonic stack ★ · log

| Date | Event | Result |
|---|---|---|
| 2026-06-06 17:55 | Announced — Daily Temperatures (739) | ✅ **CLEAN self-derived first-submission AC** — derived and coded cold, no hints, correct on first paste. Right-to-left, stack of `(temp, index)`, pop `<=` (dominated), peek = next warmer, `ans = peek.index - i`. **Genuine ownership rep 1 of 2 for the monotonic blind-spot (rule 6B).** |
| 2026-06-06 | Perturbation (collaborative, post-AC) | ✓ domination = warmer **and** closer → popped element invisible behind a taller-closer one → O(n). Left-to-right duality surfaced: pop *resolves the popped element's answer* (future resolves past) vs right-to-left pop *discards a dominated element* + peek reads own answer. Family grid `{next,prev}×{greater,smaller}` × {read distance/value/accumulate} |
| 2026-06-06 | Disguised — Largest Rectangle (84) | ◐ **recalled, does NOT count.** User correctly reframed "bar i = the rectangle's limiting/min height" → `area[i] = h[i]×(nextSmaller − prevSmaller − 1)`, max over i (two monotonic passes, or fuse into one accumulate-on-pop pass). But explicitly recalled from prior solves → recognition confirmed, not a cold derivation. Not coded; foundation deemed sufficient |

**Atom #6 status:** announced rep (739) is a **clean self-derived AC = ownership rep 1 of 2** for the monotonic blind-spot. 84 confirmed the reframe but was recalled (no new rep). **Decision (2026-06-06): foundation is installed; the 2nd ownership rep is deferred to zerotrac** — monotonic problems are common there, so rep 2 accrues in the live band grind rather than being manufactured in the atom track. Blind-spot is 1/2; watch zerotrac for the closing clean rep.

**Key harvest:** the monotonic-stack invariant (*what the stack holds + what a pop means*) is the analogue of **DP state** — naming it is 90% of the problem, coding is the easy 10%. Three knobs generate the whole family: greater↔smaller (pop comparison), next↔previous (scan direction), read distance↔value↔accumulate (what you read on a pop).

**Owned (drill slot, later):** name in <5s cold, mixed-order, 3-day hold.
