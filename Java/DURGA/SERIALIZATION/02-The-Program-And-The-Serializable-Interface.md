# Serialization and deserialization, as a program

> *"Can you explain serialization and deserialization with a program, with an example? We should be
> in a position to answer."*

Part `01` established the terminology and the four streams. **This is the whole thing as one runnable
file** — and it contains a trap that he says 90% of people fall into.

---

# Building it up

## The class to be serialized

```java
class Dog implements Serializable {
    int i = 10;
    int j = 20;
}
```

**Two instance variables.** And a definition worth being precise about:

> **The state of an object is the values of the instance variables. Only.**

## Creating the object

```java
Dog d1 = new Dog();          // i = 10, j = 20
```

## The three lines that are serialization

```java
FileOutputStream  fos = new FileOutputStream("abc.ser");
ObjectOutputStream oos = new ObjectOutputStream(fos);
oos.writeObject(d1);
```

> **"Can you tell what I did? These three lines are serialization."**

## The three lines that are deserialization

```java
FileInputStream  fis = new FileInputStream("abc.ser");
ObjectInputStream ois = new ObjectInputStream(fis);
Dog d2 = (Dog) ois.readObject();
```

> **"These three lines are deserialization."**

**The cast is required** — `readObject()`'s return type is `Object`, *"but internally which object is
there? Dog object is there. That's why type casting has to be done."*

## The whole file

```java
import java.io.*;

class Dog implements Serializable {
    int i = 10;
    int j = 20;
}

class SerializeDemo {
    public static void main(String[] args) throws Exception {

        Dog d1 = new Dog();

        FileOutputStream  fos = new FileOutputStream("abc.ser");     // ┐
        ObjectOutputStream oos = new ObjectOutputStream(fos);        // ├ serialization
        oos.writeObject(d1);                                         // ┘

        FileInputStream  fis = new FileInputStream("abc.ser");       // ┐
        ObjectInputStream ois = new ObjectInputStream(fis);          // ├ deserialization
        Dog d2 = (Dog) ois.readObject();                             // ┘

        System.out.println(d2.i + " " + d2.j);
    }
}
```

Measured on JDK 25:

```
10 20
```

## The two small things that make it compile

| Addition | Why |
|---|---|
| **`import java.io.*;`** | all four stream classes and `Serializable` live in **`java.io`** |
| **`throws Exception` on `main`** | file I/O throws **`IOException`**, a **checked** exception — *"I'm not interested to handle any exception; if any checked exception comes, my JVM is going to take care"* |

---

# The trap

> *"Can you please tell whether the code is going to compile or not? If I ask this, **out of 100, 90%
> of people are going to tell: sorry, it won't compile** — because you are trying to serialize a Dog
> object, but the Dog class doesn't implement `Serializable`."*

**They are wrong.**

> [!important] **A class that serializes a non-`Serializable` object compiles perfectly.**
> `writeObject(Object)` accepts **any** `Object`. The compiler has no idea whether the runtime type
> will implement `Serializable`, and it does not try to find out.
>
> **The failure is at runtime, not compile time.**

Measured on JDK 25 — compiling with `-Xlint:all` and `Dog` **not** implementing `Serializable`:

```
(exit 0)  — no error, no warning
```

Running it:

```
Exception in thread "main" java.io.NotSerializableException: Dog
```

**Add `implements Serializable` and the same program prints `10 20`.**

| | |
|---|---|
| **Compile time** | ✅ **no problem at all** |
| **Runtime** | ❌ **`NotSerializableException`** |

> **"If the object is not serializable and still you are trying to serialize — there is no problem at
> compile time. Remember this."**

---

# The file

## The extension does not matter

He uses `abc.ser`, and immediately says not to read anything into it:

> **"It's not mandatory to use any extension. You can use `abc.txt`, `abc.dat` also — no problem at
> all, because in Java the file extension is not important."**

Measured on JDK 25 — the same object written to four names:

```
wrote a.ser -> 12 bytes
wrote b.txt -> 12 bytes
wrote c.dat -> 12 bytes
wrote d     -> 12 bytes
```

**Identical.** `.ser` is a convention for humans, nothing more.

## The file does not need to exist first

> *"Whether it is there or not there at the beginning, we are not required to check — this line itself
> is going to create it."*

Measured on JDK 25:

```
brandnew.ser existed before? false
brandnew.ser exists after?   true
```

**`new FileOutputStream(name)` creates the file.** It lands in the **current working directory**.

## And you cannot read it

> *"In which format will the data be there? Binary data. Don't try to read this one — even we can't
> read it also."*

**He is right that it is binary**, though as part `01` showed, a hex dump is readable enough to pick
out the class name, the field names and the values.

---

# The `Serializable` interface

Everything he says about it, confirmed on JDK 25:

| | Measured |
|---|---|
| Package | **`java.io`** |
| Declared methods | **0** |
| Declared fields | **0** |
| Is an interface | **true** |

> **`Serializable` is a marker interface** — an interface with no methods, where **the required
> ability is provided automatically by the JVM.**

> **An object is said to be serializable if and only if the corresponding class implements
> `Serializable`.**

> [!important] **The rule and its consequence, in the two sentences he wants:**
> - **To serialize an object, the corresponding class must implement `Serializable`.**
> - **If it does not, we get a runtime exception saying `NotSerializableException`.**

> [!question]- **Deep dive — what "the JVM provides the ability" actually means, and why it is the
> root of serialization's security problem.** Worth opening once; it explains why this interface with
> no methods is the most criticised feature in the JDK.
>
> **A marker interface carries no code, so the behaviour has to come from somewhere else.** For
> `Serializable`, it comes from `ObjectOutputStream` and `ObjectInputStream`, which use **reflection**
> to walk the object's fields and read or write them directly — bypassing the class's own methods
> entirely.
>
> **On the way back in, deserialization does not call your constructor.** It allocates the object and
> writes the fields in. Every invariant your constructor enforces — a validated email, a non-negative
> balance, a non-null list — **can be violated by a crafted byte stream**, because the code that
> enforces it never runs.
>
> **That is why `implements Serializable` is a far bigger commitment than it looks.** You have created
> a second, invisible, public constructor for the class that accepts arbitrary bytes, and you are
> promising to keep it working in every future version.
>
> **The consequence in practice:** deserializing untrusted data is one of the most reliably exploitable
> classes of vulnerability in Java, because a crafted stream can chain together methods on classes that
> happen to be on the classpath. Java 9 added **`ObjectInputFilter`** as the mitigation — an allowlist
> of classes permitted to be deserialized, settable per-stream or globally with
> `-Djdk.serialFilter=...`. **Since Java 17 the JDK also ships a filter factory**, and the platform's
> own serialized types are increasingly locked down.
>
> **The practical rule:** never deserialize bytes you did not produce yourself, and for anything
> crossing a network boundary use a data format — JSON, protobuf, Avro — rather than Java
> serialization. The lecture's use of it, saving your own object to your own file, is the safe case.

---

# What this part established

| | |
|---|---|
| The state of an object | the values of its **instance variables** |
| Serialization, in code | `FileOutputStream` → `ObjectOutputStream` → **`writeObject(d1)`** |
| Deserialization, in code | `FileInputStream` → `ObjectInputStream` → **`readObject()`** |
| The cast | **required** — `readObject()` returns `Object` |
| Two additions needed | **`import java.io.*;`** and **`throws Exception`** on `main` |
| Serializing a non-`Serializable` object | ✅ **compiles fine** |
| …and at runtime | ❌ **`NotSerializableException`** |
| File extension | **irrelevant** — `.ser` is convention only |
| The file | **created automatically**, in the current working directory |
| File contents | **binary** |
| `Serializable` lives in | **`java.io`** |
| It declares | **no methods** — it is a **marker interface** |
| The ability comes from | **the JVM**, automatically |
| An object is serializable iff | its **class implements `Serializable`** |
| ⚠️ Never | deserialize **untrusted** bytes — deserialization skips your constructor |
