# Module 0 — Foundations (the alphabet)

> The bit alphabet you must have **cold** before any trigger module. This isn't trigger-mapping — it's recall:
> these idioms should fire in <2s so derivation budget in later modules goes to *mapping*, not re-deriving `x&-x`.
> Install = drill each to blank-page reflex, verified by the LearnYard "Basic Bit Concepts" classics.

## Sub-topic folders (each = `NN-Topic/` with `02-notes.md` + `problems/`)

Module 0 is split into 4 topic folders — grouped so each is a real chunk (not one monolith, not over-fragmented):

| Folder | Atoms | Topic | Status |
|---|---|---|---|
| `01-Number-System/` | 0.1, 0.2 | representation: place value, binary, conversion, fixed width/range, two's complement | ✅ notes done (Sec. 1–9); problems: P1 number-of-1-bits, P2 add-binary done · P3 alternating-bits pending |
| `02-Operators/` | 0.3 | the 6 operators `& \| ^ ~ << >>` (+ `>>>`) — what each does bit-by-bit | ✅ COMPLETE — notes Sec. 1–7 (all 7 ops) + 6 problems (1-bits redo, single-number, hamming, reverse-bits, complement, power-of-two) |
| `03-Single-Bit-Ops/` | 0.4–0.8 | test / set / clear / toggle bit `i` from `1<<i`; odd-even | ✅ notes Sec. 1–5 (all 5 verbs derived); drills waived as trivial |
| `04-Idioms/` | 0.9–0.18 | `x&-x`, `x&(x-1)`, masks, char tricks, power checks, range masks | ✅ notes Sec. 1–7 (all atoms 0.9–0.18) + Power-of-Four problem |

## Atoms (drill to reflex)

| # | Concept | Idiom / code | Classic to verify |
|---|---|---|---|
| 0.1 | Binary representation, place values | bit `i` has value `2^i` | Decimal to Binary |
| 0.2 | **2's complement** (how negatives work) | `-x = ~x + 1`; high bit = sign | (conceptual) |
| 0.3 | The 6 operators | `& \| ^ ~ << >>` | — |
| 0.4 | Test bit `i` | `(x >> i) & 1` | Kth Bit is Set or Not |
| 0.5 | Set bit `i` | `x \| (1<<i)` | Get, Set, Clear ith Bit |
| 0.6 | Clear bit `i` | `x & ~(1<<i)` | Get, Set, Clear ith Bit |
| 0.7 | Toggle bit `i` | `x ^ (1<<i)` | — |
| 0.8 | Odd/even | `x & 1` | Check Odd or Even |
| 0.9 | **Lowbit** (isolate lowest set bit) | `x & -x` | — |
| 0.10 | **Drop lowest set bit** | `x & (x-1)` | (→ popcount, Module 1) |
| 0.11 | Low-`k` all-ones mask | `(1<<k) - 1` | — |
| 0.12 | Set rightmost **unset** bit | `x \| (x+1)` | Set the Rightmost Unset Bit |
| 0.13 | Number complement (flip within width) | `x ^ ((1<<bits)-1)` | Number Complement |
| 0.14 | Power-of-two check | `x>0 && (x&(x-1))==0` | Power of Two |
| 0.15 | Power-of-four check | power-of-two **and** `(x & 0x55555555)!=0` (alt: pow2 && `n%3==1`) | Power of Four |
| 0.16 | **Char case convert** (bit 5) | `c\|32`→lower · `c&~32`→upper · `c^32`→toggle case | (string problems) |
| 0.17 | **Letter → index** (1..26) | `c & 31` (or `c-'a'+1` / `c-'A'+1`) | (string problems) |
| 0.18 | **Keep / clear low `i` bits** | keep low: `x & ((1<<i)-1)` · clear low: `x & ~((1<<i)-1)` | range masks |

> Range-from-position family (from LC post 3695233, verify exact semantics on use): `x\|(x+1)` set lowest cleared (0.12) · `x&(x+(1<<n))` clear set-bits from n · `x\|(x-(1<<n))` set cleared-bits from n.

## Identities to know cold
`x^x = 0` · `x^0 = x` · `x&(x-1)` removes the lowest set bit · `x&-x` isolates it · XOR is its own inverse (`a^b^b = a`).

## ⚠ Java gotchas (recurring-bug guard)
- **Operator precedence:** `&`/`^`/`|`/`<<`/`>>` all bind **looser than `+ - ==`** → always parenthesize: `(x>>i)&1`, `low + ((hi-lo)>>1)`. [[lc-java-shift-precedence-trap]]
- **`1<<i` overflows int** for `i≥31` → use `1L<<i` when shifting past bit 30.
- `>>>` (unsigned) vs `>>` (signed/arithmetic) — use `>>>` when treating as raw bits.

## Install check (graduation for this module)
Blank-page reproduce all 18 idioms in <2s each, AND solve Get/Set/Clear + Power-of-Two + Number-Complement cold.
Then → Module 1.

## Status
✅ **MODULE 0 COMPLETE** (2026-06-17) — all 4 sub-topics derived Socratically + noted:
- `01-Number-System` ✅ (Sec. 1–9 + Sec. 6B subtraction-by-borrow; revised cold 2026-06-17) — problems: P1 number-of-1-bits, P2 add-binary
- `02-Operators` ✅ (all 7 ops Sec. 1–7) — 6 problems
- `03-Single-Bit-Ops` ✅ (5 verbs; drills waived as trivial)
- `04-Idioms` ✅ (atoms 0.9–0.18, Sec. 1–7) — Power-of-Four problem

All 18 atoms (0.1–0.18) derived. Next: **Module 1 — Counting & bit arithmetic** (`01-counting-arithmetic`).
