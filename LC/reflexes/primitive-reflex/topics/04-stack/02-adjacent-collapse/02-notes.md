# Stack Atom 02 — notes

## Backing a stack with a list (reusable beyond this atom)

A stack is an **interface** (push/pop/peek), not a concrete type. The `ArrayDeque` "stack" pushes/pops at the **head**, so draining it gives top→bottom order → you must `reverse()` to read in sequence. That's what made the Deque solution messy here.

Pick the backing structure by **what you need to read**, not how you write:

| You need… | Use |
|---|---|
| LIFO only (never read in order, or reversing is fine) | `ArrayDeque` (push/pop) |
| LIFO **+ ordered read-out / random access / snapshot** | `ArrayList` / `StringBuilder` (top = last index) |
| FIFO (queue / BFS) | `ArrayDeque` (offer/poll) |

`ArrayList`/`StringBuilder` as a stack — `add` / `get(size-1)` / `remove(size-1)` are all `O(1)` amortized (same cost as Deque), and the result is **already in order** (no reverse).

If you want to keep `ArrayDeque` but avoid the reverse: use `addLast` / `pollLast` / `peekLast` (treat the tail as top).

## Where this recurs — tree path problems

Root-to-leaf path / backtracking uses an `ArrayList` *because* you need the path in order and copyable:
```java
path.add(node.val);                              // push (enter)
if (leaf) result.add(new ArrayList<>(path));     // snapshot in order
dfs(left); dfs(right);
path.remove(path.size() - 1);                    // pop (backtrack)
```
Stack-by-behavior, list-by-need. Never `ArrayDeque` here — you need ordered, snapshot-able access.

## Java gotcha

`stack.peek() == c` is safe only because `c` is a primitive `char` (auto-unboxes the boxed `Character`). Comparing **two** `Character` objects with `==` hits the cached-range bug (works ≤127, breaks above) — use `.equals()` or `.charValue()`.
