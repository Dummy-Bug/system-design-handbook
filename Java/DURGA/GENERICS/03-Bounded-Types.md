# Why a type parameter sometimes needs a boundary

So far the type parameter has been wide open — `Test<T>` accepts anything. Sometimes that is too generous, and here is the case that shows it.

```java
class Test<T> {
    public void m1() {
        T a, b;
        System.out.println(a + b);
        System.out.println(a * b);
        System.out.println(a / b);
    }
}
```

Those are **arithmetic operations**, and arithmetic makes sense only for numbers.

- If `a` and `b` are `String`, then `a + b` is fine — concatenation. But `a * b`? `a / b`? **Meaningless.**
- If `a` and `b` are `Student`, then **first student plus second student** is meaningless from the start.

> If the functionality is applicable only for a particular range, then we have to **bound the type parameter** to that range.

The fix is one keyword:

```java
class Test<T extends Number> {}
```

Now the type parameter accepts `Number` or any of its children — `Byte`, `Short`, `Integer`, `Long`, `Float`, `Double` — and nothing else.

> We can bound the type parameter for a particular range by using the **`extends`** keyword. Such types are called **bounded types**.

---

# Bounded versus unbounded

```java
class Test<T> {}                     // unbounded

Test<Integer> t1 = new Test<Integer>();   // ✅
Test<String>  t2 = new Test<String>();    // ✅
```

Anything is accepted, no restrictions — **unbounded**.

```java
class Test<T extends Number> {}      // bounded

Test<Integer> t1 = new Test<Integer>();   // ✅  Integer is a child of Number
Test<String>  t2 = new Test<String>();    // ✗
```

Measured on JDK 25:

```
error: type argument String is not within bounds of type-variable T
```

---

# The syntax, stated generally

```java
class Test<T extends X> {}
```

**`X` can be either a class or an interface**, and that changes what is accepted:

| If `X` is a… | The type parameter accepts |
|---|---|
| **class** | `X` type, or its **child classes** |
| **interface** | `X` type, or its **implementation classes** |

Measured on JDK 25 for the interface case:

```java
class Test<T extends Runnable> {}

Test<Thread>  t1 = new Test<Thread>();    // ✅  Thread implements Runnable
Test<Integer> t2 = new Test<Integer>();   // ✗
```

```
error: type argument Integer is not within bounds of type-variable T
```

> [!important] **`extends` is doing double duty, and that is the point.** In ordinary Java you `extends` a class and `implements` an interface. In generics bounds there is **only `extends`**, and it covers both. See the next section for why.

---

# Conclusion 1 — only `extends`, never `implements` or `super`

Four declarations, and only two are legal:

| Declaration | Valid? |
|---|---|
| `class Test<T extends Number> {}` | ✅ |
| `class Test<T implements Runnable> {}` | ❌ |
| `class Test<T extends Runnable> {}` | ✅ |
| `class Test<T super String> {}` | ❌ |

Measured on JDK 25 — both invalid forms fail at the parser, before any type checking:

```
class Test<T implements Runnable>{}    error: > expected
class Test<T super String>{}           error: > expected
```

> We can define bounded types **only by using the `extends` keyword**. We cannot use `implements` and `super`. But the **purpose** of `implements` can be achieved with `extends`.

So wherever you would want `implements`, write `extends` instead and it works — that is why `T extends Runnable` is legal even though `Runnable` is an interface.

> [!important] **Remember the `super` result — it is about to become half-true.** `super` is banned **here**, at class level, with a named type parameter `T`. It is **allowed** at method level with the wildcard `?`, which is the subject of note `04`. Many people carry super is not allowed in generics as a flat rule and get caught by the wildcard form.

---

# Combination bounds

A bound need not be a single type. Suppose the requirement is: the type parameter must be **a child of `Number`** **and** **implement `Runnable`** — both at once.

```java
class Test<T extends Number & Runnable> {}
```

The separator is **`&`**, not a comma.

All six cases, measured on JDK 25:

| Declaration | Result |
|---|---|
| `class Test<T extends Number & Runnable> {}` | ✅ valid |
| `class Test<T extends Number & Runnable & Comparable> {}` | ✅ valid |
| `class Test<T extends Runnable & Comparable> {}` | ✅ valid |
| `class Test<T extends Number & String> {}` | ❌ `interface expected here` |
| `class Test<T extends Runnable & Number> {}` | ❌ `interface expected here` |
| `class Test<T extends Number & Thread> {}` | ❌ `interface expected here` |

Two rules generate every row, and both come straight from ordinary Java:

> [!important] **Rule 1 — the class comes first, interfaces after.**
> `Runnable & Number` fails because `Number` is a class and it is written second. This mirrors normal syntax: `class A extends B implements C` is valid, `class A implements B extends C` is not. First the class, then the interfaces.
>
> **Rule 2 — at most one class.**
> `Number & String` and `Number & Thread` both fail because both names are classes. Java does not support multiple inheritance of classes — `class A extends B, C` is invalid — and the same rule applies to a bound.

So a type parameter may extend **one class and any number of interfaces**, in that order. All three failures report the same message, `interface expected here`, because the compiler reached a position where only an interface is permitted and found a class.

---

# Conclusion 2 — `T` is only a convention

```java
class Test<T> {}      // ✅
class Test<X> {}      // ✅
class Test<A> {}      // ✅
class Test<Durga> {}  // ✅
```

> As the type parameter we can use **any valid Java identifier**, but it is a **convention** to use `T`.

`T` is simply the first letter of **type parameter**. Nothing enforces it.

> [!info] **The conventional letters are worth knowing**, since the JDK uses them consistently: **`T`** for type, **`E`** for element (used across collections), **`K`** and **`V`** for key and value, **`N`** for number. Following them makes an unfamiliar generic signature readable at a glance.

---

# Conclusion 3 — any number of type parameters

Nothing restricts you to one.

```java
class Test<A, B> {}       // two
class Test<X, Y, Z> {}    // three
```

> Based on our requirement we can declare **any number of type parameters**, and they should be separated by **commas**.

The example that is not invented — it is already in the Java API:

```java
class HashMap<K, V> { … }

HashMap<Integer, String> h = new HashMap<Integer, String>();
```

A map is a group of **key–value pairs**, so it needs two: **`K`** for the key type and **`V`** for the value type. Here the keys are `Integer` and the values are `String`.

> [!info] **Note the separator difference, because they appear close together.** Multiple **type parameters** are separated by **commas** — `<K, V>`. Multiple **bounds on one** parameter are separated by **`&`** — `<T extends Number & Runnable>`. A comma introduces another parameter; an ampersand adds another constraint to the same one.

---

# What this part established

| | |
|---|---|
| Why bounds exist | some functionality is valid only for a **particular range** of types |
| Declared with | **`extends`** — `class Test<T extends Number> {}` |
| Such types are called | **bounded types** |
| `T extends X` where `X` is a **class** | accepts `X` or its **child classes** |
| `T extends X` where `X` is an **interface** | accepts `X` or its **implementation classes** |
| `implements` in a bound | ❌ **never** — use `extends` instead |
| `super` in a bound at **class** level | ❌ **not allowed** (but see note `04` for `?`) |
| Combination bounds | joined with **`&`** |
| Ordering rule | **class first**, then interfaces |
| Class count rule | **at most one class** |
| The identifier `T` | a **convention**, not a requirement |
| Number of type parameters | **any**, separated by **commas** |
