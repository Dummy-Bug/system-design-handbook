## The starting problem — dividing when only remainders are left

**The task.** You get a number `a` and a prime `p`, with `a` not a multiple of `p`. Return the number `x` between 1 and `p − 1` with `(a × x) % p == 1`. This `x` is the **modular inverse** of `a`, and it is what replaces division once only remainders are known.

**Example.**

|   a |       p | Expected output x | Check: (a × x) % p    |
| --: | ------: | ----------------: | --------------------- |
|   2 |       7 |                 4 | 8 % 7 = 1             |
|   3 |       7 |                 5 | 15 % 7 = 1            |
|   2 | 10⁹ + 7 |       500,000,004 | 1,000,000,008 % p = 1 |

**Why it matters.** An answer is `30! / 28!` (it is 870), and the problem wants it mod `p = 10^9 + 7`. Both factorials are far past `long`, so they were computed with `% p` at every step, and only their remainders are known. Dividing the remainders gives a wrong answer, as the mod rules showed:

| Expression              | Value |
| ----------------------- | ----: |
| `30! / 28!` exact       |   870 |
| `(30! % p) / (28! % p)` |     3 |
| `(24 / 6) % 7`          |     4 |
| `(24 % 7) / (6 % 7)`    |     0 |

Remainders forget how many copies of `p` were thrown away, and division needs them. The fix is to stop dividing and multiply by something else instead.

## What an inverse is — a · x ≡ 1 (mod m)

In ordinary arithmetic, dividing by 6 is multiplying by `1/6`, the number that gives 1 when multiplied by 6. Under mod `m` the same role is played by a whole number `x` in `1..m−1` with

`a · x % m == 1`, written `a · x ≡ 1 (mod m)`

and `x` is called the **modular inverse** of `a`. The sign `≡` reads as leaves the same remainder mod `m`. Mod 7, the inverse of 6 is 6 itself, because `6 · 6 = 36 = 5 · 7 + 1`. The naive way to find one tries every `x`:

```java
public class InverseBrute {
    static long inverseBrute(long a, long m) {
        for (long x = 1; x < m; x++) {
            if (a % m * x % m == 1) return x;
        }
        return -1;
    }

    public static void main(String[] args) {
        StringBuilder row = new StringBuilder("mod 7:");
        for (long a = 1; a <= 6; a++) row.append("  inv(" + a + ") = " + inverseBrute(a, 7));
        System.out.println(row);

        StringBuilder products = new StringBuilder("4 * x % 10 for x = 0..9:");
        for (long x = 0; x <= 9; x++) products.append(" " + (4 * x % 10));
        System.out.println(products + "   inverse of 4 mod 10 = " + inverseBrute(4, 10));

        long p = 1_000_000_007L;
        long s = System.nanoTime();
        long r = inverseBrute(p - 1, p);
        System.out.println("inverse of p - 1 mod p = " + r + "  time = " + (System.nanoTime() - s) / 1_000_000 + " ms");
    }
}
```

Run:
```text
mod 7:  inv(1) = 1  inv(2) = 4  inv(3) = 5  inv(4) = 2  inv(5) = 3  inv(6) = 6
4 * x % 10 for x = 0..9: 0 4 8 2 6 0 4 8 2 6   inverse of 4 mod 10 = -1
inverse of p - 1 mod p = 1000000006  time = 1460 ms
```

The search is O(m): finding the inverse of `p − 1` mod `10^9 + 7` took 1460 ms for a single number, and a problem that divides by `10^5` different numbers cannot afford it.

## An inverse exists exactly when gcd(a, m) = 1

Mod 10, the number 4 has no inverse: `4 · x % 10` only ever lands on 0, 4, 8, 2, 6. The reason is the gcd. Suppose `a · x ≡ 1 (mod m)`. Then `a · x − 1 = k · m` for some `k`, so `1 = a · x − k · m`. Any common divisor of `a` and `m` divides the right-hand side, so it divides 1. So **`gcd(a, m)` must be 1**. For `a = 4, m = 10` the gcd is 2, which can never divide 1.

The other direction (gcd 1 means an inverse exists) is true too. Its proof needs a tool this note does not cover, so here it is checked by brute force instead:

```java
public class InverseExists {
    static long gcd(long a, long b) {
        return b == 0 ? a : gcd(b, a % b);
    }

    public static void main(String[] args) {
        int checked = 0;
        for (long m = 2; m <= 300; m++) {
            for (long a = 1; a < m; a++) {
                boolean found = false;
                for (long x = 1; x < m; x++) if (a * x % m == 1) found = true;
                if (found != (gcd(a, m) == 1)) throw new AssertionError(a + " " + m);
                checked++;
            }
        }
        System.out.println("inverse exists exactly when gcd(a, m) = 1: held for all " + checked + " pairs with 2 <= m <= 300");
    }
}
```

Run:
```text
inverse exists exactly when gcd(a, m) = 1: held for all 44850 pairs with 2 <= m <= 300
```

For a prime `p`, every `a` from 1 to `p − 1` has gcd 1 with `p` (a prime's only divisors are 1 and itself), so **every nonzero remainder has an inverse**. That is the first reason contests use the prime `10^9 + 7`.

## Fermat — for a prime p, the inverse of a is a^(p−2) mod p

**Fermat's little theorem:** if `p` is prime and `p` does not divide `a`, then `a^(p−1) ≡ 1 (mod p)`. Split off one factor: `a · a^(p−2) ≡ 1`, so `a^(p−2) % p` **is the inverse**, and fast power computes it in about 30 squarings for `p = 10^9 + 7`.

Why it holds, on `p = 7, a = 3`:

```java
public class FermatTable {
    public static void main(String[] args) {
        long p = 7, a = 3;
        StringBuilder row = new StringBuilder("a * i % 7 for i = 1..6:");
        long product = 1, factorial = 1;
        for (long i = 1; i <= 6; i++) {
            row.append(" " + a * i % p);
            product = product * (a * i % p);
            factorial = factorial * i;
        }
        System.out.println(row);
        System.out.println("product of those = " + product + ", 6! = " + factorial);
        long pow5 = 1;
        for (int i = 0; i < 5; i++) pow5 = pow5 * a % p;
        long pow6 = pow5 * a % p;
        System.out.println("3^6 % 7 = " + pow6 + "   3^5 % 7 = " + pow5 + "   3 * " + pow5 + " % 7 = " + (a * pow5 % p));
    }
}
```

Run:
```text
a * i % 7 for i = 1..6: 3 6 2 5 1 4
product of those = 720, 6! = 720
3^6 % 7 = 1   3^5 % 7 = 5   3 * 5 % 7 = 1
```

| i         |   1 |   2 |   3 |   4 |   5 |   6 |
| --------- | --: | --: | --: | --: | --: | --: |
| 3 · i % 7 |   3 |   6 |   2 |   5 |   1 |   4 |

The six multiples of 3 land on 1..6 again, each exactly once, just reordered. So the product of all of them, `3^6 · 6!`, leaves the same remainder as `6!`. `6!` is not a multiple of the prime 7, so it has an inverse mod 7, and multiplying both sides by that inverse cancels it, leaving `3^6 ≡ 1`. In general the multiples `a, 2a, ..., (p−1)a` are distinct mod `p`: if `i·a ≡ j·a`, then `p` divides `(i − j)·a`, and a prime that divides a product divides one of its factors, so `p` divides `i − j`, which forces `i = j`.

```java
import java.math.BigInteger;
import java.util.*;

public class FermatInverse {
    static long power(long a, long b, long m) {
        long result = 1 % m, base = a % m;
        while (b > 0) {
            if ((b & 1) == 1) result = result * base % m;
            base = base * base % m;
            b >>= 1;
        }
        return result;
    }

    static long inverse(long a, long p) {
        return power(a, p - 2, p);
    }

    public static void main(String[] args) {
        long p = 1_000_000_007L;
        System.out.println("inverse(3) = " + inverse(3, p) + "   3 * inverse(3) % p = " + 3 * inverse(3, p) % p);
        System.out.println("inverse(p - 1) = " + inverse(p - 1, p));

        Random rnd = new Random(29);
        BigInteger bp = BigInteger.valueOf(p);
        int tests = 100_000;
        for (int t = 0; t < tests; t++) {
            long a = 1 + (long) (rnd.nextDouble() * (p - 1));
            if (inverse(a, p) != BigInteger.valueOf(a).modInverse(bp).longValue()) throw new AssertionError(a);
        }
        System.out.println("matched BigInteger.modInverse on " + tests + " random a in 1..p-1");

        System.out.println("m = 10, a = 3: 3^(10-2) % 10 = " + power(3, 8, 10) + ", and 3 * " + power(3, 8, 10) + " % 10 = " + 3 * power(3, 8, 10) % 10);
        System.out.println("m = 10: BigInteger.modInverse(3) = " + BigInteger.valueOf(3).modInverse(BigInteger.TEN) + ", and 3 * 7 % 10 = " + 3 * 7 % 10);
        System.out.println("a = 0: inverse(0) = " + inverse(0, p) + ", and 0 * that % p = " + 0 * inverse(0, p) % p);
    }
}
```

Run:
```text
inverse(3) = 333333336   3 * inverse(3) % p = 1
inverse(p - 1) = 1000000006
matched BigInteger.modInverse on 100000 random a in 1..p-1
m = 10, a = 3: 3^(10-2) % 10 = 1, and 3 * 1 % 10 = 3
m = 10: BigInteger.modInverse(3) = 7, and 3 * 7 % 10 = 1
a = 0: inverse(0) = 0, and 0 * that % p = 0
```

The Fermat inverse matched `BigInteger.modInverse` on 100,000 random `a` in `1..p−1`, and it costs O(log p) instead of the brute force's O(p).

## Fermat is wrong for a modulus that is not prime

The run above also shows `m = 10`, `a = 3`. `gcd(3, 10) = 1`, so an inverse exists: it is 7, because `3 · 7 = 21`. But the Fermat formula gives `3^(10−2) % 10 = 1`, and `3 · 1 = 3`, not 1. The theorem needs a prime modulus; for 10 it simply does not hold.

| Modulus |   a | `a^(m−2) % m` | a times that, mod m | True inverse |
| ------: | --: | ------------: | ------------------: | -----------: |
|       7 |   3 |             5 |                   1 |            5 |
|      10 |   3 |             1 |                   3 |            7 |

> [!warning] `power(a, m − 2, m)` returns a number for any `m` and any `a`, with no error. For a non-prime `m` it is usually wrong, and for `a % p == 0` it returns 0, which is not an inverse (`0 · 0 = 0`). Use Fermat only with a prime modulus and `a` not a multiple of it.

## Dividing under mod — multiply by the inverse

With the inverse, division becomes `(x / y) % p = (x % p) · inverse(y % p) % p`, valid whenever `y` divides `x` exactly and `p` does not divide `y`. Redoing both counterexamples:

```java
public class DivideByInverse {
    static long power(long a, long b, long m) {
        long result = 1 % m, base = a % m;
        while (b > 0) {
            if ((b & 1) == 1) result = result * base % m;
            base = base * base % m;
            b >>= 1;
        }
        return result;
    }

    static long divide(long x, long y, long p) {
        return x % p * power(y % p, p - 2, p) % p;
    }

    public static void main(String[] args) {
        System.out.println("inverse of 6 mod 7 = " + power(6, 5, 7) + "   24 / 6 under mod 7 = (24 % 7) * 6 % 7 = " + divide(24, 6, 7));

        long p = 1_000_000_007L;
        long f30 = 1, f28 = 1;
        for (int i = 2; i <= 30; i++) {
            f30 = f30 * i % p;
            if (i <= 28) f28 = f28 * i % p;
        }
        System.out.println("30! % p = " + f30 + ", 28! % p = " + f28);
        System.out.println("plain division:          " + f30 / f28);
        System.out.println("times the inverse of 28!: " + divide(f30, f28, p));
    }
}
```

Run:
```text
inverse of 6 mod 7 = 6   24 / 6 under mod 7 = (24 % 7) * 6 % 7 = 4
30! % p = 109361473, 28! % p = 35757887
plain division:          3
times the inverse of 28!: 870
```

| Expression        | Plain division of remainders | Times the inverse | Correct |
| ----------------- | ---------------------------: | ----------------: | ------: |
| `(24 / 6) % 7`    |                            0 |                 4 |       4 |
| `(30! / 28!) % p` |                            3 |               870 |     870 |

Why it works: `y · inverse(y) ≡ 1`, so multiplying `x / y` by `y · inverse(y)` changes nothing mod `p`, and `(x / y) · y = x`. The division formula matched BigInteger on 100,000 random exact divisions where only the remainders of `x` and `y` were used.

```mermaid
graph LR
    A[x / y mod p] -->|y times its inverse is 1| B[x times inverse of y, mod p]
    B -->|inverse = y to the p minus 2, by fast power| C[O of log p per division]
    style C fill:#2e7d32,color:#fff
```

## On LeetCode

- count-anagrams (LC 2514, 2070): the count per word is `n! / (c1! · c2! · ...)`, so every factorial in the denominator becomes a multiplication by its Fermat inverse.
- number-of-ways-to-reach-a-position-after-exactly-k-steps (LC 2400, 1751): the answer is a choose-count, `k! / (r! · (k−r)!)` mod `10^9 + 7`, computed with inverses.
- fancy-sequence (LC 1622, 2476): undoing an earlier multiply-all by `m` means multiplying by the inverse of `m` mod `10^9 + 7`.
- count-the-number-of-arrays-with-k-matching-adjacent-elements (LC 3405, 2310): a choose-count times a fast power, with the factorial denominators handled by inverses.
