# The decision rule, in one table

Before anything new, the three from last session are restated as a single decision — and this is the form worth memorising, because it is how you pick one in real code.

| Requirement | Interface |
|---|---|
| take input → perform a **conditional check** → return **boolean** | **`Predicate`** |
| take input → perform an **operation** → return a result **of any type** | **`Function`** |
| take input → perform an operation → **return nothing** | **`Consumer`** |

> [!info] **A function can return boolean too.** Nothing stops `Function<Integer, Boolean>`. But if what you want **is** a boolean, go for `Predicate` — it exists for exactly that, and it says so in the type.

---

# Consumer chaining

`Function` had `andThen` and `compose`. **`Consumer` has chaining too** — and one of those two methods.

## The movie example

```java
import java.util.function.*;

class Movie {
    String name;
    Movie(String name) { this.name = name; }
}

class MovieDemo {
    public static void main(String[] args) {
        Consumer<Movie> c1 = m -> System.out.println(m.name + " ready to release");
        Consumer<Movie> c2 = m -> System.out.println(m.name + " released but it is a bigger flop");
        Consumer<Movie> c3 = m -> System.out.println(m.name + " storing info in database");

        Movie m = new Movie("Spyder");
        c1.accept(m);
        c2.accept(m);
        c3.accept(m);

        System.out.println("--- chained ---");
        Consumer<Movie> cc = c1.andThen(c2).andThen(c3);
        cc.accept(m);
    }
}
```

Measured on JDK 25:

```
Spyder ready to release
Spyder released but it is a bigger flop
Spyder storing info in database
--- chained ---
Spyder ready to release
Spyder released but it is a bigger flop
Spyder storing info in database
```

**Three separate consumers**, each a different thing you might do to a movie — announce it, report its result, store it. `cc` is the **chained consumer**: one `accept()` call runs all three, in order.

> [!info] **Don't read too much into the `println`s.** Don't feel it is only a SOP statement — of course I am doing the corresponding activities also. `c3` stands for genuinely writing to a database; printing is just what fits on a slide.

## `Consumer` has `andThen` but **not** `compose`

Measured on JDK 25:

```java
c1.compose(c2).accept("x");
```

```
error: cannot find symbol
  symbol:   method compose(Consumer<String>)
```

> **`Function` has both `andThen` and `compose`. `Consumer` has only `andThen`.**

> [!question]- **Deep dive — why `Consumer` has no `compose`, and it is not an oversight.** `compose` means **run the other one first, then feed its result into me**. A `Consumer` **returns nothing**, so there is no result to feed anywhere. `c2.compose(c1)` would have to take `c1`'s output — and `c1` has none.
>
> `andThen` survives because it needs no result: it means **run me, then run the other one on the same input**. That works fine for consumers, and it is exactly what the movie example does — all three consumers receive the same `Movie` object.
>
> The same reasoning explains the whole family. Wherever a method passes a value along the chain, only the result-producing interfaces can have it.

---

# `Supplier`

The fourth of the four, and the mirror image of `Consumer`.

> Sometimes I don't want to give any input. Just supply my required objects — it won't take any input. Then we should go for supplier.

```java
interface Supplier<R> {
    public R get();
}
```

| | Takes | Returns | Method |
|---|---|---|---|
| `Consumer<T>` | one input | **nothing** | `accept()` |
| `Supplier<R>` | **nothing** | one object | `get()` |

> [!important] **The type parameter on `Supplier` is the RETURN type, not the input type.** This is the exam question. `Supplier` never accepts any input, so there is no input type to name — the single parameter can only be what it hands back.

And because `get()` takes no argument and there is only one method, **there is no question of chaining** for `Supplier`.

## Supplier 1 — the system date

```java
import java.util.function.*;
import java.util.Date;

Supplier<Date> s = () -> new Date();
System.out.println(s.get());
```

Measured on JDK 25:

```
Fri Aug 14 22:06:32 IST 2026
```

Call `s.get()` as many times as you like — every call supplies the date again.

## Supplier 2 — a random OTP

Can you please supply a random OTP? An OTP is usually **six digits**, and each digit can be anything from **0 to 9**.

**First, the logic for one random digit** — this is worth deriving rather than memorising:

| Expression | Minimum | Maximum |
|---|---|---|
| `Math.random()` | `0.0` | `0.99999…` — **never 1.0** |
| `Math.random() * 10` | `0.0` | `9.9999…` |
| `(int)(Math.random() * 10)` | **0** | **9** |

So `(int)(Math.random() * 10)` gives a random digit 0–9. Six of them, appended, is the OTP:

```java
Supplier<String> otp = () -> {
    String o = "";
    for (int i = 0; i < 6; i++) o = o + (int) (Math.random() * 10);
    return o;
};
for (int i = 0; i < 6; i++) System.out.println(otp.get());
```

Measured on JDK 25:

```
802158
268118
153579
650561
769108
548215
```

Six calls, six different values, no repeats — the chance of repeating is very, very low.

> **Write the supplier once; call it any number of times.** That is the payoff of all four of these interfaces.

---

# Two-argument functional interfaces

Now the limitation that runs through everything so far.

> **`Predicate`, `Function` and `Consumer` all take exactly ONE input.**

That is fine for is this number even? But what about **the sum of two given numbers — is it even?** Two inputs, one check. None of the three can express it.

> **For that, go for the two-argument functional interfaces**, and `Bi` means **two**.

| One argument | Two arguments | Type parameters |
|---|---|---|
| `Predicate<T>` | **`BiPredicate<T, U>`** | 2 |
| `Function<T, R>` | **`BiFunction<T, U, R>`** | **3** |
| `Consumer<T>` | **`BiConsumer<T, U>`** | 2 |
| `Supplier<R>` | ❌ **no `BiSupplier`** | — |

> [!important] **Why there is no `BiSupplier`, and why that question is a good one.** `Bi` refers to **two input arguments**. But a supplier **never takes any input at all** — so there is nothing for `Bi` to double. Then automatically, where is the question of BiSupplier?
>
> Measured on JDK 25:
> ```java
> BiSupplier<String> s = null;
> ```
> ```
> error: cannot find symbol
> ```
> It does not exist. Nor does `TriPredicate` or `QuadPredicate` — the family stops at two.

**Everything else is unchanged.** Except that it takes two arguments, all the remaining methods, everything is the same — API-wise no difference at all. `BiPredicate` still has `test`, `and`, `or`, `negate`; `BiFunction` still has `apply` and `andThen`.

## `BiPredicate`

```java
BiPredicate<Integer, Integer> p = (a, b) -> (a + b) % 2 == 0;
System.out.println(p.test(10, 20));
System.out.println(p.test(15, 20));
```

Measured on JDK 25:

```
true
false
```

10 + 20 = 30, even → `true`. 15 + 20 = 35, odd → `false`.

## `BiFunction` — and why it takes three type parameters

Provide an employee number and a name; get back an `Employee` object.

- input 1: `Integer` — the employee number
- input 2: `String` — the name
- return: `Emp`

**Three types, so three type parameters** — `BiFunction<Integer, String, Emp>`.

```java
import java.util.function.*;
import java.util.*;

class Emp {
    int eno;
    String name;
    Emp(int eno, String name) { this.eno = eno; this.name = name; }
}

BiFunction<Integer, String, Emp> f = (eno, name) -> new Emp(eno, name);

ArrayList<Emp> l = new ArrayList<Emp>();
l.add(f.apply(100, "Durga"));
l.add(f.apply(200, "Ravi"));
l.add(f.apply(300, "Shiva"));
l.add(f.apply(400, "Pavan"));
for (Emp e : l) System.out.println(e.eno + "  " + e.name);
```

Measured on JDK 25:

```
100  Durga
200  Ravi
300  Shiva
400  Pavan
```

The `BiFunction` has become an **object factory** — give it the two pieces of data and it is responsible for producing the object.

## `BiConsumer` — modify, return nothing

Give every employee a 500 rupee raise. Two inputs (**which employee**, **how much**), nothing returned.

```java
class Emp2 {
    String name;
    double salary;
    Emp2(String name, double salary) { this.name = name; this.salary = salary; }
}

ArrayList<Emp2> l2 = new ArrayList<Emp2>();
l2.add(new Emp2("Durga", 1000));
l2.add(new Emp2("Sunny", 2000));
l2.add(new Emp2("Bunny", 3000));
l2.add(new Emp2("Chinny", 4000));

BiConsumer<Emp2, Double> c = (e, d) -> e.salary = e.salary + d;
for (Emp2 e : l2) c.accept(e, 500.0);
for (Emp2 e : l2) System.out.println(e.name + "  " + e.salary);
```

Measured on JDK 25:

```
Durga  1500.0
Sunny  2500.0
Bunny  3500.0
Chinny  4500.0
```

It returned nothing, and yet every salary changed — a consumer can still **mutate** the object it is handed. Returning nothing is not the same as doing nothing.

> [!important] **The compile error he hits live, and it is a good one.** Writing `c.accept(e, 500)` instead of `500.0` fails. Measured on JDK 25:
> ```
> error: incompatible types: int cannot be converted to Double
> ```
> Autoboxing will turn `int` into `Integer`, and widening will turn `int` into `double` — but Java will **not** do both at once. `int` → `Integer` → `Double` is two conversions, and only one is allowed. Write `500.0` and it boxes cleanly to `Double`.

---

# Reading the package itself

He opens the `java.util.function` documentation live and reads the entries, which is worth copying because the naming is completely systematic.

| Interface | Method | Takes | Returns |
|---|---|---|---|
| `Predicate<T>` | `test` | 1 | `boolean` |
| `Function<T, R>` | `apply` | 1 | `R` |
| `Consumer<T>` | `accept` | 1 | nothing |
| `Supplier<R>` | `get` | **0** | `R` |
| `BiPredicate<T, U>` | `test` | 2 | `boolean` |
| `BiFunction<T, U, R>` | `apply` | 2 | `R` |
| `BiConsumer<T, U>` | `accept` | 2 | nothing |

**Chaining methods, by interface:**

| Interface | Has |
|---|---|
| `Predicate` | `and()`, `or()`, `negate()` |
| `Function` | `andThen()`, `compose()` |
| `Consumer` | `andThen()` only |
| `Supplier` | none |

He also spots `BinaryOperator` and `BooleanSupplier` in the same package while scrolling — the **primitive** variants, which are the subject of the next part.

---

# What this part established

| | |
|---|---|
| Consumer chaining | **`andThen()`** — one `accept()` runs all of them |
| `Consumer.compose()` | ❌ does not exist — a consumer produces no result to pass on |
| `Supplier<R>` | takes **nothing**, returns an object, method **`get()`** |
| `Supplier`'s type parameter | the **return** type — there is no input type |
| Random digit 0–9 | `(int)(Math.random() * 10)` — `Math.random()` never reaches 1.0 |
| The one-argument limit | `Predicate`, `Function`, `Consumer` all take exactly one input |
| `Bi` means | **two input arguments** |
| `BiPredicate<T, U>` | 2 type parameters |
| `BiFunction<T, U, R>` | **3** type parameters — two in, one out |
| `BiConsumer<T, U>` | 2 type parameters, returns nothing, **can still mutate** |
| `BiSupplier` | ❌ does not exist — a supplier has no input to double |
| Everything else about `Bi` versions | **identical** — same method names, same default methods |
| `int` where `Double` is expected | ❌ boxing **and** widening cannot both apply — write `500.0` |
