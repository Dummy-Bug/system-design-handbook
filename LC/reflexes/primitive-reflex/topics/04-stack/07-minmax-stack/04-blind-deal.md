# Stack Atom 07 — Min/max auxiliary stack · blind-deal bank (DEALER-ONLY · SPOILER)

> **Do not read during learning.** Claude's deal source for the Phase-2 cold exam:
> reserved problems this atom covers but we have NOT solved cold, kept pristine for cold recognition.
> At deal time hand a **bare link only** — never the atom, type, or any note below.
> When a problem here is solved cold, move it to `03-log.md` and delete the row.

| Link | Source | Title | Note |
|---|---|---|---|
| https://leetcode.com/problems/maximum-frequency-stack/ | LC 895 | Maximum Frequency Stack | DEFERRED disguised rep — bucket-by-frequency (group: freq→stack) O(1), or PQ `(freq,seq)` O(log n). Design-flavored; revisit for interview prep |
| https://leetcode.com/problems/max-stack/ | LC 716 | Max Stack | getMax + popMax; popMax removes a buried element → pure min-stack lockstep breaks, needs an ordered structure (TreeMap / two-heaps-with-lazy-delete). The "non-top pop" boundary case in costume |

NOTE: announced rep Min Stack (155) was **recalled** (not cold) — fine, min/max stack is not a blind-spot. The atom's chunk is installed. These reserved problems are the *boundary* cases (non-top pop / mutation) where the simple lockstep cache fails and you must bucket-by-key or use an ordered structure.
