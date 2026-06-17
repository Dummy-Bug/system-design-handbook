# Topic 04 — Idioms (the "magic" combinations)

> Atoms 0.9–0.18. Single-Bit-Ops aimed an operator at *one* bit via `1 << i`. This topic is where the operators combine into idioms that aren't obvious from the truth tables — the moves that *look* like magic until you derive them, then become one-liners you fire on reflex. Almost every one leans on a Number-System fact (`2^k − 1`, `~x = −x − 1`).

## The idioms, in derivation order

### Group A — the lowest-set-bit family (the core magic)
| Atom | Idiom | Does | Leans on |
|---|---|---|---|
| 0.10 | `x & (x - 1)` | **drops** the lowest set bit (clears it to 0) | `x-1` flips the lowest 1 and the zeros below it |
| 0.9 | `x & -x` | **isolates** the lowest set bit (keeps only it) | `-x = ~x + 1` (§4) |

These two are a pair — one removes the lowest set bit, the other extracts it. Derive `x & (x-1)` first (simpler), then `x & -x`.

### Group B — mask building
| Atom | Idiom | Does |
|---|---|---|
| 0.11 | `(1 << k) - 1` | low-`k` **all-ones mask** (`k` ones) — the `2^k − 1` fact (§6), now as a tool |
| 0.18 | `x & ((1<<i) - 1)` / `x & ~((1<<i) - 1)` | **keep** low `i` bits / **clear** low `i` bits |

### Group C — checks built on Group A
| Atom | Idiom | Does |
|---|---|---|
| 0.14 | `x > 0 && (x & (x-1)) == 0` | **power-of-two** check (one set bit + positive) — closes the Power-of-Two redo deferred from Operators |
| 0.15 | power-of-two **and** `(x & 0x55555555) != 0` (alt: pow2 && `x % 3 == 1`) | **power-of-four** check (single bit, on an even position) |
| 0.13 | `x ^ ((1 << bits) - 1)` | **number complement** — flip within width (already met in Operators P5; reframe as `^ mask`) |

### Group D — char / letter tricks (bit 5 = the case bit)
| Atom | Idiom | Does |
|---|---|---|
| 0.16 | `c \| 32` → lower · `c & ~32` → upper · `c ^ 32` → toggle case | ASCII case convert (uppercase/lowercase differ only in bit 5) |
| 0.17 | `c & 31` (= `c & 0x1F`) | letter → index 1..26 (`'a'`/`'A'` → 1, …) |

### Group E — rightmost-unset / range-from-position (verify on use)
| Atom | Idiom | Does |
|---|---|---|
| 0.12 | `x \| (x + 1)` | **set** the rightmost **unset** (0) bit |
| — | `x & (x + (1<<n))` · `x \| (x - (1<<n))` | clear/set bits from position `n` (from LC post 3695233 — verify exact semantics on use) |

## Derivations to do (Socratically)
1. **`x & (x-1)` drops the lowest set bit** — why subtracting 1 flips the lowest `1` to `0` and turns the zeros below into `1`s, so AND wipes that whole low chunk. (Then: repeatedly applying it counts set bits in #set-bits steps → Module 1 popcount.)
2. **`x & -x` isolates the lowest set bit** — using `-x = ~x + 1`: above the lowest set bit the bits are inverted, at-and-below they align, so AND keeps exactly the lowest 1.
3. **`(1<<k) - 1` as the low-ones mask** — the `2^k − 1` fact reused as a tool; then keep/clear-low-`i`.
4. **Power-of-two via `x & (x-1) == 0`** — one set bit ⇔ dropping it gives 0; add the `x > 0` guard (the necessary-not-sufficient lesson from the Operators redo). **This is the deferred Power-of-Two install (atom 0.10 use).**
5. **Power-of-four** — power-of-two AND the single bit sits at an even position; why `0x55555555` (mask of even positions) tests that.
6. **Char case bit** — why upper/lower ASCII differ only in bit 5 (value 32), so `|32`/`&~32`/`^32` convert; `c & 31` strips to the 1..26 letter index.

## Identities to hold cold
`x & (x-1)` removes lowest set bit · `x & -x` isolates it · `(1<<k)-1` = `k` ones · `x ^ x = 0`, `x ^ 0 = x` · case bit = bit 5 (32).

## Gotchas
- **Precedence:** parenthesize everything — `(x & (x-1)) == 0`, not `x & (x-1) == 0` (the `==` binds tighter than `&`!). [[lc-java-shift-precedence-trap]]
- **`x & -x` on `Integer.MIN_VALUE`** returns MIN_VALUE itself (its own lowest bit is the sign bit) — fine as a pattern, watch arithmetic use.
- **`(1 << k) - 1`** for `k = 32` is wrong on `int` (shift wraps mod 32 → `1<<32 = 1` → mask `0`); use `-1` (all ones) or `1L` for full-width.
- Power-of-two/four checks need the **`x > 0`** guard (necessary-not-sufficient; `0` and negatives slip through one-bit tests).

## Install check
Cold one-liners: drop-lowest-bit, isolate-lowest-bit, low-`k` mask, power-of-two, power-of-four, case-convert. Classics:
- **Power of Two** (`x & (x-1)` way — the deferred redo)
- **Power of Four**
- **Set the Rightmost Unset Bit** (atom 0.12)
- (LearnYard "Basic Bit Concepts" idiom rows)

## Status
**In progress.** Notes `02-notes.md`:
- §1 `x & (x-1)` drops lowest set bit (general region proof from §6B borrow shape) ✅
- §2 power-of-two `n>0 && (n&(n-1))==0` ✅ · §3 power-of-four `+ (n & 0x55555555)!=0` (single bit on even position) ✅
- §4 `x & -x` isolates lowest set bit (lowbit, via `-x=~x+1`; matched pair w/ §1) ✅

Problems: `problems/01-power-of-four.md` ✅ (also exercised `n&(n-1)` pow2 mechanic → closes the rep deferred from Operators). Power-of-Three explored + **rejected as non-bit** (no bit structure for non-power-of-2 base; boundary lesson: bit tricks are for powers of 2 — divisor-of-`3^19` trick & loop noted, not installed).

**Remaining atoms:** 0.11 `(1<<k)-1` low-ones mask · 0.18 keep/clear low `i` bits · 0.13 number-complement reframe (`^ mask`) · 0.16/0.17 char case bit (`|32`/`&~32`/`^32`) + letter→index (`c&31`) · 0.12 set rightmost unset `x|(x+1)` · Group E range-from-position (verify on use).
