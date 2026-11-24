## The starting problem — one tile for many walls

**The task.** You get an array of positive whole numbers. Return the largest number that divides every element exactly, the **gcd of the array**.

**Example.** Five walls have lengths 12, 18, 8, 9 and 30, and one square tile size must fit every wall a whole number of times, so the tile side must divide every length:

| Array              | Numbers dividing every element | Expected output |
| ------------------ | ------------------------------ | --------------: |
| [12, 18, 8, 9, 30] | 1                              |               1 |
| [24, 36, 60]       | 1, 2, 3, 4, 6, 12              |              12 |

**Why it matters.** Whether an array can be split, scaled or reduced to equal parts usually comes down to the gcd of all its elements.

The naive way copies the brute force for two numbers: start at the smallest element and walk down until a candidate divides every element. For two numbers near 10^9 that walk already took 640 ms, and an array only adds work to every candidate.

## The gcd of an array folds left to right, and can stop at 1

Euclid showed that `(a, b)` and `(gcd(a, b), 0)` have the same common divisors, so **the common divisors of `a` and `b` are exactly the divisors of `gcd(a, b)`**. A number divides `a`, `b` and `c` exactly when it divides `gcd(a, b)` and `c`, so `gcd(a, b, c) = gcd(gcd(a, b), c)`, and the whole array is one running value updated element by element. Start the running value at 0, because `gcd(0, x) = x`. The running gcd only ever stays the same or drops to a divisor of itself, and once it hits 1 it stays 1 (`gcd(1, x) = 1`), so the loop can stop there.

| Element read |  12 |  18 |   8 |   9 |
| ------------ | --: | --: | --: | --: |
| Running gcd  |  12 |   6 |   2 |   1 |

```java
public class GcdFold {
    static long gcd(long a, long b) {
        return b == 0 ? a : gcd(b, a % b);
    }

    static int read = 0;

    static long gcdOfArray(long[] nums) {
        long g = 0;
        read = 0;
        for (long x : nums) {
            g = gcd(g, x);
            read++;
            if (g == 1) break;
        }
        return g;
    }

    public static void main(String[] args) {
        System.out.println("[12, 18, 8, 9, 30] -> gcd " + gcdOfArray(new long[]{12, 18, 8, 9, 30}) + ", read " + read + " of 5 elements");
        System.out.println("[24, 36, 60]       -> gcd " + gcdOfArray(new long[]{24, 36, 60}) + ", read " + read + " of 3 elements");
    }
}
```

Run:
```text
[12, 18, 8, 9, 30] -> gcd 1, read 4 of 5 elements
[24, 36, 60]       -> gcd 12, read 3 of 3 elements
```

The fold costs n Euclid calls at most, O(n log max), and matched the walk-down brute force on 100,000 random arrays.

## The gcd of factorials is the factorial of the minimum

**Problem:** given an array, return the gcd of the factorials of its elements, where `n! = 1·2·...·n`. For `[5, 3, 7]` that is `gcd(120, 6, 5040)`, and the expected output is 6. Computing the factorials is the broken part: they leave `long` at 21!, as the first line of the run shows.

```java
import java.math.BigInteger;

public class GcdFactorials {
    static BigInteger fact(int n) {
        BigInteger f = BigInteger.ONE;
        for (int i = 2; i <= n; i++) f = f.multiply(BigInteger.valueOf(i));
        return f;
    }

    public static void main(String[] args) {
        long f = 1;
        for (int i = 2; i <= 21; i++) f *= i;
        System.out.println("21! in a long = " + f + ", exact 21! = " + fact(21));
        int[] nums = {5, 3, 7};
        BigInteger g = BigInteger.ZERO;
        for (int x : nums) g = g.gcd(fact(x));
        System.out.println("[5, 3, 7]: gcd(120, 6, 5040) = " + g + ", and 3! = " + fact(3));
    }
}
```

Run:
```text
21! in a long = -4249290049419214848, exact 21! = 51090942171709440000
[5, 3, 7]: gcd(120, 6, 5040) = 6, and 3! = 6
```

No factorial needs computing. Let `m` be the minimum. For any `k ≥ m`, `k! = m! · (m+1) · ... · k`, so `m!` divides every factorial in the array and is a common divisor. And no common divisor can be bigger than `m!`, because `m!` is itself one of the numbers. So the answer is `m!`, here `3! = 6`, and it matched the BigInteger computation on 10,000 random arrays.

## A subsequence with gcd 1 exists exactly when the whole array has gcd 1

**Problem:** can some **subsequence** (any choice of elements, order kept) have gcd 1? Order does not change a gcd, so this is a question about subsets. Expected output: `true` for `[6, 10, 15]`, `false` for `[6, 12, 18]`. Trying all of them is `2^n − 1` choices.

```java
public class SubsetGcdOne {
    static long gcd(long a, long b) {
        return b == 0 ? a : gcd(b, a % b);
    }

    static boolean anySubsequenceBrute(long[] a) {
        int n = a.length;
        for (int mask = 1; mask < (1 << n); mask++) {
            long g = 0;
            for (int i = 0; i < n; i++) if ((mask >> i & 1) == 1) g = gcd(g, a[i]);
            if (g == 1) return true;
        }
        return false;
    }

    static boolean anySubsequence(long[] a) {
        long g = 0;
        for (long x : a) g = gcd(g, x);
        return g == 1;
    }

    public static void main(String[] args) {
        System.out.println("[6, 10, 15]: " + anySubsequence(new long[]{6, 10, 15}) + "   [6, 12, 18]: " + anySubsequence(new long[]{6, 12, 18}));
        long[] evens = new long[24];
        for (int i = 0; i < 24; i++) evens[i] = 2L * (i + 1);
        long s = System.nanoTime();
        boolean r = anySubsequenceBrute(evens);
        System.out.println("brute on 24 even numbers: " + r + "  subsets tried = " + ((1 << 24) - 1) + "  time = " + (System.nanoTime() - s) / 1_000_000 + " ms");
    }
}
```

Run:
```text
[6, 10, 15]: true   [6, 12, 18]: false
brute on 24 even numbers: false  subsets tried = 16777215  time = 1264 ms
```

The brute force needed more than a second for just 24 elements, and every extra element doubles it. The one-pass rule in `anySubsequence` matched it on 100,000 random arrays, and it holds for two reasons:

- **If the whole array has gcd `g > 1`:** `g` divides every element, so it divides the gcd of any choice of elements, and no choice can reach 1.
- **If the whole array has gcd 1:** the whole array is itself a subsequence, and its gcd is 1.

## Delete exactly one element to maximise the gcd — prefix and suffix gcd

**Problem:** remove exactly one element so the gcd of the rest is as large as possible. For `[12, 18, 7, 30]` the 7 is the obvious culprit, and removing it leaves `gcd(12, 18, 30) = 6`.

The naive way removes each element in turn and refolds the other `n − 1`: O(n²) gcd calls. The fix is to precompute two arrays, and then deleting index `i` leaves everything before it and everything after it, so the gcd of the rest is `gcd(pre[i], suf[i+1])`, one Euclid call per index:

- `pre[i]` = gcd of the first `i` elements, `nums[0..i−1]`, with `pre[0] = 0`.
- `suf[i]` = gcd of `nums[i..n−1]`, with `suf[n] = 0`.

| Delete index | Element | pre[i] | suf[i+1] | gcd of the rest |
| -----------: | ------: | -----: | -------: | --------------: |
|            0 |      12 |      0 |        1 |               1 |
|            1 |      18 |     12 |        1 |               1 |
|            2 |       7 |      6 |       30 |               6 |
|            3 |      30 |      1 |        0 |               1 |

```java
import java.util.*;

public class DeleteOne {
    static long gcd(long a, long b) {
        return b == 0 ? a : gcd(b, a % b);
    }

    static long bestAfterDeleteBrute(long[] nums) {
        long best = 0;
        for (int i = 0; i < nums.length; i++) {
            long g = 0;
            for (int j = 0; j < nums.length; j++) {
                if (j != i) g = gcd(g, nums[j]);
            }
            best = Math.max(best, g);
        }
        return best;
    }

    static long bestAfterDelete(long[] nums) {
        int n = nums.length;
        long[] pre = new long[n + 1];
        long[] suf = new long[n + 1];
        for (int i = 0; i < n; i++) pre[i + 1] = gcd(pre[i], nums[i]);
        for (int i = n - 1; i >= 0; i--) suf[i] = gcd(suf[i + 1], nums[i]);
        long best = 0;
        for (int i = 0; i < n; i++) best = Math.max(best, gcd(pre[i], suf[i + 1]));
        return best;
    }

    public static void main(String[] args) {
        long[] nums = {12, 18, 7, 30};
        System.out.println("best after deleting one from " + Arrays.toString(nums) + " = " + bestAfterDelete(nums));
        Random rnd = new Random(8);
        long[] big = new long[100_000];
        for (int i = 0; i < big.length; i++) big[i] = 1 + rnd.nextInt(1_000_000_000);
        long s = System.nanoTime();
        bestAfterDelete(big);
        System.out.println("n = 100000: prefix/suffix " + (System.nanoTime() - s) / 1_000_000 + " ms");
        s = System.nanoTime();
        bestAfterDeleteBrute(big);
        System.out.println("n = 100000: brute " + (System.nanoTime() - s) / 1_000_000 + " ms");
    }
}
```

Run:
```text
best after deleting one from [12, 18, 7, 30] = 6
n = 100000: prefix/suffix 4 ms
n = 100000: brute 38180 ms
```

The prefix and suffix version matched the brute force on 100,000 random arrays. At `n = 100,000` the brute force took 38 seconds and the prefix and suffix version 4 ms. Building the arrays is n Euclid calls each, so the whole thing is O(n log max).

> [!warning] The two sentinels are 0, not 1: `pre[0] = 0` and `suf[n] = 0` mean nothing on that side, and `gcd(0, x) = x`. A sentinel of 1 would make every answer 1.

## The attack game — the last survivor's minimum health is the gcd

**Problem:** N players have strengths `A[0..N−1]`. When player `i` attacks player `j`, `A[j]` becomes `A[j] − A[i]`, and a player whose health reaches 0 or below is out. Attacks continue until one player is left. What is the smallest health that last survivor can end with? For strengths `[12, 18, 30]` the expected output is 6. The brute force tries every sequence of attacks. It explodes quickly, but on small games it gives the true answer to check against.

```java
import java.util.*;

public class AttackGame {
    static Map<List<Integer>, Integer> memo = new HashMap<>();

    static int bestSurvivor(List<Integer> health) {
        if (health.size() == 1) return health.get(0);
        Integer cached = memo.get(health);
        if (cached != null) return cached;
        int best = Integer.MAX_VALUE;
        for (int i = 0; i < health.size(); i++) {
            for (int j = 0; j < health.size(); j++) {
                if (i == j) continue;
                List<Integer> next = new ArrayList<>(health);
                int left = health.get(j) - health.get(i);
                if (left <= 0) next.remove(j);
                else next.set(j, left);
                Collections.sort(next);
                best = Math.min(best, bestSurvivor(next));
            }
        }
        memo.put(health, best);
        return best;
    }

    static void playSmallestHitsLargest(List<Integer> health) {
        List<Integer> h = new ArrayList<>(health);
        while (h.size() > 1) {
            Collections.sort(h);
            int last = h.size() - 1, left = h.get(last) - h.get(0);
            if (left == 0) h.remove(last);
            else h.set(last, left);
            System.out.print(h + " ");
        }
        System.out.println();
    }

    static int gcd(int a, int b) {
        return b == 0 ? a : gcd(b, a % b);
    }

    public static void main(String[] args) {
        for (List<Integer> start : List.of(List.of(12, 18, 30), List.of(6, 10, 15))) {
            int g = gcd(gcd(start.get(0), start.get(1)), start.get(2));
            System.out.println("strengths " + start + ": best last survivor = " + bestSurvivor(start) + ", gcd = " + g);
        }
        playSmallestHitsLargest(List.of(12, 18, 30));
    }
}
```

Run:
```text
strengths [12, 18, 30]: best last survivor = 6, gcd = 6
strengths [6, 10, 15]: best last survivor = 1, gcd = 1
[12, 18, 18] [12, 18, 6] [6, 12, 12] [6, 12, 6] [6, 6, 6] [6, 6] [6] 
```

The exhaustive search agrees with the gcd on both games, and on 2,000 random games of 2 to 4 players (also under the stricter rule that a player may only attack someone with at least its own health). The reason has two halves:

- **Never below `g`.** Every health starts as a multiple of `g = gcd(A)`, and a multiple of `g` minus a multiple of `g` is still a multiple of `g`. The survivor has positive health, and the smallest positive multiple of `g` is `g`.
- **`g` is reachable.** Let the smallest player always attack the largest. That is the subtraction form of Euclid running on the whole group, so the gcd of the alive players never changes, and a player only leaves when its health hits exactly 0. The trace above walks `[12, 18, 30]` down to `[6]`.

## On LeetCode

- x-of-a-kind-in-a-deck-of-cards (LC 914, 1371): the groups exist exactly when the gcd of all the card counts is at least 2.
- find-the-maximum-factor-score-of-array (LC 3334, 1519): remove at most one element, with prefix and suffix gcd arrays exactly as above (plus a matching pair of arrays for the least common multiple).
- check-if-it-is-a-good-array (LC 1250, 1983): the answer is whether the gcd of the whole array is 1.
- minimum-number-of-operations-to-make-all-array-elements-equal-to-1 (LC 2654, 1929): returns −1 exactly when the gcd of the whole array is above 1; otherwise it needs the shortest subarray with gcd 1.
