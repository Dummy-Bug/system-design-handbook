# Bit Manipulation — Family Syllabus

> Standalone bit family (number-theory lives in `math-reflex/`, kept separate per user). Built 2026-06-16 from
> **Scaler Academy ∪ LearnYard (47 problems, 4 subgroups) ∪ AlgoMaster (13 classics)**.
> This family's job is **trigger reflexes** — *when/where* to reach for a bit move — since the mechanics are simple
> but the mapping is the gap. Each module owns its own `00-syllabus.md`.

Discriminator (the confusion matrix that makes bit-mapping fast): **am I —**
- *cancelling pairs* (XOR), or
- *summing each bit's contribution independently* (per-bit), or
- *representing a set of ≤~20 things* (bitmask), or
- *exploiting OR/AND monotonicity over a subarray* (bit-count-in-window)?

That 4-way split is the core mapping skill for bits.

## ⚠ Scope boundary — what is NOT in this family (don't re-drift)

**Carry-arithmetic / positional digit-simulation is a SEPARATE primitive, not bit manipulation.** The family
*Add Binary · Plus One · Add Strings · Add to Array-Form · Multiply Strings · Add Two Numbers (linked list)* all
share one skeleton — *simulate grade-school positional arithmetic with carry* (`sum = digits + carry`, emit
`sum % base`, carry `sum / base`, base-agnostic) — and it uses **`%base` / `/base` arithmetic**, not bit operators.
It belongs to a math/array **simulation** primitive, tracked elsewhere. We touched **Add Binary** only as a
*foundation warm-up* (it exercises base-2 representation + carry, Sec. 6/Sec. 9 of `01-Number-System`); do **not** expand
into its cousins here.

**The genuinely-bit "add" is the exception:** *Sum of Two Integers* (add without `+`) → `sum = a^b`,
`carry = (a&b) << 1` — that one IS bit manipulation and lives in **Module 1** (addition via XOR+carry), done with operators.

> Litmus test: solved with `%base`//`base` digit arithmetic → digit-simulation (not here). Solved with
> `& | ^ ~ << >> >>>` on raw bits → bit manipulation (here).
>
> Note: the `01-Number-System` foundation problems (P1 Number-of-1-Bits, P2 Add-Binary, P3 Alternating-Bits) were
> all solved via `%2`//`2` **arithmetic** as *stopgaps* — real bit manipulation begins at `02-Operators/`, after
> which we redo them the bit way (`& 1`, `>>>`) — incl. the P1 negative-`n` cliffhanger.

## Install + test loop (per atom)
1. **Classic** — the simpler tool solves it.
2. **Break the simpler tool** — a constraint forces the bit move → derive it (Socratic).
3. **Extract the trigger** — the felt-signal + where it sits in the confusion matrix. *Reflex written only after derivation.*
4. **Holdout test** — a blind 1700-1800 sealed-queue problem: map in <30 min self-derived = installed; else not.

## Modules (basic → advanced)

| # | Module | Status | Syllabus |
|---|---|---|---|
| 0 | **Foundations** (the alphabet — ops, idioms, 2's-comp) | ✅ DONE (2026-06-17) | `00-foundations/00-syllabus.md` |
| 1 | **Counting & bit arithmetic** (popcount, Counting-Bits DP, count-bits-in-1..N, reverse, add, add-via-XOR, divide) | ✅ DONE (2026-06-18) | `01-counting-arithmetic/00-syllabus.md` |
| 2 | **XOR mastery** (cancellation, parity-invariant, two-uniques/thrice, reconstruction/decode, prefix-XOR, Gray) | ✅ DONE (2026-06-18) *(1442 O(n) opt owed)* | `02-xor-mastery/00-syllabus.md` |
| 3 | **Per-bit thinking & properties** (per-bit contribution, XOR=sum⟺no-carry, greedy bit construction, per-bit decision) | ✅ DONE (2026-06-19) *(3 carries: Smallest-XOR 2nd rep, LC 421/1835/1442)* | `03-per-bit-properties/00-syllabus.md` |
| 4 | **OR/AND over subarrays** (monotonicity → bit-count-in-window; no-shared-bits window; OR≥K / AND=K; LogTrick; AND-of-range) | ◑ DERIVATIONS DONE (2026-06-19) — 4.1 ✅ owned (LC 201); 4.2/4.3/4.4 derived, holdout-pending (problem block deferred) | `04-or-and-subarrays/00-syllabus.md` |
| 5 | **Bitmask as a set** (subset/submask enumeration; int as set of ≤20; bitmask + prefix-parity) | ⏸ DEFERRED | `05-bitmask-as-set/00-syllabus.md` |
| 6 | **Advanced** (XOR basis; bit-trie → Trie phase; Bitmask-DP; UTF-8/bit-field parsing) | ⏸ DEFERRED | `06-advanced/00-syllabus.md` |

**Active install scope = Modules 0–4.** Modules 5–6 kept in the syllabus, deferred.

## Folded additions — audited vs LC post 3695233 (2026-06-16)
Cross-checked the syllabus against the "All types of patterns for Bit Manipulation" LC discuss post. Syllabus was
structurally complete (no missing module); these idioms/identities were folded into existing modules:
- **Module 0** ✅ done — char case-convert (bit 5) + letter→index `c&31` + keep/clear-low-`i` masks + range-from-n family.
- **Module 1** (when built) — add **overflow detection** (compare carry-in vs carry-out on MSB).
- **Module 2** (when built) — add **Gray↔Binary both directions** (we had binary→gray only).
- **Module 3** (when built) — add the **bit-algebra identity set**: `a+b=(a|b)+(a&b)=(a^b)+2(a&b)` · `a|b=(a^b)+(a&b)` · `(a&b)^(a|b)=a^b` · `a-b=a+(~b+1)`.
- **Module 5** (when built) — make **char-presence 26-bit mask** explicit; add **meet-in-the-middle + bitmask** note.
- **Module 6** (when built) — add **branchless min/max** `y ^ ((x^y) & -(x<y))`.

## Sources
- Scaler: BM I (Single Number, Number of 1 Bits, Binary Strings, Interesting Array, Divide Integers, Reverse Bits) + BM II (Different Bits Sum Pairwise, Strange Equality, Smallest XOR, Single Number III).
- LearnYard `bit-manipulation.tsv`: Basic Bit Concepts (18), Bitwise XOR (17), Bitwise OR (5), Bitwise AND (7).
- AlgoMaster `bit-manipulation.tsv` (13 classics).
- LC discuss post 3695233 ("All types of patterns for Bit Manipulation") — idiom/identity audit, folded above.
