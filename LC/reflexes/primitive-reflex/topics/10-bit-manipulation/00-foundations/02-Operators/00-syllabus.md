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
Syllabus set. Derivations pending (Socratic), starting with `&`. Notes → `02-notes.md`; problems → `problems/`.
