
> [!info] The core idea
> When a concurrent delete happens before your insert arrives at the server, positions shift left. If you apply the insert at the original position, it lands in the wrong place. The server must transform the insert position by accounting for the delete before applying it.

---

## The happy case — no concurrency

Same document:

```
"Hello"
```

User 1 deletes character at position 2 — that's the first "l":

```
Delete(position=2) → "Helo"
```

User 2 is not editing at the same time. Their operation arrives after User 1's delete is already applied. Server just applies it directly. No transformation needed.

---

## The concurrent case — delete and insert at the same time

Same document:

```
H e l l o
0 1 2 3 4
```

User 1 deletes "H" at position 0. At the exact same time, User 2 inserts "X" at position 2 — intending to place X between "e" and the first "l":

```
User 1: Delete(position=0)       → concurrent
User 2: Insert("X", position=2)  → concurrent
```

User 2's intention was clear — X goes between "e" and "l":

```
"Hello" → Insert("X", position=2) → "HeXllo"
```

---

## Without transformation — wrong result

Server processes User 1's delete first:

```
"Hello" → Delete(position=0) → "ello"
```

New positions:

```
e l l o
0 1 2 3
```

Server now applies User 2's operation as-is — Insert X at position 2:

```
"ello" → Insert("X", position=2) → "elXlo"
```

X lands between the two l's — not where User 2 intended. The delete shifted everything left by 1, but the insert position was never updated to account for that.

---

## With transformation — correct result

Since User 1 deleted position 0, every position after 0 shifted left by 1. User 2's position 2 must become position 1:

```
Original:  Insert("X", position=2)
Transform: Insert("X", position=1)  ← shift left by 1 because of User 1's delete
```

Server applies the transformed operation:

```
"ello" → Insert("X", position=1) → "eXllo" ✓
```

X is back between "e" and the first "l" — exactly where User 2 intended.

---

## The transformation rule for concurrent delete + insert

```
If Delete happened at position D before Insert arrives:
→ If Insert position > D  → shift Insert position left by 1
→ If Insert position <= D → Insert position stays unchanged
→ If Insert position == D → the character the insert was relative to is gone — server must decide (typically keep the insert at position D)
```

The server is always the arbiter. It applies one operation, transforms all concurrent operations based on what changed, then applies them in order. Every client converges to the same document.
