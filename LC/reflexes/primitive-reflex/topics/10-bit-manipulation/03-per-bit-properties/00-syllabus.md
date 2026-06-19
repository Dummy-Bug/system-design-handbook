# Module 3 — Per-bit thinking & properties

> The **generative** core of the bit family. One idea: **bits don't interact across columns**, so a problem
> defined bit-by-bit (over all pairs / all subsets / a sum) decomposes into ~31 *independent* per-column counting
> problems. This is where contest speed comes from — it's a *thinking move*, not a one-shot trick.

## Atoms (derivation order)

| # | Atom | Core idea | Classic |
|---|---|---|---|
| 3.1 | **Per-bit contribution** (all-pairs / sum decomposition) | sum over all pairs of a bit-defined quantity → go column by column; count set bits `c`, plug a closed form per operator | LC 477 (Hamming) + GfG AND/OR/XOR pairs |
| 3.2 | **Greedy bit construction** (build the answer MSB→LSB) | maximize/construct a number bit by bit from the top; commit a bit if it stays feasible | TBD |
| 3.3 | **Bit-algebra identities** | `a+b=(a^b)+2(a&b)` · `a+b=(a\|b)+(a&b)` · `a\|b=(a^b)+(a&b)` · `(a&b)^(a\|b)=a^b` · `a-b=a+(~b+1)` | TBD |

## Discriminator (where this sits in the bit confusion matrix)
This is the **"summing each bit's contribution independently"** corner. Felt-signal: *"the answer is a SUM over
many pairs/subsets, and each pair's value is defined per-bit"* → **don't enumerate pairs; iterate the 31 columns**,
in each column you only need the count `c` of set bits, then a closed form. The XOR-mastery module (cancelling
pairs) and this module are the two halves of "thinking in columns."

## 3.1 closed-form table (the transfer payload)
For "Σ over all pairs `i<j`", column `b` has `c` numbers with the bit set, `n` total:

| Over all pairs | Column `b` fires when… | # pairs in column | Per-column term |
|---|---|---|---|
| Hamming distance | the two bits **differ** | `c·(n−c)` | `c·(n−c)` |
| **AND** sum | **both** set | `C(c,2)` | `2^b · c(c−1)/2` |
| **OR** sum | **≥ one** set | `C(n,2) − C(n−c,2)` | `2^b · [totalPairs − bothUnset]` |
| **XOR** sum | **exactly one** set | `c·(n−c)` | `2^b · c(n−c)` |

> The reflex is NOT the table — it's "**decompose by column, then ask: what does this operator need from a pair
> in one column?**" Memorize the *question*, re-derive the row.

## Install loop (per atom)
Socratic derivation → notes written **only after** deriving → blind classic to verify mapping.
Holdout = a blind 1700-1800 sealed-queue problem mapped <30 min self-derived.

## Status
✅ **MODULE 3 COMPLETE** (2026-06-19). Notes in `02-notes.md`. *(carries: 3.2 Smallest-XOR 2nd rep + the 3 deferred
LCs below — none block module completion.)*
- 3.1 Per-bit contribution —
  - **Hamming (LC 477) ✅ TRULY OWNED** — count differing positions, weight 1.
  - **AND-pairs ✅ TRULY OWNED (2026-06-19)** — re-derived cold; the value-decomposition / order-swap intuition is
    installed via the **carry-conservation** argument (carry = relabel, value conserved ⇒ `total = Σ_b 2^b·count`).
    Count for AND = both-set = `C(c,2)`.
  - **XOR-pairs ✅ TRULY OWNED (2026-06-19)** — self-derived count = `c·(n−c)` (exactly one set), weighted `2^b`
    (= Hamming's count + value weight).
  - **OR-pairs ✅ TRULY OWNED (2026-06-19)** — self-derived count, direct split: `C(c,2) + c·(n−c)` (≥one set)
    = complement `C(n,2) − C(n−c,2)`.
  - **LC 1835 (XOR of all ANDs) ⏸ DEFERRED (optional)** — variants are infinite; reflex owned, escalation skippable.
  - **✅ Blocking gap CLOSED (2026-06-19):** the per-bit *contribution* / order-swap intuition is now installed
    (see notes §1 carry-conservation). All four pair-sums (Hamming/AND/OR/XOR) self-owned.
- 3.2 Greedy bit construction —
  - **Reflex installed (2026-06-19):** build MSB→LSB, set bit if feasible, narrow candidates on commit; engine =
    `2^k > Σ lower bits`. **Max AND pair ✅ self-derived + coded.**
  - ▢ Smallest XOR with B set bits — re-derive cold (2nd rep).
- 3.3 Bit-algebra identities — ✅ OWNED (2026-06-19) — derived `a|b=(a^b)+(a&b)`, `a+b=(a|b)+(a&b)`,
  `a+b=(a^b)+2(a&b)`, `a−b=a+(~b+1)` from a 2-bit truth table; trigger `a+b==a^b ⟺ a&b==0` (disjoint bits).

## ⏸ Deferred to revision time (don't lose these)
1. **LC 421 — Max XOR pair** (greedy-MSB + XOR-complement-in-set / trie). Brainstormed start: bit feasible when two
   numbers **differ** there. Pick up the prefix-set construction at revision.
2. **LC 1835 — XOR of all pair-ANDs** (the "hard version" escalation of atom 3.1; distributive + per-bit twist).
3. **LC 1442 — Count triplets equal XOR, O(n)** (owed from Module 2 / 2.6b: `freq*k − sum` aggregate, off-by-one
   indexing un-finalized). Re-derive & code the O(n) cleanly.

Notes in `02-notes.md`.
