# One more pass at the interface static method rule

He opens by asking the class to recall *the loophole* from the previous session, and it is worth having
in both places because it is the most commonly got-wrong rule of the pair.

> **Interface static methods are by default NOT available to the implementation classes. They must be
> called using the interface name only.**

```java
interface Interf {
    public static void m1() { System.out.println("Interface static method"); }
}
```

Whether `Test` implements `Interf` or not makes **no difference at all**:

| Call | Valid? |
|---|---|
| `Interf.m1()` | ✅ the only way |
| `t.m1()` — object reference | ❌ |
| `Test.m1()` — implementation class name | ❌ |
| `m1()` — directly | ❌ |

> *"Whether that class is a normal class or an implementation class — no change in calling a static
> method of an interface."*

---

# Predefined functional interfaces

Now the new topic, and the motivation is practical.

To invoke a lambda expression you need a functional interface. In everyday programming the same few
shapes of small task come up constantly — so rather than making everyone declare their own interface
every time, **Java 8 ships a package of ready-made ones**.

> **`java.util.function`** — the package where all of them live.

The families, in the order he teaches them:

| | |
|---|---|
| **The four core ones** | `Predicate`, `Function`, `Consumer`, `Supplier` |
| **Two-argument versions** | `BiPredicate`, `BiFunction`, `BiConsumer` |
| **Primitive versions** | `IntPredicate`, `IntFunction`, `IntConsumer`, … |

> *"First make sure the first four things are very important — the remaining are copy-paste only."*
> That is a good description: once the four are understood, the rest are the same ideas with the
> argument count or the primitive type changed.

---

# `Predicate`

## Where it comes from — conditional checks

He asks the class to name conditional checks from their own projects, and the examples are his:

- I will give you a number — **is it an even number or not?**
- I will give a string — **is its length 5 or not?**
- **Is an employee's salary greater than 10,000 or not?**
- **Does the employee have a girlfriend or not?** — *"because at the weekend if he wants to go to the
  pub, compulsorily a girlfriend must be required"*

> *"These kinds of conditional checks are very common. If you require a conditional check, always your
> hand goes for `if` / `else`."*

**From 1.8 onwards, those checks can be lambda expressions instead — and the functional interface that
holds them is `Predicate`.**

## The definition

`Predicate` is a functional interface, so it has exactly one abstract method:

```java
interface Predicate<T> {
    public boolean test(T t);
}
```

| | |
|---|---|
| Method | **`test()`** |
| Input type | **anything** — varies example to example |
| Return type | **always `boolean`** |

> [!important] **Why `Predicate` takes only ONE type parameter.** The return type is **always
> `boolean`**, so there is nothing to specify — it never varies. The **input** does vary (`Integer` in
> one example, `String` in the next, `Employee` in the one after), so that is the one thing you must
> state.
>
> **A predicate is a boolean-valued function.**

## Deriving the first one

*Check whether a given integer is even.* Written as an ordinary method first:

```java
public boolean test(Integer i) {
    if (i % 2 == 0) {
        return true;
    } else {
        return false;
    }
}
```

Now convert it to a lambda. Method name gone, return type gone, modifiers gone:

```java
(Integer i) -> {
    if (i % 2 == 0) return true;
    else return false;
}
```

**Then notice something about the condition itself.** `i % 2 == 0` is *already* `true` or `false`:

> *"If I'm giving 10 — what is the answer of this total expression? `10 % 2 == 0` — yes. That's why it
> is going to return `true` only. **We are not required to specify true or false explicitly.**"*

So the whole `if`/`else` collapses:

```java
(Integer i) -> i % 2 == 0
```

And then the usual shortenings — one parameter means the parentheses go, and the type is inferred:

```java
i -> i % 2 == 0
```

## Running it

```java
import java.util.function.*;

Predicate<Integer> p1 = i -> i % 2 == 0;
System.out.println(p1.test(10));
System.out.println(p1.test(15));
```

Measured on JDK 25:

```
true
false
```

> [!important] **The import is required, and it is worth memorising:**
> **`import java.util.function.*;`** — `Predicate` lives there, not in `java.util`.

---

# Why a predicate rather than an `if`

The obvious objection, asked in the session: *`if`/`else` already exists — why bother?*

His answer is about **writing it once and using it everywhere**:

```java
Predicate<Employee> p = e -> e.salary > 10000 && e.hasGirlfriend();
```

Now imagine that condition is not two clauses but **ten or fifteen**. Without a predicate you must
retype all ten conditions at every place they are checked. With one:

```java
p.test(e)
```

> *"How many times do I need to write a predicate? **Only one.** How many times can I use it? **Any
> number of times.** That is the biggest advantage of the predicate concept."*

So the predicate is not a replacement for `if` — it is **a name for a condition**, so the condition
can be passed around, reused, and (as the last section shows) combined.

---

# More predicates

## String length

*Write a predicate to check whether the length of a string is greater than 5.*

Ask the one question that matters: **what type is the input?** `String`. So:

```java
Predicate<String> p = s -> s.length() > 5;
```

## Applied to an array

```java
import java.util.function.*;

String[] s = {"Nag", "Chiranjeevi", "Venkatesh", "Balayya", "Sunny", "Katrina"};

Predicate<String> p = s1 -> s1.length() > 5;
for (String s1 : s) if (p.test(s1)) System.out.println(s1);
```

Measured on JDK 25:

```
Chiranjeevi
Venkatesh
Balayya
Katrina
```

> [!important] **Watch `Sunny` — it is excluded, and that is the teaching point.** `Sunny` has exactly
> **5** characters, and the condition is `> 5`, not `>= 5`. *"Sunny again — only 5 length, but our
> condition is greater than 5."* Off-by-one lives here.

Change the condition and everything else stays:

```java
Predicate<String> p2 = s1 -> s1.length() % 2 == 0;
```

Now it asks *is the length even?* — and with this list nothing is printed, because every name is
3, 11, 9, 7, 5 or 7 characters. *"All the remaining are having odd length."*

> [!info] **On the count of even-length names.** He says one name survives this filter; with the
> spellings above, measured on JDK 25, none do. The exact count depends on how the names are spelled on
> his screen — the point being made (that the same array gives a completely different answer when only
> the condition changes) is unaffected.

## On your own classes

The same as everywhere else in this course: it works on `Employee`, not just `Integer` and `String`.

```java
import java.util.function.*;
import java.util.*;

class Employee {
    String name;
    double salary;
    Employee(String name, double salary) { this.name = name; this.salary = salary; }
}

class EmpPred {
    public static void main(String[] args) {
        ArrayList<Employee> l = new ArrayList<Employee>();
        l.add(new Employee("Durga", 1000));
        l.add(new Employee("Ravi", 2000));
        l.add(new Employee("Shiva", 3000));
        l.add(new Employee("Mahesh", 4000));
        l.add(new Employee("Adarsh", 5000));
        l.add(new Employee("Sagar", 6000));

        Predicate<Employee> p = e -> e.salary > 3000;
        for (Employee e : l) if (p.test(e)) System.out.println(e.name + "  " + e.salary);
    }
}
```

Measured on JDK 25:

```
Mahesh  4000.0
Adarsh  5000.0
Sagar  6000.0
```

`Predicate<Employee>` — the input type is your own class, and nothing else changes.

---

# Predicate joining

The last piece, and the one that makes predicates more than named conditions.

> **Two predicates can be combined into a single predicate.**

Three methods do it, and they are **default methods** on the `Predicate` interface:

| Method | Meaning |
|---|---|
| `p1.and(p2)` | **both** conditions must hold |
| `p1.or(p2)` | **at least one** must hold |
| `p1.negate()` | the **opposite** of `p1` |

> These are *"exactly the same as the logical AND, OR and complement operators"* — and note the
> connection back to the last part: **`and`, `or` and `negate` are default methods**, which is precisely
> the feature that let Java add them to an existing interface.

## The measured example

```java
import java.util.function.*;

class P2 {
    public static void main(String[] args) {
        int[] x = {0, 5, 10, 15, 20, 25, 30};
        Predicate<Integer> p1 = i -> i > 10;
        Predicate<Integer> p2 = i -> i % 2 == 0;

        System.out.println("The Numbers Greater Than 10:");      m1(p1, x);
        System.out.println("The Even Numbers Are:");             m1(p2, x);
        System.out.println("The Numbers Not Greater Than 10:");  m1(p1.negate(), x);
        System.out.println("Greater Than 10 And Even:");         m1(p1.and(p2), x);
        System.out.println("Greater Than 10 OR Even:");          m1(p1.or(p2), x);
    }
    public static void m1(Predicate<Integer> p, int[] x) {
        for (int x1 : x) if (p.test(x1)) System.out.print(x1 + " ");
        System.out.println();
    }
}
```

Measured on JDK 25:

```
The Numbers Greater Than 10:
15 20 25 30 
The Even Numbers Are:
0 10 20 30 
The Numbers Not Greater Than 10:
0 5 10 
Greater Than 10 And Even:
20 30 
Greater Than 10 OR Even:
0 10 15 20 25 30 
```

**Read the last two against each other, which is where the understanding is:**

- **`and`** → `20 30`. Both conditions: over 10 **and** even. `0` and `10` are even but not over 10;
  `15` and `25` are over 10 but not even.
- **`or`** → `0 10 15 20 25 30`. **`5` is the only number missing** — it is neither over 10 nor even.
  Everything else satisfies at least one.

> *"If both conditions fail, then only we should not consider. At least one condition satisfied, then
> happily we can consider."*

And `negate()` on *greater than 10* gives `0 5 10` — the complement, exactly as expected.

> [!important] **Why joining is the real payoff.** *"Multiple predicates we can combine together to
> check very complex conditional expressions."* One predicate names a condition; joined predicates let
> you build a complicated condition out of simple named parts, and pass the whole thing around as one
> object.

---

# The bridge to the next part

Everything above returns `boolean`. But sometimes the requirement is different:

> *"I will give input, perform some operation, and produce some result — and **the result need not be
> boolean type.** It can be `int`, it can be `String`, it can be a `Student`, a `Customer`, anything."*

- give an `int`, get back `i * i`
- give a `String`, get back its length
- give a `String`, get back `s + s`

> **For that, we should go for `Function`** — which is where the next part starts.

---

# What this part established

| | |
|---|---|
| Interface static methods | callable **only** through the interface name, implementer or not |
| Where the predefined interfaces live | **`java.util.function`** |
| The four core ones | `Predicate`, `Function`, `Consumer`, `Supplier` |
| Why they exist | so common small tasks have a ready-made functional interface for their lambdas |
| `Predicate<T>` | method **`test()`**, one type parameter, returns **`boolean`** |
| Why one type parameter | the return type is always boolean — only the input varies |
| `i % 2 == 0` | already boolean — no `if`/`else`, no explicit `true`/`false` |
| Why not just `if` | write the condition **once**, use it **any number of times** |
| Works on | `Integer`, `String`, and **your own classes** |
| `> 5` vs `>= 5` | `Sunny` at exactly 5 is excluded — the off-by-one is the point |
| `p1.and(p2)` | both — `20 30` |
| `p1.or(p2)` | at least one — everything except `5` |
| `p1.negate()` | the complement — `0 5 10` |
| What `and`/`or`/`negate` are | **default methods** — the previous part's feature, in production |
| When boolean is not enough | go for **`Function`** |
