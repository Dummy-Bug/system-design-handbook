UTF-16 is:

> A Unicode encoding that represents characters using **16-bit code units**,
> where most characters use **one code unit** and some use **two code units**.

Key terms to keep in mind:

- Unicode → character identity
- UTF-16 → representation strategy
- Code unit → the basic storage unit (16 bits)

---

## The Basic Building Block: Code Units 🧱

UTF-16 does **not** work in bytes as its primary unit.

Instead, it works in:

> **16-bit units (2 bytes each)**

These units are called **code units**.

A UTF-16 text is therefore a sequence of 16-bit values.

---

## How Characters Are Represented (High-Level)

Conceptually, UTF-16 follows this model:

- Most common characters → **1 code unit**
- Some characters → **2 code units together**

So UTF-16 is:

> Mostly fixed-width, but not completely.

This “mostly” is important and will be explored later.

---

## Examples (Conceptual Only)

| Character | UTF-16 Code Units |
|----------|-------------------|
| `A` | 1 |
| `ह` | 1 |
| `你` | 1 |
| `😂` | 2 |

At this stage, do **not** worry about *how* the two units work.
Only note **that they exist**.

---

## What UTF-16 Optimizes For ⚙️

UTF-16 is designed to optimize for:

- In-memory text processing
- Faster indexing compared to byte-based encodings
- Predictable performance for most scripts
- Language runtime implementations

This makes UTF-16 a good fit for **programming language internals**.

---

## What UTF-16 Is NOT Optimized For 🚫

UTF-16 is not designed for:

- Compact network transmission
- ASCII-heavy payload efficiency
- Backward compatibility with ASCII byte streams

Those are goals better served by other encodings.

---

## Important Clarification ❗

UTF-16 is **not**:

- A compression format
- A transport encoding
- A storage recommendation for APIs

It is simply:

> One way to represent Unicode characters, optimized for a specific set of constraints.

---

## Mental Model To Lock In 🪜

> UTF-16 represents text as a sequence of 16-bit units.
> Most characters use one unit; some require two.

---

