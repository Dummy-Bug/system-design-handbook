# Digit Operations — Drill Log

| Card | Status | First drilled | Notes |
|------|--------|---------------|-------|
| a.1 — right-to-left arithmetic loop (`%10` / `/=10`) | ● Graduated | 2026-05-24 | Clean. Needed nudge on loop condition (`while (n > 0)`) and order (reversed). |
| a.2 — left-to-right via string conversion | ● Graduated | 2026-05-24 | Initial answer was "convert to string and reverse" — corrected: string already reads L→R, no reverse needed. `s.charAt(i) - '0'` trap re-noted. |
| b.1 — `Long.toString(n).length()` | ● Graduated | 2026-05-24 | Skipped — user jumped to b.2. Implicitly held. |
| b.2 — `(int)(Math.log10(n) + 1)` with trap | ● Graduated | 2026-05-24 | User wrote the formula confidently. Trap unpacked at length — Math.log10(1000) = 2.9999..., +1 cast trick does NOT save it. Floating-point first principles explained from scratch (irrational ln(10), repeating-binary 0.1+0.2). User asked "WTF" — full derivation landed. |
| b.3 — manual `while (n > 0)` loop | ● Graduated | 2026-05-24 | n=0 trap noted (loop never enters, returns 0 instead of 1). Do-while or special-case fix recorded. |
| c.1 — sum of digits via loop | ● Graduated | 2026-05-24 | Trivial composition of a.1. No n=0 trap here (digit_sum(0) = 0 is correct). |
| d.1 — reverse via `rev = rev*10 + n%10` | ● Graduated | 2026-05-24 | User had both string and arithmetic approaches. Locked arithmetic form. Full walk table for n=4729 written. |
| d.2 — overflow trap (long accumulator) | ● Graduated | 2026-05-24 | User said "use long" — sharpened: overflow happens mid-loop silently if `rev` is int, even when assignment target is long. Same as pre-submit checklist `long j = i*i` trap. |
| e.1 — digit palindrome check | ● Graduated | 2026-05-24 | User had both string and arithmetic approaches. Sharpened the "save original before mutating n" gotcha. Negative number edge case noted for LC 9. |
| f.1 — i-th digit from right `(n / 10^i) % 10` | ● Graduated | 2026-05-24 | User gave partial answer ("divide by 10, then... 10^n"). Two-step intuition unpacked (shift then peel). Full walk table for n=4729 written. |
| f.2 — i-th digit from left | ● Graduated | 2026-05-24 | User had right idea but index was off ("n-i+1"). Sharpened to `L - 1 - i`. Note: left-indexing requires digit count step, so right-indexing is cheaper when problem allows. |
| g.1 — modify i-th digit via place-value delta | ● Graduated | 2026-05-24 | User initially confused ("WTF is this"). Backed up and unpacked place value from scratch: every number is sum of `digit × 10^i`, change one digit = adjust by `(new-old) × 10^i`. Landed clean after second pass. |
| h.1 — build n from digit array | ● Graduated | 2026-05-24 | Clean. Walk table written. Key insight captured: same line as d.1, but feed direction determines reversed-vs-original output. |
| i.1 — powers of 10 table | ● Graduated | 2026-05-24 | User answered with storage units (PB/EB) first — sharpened to numeric forms (1B = 10^9). LC default constraint = 10^9 noted. |
| i.2 — overflow boundary (int = 10^9, long = 10^18) | ● Graduated | 2026-05-24 | Clean — "9, 18". Locked. |
| j.1 — `n ≡ digit_sum(n) mod 9` | ● Graduated | 2026-05-24 | User derived both 133 mod 9 = 7 and digit_sum(133) mod 9 = 7. Full why (10^k ≡ 1 mod 9) unpacked. Generalises to mod 3. |
| j.2 — digital root closed form `1 + (n-1) % 9` | ○ Parked | 2026-05-24 | User asked "am I required to remember this?" — honest answer: no, not reflex. Theorem (j.1) is the high-leverage piece. Shortcut formula recorded in notes but parked from drill. |
| k.1 — restricted-digit set count | ● Graduated | 2026-05-24 | User initially assumed no repetition (wrote nC3 for Q1, 2*2*1 for Q2). Reframed: digits repeat by default. Re-drilled Socratically — user derived `|S|^L` (no zero) and `(|S|-1) × |S|^(L-1)` (with zero) from scratch via the 2-digit warmups. Also flagged that perms/combs machinery (Topic 10) is NOT needed here — just multiplication principle. |
| l.1 — sum of digit_sum across [1, n] | ● Graduated | 2026-05-24 | Clean case only (n = 10^L - 1). Derived column-decomposition Socratically: [0, 99] = 900, [0, 999] = 13,500. User asked "how is each-digit-appears-10^(L-1) derived" — unpacked via multiplication principle (fix one column at d, other L-1 columns free → 10^(L-1)). Final formula `L × 45 × 10^(L-1)` not memorised; reasoning is the reflex. Messy n (tight prefix) deferred to card m. |
| m.1 — digit walk Part A | ◯ Not drilled | — | |
| m.2 — digit walk Part B | ◯ Not drilled | — | |
| m.3 — digit walk include-n edge case | ◯ Not drilled | — | |
| n.1 — digit DP state | ◯ Not drilled | — | Band 1800, not required for current target. |
| n.2 — digit DP transition | ◯ Not drilled | — | Band 1800, stretch. |
| n.3 — digit DP base + memo | ◯ Not drilled | — | Band 1800, stretch. |

## Cold revision sessions

| Date | Cards tested | Misses | Action |
|------|-------------|--------|--------|
| — | — | — | — |

## Session notes

- **2026-05-24 session 1:** Installed a.1 through l.1 (18 cards graduated in one sitting). Heavy unpacking on b.2 floating-point trap (~10 min), g.1 place-value intuition (~5 min), and l.1 column decomposition (~10 min). User pulled back twice for slower pace: at l.1 introduction ("you dumped too much in one go") and at the 10^(L-1) derivation ("how is this getting derived"). Both unpacked Socratically — landed clean.
- j.2 parked by user as low-leverage shortcut. Recurring preference confirmed: derivation muscle over formula memorisation. *"these little stuff matters because i might forget all about these formulas and all after 6 months but the derivation muscle should stay intact"* — applied throughout.
- Topic 04 stands at 18/24 cards graduated after one session. Remaining: m.1-m.3 (digit walk for messy n, 1700-band, the big one) and n.1-n.3 (digit DP, 1800-band stretch). Card m is the natural next session — it's the messy-n extension of l.1 that the user is now primed for.
