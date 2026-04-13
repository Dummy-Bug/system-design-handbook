
> [!info] The core idea
> Every edit in a text document is either an Insert or a Delete. When two concurrent inserts arrive at the server, you cannot apply the second one as-is — the first insert already shifted positions. You must transform the second operation based on what already happened. This is Operational Transformation.

---

## The only two operations in a text document

Every edit you make in Google Docs is one of two operations:

- **Insert** — add a character at a position
- **Delete** — remove a character at a position

Even pasting a paragraph is just a series of inserts. Even selecting and replacing text is a delete followed by an insert. Everything reduces to these two.

---

## The problem — concurrent inserts

Two users are looking at the same document:

```
"Hello"
```

User 1 inserts "X" at position 0 (the very beginning). At the exact same time, User 2 inserts "Y" at position 0.

```
User 1: Insert("X", position=0)
User 2: Insert("Y", position=0)  ← concurrent, neither knows about the other
```

Both operations reach the server. The server processes User 1 first:

```
"Hello" → Insert("X", position=0) → "XHello"
```

Now User 2's operation arrives — "insert Y at position 0." If the server applies it as-is:

```
"XHello" → Insert("Y", position=0) → "YXHello"
```

But User 2's screen still shows "YHello" — not "YXHello". The two clients are now showing different documents. Split brain.

---

## The fix — transform before applying

The server cannot apply User 2's operation as-is. It must **transform** it based on what already happened.

User 1 already inserted X at position 0 — everything in the document shifted right by 1. So User 2's "insert Y at position 0" needs to become "insert Y at position 1":

```
Original operation:   Insert("Y", position=0)
Transformed:          Insert("Y", position=1)  ← shift right by 1 because of User 1's insert
```

Server applies the transformed operation:

```
"XHello" → Insert("Y", position=1) → "XYHello"
```

Both clients now converge to **"XYHello"**. No data lost. Both X and Y are present.

---

## What if the server processed User 2 first?

```
"Hello" → Insert("Y", position=0) → "YHello"
User 1's operation transformed → Insert("X", position=1)
"YHello" → Insert("X", position=1) → "YXHello"
```

Result is "YXHello" instead of "XYHello" — the order of the two characters flips depending on who the server processed first. Both are valid. The guarantee OT provides is not a specific order — it is that **both clients converge to the same document** with no data lost.

---

## The transformation rule for concurrent inserts

When two inserts happen concurrently at the same or overlapping positions:

```
If Insert A is applied first at position P:
→ Any concurrent Insert B at position >= P must shift right by 1
→ Any concurrent Insert B at position < P stays unchanged
```

The server is the arbiter — it picks an order and transforms all concurrent operations accordingly. Every client ends up with the same document.
