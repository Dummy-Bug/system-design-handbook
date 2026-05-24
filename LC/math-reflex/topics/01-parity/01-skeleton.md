# Parity [1100]

Even / odd reasoning. The simplest math reflex — pure structural argument, no arithmetic depth. Used as a *necessary condition check* across thousands of LC problems ("can you reach target?", "is this configuration possible?", "count valid arrangements"). Caps in usefulness around Band 1800 — beyond that, parity dissolves into the wider mod-k machinery (see Modular Arithmetic).

## Empirical frequency

| Band | PARITY-tagged problems |
|------|------------------------|
| 1100-1399 | (tagged differently in legacy band — present but folded into broader counts) |
| 1400-1499 | 9 |
| 1500-1599 | 8 |
| 1600-1699 | 7 |
| 1700-1799 | 5 |
| 1800-1899 | 6 |
| 1900-1999 | 0 |
| 2000+ | 0 (absorbed into MOD_ARITH / XOR at higher bands) |

**Total verified: 35 problems in the 1400-1899 range.** Plus an unspecified larger pool at 1100-1399 where parity arguments are common but not tagged as a distinct topic.

## Subtopic structure

Each subtopic is rated `[required-from XXXX]` — meaning: at any target rating ≥ XXXX, this subtopic is mandatory. If your target is below the bracket, skip.

Each subtopic decomposes into one or more atomic cards (numbered `x.N`). Card *content* is intentionally NOT in this file — those get unpacked via Socratic drill when we install the topic. This file is the skeleton.

---

## a. Parity arithmetic rules [1100]

**Cards (3):**
- a.1 — Sum / difference parity of two integers
- a.2 — Product parity of two integers
- a.3 — Parity of `a^k`

---

## b. Bit-0 as parity reflex [1100]

**Cards (1):**
- b.1 — Equivalence of `n % 2` and `n & 1`

---

## c. Parity-preserving operation invariant [1300]

**Cards (2):**
- c.1 — Recognising operations that preserve parity
- c.2 — Recognising operations that flip parity

---

## d. "Can target be reached?" parity check [1400]

**Cards (2):**
- d.1 — Parity as a necessary condition for reachability
- d.2 — When parity is necessary-only vs necessary-and-sufficient

**LC anchor problems:**
- *Sum of Two Integers* (LC 371)
- "Can the operation reach target" family

---

## e. Parity of a sum or count [1400]

**Cards (1):**
- e.1 — Sum parity equals count of odd elements mod 2

---

## f. XOR as per-bit parity [1500]

**Depends on:** Bit Operations → bit indexing `[1400]`

**Cards (1):**
- f.1 — XOR of the i-th bit across n numbers = parity of how many have that bit set

---

## g. Adjacent-parity grouping / swap counting [1500]

**Cards (1):**
- g.1 — Counting / rearranging by adjacent-parity classes

---

## h. Parity argument in 2-coloring / bipartite check [1700]

**Depends on:** Graph traversal (BFS / DFS) — algorithmic prerequisite, lives outside math syllabus

**Cards (1):**
- h.1 — Bipartite ⇔ no odd cycle ⇔ consistent 2-coloring

---

## i. Parity in subset counting [1700]

**Depends on:** Pair / Triple Count → subset enumeration `[1500]`

**Cards (1):**
- i.1 — Counting subsets with even-sum vs odd-sum

---

## j. Parity as a DP state dimension [1800]

**Cards (1):**
- j.1 — When parity becomes a tracked dimension in DP state

---

## Card count

13 atomic cards total across 10 subtopics.

| Target rating | Required cards (cumulative) |
|---------------|------------------------------|
| 1100-1299     | a (3) + b (1) = **4 cards** |
| 1300-1399     | + c (2) = **6 cards** |
| 1400-1499     | + d (2) + e (1) = **9 cards** |
| 1500-1599     | + f (1) + g (1) = **11 cards** |
| 1700-1799     | + h (1) + i (1) = **13 cards** |
| 1800+         | + j (1) = **13 cards (full)** |

## How this file gets used

1. **Install order** — start at subtopic `a`, work down. The Socratic drill turns each card into a question, you derive or recall, we lock the answer.
2. **Each card joins the drill pool** once it passes the graduation bar (see `00-protocol.md`).
3. **At target-rating preparation time**, this file's "Required cards" table tells you exactly which cards must be installed before that band feels effortless.
4. **This file does not contain answers.** Answers come via Socratic. Once a card is graduated, the user owns the answer cold — no need to write it here.
