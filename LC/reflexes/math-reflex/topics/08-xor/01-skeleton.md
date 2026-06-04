# XOR [1100]

Exclusive OR — the bit-level operation whose identity-based algebra makes it the most-used "trick" operator in LC. Distinct from general bit operations (#7) because XOR enables algebraic reasoning (`a ^ a = 0`, telescoping, prefix invariants) that AND/OR don't.

Appears at every band. Peaks in standalone form around 1500-1600 (7.7%) where XOR-prefix patterns become the dominant counting technique. Tapers at higher bands not because XOR disappears — but because it fuses into harder topics (trie, contribution, mod-2 linear algebra).

## Empirical frequency

| Band | XOR-tagged | % of math |
|------|-----------|-----------|
| 1100-1399 | (folded into BIT_XOR = 40, ~14%) | — |
| 1400-1499 | 2 | 2.5% |
| 1500-1599 | 6 | 7.7% |
| 1600-1699 | — | 6-7% (XOR prefix dominant form) |
| 1700-1799 | 2 | 2.8% |
| 1800-1899 | 2 | 2.6% |
| 1900+ | tail | — |

**Total: ~25 problems where XOR is the binding step,** plus dozens more where it appears as a sub-step.

## Subtopic structure

Each subtopic is rated `[required-from XXXX]`. Card titles only. Content unpacked via Socratic drill on install.

---

## a. XOR identities [1100]

**Cards (4):**
- a.1 — `a ^ a = 0` (self-inverse — the cornerstone identity)
- a.2 — `a ^ 0 = a` (identity element)
- a.3 — XOR is commutative and associative — order doesn't matter, group however
- a.4 — `a ^ b ^ b = a` — XORing the same value twice cancels out

---

## b. Find the unique element (pair cancellation) [1100]

**Cards (1):**
- b.1 — XOR all elements; pairs cancel via `a ^ a = 0`, leaving the unique element

**LC anchor:** *Single Number* (LC 136), *Missing Number* (LC 268)

---

## c. XOR with itself in a range [1200]

**Cards (2):**
- c.1 — XOR of `1 ^ 2 ^ 3 ^ ... ^ n` has a closed-form pattern (cycle of 4: `n, 1, n+1, 0` based on `n % 4`)
- c.2 — XOR of `[L, R]` = `xor(1..R) ^ xor(1..L-1)` — prefix XOR reduction

**LC anchor:** *XOR Operation in an Array* (LC 1486)

---

## d. XOR as parity per bit [1300]

**Depends on:** Parity → f.1 [1500] (cross-reference)

**Cards (1):**
- d.1 — XOR of bit-i across n numbers = 1 iff odd count of those n numbers have bit-i set. XOR is per-bit parity.

---

## e. Prefix XOR for subarrays [1500]

**Cards (3):**
- e.1 — Define `pxor[i] = a[0] ^ a[1] ^ ... ^ a[i-1]`, with `pxor[0] = 0`
- e.2 — XOR of subarray `[l, r]` = `pxor[r+1] ^ pxor[l]`
- e.3 — "Count subarrays with XOR = k": for each prefix, count earlier prefixes equal to `pxor ^ k` via hashmap

**LC anchor:** *Count the Number of Beautiful Subarrays* (LC 2588), *Subarray Sum Equals K* (analog), *Subarrays with XOR Equal to k*

---

## f. XOR of two strings / arrays [1500]

**Cards (1):**
- f.1 — "Minimum operations to make XOR of array equal to k": XOR all, compare to k bit by bit — answer = popcount of `current ^ k`

**LC anchor:** *Min Ops to Make Array XOR Equal to K* (LC 2997)

---

## g. Bit-by-bit greedy on XOR max/min [1500]

**Depends on:** Bit Operations → i.1 (bit-by-bit greedy) [1500]

**Cards (2):**
- g.1 — "Maximise XOR with constraint": walk bits from MSB to LSB, commit each bit if reachable
- g.2 — "Minimise XOR": match high bits first (e.g., place num2's set bits in num1's highest positions)

**LC anchor:** *Minimize XOR* (LC 2429), *Max XOR After Operations* (LC 2317)

---

## h. XOR-prefix on 2D / submatrix [1600]

**Cards (1):**
- h.1 — 2D prefix XOR: `pxor[i][j] = pxor[i-1][j] ^ pxor[i][j-1] ^ pxor[i-1][j-1] ^ grid[i][j]` (inclusion-exclusion form)

**LC anchor:** *Find the K-th Largest XOR Coordinate Value* (LC 1738)

---

## i. XOR + state pair (parity + xor) [1700]

**Cards (1):**
- i.1 — When subarray must satisfy XOR=0 AND another parity-like condition, track tuple `(pxor, parity_diff)` in hashmap

**LC anchor:** *Find Maximum Balanced XOR Subarray Length* (LC 3755)

---

## j. XOR with trie (max-XOR pair) [1700]

**Cards (2):**
- j.1 — Insert each number bit-by-bit (MSB first) into a binary trie
- j.2 — Query max XOR: walk trie taking the opposite branch when possible — O(30) per query

**LC anchor:** *Maximum XOR of Two Numbers in Array* (LC 421), *Maximum XOR With Element from Array* (LC 1707)

---

## k. XOR basis / linear algebra over GF(2) [1900]

**Cards (1):**
- k.1 — XOR basis: maintain log(max) vectors that span the XOR-closure of the set. Used for "max-XOR subset" and "is value reachable" queries.

**Note:** Above 1700 band — install only at 1900+ target.

---

## Card count

19 atomic cards across 11 subtopics.

| Target rating | Required cards (cumulative) |
|---------------|------------------------------|
| 1100-1199     | a (4) + b (1) = **5 cards** |
| 1200-1299     | + c (2) = **7 cards** |
| 1300-1399     | + d (1) = **8 cards** |
| 1400-1499     | — = 8 cards |
| 1500-1599     | + e (3) + f (1) + g (2) = **14 cards** |
| 1600-1699     | + h (1) = **15 cards** |
| 1700-1799     | + i (1) + j (2) = **18 cards** |
| 1800-1899     | — = 18 cards |
| 1900+         | + k (1) = **19 cards (full)** |

## Notes for Socratic drill

- Subtopic `a` (the four identities) is the entire foundation. `a.1` (`a ^ a = 0`) is the most invoked single fact in this whole topic — install it cold first.
- Subtopic `c.1` (XOR of 1 to n closed form) is a niche but contest-recurring trick. The cycle of 4 (`n, 1, n+1, 0`) is the answer — derive it from the pattern, install it as a lookup.
- Subtopic `e` (prefix XOR for subarrays) is the bridge between XOR and counting. Once installed, "count subarrays with XOR = k" is reflex, not derivation.
- Subtopic `j` (XOR trie) is the high-ceiling pattern at 1700+. Don't install before then — it has algorithmic prereqs.
- Subtopic `k` (XOR basis) is full linear algebra — skip until 1900+ target unless explicitly motivated.
