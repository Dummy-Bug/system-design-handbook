# Module 1 — Counting & bit arithmetic

> The "do arithmetic *with* bits" module. Foundations (Module 0) gave you the alphabet; here you count bits
> efficiently and rebuild `+`, `-`, `×`, `÷` out of `^` / `&` / `<<` when the operators themselves are forbidden
> or when per-bit structure is the point. Built off Idioms Sec. 1 (`x & (x-1)` drops the lowest set bit).

## Atoms (derivation order)

| # | Atom | Idiom / core | Classic to verify |
|---|---|---|---|
| 1.1 | **popcount** (count set bits, answer-proportional) | `while(x != 0){ x &= x-1; c++; }` — Idioms Sec. 1 looped | Number of 1 Bits |
| 1.2 | **Counting Bits DP** (popcount of `0..n` as an array) | `bits[i] = bits[i>>1] + (i&1)`  (alt: `bits[i&(i-1)] + 1`) | Counting Bits (LC 338) |
| 1.3 | **count set bits in `1..N`** (total ones across a range) | per-bit periodicity: bit `b` cycles every `2^(b+1)`, half are ones | Count Total Set Bits |
| 1.4 | **reverse bits** | swap-from-ends, or divide-and-conquer mask swaps | Reverse Bits (LC 190) |
| 1.5 | **add via XOR + carry** (add without `+`) | `sum = a^b`, `carry = (a&b)<<1`, loop till carry `0` | Sum of Two Integers (LC 371) |
| 1.6 | **divide without `/` or `%`** | subtract shifted divisor; double the divisor via `<<` | Divide Two Integers (LC 29) |
| — | folded: **overflow detection** | compare carry-in vs carry-out on the MSB | (within 1.5) |

## Discriminator (where these sit in the bit confusion matrix)
- **1.1–1.3 = per-bit counting** — summing how many bits are set; leans on `x&(x-1)` or per-bit periodicity.
- **1.4 = positional rearrangement** — moving bits, not counting them.
- **1.5–1.6 = bit-arithmetic** — `^` is "add with no carry," `(a&b)<<1` is "the carry"; multiply/divide are
  repeated shift-add. This is the one place carry-arithmetic legitimately enters the bit family (the
  scope-boundary exception called out in the family syllabus: *Sum of Two Integers* is genuinely-bit).

## Install loop (per atom)
Socratic derivation first → notes written **only after** deriving → blind classic to verify mapping.
Retention = blank-page retrieval, never re-reading. Same loop as Module 0.

## Install check (graduation for Module 1)
Cold one-liners: popcount loop, Counting-Bits recurrence, add-via-XOR loop.
Classics cold: Number of 1 Bits (bit way), Counting Bits (LC 338), Sum of Two Integers (LC 371).
Then → **Module 2 — XOR mastery**.

## Status
✅ **MODULE 1 COMPLETE** (2026-06-18). Notes in `02-notes.md`.
- 1.1 popcount (Kernighan `x&=x-1` loop; negatives resolved) ✅
- 1.2 Counting Bits DP `dp[i>>1]+(i&1)` (LC 338; +alt `dp[i&(i-1)]+1` as trivia) ✅
- 1.3 count set bits in `1..N` — per-bit periodicity, column-flip, O(log N) (GfG) ✅
- 1.4 reverse bits ✅ **already done in Foundations** → `00-foundations/02-Operators/problems/04-reverse-bits.md`
  (two-ptr read/write `(x>>p)&1` / `|=(b<<q)`; banked: `1<<k` not `Math.pow`, AC≠correct). Not duplicated here.
- 1.5 add via XOR+carry (LC 371) — `sum=a^b`, `carry=(a&b)<<1`, loop till carry 0; sum/XOR identity banked ✅
- 1.6 divide without `*`/`/`/`%` (LC 29) — batch-doubling subtraction, O(log); 2 overflow spots (use `long`) ✅

Next → **Module 2 — XOR mastery** (`02-xor-mastery/`).
