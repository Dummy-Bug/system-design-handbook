# What a wrapper is

Start with the everyday word, not the Java one.

> What is a wrapper? It's a cover — something like a chocolate cover. A Dairy Milk is a piece of chocolate inside a neat wrapper, and the wrapper is what lets you put it on the market.

**The same idea, in Java:** you have a **primitive**, and you need to present it to the world **as an object**. Something must wrap it — and that something is a **wrapper class**.

---

# The two purposes

## 1. To wrap a primitive into object form

> **To wrap a primitive into object form, so that we can handle primitives also just like objects.**

The classic demonstration — up to Java 1.4:

```java
ArrayList l = new ArrayList();
l.add(10);            // ❌ compile error in 1.4
```

> **Collections can hold only objects, not primitives.**

So you wrap it first:

```java
Integer i = new Integer(10);
l.add(i);             // ✅
```

> [!info] **Why this matters at all.** Java is an object-oriented language — most of the time we have to talk in terms of objects only. Without wrapper classes, primitives could never participate: primitives would always be primitives only, they can't have object capability.

## 2. To define utility methods for primitives

A `Student` object needs methods — `getName()`, `getMarks()` — and they live in the `Student` class.

**But a primitive `10` needs methods too.** Converting it to a `String`, parsing one, finding the maximum value — where would those live? A primitive has no class of its own.

> **The wrapper class provides the home for the utility methods required by primitives.**

```java
Integer.toString(10);      // primitive → String
```

> **The main objectives of wrapper classes:**
> **1. to wrap a primitive into object form, so we can handle primitives just like objects** **2. to define several utility methods required for primitives**

---

# The eight wrapper classes

| Primitive | Wrapper |
|---|---|
| `byte` | `Byte` |
| `short` | `Short` |
| `int` | **`Integer`** |
| `long` | `Long` |
| `float` | `Float` |
| `double` | `Double` |
| `char` | **`Character`** |
| `boolean` | `Boolean` |

**Eight primitives, eight wrappers.** Note the two whose names are not just capitalised — `int` → `Integer` and `char` → `Character`.

---

# Constructors

> **ALMOST ALL wrapper classes contain two constructors:** one taking the **corresponding primitive**, the other taking a **`String`**.

```java
Integer i1 = new Integer(10);      // primitive
Integer i2 = new Integer("10");    // String
```

**Both are deprecated — you write `Integer.valueOf(...)` instead.** The constructors are still worth knowing because the question how many constructors does each wrapper have? is asked directly, and because the reason they were retired is itself the interesting part.

> [!important] **He stresses the word `almost`.** Have you observed — I'm not using the word **all**. **Almost all.** That caution is exactly right. Measured on JDK 25:
>
> | Wrapper | Public constructors |
> |---|---|
> | `Byte`, `Short`, `Integer`, `Long`, `Double`, `Boolean` | **2** |
> | **`Character`** | **1** — `Character(char)` only |
> | **`Float`** | **3** — `Float(float)`, `Float(double)`, `Float(String)` |
>
> **`Character` is the exception**, and the reason is that there is no sensible `String` form for a single character that is not already a `char`. **`Float` has an extra one** so a `double` literal can be narrowed directly.

> [!warning] **Never call a wrapper constructor.** Compiling one gives:
> ```
> warning: [deprecation] Integer(int) in Integer has been deprecated
> ```
> The replacement is the static factory:
> ```java
> Integer i = Integer.valueOf(10);      // instead of new Integer(10)
> ```
> **Why the factory wins, and it is the reason the constructors were retired:** `valueOf()` may return a **cached** object for small values — `Integer` caches −128 to 127 — while `new` is contractually obliged to create a fresh object every single time. The factory is faster and uses less memory.
>
> **In practice you write neither**, because autoboxing (note `10`) does it for you:
> ```java
> ArrayList<Integer> l = new ArrayList<>();
> l.add(20);                            // boxes automatically
> ```
> Measured on JDK 25: `[10, 20]`.

---

# What this part established

| | |
|---|---|
| A wrapper is | a **cover** — a primitive presented as an object |
| Purpose 1 | wrap a primitive into **object form** |
| Why needed | **collections hold only objects**, not primitives |
| Purpose 2 | provide a home for **utility methods** operating on primitives |
| How many wrapper classes | **eight**, one per primitive |
| The two irregular names | `int` → **`Integer`**, `char` → **`Character`** |
| Constructors | **almost all** have two — primitive and `String` |
| `Character` | **one** — no `String` constructor |
| `Float` | **three** — `float`, `double`, `String` |
| ⚠️ All constructors | **deprecated since Java 9** |
| Use instead | **`valueOf()`** — may return a **cached** object |
| In practice | **autoboxing** does it for you |
