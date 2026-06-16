# primitive-reflex — Master Index

The **third reflex track**. Atomic **trigger → move** installs for the reusable *algorithmic atoms* — the data-structure moves and tricks you acquire once and then **fire on recognition**, so a framing that cost hours the first time costs seconds forever.

> Born 2026-06-03 out of *Score of Parentheses* — 2 hours stuck staring at the abyss for a primitive (stack fold-up) that, once installed, is 8 lines. That gap is exactly what this track closes.

---

## The three reflex tracks (scope boundaries — what earns a card where)

| Track | Installs | Example |
|---|---|---|
| `math-reflex/` | numeric **recall** | "n=20 pairs → 190", mod arithmetic facts |
| `patterns/deck.md` | solving-process **heuristics** (how to think when stuck) | "ambiguous assignment → enumerate the small set, take min" |
| **`primitive-reflex/`** (this) | reusable **algorithmic atoms** (the move the code performs) | "nested structure → it's a tree → stack fold-up" |

- **Not** numeric recall (→ math-reflex). **Not** a meta-cognitive tell (→ deck.md). This track is the *building blocks you assemble*.
- **DP is cross-referenced, not duplicated** — `DP/01-syllabus.md` is the single source of truth for DP sub-patterns.

## Structure (each family owns its own syllabus)

- This file is the **master index** — it lists families and links to each family's own syllabus. It does **not** hold atom detail.
- **Each family** = a folder `topics/NN-family/` with its own **`00-syllabus.md`** — the complete variant catalog + LC problems + atom list + status for that family (the single source of truth for it).
- **Each atom** nests as `topics/NN-family/MM-atom/` with `01-skeleton.md` (trigger, move, derivation) and `03-log.md` (drill reps, dates).
- Family numbering is **local & insert-stable** (two-pointer 1–6, stack 1–7) — adding an atom never renumbers other families.

## Robustness principle (why we audit a family to "complete")

When a family's primitive set is **provably complete**, the missing-tool failure is eliminated by construction — so every remaining failure on that family is **mapping the problem to the right primitive**, which is the trainable recognition muscle. Incomplete catalog = two failure modes you can't tell apart. So each family gets a completeness audit (enumerate every variant by its discriminating feature) before it's stamped ✅.

## How an atom is learned

Socratically first (you derive it), **then** the file is written from what you derived. Re-reading a written-up atom = fluency illusion. Open an atom when a real problem makes you **stall** — not top-down.

## v2 over math-reflex (a primitive is a 3-stage pipeline, a math fact is 1)

A math fact = **recall** a number. A primitive = **① recognize** the (often disguised) trigger → **② recall** the move → **③ produce** the code. Each skeleton trains all three: recognition drills (disguised scenarios), confusion matrix (the discriminator), code-skeleton (blank-page re-type).

## Graduation bar

Named in **< 5 s** cold, mixed-order with other atoms, holding **3 consecutive days**. Drilled by **retrieval**, never by re-reading. `★` = mandated blind-spot (CLAUDE.md rule 6B).

---

# Families (dependency-ordered)

Audit: ✅ audited-complete · ▢ rough draft, audit-on-entry.

| Tier | Family | Atoms | Audit | Syllabus |
|---|---|---|---|---|
| 0 | Substrate *(assumed, not drilled)* — hashmap-count, sort-prep, array-sweep | 3 | — | (inline) |
| 1 | **Two-Pointers** | 6 | ✅ | `topics/01-two-pointers/00-syllabus.md` |
| 2 | Prefix & Suffix | 3 | ▢ | (on entry) |
| 3 | Sliding Window | 3 | ▢ | (on entry) |
| 4 | **Stack** | 7 | ✅ | `topics/04-stack/00-syllabus.md` |
| 5 | Binary Search | 4 | ▢ | (on entry) |
| 6 | Heap | 4 | ▢ | (on entry) |
| 6 | **Interval** | 6 (+2 deferred) | ✅ | `topics/06-interval/00-syllabus.md` |
| 7 | Graph (BFS/DFS/topo/Dijkstra/0-1BFS/cycle/Bellman-Ford) | 7 | ▢ | (on entry) |
| 7 | **Union-Find ★** *(split from Graph — own data-structure family)* | 7 (+5 deferred) | ✅ | `topics/07-union-find/00-syllabus.md` |
| 8 | Recursion / Backtracking | 2 | ▢ | (on entry) |
| 9 | Trees | 5 | ▢ | (on entry) |
| 10 | **Bit Manipulation** *(number-theory → math-reflex)* | 7 modules | ◑ building | `topics/10-bit-manipulation/00-syllabus.md` |
| 11 | DP → `DP/01-syllabus.md` | — | ▢ | (cross-ref) |
| 12 | Advanced (Trie ★ / SegTree-BIT / String-matching) | 3 | ▢ | (on entry) |

**Audited families have a real syllabus; the rest are provisional** (rough atom lists below, replaced by a real family syllabus when we enter that tier).

## Provisional atom lists (un-audited families — will be audited on entry)

- **Tier 2 Prefix & Suffix:** prefix-sum + hashmap · difference array · prefix/suffix decomposition
- **Tier 3 Sliding Window:** variable window · fixed window · exactly-K (`atMost(K) − atMost(K−1)`)
- **Tier 5 Binary Search:** lower/upper bound · BS-on-answer ★ · BS rotated · BS on 2D matrix
- **Tier 6 Heap:** top-K · two-heaps median · k-way merge · heap-scheduling *(incl. interval heap-scheduling — see Interval family DEFERRED)*
- **Tier 6 Interval:** ✅ audited — see `topics/06-interval/00-syllabus.md` (merge · intersection · scheduling · sweep-line · covered · weighted; heap-scheduling + interval-queries deferred)
- **Tier 7 Graph:** BFS/multi-source · DFS/flood-fill · topo-sort · cycle-detection · Dijkstra · 0-1 BFS · Bellman-Ford/Floyd  _(**Union-Find ★ split to its own audited family** → `topics/07-union-find/00-syllabus.md`)_
- **Tier 8 Backtracking:** subsets/combos/perms skeleton · prune-on-constraint
- **Tier 9 Trees:** recursive traversal · Tree-DP ★ · BST-inorder · build-from-traversals · LCA
- **Tier 10 Bit & NT:** XOR cancel · bitmask subset enum · sieve · modpow · GCD/LCM
- **Tier 12 Advanced:** Trie ★ · Segment-tree/BIT · string matching (KMP/Z/Rabin-Karp)

> Note: these provisional lists are *unaudited* — entering a tier may add atoms (Stack went 4 → 7 on audit). Treat them as a sketch, not a complete toolbox, until the family syllabus is written.
