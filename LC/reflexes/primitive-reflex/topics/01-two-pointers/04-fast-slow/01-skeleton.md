# Atom 04 — Fast & slow pointers

Tier 1 (Pointers) · motion `→ →→` (same direction, different speeds)
*Derived Socratically 2026-06-03.*

## ① Trigger

A linked structure — a linked list, or an implicit `i → next[i]` functional graph — and you need cycle / middle / nth-from-end in `O(1)` extra space (no visited-set).

## ② The atom (cycle detection)

Both pointers start at head; `slow` moves 1, `fast` moves 2.

- No cycle → `fast` walks off the end: `fast == null || fast.next == null` → return false.
- Cycle → `slow == fast` at some step → return true.

Why they must meet (and never leap over): once both are inside the loop, `fast` gains exactly 1 on `slow` each step. On a circle, gaining a step *is* closing in from behind, so the gap shrinks by exactly 1 per step → it must hit 0. Because it changes by **exactly 1**, it can't skip from "1 behind" to "1 ahead" — it lands. (3× speed could skip; 2× is the unique safe speed.)

```java
ListNode slow = head, fast = head;
while (fast != null && fast.next != null) {
    slow = slow.next;
    fast = fast.next.next;
    if (slow == fast) return true;   // collision = cycle
}
return false;                        // fast fell off the end = no cycle
```

## ③ Costumes

| Costume | Mechanic | Status |
|---|---|---|
| Cycle detection | the collision proof above | ✅ derived |
| Find middle | when `fast` reaches the end, `slow` is at the middle | ✅ free bonus |
| Cycle entry point (LL Cycle II) | after collision, reset one pointer to head, move both 1 step, they meet at loop start | ⬜ queued — new insight |
| Nth-from-end (Remove Nth Node) | two pointers held a fixed gap of `n` apart | ⬜ queued — different setup |
| Functional-graph cycle (Happy Number / Find Duplicate) | read `i → next[i]` as a linked list, same Floyd | ⬜ queued — recognition reskin |

## ④ Confusion matrix

| Confused with | Discriminator |
|---|---|
| #2 same-direction | different *speeds* on one structure (this) *vs* read/write at the same speed building a prefix |
| visited-set cycle check | `O(1)` space via two speeds (this) *vs* `O(n)` hash of seen nodes |

## ⑤ Practice queue

- [x] Linked List Cycle (141) — detection, derived
- [x] Middle of the Linked List (876) — free bonus, derived
- [ ] Linked List Cycle II (142) — cycle entry (reset-to-head)
- [ ] Remove Nth Node From End (19) — fixed-gap
- [ ] Happy Number (202) / Find the Duplicate Number (287) — functional-graph recognition

## ⑥ Reflex check

Prompt: *cycle / middle of a linked list in `O(1)` space — move?*
Answer: *two pointers from head, fast 2×; collision = cycle, fast hits null = no cycle, and slow sits at the middle when fast ends.*
