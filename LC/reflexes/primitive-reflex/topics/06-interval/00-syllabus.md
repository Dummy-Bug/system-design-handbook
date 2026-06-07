# Interval — Family Syllabus

**Discriminator: which endpoint you sort by + what you do when two intervals touch.**
The sort key is the whole tell — start → *combine*, end → *greedily select*, events → *count concurrency*. The one exception is value-maximizing selection, which adds *binary-search the next compatible interval*.

Goal: with every atom installed, an interval problem can only fail on **mapping it to the right atom**, never on a missing tool. (Family robustness principle — see `00-master-syllabus.md`.)

> Born 2026-06-07 out of **Biweekly 184 Q2** (min-energy bulbs): the answer was `ceil(brightness/3) × union-length-of-intervals`, but the interval-union mechanic was a *decayed* reflex (last interval problem solved ~1 year prior) → ~47 min on a problem that's ~12 min with the family installed. Intervals are a pattern unto themselves, so they earn their own family, split out from the old "Heap & Intervals" tier-6 bundle.

---

## The atoms (learning order: foundation → hard)

| # | Atom | Sort by | Move when intervals touch / overlap | Canonical problems |
|---|------|---------|-------------------------------------|--------------------|
| 1 | **Merge / union** | start | `next.start ≤ cur.end` → extend `cur.end = max(cur.end, next.end)`; else flush | Merge Intervals (56), Summary Ranges (228), Partition Labels (763, disguised), Employee Free Time (759, merge→gaps), Meeting Rooms I (252, overlap-check) |
| 1b | **Insert interval** *(sub-variant of merge)* | pre-sorted | walk, merge the spill around the inserted one | Insert Interval (57) |
| 2 | **Intersection (two lists)** | both pre-sorted | overlap = `[max(starts), min(ends)]`; advance the pointer with the smaller end | Interval List Intersections (986), Meeting Scheduler (1229) |
| 3 | **Greedy scheduling** | **end** | take the earliest-finishing, skip everything that conflicts | Non-overlapping Intervals (435), Max Events Attended (1353, simple) |
| 3b | **Min arrows / point-cover** *(sub-variant of scheduling)* | end | shoot at the first end, skip all intervals it pierces | Min Arrows to Burst Balloons (452) |
| 4 | **Sweep-line / concurrency** | **events ±1** | split each interval into `(start,+1),(end,−1)`, sort, running sum, track the max | Meeting Rooms II (253), Car Pooling (1094), Divide Intervals into Min Groups (2406), My Calendar (729/731) |
| 5 | **Covered / containment** | start ↑, **end ↓** | track `maxEnd`; `cur.end ≤ maxEnd` → this interval is *contained* (detect, don't combine) | Remove Covered Intervals (1288) |
| 6 | **Weighted interval scheduling** | start (or end) **+ binary search** | maximize **value**, not count → greedy fails → BS the latest non-conflicting + carry best-so-far (suffix-max / DP) | Two Best Non-Overlapping Events (2054), Max Profit Job Scheduling (1235) — **cross-ref `DP/01-syllabus.md`** |

**The one insight the family installs:** the moment you see intervals, the question is never "what algorithm?" — it's **"which endpoint do I sort by?"** That single question routes you to the atom. Atom 6 is the lone exception that breaks "sort-key = the whole tell" (it needs a binary-search step), which is exactly why it's last and bridges into DP.

---

## Atoms

| # | Atom | Folder | Status |
|---|------|--------|--------|
| 1 | Merge / union (incl. insert) | `01-merge-union/` | ⏳ not started — **priority** (surfaced by Biweekly 184 Q2; decayed reflex, needs blank-page retrieval rep) |
| 2 | Intersection (two lists) | `02-intersection/` | ⏳ not started |
| 3 | Greedy scheduling (incl. arrows) | `03-scheduling/` | ⏳ not started |
| 4 | Sweep-line / concurrency | `04-sweep-line/` | ⏳ not started |
| 5 | Covered / containment | `05-covered/` | ⏳ not started |
| 6 | Weighted interval scheduling | `06-weighted/` | ⏳ not started (DP-bridge — do last) |

Per atom: derive Socratically → solve announced (produce code cold) → solve disguised (install recognition) → perturbation debrief → write files → tick.
Each atom folder: `01-skeleton.md` · `02-notes.md` · `03-log.md` · `04-blind-deal.md` (DEALER-ONLY reserved-problem bank for the Phase-2 cold exam).

**Planned start order:** merge → scheduling → sweep-line → covered → weighted. (Intersection slots in after merge whenever a two-list problem surfaces.)

---

## Completeness

Cross-checked vs `algomaster-data/intervals.tsv` (16 problems) + LearnYard's scattered interval problems (filed under greedy / heap / prefix-sum / binary-search — LearnYard has no interval category). Every in-scope (≤ Q2 / ≤ ~1700) bank problem maps to atoms 1–6. The audit *added* two atoms the first sketch missed — **covered/containment** (#5, the move is *detect* not *combine*) and **weighted scheduling** (#6, greedy fails → BS+DP) — mirroring how Stack grew 4 → 7 on its audit. Two further variants are **deferred** (below), not dropped.

---

## ⏸ DEFERRED (recorded so we don't forget — out of scope for the Q1/Q2 ≤1700 goal)

3. **Heap-scheduling** — Meeting Rooms III (2402), Max Events Attended II (1751) — maintain a **heap of end-times**. This is the heap ∩ interval overlap; it belongs to the **Heap family**, cross-referenced. (Hard, >1700.)
4. **Interval queries / stabbing** — Minimum Interval to Include Each Query (1851), Find Right Interval (436) — offline **sort + binary-search/heap** to answer per-point queries. Advanced/Hard, edges into **segment-tree** (outlier-class). Defer.

> Pick either up *live* if a contest surfaces it (emergent-only policy). Until then they stay parked here — known, named, and not blocking the family from being stamped ✅ on the six core atoms.

---

## Practice plan — minimal non-redundant reps (announced + disguised)

| Atom | Announced | Disguised / applied |
|------|-----------|---------------------|
| 1 merge | Merge Intervals (56) | Partition Labels (763) — looks like a string problem, is a merge |
| 2 intersection | Interval List Intersections (986) | Meeting Scheduler (1229) |
| 3 scheduling | Non-overlapping Intervals (435) | Min Arrows (452) — same sort-by-end greedy |
| 4 sweep-line | Meeting Rooms II (253) | Car Pooling (1094) — events on a number line |
| 5 covered | Remove Covered Intervals (1288) | *(few in bank — acquire-once, harvest the (start↑,end↓) trick)* |
| 6 weighted | Two Best Non-Overlapping Events (2054) | Max Profit Job Scheduling (1235) — classic WIS (cross-ref DP) |
