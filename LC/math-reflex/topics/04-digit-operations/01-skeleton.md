# Digit Operations [1100]

Manipulating the individual digits of an integer — counting, summing, reversing, replacing, walking. Mechanics are simple at low bands (decimal-base loops with `% 10` and `/ 10`), and the topic deepens substantially around Band 1700+ into **digit DP / digit walk**, where you count integers in `[1, n]` with a digit-pattern property.

Mostly closed at Band 1900 — past that, digit problems appear inside larger DP/string contexts rather than as standalone digit problems.

## Empirical frequency

| Band | DIGIT_OPS problems | Notes |
|------|-------------------|-------|
| 1100-1399 | 40 (under DIGIT legacy tag, 14.0% of math) | Strong anchor zone |
| 1400-1499 | 10 (12.3% of math — #2 most common) | |
| 1500-1599 | 7 | |
| 1600-1699 | 7 | |
| 1700-1799 | 3 | Digit walk starts |
| 1800-1899 | 4 | Digit DP territory |
| 1900+ | 0 | |

**Total: ~71 problems.** Heavy concentration at 1100-1500 makes this a high-leverage anchor topic for Q1 / easy-Q2 speed.

## Subtopic structure

Each subtopic is rated `[required-from XXXX]`. Card titles only. Content unpacked via Socratic drill on install.

---

## a. Iterate digits of n [1100]

**Cards (2):**
- a.1 — Standard right-to-left loop using `n % 10` and `n /= 10`
- a.2 — Left-to-right traversal via string conversion

---

## b. Digit count of n [1100]

**Cards (3):**
- b.1 — `Long.toString(n).length()` — most reliable
- b.2 — `(int) Math.log10(n) + 1` — formula form, watch floating-point edge cases at exact powers of 10
- b.3 — Manual `while (n > 0)` digit-counting loop

---

## c. Sum of digits of n [1100]

**Cards (1):**
- c.1 — Loop accumulator pattern over `n % 10`

---

## d. Reverse digits of n [1100]

**Cards (2):**
- d.1 — Build reversed via `rev = rev*10 + n%10; n /= 10`
- d.2 — Overflow risk when reversing large ints (e.g., `Reverse Integer` problem)

**LC anchor:** *Reverse Integer* (LC 7)

---

## e. Check digit palindrome [1200]

**Depends on:** Reverse digits [1100]

**Cards (1):**
- e.1 — Compare n to reversed(n) — equal → palindrome

---

## f. Place value / extracting the i-th digit [1300]

**Cards (2):**
- f.1 — i-th digit from the right: `(n / 10^i) % 10`
- f.2 — i-th digit from the left: count digits first, then index

---

## g. Modifying / replacing a specific digit [1300]

**Cards (1):**
- g.1 — Replace i-th digit with new value: extract, subtract old × 10^i, add new × 10^i

---

## h. Building n from a digit array [1300]

**Cards (1):**
- h.1 — Left-to-right accumulator: `n = n * 10 + digit[i]`

---

## i. Powers of 10 reflex [1400]

**Cards (2):**
- i.1 — Powers of 10 up to 10^9 (memorise table)
- i.2 — `10^k` overflow boundary: 10^9 fits int, 10^10 needs long, 10^18 fits long, 10^19 overflows long

---

## j. Digit-sum identities [1400]

**Cards (2):**
- j.1 — `n ≡ digit_sum(n) (mod 9)` — divisibility-by-9 reflex
- j.2 — Repeated digit-sum until single digit = `1 + (n-1) % 9` (digital root)

**LC anchor:** *Add Digits* (LC 258)

---

## k. Numbers with restricted-digit set [1500]

**Cards (1):**
- k.1 — Count of L-digit numbers using only digits from set S = `(|S|-1) × |S|^(L-1)` (when 0 ∈ S) or `|S|^L` (when 0 ∉ S)

**LC anchor:** *Numbers At Most N Given Digit Set* (LC 902)

---

## l. Sum of digits across a range [1600]

**Cards (1):**
- l.1 — Sum of digit_sum(i) for i in `[1, n]` — closed-form / digit-position contribution

---

## m. Digit walk (no memo) for "count in [1, n] with property" [1700]

The 1700-band digit DP precursor — for properties expressible without a memoization table, walk n's digits left-to-right contributing combinations at each position.

**Cards (3):**
- m.1 — Part A: count of numbers with d < length(n) digits — closed-form sum over digit counts
- m.2 — Part B: walk n's digits, at each position contribute `(digit_at_i) × (remaining_combinations)`
- m.3 — Edge case: include n itself if it satisfies the property

**LC anchor:** *Count Numbers with Unique Digits* (LC 357), *Numbers At Most N Given Digit Set* (LC 902), *Count Distinct Strip-Zero Values* (your 2026-05-21 problem)

---

## n. Digit DP with tight-bound flag [1800]

**Depends on:** Digit walk [1700], DP memoization (algorithmic prereq)

**Cards (3):**
- n.1 — State design: `(position, tight, started, custom_state)`
- n.2 — Transition: when tight, restrict next digit to ≤ current digit of n; otherwise 0-9
- n.3 — Base case + memoization keys

**LC anchor:** *Find Good Integers* (LC 3267 — partial), *Count Stepping Numbers in Range* (LC 2801)

---

## Card count

24 atomic cards across 14 subtopics.

| Target rating | Required cards (cumulative) |
|---------------|------------------------------|
| 1100-1199     | a (2) + b (3) + c (1) + d (2) = **8 cards** |
| 1200-1299     | + e (1) = **9 cards** |
| 1300-1399     | + f (2) + g (1) + h (1) = **13 cards** |
| 1400-1499     | + i (2) + j (2) = **17 cards** |
| 1500-1599     | + k (1) = **18 cards** |
| 1600-1699     | + l (1) = **19 cards** |
| 1700-1799     | + m (3) = **22 cards** |
| 1800+         | + n (3) = **24 cards (full)** |

## Notes for Socratic drill

- Subtopics `a`-`d` are the bedrock — every digit problem invokes one of them. Graduate these first; they unlock most of 1100-1399.
- Subtopic `i.2` (overflow boundary table) is the cousin of the Java-impl checklist item from CLAUDE.md. Pair this card's install with a re-read of `02-syntax/05-conversions.md`.
- Subtopic `j` (digit-sum identities) is the easiest "trick" card in the syllabus — the mod-9 reflex unlocks several Q1 problems instantly.
- Subtopic `m` (digit walk) is the foundation for digit DP. Install it cold before `n` — `n` is just `m` plus memoization.
- Subtopic `n` (digit DP) is the closing card for this topic at 1800. Once installed, the topic is fully covered for the Q3 reach. The depth past that is in the algorithmic DP topic, not here.
