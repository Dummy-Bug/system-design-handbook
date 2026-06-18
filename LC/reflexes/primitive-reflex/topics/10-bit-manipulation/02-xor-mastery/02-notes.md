## 1. The parity invariant (the engine of the whole module)

Three facts from Foundations:
- `a ^ a = 0` — anything XOR'd with itself cancels.
- `a ^ 0 = a` — XOR with 0 changes nothing.
- XOR is **commutative + associative** — order doesn't matter; rearrange terms freely.

Put them on a list and the consequence is immediate:
```
5 ^ 3 ^ 5 ^ 3 ^ 9  =  (5^5) ^ (3^3) ^ 9  =  0 ^ 0 ^ 9  =  9
```

> **XOR-ing a whole list cancels every value that appears an _even_ number of times; only values appearing an
> _odd_ number of times survive.** XOR measures **parity of occurrence** — nothing else.

Refinements:
- Not just pairs — **any even count** cancels. `7^7^7^7 = 0`. Even → 0, odd → survives.
- Values are irrelevant, only **how many times** each appears: `XOR(list) = XOR(odd-count values)`.

This single fact drives atoms 2.2–2.6. **Felt-signal / trigger:** *"things pair up / parity / cancel duplicates
without a hash set."* Lives in the **cancelling-pairs** corner of the bit confusion matrix.

## 2. Single Number (LC 136) — one odd-one-out, rest twice

Array: every element appears exactly twice **except one** that appears once. XOR everything → all the pairs
cancel, the lone element is what's left.

```java
int singleNumber(int[] nums) {
    int x = 0;
    for (int n : nums) x ^= n;
    return x;            // twice-appearing values cancel; the lone one remains
}
```

### Break-the-simpler-tool (why XOR is the *intended* answer)
- **HashSet/HashMap** (add/remove or count) works but costs **O(n) extra space**.
- **XOR** = **O(1) space, O(n) time, single pass**, no data structure. LC 136's follow-up demands constant
  space → XOR is the clean answer. The parity invariant *is* the algorithm.

> **Trigger:** *"find the unpaired / odd-one-out element, ideally with no extra space"* → XOR the whole array.

## 3. Two uniques (LC 260, Single Number III) — partition on a differing bit

Array: every element twice **except two** (`a`, `b`) that appear once. Return both, O(1) space.

### Why 2.2 alone gets stuck
XOR-all still cancels the pairs, but now **two** survivors remain tangled together:
```
1^2^1^3^2^5 = 3^5 = 110     ← this is a^b, mashed into one number — can't read a or b out of it
```

### The move: a set bit of `a^b` is a place where a and b differ
A `1` in `a^b` means `a` and `b` have **different** bits there — one has `1`, the other `0`. So **partition the
whole array by that bit**:
- duplicates: both copies share identical bits → land in the **same** group → still cancel there.
- the two singles: differ at that bit → land in **different** groups.

So each group = one single + complete pairs → XOR the group → isolates that single. Reduces to two independent
Single-Number (2.2) problems.

> Pick the differing bit with the **lowbit idiom** (Foundations): `diffBit = (a^b) & -(a^b)` → lowest set bit.

```java
public int[] singleNumber(int[] nums) {
    int xorAll = 0;
    for (int n : nums) xorAll ^= n;        // xorAll = a ^ b

    int diffBit = xorAll & -xorAll;        // lowest bit where a and b differ

    int a = 0, b = 0;
    for (int n : nums) {                    // split every number into its group
        if ((n & diffBit) != 0) a ^= n;     // group: diffBit set
        else                    b ^= n;     // group: diffBit unset
    }
    return new int[]{a, b};
}
```

This two-group form is the clearest: every number goes into exactly one accumulator, and each group ends up with
one single + complete pairs, so `a` and `b` both come straight out — no reconstruction step.

Compact variant (one fewer XOR): isolate only `a`, then `b = xorAll ^ a` (since `(a^b) ^ a = b`, self-inverse —
a preview of 2.5):
```java
int a = 0;
for (int n : nums) if ((n & diffBit) != 0) a ^= n;
int b = xorAll ^ a;
```

> **Trigger:** *"**two** unpaired elements"* → XOR-all = `a^b`, then **partition on any differing bit** (`& -x`
> lowbit) to split into two independent odd-one-out problems. The "un-tangle two survivors by a distinguishing
> bit" move generalizes beyond this problem.

## 4. Once vs thrice (LC 137, Single Number II) — the parity reflex BREAKS → per-bit count mod 3

Array: every element appears exactly **three** times **except one** (appears once). Return it. O(1) space.

### Why XOR-all fails (the lesson)
The parity invariant cancels **even** counts. Here duplicates appear **3 times = odd**, so they DON'T cancel —
three copies of `x` XOR to `x`, not `0`:
```
2^2^3^2 = (2^2)^2^3 = 0^2^3 = 2^3   ✗   (not 3)
```
> **XOR only works when the cancelling count is even.** Count = 3 (or any odd) → reach for a different tool.

### The generalization: count each bit position mod 3
Forget XOR; think **per bit column** (the per-bit-counting reflex from Module 1). At any bit position `i`, every
thrice-element contributes its bit **3 times** → a multiple of 3. The single contributes its bit **once**. So:

> **For each bit `i`: (total set count across all numbers) % 3 = the single's bit at `i`** (0 or 1).
> The triples vanish under `% 3`; only the lone element's bits survive. Rebuild the answer bit by bit.

Generalizes directly: "every element `k` times except one" → **count mod `k`**. (`k=2` is just the XOR case.)

```java
public int singleNumber(int[] nums) {
    int num = 0;
    for (int i = 0; i < 32; i++) {
        int count = 0;
        for (int n : nums) count += (n >> i) & 1;   // set-bits in column i
        if (count % 3 != 0) num |= 1 << i;          // that bit belongs to the single
    }
    return num;
}
```
`O(32·n)` time, `O(1)` space. **Negatives handled for free** — iterating all 32 bits sets bit 31 (sign bit) just
like any other, so two's-complement negatives reconstruct correctly with no special case.

> **Trigger:** *"every element appears `k` times except one"* with `k` **odd** (XOR can't cancel) → **per-bit
> count mod `k`**, rebuild the answer column by column. This is the deliberate exception to the cancelling-pairs
> corner — recognizing *when the parity reflex doesn't apply* is the skill.

## 5. Reconstruction / decode — recover hidden values via self-inverse XOR

XOR is its own inverse (`a^b^b = a`). So if a value got XOR'd into something, you recover it by XOR-ing the same
thing back in. Two flavors:

### 5a. Missing Number (LC 268)
`n` distinct numbers from range `[0, n]` (one missing). Same shape as Single Number — **pair each index with its
value**; matching index/value cancel, the unpaired one (the missing number) survives. Catch: indices run
`0..n-1` but the range tops out at `n`, so seed the accumulator with `n` to cover the index the loop never visits.

```java
public int missingNumber(int[] nums) {
    int n = nums.length;
    int xor = n;                          // covers the top index 0..n-1 never reaches
    for (int i = 0; i < n; i++)
        xor ^= i ^ nums[i];               // each index pairs with its matching value → cancels
    return xor;                           // the missing number is left
}
```
O(n) time, O(1) space. (Gauss sum `n(n+1)/2 - Σnums` also works but can overflow; XOR can't.)

### 5b. Decode XORed Array (LC 1720) — the decode chain
`encoded[i] = arr[i] ^ arr[i+1]`, given `first = arr[0]`. Recover `arr` (length `n+1`).

Self-inverse un-XORs the chain one link at a time: from `encoded[i] = arr[i] ^ arr[i+1]`, XOR `arr[i]` into both
sides → **`arr[i+1] = encoded[i] ^ arr[i]`**. Seed `arr[0] = first`, walk forward.

```java
public int[] decode(int[] encoded, int first) {
    int n = encoded.length;
    int[] arr = new int[n + 1];
    arr[0] = first;
    for (int i = 1; i <= n; i++)
        arr[i] = arr[i - 1] ^ encoded[i - 1];   // each element = prev element ^ its encoded link
    return arr;
}
```
Trace `encoded=[1,2,3], first=1`: `1 → 1^1=0 → 0^2=2 → 2^3=1` → `[1,0,2,1]` ✓.
(Reusing a rolling `prev`/`first` variable instead of reading `arr[i-1]` works too — same logic, just a less
self-documenting name.)

> **Trigger:** *"a value was XOR'd in / an array was XOR-encoded, recover the original"* → XOR the known piece
> back in (`a^b^b=a`). Pairing-cancellation (5a) and chained-decode (5b) are the two shapes.

## 6. Prefix-XOR — the XOR analogue of prefix-sums

Same idea as prefix-sums, but XOR replaces `+` (and self-inverse replaces subtraction). `pre[i]` = XOR of the
first `i` elements; a **range XOR is the difference of two prefixes**:

> **`xor(L..R) = pre[R+1] ^ pre[L]`** (with the padded convention `pre[0]=0`, `pre[i]=arr[0]^…^arr[i-1]`).
> The shared `[0..L-1]` portion appears in both prefixes and cancels. Precompute once → **O(1) per query**.

### 6a. Range XOR queries (LC 1310)
Naive re-XORs each subarray per query → `O(Q·n)`. Prefix-XOR → `O(n + Q)`.

```java
public int[] xorQueries(int[] arr, int[][] queries) {
    int n = arr.length;
    int[] pre = new int[n + 1];                 // pre[0] = 0 (empty-prefix identity)
    for (int i = 0; i < n; i++) pre[i + 1] = pre[i] ^ arr[i];

    int[] ans = new int[queries.length];
    for (int q = 0; q < queries.length; q++)
        ans[q] = pre[queries[q][1] + 1] ^ pre[queries[q][0]];   // uniform, no L==0 branch
    return ans;
}
```

> **The padding trick (`size n+1`, `pre[0]=0`) removes the `L==0` special case** — `pre[L]` = "everything before
> L," so `L=0 → pre[0]=0`. Same off-by-one idiom as prefix-sums; making it reflexive kills a class of boundary
> bugs. (A non-padded `pre[i]=arr[0..i]` works but forces an `if (L==0)` branch.)

### 6b. Count Triplets That Form Two Arrays of Equal XOR (LC 1442)
Pick `i < j ≤ k`; `a = xor(arr[i..j-1])`, `b = xor(arr[j..k])`. Count triplets with `a == b`. `n ≤ 300`.

**The reframe chain (this is the whole insight):**
1. `a == b  ⟺  a ^ b == 0`.
2. `a` and `b` are adjacent disjoint ranges covering `i..k`, so `a ^ b = xor(arr[i..k])`.
3. Therefore `a == b  ⟺  xor(arr[i..k]) == 0` — **`j` vanishes from the condition.**
4. The split point doesn't matter: for any zero-XOR range `(i,k)`, **every** `j` in `i < j ≤ k` works →
   **`k - i`** valid triplets. So count all `j`'s at once: `count += (k - i)` per zero range.

**Primary solution — O(n²)** (right level for `n ≤ 300`):
```java
public int countTriplets(int[] arr) {
    int n = arr.length, count = 0;
    for (int i = 0; i < n - 1; i++) {
        int xor = arr[i];
        for (int k = i + 1; k < n; k++) {
            xor ^= arr[k];
            if (xor == 0) count += (k - i);   // whole range i..k = 0 → (k-i) valid j's
        }
    }
    return count;
}
```
(Drops the `j`-loop from the O(n³) brute force; verified `[2,3,1,6,7]→4`.)

> **⚠ OPEN / DEFERRED — O(n) optimization owed (future session).** prefix-XOR + hashmap. Reframe: zero range
> `[i..k]` ⟺ `P(k) == P(i-1)` (`P(m)=xor(arr[0..m])`). For current `k`, sum `(k-i)` over all earlier matches in
> O(1): keep `map: prefixValue -> {freq, sumOfRangeStarts}` and add **`freq*k - sum`** (the aggregate trick that
> kills the index list). Off-by-one: range start `i = m+1`, so bank `k+1` (not `k`) and seed `{0:(freq1, start0)}`.
> Derived the `freq*k - sum` chunk; left the indexing un-finalized — **re-derive & code the O(n) cleanly next time.**

> **Trigger:** *"two adjacent parts with equal XOR"* / *"count subarrays whose XOR = 0 / = K"* → `a==b ⟺ a^b==0`,
> collapse to a prefix-XOR equality; the split point usually drops out. Mirror of subarray-sum + hashmap.

## 7. Gray code (LC 89) — `i ^ (i>>1)`

**Gray code** = an ordering of all `n`-bit numbers where **consecutive entries differ in exactly one bit**
(wraps around too). Normal binary doesn't: `01→10` flips two bits. Used in hardware (rotary encoders) where
flipping 2 bits "at once" is physically impossible. LC 89: return any `n`-bit Gray sequence starting at 0
(`2ⁿ` numbers). `n=2 → [0,1,3,2]` (`00,01,11,10`).

### Approach A — reflect-and-prefix (recursive, structural)
Build `gray(n)` from `gray(n-1)`: **first half** = `prev` as-is; **second half** = `prev` **reversed**, each
with the new high bit `1<<(n-1)` set. The reversal makes the seam (last of first half ↔ first of second half)
the *same* low pattern differing only in the new high bit → one-bit step. Inside each half, steps inherit
`prev`'s one-bit property.
```java
public List<Integer> grayCode(int n) {
    if (n == 0) { List<Integer> b = new ArrayList<>(); b.add(0); return b; }
    List<Integer> prev = grayCode(n - 1);
    List<Integer> curr = new ArrayList<>(prev);
    int high = 1 << (n - 1);
    for (int i = prev.size() - 1; i >= 0; i--) curr.add(high + prev.get(i));  // reversed + high bit
    return curr;
}
```

### Approach B — the formula `gray(i) = i ^ (i >> 1)` (O(1) per number, the reflex)
Derived column-by-column from the (binary, gray) table:
- **MSB of gray = MSB of binary** (nothing to its left).
- every other **gray bit `k` = binary bit `k` XOR binary bit `k+1`** (its left-neighbor). Discovered by
  XOR-ing adjacent binary columns and matching the gray column.
- `i >> 1` slides every bit's **left-neighbor** down into its own position; `^` then XORs each bit with that
  neighbor — **all positions at once.**

Trace `i = 6 = 110`: `i>>1 = 011`, `110 ^ 011 = 101 = 5 = gray(6)` ✓.

Feeding `i = 0..2ⁿ-1` **in order** auto-produces a valid Gray sequence:
```java
public List<Integer> grayCode(int n) {
    List<Integer> result = new ArrayList<>();
    for (int i = 0; i < (1 << n); i++) result.add(i ^ (i >> 1));   // i-th Gray code, directly
    return result;
}
```
`n=2 → [0,1,3,2]` (same as Approach A), O(1) per number, no recursion/reversal.

> **Inverse (gray→binary), if ever needed:** XOR-scan from the high bit down — `b = g; while ((g >>= 1) != 0) b ^= g;`
> (each binary bit = XOR of all gray bits at-and-above it). Not drilled; bank as "exists."

> **Trigger:** *"generate Gray code / need a sequence where consecutive values differ by one bit"* → `i ^ (i>>1)`.
> The structural why (each gray bit = binary bit ^ left-neighbor) ties back to the reflection construction.
> This atom is the **positional outlier** of the XOR module — bit *reflection/positioning*, not cancellation.
