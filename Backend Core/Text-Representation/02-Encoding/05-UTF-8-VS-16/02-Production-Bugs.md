## Bug Class 1 — “Length” Means Different Things ❗

There are **three different lengths** engineers confuse:

| Length Type | What it measures | Where it applies |
|------------|------------------|------------------|
| Byte length | Number of bytes | Network, files, DB |
| Code unit length | UTF-16 units | Runtime internals |
| Character count | User-visible characters | Validation, UI |

### Example
Text: "😂"


- UTF-8 byte length: 4
- UTF-16 code units: 2
- Characters: 1

If your code assumes these are the same → bugs.

---

## Bug Class 2 — Validation Errors (Max Length Rules)

### Typical Bug
> “Username max length = 10 characters”

Implementation mistake:
- Counting UTF-16 code units
- Or counting UTF-8 bytes

Result:
- Emojis break limits
- Users get rejected unexpectedly
- Or invalid data passes validation

### Rule
> **Validation rules must explicitly state what “length” means.**

If the rule is user-facing:
- Count **characters**, not bytes or code units.

---

## Bug Class 3 — Truncation Corruption ✂️

### Typical Bug
- Truncating strings by index or byte length
- Cutting in the middle of:
  - UTF-8 multi-byte sequence
  - UTF-16 surrogate pair

Result:
- Invalid text
- Replacement characters (�)
- Downstream decoding failures

### Rule
> **Never truncate raw bytes or code units blindly.**
> Truncate at **character boundaries**.

---

## Bug Class 4 — Byte Length Used For Character Limits 🚫

### Typical Bug
- Database column defined as “VARCHAR(255)”
- Code assumes “255 characters”

Reality:
- DB limit is often **bytes**
- UTF-8 characters may use more than 1 byte

Result:
- Insert failures
- Silent truncation
- Data loss

### Rule
> **Know whether your storage limits bytes or characters.**
> Do not assume they are the same.

---

## Bug Class 5 — Missing or Wrong Charset Declarations 🌐

### Typical Bug
- API returns text
- Charset not specified (or wrong)
- Client decodes with different encoding

Result:
- Garbled text
- � replacement characters
- Hard-to-reproduce issues

### Rule
> **Always declare charset explicitly at boundaries.**
> Defaults are dangerous.

---

## Bug Class 6 — Assuming ASCII Forever 🧨

### Typical Bug
- Code assumes:1 character = 1 byte

- Works for years
- Breaks the moment emojis or non-English text appear

### Rule
> **ASCII is a subset, not the world.**
> Design for Unicode from day one.

---

## Production Rules Of Thumb (Memorize These) ✅

1. **Transport (HTTP, APIs, JSON)** → UTF-8  
2. **Storage (DB, files, logs)** → UTF-8  
3. **Runtime (string processing)** → depends on language  
4. **Never assume “length” means characters**  
5. **Emojis are the test case for bad assumptions**  
6. **Encoding bugs happen at boundaries, not in business logic**

---

## Debugging Checklist 🛠️

When text looks broken in production, ask:

1. What encoding was used to **send** the data?
2. What encoding was assumed to **receive** it?
3. Are we counting bytes, code units, or characters?
4. Did we truncate or slice text?
5. Is charset explicitly declared?

Answering these usually finds the bug.

---

## Interview-Ready Summary (SDE-3)

If asked:

> What are common UTF-8 / UTF-16 bugs in production?

Answer:

> Most bugs come from confusing byte length, code unit length, and character count. 
> UTF-8 is ideal for transport and storage, UTF-16 is used internally by runtimes. 
> Problems appear at boundaries—validation, truncation, and missing charset declarations.
