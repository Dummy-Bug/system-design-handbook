# Hash Index

---

## The Fastest Possible Lookup — O(1)

You have 100 million users. Someone logs in with `alice@gmail.com`. You need to find her instantly.

What if instead of searching at all, you could just compute exactly where she is — in one step, regardless of how many rows exist?

That's a Hash Index. The database runs the email through a hash function, which produces a number. That number maps to a slot in a hash table, and that slot contains a pointer to the actual row.

```
hash("alice@gmail.com") → slot 4521847
slot 4521847            → pointer → actual row on disk
→ found Alice in 1 step ✓
```

No traversal, no searching, no comparisons. Just compute → jump. O(1).

---

## How It's Stored — Two Levels of Indirection

The hash index doesn't map directly to a physical position on disk — rows can move around as the database manages storage. Instead it maps to a **slot in a hash table**, and that slot stores a **pointer** to wherever the row actually lives.

```
Hash table (index):              Actual table (data):
slot 4521847 → ptr ──────────→  [alice@, London, 28, ...]
slot 892341  → ptr ──────────→  [bob@, NYC, 34, ...]
slot 234901  → ptr ──────────→  [charlie@, Paris, 22, ...]
```

When a new user is inserted, the row is written to disk wherever the database puts it — could be position 50,000,001. The hash index stores a pointer to that location:

```
New user alice@ inserted at disk position 50,000,001

hash("alice@gmail.com") → always produces slot 4521847
slot 4521847 → stores pointer → "row is at disk position 50,000,001"
```

The hash of a value always produces the same slot number — that never changes. If the row moves, just update the pointer. The slot stays the same.

```
hash(email) → slot in hash table → pointer → actual row on disk
```

The hash table never stores data — just pointers. Data always lives in the actual table. Same concept as a HashMap in Java or a dict in Python.

---

## The Fatal Limitation — No Range Queries

Hash index sounds perfect — O(1), instant lookups. So why not use it for everything?

Try to find all users whose email starts with "a":

```
hash("alice@gmail.com") → slot 4521847   ✓ exact match works
hash("a*")              → ???            ✗ you can't hash a pattern
```

Hash functions are one-way and unpredictable. `alice@` and `alicez@` produce completely different slot numbers — there's no ordering, no grouping, no relationship between similar values:

```
hash("alice@")  → 4521847
hash("alicez@") → 89234521   ← completely unrelated number
```

Values are scattered randomly across slots. There's no way to say "give me everything between these two hash values" — because there is no between. Hash values have no order.

```
Hash Index:
  ✓ WHERE email = 'alice@gmail.com'   → O(1), instant
  ✗ WHERE email LIKE 'a%'             → impossible
  ✗ WHERE age > 25                    → impossible
  ✗ WHERE date BETWEEN x AND y        → impossible
  ✗ ORDER BY any column               → impossible
```

> [!info] **Hash Index** — runs the column value through a hash function to find a slot in a hash table. That slot stores a pointer to the actual row. O(1) exact lookup. Range queries completely impossible.

> [!important] Hash index is only worth using when you know with certainty you will only ever need exact lookups on that column — never ranges, never LIKE, never ORDER BY. For everything else, you need a different index structure — one that keeps values sorted.

---

## When to Actually Use a Hash Index

The limitation is real — but so is the O(1) speed. The systems where hash indexes shine are the ones where every query is an exact match and range queries simply never happen.

**Session stores / auth tokens**

```sql
WHERE session_token = 'abc123xyz'
```

You always look up a session by exact token. Never "give me all sessions after 3pm." Hash index is perfect — millions of logins per second, O(1) every time. Redis does exactly this.

**User login — email lookup**

```sql
WHERE email = 'alice@gmail.com'
```

Login is always exact match. You never query `WHERE email LIKE 'a%'`. Pure O(1), no range queries ever needed.

**Cache / key-value lookups**

```
GET user:4521847
```

Every cache lookup is exact key → value. This is why Redis is built entirely on hash tables internally — it's a system designed exclusively for exact lookups at speed.

The pattern is the same across all three: you have a key you know exactly, and you just need the value back fast. No filtering, no sorting, no ranges. The moment your query needs anything other than `=`, you're back to B+ Tree.
