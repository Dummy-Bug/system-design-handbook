# Topic 02 — Operators (`& | ^ ~ << >>` + `>>>`)

> Where real bit manipulation begins. `01-Number-System` used `%2`//`2` *arithmetic* (value-view); operators act on
> **raw bits** directly. Atom 0.3 of the foundations module. Each operator drilled to reflex, then the "magic"
> combinations (Modules 1–3) fall out.

## Group A — Bitwise logic (combine two numbers bit-by-bit, each position independent)

| Op | Name | Result bit is `1` when… | Core use |
|----|------|--------------------------|----------|
| `&` | AND | **both** input bits are `1` | mask / test / clear bits ("keep only…") |
| `\|` | OR | **either** input bit is `1` | set bits ("turn on…") |
| `^` | XOR | the two bits **differ** | toggle; cancellation (`a^a=0`) |
| `~` | NOT (unary) | flip **every** bit | complement; ties to `-x = ~x+1` |

## Group B — Shifts (slide all bits left/right by `k`)

| Op | Name | What it does to the bits | Value meaning |
|----|------|--------------------------|----------------|
| `<< k` | left shift | slide left `k`, fill `0` on the right | **× 2^k** |
| `>> k` | arithmetic right shift | slide right `k`, fill with the **sign bit** | **⌊x / 2^k⌋** (works for negatives) |
| `>>> k` | logical / unsigned right shift | slide right `k`, fill with **`0`** | raw-bit shift (treats value as unsigned) |

## Derivations to do (Socratically)
1. AND/OR/XOR/NOT — derive each truth table; *why* each is the masking / setting / toggling tool.
2. **Shift = ×/÷ by powers of 2** (value-view) **and** sliding bits (bit-view) — both at once.
3. **`>>` vs `>>>`** — the sign-fill difference. *This fixes the P1 `-3` cliffhanger* (walk raw bits with `>>>`, read lowest with `& 1`).

## The "magic" these unlock (later modules — motivation, not now)
`n & (n-1)` clears lowest set bit → popcount in #set-bits steps, `pow2 ⇔ n&(n-1)==0` · XOR cancellation → unique-in-O(1)-space · swap without temp · add without `+` (`^` + `(a&b)<<1`) · `x & -x` isolates lowest set bit.
All of it is *just* these 7 operators applied cleverly — install the alphabet cold first.

## Gotchas (carry forward)
- **Precedence:** `& ^ | << >>` bind *looser* than `+ - ==` → parenthesize: `(x>>i)&1`. [[lc-java-shift-precedence-trap]]
- `1 << 31` overflows `int` → `1L << 31` when needed.
- Shift amount is taken **mod 32** for `int` (`1 << 32 == 1`, not 0); mod 64 for `long`.

## Install check
Compute `& | ^ ~` by hand on 4-bit examples; predict `<<` / `>>` / `>>>` results including on a **negative**; then
**redo P1 (Number of 1 Bits) with `& 1` + `>>>`** — the operator version handles negatives, closing the cliffhanger.

## Status
✅ All 7 operators derived (Socratic) and written to `02-notes.md`:
- Sec. 1 AND (masking/clear-tool, `n&1` parity, extreme masks) · Sec. 2 OR (set-tool, AND/OR duality) · Sec. 3 XOR (toggle, self-inverse `a^b^b=a`, even-occurrence cancellation) · Sec. 4 NOT (`~x = −x−1`, one's complement)
- Sec. 5 `<<` (×2^k, full fixed-width overflow traps: `1<<31` negative + `1<<32` wraps + `1L<<k` fix) · Sec. 6 `>>` (÷2^k, sign-fill, why) · Sec. 7 `>>>` (zero-fill, bit-walking, **closes P1 negative-`n` cliffhanger**, BS midpoint bonus)

✅ **TOPIC COMPLETE** — 7 operators derived + 6 problems logged in `problems/`:
1. Number of 1 Bits (operator redo) — `n & 1` + `n >>> 1`, `>>>`-over-`>>` flagged unprompted, negative-`n` cliffhanger closed
2. Single Number — XOR self-inverse, pairs cancel
3. Hamming Distance — XOR-marks-differences + set-bit count (first chained idiom)
4. Reverse Bits — read `(x>>p)&1` / write `|=(b<<q)`; **`1<<k` not `Math.pow`** (overflow clamps); **AC ≠ correct** (constraint-masked bug, self-caught)
5. Number Complement — width-bounded complement via `(1<<bitLength)-1`; `highestOneBit` returns value-not-index trap
6. Power of Two — one-set-bit necessary-not-sufficient (`0`/MIN_VALUE slip); property-guard `n>0` over value-enumeration

Deferred to `04-Idioms`: Power-of-Two via `n & (n-1)` (atom 0.10, to be derived cold).
