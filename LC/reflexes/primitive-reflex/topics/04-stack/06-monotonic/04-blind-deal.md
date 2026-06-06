# Stack Atom 06 — Monotonic stack ★ · blind-deal bank (DEALER-ONLY · SPOILER)

> **Do not read during learning.** Claude's deal source for the Phase-2 cold exam:
> reserved problems this atom covers but we have NOT solved cold, kept pristine for cold recognition.
> At deal time hand a **bare link only** — never the atom, type, or any note below.
> When a problem here is solved cold, move it to `03-log.md` and delete the row.

| Link | Source | Title | Note |
|---|---|---|---|
| https://leetcode.com/problems/largest-rectangle-in-histogram/ | LC 84 | Largest Rectangle in Histogram | PLANNED DISGUISED REP — knob 3 = *accumulate on pop* (width when a bar pops = current − prev-smaller − 1). Hardest core monotonic problem; the real chunk test |
| https://leetcode.com/problems/next-greater-element-i/ | LC 496 | Next Greater Element I | read **value** not distance; map answers, then look up. The plainest costume |
| https://leetcode.com/problems/next-greater-element-ii/ | LC 503 | Next Greater Element II | circular array → iterate `2n` with `i % n`; same monotonic core |
| https://leetcode.com/problems/trapping-rain-water/ | LC 42 | Trapping Rain Water | monotonic-decreasing stack; water trapped when a taller bar pops a shorter one between two walls (or two-pointer) |
| https://leetcode.com/problems/sum-of-subarray-minimums/ | LC 907 | Sum of Subarray Minimums | count spans on pop = (prev-smaller distance)×(next-smaller distance); contribution technique |
| https://leetcode.com/problems/remove-k-digits/ | LC 402 | Remove K Digits | greedy + monotonic-increasing stack; pop larger preceding digit while budget remains |
| https://leetcode.com/problems/online-stock-span/ | LC 901 | Online Stock Span | previous-greater run length; monotonic stack of (price, span) |

NOTE: announced rep 739 was a **clean self-derived AC** (ownership 1 of 2). The cold ownership certificate is one more clean self-derived monotonic AC — ideally **84** (accumulate-on-pop) to prove the invariant transfers past simple distance lookups, on a blind deal.
