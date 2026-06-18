# Module 2 — XOR mastery

> The most contest-relevant module of the bit family. Everything flows from one fact — **XOR is self-inverse, so
> it measures parity and cancels values that appear an even number of times.** Built after Module 1; uses the
> read/write and counting reflexes already installed.

## Atoms (derivation order)

| # | Atom | Core idea | Classic |
|---|---|---|---|
| 2.1 | **XOR fundamentals — the parity invariant** | `a^a=0`, `a^0=a`, commutative + associative → XOR-ing a list cancels every value appearing an **even** number of times; the survivor is the odd-count one | (foundation) |
| 2.2 | **Single Number** (one odd-one-out, rest twice) | XOR the whole array → pairs cancel, lone one survives | LC 136 |
| 2.3 | **Two uniques** (two appear once, rest twice) | XOR-all = `a^b`; pick a set bit of it to **partition** elements into two groups, reduce to 2.2 | LC 260 (Single Number III) |
| 2.4 | **Once vs thrice** (all appear 3×, one once) | parity trick dies (3 is odd) → **per-bit count mod 3** | LC 137 (Single Number II) |
| 2.5 | **Reconstruction / decode** (missing number, XOR'd arrays) | XOR is its own inverse → recover hidden values by re-XOR | LC 268, LC 1720 |
| 2.6 | **Prefix-XOR** (subarray XOR queries / count subarrays XOR=K) | `xor(l..r) = pre[r] ^ pre[l-1]`; prefix-sum idea with XOR + hashmap | LC 1310, LC 1442 |
| 2.7 | **Gray code ↔ binary** (both directions) | consecutive codes differ by one bit; `g = n ^ (n>>1)`, plus the inverse | LC 89 |

## Discriminator (where this sits in the bit confusion matrix)
This whole module is the **"cancelling pairs"** corner — felt-signal: *"things pair up / parity / cancel
duplicates without a hash set."* **2.4 is the deliberate exception** that breaks the parity reflex (count appears
3× = odd, so XOR won't cancel it) and forces **per-bit count mod k**. **2.7 is the odd cousin** — positional
bit-reflection, not cancellation.

## The spine
One fact: **XOR self-inverse ⇒ counts parity ⇒ cancels even occurrences.**
- 2.2 → 2.6 = escalating uses of that fact (one survivor → two survivors → subarray ranges).
- 2.4 = the "parity doesn't apply, generalize to mod-k counting" case.
- 2.7 = the structural outlier (Gray reflection).

## Folded additions (from family-syllabus audit)
- **Gray ↔ Binary both directions** (atom 2.7) — we'd otherwise only cover binary→gray; add gray→binary inverse.

## Install loop (per atom)
Socratic derivation → notes written **only after** deriving → blind classic to verify mapping.
Holdout = a blind 1700-1800 sealed-queue problem mapped <30 min self-derived.

## Install check (graduation for Module 2)
Cold: derive Single Number (2.2), the two-uniques partition (2.3), per-bit-mod-3 (2.4), and
`xor(l..r)=pre[r]^pre[l-1]` (2.6) from blank page. Then → **Module 3 — Per-bit thinking & properties**.

## Status
✅ **MODULE 2 COMPLETE** (2026-06-18). Notes in `02-notes.md`.
*(one open carry: 2.6b LC 1442 O(n) hashmap optimization owed — see below)*
- 2.1 parity invariant (XOR cancels even-count values) ✅
- 2.2 Single Number (LC 136) — XOR-all, O(1) space ✅
- 2.3 Two uniques (LC 260) — XOR-all=`a^b`, partition on lowbit differing bit ✅
- 2.4 Once vs thrice (LC 137) — parity breaks (odd count) → per-bit count mod 3 ✅ *(self-derived)*
- 2.5a Missing Number (LC 268) — pair index↔value, seed with `n`, self-inverse ✅ *(self-derived)*
- 2.5b Decode XORed Array (LC 1720) — decode chain `arr[i]=arr[i-1]^encoded[i-1]` ✅ *(self-derived)*
- 2.6a Range XOR queries (LC 1310) — prefix-XOR, `pre[R+1]^pre[L]`, padding kills L==0 branch ✅ *(self-derived)*
- 2.6b Count triplets equal XOR (LC 1442) — `a==b⟺xor(i..k)==0`, `j` drops, `+= (k-i)`; O(n²) ✅ *(self-derived)*
       ⚠ **O(n) hashmap optimization DEFERRED — owed in a future session** (derived `freq*k - sum` aggregate; left
       the off-by-one/indexing un-coded). Re-derive & implement O(n) cleanly next time.
- 2.7 Gray code (LC 89) — reflect-and-prefix (recursive) + `i^(i>>1)` formula (derived column-by-column) ✅ *(self-derived recursion)*

Next → **Module 3 — Per-bit thinking & properties** (`03-per-bit-properties/`).
