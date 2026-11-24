## The starting problem — an answer too big to print

**The task.** You get a length `n`, from 1 to 1000. Count the strings of exactly that length made only of the characters `0` and `1`. The count is too big to print, so return its remainder after dividing by 1,000,000,007, written **mod 10⁹ + 7**.

**Example.** Each position can be `0` or `1`, so every extra position doubles the count, and the count is 2ⁿ:

|    n | Strings                                |                      Count | Expected output |
| ---: | -------------------------------------- | -------------------------: | --------------: |
|    1 | 0, 1                                   |                          2 |               2 |
|    2 | 00, 01, 10, 11                         |                          4 |               4 |
|    3 | 000, 001, 010, 011, 100, 101, 110, 111 |                          8 |               8 |
|   64 | too many to list                       | 18,446,744,073,709,551,616 |     582,344,008 |
| 1000 | too many to list                       |         a 302-digit number |     688,423,210 |

**Why it matters.** LeetCode asks for the answer mod 10⁹ + 7 whenever the true answer does not fit in a `long`, and every such problem needs the rules in this note.

The plain way doubles a `long` `n` times and takes `% m` at the end, with `m = 10⁹ + 7`.

```java
import java.math.BigInteger;

public class PowerOfTwo {
    public static void main(String[] args) {
        long m = 1_000_000_007L;
        BigInteger bm = BigInteger.valueOf(m);

        long ways = 1;
        for (int n = 1; n <= 64; n++) {
            ways = ways * 2;
            if (n >= 62) System.out.println("no mod,  n = " + n + ": ways = " + ways + ", then % m = " + (ways % m));
        }

        long modded = 1;
        for (int n = 1; n <= 1000; n++) {
            modded = modded * 2 % m;
            if (n == 64 || n == 1000) System.out.println("mod each step, n = " + n + ": " + modded + "   BigInteger: " + BigInteger.TWO.pow(n).mod(bm));
        }
    }
}
```

Run:
```text
no mod,  n = 62: ways = 4611686018427387904, then % m = 145586002
no mod,  n = 63: ways = -9223372036854775808, then % m = -291172004
no mod,  n = 64: ways = 0, then % m = 0
mod each step, n = 64: 582344008   BigInteger: 582344008
mod each step, n = 1000: 688423210   BigInteger: 688423210
```

The plain version is right up to `n = 62`. At 63 the `long` wraps negative (its largest value is `2^63 − 1`), and at 64 every bit has shifted out and the count is 0. Taking `% m` at the end cannot repair a number that is already wrong. The version that takes `% m` after every doubling matches BigInteger at 64 and at 1000.

**Diagnosis:** the final remainder is all that is asked for, and it turns out every intermediate value can be replaced by its own remainder without changing that final remainder. The rest of the note is why that is allowed, for which operations, and the one operation where it is not.

## Why the modulus is 10^9 + 7

```java
public class ModConstants {
    public static void main(String[] args) {
        long m = 1_000_000_007L;
        boolean prime = true;
        for (long d = 2; d * d <= m; d++) {
            if (m % d == 0) { prime = false; break; }
        }
        System.out.println("1000000007 is prime: " + prime);
        System.out.println("fits in int: " + (m <= Integer.MAX_VALUE) + "   (m - 1) + (m - 1) = " + (2 * (m - 1)) + " <= Integer.MAX_VALUE = " + Integer.MAX_VALUE);
        System.out.println("(m - 1) * (m - 1) = " + (m - 1) * (m - 1) + " <= Long.MAX_VALUE = " + Long.MAX_VALUE);
        int r = 1_000_000_006;
        System.out.println("same product in int arithmetic: " + (r * r));
    }
}
```

Run:
```text
1000000007 is prime: true
fits in int: true   (m - 1) + (m - 1) = 2000000012 <= Integer.MAX_VALUE = 2147483647
(m - 1) * (m - 1) = 1000000012000000036 <= Long.MAX_VALUE = 9223372036854775807
same product in int arithmetic: 1923446820
```

| Property                                           | Why it matters                                                                        |
| -------------------------------------------------- | ------------------------------------------------------------------------------------- |
| It is prime                                        | every remainder except 0 then has an inverse, which is how division is done under mod |
| Fits in `int`, and so does a sum of two remainders | `(a + b) % m` never overflows an `int`                                                |
| The product of two remainders fits in `long`       | `(a * b) % m` is safe in `long`, but wraps in `int` (1923446820 above)                |

A remainder mod `m` is always in `0..m−1`, so the largest product of two of them is `(m−1)²`, about 10^18, which is under `Long.MAX_VALUE` (about 9.2·10^18).

## The four rules — replace any operand by its remainder

Write `a = qa·m + ra` and `b = qb·m + rb`, where `ra = a % m` and `rb = b % m`. Every multiple of `m` vanishes from a remainder, so:

- **Addition:** `a + b = (qa + qb)·m + (ra + rb)`, hence `(a + b) % m = (a % m + b % m) % m`.
- **Multiplication:** `a·b = m·(qa·qb·m + qa·rb + qb·ra) + ra·rb`, hence `(a * b) % m = ((a % m) * (b % m)) % m`.
- **Adding m changes nothing:** `a + m` has quotient one higher and the same leftover, hence `a % m = (a + m) % m`.
- **Subtraction:** `(a − b) % m = (a % m − b % m + m) % m`. The difference of two remainders lies in `−(m−1)..(m−1)`; adding `m` moves it into `1..2m−1` without changing its remainder (the previous rule), and the last `% m` brings it into `0..m−1`.

The `+ m` exists because Java's `%` keeps the sign of the left operand, so `(3 − 5) % m` is `−2`, not a remainder at all.

```java
import java.math.BigInteger;
import java.util.*;

public class ModRules {
    static final long M = 1_000_000_007L;

    static long add(long a, long b) { return (a % M + b % M) % M; }
    static long mul(long a, long b) { return (a % M) * (b % M) % M; }
    static long sub(long a, long b) { return (a % M - b % M + M) % M; }

    public static void main(String[] args) {
        System.out.println("(3 - 5) % M            = " + (3 - 5) % M);
        System.out.println("((3 - 5) + M) % M      = " + ((3 - 5) + M) % M);
        System.out.println("sub(3, 5)              = " + sub(3, 5));
        System.out.println("sub(5, 3)              = " + sub(5, 3));

        Random rnd = new Random(1);
        BigInteger bm = BigInteger.valueOf(M);
        int tests = 100_000;
        for (int t = 0; t < tests; t++) {
            long a = rnd.nextLong() >>> 4, b = rnd.nextLong() >>> 4;
            BigInteger A = BigInteger.valueOf(a), B = BigInteger.valueOf(b);
            if (add(a, b) != A.add(B).mod(bm).longValue()) throw new AssertionError("add");
            if (mul(a, b) != A.multiply(B).mod(bm).longValue()) throw new AssertionError("mul");
            if (sub(a, b) != A.subtract(B).mod(bm).longValue()) throw new AssertionError("sub");
        }
        System.out.println("add, mul and sub matched BigInteger on " + tests + " random pairs below 2^60");
    }
}
```

Run:
```text
(3 - 5) % M            = -2
((3 - 5) + M) % M      = 1000000005
sub(3, 5)              = 1000000005
sub(5, 3)              = 2
add, mul and sub matched BigInteger on 100000 random pairs below 2^60
```

> [!warning] Forgetting the `+ m` in a subtraction gives a negative answer, which LeetCode marks wrong, and a negative index if the value is used to index an array.

## Apply the mod at every step, not at the end

The rules say an operand may be replaced by its remainder, which only helps if it is done **before** the value overflows. A product of 25 numbers shows the difference:

```java
import java.math.BigInteger;

public class ModEachStep {
    public static void main(String[] args) {
        long m = 1_000_000_007L;
        long noMod = 1, eachStep = 1;
        BigInteger exact = BigInteger.ONE;
        for (int i = 2; i <= 25; i++) {
            noMod = noMod * i;
            eachStep = eachStep * i % m;
            exact = exact.multiply(BigInteger.valueOf(i));
        }
        System.out.println("25! exact           = " + exact);
        System.out.println("25! % m, BigInteger = " + exact.mod(BigInteger.valueOf(m)));
        System.out.println("mod at the end      = " + noMod % m + "   (the long had already wrapped to " + noMod + ")");
        System.out.println("mod at every step   = " + eachStep);
    }
}
```

Run:
```text
25! exact           = 15511210043330985984000000
25! % m, BigInteger = 440732388
mod at the end      = 332217180   (the long had already wrapped to 7034535277573963776)
mod at every step   = 440732388
```

| Strategy             | Result for 25! % m | Correct |
| -------------------- | -----------------: | ------- |
| mod at the end       |          332217180 | no      |
| mod at every step    |          440732388 | yes     |
| BigInteger reference |          440732388 | yes     |

The rule of thumb: every line that adds or multiplies something that may already be large ends in `% m`, and every running value is stored already reduced.

```mermaid
graph LR
    A[value below m] -->|times x below m| B[below m squared, fits long]
    B -->|% m| A
    style A fill:#2e7d32,color:#fff
```

## Division does not carry through mod

The tempting fourth operation, `(a / b) % m = (a % m) / (b % m)`, is false. The smallest counterexample, and a realistic one:

```java
import java.math.BigInteger;

public class DivisionUnderMod {
    public static void main(String[] args) {
        long m = 7;
        long a = 24, b = 6;
        System.out.println("(24 / 6) % 7             = " + (a / b) % m);
        System.out.println("(24 % 7) / (6 % 7)       = " + (a % m) + " / " + (b % m) + " = " + (a % m) / (b % m));

        long p = 1_000_000_007L;
        long f30 = 1, f28 = 1;
        for (int i = 2; i <= 30; i++) {
            f30 = f30 * i % p;
            if (i <= 28) f28 = f28 * i % p;
        }
        BigInteger exact = fact(30).divide(fact(28));
        System.out.println("30! / 28! exact          = " + exact);
        System.out.println("(30! % p) / (28! % p)    = " + f30 + " / " + f28 + " = " + f30 / f28);
    }

    static BigInteger fact(int n) {
        BigInteger f = BigInteger.ONE;
        for (int i = 2; i <= n; i++) f = f.multiply(BigInteger.valueOf(i));
        return f;
    }
}
```

Run:
```text
(24 / 6) % 7             = 4
(24 % 7) / (6 % 7)       = 3 / 6 = 0
30! / 28! exact          = 870
(30! % p) / (28! % p)    = 109361473 / 35757887 = 3
```

`24 / 6 = 4`, but after reducing, `3 / 6` is 0 in integer division. `30! / 28! = 30·29 = 870`, but the reduced factorials divide to 3. Remainders forget how many whole copies of `m` were thrown away, and division needs exactly that information. So an answer that needs a division, like `n! / (k!·(n−k)!)`, cannot be computed by reducing first and dividing after. Division under a prime modulus has to be replaced by multiplication with a different number, the **modular inverse**, which takes fast power to compute.

## On LeetCode

- binary-prefix-divisible-by-5 (LC 1018, 1376): the prefix number doubles and adds a bit at every step; keeping only `% 5` at every step is the whole solution.
- smallest-integer-divisible-by-k (LC 1015, 1875): the number `11...1` outgrows `long` almost at once, so only its remainder `r = (r * 10 + 1) % k` is kept.
- concatenation-of-consecutive-binary-numbers (LC 1680, 1630): the number is shifted left and the next value added, `n` times, with `% m` after every step or it overflows within a few numbers.
- number-of-substrings-with-only-1s (LC 1513, 1351): each run of length `L` contributes `L·(L+1)/2`, summed with `% m` at every addition.
- count-number-of-texts (LC 2266, 1857): a DP whose every addition of earlier states is reduced mod 10^9 + 7.
