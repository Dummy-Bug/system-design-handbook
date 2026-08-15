# Serializing more than one object

**Everything so far serialized a single `Dog`.** The question now:

> **Is it possible to serialize any number of objects to the file?**

**Yes — with one constraint.**

---

# Writing three objects

```java
Dog d1 = new Dog();
Cat c1 = new Cat();
Rat r1 = new Rat();

FileOutputStream  fos = new FileOutputStream("abc.ser");
ObjectOutputStream oos = new ObjectOutputStream(fos);

oos.writeObject(d1);        // dog serialized first
oos.writeObject(c1);        // then cat
oos.writeObject(r1);        // then rat
```

**One stream, three `writeObject()` calls.** *"Any number of objects we can serialize — no problem at
all."*

---

# The constraint

```java
FileInputStream  fis = new FileInputStream("abc.ser");
ObjectInputStream ois = new ObjectInputStream(fis);

Dog d2 = (Dog) ois.readObject();       // first written, first read
Cat c2 = (Cat) ois.readObject();
Rat r2 = (Rat) ois.readObject();
```

> **In whichever order we serialize, in the same order only we have to deserialize.**

Measured on JDK 25:

```
wrote 3 objects: Dog, Cat, Rat
same order  -> bow meow eek
```

## Getting it wrong

*"By mistake, if I interchange these lines — internally the first `readObject()` gives a dog, but I am
trying to typecast to cat."*

```java
Cat c2 = (Cat) ois.readObject();       // but a Dog comes out first
```

Measured on JDK 25:

```
java.lang.ClassCastException: class Dog4 cannot be cast to class Cat4
```

> [!important] **The order of objects is part of the file format.** Nothing in the stream lets you
> seek to "the cat" — it is a sequence, read front to back. **Interchange the order at deserialization
> time and you get `ClassCastException`.**

> [!info] **Reading past the last object throws `EOFException`.** Measured on JDK 25 — a fourth
> `readObject()` on a three-object file gives **`java.io.EOFException`**. It is not `null` and it is
> not a clean end marker, which matters for the loop below: **the loop has to be bounded, or the
> `EOFException` has to be caught.**

---

# When you don't know the order

> *"Some X person is serializing, some Y person is deserializing. I don't know in which order X person
> serialized. If we don't know the order of objects in serialization, how can we handle it?"*

**Read into an `Object` reference, then ask what it is.**

```java
Object o = ois.readObject();
```

**Why this works:** *"Parent reference can be used to hold a child object."* `Object` will hold a
`Dog`, a `Cat` or a `Rat` equally well.

**But that alone is not enough** — *"by using the parent reference, child-specific methods we can't
call."* So you have to test and cast:

```java
Object o = ois.readObject();

if (o instanceof Dog) {
    Dog d2 = (Dog) o;
    // perform dog-specific functionality
} else if (o instanceof Cat) {
    Cat c2 = (Cat) o;
    // perform cat-specific functionality
} else if (o instanceof Rat) {
    Rat r2 = (Rat) o;
    // perform rat-specific functionality
}
```

> **`instanceof` is the best helper in this scenario.**

> [!warning] **Read once, then test — do not call `readObject()` inside each branch.** He catches
> himself making exactly this mistake mid-derivation: *"a small mistake I am doing — we read already,
> we are not required to read. Just typecast `o`."*
>
> **A second `readObject()` inside the `if` would consume the *next* object**, silently skipping one
> and eventually throwing `EOFException`. The object is already in `o`; only cast it.

## "That's a lot of code for one object"

> *"For one object I have to write this much lengthy code — if a thousand objects are there, then a
> thousand times I have to write it?"*

**No.** *"I will keep this total thing inside a loop — while loop or for loop or for-each loop — so
that for any object the code will become the same. The length of the code is not going to increase."*

Measured on JDK 25, the loop form:

```
unknown order, classic instanceof:
  Dog -> bow
  Cat -> meow
  Rat -> eek
```

## The modern form

> [!important] **Pattern matching removes the cast entirely.** `instanceof` binds the variable
> directly, and a `switch` over the type reads far better than an `if`/`else if` chain:
>
> ```java
> Object o = ois.readObject();
>
> if (o instanceof Dog d) {           // no cast needed
>     d.bark();
> }
> ```
>
> **Or as a switch**, which is the natural shape when there are several types:
>
> ```java
> switch (ois.readObject()) {
>     case Dog d -> d.bark();
>     case Cat c -> c.mew();
>     case Rat r -> r.eek();
>     default    -> { }
> }
> ```
>
> Measured on JDK 25 — identical output to the `if`/`else if` version:
> ```
> unknown order, pattern matching for switch:
>   Dog -> bow
>   Cat -> meow
>   Rat -> eek
> ```
>
> **`instanceof` with a binding variable is standard since Java 16; pattern matching for `switch` since
> Java 21.** The `if (o instanceof Dog) { Dog d = (Dog) o; ... }` shape still works and is what older
> code looks like — but writing the cast out is now redundant, and the `switch` form is checked for
> exhaustiveness, which the `if` chain is not.

---

# What this part established

| | |
|---|---|
| Multiple objects per file | **yes**, any number |
| How | several **`writeObject()`** calls on **one** stream |
| The constraint | **read in the same order you wrote** |
| Wrong order gives | **`ClassCastException`** |
| Past the last object | **`EOFException`** |
| Unknown order — read into | an **`Object`** reference |
| Why that works | a **parent reference can hold a child object** |
| But then | child-specific methods **cannot be called** without a cast |
| The tool | **`instanceof`** |
| ⚠️ Read | **once**, then test — never `readObject()` inside each branch |
| To avoid repetition | put it in a **loop** |
| Modern form | **`o instanceof Dog d`** (16+) and **pattern matching for `switch`** (21+) |
