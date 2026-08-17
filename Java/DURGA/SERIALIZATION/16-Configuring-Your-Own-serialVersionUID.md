# Reproducing the problem

**Same person, same machine, same JVM.** The only thing that changes is the `.class` file — and that is enough.

```java
public class Dog implements Serializable {
    public int i = 10;
    public int j = 20;
}
```

**Three files:** `Dog.java`, `Sender.java` which creates and serializes a `Dog`, and `Receiver.java` which deserializes and prints.

## First, the happy case

```
java Sender      -> serialization completed
java Receiver    -> 888 999
```

> If there is no change in JVM version and no change in class file version, no problem at all — because the unique IDs are the same.

## Then modify the class after serializing

**Serialize first. Then add one field and recompile:**

```java
public class Dog implements Serializable {
    public int i = 10;
    public int j = 20;
    public int k = 30;          // added AFTER the file was written
}
```

```
javac Dog.java
java Receiver
```

Measured on JDK 25:

```
java.io.InvalidClassException: Dog; local class incompatible:
   stream classdesc serialVersionUID = -4370522500503404182,
   local class serialVersionUID    = -1320636198254596889
```

> **Just because of a class file change, deserialization fails.** The receiver has the updated class file, but the file contains an object from the old class file. Even though we are using the same JVM version, different `serialVersionUID`s will be generated.

---

# The fix

> Who is responsible to generate the `serialVersionUID`? The sender and receiver JVM. **Don't give the chance to the bloody JVM** to generate it — configure our own.

**One line, in the serializable class:**

```java
private static final long serialVersionUID = 1L;
```

| Part | Why |
|---|---|
| `private static final long` | the exact modifiers the JVM looks for |
| `serialVersionUID` | compulsorily the name should be like this |
| `1L` | **any long value** — 1L, 2L, 3L, any number you can keep |

**Once this field is present the JVM does not compute anything.** It uses your value, on both sides.

## It working

**Serialize with the one-field version, then add two fields, recompile, and read:**

```java
public class Dog implements Serializable {
    private static final long serialVersionUID = 1L;      // unchanged
    public int i = 10;
    public int j = 20;
    public int k = 30;                                    // added
    public String m = "hello";                            // added
}
```

Measured on JDK 25:

```
=== sender, v1:
wrote, UID = 1

=== receiver with v2 (two fields ADDED, same explicit UID):
local UID = 1
deserialized: i=888 j=999  k=0  m=null
```

> **Deserialization succeeds** — even though you added new properties, no problem at all, because you are not giving the chance to the JVM to generate.

> [!important] **Look at what the new fields hold: `k=0` and `m=null`, not `30` and `"hello"`.** The stream has no values for them, so they get the **type defaults** — **not their initialisers**, because deserialization does not run field initialisers for the serializable class (part `02`). **New fields added to an existing class always arrive empty on old data**, and code reading them must expect that.

## The recommendation

> **Wherever `implements Serializable` is there — in that class, highly recommended to write our own `serialVersionUID`.**

---

# What the tooling does about it

> If you are working on IDEs — Eclipse and so on — sometimes the IDE prompts the programmer to enter `serialVersionUID`, because the IDE is aware of this problem. And some intelligent IDEs will generate it automatically instead of giving the chance to the JVM.

**Three tools do this for you, and all three are worth knowing:**

## 1. The compiler will warn you

Measured on JDK 25:

```
javac -Xlint:serial Dog.java

warning: [serial] serializable class Dog has no definition of serialVersionUID
```

**Turn `-Xlint:serial` on in your build** and every class that forgot it is listed.

## 2. `@Serial` marks the field

```java
@Serial
private static final long serialVersionUID = 1L;
```

**Same annotation as the callbacks in part `07`** (Java 14+). It tells the compiler this field is meant to be the magic one, so a misspelling — `serialVersionUid`, `SerialVersionUID` — is caught instead of silently ignored.

## 3. `serialver` computes the existing value

**The one case where you must not just pick `1L`:** a class that has **already** been serialized somewhere, whose existing data you need to keep reading. You need the value the JVM was computing.

Measured on JDK 25:

```
$ serialver -classpath . Dog
Dog:    private static final long serialVersionUID = -4370522500503404182L;
```

**It prints the whole declaration, ready to paste.** Add that line and every previously written file stays readable.

---

# What the UID does and does not promise

> [!question]- **Deep dive — a matching UID means I promise these are compatible, not these are compatible.** Worth opening: fixing the UID moves the responsibility onto you, and the failure mode changes from an exception to wrong data.
>
> **The generated UID was a safety check.** Pinning it to `1L` switches the check off and makes **you** the one asserting the two versions are compatible.
>
> **Changes that stay compatible** — old data still reads correctly:
>
> | Change | Effect on old data |
> |---|---|
> | **adding** a field | arrives as **`0` / `null`** |
> | **removing** a field | the value in the stream is **ignored** |
> | adding or changing **methods** | no effect — methods are not serialized |
> | adding an **interface** | no effect |
>
> **Changes that are not compatible, and where the exception no longer protects you:**
>
> | Change | What happens |
> |---|---|
> | changing a field's **type** | **`InvalidClassException`** — the field descriptors still have to match |
> | changing `static` ↔ instance, or adding `transient` | behaves like **deleting** the field — silently `0` / `null` |
> | changing the **class hierarchy** | undefined; usually fails |
> | changing the **meaning** of a field | **nothing is detected** — you get plausible, wrong data |
>
> **The last row is the real risk.** Repurpose `int status` from `0 = active` to `0 = deleted` and every old record is silently reinterpreted. **The UID cannot see that**, and with it pinned, nothing else will either.
>
> **So the practical rule:** pin the UID, keep old fields around rather than deleting them, only ever **add**, and write a test that deserializes a checked-in file produced by the previous version.

---

# The chapter ends here

> With this, the total serialization concept got completed.

> [!info] **His closing advice, which is about where the leverage is.** This is one area where, compared with the remaining, you people can show the difference — especially externalization. Most people don't know about this concept. `serialVersionUID` — most people don't know. Can you explain the difference between serialization and deserialization — most people don't know.
>
> **The claim is that this chapter is underlearned relative to how often it is asked**, which matches why part `15` exists at all: he ignored `serialVersionUID` for nine years until a student was asked about it in an interview.

---

# What this part established

| | |
|---|---|
| Reproducing the bug | serialize, **add a field**, recompile, deserialize |
| Result | **`InvalidClassException`**, both UIDs printed |
| The fix | **`private static final long serialVersionUID = 1L;`** |
| The name | must be **exactly** `serialVersionUID` |
| The value | **any** long |
| Effect | the JVM **stops computing** and uses yours |
| With it, adding fields | ✅ **deserialization succeeds** |
| The added fields hold | **`0` / `null`** — not their initialisers |
| The recommendation | put it in **every** `Serializable` class |
| The compiler flag | **`-Xlint:serial`** warns when it is missing |
| The annotation | **`@Serial`** catches a misspelled name |
| For an **existing** class | use **`serialver`** to recover the computed value |
| ⚠️ A matching UID means | I promise these are compatible — the check is now **yours** |
| Compatible changes | **add** a field, **remove** a field, change methods |
| Incompatible | changing a field's **type** |
| Undetectable | changing a field's **meaning** |
