---
type: primitive
used_by: "[[01 Thread-Safe LRU Cache Design]], [[02 Rate Limiter Design]]"
status: 🚧 chunks 1–3 of 4 written
---
> [!abstract] `HashMap` internals
> A **primitive note**, not a case study — the structure sits under LRU Cache, Rate Limiter, and
> every "make it thread-safe" follow-up. Built in four chunks:
> **1. array + hashing** → **2. collisions and chains** → **3. load factor and resize** →
> **4. what two threads do to all of it**.

---

## Chunk 1 — a hash map is an array plus a trick

### Why an array

`int[] arr = new int[4]`. Reading `arr[2]` is **instant** — not "fast", instant — because the array
starts at a known memory address and every slot is the same size, so slot 2 is just
`start + 2 × slotSize`. One multiply, one add. **It never searches.**

That is exactly the property a map wants: `counters.get("alice")` in one step.

### The problem

An array can only be indexed by a number in range — `0, 1, 2, 3`. The key is `"alice"`.
There is no `arr["alice"]`.

### The trick — turn the key into a number

Every Java object has **`hashCode()`**: a method that reads the object's contents and returns an
`int`. For a `String` it chews through the characters and produces one big number.
**Same string → always the same number. Different strings → usually different numbers.**

```
"alice".hashCode()  →  92902992      (illustrative values)
"bob".hashCode()    →     97714
"dave".hashCode()   →   3076014
```

Those numbers are far too big to index a 4-slot table, so squash them into range with a remainder:

```
index = hashCode % tableLength
```

```
92902992 % 4  =  0     →  "alice"  →  slot 0
   97714 % 4  =  2     →  "bob"    →  slot 2
 3076014 % 4  =  2     →  "dave"   →  slot 2     ← same slot as bob
```

### Lookup, end to end

`get("bob")`:

1. compute `"bob".hashCode()` → `97714`
2. `97714 % 4` → `2`
3. jump straight to slot 2

No slot is scanned, nothing is compared along the way. **That is why a hash map is O(1) — it
*computes* the address instead of *searching* for it.**

> [!important] Why two unrelated keys share a slot — the answer to "how is dave in the same slot as bob?"
> Nothing about `"dave"` is related to `"bob"`. They collide because taking a huge number's remainder
> mod 4 has **only four possible answers**, so unrelated keys are forced together. With 4 slots and
> 5 keys it is not bad luck, it is **arithmetically unavoidable**.
>
> This is called a **collision**, and it is the normal case, not an error case. Essentially all of
> `HashMap`'s design is the answer to *"what do we do about collisions?"*

---

## Chunk 2 — collisions and chains

`"bob"` and `"dave"` both want slot 2, and only one thing can be stored at `table[2]`. So what goes
there?

### Not the value — a node

Every stored pair is wrapped in a small object:

```java
class Node {
    int hash;       // the key's hashCode, cached
    String key;     // "bob"
    Window value;   // the thing you stored
    Node next;      // ← the important field
}
```

`next` is the entire answer. **A slot doesn't hold one entry — it holds the head of a linked list**,
and colliding keys are appended to it. That list is called a **bucket** or a **chain**.

```
table[0] → ("alice", W1) → null
table[1] → null
table[2] → ("bob", W2) → ("dave", W4) → null
table[3] → null
```

`put("dave", W4)` = compute slot 2 → walk the chain → no `"dave"` found → append.

### So `get` needs a second step

Landing on the right slot is no longer enough, because two different keys live there:

```
get("dave"):
  1. hash → slot 2
  2. walk the chain:
       node 1: key "bob"  — is this "dave"? no  → follow next
       node 2: key "dave" — is this "dave"? yes → return W4
```

> [!important] This is why hash collections need **both** methods
> **`hashCode()` picks the slot** — it narrows a million keys down to one short chain.
> **`equals()` picks the node inside that chain** — because arriving at the correct slot does not
> mean you have found the correct key.
> Consequence for design: any object used as a `Map` key needs both. See the `Rule` record in
> [[02 Rate Limiter Design]] — without them, `rules.get(new Rule("/login", FREE))` misses every time.

### The cost hiding in the chain

O(1) was the promise, but a `get` is now *jump to slot* **plus** *walk the chain*. If every key
collided into one slot you would have a single chain holding everything, and lookup would be
**O(n) — a plain linked-list scan.** The hash map degenerates into a list.

Java defends this two ways:

1. **A good hash function**, spreading keys evenly across slots — the primary defence.
2. **Treeification (Java 8+)** — once one chain passes **8 nodes**, it converts itself into a
   balanced tree, making the worst case **O(log n)** instead of O(n).

But the real defence is simply **keeping chains short**: never letting the table get crowded relative
to the number of keys stored. Which is chunk 3.

---

## Chunk 3 — load factor and resize

Chains stay short only if there are enough slots to go around. 4 slots holding 40 keys means chains
averaging 10 nodes, and every lookup pays for that walk. So the map **watches how full it is and
grows the table**.

### The two numbers

- **`capacity`** — the length of the `table` array. Default **16**.
- **`size`** — how many entries are currently stored (not how many slots are used).
- **`loadFactor`** — how full is *too* full. Default **0.75**.

From those: `threshold = capacity × loadFactor`. Default `16 × 0.75 = 12`.

**When `size` exceeds the threshold, the map resizes.** 0.75 is a deliberate compromise — lower
wastes memory on empty slots, higher lets chains grow and lookups slow down.

### What resize actually does

Two steps, and the second is the expensive one:

1. **Allocate a new table at double the capacity** — 4 → 8, 16 → 32. (Always a power of two, which
   is why the growth is doubling.)
2. **Rehash: move every existing entry into the new table.**

Step 2 is unavoidable, and this is the part worth internalising: **an entry's slot depends on the
table's length**, since the index is `hash % length`. Change the length and the arithmetic changes,
so entries must be recomputed and physically relocated.

Take the chunk-1 table, now full enough to trigger a resize (`size` 3 ≥ `4 × 0.75`):

```
BEFORE — capacity 4                     index = hash % 4
  table[0] → ("alice", W1) → null              92902992 % 4 = 0
  table[1] → null
  table[2] → ("bob", W2) → ("dave", W4)        97714 % 4 = 2 ,  3076014 % 4 = 2
  table[3] → null
```

```
AFTER — capacity 8                      index = hash % 8
  table[0] → ("alice", W1) → null              92902992 % 8 = 0    (stayed)
  table[1] → null
  table[2] → ("bob", W2) → null                   97714 % 8 = 2    (stayed)
  table[3] → null
  table[4] → null
  table[5] → null
  table[6] → ("dave", W4) → null                3076014 % 8 = 6    (MOVED)
  table[7] → null
```

**The chain that held bob and dave got split** — which is exactly the point of resizing. Doubling the
table gives each key one more bit of the hash to spread on, so an entry either **stays at index `i`
or moves to `i + oldCapacity`** (dave: `2 + 4 = 6`). Nothing else is possible, and Java 8 exploits
that to split each chain into two lists in a single pass.

### The cost, and the thing to carry into chunk 4

A resize is **O(n)** — it touches every entry in the map. Amortised over all the inserts, `put` is
still O(1) on average, so this is fine.

> [!warning] The property that makes resize the concurrency landmine
> A resize is a **bulk pointer-rewiring of the entire data structure**, and it runs on **whichever
> unlucky thread happened to be the one that pushed `size` past the threshold** — with no lock and no
> announcement. For the duration of that operation the map is in an **inconsistent intermediate
> state**: entries exist in two tables, chains are half-moved, `size` and `table.length` briefly
> disagree.
>
> A second thread writing during that window is not "racing on a counter" — it is mutating a
> structure that is being rebuilt underneath it. That is chunk 4.

## Chunk 4 — what two threads do to this structure

*→ next.*
