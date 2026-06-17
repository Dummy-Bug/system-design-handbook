# P2 — Add Binary (LC 67)

**Task:** given two binary strings `a`, `b`, return their sum as a binary string. `"11" + "1" → "100"`.

**Tooling:** schoolbook carry addition in base 2 — no bitwise operators. Digits are already separated (they're string chars), so the `%2`//`2` extraction isn't needed; the base-2 *arithmetic* (carry) is the point.

### Mapping (instant — got it in one breath)
Add from the **least-significant end** (back of the strings) forward, carrying:
- at each position `sum = bitA + bitB + carry`
- output bit = `sum % 2`, new `carry = sum / 2` (covers `1+1+1=3` → emit `1`, carry `1`)
- after both strings exhausted, append any leftover `carry`
- built low→high, so **reverse** at the end

### Final solution (single loop)
```java
class Solution {
    public String addBinary(String a, String b) {
        int i = a.length() - 1;
        int j = b.length() - 1;
        int carry = 0;
        StringBuilder sb = new StringBuilder();

        while (i >= 0 || j >= 0) {
            int sum = carry;
            if (i >= 0) sum += a.charAt(i--) - '0';
            if (j >= 0) sum += b.charAt(j--) - '0';
            sb.append(sum % 2);
            carry = sum / 2;
        }
        if (carry != 0) sb.append('1');

        return sb.reverse().toString();
    }
}
```
Trace `"11"+"1"`: (2→`0`,c1) (2→`0`,c1) (carry→`1`) → `"001"` → reverse → `"100"` ✓.

### Headline lesson: the bugs were all PLUMBING, not algorithm
The mapping was correct immediately. **Every** bug was in translating idea → correct loop code — i.e. *implementation rust*, not a thinking gap. This is the implementation-speed half of [[lc-derivation-budget-chunking]] (mapping vs implementation), and the rusty half is the *easy* one to fix: pure reps.

Four bugs in the first attempt, all mechanical:

| # | Bug | Why it broke | Fix |
|---|---|---|---|
| 1 | `while (j-- >= 0 && i-- >= 0)` | post-decrement mutates the index *before* the body reads it → reads one char too early / `charAt(-1)` crash; `&&` short-circuit also desyncs the two decrements | condition only **tests** (`i>=0 && j>=0`); decrement **inside** the body |
| 2 | only `if (digit>=2) carry=1;` | carry never reset → once `1`, stuck `1` forever | `carry = sum / 2;` (or add `else carry = 0`) |
| 3 | tail loops crossed strings: `while(j>=0){ a.charAt(i) }` | loop variable and string mismatched — `j` drains `b`, but it read `a`; `i` was stale `-1` → crash | pair them: `j`↔`b`, `i`↔`a`, always |
| 4 | `sb.append(digit % BASE - '0')` | `digit%2` is already the number `0/1`; subtracting `'0'`(48) gives `-47`, and `append(int)` writes `"-47"` | `sb.append(sum % 2)` — no `- '0'` |

### The reusable fix (kills a whole bug class)
**Bugs 1 and 3 both came from having three near-duplicate loops** (main + two tails). Duplication is where copy-paste errors breed (wrong index, stale variable). Collapsing to **one loop** that pulls a bit from each string *only if its index is still valid* (`if (i >= 0) sum += …`) removes the tail loops entirely → bugs 1 and 3 cannot occur.

> **Reflex:** "main loop + parallel tail loops over two sequences" → collapse to one loop guarded by `if (idx valid)`. Fewer loops, no crossed indices, uniform carry.

### Perturbation debrief (worked Socratically, then written)

Poke the "suspicious specifics" to find which assumptions are **load-bearing** (break the algorithm) vs **cosmetic** (change nothing).

**Perturbation 1 — the base (2 → 10 → any `b`). COSMETIC.**
Add two *decimal* strings instead (`"47"+"8"`)? Only `% 2 → % b` and `/ 2 → / b` change. The back-to-front loop, `sum = carry + digits`, output `sum % b`, `carry = sum / b`, the reverse — all identical. Schoolbook carry-addition is **base-agnostic** (same as P1's digit-iterator). The base is a knob, not load-bearing.

**Perturbation 2 — the operand count (2 → `k` strings). LOAD-BEARING, hidden in one line.**
The line `if (carry != 0) sb.append('1')` secretly assumes **the final carry is a single digit `1`** — i.e. it bakes in `k = 2`.

*How big can the carry get when adding `k` numbers in base `b`?* It **never exceeds `k − 1`**, regardless of base. Proof (induction on columns): if `carry_in ≤ k−1`, then `sum ≤ (k−1) + k(b−1) = kb − 1`, so `carry_out = ⌊sum/b⌋ ≤ ⌊(kb−1)/b⌋ = k−1`. Starts at 0 → stays `≤ k−1` forever. (No snowball — the feedback converges, it doesn't blow up.)

- `k = 2`, base 2 → max carry `= 1` = a single bit `'1'` → `append('1')` is **correct** (our exact problem). ✓
- `k = 3`, base 2 → max carry `= 2` = `"10"` — **two digits** → `append('1')` loses the `0`. ✗

**The fix = P1's digit-iterator, applied to the leftover carry:**
```java
while (carry > 0) { sb.append(carry % base); carry /= base; }
```
The leftover carry is itself a multi-digit number; emit *all* its digits (low→high), not a single `'1'`.

*Trace — `k=4`, all `"1"` (truth: `1+1+1+1 = 4 = "100"`):* one column → `sum = 4` → append `0`, `carry = 2`. Old line `append('1')` → `"01"` → `"10"` = 2 ✗. Emit-loop: `2%2=0` (carry 1), `1%2=1` (carry 0) → append `0,1` → built `"001"` → reverse → `"100"` = 4 ✓.

**Connection:** the same primitive (P1's `%base`//`base` iterator) that read a number's digits now *writes out* the leftover carry's digits. The "trivial" `append('1')` was the special case `k=2` in disguise.

*Status: AC after debugging (implementation rust — bugs were plumbing, not algorithm; mapping was instant). Counts as a clean concept rep on base-2 carry addition. Perturbation findings: base = cosmetic; operand-count `k=2` = load-bearing (hidden in `append('1')`; general fix = carry emit-loop, max carry `= k−1`).*
