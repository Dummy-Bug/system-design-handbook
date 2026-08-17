# All the differences

> Can you please list out all differences between serialization and externalization? Very important question for the interview room. Compulsorily we should be in a position to give left and right to that interview person.

**Eight differences, in his order.** Everything here was demonstrated in parts `12` and `13`; this is the consolidated answer.

---

# The table

| # | | **Serialization** | **Externalization** |
|---|---|---|---|
| **1** | Meant for | **default** serialization | **customized** serialization |
| **2** | Control | everything by the **JVM** — the programmer has **no control** | everything by the **programmer** — the **JVM** has no control |
| **3** | What is saved | always the **total object**; **not possible** to save part of it | **total object or part of it**, based on our requirement |
| **4** | Performance | relatively **low** | relatively **high** |
| **5** | The interface | **`Serializable`** — **no methods**, a **marker interface** | **`Externalizable`** — **two methods**, **not** a marker interface |
| **6** | Best choice when | you want to save the **total object** | you want to save **part of the object** |
| **7** | Public no-arg constructor | **not required** | **compulsory** — else **`InvalidClassException`** |
| **8** | `transient` | **plays a role** | **plays no role**, and is not required |

---

# The reasoning behind each

**Memorising the table is not the point — each row has a one-sentence justification, and that is what survives a follow-up question.**

## 1 and 2 — default versus customized

**Serialization is the default machinery.** You write `implements Serializable` and the JVM does everything. **Externalization is you doing it**, via `writeExternal` and `readExternal`.

> [!info] **Careful with the word `customized` here.** It does **not** mean the customized serialization of parts `06`–`09` — that was `Serializable` plus two private callbacks, and the JVM still did the default work when asked. **Externalization is customized in a stronger sense: there is no default work at all.**

## 3 and 4 — the whole object, and what it costs

**Row 4 is a consequence of row 3, not an independent fact.**

> If you want one or two properties, total object will be saved — that's why relatively performance is low.

**With externalization you write what you need.** One property means one property's worth of bytes and time — the 2 minutes versus 2,000 minutes from part `12`.

## 5 — marker versus two methods

> `Serializable` doesn't contain any methods because the required ability is provided by the JVM. In externalization the required ability should be provided by the programmer only — that's why it contains two methods.

**The method count follows from who does the work.** Same fact as rows 1–2, expressed in the type system.

## 6 — which to reach for

**A restatement of row 3 as advice.** Total object → serialization. Part of the object → externalization.

## 7 — the constructor

**This is the one with the most interesting reason**, and part `13` proved it by watching the constructor print or not print:

| | Why |
|---|---|
| `Serializable` | the file **already contains the total object**, so at deserialization you get the object out of the file — **nothing needs constructing** |
| `Externalizable` | the file contains **one or two properties**, not an object — so the JVM must **create a new object** by calling the **public no-arg constructor**, then call `readExternal` on it |

**Without it: `InvalidClassException`.**

## 8 — `transient`

> In serialization, who is responsible to save the data? The JVM. So I have to convey to the JVM: don't save the value of the password, it is sensitive data — instead of the original value, please save the default value. **How do we convey that? By declaring the variable `transient`.**
>
> But in externalization, who is responsible to save the data? The programmer. **If you don't want to save the value of a particular variable, don't save it.** What is the need of the `transient` keyword?

**`transient` is a message to the JVM. In externalization there is nobody to send it to.** Part `13` measured it: every field marked `transient` changed nothing.

---

# Where they overlap

> [!important] **`Externalizable` extends `Serializable`,** so an `Externalizable` object is also a `Serializable` object — it passes `instanceof Serializable`, and `ObjectOutputStream` accepts it for the same reason it accepts any other. **The two are not alternatives at the type level; one is a specialisation of the other.**
>
> What differs is which path `ObjectOutputStream` takes once it has the object: **if the class implements `Externalizable`, your two methods are used and the default field-walking machinery is skipped entirely.**

---

# Choosing between them today

> [!important] **In current Java the honest answer to which should I use is usually neither.** Both write a Java-specific binary format that only Java can read, both are tied to your class shape, and both carry the deserialization risks from part `02`. **For anything crossing a process boundary, a data format — JSON, protobuf, Avro — is the default choice**, and it is what an interviewer asking this expects you to know.
>
> **Where `Externalizable` still earns its place** is a large object graph inside one system where the serialized size or speed genuinely matters and you control both ends. **Even then, the modern alternative is usually a `record` plus an explicit serializer**, which gives you the same control without the constructor rules, the `InvalidClassException`, or the version-compatibility problem that part `15` is about.

---

# What this part established

| | |
|---|---|
| Difference 1 | **default** vs **customized** serialization |
| Difference 2 | **JVM** in control vs **programmer** in control |
| Difference 3 | **total object only** vs **total or part** |
| Difference 4 | performance **low** vs **high** |
| Difference 5 | **marker interface** vs **two methods** |
| Difference 6 | best for the **whole object** vs **part of it** |
| Difference 7 | constructor **not required** vs **public no-arg mandatory** |
| Difference 8 | `transient` **works** vs **no effect** |
| Row 4 follows from | row 3 |
| Row 5 follows from | rows 1–2 |
| Row 7's reason | the file holds **an object** vs **just some values** |
| Row 8's reason | `transient` is **a message to the JVM** |
| At the type level | **`Externalizable` extends `Serializable`** |
