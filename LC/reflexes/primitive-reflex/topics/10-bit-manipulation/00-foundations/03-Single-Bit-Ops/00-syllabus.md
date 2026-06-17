# Topic 03 — Single-Bit Operations (test / set / clear / toggle bit `i`)

> Atoms 0.4–0.8. The Operators topic gave us `& | ^ ~ << >>` as whole-number tools. This topic aims them at **one chosen bit at position `i`** — the everyday verbs of bit manipulation: *is bit i on? turn it on. turn it off. flip it.*

## The one unifying idea: `1 << i` is the "address" of bit `i`

Every operation here is built from a single mask: `1 << i` — a number with **exactly one `1`, sitting at position `i`** (all else `0`). That mask *selects* position `i`; then you pick the **operator** for the job you want, reusing the Group A roles:

| Atom | Operation | Idiom | Operator role (from Operators topic) |
|---|---|---|---|
| 0.4 | **Test** bit `i` | `(x >> i) & 1` → the bit's value `0/1` · or `(x & (1<<i)) != 0` → boolean | `&` masks to inspect |
| 0.5 | **Set** bit `i` (force to 1) | `x \| (1 << i)` | `\|` sets |
| 0.6 | **Clear** bit `i` (force to 0) | `x & ~(1 << i)` | `&` with inverted mask clears |
| 0.7 | **Toggle** bit `i` (flip) | `x ^ (1 << i)` | `^` toggles |
| 0.8 | **Odd / even** | `x & 1` | test at `i = 0` (special case of 0.4) |

The whole topic is just: **`1 << i` picks the position, the operator does the verb.** Set→`|`, clear→`&~`, toggle→`^`, test→`&` — exactly the masking/set/toggle roles already derived.

## Already partly seen (consolidate, don't re-acquire)
- **Test / read** `(x >> i) & 1` — used in Reverse Bits (read a bit at position `p`).
- **Write a bit** `x |= (b << i)` — used in Reverse Bits (place a bit at position `q`).
- **Odd/even** `x & 1` — derived in Operators §1.

This topic completes the set with **set / clear / toggle** and the `~(1<<i)` clear-mask, then unifies all five under the `1 << i` address idea.

## Derivations to do (Socratically)
1. **`1 << i` as a single-bit mask** — why it isolates exactly position `i` (place value `2^i`).
2. **Set** — why `| (1<<i)` forces bit `i` on and leaves the rest untouched (mask `0` elsewhere = keep).
3. **Clear** — why you need `~(1<<i)` (a `0` at position `i`, `1`s everywhere else) and `&` it; derive the inverted mask.
4. **Toggle** — why `^ (1<<i)` flips just bit `i`.
5. **Test** — two forms: value form `(x>>i)&1` vs boolean form `(x & (1<<i)) != 0`; when each is handier.
6. **Odd/even** as the `i=0` special case of test.

## Gotchas (carry forward from Operators)
- **Precedence:** `(x >> i) & 1` and `x & ~(1 << i)` need the parens — `& ^ |` bind looser than `+ - ==`. [[lc-java-shift-precedence-trap]]
- **`1 << i` overflows for `i ≥ 31`** → use `1L << i` when addressing bit 31+ (e.g. a 64-bit mask).
- **Test trap:** `x & (1<<i)` returns the *place value* (e.g. `8`), not `1` — so compare `!= 0`, don't compare `== 1`. The `== 1` form only works on `(x >> i) & 1`.

## Install check
For an arbitrary `x` and position `i`, write cold (each in one line): test, set, clear, toggle bit `i`. Then solve the classics:
- **Kth Bit is Set or Not** (test)
- **Get, Set, Clear ith Bit** (all three)
- **Check Odd or Even** (`x & 1`)

## Status
✅ Notes done — `02-notes.md` §1–5 + summary table, all derived Socratically:
- §1 `1 << i` as single-bit address (+ width caveat: safe-as-mask through i=31, wraps at ≥32, `1L<<i` for 64-bit)
- §2 Test boolean `(x & (1<<i)) != 0` (the `!= 0` not `== 1` trap) · value `(x >> i) & 1`
- §3 Set `x | (1<<i)` (idempotent) · §4 Clear `x & ~(1<<i)` (derived `~`-mask; works on negatives) · §5 Toggle `x ^ (1<<i)` (self-inverse, not idempotent)
- unifying idea: `1<<i` picks position, operator does verb; set/clear idempotent vs toggle self-inverse

**Problems: WAIVED as trivial** (2026-06-17). The 3 LearnYard drills (Kth Bit Set, Get/Set/Clear ith Bit, Check Odd/Even) are direct one-line applications of the derived idioms — install already happened in the Socratic derivation, and test/read + write were exercised in Reverse Bits. No grind value. Links retained for reference: GfG check-k-th-bit, GfG bit-manipulation-1666686020, GfG odd-or-even3618.

✅ **TOPIC COMPLETE** (notes-derived; drills waived).
